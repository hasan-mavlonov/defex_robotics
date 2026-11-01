"""Train and evaluate v2 learned contact terms for controller G (v0.2c).

See :mod:`defex.recovery.contact_likelihood` for the model. Training data are contact
records from ``experiments/collect_contacts.py`` (C's, and G's for the DAgger-style
re-collection), labelled offline. For every surface-block contact this script rebuilds
C's analytic hole-localizer posterior along the trial's own record sequence (the same
updates C ran; checked against the recorded posterior mean on C's data), so a model can
be trained and scored on the posterior G actually acts on.

Splits by base seed (``SPLITS``): fit 3001-3025 and 3033-3038, early stopping and
every offline choice 3026-3030 and 3039-3040, dev 2026 reported only. 4001 (spent),
3031, 3032 and every reserved seed are never read.

Loss, for every contact i of a trial (all on the localizer's 57 x 57 grid, 0.25 mm):

    L_i = -log softmax_c(b_i(c) + w * g_i(c))[cell of the true mouth]

``g_i`` is the model's floored mixture log density for contact i; ``b_i`` is 0 in mode
``posterior`` (the model alone) and, in mode ``residual``, C's analytic log posterior
after contact i plus ``w * g_j`` of the trial's earlier contacts j (the model's own
current values, not differentiated, refreshed every epoch), as in G at run time.
Adam, mini-batches, L2, standardized inputs and offsets, early stopping on the stopping
split's loss, fixed numpy seed: retraining reproduces the weights.

    python -m experiments.train_contact_likelihood fit --backend gantry --mode residual --components 2 \\
        --sources results/w9_development/data:train_main,train_noise05 --name gantry_residual_k2
    python -m experiments.train_contact_likelihood evaluate --backend gantry --models a.json,b.json ...

Outputs under results/v0.2c_learned_prior/models/: <name>.json (model) and
<name>_metrics.json.
"""

from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse  # noqa: E402
import gzip  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

from defex.config import MM, REPO_ROOT, AdaptiveConfig, LearnedPriorConfig  # noqa: E402
from defex.recovery.contact_likelihood import (  # noqa: E402
    FORMAT_V2,
    ContactLikelihood,
    floored_log_density,
    gaussian_mixture_log_density,
    n_outputs,
)
from defex.recovery.learned_prior import D_MAX, FEATURE_SETS, ContactPrior, feature_matrix, mlp_forward  # noqa: E402
from defex.recovery.search_policy import HoleLocalizer  # noqa: E402
from defex.tasks.scenarios import resolve_connector  # noqa: E402
from experiments.collect_contacts import RESERVED_SEEDS, all_conditions  # noqa: E402
from experiments.train_contact_prior import (  # noqa: E402
    backend_fixture_dynamics,
    backward,
    characterized_fixture_dynamics,
    complete_fixture_dynamics,
    consistent_fixture_dynamics,
    git_info,
    standardize,
)

OUT = REPO_ROOT / "results" / "v0.2c_learned_prior"
FIT_SEEDS = frozenset((*range(3001, 3026), *range(3033, 3039)))
STOP_SEEDS = frozenset((*range(3026, 3031), 3039, 3040))
DEV_SEEDS = frozenset((2026,))
NEVER_READ = frozenset((*RESERVED_SEEDS, 4001, 3031, 3032))
SPLITS = {"fit": FIT_SEEDS, "stop": STOP_SEEDS, "dev": DEV_SEEDS}
NUMPY_SEED = 11
# Both v1 models selected 32x32 and lr 3e-3 from the full W9 grid; v0.2c searches only the L2 weight.
GRID = {"hidden": [(32, 32)], "lr": [3e-3], "weight_decay": [1e-4, 1e-3]}
INIT_OUTLIER = 0.1  # starting value of the fitted floor (C's localizer_outlier_weight)
MIN_OUTLIER = 1e-3  # the floor is never fitted to zero: a confident wrong term must not erase the truth
COMPONENT_SPREAD = 0.5  # initial spread of the mixture means (standardized units), breaks the symmetry


# ------------------------------------------------------------------ data and replay
@dataclass
class Rows:
    records: list = field(default_factory=list)
    h_mm: list = field(default_factory=list)  # true mouth offset x, y
    cell: list = field(default_factory=list)  # flat grid index of the truth (-1: off the grid)
    base: list = field(default_factory=list)  # (C,) float32 analytic log posterior after this contact
    earlier: list = field(default_factory=list)  # row indices of the trial's earlier surface blocks
    excluded: list = field(default_factory=list)  # probes C excludes after this contact (mm), for best_probe
    meta: list = field(default_factory=list)


