"""How well does the contact (CoP) model hold on each backend? (W5b, development, offline)

The hole localizer assumes that a plug blocked on the top face pivots onto its
supports, so the measured centre of pressure (CoP) is the projection of the plug
centre onto the supported region (``defex.recovery.search_policy``). That was
validated on the gantry, whose wrist is soft (15 N m/rad). This script measures the
model error two ways, using ground truth offline:

* ``static``: the procedure of tests/test_physics.py (fixed orientation, setpoint
  0.6 mm into the face at five offsets), no controller involved.
* ``in_loop``: every top-face diagnosis controller C makes in real trials: the CoP C
  measured against the model's CoP for the true plug offset and yaw.

    python -m experiments.cop_model_error --backend arm --conditions noise_1mm,noise_2mm --trials 10 \
        --name w5b_development/cop_model/arm_before
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import replace
from pathlib import Path

import numpy as np

from defex.config import MM, REPO_ROOT, SensorNoiseConfig

DEV_SEEDS = (2026, 2027)
STATIC_OFFSETS_MM = ((2.0, 0.0), (4.0, 0.0), (0.0, 3.0), (2.5, 2.5), (-2.5, 1.0))


def _model_cop(spec, offset: np.ndarray, yaw: float) -> np.ndarray | None:
    from defex.recovery.yaw_localizer import support_cop_yaw

    op = (spec.cavity_half[0] + spec.chamfer, spec.cavity_half[1] + spec.chamfer)
    blocked, _, cop = support_cop_yaw(np.asarray(offset, float)[None], np.array([yaw]), spec.plug_half[:2], op,
                                      spec.outer_half, 0.02 * MM)
    return cop[0].copy() if blocked[0] else None


def static_check(backend) -> list[dict]:
    """tests/test_physics.py::test_measured_center_of_pressure_matches_forward_model on any backend."""
    from defex.config import ConnectorSpec
    from defex.perception.sensors import SensorSuite
    from defex.perception.state_estimator import StateEstimator
    from defex.recovery.search_policy import predicted_cop
    from defex.sim.backend import SceneParams
    from defex.utils.transforms import Pose

    spec = ConnectorSpec.load("rect_12x8")
    backend.load(SceneParams(spec, spec.friction, Pose.identity()))
    S = backend.nominal_socket_pose
    backend.load(SceneParams(spec, spec.friction, S))
    noise = SensorNoiseConfig()
    out = []
    for k, (ox, oy) in enumerate(STATIC_OFFSETS_MM):
        backend.reset()
        sensors = SensorSuite(noise, 100 + k)
        est = StateEstimator(backend.true_payload, 0.002, noise.ft_filter_cutoff_hz)
        est.reset(S, Pose.identity())
        backend.set_tcp_setpoint(backend.home_tcp_pose)
        for i in range(100):
            if i == 50:
                est.begin_tare()
            backend.step(0.002)
            est.update(sensors.measure(backend.read_sensors()), backend.home_tcp_pose)
        est.end_tare()
        p_above = Pose(S.p + np.array([ox, oy, 1.0]) * MM, S.R)
        backend.set_joint_positions_kinematic(backend.inverse_kinematics(p_above))
        for i in range(400):
            z = 1.0 - min(i / 200, 1.0) * 1.6
            backend.set_tcp_setpoint(Pose(S.p + np.array([ox, oy, z]) * MM, S.R))
            backend.step(0.002)
        obs = []
        for _ in range(60):
            backend.step(0.002)
            obs.append(est.update(sensors.measure(backend.read_sensors()), backend.home_tcp_pose))
        F = np.mean([o.force for o in obs], axis=0)
        T = np.mean([o.torque for o in obs], axis=0)
        cop = np.array([-T[1] / F[2], T[0] / F[2]])
        lat = np.mean([o.lateral for o in obs], axis=0)
        pred = predicted_cop(spec, lat)
        out.append({"offset_mm": [ox, oy], "axial_n": float(F[2]), "cop_mm": (cop / MM).round(3).tolist(),
                    "model_mm": None if pred is None else (pred / MM).round(3).tolist(),
                    "error_mm": None if pred is None else float(np.linalg.norm(cop - pred) / MM)})
    return out


def in_loop(conditions: list[str], trials: int, seed: int, cfg_overrides: dict | None = None) -> list[dict]:
    from defex.control.registry import make_controller
    from defex.perception.sensors import SensorSuite
    from defex.tasks.conditions import latching_conditions, standard_conditions
    from defex.tasks.insertion import InsertionTask
    from defex.tasks.scenarios import sample_scenario
    from defex.utils.transforms import twist_about_axis
    from experiments.runner import make_backend, nominal_socket_pose

    conds = {c.name: c for c in (*standard_conditions(), *latching_conditions())}
    task = InsertionTask(backend=make_backend())
    rows: list[dict] = []
    for name in conditions:
        cond = conds[name]
        for i in range(trials):
            sc = sample_scenario(cond, i, seed, nominal_socket_pose(cond, task.fixture))
            ctrl = make_controller("adaptive")
            if cfg_overrides:
                ctrl.cfg = replace(ctrl.cfg, **cfg_overrides)
            vision = SensorSuite(sc.noise, sc.seed).vision_measurement(sc.socket_pose)
            seen: set[int] = set()

            def on_step(info, ctrl=ctrl, sc=sc, vision=vision, seen=seen, name=name, i=i) -> None:
                d = ctrl.diagnosis
                if d is None or id(d) in seen or ctrl.state != "RECOVER":
                    return
                seen.add(id(d))
                if d.kind != "surface_block" or d.cop is None:
                    return
                gt = info.gt
                rel = gt.socket_pose.inv() @ gt.connector_pose
                yaw = twist_about_axis(rel.R)
                R2 = (gt.socket_pose.R.T @ vision.R)[:2, :2]  # estimated socket axes -> true socket axes
                cop_true_axes = R2 @ d.cop
                model = _model_cop(sc.connector, rel.p[:2], yaw)
                rows.append({
                    "condition": name, "trial": i, "t": info.t, "offset_x_mm": rel.p[0] / MM,
                    "offset_y_mm": rel.p[1] / MM, "yaw_deg": np.degrees(yaw), "axial_n": d.axial_force,
                    "cop_x_mm": cop_true_axes[0] / MM, "cop_y_mm": cop_true_axes[1] / MM,
                    "model_x_mm": np.nan if model is None else model[0] / MM,
                    "model_y_mm": np.nan if model is None else model[1] / MM,
                    "error_mm": np.nan if model is None else float(np.linalg.norm(cop_true_axes - model) / MM),
                    "conform": next((e.detail for e in reversed(ctrl.events) if e.kind == "conform"), ""),
                })

            task.run(ctrl, sc, on_step=on_step)
    return rows


def summarize(rows: list[dict]) -> dict:
    err = np.array([r["error_mm"] for r in rows if np.isfinite(r["error_mm"])])
    if err.size == 0:
        return {"n": 0}
    return {"n": int(err.size), "n_model_not_blocked": int(sum(not np.isfinite(r["error_mm"]) for r in rows)),
            "median_mm": float(np.median(err)), "p90_mm": float(np.percentile(err, 90)),
            "within_0p5mm": float(np.mean(err <= 0.5)), "within_1mm": float(np.mean(err <= 1.0))}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["gantry", "arm"], default="arm")
    ap.add_argument("--conditions", default="noise_1mm,noise_2mm")
    ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--name", required=True)
    ap.add_argument("--overrides", default="", help="JSON dict of AdaptiveConfig overrides")
    args = ap.parse_args()
    if args.seed not in DEV_SEEDS:
        raise SystemExit("development seeds only (2026, 2027)")
    os.environ["DEFEX_BACKEND"] = args.backend
    from experiments.runner import make_backend

    be = make_backend()
    if be is None:
        from defex.sim.mujoco_backend import MuJoCoBackend

        be = MuJoCoBackend()
    out = REPO_ROOT / "results" / args.name
    out.mkdir(parents=True, exist_ok=True)
    static = static_check(be)
    rows = in_loop([c for c in args.conditions.split(",") if c], args.trials, args.seed,
                   json.loads(args.overrides) if args.overrides else None)
    if rows:
        with open(out / "in_loop.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    summary = {"backend": args.backend, "seed": args.seed, "conditions": args.conditions, "trials": args.trials,
               "overrides": args.overrides, "static": static, "in_loop": summarize(rows)}
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({"static_errors_mm": [s["error_mm"] for s in static], "in_loop": summary["in_loop"]}, indent=1))


if __name__ == "__main__":
    main()
