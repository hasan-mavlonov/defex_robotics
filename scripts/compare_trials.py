"""Field-by-field comparison of two trials.csv files (behaviour-equivalence check).

    python scripts/compare_trials.py results/a/trials.csv results/b/trials.csv [--ignore wall_time_s]
    python scripts/compare_trials.py run/trials.csv run/trials.csv --pair adaptive,adaptive_learned

Rows are matched on (controller, condition, trial_index, seed); every other column
except the ignored ones must be byte-identical. Exit status 1 on any difference.
``--pair A,B`` compares controller A's rows in the first file with controller B's rows
in the second (the controller column itself is then ignored).
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

KEY = ("controller", "condition", "trial_index", "seed")


def load(path: Path, controller: str | None = None) -> tuple[list[str], dict[tuple, dict]]:
    with path.open() as fh:
        reader = csv.DictReader(fh)
        rows = [r for r in reader if controller is None or r["controller"] == controller]
        key = KEY if controller is None else KEY[1:]
        return list(reader.fieldnames or []), {tuple(r[k] for k in key): r for r in rows}


def compare(a: Path, b: Path, ignore: set[str], pair: tuple[str, str] | None = None) -> list[str]:
    cols_a, rows_a = load(a, pair[0] if pair else None)
    cols_b, rows_b = load(b, pair[1] if pair else None)
    if pair:
        ignore = ignore | {"controller"}
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
    ap.add_argument("--pair", default="", help="A,B: controller A in the first file against B in the second")
    args = ap.parse_args()
    pair = tuple(args.pair.split(",")) if args.pair else None
    problems = compare(args.a, args.b, set(args.ignore.split(",")), pair)
    for p in problems[:50]:
        print("  ", p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