def _localizer(rec: dict, condition: str, cfg: AdaptiveConfig) -> HoleLocalizer:
    spec = resolve_connector(all_conditions()[condition])
    sigma_xy = max(rec["vision_xy_sigma_mm"], cfg.min_prior_sigma_mm) * MM
    return HoleLocalizer(
        spec, prior_sigma=float(np.hypot(cfg.prior_sigma_scale * sigma_xy, rec["vision_bias_mm"] * MM)),
        extent=cfg.search_extent_mm * MM, resolution=cfg.search_resolution_mm * MM, cop_sigma=cfg.cop_sigma_mm * MM,
        outlier_weight=cfg.localizer_outlier_weight, entry_likelihood=cfg.localizer_entry_likelihood,
        band_stick_probability=cfg.localizer_band_stick_probability,
        prior_uniform_weight=cfg.localizer_prior_uniform_weight, exclude_fraction=cfg.localizer_exclude_fraction,
        exclude_min_cells=cfg.localizer_exclude_min_cells, min_support=cfg.localizer_min_support_mm * MM,
    )


def parse_sources(text: str) -> list[tuple[Path, str]]:
    """'root:name1,name2;root2:name3' -> [(root/<backend>/name, name), ...] (backend added later)."""
    out = []
    for part in text.split(";"):
        if not part:
            continue
        root, names = part.split(":")
        out += [(REPO_ROOT / root, n) for n in names.split(",") if n]
    return out


def load_split(backend: str, sources: list[tuple[Path, str]], seeds: frozenset, cfg: AdaptiveConfig) -> Rows:
    """Every surface-block contact of these base seeds, with C's analytic posterior replayed."""
    rows = Rows()
    replay_dev = []
    for root, name in sources:
        trials: dict[tuple, list] = {}
        with gzip.open(root / backend / name / "contacts.jsonl.gz", "rt") as fh:
            for line in fh:
                r = json.loads(line)
                if r["base_seed"] in NEVER_READ:
                    raise SystemExit(f"seed {r['base_seed']} must not be read ({name})")
                if r["base_seed"] not in seeds:
                    continue
                trials.setdefault((r["condition"], r["base_seed"], r["trial_index"]), []).append(r)
        for key in sorted(trials):
            recs = sorted(trials[key], key=lambda r: r["record_index"])
            loc = _localizer(recs[0]["record"], key[0], cfg)
            hx, hy = loc.hx.ravel() / MM, loc.hy.ravel() / MM
            prior_rows: list[int] = []
            excluded: list[list[float]] = []
            for k, r in enumerate(recs):
                rec = r["record"]
                if rec["kind"] in ("surface_block", "no_contact") and "cop_clean" in rec:
                    sigma = (cfg.cop_sigma_mm if rec["cop_clean"] else cfg.unclean_cop_sigma_mm) * MM
                    cop = None if rec["cop_mm"] is None or rec["kind"] != "surface_block" else np.asarray(rec["cop_mm"]) * MM
                    loc.update_blocked(np.asarray(rec["probe_xy_mm"]) * MM, cop, cop_sigma=sigma)
                    excluded.append(list(rec["probe_xy_mm"]))
                    if rec["kind"] == "surface_block" and "analytic_mean_mm" in rec:
                        if r["controller"] == "adaptive":
                            replay_dev.append(float(np.abs(loc.mean() / MM - np.asarray(rec["analytic_mean_mm"])).max()))
                        h = np.array([r["label"]["x_mm"], r["label"]["y_mm"]])
                        lp = loc.log_post - loc.log_post.max()
                        lp = lp - np.log(np.exp(lp).sum())
                        idx = int(np.argmin((hx - h[0]) ** 2 + (hy - h[1]) ** 2))
                        on_grid = np.all(np.abs(h) <= np.abs(hx).max() + 0.5 * cfg.search_resolution_mm)
                        rows.records.append(rec)
                        rows.h_mm.append(h)
                        rows.cell.append(idx if on_grid else -1)
                        rows.base.append(lp.ravel().astype(np.float32))
                        rows.earlier.append(list(prior_rows))
                        rows.excluded.append([list(p) for p in excluded])
                        rows.meta.append({"source": name, "condition": key[0], "base_seed": key[1],
                                          "trial_index": key[2], "attempt": rec["attempt"],
                                          "controller": r["controller"], "trial_success": r["trial_success"]})
                        prior_rows.append(len(rows.records) - 1)
                elif rec["kind"] == "partial_jam" and k < len(recs) - 1:
                    loc.update_entered(np.asarray(rec["probe_xy_mm"]) * MM)
    rows.replay_max_dev_mm = max(replay_dev) if replay_dev else None
    return rows


