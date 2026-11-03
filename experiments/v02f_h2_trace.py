"""v0.2f h2 diagnosis (post hoc): replay and trace one heldout2 trial, with the F/T error C's wrench carries.

    PYTHONPATH=. python -m experiments.v02f_h2_trace --backend arm --condition h2_ft_drift_0.3 \
        --controller adaptive --index 4 --seed 20261207 [--out trace.npz] [--window 1.0]

Offline, uses ground truth. Seeds: development (2026, 2027), or the reported heldout2 seed 20261207 only for
the trials results/heldout2_v0.2f names as C failures (replay to diagnose, never to select or tune).

Prints the trial result and C's events, then a summary: at every DETECT diagnosis and VERIFY phase change,
the depth C believes (touch-corrected) against the true depth, and the axial force C reads against the true
contact force along the socket axis. The difference is the wrench error (drift since C's last tare, plus
noise and filtering).
"""

from __future__ import annotations

import argparse
import csv
import os
from dataclasses import replace
from pathlib import Path

import numpy as np

from defex.config import DEG, MM

H2_SEED = 20261207
H2_DIR = Path("results/heldout2_v0.2f")
TRACED_CONDITIONS = ("h2_ft_drift_0.3", "h2_ft_drift_0.1", "h2_mf_grasp_unseen_2deg", "h2_mf_grasp_unseen_1deg")


def named_failures(backend: str, condition: str) -> set[int]:
    """Trial indices of C's failures in the reported heldout2 run (the failures the report names)."""
    path = H2_DIR / f"{backend}_heldout2" / "trials.csv"
    with path.open() as f:
        return {int(r["trial_index"]) for r in csv.DictReader(f)
                if r["condition"] == condition and r["controller"] == "adaptive" and r["success"] != "True"}


def check_seed(backend: str, condition: str, index: int, seed: int) -> None:
    if seed in (2026, 2027):
        return
    if seed == H2_SEED and condition in TRACED_CONDITIONS and index in named_failures(backend, condition):
        return
    raise SystemExit("development seeds, or a named heldout2 C failure on seed 20261207, only")


def run(backend: str, condition: str, controller: str, index: int, seed: int, noise_overrides: dict | None = None,
        scenario_hook=None, cfg_overrides: dict | None = None):
    """Replay one trial; return (result, per-tick arrays, controller, scenario)."""
    os.environ["DEFEX_BACKEND"] = backend
    from defex.control.registry import make_controller
    from defex.tasks.conditions import heldout2_conditions_by_name
    from defex.tasks.insertion import InsertionTask
    from defex.tasks.scenarios import sample_scenario
    from experiments.runner import make_backend, nominal_socket_pose

    cond = heldout2_conditions_by_name()[condition]
    task = InsertionTask(backend=make_backend())
    scenario = sample_scenario(cond, index, seed, nominal_socket_pose(cond, task.fixture))
    if noise_overrides:
        scenario = replace(scenario, noise=replace(scenario.noise, **noise_overrides))
    if scenario_hook is not None:
        scenario = scenario_hook(scenario)
    ctrl = make_controller(controller)
    if cfg_overrides:
        ctrl.cfg = replace(ctrl.cfg, **cfg_overrides)
    keys = ("t", "state", "phase", "F", "T", "F_true", "depth_est", "depth_true", "depth_offset", "touch",
            "bias_f", "lat_est", "lat_true", "tilt_true_deg", "adm_lat", "xy", "contact_n")
    rows: dict[str, list] = {k: [] for k in keys}

    def on_step(info) -> None:
        c = info.controller
        o = info.obs
        bf = np.asarray(getattr(c, "bias_f", np.zeros(3)), dtype=float)
        bt = np.asarray(getattr(c, "bias_t", np.zeros(3)), dtype=float)
        rel = info.gt.socket_pose.inv() @ info.gt.connector_pose
        rows["t"].append(o.t)
        rows["state"].append(c.state)
        rows["phase"].append(getattr(c, "phase", ""))
        rows["F"].append(o.force - bf)
        rows["T"].append(o.torque - bt)
        # True net contact force on the held parts, in the estimated socket frame (as the controller's F).
        rows["F_true"].append(o.socket_pose.R.T @ np.asarray(info.gt.contact_force, dtype=float))
        off = float(getattr(c, "depth_offset", 0.0))
        rows["depth_est"].append(o.depth - off)
        rows["depth_true"].append(float(-rel.p[2]))
        rows["depth_offset"].append(off)
        rows["touch"].append(bool(getattr(c, "touch_calibrated", False)))
        rows["bias_f"].append(bf.copy())
        rows["lat_est"].append(o.lateral.copy())
        rows["lat_true"].append(rel.p[:2].copy())
        rows["tilt_true_deg"].append(float(np.degrees(np.arccos(np.clip(rel.R[2, 2], -1.0, 1.0)))))
        rows["adm_lat"].append(np.array(getattr(getattr(c, "adm_lat", None), "x", np.zeros(2)), dtype=float))
        rows["xy"].append(np.array(getattr(c, "xy", np.zeros(2)), dtype=float))
        rows["contact_n"].append(info.gt.contact_force_norm)

    result = task.run(ctrl, scenario, on_step=on_step)
    arrays = {k: np.asarray(v) for k, v in rows.items()}
    return result, arrays, ctrl, scenario


