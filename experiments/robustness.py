"""Full robustness benchmark: all conditions x all controllers, paired seeds.

Usage (from the repository root):

    python -m experiments.robustness --trials 100 --workers 8
    python -m experiments.robustness --trials 20 --conditions lateral_3mm,noise_1mm
    python -m experiments.robustness --list

Outputs land in ``results/<name>/``: ``trials.csv`` (one row per trial),
``summary.json`` / ``summary.csv`` (per condition x controller), ``events.json``
(controller event logs), ``config.json`` (full configuration, versions, git
commit) and, with ``--record N``, replayable trajectories. Plots are produced by
``python -m experiments.evaluate results/<name>``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from defex.config import REPO_ROOT
from defex.control.registry import CONTROLLERS
from defex.tasks.conditions import standard_conditions
from experiments.runner import default_workers, run_suite


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trials", type=int, default=100, help="trials per condition and controller")
    ap.add_argument("--workers", type=int, default=default_workers())
    ap.add_argument("--seed", type=int, default=2026, help="base seed (paired across controllers)")
    ap.add_argument("--conditions", type=str, default="", help="comma-separated condition names (default: all)")
    ap.add_argument("--controllers", type=str, default=",".join(CONTROLLERS), help="comma-separated controllers")
    ap.add_argument("--name", type=str, default="robustness", help="output folder name under results/")
    ap.add_argument("--record", type=int, default=0, help="save trajectories for the first N trials of each cell")
    ap.add_argument("--list", action="store_true", help="list the available conditions and exit")
    ap.add_argument("--no-plots", action="store_true")
    args = ap.parse_args()

    conds = standard_conditions()
    if args.list:
        for c in conds:
            print(f"{c.name:26s} [{c.group}] {c.description}")
        return
    if args.conditions:
        wanted = set(args.conditions.split(","))
        unknown = wanted - {c.name for c in conds}
        if unknown:
            raise SystemExit(f"unknown conditions: {sorted(unknown)}")
        conds = [c for c in conds if c.name in wanted]
    controllers = [c for c in args.controllers.split(",") if c]
    out = REPO_ROOT / "results" / args.name
    n_cells = len(conds) * len(controllers)
    print(
        f"DAIE robustness benchmark: {len(conds)} conditions x {len(controllers)} controllers x "
        f"{args.trials} trials = {n_cells * args.trials} trials on {args.workers} workers -> {out}"
    )
    run_suite(conds, controllers, args.trials, args.seed, args.workers, out, record_trajectories=args.record)
    print(f"wrote {out / 'trials.csv'} and {out / 'summary.json'}")
    if not args.no_plots:
        from experiments.evaluate import evaluate

        evaluate(Path(out))


if __name__ == "__main__":
    main()
