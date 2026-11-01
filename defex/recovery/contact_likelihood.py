"""Learned contact term, format v2 (v0.2c): mixture head and likelihood-type integration.

The v1 model (:mod:`defex.recovery.learned_prior`) predicts one Gaussian over the
plug-to-mouth offset from a contact, trained on its own. Multiplied into C's posterior
it double-counts: first contacts sit at the vision estimate, so the network's output
already contains the camera prior, and it reads the same centre of pressure C's
analytic update has used. A single Gaussian also cannot represent the mirror-ambiguous
contacts, so its tails are overconfident.

A v2 model keeps the v1 network body (tanh MLP on the same observation-only features)
and changes two things:

* Head: a mixture of ``K`` Gaussians over the offset ``o = probe - h`` (x, y only; G
  never used the yaw output), plus a uniform floor ``e`` over the localizer grid. ``e``
  is a stored model parameter (fitted with the network, not copied from C).
* Integration mode, stored with the model:

  - ``posterior``: trained alone, as v1 (b = 0 below); G adds its log density.
  - ``ratio``: a ``posterior`` model with the training marginal of the offset divided
    out (stored as a Gaussian mixture), so what is added is a likelihood ratio
    p(o | f) / p(o) instead of a posterior.
  - ``residual``: trained against C's own posterior. For each training contact the
    combined grid posterior ``normalize(b(h) + g(h))``, with ``b`` C's analytic log
    posterior after that contact (plus the model's own terms of the earlier contacts of
    the trial), is scored on the true mouth position. The network can only add what
    C's posterior lacks, and the combination is what is calibrated.

The term returned is ``weight x g(h)`` on the localizer grid (natural log, densities in
mm^-2). Only numpy and JSON: no simulator, no ground truth.
"""

from __future__ import annotations

import numpy as np

from defex.config import MM
from defex.recovery.learned_prior import D_MAX, feature_matrix, fixture_matches, mlp_forward

FORMAT_V2 = "defex-contact-prior-v2"
MODES = ("posterior", "ratio", "residual")
N_PER_COMPONENT = 6  # mean x, y; log-precision diagonal x, y; precision off-diagonal; mixture logit
_LOG_2PI = float(np.log(2.0 * np.pi))


def n_outputs(components: int) -> int:
    return N_PER_COMPONENT * components


def mixture_head(raw: np.ndarray, components: int):
    """Raw outputs (N, 6K) -> mean (N, K, 2), log-precision diagonal (N, K, 2), off-diagonal (N, K),
    log mixture weights (N, K), and the pre-squash diagonal (N, K, 2) (standardized offset units)."""
    r = raw.reshape(raw.shape[0], components, N_PER_COMPONENT)
    m = r[..., 0:2]
    pre = r[..., 2:4]
    d = D_MAX * np.tanh(pre / D_MAX)
    u = r[..., 4]
    a = r[..., 5]
    a = a - a.max(axis=1, keepdims=True)
    log_pi = a - np.log(np.exp(a).sum(axis=1, keepdims=True))
    return m, d, u, log_pi, pre


def component_log_density(m, d, u, t):
    """log N_k(t) for standardized offsets ``t`` (N, C, 2) under each component: (N, K, C), plus the
    residuals and whitened residuals the gradients need."""
    r1 = t[:, None, :, 0] - m[:, :, None, 0]
    r2 = t[:, None, :, 1] - m[:, :, None, 1]
    e1 = np.exp(d[..., 0])[..., None]
    e2 = np.exp(d[..., 1])[..., None]
    z1 = e1 * r1 + u[..., None] * r2
    z2 = e2 * r2
    logn = -0.5 * (z1**2 + z2**2) + (d[..., 0] + d[..., 1])[..., None] - _LOG_2PI
    return logn, (r1, r2, z1, z2, e1, e2)


def floored_log_density(raw, t, components: int, floor_density: float, outlier: float):
    """g = log[(1 - e) sum_k pi_k N_k(t) + e * floor_density] (N, C) in standardized units, and the parts
    of the computation the gradients reuse."""
    m, d, u, log_pi, pre = mixture_head(raw, components)
    logn, parts = component_log_density(m, d, u, t)
    lw = log_pi[..., None] + logn  # (N, K, C)
    mx = lw.max(axis=1, keepdims=True)
    mix = np.exp(lw - mx).sum(axis=1)  # (N, C)
    log_mix = np.log(mix) + mx[:, 0]
    a = np.log1p(-outlier) + log_mix
    b = np.log(outlier * floor_density) if outlier > 0 else -np.inf
    g = np.logaddexp(a, b)
    return g, (m, d, u, log_pi, pre, logn, lw, log_mix, a, parts)


