"""Compare trial rows of two runs, or two controllers inside one run.

    python results/v0.2e_arm_reset/compare.py runs A/trials.csv B/trials.csv
    python results/v0.2e_arm_reset/compare.py by-controller A/trials.csv B/trials.csv
    python results/v0.2e_arm_reset/compare.py pair A/trials.csv spiral_rcc spiral_rcc_pull

Rows are matched on (controller, condition, trial_index) for ``runs`` and on (condition,
trial_index) for ``pair``. ``wall_time_s`` (wall clock) is never compared; in ``pair`` the
``controller`` column is not compared either. Prints one summary line.
"""

from __future__ import annotations

import csv
import sys

TIMING = {"wall_time_s"}
OUTCOME = ("success", "failure_reason", "gt_seated", "declared_success", "retries", "recovered",
           "protective_stop", "timeout")


def read(path: str) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def diff(a: dict[tuple, dict], b: dict[tuple, dict], skip: set[str]) -> str:
    if a.keys() != b.keys():
        return f"KEY MISMATCH: {len(a.keys() - b.keys())} only in first, {len(b.keys() - a.keys())} only in second"
    any_diff = outcome_diff = 0
    max_cycle = 0.0
    cols: set[str] = set()
    for k in sorted(a):
        ra, rb = a[k], b[k]
        changed = [c for c in ra if c not in skip and ra[c] != rb.get(c)]
        if changed:
            any_diff += 1
            cols.update(changed)
        if any(ra[c] != rb[c] for c in OUTCOME):
            outcome_diff += 1
        if ra["cycle_time_s"] and rb["cycle_time_s"]:
            max_cycle = max(max_cycle, abs(float(ra["cycle_time_s"]) - float(rb["cycle_time_s"])))
    return (f"rows {len(a)}; rows differing (any column except {sorted(skip)}): {any_diff}; "
            f"rows with a different outcome: {outcome_diff}; max |cycle_time_s diff|: {max_cycle * 1e3:.3f} ms"
            + (f"; columns that differ: {','.join(sorted(cols))}" if cols else ""))


def main() -> None:
    mode = sys.argv[1]
    if mode == "runs":
        a = {(r["controller"], r["condition"], r["trial_index"]): r for r in read(sys.argv[2])}
        b = {(r["controller"], r["condition"], r["trial_index"]): r for r in read(sys.argv[3])}
        print(diff(a, b, TIMING))
    elif mode == "by-controller":
        a = {(r["controller"], r["condition"], r["trial_index"]): r for r in read(sys.argv[2])}
        b = {(r["controller"], r["condition"], r["trial_index"]): r for r in read(sys.argv[3])}
        for ctrl in dict.fromkeys(k[0] for k in a):
            print(f"  {ctrl:18s} " + diff({k: v for k, v in a.items() if k[0] == ctrl},
                                          {k: v for k, v in b.items() if k[0] == ctrl}, TIMING))
    elif mode == "pair":
        rows = read(sys.argv[2])
        a = {(r["condition"], r["trial_index"]): r for r in rows if r["controller"] == sys.argv[3]}
        b = {(r["condition"], r["trial_index"]): r for r in rows if r["controller"] == sys.argv[4]}
        print(diff(a, b, TIMING | {"controller"}))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
