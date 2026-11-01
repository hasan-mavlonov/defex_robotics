"""Grid-search tuning of the conventional baselines (D, E, F) on the development seed.

Every baseline gets a tuning budget at least as large as controller C's: C was
tuned by hand on base seed 2026 over the same condition families. This script
runs a full grid over each baseline's free parameters on seed 2026 and ranks the
settings by success rate, then by median cycle time. It never touches a reported
benchmark seed.

    python -m experiments.tune_baselines --controller spiral --stage coarse
    python -m experiments.tune_baselines --controller spiral --stage confirm --top 5

v0.2c, the same protocol on the UR5e arm (results/v0.2c_arm_baselines/SELECTION_RULE.md):

    python -m experiments.tune_baselines --backend arm --controller spiral --stage coarse \
        --out v0.2c_arm_baselines/tuning --trials 5

On the arm, settings are applied to the controller's stiff-fixture config (the one it runs on
the arm); the grids, conditions and stages are the ARM_* ones below.

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
from pathlib import Path

import os

import numpy as np

from defex.config import REPO_ROOT
from defex.control.registry import CONTROLLERS
from defex.logging.metrics import is_escape
from defex.tasks.conditions import conditions_by_name, latching_conditions_by_name
from defex.tasks.insertion import InsertionTask
from defex.tasks.scenarios import sample_scenario
from experiments.runner import default_workers, git_dirty, git_revision, make_backend, nominal_socket_pose

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

# v0.2c: the W1 protocol on the UR5e arm, scaled to the compute available (SELECTION_RULE.md there).
# Conditions: W1's six hardest plus the Micro-Fit good parts, which W1 (before W3) never had and
# the reported benchmark does. Confirm: W1's 18 development families plus the three Micro-Fit
# good-part conditions. The bad-part conditions are never tuned on (they cannot succeed).
ARM_COARSE_CONDITIONS = COARSE_CONDITIONS + ("mf_nominal", "mf_noise_1mm")
ARM_CONFIRM_CONDITIONS = CONFIRM_CONDITIONS + ("mf_nominal", "mf_moderate", "mf_noise_1mm")
# Coarse: W1 coarse and edge values, without the values that never made the gantry top five
# (8 N search force, 2.0 and 2.5 mm pitch, 20 mm/s), push distance held at both gantry winners' 0.5 mm.
ARM_SPIRAL_GRID = {
    "search_force_n": [2.0, 3.0, 5.0],
    "spiral_pitch_mm": [0.5, 1.0, 1.5],
    "spiral_speed_mm_s": [2.5, 5.0, 10.0],
    "search_lateral_stiffness_n_per_mm": [0.0, 2.0, 0.5],
}
# Fine: W1 fine values (one attempt dropped: it never ranked on the gantry), around the top coarse settings.
ARM_SPIRAL_FINE = {
    "insert_force_n": [3.0, 5.0, 8.0],
    "max_attempts": [2, 3],
    "seat_margin_mm": [0.5, 1.0],
}
# Speed/push/lag (arm only). The W5 contact-speed rule scales D's and F's guarded speeds by 0.40 on the
# UR5e (6.3 kg at the tool): Flexiv InsertComp insertVel (default 10 mm/s), used here for the descent
# and the insertion alike, is offered at 10 or 25 mm/s nominal (4 or 10 mm/s on the arm), with W1's
# push distances, and with or without continuing from the measured position when the hole is found
# (SpiralSearchConfig.hole_at_measured_position: the UR5e's 0.2 s lag puts the command ahead of the plug).
ARM_SPIRAL_SPEED = [
    {"hole_push_mm": push, "insert_speed_mm_s": v, "descent_speed_mm_s": v, "hole_at_measured_position": lag}
    for push in (0.3, 0.5, 1.0) for v in (10.0, 25.0) for lag in (False, True)
]
# Two-speed guarded moves (arm only, amendment 1 of SELECTION_RULE.md): the speed stage showed that a
# faster single speed aborts on the floor contact (20 N). Offered on the speed winner: a free speed in
# the cavity of 15 mm/s nominal (C's free_insert_speed_mm_s) or 25 mm/s, slowing to the tuned speed
# 2 mm (C's near_bottom_margin_mm) or 4 mm above the floor.
ARM_SPIRAL_SPEED2 = [{"free_speed_mm_s": v, "near_floor_margin_mm": m} for v in (15.0, 25.0) for m in (2.0, 4.0)]
ARM_CORRECTION_GRID = CORRECTION_GRID

_TASK: InsertionTask | None = None


def _grid(spec: dict[str, list]) -> list[dict]:
    keys = list(spec)
    return [dict(zip(keys, vals)) for vals in itertools.product(*(spec[k] for k in keys))]


def _condition(name: str):
    return {**conditions_by_name(), **latching_conditions_by_name()}[name]


def _job(controller: str, overrides: dict, cond_name: str, indices: tuple[int, ...]) -> list[dict]:
    global _TASK
    if _TASK is None:
        _TASK = InsertionTask(backend=make_backend())
    cond = _condition(cond_name)
    if cond.defect is not None:
        raise ValueError("bad-part conditions are not tuned on")
    nominal = nominal_socket_pose(cond, _TASK.fixture)
    cls = CONTROLLERS[controller]
    out = []
    for i in indices:
        ctrl = cls()
        if os.environ.get("DEFEX_BACKEND", "gantry") == "arm":
            ctrl.stiff_fixture_cfg = replace(ctrl.stiff_fixture_cfg, **overrides)  # what D, E, F run on the arm
        else:
            ctrl.cfg = replace(ctrl.cfg, **overrides)
            if hasattr(ctrl, "dwell_s"):
                ctrl.dwell_s = ctrl.cfg.dwell_s
        r = _TASK.run(ctrl, sample_scenario(cond, i, DEV_SEED, nominal))
        out.append({"success": r.success, "cycle": r.cycle_time_s, "stop": r.protective_stop,
                    "false_accept": r.failure_reason == "false_accept", "escape": is_escape(r),
                    "time_limit": r.failure_reason == "aborted:time_limit"})
    return out


def evaluate(controller: str, settings: list[dict], conditions: tuple[str, ...], trials: int, workers: int) -> list[dict]:
    jobs = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for k, ov in enumerate(settings):
            for cond in conditions:
                jobs.append((k, pool.submit(_job, controller, ov, cond, tuple(range(trials)))))
        rows = [dict(setting=k, **settings[k], n=0, ok=0, stops=0, false_accepts=0, escapes=0, time_limits=0, cycles=[])
                for k in range(len(settings))]
        t0 = time.time()
        for done, (k, fut) in enumerate(jobs, 1):
            for r in fut.result():
                row = rows[k]
                row["n"] += 1
                row["ok"] += r["success"]
                row["stops"] += r["stop"]
                row["false_accepts"] += r["false_accept"]
                row["escapes"] += r["escape"]
                row["time_limits"] += r["time_limit"]
                row["cycles"].append(r["cycle"])
            if done % 50 == 0:
                print(f"  {done}/{len(jobs)} jobs, {time.time() - t0:.0f} s", flush=True)
    for row in rows:
        c = np.array(row.pop("cycles"))
        row["success_rate"] = row["ok"] / row["n"]
        row["median_cycle_s"] = float(np.median(c))
        row["p95_cycle_s"] = float(np.percentile(c, 95))
    # Ranking rule: success rate, then median cycle time, then 95th-percentile cycle time
    # (the p95 tie-break is v0.2c's; W1 stated it but sorted on the first two only).
    rows.sort(key=lambda r: (-r["success_rate"], r["median_cycle_s"], r["p95_cycle_s"]))
    return rows


def _arm_stage(args, out: Path) -> tuple[list[dict], tuple[str, ...]]:
    """Settings and conditions for one stage of the v0.2c arm protocol."""
    spiral = args.controller.startswith("spiral")
    if args.stage == "coarse":
        return _grid(ARM_SPIRAL_GRID if spiral else ARM_CORRECTION_GRID), ARM_COARSE_CONDITIONS
    if not spiral and args.stage != "confirm":
        raise SystemExit("E has a coarse and a confirm stage only")
    prev = {"fine": "coarse", "speed": "fine", "speed2": "speed", "confirm": "speed2" if spiral else "coarse"}[args.stage]
    keys = {"coarse": list(ARM_SPIRAL_GRID), "fine": list(ARM_SPIRAL_GRID) + list(ARM_SPIRAL_FINE),
            "speed": list(ARM_SPIRAL_GRID) + list(ARM_SPIRAL_FINE) + list(ARM_SPIRAL_SPEED[0])}.get(prev)
    if not spiral:
        keys = list(ARM_CORRECTION_GRID)
    if prev == "speed2":
        # Confirm ranks the speed and speed2 settings together (same 21 conditions and trials); a
        # speed-stage setting has the two-speed option off.
        keys = list(ARM_SPIRAL_GRID) + list(ARM_SPIRAL_FINE) + list(ARM_SPIRAL_SPEED[0]) + list(ARM_SPIRAL_SPEED2[0])
        off = {"free_speed_mm_s": "0.0", "near_floor_margin_mm": "2.0"}
        rows = [{**off, **r} for r in csv.DictReader((out / f"tuning_{args.controller}_speed.csv").open())]
        rows += list(csv.DictReader((out / f"tuning_{args.controller}_speed2.csv").open()))
        rows.sort(key=lambda r: (-int(r["ok"]) / int(r["n"]), float(r["median_cycle_s"]), float(r["p95_cycle_s"])))
        prev_rows = rows[: args.top]
    else:
        prev_rows = list(csv.DictReader((out / f"tuning_{args.controller}_{prev}.csv").open()))[: args.top]
    base = [{k: _parse(k, r[k]) for k in keys} for r in prev_rows]
    if args.stage == "fine":
        return [{**b, **f} for b in base for f in _grid(ARM_SPIRAL_FINE)], ARM_COARSE_CONDITIONS
    if args.stage == "speed":
        return [{**base[0], **e} for e in ARM_SPIRAL_SPEED], ARM_CONFIRM_CONDITIONS
    if args.stage == "speed2":
        return [{**base[0], **e} for e in ARM_SPIRAL_SPEED2], ARM_CONFIRM_CONDITIONS
    return base, ARM_CONFIRM_CONDITIONS


def _parse(key: str, value: str):
    if key == "max_attempts":
        return int(float(value))
    if key == "hole_at_measured_position":
        return {"True": True, "False": False}[value]
    return float(value)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--controller", required=True, choices=["spiral", "spiral_rcc", "correction_rcc"])
    ap.add_argument("--stage", choices=["coarse", "fine", "edge", "speed", "speed2", "confirm"], default="coarse")
    ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--top", type=int, default=5, help="settings carried from the previous stage")
    ap.add_argument("--out", default="benchmark_v0.2a/tuning")
    ap.add_argument("--workers", type=int, default=default_workers())
    ap.add_argument("--backend", choices=["gantry", "arm"], default="gantry",
                    help="arm: the v0.2c protocol on the UR5e (ARM_* grids and conditions)")
    ap.add_argument("--protocol", choices=["w1", "v02c"], default=None,
                    help="v02c: the ARM_* grids, conditions and stages on either backend (default: w1 on the "
                         "gantry, v02c on the arm); see results/v0.2c_gantry_baselines/SELECTION_RULE.md")
    args = ap.parse_args()
    if args.protocol is None:
        args.protocol = "v02c" if args.backend == "arm" else "w1"
    if args.backend == "arm" and args.protocol != "v02c":
        raise SystemExit("the arm runs the v02c protocol only")
    os.environ["DEFEX_BACKEND"] = args.backend
    out = REPO_ROOT / "results" / args.out
    out.mkdir(parents=True, exist_ok=True)

    spiral = args.controller.startswith("spiral")
    if args.protocol == "v02c":
        if args.stage == "edge":
            raise SystemExit("the v02c protocol has no edge stage (its coarse grid includes the edge values)")
        settings, conditions = _arm_stage(args, out)
    elif args.stage in ("speed", "speed2"):
        raise SystemExit("the speed stages are part of the arm protocol only")
    elif args.stage == "coarse":
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
    print(f"{args.controller} {args.stage} ({args.backend}): {len(settings)} settings x {len(conditions)} conditions x "
          f"{args.trials} trials = {len(settings) * len(conditions) * args.trials} trials, seed {DEV_SEED}")
    t0 = time.time()
    rows = evaluate(args.controller, settings, conditions, args.trials, args.workers)
    path = out / f"tuning_{args.controller}_{args.stage}.csv"
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (out / f"tuning_{args.controller}_{args.stage}.json").write_text(
        json.dumps({"seed": DEV_SEED, "conditions": conditions, "trials": args.trials, "backend": args.backend,
                    "protocol": args.protocol,
                    "top": args.top, "git_commit": git_revision(), "git_dirty": git_dirty(),
                    "wall_time_s": time.time() - t0}, indent=2)
    )
    for r in rows[:5]:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
