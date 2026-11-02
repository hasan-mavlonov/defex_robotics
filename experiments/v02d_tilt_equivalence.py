"""v0.2d tilt check: field-by-field equivalence of two robustness runs, explained by the check's verdicts.

    python -m experiments.v02d_tilt_equivalence BEFORE_DIR AFTER_DIR [--pair adaptive,adaptive@tilt_k1 ...]

Rows are matched on (condition, trial_index, seed) for each controller pair (default: the same name in
both runs). Every trials.csv field except wall_time_s is compared. A differing trial is explained when the
after run's event log has a failed tilt check ("tilt ... FAIL") in it; anything else is reported as
unexplained. Exit status 1 if any difference is unexplained.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from pathlib import Path

IGNORE = {"wall_time_s", "controller"}


def load(d: Path) -> tuple[list[dict], dict]:
    with (d / "trials.csv").open() as fh:
        rows = list(csv.DictReader(fh))
    with gzip.open(d / "events.json.gz", "rt") as fh:
        events = json.load(fh)
    return rows, events


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("before", type=Path)
    ap.add_argument("after", type=Path)
    ap.add_argument("--pair", action="append", default=[], help="BEFORE_CTRL,AFTER_CTRL (repeatable)")
    args = ap.parse_args()
    rows_b, _ = load(args.before)
    rows_a, ev_a = load(args.after)
    pairs = [tuple(p.split(",")) for p in args.pair] or sorted({(r["controller"], r["controller"]) for r in rows_b})
    unexplained = 0
    for cb, ca in pairs:
        b = {(r["condition"], r["trial_index"], r["seed"]): r for r in rows_b if r["controller"] == cb}
        a = {(r["condition"], r["trial_index"], r["seed"]): r for r in rows_a if r["controller"] == ca}
        if b.keys() != a.keys():
            print(f"{cb} vs {ca}: trial sets differ ({len(b.keys() ^ a.keys())} keys)")
            unexplained += 1
            continue
        cols = [c for c in next(iter(b.values())).keys() if c not in IGNORE]
        diff, fails, explained = [], 0, 0
        for k in sorted(b):
            ev = ev_a.get(f"{k[0]}|{ca}|{int(k[1])}", [])
            failed = any(kind == "tilt" and detail.endswith("FAIL") for _, kind, detail in ev)
            fails += failed
            cols_diff = [c for c in cols if b[k][c] != a[k][c]]
            if cols_diff:
                if failed:
                    explained += 1
                else:
                    diff.append((k, cols_diff))
        n_fields = len(b) * len(cols)
        print(f"{cb} vs {ca}: {len(b)} trials, {n_fields} fields compared; {fails} trials with a failed tilt check; "
              f"{explained} differing trials explained by it; {len(diff)} unexplained")
        for k, c in diff:
            print(f"  unexplained {k}: {c}")
        unexplained += len(diff)
    sys.exit(1 if unexplained else 0)


if __name__ == "__main__":
    main()
