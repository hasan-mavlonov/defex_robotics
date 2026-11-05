"""v0.2f h2 diagnosis (post hoc): the F/T drift each h2_ft_drift trial carries, in the controllers' socket frame,
joined with the outcomes in a trials.csv.

    PYTHONPATH=. python -m experiments.v02f_h2_drift_axes results/heldout2_v0.2f/arm_heldout2 [--condition h2_ft_drift_0.3]

No simulation: the drift direction is a property of the trial's seed (defex/perception/sensors.py, its own
stream). In these trials the plug is held without an in-hand tilt and the F/T frame is parallel to the TCP, so at
the insertion pose the sensor axes are the estimated socket axes and the drift adds -d(t) to the controller's
force (the estimator's sign: external force = -sensor reading). ``fz`` > 0 reads as the socket pushing the plug
out; a controller that tared at t0 carries fz x (t - t0) of axial error at time t.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

CONTROLLERS = ("adaptive", "spiral", "spiral_rcc", "spiral_rcc_pull", "spiral_rcc_verify")
SHORT = {"adaptive": "C", "spiral": "D", "spiral_rcc": "F", "spiral_rcc_pull": "I", "spiral_rcc_verify": "J"}


def drift_rates(condition_name: str, base_seed: int, indices, stream: str = "v0.2f") -> dict[int, np.ndarray]:
    """Per trial: the force drift rate (N/s) as it enters the controllers' force, socket frame.

    stream="v0.2f" rebuilds the drift the heldout2_v0.2f run used, which shared the scenario
    disturbance stream (fixed on v0.2g/drift-stream); stream="current" uses SensorSuite as it is now.
    """
    from defex.perception.sensors import SensorSuite
    from defex.tasks.conditions import heldout2_conditions_by_name
    from defex.tasks.scenarios import sample_scenario
    from defex.utils.transforms import Pose

    cond = heldout2_conditions_by_name()[condition_name]
    out = {}
    for i in indices:
        sc = sample_scenario(cond, i, base_seed, Pose(np.zeros(3), np.eye(3)))
        assert np.allclose(sc.grasp_offset.R, np.eye(3)), "drift trials have no in-hand rotation"
        if stream == "v0.2f":
            u_f = np.random.default_rng(np.random.SeedSequence(sc.seed).spawn(5)[4]).standard_normal(3)
            out[i] = -sc.noise.ft_drift_force_n_per_s * u_f / np.linalg.norm(u_f)
        elif stream == "current":
            out[i] = -SensorSuite(sc.noise, sc.seed).ft_force_drift
        else:
            raise ValueError(stream)
    return out


def classify(r: dict) -> str:
    if r["success"] == "True":
        return "ok"
    reason = r["failure_reason"]
    if reason == "false_accept":
        return "BAD"
    if reason.startswith("aborted:time_limit"):
        return "time"
    if reason == "protective_stop":
        return "stop"
    return reason[:10]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--condition", default="h2_ft_drift_0.3")
    args = ap.parse_args()
    run = Path(args.run_dir)
    seed = int(json.loads((run / "config.json").read_text())["base_seed"])
    rows = [r for r in csv.DictReader((run / "trials.csv").open()) if r["condition"] == args.condition]
    by: dict[int, dict[str, dict]] = {}
    for r in rows:
        by.setdefault(int(r["trial_index"]), {})[r["controller"]] = r
    rates = drift_rates(args.condition, seed, sorted(by))
    ctrls = [c for c in CONTROLLERS if any(c in d for d in by.values())]
    print(f"{run} {args.condition} seed {seed}")
    print("idx   fz N/s  fxy N/s   " + " ".join(f"{SHORT[c]:>5s}" for c in ctrls) + "   C cycle s  C final depth mm")
    for i in sorted(by):
        fz = rates[i][2]
        fxy = float(np.hypot(*rates[i][:2]))
        cells = " ".join(f"{classify(by[i][c]) if c in by[i] else '-':>5s}" for c in ctrls)
        c = by[i].get("adaptive")
        tail = f"{float(c['cycle_time_s']):9.2f}  {float(c['final_depth_mm']):8.2f}" if c else ""
        print(f"{i:3d}  {fz:+6.3f}  {fxy:6.3f}    {cells}   {tail}")
    # Counts by the sign of the axial drift (post hoc grouping).
    for c in ctrls:
        for lo, hi, name in ((0.1, 1.0, "fz > +0.1"), (-0.1, 0.1, "|fz| <= 0.1"), (-1.0, -0.1, "fz < -0.1")):
            sel = [i for i in by if lo < rates[i][2] <= hi and c in by[i]]
            kinds = [classify(by[i][c]) for i in sel]
            summary = ", ".join(f"{k} {kinds.count(k)}" for k in sorted(set(kinds)))
            print(f"  {SHORT[c]} {name:12s} n={len(sel):2d}: {summary}")


if __name__ == "__main__":
    main()
