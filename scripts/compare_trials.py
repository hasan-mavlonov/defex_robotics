"""Field-by-field comparison of two trials.csv files (behaviour-equivalence check).

    python scripts/compare_trials.py results/a/trials.csv results/b/trials.csv [--ignore wall_time_s]

Rows are matched on (controller, condition, trial_index, seed); every other column
except the ignored ones must be byte-identical. Exit status 1 on any difference.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

KEY = ("controller", "condition", "trial_index", "seed")


def load(path: Path) -> tuple[list[str], dict[tuple, dict]]:
    with path.open() as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        return list(reader.fieldnames or []), {tuple(r[k] for k in KEY): r for r in rows}


def compare(a: Path, b: Path, ignore: set[str]) -> list[str]:
    cols_a, rows_a = load(a)
    cols_b, rows_b = load(b)
    problems = []
    if cols_a != cols_b:
        problems.append(f"columns differ: {sorted(set(cols_a) ^ set(cols_b))}")
    if rows_a.keys() != rows_b.keys():
        problems.append(f"trials differ: {len(rows_a.keys() ^ rows_b.keys())} keys")
    n_fields = 0
    for k in sorted(rows_a.keys() & rows_b.keys()):
        for col in cols_a:
            if col in ignore or col not in rows_b[k]:
                continue
            n_fields += 1
            if rows_a[k][col] != rows_b[k][col]:
                problems.append(f"{k} {col}: {rows_a[k][col]!r} != {rows_b[k][col]!r}")
    print(f"{a} vs {b}: {len(rows_a)} trials, {n_fields} fields compared, {len(problems)} differences")
    return problems


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("a", type=Path)
    ap.add_argument("b", type=Path)
    ap.add_argument("--ignore", default="wall_time_s")
    args = ap.parse_args()
    problems = compare(args.a, args.b, set(args.ignore.split(",")))
    for p in problems[:50]:
        print("  ", p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