def grid_mm(cfg: AdaptiveConfig) -> tuple[np.ndarray, float, float]:
    """Flattened localizer grid (C, 2) in mm, cell area and grid area (mm^2)."""
    half = int(np.ceil(cfg.search_extent_mm / cfg.search_resolution_mm))
    g = np.arange(-half, half + 1) * cfg.search_resolution_mm
    hx, hy = np.meshgrid(g, g, indexing="ij")
    return np.stack([hx.ravel(), hy.ravel()], axis=1), cfg.search_resolution_mm**2, (g.size * cfg.search_resolution_mm) ** 2


# ------------------------------------------------------------------ model math
class Net:
    """Parameters of one v2 model while training: MLP layers and the floor logit."""

    def __init__(self, layers, eta: float):
        self.layers = layers
        self.eta = eta

    @property
    def outlier(self) -> float:
        return MIN_OUTLIER + (1.0 - MIN_OUTLIER) / (1.0 + np.exp(-self.eta))


def init_net(rng, n_in: int, hidden, components: int) -> Net:
    sizes = [n_in, *hidden, n_outputs(components)]
    layers = []
    for k, (a, b) in enumerate(zip(sizes[:-1], sizes[1:])):
        lim = np.sqrt(6.0 / (a + b))
        W = rng.uniform(-lim, lim, (a, b))
        bias = np.zeros(b)
        if k == len(sizes) - 2:
            W *= 0.1
            if components > 1:
                ang = 2.0 * np.pi * np.arange(components) / components
                for j in range(components):
                    bias[6 * j] = COMPONENT_SPREAD * np.cos(ang[j])
                    bias[6 * j + 1] = COMPONENT_SPREAD * np.sin(ang[j])
        layers.append((W, bias))
    p = (INIT_OUTLIER - MIN_OUTLIER) / (1.0 - MIN_OUTLIER)
    return Net(layers, float(np.log(p / (1.0 - p))))


def head_grads(raw, t, components, floor_std, outlier, wvec):
    """g (N, C) and dL/d(raw) (N, 6K), dL/d(outlier) for L = sum_c wvec[n, c] * g[n, c]."""
    g, (m, d, u, log_pi, pre, logn, lw, log_mix, a, parts) = floored_log_density(raw, t, components, floor_std, outlier)
    r1, r2, z1, z2, e1, e2 = parts
    s = np.exp(a - g)  # share of the mixture in g
    rho = np.exp(lw - log_mix[:, None, :])  # component responsibilities within the mixture
    A = (wvec * s)[:, None, :] * rho  # (N, K, C)
    gr = np.zeros((raw.shape[0], components, 6))
    gr[..., 0] = (A * z1 * e1).sum(-1)
    gr[..., 1] = (A * (z1 * u[..., None] + z2 * e2)).sum(-1)
    dd1 = (A * (1.0 - z1 * e1 * r1)).sum(-1)
    dd2 = (A * (1.0 - z2 * e2 * r2)).sum(-1)
    sq = 1.0 - np.tanh(pre / D_MAX) ** 2
    gr[..., 2] = dd1 * sq[..., 0]
    gr[..., 3] = dd2 * sq[..., 1]
    gr[..., 4] = -(A * z1 * r2).sum(-1)
    ws = (wvec * s).sum(-1)  # (N,)
    gr[..., 5] = (wvec[:, None, :] * s[:, None, :] * rho).sum(-1) - np.exp(log_pi) * ws[:, None]
    d_out = float((wvec * (np.exp(np.log(floor_std) - g) - np.exp(log_mix - g))).sum())
    return g, gr.reshape(raw.shape[0], -1), d_out


