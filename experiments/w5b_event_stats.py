"""Where controller C fails on the arm, from the event logs of committed runs (W5b report).

    python -m experiments.w5b_event_stats > results/w5b_development/diagnosis/event_stats.json
"""

from __future__ import annotations

import csv
import gzip
import json
import re
from collections import Counter

from defex.config import REPO_ROOT

ROOT = REPO_ROOT / "results" / "w5b_development"
RUNS = ("before/arm_standard_seed2026", "after/arm_standard_seed2026", "before/arm_latching_seed2026",
        "after/arm_latching_seed2026")


def stats(run: str) -> dict:
    rows = {f"{r['condition']}|{r['controller']}|{r['trial_index']}": r
            for r in csv.DictReader(open(ROOT / run / "trials.csv"))}
    with gzip.open(ROOT / run / "events.json.gz", "rt") as fh:
        events = json.load(fh)
    stop_after = Counter()
    probe_gave_up = 0
    wall_yaw = Counter()
    detect_kinds = Counter()
    for key, ev in events.items():
        if "|adaptive|" not in key:
            continue
        ev = [e for e in ev if e[1] != "state"]
        if rows[key]["failure_reason"] == "protective_stop":
            prev = [e for e in ev if e[1] not in ("protective_stop", "attempt")]
            last = prev[-1] if prev else ("", "", "")
            label = last[1] + (" PASS" if "PASS" in last[2] else " FAIL" if "FAIL" in last[2] else "")
            stop_after[label] += 1
        for _, kind, detail in ev:
            if kind == "verify" and "wall reactions" in detail and "FAIL" in detail:
                travels = [float(x) for x in re.findall(r"[-+]?\d+\.\d+", detail.split("travel")[1])]
                reactions = [float(x) for x in re.findall(r"[-+]?\d+\.\d+", detail.split("travel")[0])]
                if any(r < 2.0 for r in reactions) and max(travels) >= 1.3:
                    probe_gave_up += 1
            if kind == "wall_yaw":
                wall_yaw[detail.split("->")[-1].split(",")[0].strip().split(" ")[0]] += 1
            if kind == "detect":
                detect_kinds[detail.split(" ")[0]] += 1
    return {"protective_stops_by_last_event": dict(stop_after),
            "wall_probes_that_gave_up_on_travel": probe_gave_up,
            "wall_yaw_outcomes": dict(wall_yaw), "detect_kinds": dict(detect_kinds)}


def main() -> None:
    print(json.dumps({run: stats(run) for run in RUNS if (ROOT / run / "events.json.gz").exists()}, indent=1))


if __name__ == "__main__":
    main()
