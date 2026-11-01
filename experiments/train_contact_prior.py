"""Train the learned contact prior (W9) with ordinary supervised-learning discipline.

Data: C's surface-contact records from ``experiments/collect_contacts.py``.
Splits are by base seed: train = 3001-3030, validation = 4001 (early stopping, the
hyperparameter grid, and later the integration weight), dev sanity = 2026 (reported,
never used for a choice). The pre-registered Checkpoint 2 seed is never read.

Model (``defex/recovery/learned_prior.py``): tanh MLP -> heteroscedastic Gaussian
(mean x, y, yaw; full x/y covariance via the precision's Cholesky factor; yaw sigma),
trained on the Gaussian negative log-likelihood with Adam, mini-batches, L2 weight
decay, standardized inputs and targets, early stopping on validation NLL, fixed
numpy seed. A small MLP rather than a linear model because the centre-of-pressure
to offset map is piecewise (support hull edges, lead-in band, tipping) and its
uncertainty is strongly input-dependent; numpy only, so the network is kept small.

    python -m experiments.train_contact_prior --backend gantry --feature-set contact
    python -m experiments.train_contact_prior --backend gantry --feature-set all --install-existing --weight 1 \\
        --weight-source results/w9_development/validation/weights/paired.md

Data is read from <root>/data/<backend>/ and models are written to <root>/models/
(root: results/w9_development unless --root says otherwise).

Outputs: <root>/models/<backend>_<feature set>.json (model) and
..._metrics.json (search table, train/val/dev NLL, MAE against the analytic
localizer, calibration). ``--install`` also writes assets/models/contact_prior_<backend>.json
with the integration weight chosen on the validation seed.
"""

from __future__ import annotations

import argparse
import gzip
import itertools
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from defex.config import MM, REPO_ROOT, AdaptiveConfig, LearnedPriorConfig
from defex.recovery.learned_prior import (
    D_MAX,
    FEATURE_SETS,
    FORMAT,
    N_OUT,
    TARGET_NAMES,
    ContactPrior,
    feature_matrix,
    gaussian_head,
    gaussian_nll,
    mlp_forward,
    probe_pose,
)
from defex.recovery.search_policy import HoleLocalizer
from defex.tasks.scenarios import resolve_connector
from experiments.collect_contacts import RESERVED_SEEDS, TRAIN_SEEDS, VALIDATION_SEED, all_conditions

DATA = REPO_ROOT / "results" / "w9_development" / "data"
TRAIN_BASE_SEEDS = tuple(range(3001, 3031))
GRID = {"hidden": [(32, 32), (64, 64)], "lr": [1e-3, 3e-3], "weight_decay": [1e-4, 1e-3]}
NUMPY_SEED = 9


# ------------------------------------------------------------------ data
def load_rows(backend: str, names: list[str], seeds: set[int] | None = None, data_root: Path = DATA) -> list[dict]:
    rows = []
    for name in names:
        with gzip.open(data_root / backend / name / "contacts.jsonl.gz", "rt") as fh:
            for line in fh:
                r = json.loads(line)
                if r["base_seed"] in RESERVED_SEEDS:
                    raise SystemExit(f"reserved seed {r['base_seed']} in {name}")
                if seeds is not None and r["base_seed"] not in seeds:
                    continue
                # Contacts where G would apply the model: surface blocks that reached the
                # localizer update (a retry-limit or time-limit stop ends the cycle before it).
                if r["record"]["kind"] == "surface_block" and "analytic_mean_mm" in r["record"]:
                    rows.append(r)
    return rows