def batch_loss_grads(net: Net, x, t, base, cell, components, floor_std, weight, weight_decay, jac, dtype=np.float64):
    """Mean grid NLL of the truth cell under normalize(base + weight * g) and its gradients.
    ``dtype``: precision of the grid computation (training uses float32 for speed; tests float64)."""
    raw, acts = mlp_forward(net.layers, x)
    raw_h, t, base = raw.astype(dtype), t.astype(dtype), base.astype(dtype)
    g, _ = floored_log_density(raw_h, t, components, floor_std, net.outlier)
    z = base + weight * (g - jac)
    zmax = z.max(axis=1, keepdims=True)
    lse = zmax[:, 0] + np.log(np.exp(z - zmax).sum(axis=1))
    n = x.shape[0]
    ar = np.arange(n)
    loss = float((lse - z[ar, cell]).mean())
    q = np.exp(z - lse[:, None])
    wvec = q.copy()
    wvec[ar, cell] -= 1.0
    wvec *= weight / n
    _, graw, d_out = head_grads(raw_h, t, components, floor_std, net.outlier, wvec)
    graw = graw.astype(np.float64)
    grads = backward(net.layers, acts, graw)
    grads = [(gW + weight_decay * W, gb) for (gW, gb), (W, _) in zip(grads, net.layers)]
    e = net.outlier
    d_eta = d_out * (e - MIN_OUTLIER) * (1.0 - (e - MIN_OUTLIER) / (1.0 - MIN_OUTLIER))
    loss += 0.5 * weight_decay * sum(float((W**2).sum()) for W, _ in net.layers)
    return loss, grads, d_eta


@dataclass
class Prepared:
    x: np.ndarray
    probe: np.ndarray  # (N, 2) mm
    base: np.ndarray  # (N, C) float32 analytic log posterior (zeros in posterior mode)
    cell: np.ndarray
    earlier: list
    keep: np.ndarray  # rows used (truth on the grid)
    grid: np.ndarray
    o_mean: np.ndarray
    o_std: np.ndarray
    needed: np.ndarray  # rows that are an earlier contact of some row (their terms feed recurrent bases)

    def t(self, idx) -> np.ndarray:
        return ((self.probe[idx][:, None, :] - self.grid[None]) - self.o_mean) / self.o_std


def prepare(rows: Rows, names, x_mean, x_std, o_mean, o_std, grid: np.ndarray, mode: str) -> Prepared:
    keep = np.flatnonzero(np.asarray(rows.cell) >= 0)
    x = (feature_matrix([rows.records[i] for i in keep], names) - x_mean) / x_std
    probe = np.array([rows.records[i]["probe_xy_mm"] for i in keep], dtype=float).reshape(-1, 2)
    if mode == "residual":
        base = np.stack([rows.base[i] for i in keep]).astype(np.float32)
    else:
        base = np.zeros((keep.size, grid.shape[0]), dtype=np.float32)
    pos = {int(i): k for k, i in enumerate(keep)}
    earlier = [[pos[j] for j in rows.earlier[i] if j in pos] for i in keep]
    needed = np.array(sorted({j for js in earlier for j in js}), dtype=int)
    return Prepared(x, probe, base, np.asarray(rows.cell)[keep], earlier, keep, grid, o_mean, o_std, needed)


def g_rows(net: Net, p: Prepared, idx: np.ndarray, components, floor_std, jac, chunk: int = 256) -> np.ndarray:
    """g (len(idx), C) for these rows, in chunks (the grid makes each row 3,249 values)."""
    out = np.empty((idx.size, p.grid.shape[0]))
    for a in range(0, idx.size, chunk):
        j = idx[a : a + chunk]
        raw = mlp_forward(net.layers, p.x[j])[0]
        out[a : a + chunk] = floored_log_density(raw, p.t(j), components, floor_std, net.outlier)[0] - jac
    return out


def recurrent_base(p: Prepared, net: Net, components, floor_std, jac, weight: float) -> np.ndarray:
    """Base posterior of each contact plus ``weight * g`` of the trial's earlier contacts (G at run time)."""
    b = p.base.copy()
    if p.needed.size == 0:
        return b
    g = g_rows(net, p, p.needed, components, floor_std, jac)
    at = {int(j): k for k, j in enumerate(p.needed)}
    for i, js in enumerate(p.earlier):
        for j in js:
            b[i] += np.float32(weight) * g[at[j]].astype(np.float32)
    return b


def split_loss(net, p: Prepared, components, floor_std, weight, jac, recurrent: bool) -> float:
    b = recurrent_base(p, net, components, floor_std, jac, weight) if recurrent else p.base
    total = 0.0
    n = p.x.shape[0]
    for a in range(0, n, 256):
        idx = np.arange(a, min(a + 256, n))
        z = b[idx].astype(float) + weight * g_rows(net, p, idx, components, floor_std, jac)
        zmax = z.max(axis=1, keepdims=True)
        lse = zmax[:, 0] + np.log(np.exp(z - zmax).sum(axis=1))
        total += float((lse - z[np.arange(idx.size), p.cell[idx]]).sum())
    return total / n


