"""Run controller C under named AdaptiveConfig variants on paired development trials and save everything.

Used for the development measurements of W4 and W6, so their numbers trace to files:

    python -m experiments.compare_configs variants.json --conditions noise_2mm --trials 100 --name w4_localizer

``variants.json`` maps a name to AdaptiveConfig overrides. Output under results/<out>/<name>/:
trials.csv (one row per trial and variant), variants.json, summary.json.
"""

from __future__ import annotations

import argparse
import csv
import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np

from defex.config import REPO_ROOT, AdaptiveConfig
from defex.control.adaptive_fsm import AdaptiveInsertionController
from defex.tasks.conditions import conditions_by_name, heldout_conditions_by_name
from defex.tasks.insertion import InsertionTask
from defex.tasks.scenarios import sample_scenario
from experiments.runner import default_workers, environment_info, nominal_socket_pose

_TASK: InsertionTask | None = None


def _conditions() -> dict:
    return {**conditions_by_name(), **heldout_conditions_by_name()}


def _job(variant: str, overrides: dict, cond: str, idx: tuple[int, ...], seed: int) -> list[dict]:
    global _TASK
    if _TASK is None:
        _TASK = InsertionTask()
    c = _conditions()[cond]
    nominal = nominal_socket_pose(c, _TASK.fixture)
    out = []
    for i in idx:
        r = _TASK.run(AdaptiveInsertionController(replace(AdaptiveConfig(), **overrides)),
                      sample_scenario(c, i, seed, nominal))
        out.append({"variant": variant, "condition": cond, "trial_index": i, "success": r.success,
                    "failure_reason": r.failure_reason, "cycle_time_s": r.cycle_time_s, "retries": r.retries,
                    "peak_contact_force_n": r.peak_contact_force_n, "protective_stop": r.protective_stop,
                    "false_accept": r.failure_reason == "false_accept", "wall_time_s": r.wall_time_s})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("variants", type=Path)
    ap.add_argument("--conditions", required=True)
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--name", required=True)
    ap.add_argument("--out", default="dev_compare")
    ap.add_argument("--workers", type=int, default=default_workers())
    args = ap.parse_args()
    variants = json.loads(args.variants.read_text())
    conds = args.conditions.split(",")
    out = REPO_ROOT / "results" / args.out / args.name
    out.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = [pool.submit(_job, v, ov, c, tuple(range(a, min(a + 5, args.trials))), args.seed)
                for v, ov in variants.items() for c in conds for a in range(0, args.trials, 5)]
        for f in futs:
            rows += f.result()
    with (out / "trials.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    summary = {}
    for v in variants:
        rs = [r for r in rows if r["variant"] == v]
        ok = sorted(r["cycle_time_s"] for r in rs if r["success"])
        summary[v] = {
            "per_condition_successes": {c: sum(r["success"] for r in rs if r["condition"] == c) for c in conds},
            "successes": len(ok), "n": len(rs), "false_accepts": sum(r["false_accept"] for r in rs),
            "protective_stops": sum(r["protective_stop"] for r in rs),
            "median_cycle_s": float(np.median(ok)) if ok else None,
            "p95_cycle_s": float(np.percentile(ok, 95)) if ok else None,
            "p95_peak_contact_force_n": float(np.percentile([r["peak_contact_force_n"] for r in rs], 95)),
            "mean_wall_time_per_trial_s": float(np.mean([r["wall_time_s"] for r in rs])),
        }
    (out / "variants.json").write_text(json.dumps(variants, indent=2))
    (out / "summary.json").write_text(json.dumps({"seed": args.seed, "conditions": conds, "trials": args.trials,
                                                  "environment": environment_info(), "summary": summary}, indent=2))
    for v, s in summary.items():
        print(v, s)


if __name__ == "__main__":
    main()