def gaussian_mixture_log_density(params: dict, o: np.ndarray) -> np.ndarray:
    """log density (mm^-2) of a stored 2D Gaussian mixture at offsets ``o`` (..., 2) in mm."""
    w = np.asarray(params["weights"], dtype=float)
    mu = np.asarray(params["means_mm"], dtype=float)
    cov = np.asarray(params["covs_mm2"], dtype=float)
    out = []
    for k in range(w.size):
        P = np.linalg.inv(cov[k])
        dd = o - mu[k]
        maha = np.einsum("...i,ij,...j->...", dd, P, dd)
        out.append(np.log(w[k]) - 0.5 * maha - 0.5 * np.log(np.linalg.det(cov[k])) - _LOG_2PI)
    out = np.stack(out, axis=0)
    mx = out.max(axis=0)
    return mx + np.log(np.exp(out - mx).sum(axis=0))


class ContactLikelihood:
    """A v2 model file (see ``experiments/train_contact_likelihood.py`` for its fields)."""

    version = 2

    def __init__(self, data: dict, path: str | None = None) -> None:
        if data.get("format") != FORMAT_V2:
            raise ValueError(f"not a {FORMAT_V2} file: {path}")
        if data.get("mode") not in MODES:
            raise ValueError(f"unknown mode {data.get('mode')!r} in {path}")
        self.data = data
        self.path = path
        self.mode = data["mode"]
        self.components = int(data["components"])
        self.feature_names = tuple(data["feature_names"])
        self.x_mean = np.asarray(data["x_mean"], dtype=float)
        self.x_std = np.asarray(data["x_std"], dtype=float)
        self.o_mean = np.asarray(data["o_mean_mm"], dtype=float)
        self.o_std = np.asarray(data["o_std_mm"], dtype=float)
        self.outlier = float(data["outlier_weight"])
        self.layers = [(np.asarray(L["W"], dtype=float), np.asarray(L["b"], dtype=float)) for L in data["layers"]]
        self.applies_to = tuple(data.get("applies_to_kinds", ("surface_block",)))
        self.integration_weight = data.get("integration_weight")
        self.backend = data.get("backend", "")
        self.fixture_dynamics = data.get("fixture_dynamics") or {}
        self.marginal = data.get("offset_marginal")
        if self.mode == "ratio" and not self.marginal:
            raise ValueError(f"ratio model without an offset marginal: {path}")

    def matches(self, fixture_dynamics, rel_tol: float) -> bool:
        """The v1 rule: every FixtureDynamics field stated, each within the tolerance."""
        return fixture_matches(self.fixture_dynamics, fixture_dynamics, rel_tol)

    def raw(self, records: list[dict]) -> np.ndarray:
        x = (feature_matrix(records, self.feature_names) - self.x_mean) / self.x_std
        return mlp_forward(self.layers, x)[0]

    def log_term_mm(self, records: list[dict], h_mm: np.ndarray, area_mm2: float) -> np.ndarray:
        """g(h) for each record at mouth offsets ``h_mm`` (C, 2), mm relative to the vision estimate:
        (N, C), log density in mm^-2 (the floor is ``e / area_mm2``)."""
        probe = np.array([r["probe_xy_mm"] for r in records], dtype=float).reshape(-1, 2)
        o = probe[:, None, :] - h_mm[None, :, :]
        t = (o - self.o_mean) / self.o_std
        jac = float(np.log(self.o_std).sum())
        g, _ = floored_log_density(self.raw(records), t, self.components, area_mm2 ** -1 * np.prod(self.o_std),
                                   self.outlier)
        g = g - jac
        if self.mode == "ratio":
            g = g - gaussian_mixture_log_density(self.marginal, o)
        return g

    def mixture_mean_mm(self, record: dict) -> np.ndarray:
        """Mean mouth offset (2,) in mm of the mixture part alone (recorded, not used for decisions)."""
        m, _, _, log_pi, _ = mixture_head(self.raw([record]), self.components)
        o = (np.exp(log_pi[0])[:, None] * (m[0] * self.o_std + self.o_mean)).sum(axis=0)
        return np.asarray(record["probe_xy_mm"], dtype=float) - o

    def localizer_log_term(self, record: dict, hx: np.ndarray, hy: np.ndarray, area_m2: float) -> np.ndarray:
        """g on a localizer grid (``hx``, ``hy`` in metres), same shape as the grid."""
        h = np.stack([hx.ravel(), hy.ravel()], axis=1) / MM
        return self.log_term_mm([record], h, area_m2 / MM**2)[0].reshape(hx.shape)