def train(fit: Prepared, stop: Prepared, hidden, lr, weight_decay, components, floor_std, jac, recurrent: bool,
          weight: float = 1.0, seed: int = NUMPY_SEED, batch: int = 128, max_epochs: int = 400,
          patience: int = 40) -> dict:
    rng = np.random.default_rng(seed)
    net = init_net(rng, fit.x.shape[1], hidden, components)
    params = [*(W for W, _ in net.layers), *(b for _, b in net.layers)]
    m = [np.zeros_like(q) for q in params] + [0.0]
    v = [np.zeros_like(q) for q in params] + [0.0]
    b1, b2, eps = 0.9, 0.999, 1e-8
    step = 0
    best = (np.inf, None, -1)
    history = []
    nl = len(net.layers)
    for epoch in range(max_epochs):
        base = recurrent_base(fit, net, components, floor_std, jac, weight) if recurrent else fit.base
        order = rng.permutation(fit.x.shape[0])
        for a0 in range(0, order.size, batch):
            idx = order[a0 : a0 + batch]
            _, grads, d_eta = batch_loss_grads(net, fit.x[idx], fit.t(idx), base[idx], fit.cell[idx], components,
                                               floor_std, weight, weight_decay, jac, dtype=np.float32)
            step += 1
            gl = [gW for gW, _ in grads] + [gb for _, gb in grads] + [d_eta]
            cur = [W for W, _ in net.layers] + [b for _, b in net.layers] + [net.eta]
            c1, c2 = 1 - b1**step, 1 - b2**step
            new = []
            for k, (q, gq) in enumerate(zip(cur, gl)):
                m[k] = b1 * m[k] + (1 - b1) * gq
                v[k] = b2 * v[k] + (1 - b2) * gq**2
                new.append(q - lr * (m[k] / c1) / (np.sqrt(v[k] / c2) + eps))
            net = Net([(new[k], new[nl + k]) for k in range(nl)], float(new[-1]))
        val = split_loss(net, stop, components, floor_std, weight, jac, recurrent)
        history.append((epoch, val))
        if val < best[0]:
            best = (val, Net([(W.copy(), b.copy()) for W, b in net.layers], net.eta), epoch)
        elif epoch - best[2] >= patience:
            break
    return {"net": best[1], "best_epoch": best[2], "stop_loss": best[0], "epochs_run": len(history),
            "history": history}


def fit_marginal(o: np.ndarray, components: int = 2, iters: int = 200, seed: int = NUMPY_SEED) -> dict:
    """EM fit of a 2D Gaussian mixture (mm) to the training offsets (the ratio mode's divisor)."""
    rng = np.random.default_rng(seed)
    n = o.shape[0]
    mu = o[rng.choice(n, components, replace=False)]
    cov = np.stack([np.cov(o.T) for _ in range(components)])
    w = np.full(components, 1.0 / components)
    for _ in range(iters):
        logp = np.stack([np.log(w[k]) - 0.5 * np.einsum("ni,ij,nj->n", o - mu[k], np.linalg.inv(cov[k]), o - mu[k])
                         - 0.5 * np.log(np.linalg.det(cov[k])) for k in range(components)], axis=1)
        r = np.exp(logp - logp.max(axis=1, keepdims=True))
        r /= r.sum(axis=1, keepdims=True)
        nk = r.sum(axis=0)
        w = nk / n
        mu = (r.T @ o) / nk[:, None]
        cov = np.stack([((r[:, k, None] * (o - mu[k])).T @ (o - mu[k])) / nk[k] + 1e-6 * np.eye(2)
                        for k in range(components)])
    return {"weights": w.tolist(), "means_mm": mu.tolist(), "covs_mm2": cov.tolist()}


# ------------------------------------------------------------------ evaluation
def term_on_grid(model, rec: dict, grid: np.ndarray, area: float) -> np.ndarray:
    """What G adds for this contact, (C,) natural log, before the integration weight."""
    if isinstance(model, ContactLikelihood):
        return model.log_term_mm([rec], grid, area)[0]
    mean, prec = model.localizer_term(rec)
    mean, prec = mean / MM, prec * MM**2
    d = grid - mean
    maha = np.einsum("ci,ij,cj->c", d, prec, d)
    e = LearnedPriorConfig().outlier_weight
    dens = np.exp(-0.5 * maha) * np.sqrt(max(float(np.linalg.det(prec)), 0.0)) / (2.0 * np.pi)
    return np.log((1.0 - e) * dens + e / area + 1e-300)


