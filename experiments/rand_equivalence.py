"""Rule-3 slice on randomized gantry fixtures (Checkpoint 2 review fix).

The rule-3 equivalence set runs the nominal gantry only. experiments/sim_randomization.py
also runs the gantry with its servo stiffnesses drawn from bands (angular kp 10-25 N m/rad,
linear kp 5-20 kN/m), so C's gantry behaviour must hold there as well. This runs chosen
variants of that family and writes one folder per variant (the trials of different variants
share condition, trial index and seed, so scripts/compare_trials.py compares them per folder):

    python -m experiments.rand_equivalence --seed 2026 --variants 2,4,6,11,12 \
        --controllers adaptive,spiral_rcc --trials 10 --out results/<folder> --workers 4

Output: <out>/variant_<k>/trials.csv and summary.json, and <out>/variants.json with each
variant's configuration and the fixture dynamics its backend reports. Only the libraries
that already existed on v0.2/w3-latch-physics are used, so the same file runs on that tree
(PYTHONPATH=<tree>) for the reference.
"""

from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

from defex.logging.metrics import TrialResult, summarize_overall, write_csv
from experiments.runner import environment_info
from experiments.sim_randomization import CONDITIONS, _TASKS, _job, variant_configs

DEV_SEEDS = {2026, 2027, 4001, *range(3001, 3041)}  # development, validation and training seeds only


def _row_to_result(row: dict) -> TrialResult:
    keep = {f: row[f] for f in TrialResult.__dataclass_fields__ if f in row and f not in ("disturbance", "events")}
    return TrialResult(**keep)


def _dynamics(k: int, seed: int) -> dict:
    """Fixture dynamics the variant's backend reports, after one trial loaded its scene."""
    _job(k, seed, "fixed", "nominal", (0,))
    fd = getattr(_TASKS[k].backend, "fixture_dynamics", None)
    return {} if fd is None else asdict(fd)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--variants", required=True, help="comma-separated variant numbers of experiments.sim_randomization")
    ap.add_argument("--controllers", default="adaptive,spiral_rcc")
    ap.add_argument("--conditions", default=",".join(CONDITIONS))
    ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    if args.seed not in DEV_SEEDS:
        raise SystemExit(f"seed {args.seed} is not a development, training or validation seed")
    variants = [int(v) for v in args.variants.split(",")]
    ctrls = args.controllers.split(",")
    conds = args.conditions.split(",")
    args.out.mkdir(parents=True, exist_ok=True)
    jobs = [(k, c, cond) for k in variants for c in ctrls for cond in conds]
    print(f"{len(jobs)} jobs x {args.trials} trials = {len(jobs) * args.trials} trials on {args.workers} workers", flush=True)
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = [(k, pool.submit(_job, k, args.seed, c, cond, tuple(range(args.trials)))) for k, c, cond in jobs]
        dyn = {k: pool.submit(_dynamics, k, args.seed) for k in variants}
        rows: dict[int, list[dict]] = {k: [] for k in variants}
        for k, f in futs:
            rows[k] += f.result()
        dynamics = {k: f.result() for k, f in dyn.items()}
    for k in variants:
        d = args.out / f"variant_{k}"
        d.mkdir(exist_ok=True)
        write_csv(rows[k], d / "trials.csv")
        (d / "summary.json").write_text(json.dumps(
            {"variant": k, "seed": args.seed, "overall": summarize_overall([_row_to_result(r) for r in rows[k]])},
            indent=2, default=float))
    (args.out / "variants.json").write_text(json.dumps({
        "seed": args.seed, "controllers": ctrls, "conditions": conds, "trials": args.trials,
        "variants": {k: {"config": variant_configs(k, args.seed)[2], "fixture_dynamics": dynamics[k]} for k in variants},
        "environment": environment_info(), "wall_time_s": time.time() - t0,
    }, indent=2, default=float))
    print(f"wrote {args.out} in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
