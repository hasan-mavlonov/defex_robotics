"""Contact-based hole localization (search policy for recovery).

When an insertion attempt is blocked on the receptacle's top face, the wrist F/T
sensor measures where the contact force acts. With the force reference point at
the plug tip, the center of pressure (CoP) on the plug face is

    cop_x = -tau_y / F_z,   cop_y = tau_x / F_z      (socket frame)

The CoP lies on the part of the plug face that is supported by the housing, i.e.
on the side *away* from the opening, and its location depends on how far the plug
is from the opening. :class:`HoleLocalizer` turns this into a Bayesian estimate of
the true mouth position relative to the vision estimate:

* Hypotheses: a grid of mouth offsets ``h`` around the vision estimate.
* Forward model: for a probe at ``p`` the plug footprint sits at offset
  ``o = p - h``. The supported part of the plug face is (plug ∩ housing top)
  minus the lead-in opening. Because the wrist is rotationally compliant relative
  to the very stiff contact, the plug pivots on its supports and the CoP is the
  projection of the plug center onto the convex hull of that region (validated
  against the physics in ``tests/test_search_policy.py``). The model is
  precomputed once per connector geometry as a lookup table over ``o``.
* Likelihood: Gaussian on the CoP residual for blocked hypotheses, a small
  probability for hypotheses that predicted entry, plus an outlier floor.
* Lead-in band: a plug edge over the 45 degree lead-in usually slides in, but can
  stick (high friction, yaw-misaligned corners); such hypotheses keep a moderate
  block probability with the CoP on the overhanging edges.
* Decision: probe where the posterior probability of entry is highest (box
  filters of the posterior over the strict-clearance and lead-in regions).

This is a conventional, explicit Bayesian estimator: no learning is involved and
every step is inspectable.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from defex.config import MM, ConnectorSpec


@dataclass(frozen=True)
class _ContactTable:
    step: float  # m, offset grid spacing
    half_n: int  # offsets span [-half_n, half_n] * step on each axis
    blocked: np.ndarray  # (N, N) bool
    cop: np.ndarray  # (N, N, 2) m, CoP relative to the plug center (NaN when not blocked)
    capture_half: tuple[float, float]  # m, lead-in capture half-widths (o_x, o_y)
    missed: np.ndarray  # (N, N) bool, plug footprint clear of the housing
    strict_half: tuple[float, float]  # m, offsets inside which the plug clears the cavity walls
    band: np.ndarray  # (N, N) bool, plug edge over the lead-in (may slide in or stick)
    cop_band: np.ndarray  # (N, N, 2) m, CoP if the plug sticks on the lead-in

    def index(self, o: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        ij = np.rint(o / self.step).astype(int) + self.half_n
        n = 2 * self.half_n + 1
        valid = (ij[..., 0] >= 0) & (ij[..., 0] < n) & (ij[..., 1] >= 0) & (ij[..., 1] < n)
        return np.clip(ij[..., 0], 0, n - 1), np.clip(ij[..., 1], 0, n - 1), valid


def _hull_projection(P: np.ndarray, V: np.ndarray) -> np.ndarray:
    """Projection of the origin onto the convex hull of valid points.

    ``P`` (N, K, 2) points, ``V`` (N, K) validity. Returns (N, 2); rows with no
    valid point are NaN. If the origin lies inside the hull the result is (0, 0).
    """
    any_valid = V.any(axis=1)
    ang = np.where(V, np.arctan2(P[..., 1], P[..., 0]), np.inf)
    ang = np.sort(ang, axis=1)
    cnt = V.sum(axis=1)
    with np.errstate(invalid="ignore"):
        gaps = np.diff(ang, axis=1)
        gaps = np.where(np.isfinite(gaps), gaps, -np.inf)
        first = ang[:, 0]
        last = np.take_along_axis(ang, np.maximum(cnt - 1, 0)[:, None], axis=1)[:, 0]
        wrap = np.where(cnt > 0, first + 2.0 * np.pi - last, np.inf)
    max_gap = np.maximum(gaps.max(axis=1), wrap)
    at_origin = (V & (np.hypot(P[..., 0], P[..., 1]) < 1e-12)).any(axis=1)
    inside = any_valid & ((max_gap < np.pi - 1e-9) | at_origin)
    # Otherwise the closest hull point lies on a segment between two valid points.
    iu, ju = np.triu_indices(P.shape[1], k=1)
    A = P[:, iu]
    B = P[:, ju]
    AB = B - A
    L2 = (AB**2).sum(-1)
    t = np.where(L2 > 0, np.clip(-(A * AB).sum(-1) / np.where(L2 > 0, L2, 1.0), 0.0, 1.0), 0.0)
    Q = A + t[..., None] * AB
    d2 = np.where(V[:, iu] & V[:, ju], (Q**2).sum(-1), np.inf)
    k = np.argmin(d2, axis=1)
    closest = Q[np.arange(Q.shape[0]), k]
    out = np.where(inside[:, None], 0.0, closest)
    return np.where(any_valid[:, None], out, np.nan)


def _support_cop(
    o: np.ndarray, plug_half: tuple[float, float], inner_half: tuple[float, float], outer_half: tuple[float, float],
    min_width: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Analytic contact model for a flat plug face pressed on the receptacle top.

    ``o`` (N, 2): plug center minus mouth center. Works in plug-centered coordinates.
    Returns ``blocked`` (N,), ``missed`` (N,) (plug clear of the housing) and the
    predicted CoP (N, 2).

    The supporting region is (plug ∩ housing) minus the lead-in opening, a union of
    at most four rectangles. Because the wrist's rotational stiffness is tiny
    relative to the contact stiffness, the plug pivots until the net contact force
    passes as close as possible to the wrist load point (the plug center): the CoP
    is the projection of the origin onto the convex hull of the support region.
    """
    px, py = plug_half
    ex, ey = inner_half
    hx, hy = outer_half
    oxs, oys = o[:, 0], o[:, 1]
    ax0 = np.maximum(-px, -hx - oxs)
    ax1 = np.minimum(px, hx - oxs)
    ay0 = np.maximum(-py, -hy - oys)
    ay1 = np.minimum(py, hy - oys)
    missed = (ax1 - ax0 <= 0.0) | (ay1 - ay0 <= 0.0)
    ix0 = np.clip(-ex - oxs, ax0, ax1)
    ix1 = np.clip(ex - oxs, ax0, ax1)
    iy0 = np.clip(-ey - oys, ay0, ay1)
    iy1 = np.clip(ey - oys, ay0, ay1)
    rects = [
        (ax0, ix0, ay0, ay1),  # left of the opening
        (ix1, ax1, ay0, ay1),  # right of the opening
        (ix0, ix1, ay0, iy0),  # below the opening
        (ix0, ix1, iy1, ay1),  # above the opening
    ]
    pts = []
    valid = []
    for x0, x1, y0, y1 in rects:
        ok = (x1 - x0 > min_width) & (y1 - y0 > min_width) & ~missed
        for cx, cy in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            pts.append(np.stack([cx, cy], axis=1))
            valid.append(ok)
    P = np.stack(pts, axis=1)  # (N, 16, 2)
    V = np.stack(valid, axis=1)  # (N, 16)
    blocked = V.any(axis=1)
    cop = _hull_projection(P, V)
    return blocked, missed, cop


