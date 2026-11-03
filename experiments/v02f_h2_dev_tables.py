"""v0.2f h2 diagnosis (post hoc): do the two heldout2 failure modes of C reproduce on the development seeds?

    PYTHONPATH=. python -m experiments.v02f_h2_dev_tables results/v0.2f_h2_diagnosis/dev_2026_gantry ... \
        [--heldout2 results/heldout2_v0.2f/gantry_heldout2 ...]

For each run folder (trials.csv, config.json, events.json.gz when present):

* F/T drift: seated per controller; C's bad units (declared seated, not seated), split by the sign of the axial
  drift in the controllers' frame (experiments.v02f_h2_drift_axes); C's VERIFY failures by the wall-yaw check.
* Micro-Fit unseen grasp: seated per controller, split by whether the slip and the in-hand rotation move the tip
  the same way; C's failures that show the jam loop (three or more consecutive "jam: re-aim" retries from the same
  probe, within 0.15 mm) and the CoP reclassification ("contact signature inconsistent with the top face").
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
from pathlib import Path

import numpy as np

from experiments.v02f_h2_drift_axes import drift_rates

ORDER = ("adaptive", "spiral", "spiral_rcc", "spiral_rcc_pull", "spiral_rcc_verify", "adaptive_learned")
SHORT = {"adaptive": "C", "spiral": "D", "spiral_rcc": "F", "spiral_rcc_pull": "I", "spiral_rcc_verify": "J",
         "adaptive_learned": "G"}
PROBE = re.compile(r"probe=\(([-+0-9.]+),([-+0-9.]+)\)")


def load(run: Path):
    rows = list(csv.DictReader((run / "trials.csv").open()))
    seed = int(json.loads((run / "config.json").read_text())["base_seed"])
    ev_path = run / "events.json.gz"
    events = json.load(gzip.open(ev_path)) if ev_path.exists() else None
    return rows, seed, events


def jam_loop(events: list) -> bool:
    rec = [e for e in events if e[1] == "recover"]
    probes = [tuple(map(float, PROBE.findall(e[2])[0])) for e in events if e[1] == "attempt"]
    run = best = 0
    for k, e in enumerate(rec):
        same = k + 1 < len(probes) and all(abs(probes[k + 1][j] - probes[k][j]) < 0.15 for j in (0, 1))
        run = run + 1 if e[2].startswith("jam: re-aim") and same else 0
        best = max(best, run)
    return best >= 3


def reclassified(events: list) -> bool:
    return any(e[1] == "detect" and "inconsistent with the top face" in e[2] for e in events)


def wall_yaw_fail(events: list) -> bool:
    return any(e[1] == "wall_yaw" and e[2].endswith("FAIL") for e in events)


def seated(r: dict) -> bool:
    return r["success"] == "True"


def bad(r: dict) -> bool:
    return r["failure_reason"] == "false_accept"


def table_drift(rows, seed, events, cond) -> list[str]:
    sel = [r for r in rows if r["condition"] == cond]
    if not sel:
        return []
    ctrls = [c for c in ORDER if any(r["controller"] == c for r in sel)]
    n = len({r["trial_index"] for r in sel})
    rates = drift_rates(cond, seed, sorted({int(r["trial_index"]) for r in sel}))
    out = [f"  {cond} (n={n}): seated " + ", ".join(
        f"{SHORT[c]} {sum(seated(r) for r in sel if r['controller'] == c)}" for c in ctrls)
        + "; bad units " + ", ".join(f"{SHORT[c]} {sum(bad(r) for r in sel if r['controller'] == c)}" for c in ctrls)]
    c_rows = [r for r in sel if r["controller"] == "adaptive"]
    # Axial component of the drift direction, scaled to 0.3 N/s so both levels share the split.
    fz = {i: 0.3 * v[2] / float(np.linalg.norm(v)) for i, v in rates.items()}
    for name, test in (("fz > +0.1 N/s", lambda v: v > 0.1), ("fz <= +0.1 N/s", lambda v: v <= 0.1)):
        g = [r for r in c_rows if test(fz[int(r["trial_index"])])]
        line = (f"    C, axial drift {name} (scaled to 0.3 N/s): n={len(g)}, seated {sum(seated(r) for r in g)}, "
                f"bad units {sum(bad(r) for r in g)}, other failures {sum(not seated(r) and not bad(r) for r in g)}")
        if events is not None:
            wy = sum(wall_yaw_fail(events.get(f"{cond}|adaptive|{r['trial_index']}", [])) for r in g if not seated(r)
                     and not bad(r))
            line += f" (of which a wall-yaw VERIFY FAIL: {wy})"
        out.append(line)
    depths = sorted(round(float(r["final_depth_mm"]), 2) for r in c_rows if bad(r))
    if depths:
        out.append(f"    C bad-unit final depths (mm): {depths}")
    return out


def table_grasp(rows, events, cond) -> list[str]:
    sel = [r for r in rows if r["condition"] == cond]
    if not sel:
        return []
    ctrls = [c for c in ORDER if any(r["controller"] == c for r in sel)]
    out = [f"  {cond} (n={len({r['trial_index'] for r in sel})})"]
    for name, same in (("same sign", True), ("opposite sign", False)):
        g = [r for r in sel if (float(r["dist_grasp_unseen_lateral_mm"]) * float(r["dist_grasp_unseen_tilt_deg"]) > 0) == same]
        n = len({r["trial_index"] for r in g})
        out.append(f"    {name} (n={n}): seated " + ", ".join(
            f"{SHORT[c]} {sum(seated(r) for r in g if r['controller'] == c)}" for c in ctrls))
    c_fail = [r for r in sel if r["controller"] == "adaptive" and not seated(r)]
    if c_fail:
        above = sum(float(r["final_depth_mm"]) < 0.0 for r in c_fail)
        line = f"    C failures {len(c_fail)}: ending above the mouth {above}"
        if events is not None:
            ev = [events.get(f"{cond}|adaptive|{r['trial_index']}", []) for r in c_fail]
            line += (f"; jam loop {sum(jam_loop(e) for e in ev)}; CoP reclassification {sum(reclassified(e) for e in ev)}; "
                     f"both {sum(jam_loop(e) and reclassified(e) for e in ev)}")
        reasons: dict[str, int] = {}
        for r in c_fail:
            reasons[r["failure_reason"]] = reasons.get(r["failure_reason"], 0) + 1
        out.append(line + f"; reasons {reasons}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    args = ap.parse_args()
    for run in map(Path, args.runs):
        rows, seed, events = load(run)
        print(f"{run} (seed {seed}{', no events file' if events is None else ''})")
        for cond in ("h2_ft_drift_0.1", "h2_ft_drift_0.3"):
            for line in table_drift(rows, seed, events, cond):
                print(line)
        for cond in ("h2_mf_grasp_unseen_1deg", "h2_mf_grasp_unseen_2deg"):
            for line in table_grasp(rows, events, cond):
                print(line)


if __name__ == "__main__":
    main()
