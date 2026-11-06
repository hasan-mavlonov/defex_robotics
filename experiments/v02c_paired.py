"""Paired C vs H and I, escapes on good-part trials, latch_spread without mf_terminal_max.

python -m experiments.v02c_paired results/benchmark_v0.2c

When a run has J (v0.2d: F + C's VERIFY), J paired against C and against I in a second table with the same
columns, and a J column in the per-machine escapes; neither appears without J.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from math import comb
from pathlib import Path

GOOD = {
    "latching": {"mf_nominal", "mf_moderate", "mf_noise_1mm"},
    "latch_spread": {"mf_spread", "mf_latch_early", "mf_latch_late", "mf_latch_weak", "mf_terminal_max",
                     "mf_terminal_min"},
}
LETTER = {"adaptive": "C", "adaptive_learned": "G", "spiral": "D", "spiral_rcc": "F", "spiral_pull": "H",
          "spiral_rcc_pull": "I", "spiral_rcc_verify": "J"}
J = "spiral_rcc_verify"


def mcnemar(b: int, c: int) -> float:
    n = b + c
    return 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def ok(r) -> bool:
    return r["success"] == "True"


def escape(r) -> bool:
    return not ok(r) and r["protective_stop"] != "True" and r["declared_success"] != "False"


def pair_line(rows: dict, run: str, name: str, keep, a: str, other: str) -> str:
    """One paired row: ``a`` against ``other`` on the trials of ``a`` whose condition ``keep`` accepts."""
    keys = [k for k in rows if k[0] == a and keep(k[1])]
    pairs = [(rows[k], rows[(other,) + k[1:]]) for k in keys]
    b = sum(ok(x) and not ok(y) for x, y in pairs)
    c = sum(ok(y) and not ok(x) for x, y in pairs)
    eb = sum(escape(x) and not escape(y) for x, y in pairs)
    ec = sum(escape(y) and not escape(x) for x, y in pairs)
    return (f"| {run}, {name} | {LETTER[other]} | {len(keys)} | {sum(ok(x) for x, _ in pairs)} / "
            f"{sum(ok(y) for _, y in pairs)} | {b} / {c} | {mcnemar(b, c):.2g} | "
            f"{sum(escape(x) for x, _ in pairs)} / {sum(escape(y) for _, y in pairs)} | "
            f"{mcnemar(eb, ec):.2g} |")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    root = ap.parse_args().root
    print(f"# Paired comparisons for {root.name}\n")
    print("| Run | C vs | Trials | Successes C / other | C-only / other-only | p | Escapes C / other | p |")
    print("|---|---|---|---|---|---|---|---|")
    esc_total, esc_rows, j_lines, has_j = Counter(), {}, [], False
    for run in sorted(p.name for p in root.iterdir() if (p / "trials.csv").exists()):
        suite = run.split("_", 1)[1]
        rows = {(r["controller"], r["condition"], r["trial_index"]): r
                for r in csv.DictReader(open(root / run / "trials.csv"))}
        good = GOOD.get(suite)
        sets = [("good parts", lambda c: good is None or c in good)]
        if suite == "latch_spread":
            sets.append(("good parts without mf_terminal_max", lambda c: c in good - {"mf_terminal_max"}))
        for other in ("spiral_rcc_pull", "spiral_pull"):
            for name, keep in sets:
                print(pair_line(rows, run, name, keep, "adaptive", other))
        present = {k[0] for k in rows}
        if J in present:
            has_j = True
            for other in ("adaptive", "spiral_rcc_pull"):
                if other in present:
                    j_lines += [pair_line(rows, run, name, keep, J, other) for name, keep in sets]
        for ctrl in LETTER:
            e = [r for k, r in rows.items() if k[0] == ctrl and (good is None or k[1] in good) and escape(r)]
            esc_total[(run.split("_")[0], ctrl)] += len(e)
            esc_rows.setdefault(ctrl, []).extend((run, r) for r in e)
    if has_j:
        print("\n## J against C and against I\n")
        print("| Run | J vs | Trials | Successes J / other | J-only / other-only | p | Escapes J / other | p |")
        print("|---|---|---|---|---|---|---|---|")
        print("\n".join(j_lines))
    shown = [c for c in LETTER if c != J or has_j]
    print("\n## Bad units passed on good-part trials, per machine\n")
    print("| Machine | " + " | ".join(LETTER[c] for c in shown) + " |")
    print("|---|" + "---|" * len(shown))
    for m in ("gantry", "arm"):
        print(f"| {m} | " + " | ".join(str(esc_total[(m, c)]) for c in shown) + " |")
    print("\n## I's escapes on good-part trials\n")
    print("| Run | Escapes | Depth min-max (mm) | Tilt max (deg) | Lateral max (mm) | Reasons | Conditions |")
    print("|---|---|---|---|---|---|---|")
    by_run = {}
    for run, r in esc_rows.get("spiral_rcc_pull", []):
        by_run.setdefault(run, []).append(r)
    for run, rs in sorted(by_run.items()):
        d = [float(r["final_depth_mm"]) for r in rs]
        print(f"| {run} | {len(rs)} | {min(d):.2f}-{max(d):.2f} | "
              f"{max(float(r['final_tilt_deg']) for r in rs):.2f} | "
              f"{max(float(r['final_lateral_mm']) for r in rs):.2f} | "
              f"{dict(Counter(r['failure_reason'] for r in rs))} | "
              f"{dict(Counter(r['condition'] for r in rs).most_common())} |")


if __name__ == "__main__":
    main()