def _band_cop(o: np.ndarray, plug_half: tuple[float, float], cavity_half: tuple[float, float]) -> np.ndarray:
    """CoP if the plug sticks on the lead-in: it rests on its edges that overhang the cavity walls."""
    px, py = plug_half
    hx, hy = cavity_half
    fxp = o[:, 0] + px > hx
    fxn = o[:, 0] - px < -hx
    fyp = o[:, 1] + py > hy
    fyn = o[:, 1] - py < -hy
    corners = np.array([[px, py], [px, -py], [-px, py], [-px, -py]])
    V = np.stack([fxp | fyp, fxp | fyn, fxn | fyp, fxn | fyn], axis=1)
    P = np.broadcast_to(corners, (o.shape[0], 4, 2))
    return _hull_projection(P, V)


@lru_cache(maxsize=8)
def _contact_table(
    plug_half: tuple[float, float],
    cavity_half: tuple[float, float],
    chamfer: float,
    outer_half: tuple[float, float],
    step: float,
    max_offset: float,
) -> _ContactTable:
    px, py = plug_half
    hx, hy = cavity_half
    ex, ey = hx + chamfer, hy + chamfer  # outer edge of the lead-in
    half_n = int(np.ceil(max_offset / step))
    offs = np.arange(-half_n, half_n + 1) * step
    n = offs.size
    gx, gy = np.meshgrid(offs, offs, indexing="ij")
    o = np.stack([gx.ravel(), gy.ravel()], axis=1)
    blocked = np.zeros(o.shape[0], dtype=bool)
    missed = np.zeros(o.shape[0], dtype=bool)
    cop = np.full((o.shape[0], 2), np.nan)
    cop_band = np.full((o.shape[0], 2), np.nan)
    chunk = 4096
    for a in range(0, o.shape[0], chunk):
        b_, m_, c_ = _support_cop(o[a : a + chunk], (px, py), (ex, ey), outer_half, min_width=0.02 * MM)
        blocked[a : a + chunk] = b_
        missed[a : a + chunk] = m_
        cop[a : a + chunk] = c_
        cop_band[a : a + chunk] = _band_cop(o[a : a + chunk], (px, py), (hx, hy))
    strict = (max(hx - px, 0.0), max(hy - py, 0.0))
    inside_strict = (np.abs(o[:, 0]) <= strict[0]) & (np.abs(o[:, 1]) <= strict[1])
    band = ~blocked & ~missed & ~inside_strict
    capture = (max(ex - px, 0.0), max(ey - py, 0.0))
    return _ContactTable(
        step,
        half_n,
        blocked.reshape(n, n),
        cop.reshape(n, n, 2),
        capture,
        missed.reshape(n, n),
        strict,
        band.reshape(n, n),
        cop_band.reshape(n, n, 2),
    )


