"""v0.2c integration: per-controller comparison of two runs on their common trials.

    python -m experiments.v02c_integration_compare A_DIR B_DIR [A_DIR B_DIR ...] [--controllers c1,c2]

For each pair of run folders and each controller present in both, on the trials both contain
(matched on condition, trial index and seed, so a 20-trial run is compared with the first 20
trials of a 30-trial run): how many trials differ in any field (wall_time_s ignored), and, on
each side, successes on good-part conditions, bad units passed, protective stops, and the median
cycle time of successes, with the paired exact McNemar p on good-part success.
"""

from __future__ import annotations

import argparse
import csv
import statistics
from math import comb
from pathlib import Path

DEFECTS = ("mf_half_latched", "mf_broken_latch", "mf_stubbed_terminal", "mf_wrong_polarization")
IGNORE = {"wall_time_s"}


def load(path: Path) -> dict[str, dict[tuple, dict]]:
    out: dict[str, dict[tuple, dict]] = {}
    with (path / "trials.csv").open() as fh:
        for r in csv.DictReader(fh):
            out.setdefault(r["controller"], {})[(r["condition"], r["trial_index"], r["seed"])] = r
    return out


def truthy(v: str) -> bool:
    return v in ("True", "true", "1")


def escaped(r: dict) -> bool:
    """A failed unit passed as good (experiments/checkpoint_report.py's definition)."""
    return not truthy(r["success"]) and not truthy(r["protective_stop"]) and r["declared_success"] != "False"


def false_reject(r: dict) -> bool:
    return r["gt_seated"] == "True" and r["declared_success"] == "False"


def mcnemar(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2.0 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def stats(rows: list[dict]) -> dict:
    good = [r for r in rows if r["condition"] not in DEFECTS]
    bad = [r for r in rows if r["condition"] in DEFECTS]
    cyc = [float(r["cycle_time_s"]) for r in good if truthy(r["success"])]
    return {
        "good": len(good), "succ": sum(truthy(r["success"]) for r in good),
        "bad": len(bad), "bad_passed": sum(escaped(r) for r in bad),
        "false_rejects": sum(false_reject(r) for r in good),
        "escapes_good": sum(escaped(r) for r in good),
        "stops": sum(truthy(r["protective_stop"]) for r in rows),
        "median_s": statistics.median(cyc) if cyc else float("nan"),
        "bad_s": statistics.mean(float(r["cycle_time_s"]) for r in bad) if bad else float("nan"),
    }


def compare(a_dir: Path, b_dir: Path, only: set[str] | None) -> list[str]:
    a, b = load(a_dir), load(b_dir)
    lines = [f"### {a_dir} -> {b_dir}", "",
             "| Controller | Trials | Differ | Good seated A / B (A-only / B-only, p) | Bad passed A / B | "
             "Good-part escapes A / B | False rejects A / B | Stops A / B | Median cycle A / B (s) | Mean time per bad part A / B (s) |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for ctrl in [c for c in a if c in b and (only is None or c in only)]:
        keys = sorted(a[ctrl].keys() & b[ctrl].keys())
        ra, rb = [a[ctrl][k] for k in keys], [b[ctrl][k] for k in keys]
        differ = sum(any(x[f] != y[f] for f in x if f not in IGNORE) for x, y in zip(ra, rb))
        sa, sb = stats(ra), stats(rb)
        a_only = sum(truthy(x["success"]) and not truthy(y["success"]) for x, y in zip(ra, rb)
                     if x["condition"] not in DEFECTS)
        b_only = sum(truthy(y["success"]) and not truthy(x["success"]) for x, y in zip(ra, rb)
                     if x["condition"] not in DEFECTS)
        lines.append(
            f"| {ctrl} | {len(keys)} | {differ} | {sa['succ']} / {sb['succ']} of {sa['good']} "
            f"({a_only} / {b_only}, {mcnemar(a_only, b_only):.2g}) | {sa['bad_passed']} / {sb['bad_passed']} of {sa['bad']} | "
            f"{sa['escapes_good']} / {sb['escapes_good']} | {sa['false_rejects']} / {sb['false_rejects']} | {sa['stops']} / {sb['stops']} | "
            f"{sa['median_s']:.2f} / {sb['median_s']:.2f} | "
            + (f"{sa['bad_s']:.1f} / {sb['bad_s']:.1f} |" if sa["bad"] else "- |"))
    return lines + [""]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+", type=Path)
    ap.add_argument("--controllers", default="")
    args = ap.parse_args()
    if len(args.dirs) % 2:
        raise SystemExit("give folders in pairs")
    only = set(args.controllers.split(",")) if args.controllers else None
    for i in range(0, len(args.dirs), 2):
        print("\n".join(compare(args.dirs[i], args.dirs[i + 1], only)))


if __name__ == "__main__":
    main()
