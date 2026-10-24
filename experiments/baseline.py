"""Baseline check: the three controllers under nominal and mild conditions.

A quick (about a minute) sanity run to execute after any change, before the full
robustness benchmark:

    python -m experiments.baseline                 # 20 paired trials per condition
    python -m experiments.baseline --trials 50 --workers 8

Conditions: nominal, lateral 1 mm (inside the lead-in capture range) and yaw 2 deg
(inside the cavity's yaw tolerance). Every controller is expected to insert
reliably here; a regression shows up immediately as a drop below 100%.
"""

from __future__ import annotations

import argparse

from defex.config import REPO_ROOT
from defex.control.registry import CONTROLLERS
from defex.tasks.conditions import conditions_by_name
from experiments.runner import default_workers, run_suite

BASELINE_CONDITIONS = ("nominal", "lateral_1mm", "yaw_2deg")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--workers", type=int, default=default_workers())
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--name", default="dev_baseline", help="output folder under results/ (dev_* is gitignored)")
    args = ap.parse_args()
    conds = [conditions_by_name()[n] for n in BASELINE_CONDITIONS]
    out = REPO_ROOT / "results" / args.name
    results = run_suite(conds, list(CONTROLLERS), args.trials, args.seed, args.workers, out)
    print(f"\n{'condition':14s} " + " ".join(f"{c:>12s}" for c in CONTROLLERS))
    ok = True
    for cond in BASELINE_CONDITIONS:
        rates = []
        for c in CONTROLLERS:
            rs = [r for r in results if r.condition == cond and r.controller == c]
            rate = sum(r.success for r in rs) / len(rs)
            ok &= rate == 1.0
            rates.append(f"{rate * 100:11.0f}%")
        print(f"{cond:14s} " + " ".join(rates))
    print("\nbaseline:", "PASS (all controllers 100%)" if ok else "CHECK: some controller below 100%")


if __name__ == "__main__":
    main()
