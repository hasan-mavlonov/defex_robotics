"""Failure classes of controller C on the arm, from committed event logs (v0.2c arm-robustness).

    python -m experiments.c_arm_failures results/<run> [results/<run> ...] [--controller adaptive]

Offline diagnosis only: reads trials.csv (ground truth columns) and events.json.gz. Classes, in order
of precedence, for each failed good-part trial:

* protective_stop: the cell stopped (with the controller event just before it);
* repeat: a retry planned as "retry at same probe" (verify failed or ambiguous), which repeats the
  identical attempt;
* wedged: some in-cavity diagnosis (seated_candidate or partial_jam) had its centre of pressure
  outside the plug face by more than the surface margin, i.e. the walls carried the load;
* timeout_in_cavity: an insert timeout with the plug deeper than the engage depth;
* search: the remaining time and retry limits (every attempt blocked on the top face or lead-in).
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

PX, PY, MARGIN = 6.0, 4.0, 0.3  # plug half-sizes and AdaptiveConfig.surface_cop_margin_mm (rect_12x8)
DETECT = re.compile(r"(\w+) \[(\w+)\] depth=([-\d.]+) mm Fax=([-\d.]+) N .*CoP=(n/a|\(([-+\d.]+),([-+\d.]+)\) mm)")
BAD_PARTS = ("mf_half_latched", "mf_broken_latch", "mf_stubbed_terminal", "mf_wrong_polarization")


def classify(events: list) -> tuple[str, dict]:
    ev = [e for e in events if e[1] != "state"]
    info = Counter()
    wedged = timeout_cav = False
    for _, kind, detail in ev:
        if kind == "recover" and detail.startswith("retry at same probe"):
            info["repeat"] += 1
        if kind == "wall_yaw":
            info["wall_yaw_" + detail.split("->")[-1].strip().split(" ")[0]] += 1
        if kind == "detect":
            m = DETECT.match(detail)
            if not m:
                continue
            dk, trig, depth = m.group(1), m.group(2), float(m.group(3))
            info[f"detect_{dk}_{trig}"] += 1
            if dk in ("seated_candidate", "partial_jam") and m.group(6) is not None:
                cx, cy = float(m.group(6)), float(m.group(7))
                if abs(cx) > PX + MARGIN or abs(cy) > PY + MARGIN:
                    wedged = True
                    info["wedged_detects"] += 1
            if trig == "insert_timeout" and depth > 1.5:
                timeout_cav = True
    stop = [e for e in ev if e[1] == "protective_stop"]
    if stop:
        prev = [e for e in ev if e[1] not in ("protective_stop", "attempt") and e[0] <= stop[0][0]]
        last = prev[-1] if prev else ("", "", "")
        label = last[1] + (" PASS" if "PASS" in last[2] else " FAIL" if "FAIL" in last[2] else "")
        return f"protective_stop ({label})", info
    if info["repeat"]:
        return "repeat", info
    if wedged:
        return "wedged", info
    if timeout_cav:
        return "timeout_in_cavity", info
    return "search", info


def analyze(run: Path, controller: str) -> dict:
    rows = list(csv.DictReader(open(run / "trials.csv")))
    with gzip.open(run / "events.json.gz", "rt") as fh:
        events = json.load(fh)
    out: dict = defaultdict(Counter)
    totals = Counter()
    for r in rows:
        if r["controller"] != controller:
            continue
        cond = r["condition"]
        key = f"{cond}|{controller}|{r['trial_index']}"
        cls, info = classify(events[key])
        for k, v in info.items():
            totals[k] += v
        if cond in BAD_PARTS:
            out[cond]["bad part passed" if r["declared_success"] == "True" else "bad part rejected"] += 1
            continue
        if r["success"] == "True":
            out[cond]["success"] += 1
            continue
        out[cond][cls] += 1
    return {"by_condition": {k: dict(v) for k, v in out.items()}, "event_totals": dict(totals)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--controller", default="adaptive")
    args = ap.parse_args()
    print(json.dumps({str(r): analyze(r, args.controller) for r in args.runs}, indent=1))


if __name__ == "__main__":
    main()