def targets(rows: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    """(o, h): plug-minus-mouth offsets (the network's target) and the true mouth offsets."""
    h = np.array([[r["label"]["x_mm"], r["label"]["y_mm"], r["label"]["yaw_deg"]] for r in rows], dtype=float)
    return probe_pose([r["record"] for r in rows]) - h, h


# ------------------------------------------------------------------ training
def init_layers(rng: np.random.Generator, n_in: int, hidden: tuple[int, ...]) -> list[tuple[np.ndarray, np.ndarray]]:
    sizes = [n_in, *hidden, N_OUT]
    layers = []
    for k, (a, b) in enumerate(zip(sizes[:-1], sizes[1:])):
        lim = np.sqrt(6.0 / (a + b))  # Glorot uniform (tanh)
        W = rng.uniform(-lim, lim, (a, b))
        if k == len(sizes) - 2:
            W *= 0.1  # start near a unit Gaussian on standardized targets
        layers.append((W, np.zeros(b)))
    return layers


def nll_grad_raw(raw: np.ndarray, t: np.ndarray) -> np.ndarray:
    """d(mean NLL)/d(raw outputs), (N, 7)."""
    mu, d, u, pre = gaussian_head(raw)
    r = t - mu
    e = np.exp(d)
    z1 = e[:, 0] * r[:, 0] + u * r[:, 1]
    z2 = e[:, 1] * r[:, 1]
    z3 = e[:, 2] * r[:, 2]
    g = np.zeros_like(raw)
    g[:, 0] = -z1 * e[:, 0]
    g[:, 1] = -(z1 * u + z2 * e[:, 1])
    g[:, 2] = -z3 * e[:, 2]
    dd = np.stack([z1 * e[:, 0] * r[:, 0] - 1.0, z2 * e[:, 1] * r[:, 1] - 1.0, z3 * e[:, 2] * r[:, 2] - 1.0], axis=1)
    dd *= 1.0 - np.tanh(pre / D_MAX) ** 2
    g[:, 3], g[:, 4], g[:, 6] = dd[:, 0], dd[:, 1], dd[:, 2]
    g[:, 5] = z1 * r[:, 1]
    return g / raw.shape[0]


def backward(layers, acts, g_out):
    grads = [None] * len(layers)
    g = g_out
    for k in range(len(layers) - 1, -1, -1):
        W, _ = layers[k]
        grads[k] = (acts[k].T @ g, g.sum(axis=0))
        if k > 0:
            g = (g @ W.T) * (1.0 - acts[k] ** 2)
    return grads


def loss_and_grads(layers, x, t, weight_decay):
    raw, acts = mlp_forward(layers, x)
    loss = float(gaussian_nll(raw, t).mean()) + 0.5 * weight_decay * sum(float((W**2).sum()) for W, _ in layers)
    grads = backward(layers, acts, nll_grad_raw(raw, t))
    grads = [(gW + weight_decay * W, gb) for (gW, gb), (W, _) in zip(grads, layers)]
    return loss, grads


def train(x_tr, t_tr, x_va, t_va, hidden, lr, weight_decay, seed=NUMPY_SEED, batch=128, max_epochs=3000,
          patience=150) -> dict:
    rng = np.random.default_rng(seed)
    layers = init_layers(rng, x_tr.shape[1], hidden)
    m = [(np.zeros_like(W), np.zeros_like(b)) for W, b in layers]
    v = [(np.zeros_like(W), np.zeros_like(b)) for W, b in layers]
    b1, b2, eps = 0.9, 0.999, 1e-8
    step = 0
    best = (np.inf, None, -1)
    history = []
    for epoch in range(max_epochs):
        order = rng.permutation(x_tr.shape[0])
        for a in range(0, order.size, batch):
            idx = order[a : a + batch]
            _, grads = loss_and_grads(layers, x_tr[idx], t_tr[idx], weight_decay)
            step += 1
            new_layers = []
            for k, ((W, b), (gW, gb)) in enumerate(zip(layers, grads)):
                mW, mb = m[k]
                vW, vb = v[k]
                mW = b1 * mW + (1 - b1) * gW
                mb = b1 * mb + (1 - b1) * gb
                vW = b2 * vW + (1 - b2) * gW**2
                vb = b2 * vb + (1 - b2) * gb**2
                m[k], v[k] = (mW, mb), (vW, vb)
                c1, c2 = 1 - b1**step, 1 - b2**step
                new_layers.append((W - lr * (mW / c1) / (np.sqrt(vW / c2) + eps),
                                   b - lr * (mb / c1) / (np.sqrt(vb / c2) + eps)))
            layers = new_layers
        val = float(gaussian_nll(mlp_forward(layers, x_va)[0], t_va).mean())
        tr = float(gaussian_nll(mlp_forward(layers, x_tr)[0], t_tr).mean())
        history.append((epoch, tr, val))
        if val < best[0]:
            best = (val, [(W.copy(), b.copy()) for W, b in layers], epoch)
        elif epoch - best[2] >= patience:
            break
    return {"layers": best[1], "best_epoch": best[2], "val_nll_std": best[0], "epochs_run": len(history),
            "history": history}


# ------------------------------------------------------------------ evaluation
def analytic_replay(row: dict, cfg: AdaptiveConfig) -> HoleLocalizer:
    """C's localizer after this (first) contact, rebuilt from the record (for the integration diagnostic)."""
    rec = row["record"]
    spec = resolve_connector(all_conditions()[row["condition"]])
    sigma_xy = max(rec["vision_xy_sigma_mm"], cfg.min_prior_sigma_mm) * MM
    loc = HoleLocalizer(
        spec, prior_sigma=float(np.hypot(cfg.prior_sigma_scale * sigma_xy, rec["vision_bias_mm"] * MM)),
        extent=cfg.search_extent_mm * MM, resolution=cfg.search_resolution_mm * MM, cop_sigma=cfg.cop_sigma_mm * MM,
        outlier_weight=cfg.localizer_outlier_weight, entry_likelihood=cfg.localizer_entry_likelihood,
        band_stick_probability=cfg.localizer_band_stick_probability,
        prior_uniform_weight=cfg.localizer_prior_uniform_weight, exclude_fraction=cfg.localizer_exclude_fraction,
        exclude_min_cells=cfg.localizer_exclude_min_cells, min_support=cfg.localizer_min_support_mm * MM,
    )
    sigma = (cfg.cop_sigma_mm if rec["cop_clean"] else cfg.unclean_cop_sigma_mm) * MM
    cop = None if rec["cop_mm"] is None else np.asarray(rec["cop_mm"]) * MM
    loc.update_blocked(np.asarray(rec["probe_xy_mm"]) * MM, cop, cop_sigma=sigma)
    return loc


def calibration(err: np.ndarray, prec: np.ndarray) -> dict:
    """Fraction of true offsets inside the predicted 1- and 2-sigma regions (2D: Mahalanobis radius)."""
    m2 = np.einsum("ni,nij,nj->n", err, prec, err)
    return {"inside_1sigma": float((m2 <= 1.0).mean()), "inside_2sigma": float((m2 <= 4.0).mean()),
            "expected_1sigma": 1.0 - float(np.exp(-0.5)), "expected_2sigma": 1.0 - float(np.exp(-2.0))}


def evaluate(model: ContactPrior, rows: list[dict], weights=(0.25, 0.5, 1.0), replay: bool = True) -> dict:
    if not rows:
        return {"n": 0}
    recs = [r["record"] for r in rows]
    o, h = targets(rows)
    pred = model.predict(recs)
    t = (o - model.y_mean) / model.y_std
    nll_std = gaussian_nll(model.raw(recs), t)
    nll = nll_std + float(np.log(model.y_std).sum())  # nats per contact, physical units (mm, mm, deg)
    err_m = pred["mean"][:, :2] - h[:, :2]
    ana = np.array([r["record"]["analytic_mean_mm"] for r in rows])
    ana_cov = np.array([r["record"]["analytic_cov_mm2"] for r in rows])
    err_a = ana - h[:, :2]
    err_v = -h[:, :2]  # the vision estimate itself
    first = np.array([r["record"]["attempt"] == 1 for r in rows])

    def mae(e, mask=None):
        e = e if mask is None else e[mask]
        if e.shape[0] == 0:
            return None
        n = np.hypot(e[:, 0], e[:, 1])
        return {"x": float(np.abs(e[:, 0]).mean()), "y": float(np.abs(e[:, 1]).mean()),
                "radial_mean": float(n.mean()), "radial_median": float(np.median(n))}

    yaw_z = (pred["mean"][:, 2] - h[:, 2]) / pred["sigma_yaw_deg"]
    out = {
        "n": len(rows), "n_first_contact": int(first.sum()),
        "nll_nats": float(nll.mean()),
        "nll_xy_only_nats": float((nll - (0.5 * yaw_z**2 + np.log(pred["sigma_yaw_deg"])
                                          + 0.5 * np.log(2 * np.pi))).mean()),
        "mae_mm": {"learned": mae(err_m), "analytic_posterior_mean": mae(err_a), "vision_estimate": mae(err_v)},
        "mae_mm_first_contact": {"learned": mae(err_m, first), "analytic_posterior_mean": mae(err_a, first),
                                 "vision_estimate": mae(err_v, first)},
        "calibration_xy": {"learned": calibration(err_m, pred["precision_xy"]),
                           "analytic_gaussian_approx": calibration(err_a, np.linalg.inv(ana_cov + 1e-12 * np.eye(2)))},
        "calibration_yaw": {"inside_1sigma": float((np.abs(yaw_z) <= 1).mean()),
                            "inside_2sigma": float((np.abs(yaw_z) <= 2).mean()),
                            "expected_1sigma": 0.6827, "expected_2sigma": 0.9545},
        "yaw_mae_deg": {"learned": float(np.abs(pred["mean"][:, 2] - h[:, 2]).mean()),
                        "vision_estimate": float(np.abs(h[:, 2]).mean())},
        "median_predicted_sigma_xy_mm": float(np.median(np.sqrt(np.linalg.eigvalsh(pred["cov_xy"])).mean(axis=1))),
        "by_condition": {},
    }
    for cond in sorted({r["condition"] for r in rows}):
        mask = np.array([r["condition"] == cond for r in rows])
        out["by_condition"][cond] = {
            "n": int(mask.sum()), "nll_nats": float(nll[mask].mean()),
            "mae_mm": {"learned": mae(err_m, mask), "analytic_posterior_mean": mae(err_a, mask),
                       "vision_estimate": mae(err_v, mask)},
            "calibration_xy_learned": calibration(err_m[mask], pred["precision_xy"][mask]),
        }
    if replay:
        # Offline integration diagnostic on first contacts: C's posterior after the contact, then
        # with the learned term at each candidate weight (no simulation; closed loop decides).
        cfg = AdaptiveConfig()
        rep = {"replay_matches_recorded_mm": None, "posterior_mean_mae_mm": {}}
        idx = np.flatnonzero(first)
        dev = []
        means = {w: [] for w in (0.0, *weights)}
        for i in idx:
            loc = analytic_replay(rows[i], cfg)
            m0 = loc.mean() / MM
            dev.append(float(np.hypot(*(m0 - ana[i]))))
            mu_m, P_m = model.localizer_term(recs[i])
            base = loc.log_post.copy()
            for w in means:
                loc.log_post = base.copy()
                if w > 0:
                    loc.update_gaussian(mu_m, P_m, w, LearnedPriorConfig().outlier_weight)
                means[w].append(loc.mean() / MM)
        rep["replay_matches_recorded_mm"] = float(max(dev)) if dev else None
        for w, ms in means.items():
            rep["posterior_mean_mae_mm"][str(w)] = mae(np.array(ms) - h[idx, :2]) if ms else None
        out["first_contact_integration_replay"] = rep
    return out


# ------------------------------------------------------------------ main
def git_info() -> dict:
    def run(*a):
        try:
            return subprocess.check_output(["git", *a], cwd=REPO_ROOT, text=True).strip()
        except Exception:  # noqa: BLE001
            return "unknown"
    return {"commit": run("rev-parse", "HEAD"),
            "dirty": bool(run("status", "--porcelain", "--untracked-files=no", "--", ".", ":(exclude)results"))}


def consistent_fixture_dynamics(fds: list[dict], rel_tol: float) -> dict:
    """The first dataset's fixture dynamics, after checking every dataset agrees within ``rel_tol``."""
    first = fds[0]

    def same(a, b):
        if a is None or b is None:
            return a is None and b is None
        return abs(a - b) <= rel_tol * max(abs(a), abs(b))

    for fd in fds[1:]:
        if set(fd) != set(first) or not all(same(v, fd[k]) for k, v in first.items()):
            raise SystemExit(f"datasets disagree on the fixture dynamics: {fds}")
    return first


def _rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def standardize(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    std = np.where(std > 1e-9, std, 1.0)  # constant inputs (e.g. no vision bias anywhere) pass through
    return mean, std


def model_json(backend, feature_set, names, x_mean, x_std, y_mean, y_std, layers, meta) -> dict:
    return {
        "format": FORMAT, "backend": backend, "feature_set": feature_set, "feature_names": list(names),
        "x_mean": x_mean.tolist(), "x_std": x_std.tolist(), "target_names": list(TARGET_NAMES),
        "y_mean": y_mean.tolist(), "y_std": y_std.tolist(), "activation": "tanh",
        "layers": [{"W": W.tolist(), "b": b.tolist()} for W, b in layers],
        "applies_to_kinds": ["surface_block"], "integration_weight": None, **meta,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--backend", default="gantry")
    ap.add_argument("--train", default="train_main,train_noise05")
    ap.add_argument("--val", default="validation")
    ap.add_argument("--dev", default="dev_seed2026")
    ap.add_argument("--feature-set", choices=sorted(FEATURE_SETS), default="contact")
    ap.add_argument("--install", action="store_true", help="also write assets/models/contact_prior_<backend>.json")
    ap.add_argument("--weight", type=float, default=None, help="integration weight chosen on the validation seed")
    ap.add_argument("--weight-source", default="", help="file the weight choice comes from (recorded in the model)")
    ap.add_argument("--install-existing", action="store_true",
                    help="install the already trained <root>/models/<backend>_<set>.json (no retraining)")
    ap.add_argument("--root", default="results/w9_development", help="data and model root, relative to the repository")
    args = ap.parse_args()
    data_root, models = REPO_ROOT / args.root / "data", REPO_ROOT / args.root / "models"
    if args.install_existing:
        return install(json.loads((models / f"{args.backend}_{args.feature_set}.json").read_text()), args)
    t0 = time.time()
    tr_rows = load_rows(args.backend, args.train.split(","), set(TRAIN_BASE_SEEDS), data_root)
    va_rows = load_rows(args.backend, [args.val], {VALIDATION_SEED}, data_root)
    dev_dir = data_root / args.backend / args.dev
    dev_rows = load_rows(args.backend, [args.dev], {2026}, data_root) if (dev_dir / "contacts.jsonl.gz").exists() else []
    names = FEATURE_SETS[args.feature_set]
    x_tr_raw = feature_matrix([r["record"] for r in tr_rows], names)
    x_va_raw = feature_matrix([r["record"] for r in va_rows], names)
    o_tr, _ = targets(tr_rows)
    o_va, _ = targets(va_rows)
    x_mean, x_std = standardize(x_tr_raw)
    y_mean, y_std = standardize(o_tr)
    x_tr, x_va = (x_tr_raw - x_mean) / x_std, (x_va_raw - x_mean) / x_std
    t_tr, t_va = (o_tr - y_mean) / y_std, (o_va - y_mean) / y_std
    print(f"{args.backend}/{args.feature_set}: {len(tr_rows)} train / {len(va_rows)} val / {len(dev_rows)} dev "
          f"surface contacts, {len(names)} features")
    search = []
    best = None
    for hidden, lr, wd in itertools.product(GRID["hidden"], GRID["lr"], GRID["weight_decay"]):
        res = train(x_tr, t_tr, x_va, t_va, hidden, lr, wd)
        entry = {"hidden": list(hidden), "lr": lr, "weight_decay": wd, "best_epoch": res["best_epoch"],
                 "epochs_run": res["epochs_run"], "val_nll_nats": res["val_nll_std"] + float(np.log(y_std).sum()),
                 "train_nll_nats_at_best": None}
        tr_nll = float(gaussian_nll(mlp_forward(res["layers"], x_tr)[0], t_tr).mean()) + float(np.log(y_std).sum())
        entry["train_nll_nats_at_best"] = tr_nll
        search.append(entry)
        print(f"  hidden={hidden} lr={lr:g} wd={wd:g}: best epoch {res['best_epoch']}, "
              f"train NLL {tr_nll:.3f}, val NLL {entry['val_nll_nats']:.3f}")
        if best is None or entry["val_nll_nats"] < best[0]["val_nll_nats"]:
            best = (entry, res)
    entry, res = best
    meta = {
        "fixture_dynamics": None,
        "metadata": {
            "description": "W9 learned contact prior (development model, not a reported result)",
            "created_utc": datetime.now(timezone.utc).isoformat(), "git": git_info(),
            "numpy_seed": NUMPY_SEED, "numpy": np.__version__,
            "train_base_seeds": [min(TRAIN_BASE_SEEDS), max(TRAIN_BASE_SEEDS)], "validation_base_seed": VALIDATION_SEED,
            "dev_sanity_seed": 2026, "unused_training_seeds": [s for s in TRAIN_SEEDS if s not in TRAIN_BASE_SEEDS],
            "data": {"train": [_rel(data_root / args.backend / n) for n in args.train.split(",")],
                     "validation": _rel(data_root / args.backend / args.val)},
            "n_train": len(tr_rows), "n_val": len(va_rows),
            "conditions_train": sorted({r["condition"] for r in tr_rows}),
            "selected_hyperparameters": {k: entry[k] for k in ("hidden", "lr", "weight_decay", "best_epoch")},
            "selection": "lowest validation NLL over the grid; early stopping on validation NLL (patience 150 epochs)",
        },
    }
    # Fixture dynamics the data was collected on (a model applies only to a matching fixture):
    # the first training set's, after checking that every dataset agrees within the tolerance
    # G matches with (the tool's mass differs by a fraction of a percent between connectors).
    meta["fixture_dynamics"] = consistent_fixture_dynamics(
        [json.loads((data_root / args.backend / n / "summary.json").read_text())["fixture_dynamics"]
         for n in [*args.train.split(","), args.val]], LearnedPriorConfig().fixture_match_rel_tol)
    data = model_json(args.backend, args.feature_set, names, x_mean, x_std, y_mean, y_std, res["layers"], meta)
    model = ContactPrior(data)
    metrics = {
        "backend": args.backend, "feature_set": args.feature_set, "search": search,
        "selected": entry, "train": evaluate(model, tr_rows, replay=False), "validation": evaluate(model, va_rows),
        "dev_seed2026": evaluate(model, dev_rows), "history_best_run": res["history"],
        "wall_time_s": time.time() - t0,
    }
    data["metadata"]["metrics_summary"] = {
        split: {k: metrics[split].get(k) for k in ("n", "nll_nats", "mae_mm", "calibration_xy", "calibration_yaw")}
        for split in ("train", "validation", "dev_seed2026")
    }
    models.mkdir(parents=True, exist_ok=True)
    stem = f"{args.backend}_{args.feature_set}"
    (models / f"{stem}.json").write_text(json.dumps(data))
    (models / f"{stem}_metrics.json").write_text(json.dumps(metrics, indent=1))
    print(f"wrote {models / (stem + '.json')} and {stem}_metrics.json")
    for split in ("train", "validation", "dev_seed2026"):
        m = metrics[split]
        if not m.get("n"):
            continue
        print(f"  {split}: n={m['n']} NLL {m['nll_nats']:.3f}; MAE radial learned "
              f"{m['mae_mm']['learned']['radial_mean']:.3f} / analytic {m['mae_mm']['analytic_posterior_mean']['radial_mean']:.3f}"
              f" / vision {m['mae_mm']['vision_estimate']['radial_mean']:.3f} mm; 1/2-sigma "
              f"{m['calibration_xy']['learned']['inside_1sigma']:.2f}/{m['calibration_xy']['learned']['inside_2sigma']:.2f}")
    if args.install:
        install(data, args)


def install(data: dict, args) -> None:
    if args.weight is None:
        raise SystemExit("installing needs --weight (chosen on the validation seed)")
    data["integration_weight"] = args.weight
    data["metadata"]["integration_weight_source"] = args.weight_source
    dest = REPO_ROOT / "assets" / "models" / f"contact_prior_{args.backend}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data))
    print(f"installed {dest} (integration weight {args.weight})")


if __name__ == "__main__":
    main()
