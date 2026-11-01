"""Calibration of the posterior G acts on, next to C's and the learned model's alone (Checkpoint 2 review).

Offline, no simulation. For each first surface contact of a split (the contacts G's
model is applied to first), rebuild C's hole localizer after its analytic update
(experiments.train_contact_prior.analytic_replay, checked against the recorded posterior
mean), then add the installed model's term as G does (weight and outlier floor of the
installed model and LearnedPriorConfig). For each posterior, the fraction of true mouth
positions outside its highest-density regions of mass 50% and 95% (expected 0.50 / 0.05),
and the mean radial error of its mean. The learned model alone is a Gaussian, whose
highest-density region of mass p is the ellipse with Mahalanobis radius^2 <= -2 ln(1 - p).

    python -m experiments.cp2_posterior_calibration --out results/checkpoint2_prep/review_fixes/posterior_calibration.json

Splits: dev seed 2026 (held out from every choice) and validation seed 4001 (the selection
split: early stopping, grid, input set and weight were chosen on it), gantry and arm.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from defex.config import MM, REPO_ROOT, AdaptiveConfig, LearnedPriorConfig
from defex.recovery.learned_prior import DEFAULT_MODEL_DIR, ContactPrior
from experiments.train_contact_prior import VALIDATION_SEED, analytic_replay, load_rows, targets

SPLITS = (
    ("gantry", "results/w9_development/data", "dev_seed2026", 2026),
    ("gantry", "results/w9_development/data", "validation", VALIDATION_SEED),
    ("arm", "results/checkpoint2_prep/arm_prior/data", "dev_seed2026", 2026),
    ("arm", "results/checkpoint2_prep/arm_prior/data", "validation", VALIDATION_SEED),
)
LEVELS = (0.5, 0.95)


def hpd_mass_above_truth(posterior: np.ndarray, hx: np.ndarray, hy: np.ndarray, h: np.ndarray) -> float:
    """Posterior mass on cells more probable than the cell holding the truth (> p: truth outside the p region)."""
    i = np.unravel_index(np.argmin((hx - h[0]) ** 2 + (hy - h[1]) ** 2), hx.shape)
    return float(posterior[posterior > posterior[i]].sum())


def evaluate_split(backend: str, root: str, split: str, seed: int, model: ContactPrior) -> dict:
    cfg, pc = AdaptiveConfig(), LearnedPriorConfig()
    rows = [r for r in load_rows(backend, [split], {seed}, REPO_ROOT / root) if r["record"]["attempt"] == 1]
    _, h_all = targets(rows)
    weight = float(model.integration_weight)
    out = {"backend": backend, "split": split, "base_seed": seed, "n_first_contacts": len(rows),
           "model": Path(model.path).name, "weight": weight, "outlier_weight": pc.outlier_weight}
    mass = {"C": [], "G": []}
    err = {"C": [], "G": [], "learned": []}
    m2 = []
    off_grid = 0
    replay_err = 0.0
    for r, h in zip(rows, h_all[:, :2] * MM):
        loc = analytic_replay(r, cfg)
        replay_err = max(replay_err, float(np.abs(loc.mean() / MM - np.asarray(r["record"]["analytic_mean_mm"])).max()))
        off_grid += int(np.abs(h).max() > np.abs(loc.hx).max())
        mass["C"].append(hpd_mass_above_truth(loc.posterior, loc.hx, loc.hy, h))
        err["C"].append(float(np.hypot(*(loc.mean() - h))) / MM)
        mean, prec = model.localizer_term(r["record"])
        d = h - mean
        m2.append(float(d @ prec @ d))
        err["learned"].append(float(np.hypot(*d)) / MM)
        loc.update_gaussian(mean, prec, weight, pc.outlier_weight)
        mass["G"].append(hpd_mass_above_truth(loc.posterior, loc.hx, loc.hy, h))
        err["G"].append(float(np.hypot(*(loc.mean() - h))) / MM)
    m2 = np.array(m2)
    out["outside_hpd"] = {
        **{k: {f"{p:g}": float(np.mean(np.array(v) > p)) for p in LEVELS} for k, v in mass.items()},
        "learned": {f"{p:g}": float(np.mean(m2 > -2.0 * np.log(1.0 - p))) for p in LEVELS},
        "expected": {f"{p:g}": 1.0 - p for p in LEVELS},
    }
    out["mean_radial_error_mm"] = {k: float(np.mean(v)) for k, v in err.items()}
    out["truth_outside_grid"] = off_grid
    out["replay_max_abs_error_mm"] = replay_err
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--v1-copies", action="store_true",
                    help="v0.2c: read the v1 models from results/v0.2c_learned_prior/models/v1_contact_prior_*.json "
                         "(byte copies of the Checkpoint 2 models, after a v2 model is installed)")
    args = ap.parse_args()
    results = []
    for backend, root, split, seed in SPLITS:
        path = (REPO_ROOT / "results" / "v0.2c_learned_prior" / "models" / f"v1_contact_prior_{backend}.json"
                if args.v1_copies else DEFAULT_MODEL_DIR / f"contact_prior_{backend}.json")
        model = ContactPrior.from_json(path)
        results.append(evaluate_split(backend, root, split, seed, model))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2))
    print("| Backend | Split | n | Outside 50% HPD: C / G / learned (expected 0.50) | Outside 95% HPD: C / G / learned "
          "(expected 0.05) | Mean radial error C / G / learned (mm) |")
    print("|---|---|---|---|---|---|")
    for r in results:
        o, e = r["outside_hpd"], r["mean_radial_error_mm"]
        name = "dev 2026 (held out)" if r["base_seed"] == 2026 else "validation 4001 (selection split)"
        print(f"| {r['backend']} | {name} | {r['n_first_contacts']} | "
              f"{o['C']['0.5']:.2f} / {o['G']['0.5']:.2f} / {o['learned']['0.5']:.2f} | "
              f"{o['C']['0.95']:.3f} / {o['G']['0.95']:.3f} / {o['learned']['0.95']:.3f} | "
              f"{e['C']:.2f} / {e['G']:.2f} / {e['learned']:.2f} |")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
