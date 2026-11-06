"""Markdown tables for results/w5b_development/REPORT.md, from the committed trials.csv / summary.json.

    python -m experiments.w5b_tables > results/w5b_development/tables.md
"""

from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

from defex.config import REPO_ROOT

ROOT = REPO_ROOT / "results" / "w5b_development"
ORDER = ("fixed", "correction", "correction_rcc", "spiral", "spiral_rcc", "adaptive")
LETTER = {"fixed": "A", "correction": "B", "adaptive": "C", "spiral": "D", "correction_rcc": "E", "spiral_rcc": "F"}


def _load(run: Path):
    rows = list(csv.DictReader(open(run / "trials.csv")))
    summary = json.load(open(run / "summary.json"))
    return rows, {o["controller"]: o for o in summary["overall"]}


def overall_table(before: Path, after: Path) -> str:
    rb, ob = _load(before)
    ra, oa = _load(after)
    out = ["| Controller | Success before | Success after | Escapes: failed units passed as good (before / after) | "
           "Protective stops (before / after) | Median cycle of successes, s (before / after) |",
           "|---|---|---|---|---|---|"]

    def med(rows, c):
        v = [float(r["cycle_time_s"]) for r in rows if r["controller"] == c and r["success"] == "True"]
        return f"{statistics.median(v):.2f}" if v else "-"

    for c in ORDER:
        if c not in oa:
            continue
        b, a = ob[c], oa[c]
        out.append(f"| {LETTER[c]} {c} | {b['success_rate']:.0%} | {a['success_rate']:.0%} | {b['escapes']} / {a['escapes']} | "
                   f"{b['protective_stops']} / {a['protective_stops']} | {med(rb, c)} / {med(ra, c)} |")
    return "\n".join(out)


def condition_table(before: Path, after: Path, controllers=ORDER) -> str:
    rb, _ = _load(before)
    ra, _ = _load(after)

    def cells(rows):
        d = defaultdict(lambda: [0, 0, 0])  # successes, trials, escapes (defex.logging.metrics.is_escape)
        for r in rows:
            k = (r["condition"], r["controller"])
            ok = r["success"] == "True"
            d[k][0] += ok
            d[k][1] += 1
            d[k][2] += (not ok) and r["protective_stop"] != "True" and r["declared_success"] != "False"
        return d

    cb, ca = cells(rb), cells(ra)
    conds = list(dict.fromkeys(r["condition"] for r in ra))
    ctrls = [c for c in controllers if any(r["controller"] == c for r in ra)]
    out = ["| Condition | " + " | ".join(f"{LETTER[c]}" for c in ctrls) + " |",
           "|---|" + "---|" * len(ctrls)]
    for cond in conds:
        out.append(f"| {cond} | " + " | ".join(
            f"{cb[(cond, c)][0]}/{cb[(cond, c)][2]} -> {ca[(cond, c)][0]}/{ca[(cond, c)][2]}" for c in ctrls) + " |")
    return "\n".join(out)


def failure_table(run: Path, controller: str = "adaptive") -> str:
    rows, _ = _load(run)
    d = defaultdict(lambda: defaultdict(int))
    for r in rows:
        if r["controller"] == controller and r["success"] != "True":
            d[r["condition"]][r["failure_reason"]] += 1
    reasons = sorted({k for v in d.values() for k in v})
    out = ["| Condition | " + " | ".join(reasons) + " |", "|---|" + "---|" * len(reasons)]
    for cond, v in d.items():
        out.append(f"| {cond} | " + " | ".join(str(v.get(k, 0)) for k in reasons) + " |")
    return "\n".join(out)


def main() -> None:
    pairs = [
        ("Arm, standard set, seed 2026 (20 trials per cell)", "before/arm_standard_seed2026", "after/arm_standard_seed2026"),
        ("Arm, latching suite, seed 2026 (20 trials per cell)", "before/arm_latching_seed2026", "after/arm_latching_seed2026"),
        ("Arm, standard set, seed 2027 (10 trials per cell)", "before/arm_standard_seed2027", "after/arm_standard_seed2027"),
        ("Arm, latching suite, seed 2027 (10 trials per cell)", "before/arm_latching_seed2027", "after/arm_latching_seed2027"),
    ]
    for title, b, a in pairs:
        if not (ROOT / a / "trials.csv").exists() or not (ROOT / b / "trials.csv").exists():
            continue
        print(f"## {title}\n")
        print(overall_table(ROOT / b, ROOT / a) + "\n")
        print("Per condition, successes/escapes, before -> after:\n")
        print(condition_table(ROOT / b, ROOT / a) + "\n")
        print("C's failures after the change:\n")
        print(failure_table(ROOT / a) + "\n")


if __name__ == "__main__":
    main()
