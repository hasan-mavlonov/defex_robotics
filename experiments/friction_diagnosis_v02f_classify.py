"""POST HOC: classify C's (and G's) arm friction_1 trials of the v0.2f randomized run by what their event logs show.

    python -m experiments.friction_diagnosis_v02f_classify EVENTS_JSON_GZ TRIALS_CSV
    python -m experiments.friction_diagnosis_v02f_classify --benchmarks   # committed arm_standard events, 3 seeds

Reads the run's events.json.gz (not committed with that run; it lives in the run's worktree) and trials.csv.
Classes, in order (the first that matches):
  seated            the trial succeeded
  verify_reject     C reached the floor (seated_candidate) and its VERIFY failed at least once (verify_failed),
                    and the trial ended without a seat
  mouth_stall       never a seated_candidate; every DETECT is a surface_block / no_contact near the mouth
  other             anything else (the last event is printed)
Sub-flags: protective_stop, stuck_during_retract, time_limit, retry_limit (the failure reason).
"""

from __future__ import annotations

import csv
import gzip
import json
import re
import sys
from collections import Counter, defaultdict

import numpy as np

_HALF = re.compile(r"half free travel (-?[0-9.]+) mm")


def classify(events: list, success: bool) -> str:
    kinds = [e[1] for e in events]
    texts = [f"{e[1]} {e[2]}" for e in events]
    if success:
        return "seated"
    seated_cand = any(k == "detect" and "seated_candidate" in t for k, t in zip(kinds, texts))
    verify_failed = any("verify_failed" in t for t in texts)
    if seated_cand and verify_failed:
        return "verify_reject"
    detects = [t for k, t in zip(kinds, texts) if k == "detect"]
    if not seated_cand and detects and all(("surface_block" in t or "no_contact" in t) for t in detects):
        return "mouth_stall"
    return "other"


def benchmarks() -> None:
    """Every C (and J) arm friction_1 failure in benchmark_v0.2d, _rep and v0.2e (nominal, elliptic simulator)."""
    from defex.config import REPO_ROOT

    for b in ("benchmark_v0.2d", "benchmark_v0.2d_rep", "benchmark_v0.2e"):
        d = REPO_ROOT / "results" / b / "arm_standard"
        ev = json.load(gzip.open(d / "events.json.gz", "rt"))
        with open(d / "trials.csv") as fh:
            rows = [r for r in csv.DictReader(fh) if r["condition"] == "friction_1"]
        for ctrl in ("adaptive", "spiral_rcc_verify"):
            n = sum(r["controller"] == ctrl for r in rows)
            fails = [r for r in rows if r["controller"] == ctrl and r["success"] != "True"]
            print(f"{b} {ctrl}: {n - len(fails)}/{n} seated")
            for r in fails:
                e = ev[f"friction_1|{ctrl}|{r['trial_index']}"]
                states = [x[2] for x in e if x[1] == "state" and not str(x[2]).startswith("FAILURE")]
                vf = sum("verify_failed" in s for s in states)
                half = [float(m.group(1)) for x in e if x[1] == "wall_yaw" for m in [_HALF.search(x[2])] if m]
                ps = [x[2] for x in e if x[1] == "protective_stop"]
                print(f"   #{r['trial_index']:>2} {r['failure_reason']:22s} last state {states[-1] if states else '':24s} "
                      f"VERIFY failed x{vf} wall-yaw half travel {half} {ps[0] if ps else ''}")
            h = [float(m.group(1)) for k, e in ev.items() if k.startswith(f"friction_1|{ctrl}|")
                 for x in e if x[1] == "wall_yaw" for m in [_HALF.search(x[2])] if m]
            if h:
                print(f"   every wall-yaw check on friction_1: n={len(h)}, below 0.293 mm: {sum(x < 0.293 for x in h)}")


def main() -> None:
    if sys.argv[1:] == ["--benchmarks"]:
        benchmarks()
        return
    ev = json.load(gzip.open(sys.argv[1], "rt"))
    with open(sys.argv[2]) as fh:
        rows = [r for r in csv.DictReader(fh) if r["condition"] == "friction_1"]
    with open(sys.argv[2]) as fh:
        cones = {r["variant"]: r["sim_cone"] for r in csv.DictReader(fh)}
    table: dict[tuple, Counter] = defaultdict(Counter)
    reasons: dict[tuple, Counter] = defaultdict(Counter)
    for r in rows:
        if r["controller"] not in ("adaptive", "adaptive_learned", "spiral_rcc_verify"):
            continue
        if r["variant"] == "0":
            continue
        key = (r["sim_cone"], r["controller"])
        e = ev[f"{r['variant']}|{r['condition']}|{r['controller']}|{r['trial_index']}"]
        c = classify(e, r["success"] == "True")
        table[key][c] += 1
        if c != "seated":
            reasons[key][f"{c}:{r['failure_reason']}"] += 1
            if c == "other":
                print("other:", r["variant"], r["controller"], r["trial_index"], r["failure_reason"], e[-3:])
    for key in sorted(table):
        print(key, dict(table[key]))
        print("   ", dict(reasons[key]))
    # Every wall-yaw verdict line (first probe pair of each VERIFY and re-probes), all trials, by cone and controller.
    print("\nwall-yaw checks: measured half free travel (mm), need 0.293 mm for 2 deg; y free travel of a centred, unyawed"
          " plug is 0.5 mm")
    for cond in ("friction_1", "friction_0.6", "nominal"):
        half: dict[tuple, list] = defaultdict(list)
        verdicts: dict[tuple, Counter] = defaultdict(Counter)
        for k, e in ev.items():
            v, c, ctrl, _ = k.split("|")
            if c != cond or v == "0" or ctrl not in ("adaptive", "spiral_rcc_verify"):
                continue
            cone = cones[v]
            for ev_ in e:
                if ev_[1] == "wall_yaw":
                    m = _HALF.search(ev_[2])
                    if m:
                        half[(cone, ctrl)].append(float(m.group(1)))
                    verdicts[(cone, ctrl)]["PASS" if ev_[2].endswith("PASS") else "FAIL" if ev_[2].endswith("FAIL")
                                           else "probe again / turn"] += 1
        for key in sorted(half):
            h = np.array(half[key])
            print(f"  {cond:12s} {key[0]:9s} {key[1]:18s} n={h.size:4d} median {np.median(h):.3f} "
                  f"p10 {np.percentile(h, 10):.3f} p90 {np.percentile(h, 90):.3f} below 0.293: {(h < 0.293).mean():.0%} "
                  f"verdict lines {dict(verdicts[key])}")


if __name__ == "__main__":
    main()
