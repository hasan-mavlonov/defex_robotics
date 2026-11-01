"""Grid-search tuning of the conventional baselines (D, E, F) on the development seed.

Every baseline gets a tuning budget at least as large as controller C's: C was
tuned by hand on base seed 2026 over the same condition families. This script
runs a full grid over each baseline's free parameters on seed 2026 and ranks the
settings by success rate, then by median cycle time. It never touches a reported
benchmark seed.

    python -m experiments.tune_baselines --controller spiral --stage coarse
    python -m experiments.tune_baselines --controller spiral --stage confirm --top 5

Output: results/<out>/tuning_<controller>_<stage>.csv (one row per setting).
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

from defex.config import REPO_ROOT
from defex.control.registry import CONTROLLERS
from defex.tasks.conditions import conditions_by_name
from defex.tasks.insertion import InsertionTask
from defex.tasks.scenarios import sample_scenario
from experiments.runner import default_workers, nominal_socket_pose

DEV_SEED = 2026
COARSE_CONDITIONS = ("lateral_3mm", "yaw_5deg", "tilt_5deg", "noise_1mm", "noise_2mm", "friction_1")
CONFIRM_CONDITIONS = tuple(
    n for n in conditions_by_name() if not n.startswith("generalization")
)  # all development families; the two generalization conditions stay held out

SPIRAL_GRID = {
    "search_force_n": [3.0, 5.0, 8.0],
    "spiral_pitch_mm": [1.0, 1.5, 2.0, 2.5],
    "spiral_speed_mm_s": [5.0, 10.0, 20.0],
    "search_lateral_stiffness_n_per_mm": [0.0, 2.0, 0.5],
    "hole_push_mm": [0.5, 1.0, 2.0],
}
SPIRAL_FINE = {
    "insert_force_n": [3.0, 5.0, 8.0],
    "max_attempts": [1, 2, 3],
    "seat_margin_mm": [0.5, 1.0],
}
# Winners of the coarse grid sat on its edges (lowest force, pitch, speed, push):
# extend past them, down to Flexiv's minimum contact force of 2 N.
SPIRAL_EDGE = {
    "search_force_n": [2.0, 3.0],
    "spiral_pitch_mm": [0.5, 1.0],
    "spiral_speed_mm_s": [2.5, 5.0],
    "hole_push_mm": [0.3, 0.5],
}
CORRECTION_GRID = {
    "insert_speed_mm_s": [2.0, 4.0, 8.0],
    "overtravel_mm": [0.25, 0.5, 1.0],
    "approach_height_mm": [2.0, 5.0],
}

_TASK: InsertionTask | None = None


def _grid(spec: dict[str, list]) -> list[dict]:
    keys = list(spec)
    return [dict(zip(keys, vals)) for vals in itertools.product(*(spec[k] for k in keys))]


def _job(controller: str, overrides: dict, cond_name: str, indices: tuple[int, ...]) -> list[dict]:
    global _TASK
    if _TASK is None:
        _TASK = InsertionTask()
    cond = conditions_by_name()[cond_name]
    nominal = nominal_socket_pose(cond, _TASK.fixture)
    cls = CONTROLLERS[controller]
    out = []
    for i in indices:
        ctrl = cls()
        ctrl.cfg = replace(ctrl.cfg, **overrides)
        if hasattr(ctrl, "dwell_s"):
            ctrl.dwell_s = ctrl.cfg.dwell_s
        r = _TASK.run(ctrl, sample_scenario(cond, i, DEV_SEED, nominal))
        out.append({"success": r.success, "cycle": r.cycle_time_s, "stop": r.protective_stop,
                    "false_accept": r.failure_reason == "false_accept"})
    return out


def evaluate(controller: str, settings: list[dict], conditions: tuple[str, ...], trials: int, workers: int) -> list[dict]:
    jobs = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for k, ov in enumerate(settings):
            for cond in conditions:
                jobs.append((k, pool.submit(_job, controller, ov, cond, tuple(range(trials)))))
        rows = [dict(setting=k, **settings[k], n=0, ok=0, stops=0, false_accepts=0, cycles=[]) for k in range(len(settings))]
        t0 = time.time()
        for done, (k, fut) in enumerate(jobs, 1):
            for r in fut.result():
                row = rows[k]
                row["n"] += 1
                row["ok"] += r["success"]
                row["stops"] += r["stop"]
                row["false_accepts"] += r["false_accept"]
                row["cycles"].append(r["cycle"])
            if done % 50 == 0:
                print(f"  {done}/{len(jobs)} jobs, {time.time() - t0:.0f} s", flush=True)
    for row in rows:
        c = np.array(row.pop("cycles"))
        row["success_rate"] = row["ok"] / row["n"]
        row["median_cycle_s"] = float(np.median(c))
        row["p95_cycle_s"] = float(np.percentile(c, 95))
    rows.sort(key=lambda r: (-r["success_rate"], r["median_cycle_s"]))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--controller", required=True, choices=["spiral", "spiral_rcc", "correction_rcc"])
    ap.add_argument("--stage", choices=["coarse", "fine", "edge", "confirm"], default="coarse")
    ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--top", type=int, default=5, help="settings carried from the previous stage")
    ap.add_argument("--out", default="benchmark_v0.2a/tuning")
    ap.add_argument("--workers", type=int, default=default_workers())
    args = ap.parse_args()
    out = REPO_ROOT / "results" / args.out
    out.mkdir(parents=True, exist_ok=True)

    spiral = args.controller.startswith("spiral")
    if args.stage == "coarse":
        settings = _grid(SPIRAL_GRID if spiral else CORRECTION_GRID)
        conditions = COARSE_CONDITIONS
    else:
        prev = {"fine": "coarse", "edge": "fine"}.get(args.stage, "fine" if spiral else "coarse")
        if args.stage == "confirm" and spiral and (out / f"tuning_{args.controller}_edge.csv").exists():
            prev = "edge"
        prev_rows = list(csv.DictReader((out / f"tuning_{args.controller}_{prev}.csv").open()))[: args.top]
        keys = list(SPIRAL_GRID) + (list(SPIRAL_FINE) if prev in ("fine", "edge") else []) if spiral else list(CORRECTION_GRID)
        base = [{k: (int(float(r[k])) if k == "max_attempts" else float(r[k])) for k in keys} for r in prev_rows]
        if args.stage == "fine":
            settings = [{**b, **f} for b in base for f in _grid(SPIRAL_FINE)]
            conditions = COARSE_CONDITIONS
        elif args.stage == "edge":
            settings = [{**base[0], **e} for e in _grid(SPIRAL_EDGE)]
            conditions = CONFIRM_CONDITIONS
        else:
            settings = base
            conditions = CONFIRM_CONDITIONS
    print(f"{args.controller} {args.stage}: {len(settings)} settings x {len(conditions)} conditions x "
          f"{args.trials} trials = {len(settings) * len(conditions) * args.trials} trials, seed {DEV_SEED}")
    rows = evaluate(args.controller, settings, conditions, args.trials, args.workers)
    path = out / f"tuning_{args.controller}_{args.stage}.csv"
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (out / f"tuning_{args.controller}_{args.stage}.json").write_text(
        json.dumps({"seed": DEV_SEED, "conditions": conditions, "trials": args.trials}, indent=2)
    )
    for r in rows[:5]:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