def evaluate(models: dict, rows: Rows, cfg: AdaptiveConfig, backend: str) -> dict:
    """Combined-posterior metrics per candidate on one split (C = no learned term).

    For each surface-block contact: C's analytic posterior after it, plus the candidate's term for
    it and for the trial's earlier contacts (G's run-time posterior, along the recorded probes).
    """
    grid, cell_area, area = grid_mm(cfg)
    n_grid = int(round(np.sqrt(grid.shape[0])))
    keep = [i for i, c in enumerate(rows.cell) if c >= 0]
    out = {"n": len(rows.records), "n_on_grid": len(keep), "n_first_contact": int(sum(rows.meta[i]["attempt"] == 1 for i in keep)),
           "replay_max_dev_mm": rows.replay_max_dev_mm, "candidates": {}}
    first = np.array([rows.meta[i]["attempt"] == 1 for i in keep])
    locs: dict[str, HoleLocalizer] = {}
    for name, (model, weight) in models.items():
        terms: dict[int, np.ndarray] = {}
        nll, err, hpd, hit, hit_strict = [], [], [], [], []
        for i in keep:
            rec = rows.records[i]
            b = rows.base[i].astype(float)
            if model is not None and weight > 0:
                for j in (*rows.earlier[i], i):
                    if j not in terms:
                        terms[j] = term_on_grid(model, rows.records[j], grid, area)
                    b = b + weight * terms[j]
            b = b - b.max()
            p = np.exp(b)
            p /= p.sum()
            h = rows.h_mm[i]
            c = rows.cell[i]
            nll.append(-np.log(p[c] + 1e-300) + np.log(cell_area))
            mean = p @ grid
            err.append(float(np.hypot(*(mean - h))))
            hpd.append(float(p[p > p[c]].sum()))
            cnd = rows.meta[i]["condition"]
            if cnd not in locs:
                locs[cnd] = _localizer(rec, cnd, cfg)
            probe_loc = locs[cnd]
            probe_loc.log_post = np.log(p.reshape(n_grid, n_grid) + 1e-300)
            nxt, _ = probe_loc.best_probe(cfg.max_lateral_correction_mm * MM,
                                          exclude=[np.asarray(q) * MM for q in rows.excluded[i]])
            o = np.abs(nxt / MM - h)
            cap = np.asarray(probe_loc.table.capture_half) / MM
            strict = np.asarray(probe_loc.table.strict_half) / MM
            hit.append(bool(np.all(o <= cap)))
            hit_strict.append(bool(np.all(o <= strict)))
        nll, err, hpd = np.array(nll), np.array(err), np.array(hpd)
        hit, hit_strict = np.array(hit), np.array(hit_strict)

        def summ(mask):
            if not mask.any():
                return None
            return {"n": int(mask.sum()), "grid_nll_nats": float(nll[mask].mean()),
                    "mean_radial_error_mm": float(err[mask].mean()),
                    "outside_hpd50": float((hpd[mask] > 0.5).mean()), "outside_hpd95": float((hpd[mask] > 0.95).mean()),
                    "next_probe_in_capture": float(hit[mask].mean()),
                    "next_probe_in_strict_clearance": float(hit_strict[mask].mean())}

        allm = np.ones(len(keep), dtype=bool)
        res = {"weight": weight, "all": summ(allm), "first_contact": summ(first), "later_contact": summ(~first),
               "by_condition": {}}
        conds = np.array([rows.meta[i]["condition"] for i in keep])
        for cnd in sorted(set(conds)):
            res["by_condition"][cnd] = summ(conds == cnd)
        out["candidates"][name] = res
    return out


# ------------------------------------------------------------------ main
def _rel(p: Path) -> str:
    return str(p.relative_to(REPO_ROOT)) if p.is_relative_to(REPO_ROOT) else str(p)


def fixture_of(backend: str, sources, conditions: list[str]) -> tuple[dict, list[str]]:
    """The fixture dynamics the data was collected on. Data collected before a FixtureDynamics field
    existed (W9's gantry data predates W5b) gets the missing fields from the backend, after every
    stored field is checked against it (as train_contact_prior --complete-fixture-dynamics does)."""
    tol = LearnedPriorConfig().fixture_match_rel_tol
    fds = [json.loads((root / backend / n / "summary.json").read_text())["fixture_dynamics"] for root, n in sources]
    by_keys: dict[tuple, list] = {}
    for fd in fds:
        by_keys.setdefault(tuple(sorted(k for k, v in fd.items() if v is not None)), []).append(fd)
    measured, _ = backend_fixture_dynamics(backend, conditions)
    merged = []
    added: set[str] = set()
    for group in by_keys.values():
        ref = consistent_fixture_dynamics([{k: v for k, v in fd.items() if v is not None} for fd in group], tol)
        full, new = complete_fixture_dynamics(ref, measured, tol)
        merged.append(full)
        added |= set(new)
    return characterized_fixture_dynamics(consistent_fixture_dynamics(merged, tol)), sorted(added)