class HoleLocalizer:
    """Histogram filter over the true mouth offset (socket-estimate frame, metres)."""

    def __init__(
        self,
        spec: ConnectorSpec,
        prior_sigma: float,
        extent: float,
        resolution: float,
        cop_sigma: float,
        outlier_weight: float = 0.1,
        entry_likelihood: float = 0.05,
        band_stick_probability: float = 0.35,
    ) -> None:
        self.res = resolution
        self.extent = extent
        self.cop_sigma = cop_sigma
        self.outlier = outlier_weight
        self.entry_like = entry_likelihood
        half = int(np.ceil(extent / resolution))
        g = np.arange(-half, half + 1) * resolution
        self.grid = g
        self.hx, self.hy = np.meshgrid(g, g, indexing="ij")
        self.table = _contact_table(
            (spec.plug_half[0], spec.plug_half[1]),
            spec.cavity_half,
            spec.chamfer,
            spec.outer_half,
            resolution,
            2.0 * extent + max(spec.plug_half[0], spec.plug_half[1]),
        )
        self.capture_half = self.table.capture_half
        self.p_stick = band_stick_probability
        self._uniform_cop_density = 1.0 / (4.0 * spec.plug_half[0] * spec.plug_half[1])
        # Heavy-tailed prior: Gaussian around the vision estimate + uniform floor.
        r2 = self.hx**2 + self.hy**2
        gauss = np.exp(-0.5 * r2 / max(prior_sigma, 1e-6) ** 2)
        gauss /= gauss.sum()
        self.log_post = np.log(0.9 * gauss + 0.1 / gauss.size)
        self.n_updates = 0

    # ------------------------------------------------------------------ inference
    @property
    def posterior(self) -> np.ndarray:
        lp = self.log_post - self.log_post.max()
        p = np.exp(lp)
        return p / p.sum()

    def mean(self) -> np.ndarray:
        p = self.posterior
        return np.array([(p * self.hx).sum(), (p * self.hy).sum()])

    def map(self) -> np.ndarray:
        i, j = np.unravel_index(int(np.argmax(self.log_post)), self.log_post.shape)
        return np.array([self.grid[i], self.grid[j]])

    def _predict(self, probe: np.ndarray):
        o = np.stack([probe[0] - self.hx, probe[1] - self.hy], axis=-1)
        ii, jj, valid = self.table.index(o)
        t = self.table
        blocked = t.blocked[ii, jj] & valid
        band = t.band[ii, jj] & valid
        in_model = valid & ~t.missed[ii, jj]
        return blocked, band, t.cop[ii, jj], t.cop_band[ii, jj], in_model

    def update_blocked(self, probe: np.ndarray, cop: np.ndarray | None, cop_sigma: float | None = None) -> None:
        """A probe at ``probe`` stopped near the mouth plane; ``cop`` is the measured CoP (or None).

        Likelihood = P(blocked | h) * p(cop | h, blocked). Three regimes per hypothesis:
        blocked on the top face (CoP from the support hull), resting on the lead-in
        (sticks with probability ``p_stick``, CoP on the overhanging edges; covers
        high friction and yaw-misaligned corners), or clear of the walls (blocking
        unlikely). The CoP density mixes a Gaussian with a uniform outlier term, so
        an unexplainable CoP degrades gracefully to a block-only update.
        """
        blocked, band, cop_top, cop_band, in_model = self._predict(np.asarray(probe, dtype=float))
        p_block = np.full(blocked.shape, self.entry_like)
        p_block[band & in_model] = self.p_stick
        p_block[blocked & in_model] = 1.0 - self.entry_like
        if cop is None:
            like = p_block
        else:
            s2 = (self.cop_sigma if cop_sigma is None else cop_sigma) ** 2
            c = np.asarray(cop)
            pred = np.where(blocked[..., None], cop_top, np.where(band[..., None], cop_band, np.nan))
            d2 = ((np.nan_to_num(pred, nan=1e3) - c) ** 2).sum(axis=-1)
            gauss = np.where(blocked | band, np.exp(-0.5 * d2 / s2) / (2.0 * np.pi * s2), 0.0)
            like = p_block * ((1.0 - self.outlier) * gauss + self.outlier * self._uniform_cop_density)
        self.log_post += np.log(like + 1e-300)
        self.log_post -= self.log_post.max()
        self.n_updates += 1

    def update_entered(self, probe: np.ndarray) -> None:
        """The plug entered the cavity at ``probe`` (lateral position is right)."""
        o_x = probe[0] - self.hx
        o_y = probe[1] - self.hy
        cx, cy = self.table.capture_half
        inside = (np.abs(o_x) <= cx + self.res) & (np.abs(o_y) <= cy + self.res)
        like = np.where(inside, 1.0, self.entry_like)
        self.log_post += np.log(like)
        self.log_post -= self.log_post.max()
        self.n_updates += 1

    def _box(self, p: np.ndarray, half: tuple[float, float]) -> np.ndarray:
        kx = max(int(np.floor(half[0] / self.res + 1e-9)), 0)
        ky = max(int(np.floor(half[1] / self.res + 1e-9)), 0)
        n = p.shape[0]
        c = np.zeros((n + 1, n + 1))
        c[1:, 1:] = p.cumsum(0).cumsum(1)
        i = np.arange(n)
        i0 = np.clip(i - kx, 0, n)
        i1 = np.clip(i + kx + 1, 0, n)
        j0 = np.clip(i - ky, 0, n)
        j1 = np.clip(i + ky + 1, 0, n)
        return c[i1][:, j1] - c[i0][:, j1] - c[i1][:, j0] + c[i0][:, j0]

    def entry_probability(self) -> np.ndarray:
        """P(plug enters) for a probe at every grid point under the current posterior."""
        p = self.posterior
        strict = self._box(p, self.table.strict_half)
        capture = self._box(p, self.table.capture_half)
        return (1.0 - self.entry_like) * strict + (1.0 - self.p_stick) * (capture - strict)

    def entry_probability_at(self, probe: np.ndarray) -> float:
        pe = self.entry_probability()
        i = int(np.clip(np.rint(probe[0] / self.res) + (len(self.grid) - 1) // 2, 0, len(self.grid) - 1))
        j = int(np.clip(np.rint(probe[1] / self.res) + (len(self.grid) - 1) // 2, 0, len(self.grid) - 1))
        return float(pe[i, j])

    def best_probe(
        self, max_radius: float, exclude: list[np.ndarray] | None = None, exclude_radius: float | None = None
    ) -> tuple[np.ndarray, float]:
        """Probe location maximizing the entry probability within ``max_radius``.

        Locations within ``exclude_radius`` of already blocked probes are skipped:
        re-probing a spot that just blocked is never informative.
        """
        pc = self.entry_probability()
        mask = (self.hx**2 + self.hy**2) <= max_radius**2
        if exclude:
            r = min(self.table.strict_half) * 0.75 if exclude_radius is None else exclude_radius
            r = max(r, 0.6 * self.res)
            for q in exclude:
                mask &= (self.hx - q[0]) ** 2 + (self.hy - q[1]) ** 2 > r**2
        pc = np.where(mask, pc, -1.0)
        best = pc.max()
        cand = np.argwhere(pc >= best - 1e-9)
        mean = self.mean()
        pts = np.stack([self.grid[cand[:, 0]], self.grid[cand[:, 1]]], axis=1)
        k = int(np.argmin(((pts - mean) ** 2).sum(axis=1)))
        return pts[k], float(best)


def predicted_cop(spec: ConnectorSpec, offset: np.ndarray) -> np.ndarray | None:
    """Exact forward-model CoP for a plug at ``offset`` from the mouth (None if not blocked)."""
    ex, ey = spec.cavity_half[0] + spec.chamfer, spec.cavity_half[1] + spec.chamfer
    blocked, _, cop = _support_cop(
        np.asarray(offset, dtype=float).reshape(1, 2),
        (spec.plug_half[0], spec.plug_half[1]),
        (ex, ey),
        spec.outer_half,
        min_width=0.02 * MM,
    )
    return cop[0].copy() if blocked[0] else None


YAW_SEARCH_SEQUENCE_DEG = (3.0, -3.0, 6.0, -6.0, 9.0, -9.0, 12.0, -12.0)
