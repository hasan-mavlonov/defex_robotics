"""v0.2c diagnosis: does the half-latched part's end stop oscillate at a constant setpoint? (uses ground truth)

    python -m experiments.v02c_stop_chatter --out results/v0.2c_defect_verdict/stop_chatter

Runs controller C on development trials (seed 2026) and records, per control tick over the last
0.6 s of each trial (the protective stop, or the end of the cycle), the commanded and measured
TCP height, the measured axial force and the true tip depth. A half-latched trial that trips the
stop on its first insertion is compared with a good part at its bottom (mf_nominal) and with the
broken-latch part, which bottoms on the cavity floor (a MuJoCo contact) rather than on the
mating model's end stop.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from defex.config import MM
from experiments.runner import git_dirty, git_revision
from experiments.trace_trial import run_trace

CASES = (("mf_half_latched", 3), ("mf_half_latched", 5), ("mf_nominal", 0), ("mf_broken_latch", 1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/v0.2c_defect_verdict/stop_chatter")
    ap.add_argument("--window", type=float, default=0.6)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    summary = {"seed": 2026, "backend": "gantry", "controller": "adaptive", "git_commit": git_revision(),
               "git_dirty": git_dirty(), "window_s": args.window, "cases": []}
    for cond, idx in CASES:
        res, a, _ = run_trace("gantry", cond, "adaptive", idx, 2026, suite="latching")
        t = a["t"]
        # The trace keeps running through the 0.25 s settle after a stop, with the setpoint frozen.
        sel = np.nonzero(t > t[-1] - args.window)[0]
        rows = []
        for k in sel:
            rows.append({"t_s": f"{t[k]:.4f}", "state": a["state"][k], "phase": a["phase"][k],
                         "setpoint_z_mm": f"{a['sp_p'][k][2] / MM:.4f}", "tcp_z_mm": f"{a['tcp_p'][k][2] / MM:.4f}",
                         "fz_n": f"{a['F'][k][2]:.3f}", "f_norm_n": f"{a['f_norm'][k]:.3f}",
                         "true_depth_mm": f"{-a['true_rel_p'][k][2] / MM:.4f}"})
        with (out / f"{cond}_{idx:03d}.csv").open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        last = sel[t[sel] > t[-1] - 0.2]  # last 0.2 s (inside the settle after a stop)
        summary["cases"].append({
            "condition": cond, "trial_index": idx, "failure_reason": res.failure_reason,
            "protective_stop": res.protective_stop, "peak_measured_force_n": res.peak_measured_force_n,
            "last_0.2s": {
                "setpoint_z_range_mm": float(np.ptp(a["sp_p"][last][:, 2]) / MM),
                "fz_min_n": float(a["F"][last][:, 2].min()), "fz_max_n": float(a["F"][last][:, 2].max()),
                "true_depth_range_mm": float(np.ptp(a["true_rel_p"][last][:, 2]) / MM),
            },
        })
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
