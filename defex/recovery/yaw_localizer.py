"""Joint (x, y, yaw) hole localization from contact (W4).

V0.1's :class:`~defex.recovery.search_policy.HoleLocalizer` estimates the mouth
position in (x, y) and handles yaw with a fixed search sequence. Its failures
concentrate where the vision yaw error exceeds 4 degrees: a 12 x 8 mm plug in a
13 x 9 mm cavity only enters below 4.92 degrees of relative yaw, so a yaw error
looks like a position error to a 2D filter.

This module models the plug at a relative yaw ``psi`` to the socket:

* Contact model: the plug face supported by the housing top is
  (rotated plug) ∩ (housing outline) minus (lead-in opening). Its convex hull is
  spanned by the vertices of that arrangement: the plug, housing and opening
  corners and the crossings of the plug edges with the housing and opening edges
  that lie in the region. The centre of pressure is the projection of the plug
  centre onto that hull, as in the 2D model (the wrist pivots the plug on its
  supports). At psi = 0 this reproduces the 2D table.
* Entry model: a plug at offset ``o`` and relative yaw ``d`` clears a box of
  half-widths (hx, hy) iff |o_x| + px|cos d| + py|sin d| <= hx and
  |o_y| + px|sin d| + py|cos d| <= hy. With the cavity it is "strict" entry;
  with the lead-in's outer edge it is "capture" (may stick on the chamfer).
* Filter: a histogram over hypotheses (x, y, psi_h) of the true mouth pose
  relative to the vision estimate. Updates use the exact contact model on the
  hypotheses that carry posterior mass (pruned below e^-25 of the maximum).
* Decision: the probe pose (x, y, yaw) with the highest posterior probability of
  entry, excluding poses that already blocked.

No learning; every step is an explicit geometric or Bayesian computation.
"""

from __future__ import annotations

import warnings

import numpy as np

from defex.config import DEG, MM, ConnectorSpec
from defex.recovery.search_policy import _hull_projection

_TOL = 1e-9
_PRUNE_LOG = 25.0
_LOG_FLOOR = 1e-300
_DECISION_HYPOTHESES = 4000  # most probable hypotheses used to score probe poses


