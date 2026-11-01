"""v0.2c diagnosis of D and F on the arm (offline; reads ground truth for the report only).

    python -m experiments.v02c_diagnose jams --out results/v0.2c_arm_baselines/diagnosis/false_jams.json
    python -m experiments.v02c_diagnose speed --out results/v0.2c_arm_baselines/diagnosis/single_speed_25.json

``jams``: D with its gantry config on the arm (what it ran before v0.2c), trials whose events show a
jam retry after the hole was found (dev seed 2026, before/arm_dev2026_standard5). At each jam: the true
depth of the plug below the socket mouth, the estimated depth, and the "face" depth D had recorded.

``speed``: D with the fine-stage winner of the arm tuning and a single guarded speed of 25 mm/s nominal
(the speed stage's fast setting), on nominal trials 0-2: failure reason and peak measured force.
Development seeds only.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import replace
from pathlib import Path

import numpy as np

DEV_SEEDS = (2026, 2027)
JAM_TRIALS = ("nominal|1", "lateral_3mm|13", "noise_1mm|0", "friction_1|9")
FINE_WINNER = dict(search_force_n=5.0, spiral_pitch_mm=1.0, spiral_speed_mm_s=10.0, search_lateral_stiffness_n_per_mm=0.5,
                   insert_force_n=5.0, max_attempts=2, seat_margin_mm=1.0, hole_push_mm=0.5)


def _setup():
    os.environ["DEFEX_BACKEND"] = "arm"
    from defex.tasks.conditions import conditions_by_name
    from defex.tasks.insertion import InsertionTask
    from experiments.runner import make_backend, nominal_socket_pose

    return conditions_by_name(), InsertionTask(backend=make_backend()), nominal_socket_pose


def jams(seed: int) -> list[dict]:
    from defex.config import MM, SpiralSearchConfig
    from defex.control.spiral_search import SpiralSearchController
    from defex.tasks.scenarios import sample_scenario

    conds, task, nominal_pose = _setup()
    out = []
    for key in JAM_TRIALS:
        cond_name, idx = key.split("|")
        cond = conds[cond_name]
        ctrl = SpiralSearchController(stiff_fixture_cfg=SpiralSearchConfig())  # the gantry config, as before v0.2c
        rows: list[tuple[float, float, float]] = []

        def on_step(info) -> None:
            rel = info.gt.socket_pose.inv() @ info.gt.connector_pose
            rows.append((info.obs.t, -rel.p[2] / MM, info.obs.depth / MM))

        r = task.run(ctrl, sample_scenario(cond, int(idx), seed, nominal_pose(cond, task.fixture)), on_step=on_step)
        t = np.array([x[0] for x in rows])
        faces = [e[2] for e in r.events if e[1] == "contact"]
        for e in r.events:
            if e[1] == "retry" and "jam" in e[2]:
                k = max(0, int(np.searchsorted(t, e[0])) - 1)
                out.append({"trial": f"{cond_name}|spiral|{idx}", "jam_t_s": e[0], "true_depth_below_mouth_mm": rows[k][1],
                            "estimated_depth_mm": rows[k][2], "socket_depth_mm": ctrl.depth / MM, "first_contact": faces[0],
                            "seat_margin_mm": ctrl.cfg.seat_margin_mm, "success": r.success})
    return out


def speed(seed: int) -> list[dict]:
    from defex.control.spiral_search import SpiralSearchController
    from defex.tasks.scenarios import sample_scenario

    conds, task, nominal_pose = _setup()
    cond = conds["nominal"]
    out = []
    for i in range(3):
        ctrl = SpiralSearchController()
        ctrl.stiff_fixture_cfg = replace(ctrl.stiff_fixture_cfg, **FINE_WINNER, insert_speed_mm_s=25.0,
                                         descent_speed_mm_s=25.0, free_speed_mm_s=0.0)
        r = task.run(ctrl, sample_scenario(cond, i, seed, nominal_pose(cond, task.fixture)))
        out.append({"trial": f"nominal|spiral|{i}", "success": r.success, "failure_reason": r.failure_reason,
                    "peak_measured_force_n": r.peak_measured_force_n, "abort_threshold_n": ctrl.cfg.max_force_n,
                    "events": [list(e) for e in r.events if e[1] in ("contact", "abort", "retry")]})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["jams", "speed"])
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.seed not in DEV_SEEDS:
        raise SystemExit("development seeds only")
    from experiments.runner import git_dirty, git_revision

    rows = jams(args.seed) if args.mode == "jams" else speed(args.seed)
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"mode": args.mode, "seed": args.seed, "backend": "arm", "git_commit": git_revision(),
                                "git_dirty": git_dirty(), "rows": rows}, indent=2, default=float))
    for r in rows:
        print({k: v for k, v in r.items() if k != "events"})


if __name__ == "__main__":
    main()