def cmd_fit(args) -> None:
    cfg = AdaptiveConfig()
    t0 = time.time()
    sources = parse_sources(args.sources)
    fit_rows = load_split(args.backend, sources, FIT_SEEDS, cfg)
    fixture, completed = fixture_of(args.backend, sources, sorted({m["condition"] for m in fit_rows.meta}))
    stop_rows = load_split(args.backend, sources, STOP_SEEDS, cfg)
    mode = args.mode
    train_mode = "posterior" if mode == "ratio" else mode
    names = FEATURE_SETS[args.feature_set]
    grid, cell_area, area = grid_mm(cfg)
    keep = [i for i, c in enumerate(fit_rows.cell) if c >= 0]
    x_raw = feature_matrix([fit_rows.records[i] for i in keep], names)
    o = np.array([fit_rows.records[i]["probe_xy_mm"] for i in keep]) - np.array([fit_rows.h_mm[i] for i in keep])
    x_mean, x_std = standardize(x_raw)
    o_mean, o_std = standardize(o)
    jac = float(np.log(o_std).sum())
    floor_std = float(np.prod(o_std)) / area
    fit = prepare(fit_rows, names, x_mean, x_std, o_mean, o_std, grid, train_mode)
    stop = prepare(stop_rows, names, x_mean, x_std, o_mean, o_std, grid, train_mode)
    recurrent = train_mode == "residual" and not args.no_recurrent
    print(f"{args.backend}/{mode}/K={args.components}: {fit.x.shape[0]} fit / {stop.x.shape[0]} stop contacts "
          f"(replay max deviation {fit_rows.replay_max_dev_mm} mm), {len(names)} features, recurrent={recurrent}",
          flush=True)
    grid_hp = {k: v for k, v in GRID.items()}
    if args.hidden:
        grid_hp["hidden"] = [tuple(int(h) for h in s.split("x")) for s in args.hidden.split(",")]
    if args.lr:
        grid_hp["lr"] = [float(x) for x in args.lr.split(",")]
    if args.weight_decay:
        grid_hp["weight_decay"] = [float(x) for x in args.weight_decay.split(",")]
    search, best = [], None
    for hidden, lr, wd in itertools.product(grid_hp["hidden"], grid_hp["lr"], grid_hp["weight_decay"]):
        t1 = time.time()
        res = train(fit, stop, hidden, lr, wd, args.components, floor_std, jac, recurrent,
                    max_epochs=args.max_epochs, patience=args.patience)
        entry = {"hidden": list(hidden), "lr": lr, "weight_decay": wd, "best_epoch": res["best_epoch"],
                 "epochs_run": res["epochs_run"], "stop_grid_nll_nats": res["stop_loss"] + float(np.log(cell_area)),
                 "outlier_weight": res["net"].outlier, "wall_s": time.time() - t1}
        search.append(entry)
        print(f"  hidden={hidden} lr={lr:g} wd={wd:g}: best epoch {res['best_epoch']}/{res['epochs_run']}, "
              f"stop NLL {entry['stop_grid_nll_nats']:.4f}, e={entry['outlier_weight']:.3f}, {entry['wall_s']:.0f} s",
              flush=True)
        if best is None or entry["stop_grid_nll_nats"] < best[0]["stop_grid_nll_nats"]:
            best = (entry, res)
    entry, res = best
    net = res["net"]
    data = {
        "format": FORMAT_V2, "backend": args.backend, "mode": mode, "components": args.components,
        "feature_set": args.feature_set, "feature_names": list(names),
        "x_mean": x_mean.tolist(), "x_std": x_std.tolist(), "o_mean_mm": o_mean.tolist(), "o_std_mm": o_std.tolist(),
        "outlier_weight": net.outlier, "activation": "tanh",
        "layers": [{"W": W.tolist(), "b": b.tolist()} for W, b in net.layers],
        "applies_to_kinds": ["surface_block"], "integration_weight": 1.0, "fixture_dynamics": fixture,
        "metadata": {
            "description": "v0.2c learned contact term (development model, not a reported result)",
            "created_utc": datetime.now(timezone.utc).isoformat(), "git": git_info(), "numpy_seed": NUMPY_SEED,
            "numpy": np.__version__, "fit_base_seeds": sorted(FIT_SEEDS), "stop_base_seeds": sorted(STOP_SEEDS),
            "data": [_rel(r / args.backend / n) for r, n in sources], "n_fit": int(fit.x.shape[0]),
            "n_stop": int(stop.x.shape[0]), "recurrent_base": recurrent,
            "fixture_dynamics_completed_from_backend": completed,
            "conditions_train": sorted({m["condition"] for m in fit_rows.meta}),
            "selected_hyperparameters": {k: entry[k] for k in ("hidden", "lr", "weight_decay", "best_epoch")},
            "selection": "lowest stopping-split grid NLL over the grid; early stopping on it "
                         f"(patience {args.patience} epochs)",
            "command": args.command_line,
        },
    }
    if mode == "ratio":
        data["offset_marginal"] = fit_marginal(o)
    out = OUT / "models"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{args.name}.json").write_text(json.dumps(data))
    (out / f"{args.name}_search.json").write_text(json.dumps(
        {"search": search, "selected": entry, "history_best_run": res["history"], "wall_time_s": time.time() - t0},
        indent=1))
    print(f"wrote {out / (args.name + '.json')} ({time.time() - t0:.0f} s)")