def _rot(psi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.cos(psi), np.sin(psi)


def support_cop_yaw(
    o: np.ndarray,
    psi: np.ndarray,
    plug_half: tuple[float, float],
    opening_half: tuple[float, float],
    outer_half: tuple[float, float],
    min_width: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Blocked flag, missed flag and CoP (plug-centred, socket axes) for N plug poses.

    ``o`` (N, 2): plug centre minus mouth centre, socket axes. ``psi`` (N,): plug yaw
    relative to the socket. ``opening_half``: outer edge of the lead-in.
    """
    o = np.asarray(o, dtype=float)
    psi = np.broadcast_to(np.asarray(psi, dtype=float), (o.shape[0],))
    n = o.shape[0]
    px, py = plug_half
    ex, ey = opening_half
    hx, hy = outer_half
    c, s = _rot(psi)
    loc = np.array([[px, py], [-px, py], [-px, -py], [px, -py]])
    corners = np.stack([c[:, None] * loc[:, 0] - s[:, None] * loc[:, 1],
                        s[:, None] * loc[:, 0] + c[:, None] * loc[:, 1]], axis=-1)  # (N, 4, 2)
    ox, oy = o[:, 0:1], o[:, 1:2]
    xo = np.concatenate([-hx - ox, hx - ox], axis=1)  # housing x lines (N, 2)
    yo = np.concatenate([-hy - oy, hy - oy], axis=1)
    xi = np.concatenate([-ex - ox, ex - ox], axis=1)  # opening x lines
    yi = np.concatenate([-ey - oy, ey - oy], axis=1)

    pts = [corners]
    pts.append(np.stack(np.broadcast_arrays(xo[:, [0, 1, 1, 0]], yo[:, [0, 0, 1, 1]]), axis=-1))  # housing corners
    pts.append(np.stack(np.broadcast_arrays(xi[:, [0, 1, 1, 0]], yi[:, [0, 0, 1, 1]]), axis=-1))  # opening corners
    pts.append(np.stack(np.broadcast_arrays(xo[:, [0, 0, 1, 1]], yi[:, [0, 1, 0, 1]]), axis=-1))  # housing x / opening y
    pts.append(np.stack(np.broadcast_arrays(xi[:, [0, 0, 1, 1]], yo[:, [0, 1, 0, 1]]), axis=-1))  # opening x / housing y
    A = corners
    B = np.roll(corners, -1, axis=1)
    D = B - A  # (N, 4, 2) plug edges
    for lines, axis in ((xo, 0), (xi, 0), (yo, 1), (yi, 1)):
        for k in range(2):
            L = lines[:, k : k + 1]  # (N, 1)
            den = D[..., axis]
            with np.errstate(divide="ignore", invalid="ignore"):
                t = (L - A[..., axis]) / den
            ok = (np.abs(den) > _TOL) & (t >= -_TOL) & (t <= 1 + _TOL)
            P = A + np.where(ok, t, np.nan)[..., None] * D
            pts.append(P)
    P = np.concatenate(pts, axis=1)  # (N, K, 2)

    # Membership in the closed support region.
    lx = c[:, None] * P[..., 0] + s[:, None] * P[..., 1]  # into plug frame
    ly = -s[:, None] * P[..., 0] + c[:, None] * P[..., 1]
    tol = 1e-7
    in_plug = (np.abs(lx) <= px + tol) & (np.abs(ly) <= py + tol)
    in_outer = (P[..., 0] >= xo[:, :1] - tol) & (P[..., 0] <= xo[:, 1:] + tol) & \
               (P[..., 1] >= yo[:, :1] - tol) & (P[..., 1] <= yo[:, 1:] + tol)
    in_open = (P[..., 0] > xi[:, :1] + tol) & (P[..., 0] < xi[:, 1:] - tol) & \
              (P[..., 1] > yi[:, :1] + tol) & (P[..., 1] < yi[:, 1:] - tol)
    finite = np.isfinite(P).all(axis=-1)
    contact = finite & in_plug & in_outer
    V = contact & ~in_open

    def extent(mask):
        x = np.where(mask, P[..., 0], np.nan)
        y = np.where(mask, P[..., 1], np.nan)
        with np.errstate(invalid="ignore"), warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            wx = np.nanmax(x, axis=1) - np.nanmin(x, axis=1)
            wy = np.nanmax(y, axis=1) - np.nanmin(y, axis=1)
        return np.nan_to_num(wx, nan=0.0), np.nan_to_num(wy, nan=0.0)

    wx, wy = extent(contact)
    missed = (wx <= 0.0) | (wy <= 0.0)
    vx, vy = extent(V)
    blocked = (vx > min_width) & (vy > min_width) & ~missed
    cop = np.full((n, 2), np.nan)
    if blocked.any():
        cop[blocked] = _compact_hull_projection(P[blocked], V[blocked])
    return blocked, missed, cop


def _compact_hull_projection(P: np.ndarray, V: np.ndarray) -> np.ndarray:
    """_hull_projection on the valid points only (most of the 52 candidates are invalid)."""
    order = np.argsort(~V, axis=1, kind="stable")
    k = int(V.sum(axis=1).max())
    Pc = np.take_along_axis(P, order[..., None], axis=1)[:, :k]
    Vc = np.take_along_axis(V, order, axis=1)[:, :k]
    return _hull_projection(np.where(Vc[..., None], Pc, 0.0), Vc)


def fits(o: np.ndarray, d: np.ndarray, plug_half: tuple[float, float], box_half: tuple[float, float]) -> np.ndarray:
    """A plug at offset ``o`` and relative yaw ``d`` lies inside a centred box."""
    px, py = plug_half
    c, s = np.abs(np.cos(d)), np.abs(np.sin(d))
    return (np.abs(o[..., 0]) + px * c + py * s <= box_half[0]) & (np.abs(o[..., 1]) + px * s + py * c <= box_half[1])


def band_cop_yaw(o: np.ndarray, psi: np.ndarray, plug_half, cavity_half) -> np.ndarray:
    """CoP if the plug sticks on the lead-in: it rests on the corners that overhang the cavity."""
    px, py = plug_half
    c, s = _rot(np.broadcast_to(psi, (o.shape[0],)))
    loc = np.array([[px, py], [-px, py], [-px, -py], [px, -py]])
    P = np.stack([c[:, None] * loc[:, 0] - s[:, None] * loc[:, 1],
                  s[:, None] * loc[:, 0] + c[:, None] * loc[:, 1]], axis=-1)
    out = (np.abs(P[..., 0] + o[:, :1]) > cavity_half[0]) | (np.abs(P[..., 1] + o[:, 1:]) > cavity_half[1])
    return _compact_hull_projection(P, out)


class YawHoleLocalizer:
    """Histogram filter over the mouth pose (x, y, yaw) relative to the vision estimate."""

    def __init__(
        self,
        spec: ConnectorSpec,
        prior_sigma: float,
        yaw_prior_sigma: float,
        extent: float,
        resolution: float,
        yaw_extent: float,
        yaw_resolution: float,
        cop_sigma: float,
        outlier_weight: float,
        entry_likelihood: float,
        band_stick_probability: float,
        prior_uniform_weight: float,
        min_support: float,
    ) -> None:
        self.spec = spec
        self.plug_half = (spec.plug_half[0], spec.plug_half[1])
        self.cavity_half = spec.cavity_half
        self.opening_half = (spec.cavity_half[0] + spec.chamfer, spec.cavity_half[1] + spec.chamfer)
        self.outer_half = spec.outer_half
        self.res = resolution
        self.cop_sigma = cop_sigma
        self.outlier = outlier_weight
        self.entry_like = entry_likelihood
        self.p_stick = band_stick_probability
        self.min_support = min_support
        g = np.arange(-int(np.ceil(extent / resolution)), int(np.ceil(extent / resolution)) + 1) * resolution
        gy = np.arange(-int(np.ceil(yaw_extent / yaw_resolution)), int(np.ceil(yaw_extent / yaw_resolution)) + 1)
        self.grid = g
        self.yaw_grid = gy * yaw_resolution
        self.hx, self.hy, self.hpsi = np.meshgrid(g, g, self.yaw_grid, indexing="ij")
        self._uniform_cop_density = 1.0 / (4.0 * self.plug_half[0] * self.plug_half[1])
        r2 = (self.hx**2 + self.hy**2) / max(prior_sigma, 1e-6) ** 2 + self.hpsi**2 / max(yaw_prior_sigma, 1e-6) ** 2
        gauss = np.exp(-0.5 * r2)
        gauss /= gauss.sum()
        self.log_post = np.log((1 - prior_uniform_weight) * gauss + prior_uniform_weight / gauss.size)
        self.n_updates = 0

    # ------------------------------------------------------------------ inference
    @property
    def posterior(self) -> np.ndarray:
        p = np.exp(self.log_post - self.log_post.max())
        return p / p.sum()

    def _relative(self, probe_xy: np.ndarray, probe_yaw: float, sel: np.ndarray):
        """Plug offset and yaw relative to each hypothesized true socket frame."""
        hpsi = self.hpsi[sel]
        dx = probe_xy[0] - self.hx[sel]
        dy = probe_xy[1] - self.hy[sel]
        c, s = np.cos(hpsi), np.sin(hpsi)
        o = np.stack([c * dx + s * dy, -s * dx + c * dy], axis=-1)  # into the true socket frame
        return o, probe_yaw - hpsi, c, s

    def update_blocked(self, probe_xy: np.ndarray, probe_yaw: float, cop: np.ndarray | None,
                       cop_sigma: float | None = None) -> None:
        sel = self.log_post > self.log_post.max() - _PRUNE_LOG
        o, d, c, s = self._relative(np.asarray(probe_xy, float), float(probe_yaw), sel)
        blocked, missed, cop_top = support_cop_yaw(o, d, self.plug_half, self.opening_half, self.outer_half,
                                                   self.min_support)
        strict = fits(o, d, self.plug_half, self.cavity_half)
        band = ~blocked & ~missed & ~strict
        p_block = np.full(o.shape[0], self.entry_like)
        p_block[band] = self.p_stick
        p_block[blocked] = 1.0 - self.entry_like
        if cop is None:
            like = p_block
        else:
            cop_band = np.full_like(cop_top, np.nan)
            if band.any():
                cop_band[band] = band_cop_yaw(o[band], d[band], self.plug_half, self.cavity_half)
            pred = np.where(blocked[:, None], cop_top, cop_band)
            # predictions are in the true socket frame; the measurement is in the estimated one
            pred = np.stack([c * pred[:, 0] - s * pred[:, 1], s * pred[:, 0] + c * pred[:, 1]], axis=-1)
            s2 = (self.cop_sigma if cop_sigma is None else cop_sigma) ** 2
            d2 = ((np.nan_to_num(pred, nan=1e3) - np.asarray(cop)) ** 2).sum(axis=-1)
            gauss = np.where(blocked | band, np.exp(-0.5 * d2 / s2) / (2.0 * np.pi * s2), 0.0)
            like = p_block * ((1.0 - self.outlier) * gauss + self.outlier * self._uniform_cop_density)
        lp = self.log_post[sel] + np.log(like + _LOG_FLOOR)
        self.log_post[sel] = lp
        self.log_post[~sel] = np.minimum(self.log_post[~sel], lp.max() - _PRUNE_LOG - 1.0)
        self.log_post -= self.log_post.max()
        self.n_updates += 1

    def update_entered(self, probe_xy: np.ndarray, probe_yaw: float) -> None:
        sel = np.ones_like(self.log_post, dtype=bool)
        o, d, _, _ = self._relative(np.asarray(probe_xy, float), float(probe_yaw), sel)
        inside = fits(o, d, self.plug_half, (self.opening_half[0] + self.res, self.opening_half[1] + self.res))
        self.log_post[sel] += np.log(np.where(inside, 1.0, self.entry_like))
        self.log_post -= self.log_post.max()
        self.n_updates += 1

    def entry_probability(self, probe_xy: np.ndarray, probe_yaw: np.ndarray) -> np.ndarray:
        """P(entry) for M candidate probe poses under the current posterior."""
        post = self.posterior.ravel()
        # The decision depends on where the mass is concentrated; the uniform floor of the
        # prior spreads ~10% over every cell and only slows the sum down.
        k = min(_DECISION_HYPOTHESES, post.size)
        top = np.argpartition(post, -k)[-k:]
        w = post[top] / post[top].sum()
        hx, hy, hpsi = self.hx.ravel()[top], self.hy.ravel()[top], self.hpsi.ravel()[top]
        c, s = np.cos(hpsi), np.sin(hpsi)
        out = np.empty(len(probe_xy))
        chunk = max(1, 2_000_000 // max(1, w.size))
        for a in range(0, len(probe_xy), chunk):
            P = probe_xy[a : a + chunk]
            Y = probe_yaw[a : a + chunk]
            dx = P[:, 0:1] - hx
            dy = P[:, 1:2] - hy
            o = np.stack([c * dx + s * dy, -s * dx + c * dy], axis=-1)
            d = Y[:, None] - hpsi
            strict = fits(o, d, self.plug_half, self.cavity_half)
            capture = fits(o, d, self.plug_half, self.opening_half)
            pe = np.where(strict, 1.0 - self.entry_like, np.where(capture, 1.0 - self.p_stick, 0.0))
            out[a : a + chunk] = pe @ w
        return out

    def best_probe(self, max_radius: float, max_yaw: float, exclude: list[tuple[np.ndarray, float]],
                   exclude_radius: float, exclude_yaw: float, xy_step: float, yaw_step: float, refine: bool = True):
        """Probe pose (x, y, yaw) with the highest entry probability."""
        gx = np.arange(-max_radius, max_radius + 1e-12, xy_step)
        gyaw = np.arange(-max_yaw, max_yaw + 1e-12, yaw_step)
        X, Y, Z = np.meshgrid(gx, gx, gyaw, indexing="ij")
        X, Y, Z = X.ravel(), Y.ravel(), Z.ravel()
        keep = X**2 + Y**2 <= max_radius**2
        for q, qy in exclude:
            keep &= ((X - q[0]) ** 2 + (Y - q[1]) ** 2 > exclude_radius**2) | (np.abs(Z - qy) > exclude_yaw)
        X, Y, Z = X[keep], Y[keep], Z[keep]
        pe = self.entry_probability(np.stack([X, Y], axis=1), Z)
        best = pe.max()
        cand = np.flatnonzero(pe >= best - 1e-9)
        k = cand[np.argmin(X[cand] ** 2 + Y[cand] ** 2 + (Z[cand] / DEG * MM) ** 2)]  # nearest to the estimate
        if not refine:
            return np.array([X[k], Y[k]]), float(Z[k]), float(best)
        # Refine around the coarse optimum at half the step.
        fx = X[k] + np.array([-0.5, 0.0, 0.5]) * xy_step
        fz = Z[k] + np.array([-0.5, 0.0, 0.5]) * yaw_step
        FX, FY, FZ = np.meshgrid(fx, Y[k] + np.array([-0.5, 0.0, 0.5]) * xy_step, fz, indexing="ij")
        FX, FY, FZ = FX.ravel(), FY.ravel(), FZ.ravel()
        keep = (FX**2 + FY**2 <= max_radius**2) & (np.abs(FZ) <= max_yaw + 1e-12)
        for q, qy in exclude:
            keep &= ((FX - q[0]) ** 2 + (FY - q[1]) ** 2 > exclude_radius**2) | (np.abs(FZ - qy) > exclude_yaw)
        FX, FY, FZ = FX[keep], FY[keep], FZ[keep]
        pf = self.entry_probability(np.stack([FX, FY], axis=1), FZ)
        j = int(np.argmax(pf))
        if pf[j] > best + 1e-9:
            return np.array([FX[j], FY[j]]), float(FZ[j]), float(pf[j])
        return np.array([X[k], Y[k]]), float(Z[k]), float(best)
