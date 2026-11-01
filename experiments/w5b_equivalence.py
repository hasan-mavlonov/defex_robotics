"""Rule-3 check: gantry trials before and after W5b agree in every trials.csv field except wall_time_s.

    python -m experiments.w5b_equivalence > results/w5b_development/equivalence.txt
"""

from __future__ import annotations

import csv
import sys

from defex.config import REPO_ROOT

ROOT = REPO_ROOT / "results" / "w5b_development"


def compare(name: str) -> int:
    before = list(csv.DictReader(open(ROOT / "equiv_before" / name / "trials.csv")))
    after = list(csv.DictReader(open(ROOT / "equiv_after" / name / "trials.csv")))
    if len(before) != len(after):
        print(f"{name}: {len(before)} rows before, {len(after)} after")
        return 1
    fields = [k for k in before[0] if k != "wall_time_s"]
    diffs = [(b["condition"], b["controller"], b["trial_index"], k, b[k], a[k])
             for b, a in zip(before, after) for k in fields if b[k] != a[k]]
    print(f"{name}: {len(before)} trials x {len(fields)} fields compared, {len(diffs)} differences")
    for d in diffs[:20]:
        print("  ", d)
    return 1 if diffs else 0


if __name__ == "__main__":
    sys.exit(compare("standard") | compare("latching"))