def tare_times(a: dict) -> list[float]:
    """Times at which the controller's own bias estimate changed (its tares)."""
    bf = a["bias_f"]
    out = []
    for k in range(1, len(bf)):
        if np.any(np.abs(bf[k] - bf[k - 1]) > 1e-12):
            out.append(float(a["t"][k]))
    return out


def summary(a: dict, ctrl) -> list[str]:
    lines = []
    t = a["t"]
    tares = tare_times(a)
    lines.append("controller tares at t = " + ", ".join(f"{x:.2f}" for x in tares) + " s")
    err = a["F"][:, 2] - a["F_true"][:, 2]
    # State/phase changes, with the axial error and the depths there.
    prev = None
    for k in range(len(t)):
        key = (a["state"][k], a["phase"][k])
        if key != prev:
            lines.append(
                f"  {t[k]:7.3f} {a['state'][k]:8s} {a['phase'][k]:14s} depth est {a['depth_est'][k] / MM:+6.2f} "
                f"true {a['depth_true'][k] / MM:+6.2f} mm | Fz read {a['F'][k][2]:+5.2f} true {a['F_true'][k][2]:+5.2f} "
                f"err {err[k]:+5.2f} N | Fxy read ({a['F'][k][0]:+5.2f},{a['F'][k][1]:+5.2f}) true "
                f"({a['F_true'][k][0]:+5.2f},{a['F_true'][k][1]:+5.2f}) | lat true ({a['lat_true'][k][0] / MM:+.2f},"
                f"{a['lat_true'][k][1] / MM:+.2f}) est ({a['lat_est'][k][0] / MM:+.2f},{a['lat_est'][k][1] / MM:+.2f})")
            prev = key
    k = len(t) - 1
    lines.append(f"  end: depth est {a['depth_est'][k] / MM:.2f} true {a['depth_true'][k] / MM:.2f} mm, "
                 f"Fz read {a['F'][k][2]:+.2f} true {a['F_true'][k][2]:+.2f} N, tilt true {a['tilt_true_deg'][k]:.2f} deg")
    return lines


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="arm")
    ap.add_argument("--condition", default="h2_ft_drift_0.3")
    ap.add_argument("--controller", default="adaptive")
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--no-drift", action="store_true", help="counterfactual: the same trial with the drift set to 0")
    ap.add_argument("--seen-grasp", action="store_true",
                    help="counterfactual: the in-hand estimate measures the true grasp (no unseen slip or rotation)")
    ap.add_argument("--cfg", action="append", default=[], metavar="NAME=VALUE",
                    help="counterfactual controller setting (diagnosis only, never a tuned value)")
    ap.add_argument("--out", default="")
    ap.add_argument("--window", type=float, default=0.0, help="print every 5th tick this many seconds before the end")
    args = ap.parse_args()
    check_seed(args.backend, args.condition, args.index, args.seed)
    ov = {"ft_drift_force_n_per_s": 0.0, "ft_drift_torque_nm_per_s": 0.0} if args.no_drift else None
    hook = (lambda sc: replace(sc, measured_grasp_offset=None)) if args.seen_grasp else None
    cfg = {k: float(v) for k, v in (item.split("=", 1) for item in args.cfg)}
    result, a, ctrl, scenario = run(args.backend, args.condition, args.controller, args.index, args.seed, ov, hook, cfg)
    print(result.success, result.failure_reason, f"cycle {result.cycle_time_s:.2f} s retries {result.retries} "
          f"final depth {result.final_depth_mm:.2f} mm tilt {result.final_tilt_deg:.2f} deg")
    print("disturbance", {k: round(v, 3) if isinstance(v, float) else v for k, v in scenario.disturbance.items()})
    for e in result.events:
        print(f"  {e[0]:7.3f} {e[1]:18s} {e[2]}")
    for line in summary(a, ctrl):
        print(line)
    if args.window > 0:
        t_end = a["t"][-1]
        for k in np.nonzero(a["t"] > t_end - args.window)[0][::5]:
            print(f"{a['t'][k]:7.3f} {a['state'][k]:8s} {a['phase'][k]:12s} d_est {a['depth_est'][k] / MM:+6.2f} "
                  f"d_true {a['depth_true'][k] / MM:+6.2f} Fz {a['F'][k][2]:+5.2f}/{a['F_true'][k][2]:+5.2f} "
                  f"Fy {a['F'][k][1]:+5.2f}/{a['F_true'][k][1]:+5.2f} adm ({a['adm_lat'][k][0] / MM:+.2f},"
                  f"{a['adm_lat'][k][1] / MM:+.2f}) lat_true ({a['lat_true'][k][0] / MM:+.2f},{a['lat_true'][k][1] / MM:+.2f})"
                  f" tilt {a['tilt_true_deg'][k]:.2f}")
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(args.out, **a)


if __name__ == "__main__":
    main()
