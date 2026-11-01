"""Diagnosis numbers for the W5b report from per-tick traces of a few arm trials (offline, ground truth).

Runs against whichever ``defex`` is on the path, so the untouched code can be measured from an
export of the baseline commit:

    git archive fe80689 | tar -x -C /tmp/base
    PYTHONPATH=/tmp/base python experiments/w5b_trace_summary.py --out results/w5b_development/diagnosis/before.json
    python -m experiments.w5b_trace_summary --out results/w5b_development/diagnosis/after.json

Per trial: outcome; in VERIFY's yaw sweep the setpoint lead over the measured yaw when the wall
was first felt and the peak torque after it; in the wall probes the setpoint travel against the
plug's true travel at each wall; in the seat conform the number of torque sign changes and the
peak-to-peak commanded and true tilt (a settling conform has few flips and a small range).
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np

TRIALS = (("nominal", 0), ("nominal", 12), ("lateral_3mm", 7), ("noise_1mm", 5), ("noise_2mm", 5))
DEG = np.pi / 180


def trace(condition: str, index: int, seed: int = 2026):
    os.environ["DEFEX_BACKEND"] = "arm"
    from defex.control.registry import make_controller
    from defex.tasks.conditions import standard_conditions
    from defex.tasks.insertion import InsertionTask
    from defex.tasks.scenarios import sample_scenario
    from defex.utils.transforms import matrix_to_rotvec, twist_about_axis
    from experiments.runner import make_backend, nominal_socket_pose

    cond = {c.name: c for c in standard_conditions()}[condition]
    task = InsertionTask(backend=make_backend())
    sc = sample_scenario(cond, index, seed, nominal_socket_pose(cond, task.fixture))
    ctrl = make_controller("adaptive")
    rows: dict[str, list] = {k: [] for k in ("t", "phase", "T", "lead_yaw", "conf", "true_tilt", "lat_sp", "lat_true")}

    def on_step(info) -> None:
        c, o = info.controller, info.obs
        rel = info.gt.socket_pose.inv() @ info.gt.connector_pose
        rows["t"].append(o.t)
        rows["phase"].append(f"{c.state}:{getattr(c, 'phase', '')}")
        rows["T"].append(o.torque - getattr(c, "bias_t", np.zeros(3)))
        rows["lead_yaw"].append(float(matrix_to_rotvec(info.setpoint.R @ o.fixture_tcp.R.T)[2]))
        rows["conf"].append(np.array(c.adm_conf.x[:2], dtype=float))
        rows["true_tilt"].append(matrix_to_rotvec(rel.R)[:2])
        rows["lat_sp"].append(float(c.adm_lat.x[1]))
        rows["lat_true"].append(float(rel.p[1]))

    r = task.run(ctrl, sc, on_step=on_step)
    a = {k: np.asarray(v) for k, v in rows.items()}
    out = {"condition": condition, "index": index, "success": r.success, "failure_reason": r.failure_reason,
           "cycle_time_s": r.cycle_time_s, "peak_measured_torque_nm": r.peak_measured_torque_nm}
    ph = a["phase"]
    yaw = np.isin(ph, ["VERIFY:yaw_out", "VERIFY:yaw_back"])
    if yaw.any():
        i_wall = np.nonzero(yaw & (np.abs(a["T"][:, 2]) >= 0.02))[0]
        if i_wall.size:
            k = i_wall[0]
            out["yaw_sweep_lead_at_wall_deg"] = float(a["lead_yaw"][k] / DEG)
            out["yaw_sweep_peak_torque_nm"] = float(np.abs(a["T"][k:k + 20]).max())
    inside = (ph == "VERIFY:probe_out").astype(int)
    starts = np.nonzero(np.diff(inside) == 1)[0] + 1
    ends = np.nonzero(np.diff(inside) == -1)[0]  # last tick of each probe: the wall threshold was met
    # Setpoint travel of each probe, and how far the plug really moved (true pose), at the wall.
    out["wall_probe_setpoint_travel_mm"] = [round(float(abs(a["lat_sp"][e] - a["lat_sp"][s]) * 1e3), 3)
                                            for s, e in zip(starts, ends)]
    out["wall_probe_true_travel_mm"] = [round(float(abs(a["lat_true"][e] - a["lat_true"][s]) * 1e3), 3)
                                        for s, e in zip(starts, ends)]
    sc_mask = ph == "VERIFY:seat_conform"
    if sc_mask.any():
        T = a["T"][sc_mask, :2]
        flips = int(sum(((np.sign(T[1:, j]) * np.sign(T[:-1, j])) < 0).sum() for j in (0, 1)))
        out["seat_conform_s"] = float(a["t"][sc_mask][-1] - a["t"][sc_mask][0])
        out["seat_conform_torque_sign_changes"] = flips
        out["seat_conform_commanded_p2p_deg"] = (np.ptp(a["conf"][sc_mask], axis=0) / DEG).round(3).tolist()
        out["seat_conform_true_tilt_p2p_deg"] = (np.ptp(a["true_tilt"][sc_mask], axis=0) / DEG).round(3).tolist()
    out["events"] = [(round(e[0], 3), e[1], e[2]) for e in r.events if e[1] not in ("state",)]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", required=True, help="which code was measured, e.g. 'fe80689 (export)'")
    args = ap.parse_args()
    res = {"code": args.label, "backend": "arm", "seed": 2026, "trials": [trace(c, i) for c, i in TRIALS]}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(res, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    for t in res["trials"]:
        print({k: v for k, v in t.items() if k != "events"})


if __name__ == "__main__":
    main()