def load_any(path: str):
    data = json.loads((REPO_ROOT / path).read_text())
    return ContactLikelihood(data, path) if data.get("format") == FORMAT_V2 else ContactPrior(data, path)


def cmd_evaluate(args) -> None:
    cfg = AdaptiveConfig()
    sources = parse_sources(args.sources)
    models = {"C": (None, 0.0)}
    for spec in args.models.split(","):
        name, path, w = spec.split("=")[0], *spec.split("=")[1].split("@")
        models[name] = (load_any(path), float(w))
    result = {"backend": args.backend, "sources": [_rel(r / args.backend / n) for r, n in sources],
              "models": {k: (None if m is None else m.path, w) for k, (m, w) in models.items()}, "splits": {},
              "git": git_info()}
    for split in args.splits.split(","):
        rows = load_split(args.backend, sources, SPLITS[split], cfg)
        result["splits"][split] = evaluate(models, rows, cfg, args.backend)
        print(f"{split}: {len(rows.records)} contacts")
        for name, r in result["splits"][split]["candidates"].items():
            a, f = r["all"], r["first_contact"]
            print(f"  {name:28s} all: NLL {a['grid_nll_nats']:.3f} err {a['mean_radial_error_mm']:.2f} "
                  f"out50 {a['outside_hpd50']:.2f} out95 {a['outside_hpd95']:.3f} hit {a['next_probe_in_capture']:.3f} | "
                  f"first: NLL {f['grid_nll_nats']:.3f} err {f['mean_radial_error_mm']:.2f} out95 {f['outside_hpd95']:.3f} "
                  f"hit {f['next_probe_in_capture']:.3f}", flush=True)
    dest = Path(args.out) if Path(args.out).is_absolute() else REPO_ROOT / args.out
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=1))
    print(f"wrote {dest}")


def main() -> None:
    import sys

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fit")
    f.add_argument("--backend", choices=["gantry", "arm"], required=True)
    f.add_argument("--sources", required=True, help="root:name,name;root:name (relative to the repository)")
    f.add_argument("--mode", choices=["posterior", "ratio", "residual"], required=True)
    f.add_argument("--components", type=int, default=1)
    f.add_argument("--feature-set", choices=sorted(FEATURE_SETS), default="contact")
    f.add_argument("--name", required=True)
    f.add_argument("--hidden", default="", help="e.g. 32x32,64x64 (default: the grid)")
    f.add_argument("--lr", default="")
    f.add_argument("--weight-decay", default="")
    f.add_argument("--max-epochs", type=int, default=300)
    f.add_argument("--patience", type=int, default=30)
    f.add_argument("--no-recurrent", action="store_true", help="residual mode: base without the earlier terms")
    e = sub.add_parser("evaluate")
    e.add_argument("--backend", choices=["gantry", "arm"], required=True)
    e.add_argument("--sources", required=True)
    e.add_argument("--models", required=True, help="name=path@weight,...")
    e.add_argument("--splits", default="stop,dev")
    e.add_argument("--out", required=True)
    args = ap.parse_args()
    args.command_line = "python -m experiments.train_contact_likelihood " + " ".join(sys.argv[1:])
    (cmd_fit if args.cmd == "fit" else cmd_evaluate)(args)


if __name__ == "__main__":
    main()
