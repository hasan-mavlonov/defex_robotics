"""Per-tick trace of one trial, for diagnosing controller behaviour (offline; uses ground truth).

    python -m experiments.trace_trial --backend arm --condition nominal --controller adaptive --index 0 \
        --seed 2026 --out results/w5b_development/traces/nominal_c0.npz

Saves, every control tick: time, FSM state and phase, the controller's tared wrench
(socket frame), measured |T| and |F| as the protective stop sees them, the commanded
and measured TCP, the admittance offsets of controller C, and the true connector pose
relative to the true socket. ``--window`` prints the ticks around the end of the trial.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np

from defex.config import DEG, MM
from defex.utils.transforms import matrix_to_rotvec, twist_about_axis


def run_trace(backend: str, condition: str, controller: str, index: int, seed: int, suite: str = "standard",
              cfg_overrides: dict | None = None):
    os.environ["DEFEX_BACKEND"] = backend
    from dataclasses import replace

    from defex.control.registry import make_controller
    from defex.tasks.conditions import (
        heldout2_conditions,
        heldout_conditions,
        latching_conditions,
        standard_conditions,
    )
    from defex.tasks.insertion import InsertionTask
    from defex.tasks.scenarios import sample_scenario
    from experiments.runner import make_backend, nominal_socket_pose

    conds = {c.name: c for c in (*standard_conditions(), *latching_conditions(), *heldout_conditions(),
                                  *heldout2_conditions())}
    cond = conds[condition]
    task = InsertionTask(backend=make_backend())
    scenario = sample_scenario(cond, index, seed, nominal_socket_pose(cond, task.fixture))
    ctrl = make_controller(controller)
    if cfg_overrides:
        ctrl.cfg = replace(ctrl.cfg, **cfg_overrides)
    rows: dict[str, list] = {k: [] for k in (
        "t", "state", "phase", "F", "T", "f_norm", "t_norm", "sp_p", "sp_rv", "tcp_p", "tcp_rv", "adm_lat",
        "adm_rot", "adm_conf", "yaw_adj", "depth", "true_rel_p", "true_yaw", "true_tilt_rv", "contact_n")}

    def on_step(info) -> None:
        c = info.controller
        o = info.obs
        bf = getattr(c, "bias_f", np.zeros(3))
        bt = getattr(c, "bias_t", np.zeros(3))
        rows["t"].append(o.t)
        rows["state"].append(c.state)
        rows["phase"].append(getattr(c, "phase", ""))
        rows["F"].append(o.force - bf)
        rows["T"].append(o.torque - bt)
        rows["f_norm"].append(o.force_norm)
        rows["t_norm"].append(o.torque_norm)
        rows["sp_p"].append(info.setpoint.p.copy())
        rows["sp_rv"].append(matrix_to_rotvec(info.setpoint.R))
        rows["tcp_p"].append(o.fixture_tcp.p.copy())
        rows["tcp_rv"].append(matrix_to_rotvec(o.fixture_tcp.R))
        rows["adm_lat"].append(np.array(getattr(getattr(c, "adm_lat", None), "x", np.zeros(2)), dtype=float))
        rows["adm_rot"].append(np.array(getattr(getattr(c, "adm_rot", None), "x", np.zeros(3)), dtype=float))
        rows["adm_conf"].append(np.array(getattr(getattr(c, "adm_conf", None), "x", np.zeros(3)), dtype=float))
        rows["yaw_adj"].append(float(getattr(c, "yaw_adj", 0.0)))
        rows["depth"].append(o.depth)
        rel = info.gt.socket_pose.inv() @ info.gt.connector_pose
        rows["true_rel_p"].append(rel.p.copy())
        rows["true_yaw"].append(twist_about_axis(rel.R))
        rows["true_tilt_rv"].append(matrix_to_rotvec(rel.R))
        rows["contact_n"].append(info.gt.contact_force_norm)

    result = task.run(ctrl, scenario, on_step=on_step)
    arrays = {k: np.asarray(v) for k, v in rows.items()}
    return result, arrays, ctrl


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="arm")
    ap.add_argument("--condition", default="nominal")
    ap.add_argument("--controller", default="adaptive")
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--out", default="")
    ap.add_argument("--window", type=float, default=0.0, help="print ticks this many seconds before the end")
    args = ap.parse_args()
    if args.seed not in (2026, 2027) and not (3001 <= args.seed <= 3040 or args.seed == 4001):
        raise SystemExit("development seeds only")
    result, a, ctrl = run_trace(args.backend, args.condition, args.controller, args.index, args.seed)
    print(result.success, result.failure_reason, f"cycle {result.cycle_time_s:.2f} s retries {result.retries}")
    for e in result.events:
        print(f"  {e[0]:7.3f} {e[1]:18s} {e[2]}")
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(args.out, **a)
    if args.window > 0:
        t_end = a["t"][-1]
        for k in np.nonzero(a["t"] > t_end - args.window)[0][::5]:
            print(f"{a['t'][k]:7.3f} {a['state'][k]:7s} {a['phase'][k]:12s} F=({a['F'][k][0]:+5.2f},{a['F'][k][1]:+5.2f},"
                  f"{a['F'][k][2]:+5.2f}) T=({a['T'][k][0]:+.3f},{a['T'][k][1]:+.3f},{a['T'][k][2]:+.3f}) "
                  f"|T|={a['t_norm'][k]:.3f} yaw_adj={a['yaw_adj'][k] / DEG:+.2f} "
                  f"true_yaw={a['true_yaw'][k] / DEG:+.2f} sp_rvz={a['sp_rv'][k][2] / DEG:+.2f} "
                  f"tcp_rvz={a['tcp_rv'][k][2] / DEG:+.2f} lat={a['adm_lat'][k] / MM} rot={a['adm_rot'][k] / DEG}")


if __name__ == "__main__":
    main()
