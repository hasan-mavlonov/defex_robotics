"""H and I with one pull retry against the force-budget runs (v0.2d).

python -m experiments.v02d_pull_retry_tables results/v0.2d_pull_retry/dev
"""
from __future__ import annotations

import csv
from collections import Counter
from math import comb
from statistics import median

GOOD = {"latching": {"mf_nominal", "mf_moderate", "mf_noise_1mm"},
        "latch_spread": {"mf_spread", "mf_latch_early", "mf_latch_late", "mf_latch_weak", "mf_terminal_max",
                         "mf_terminal_min"}}
LETTER = {"spiral": "D", "adaptive": "C", "spiral_pull": "H", "spiral_rcc_pull": "I"}
import sys
BEFORE = "results/v0.2d_force_budget/after"
AFTER = sys.argv[1] if len(sys.argv) > 1 else "results/v0.2d_pull_retry/dev"


def mcnemar(b: int, c: int) -> float:
    n = b + c
    return 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def load(p):
    return {(r["controller"], r["condition"], r["trial_index"]): r for r in csv.DictReader(open(p))}


def ok(r):
    return r["success"] == "True"


def escape(r):
    return not ok(r) and r["protective_stop"] != "True" and r["declared_success"] != "False"


def stop(r):
    return r["protective_stop"] == "True"


def main() -> None:
    print("# v0.2d pull retry: H and I before (no retry) and after (one retry)\n")
    print(f"Before: `results/v0.2d_force_budget/after` (34520aa). After: `{AFTER}`. "
          "Seeds 2026 and 2027 pooled, 20 trials per condition and seed.\n")
    print("| Machine, suite | Ctrl | Rows differ | Good seated before -> after | Lost / gained (p) | "
          "Bad units on good parts | Bad parts passed | Stops good + bad | Median good cycle (s) | "
          "Good units/h (60 s/stop) |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    fails = Counter()
    for m in ("gantry", "arm"):
        for s in ("latching", "latch_spread"):
            B, A = {}, {}
            for seed in (2026, 2027):
                for k, v in load(f"{BEFORE}/{m}_{s}_s{seed}/trials.csv").items():
                    B[(seed,) + k] = v
                for k, v in load(f"{AFTER}/{m}_{s}_s{seed}/trials.csv").items():
                    A[(seed,) + k] = v
            for ctrl in LETTER:
                keys = [k for k in A if k[1] == ctrl]
                diff = sum(any(A[k][f] != B[k][f] for f in A[k] if f != "wall_time_s") for k in keys)
                good = [k for k in keys if k[2] in GOOD[s]]
                bad = [k for k in keys if k[2] not in GOOD[s]]
                lost = sum(ok(B[k]) and not ok(A[k]) for k in good)
                gain = sum(ok(A[k]) and not ok(B[k]) for k in good)

                def cell(R):
                    t = sum(float(R[k]["cycle_time_s"]) for k in keys) + 60.0 * sum(stop(R[k]) for k in keys)
                    n = sum(ok(R[k]) for k in good)
                    cyc = [float(R[k]["cycle_time_s"]) for k in good if ok(R[k])]
                    return (n, sum(escape(R[k]) for k in good), sum(escape(R[k]) for k in bad),
                            sum(stop(R[k]) for k in good), sum(stop(R[k]) for k in bad),
                            median(cyc) if cyc else float("nan"), 3600.0 * n / t)
                b, a = cell(B), cell(A)
                print(f"| {m}, {s} | {LETTER[ctrl]} | {diff} | {b[0]} -> {a[0]} of {len(good)} | "
                      f"{lost} / {gain} ({mcnemar(lost, gain):.2g}) | {b[1]} -> {a[1]} | {b[2]} -> {a[2]} of {len(bad)} | "
                      f"{b[3]}+{b[4]} -> {a[3]}+{a[4]} | {b[5]:.2f} -> {a[5]:.2f} | {b[6]:.0f} -> {a[6]:.0f} |")
                if ctrl in ("spiral_pull", "spiral_rcc_pull"):
                    for k in good:
                        if not ok(A[k]):
                            fails[(m, s, LETTER[ctrl], k[2], A[k]["failure_reason"])] += 1
            C = {k: A[k] for k in A if k[1] == "adaptive"}
            for ctrl in ("spiral_pull", "spiral_rcc_pull"):
                good = [k for k in C if k[2] in GOOD[s]]
                o = {k: A[(k[0], ctrl) + k[2:]] for k in good}
                x = sum(ok(C[k]) and not ok(o[k]) for k in good)
                y = sum(ok(o[k]) and not ok(C[k]) for k in good)
                print(f"| {m}, {s} | C vs {LETTER[ctrl]} after | | C-only / {LETTER[ctrl]}-only | {x} / {y} "
                      f"({mcnemar(x, y):.2g}) | | | | | |")
    print("\n## H and I good-part failures after the retry\n")
    print("| Machine | Suite | Ctrl | Condition | Reason | Trials |")
    print("|---|---|---|---|---|---|")
    for k, n in sorted(fails.items()):
        print("| " + " | ".join(k) + f" | {n} |")


if __name__ == "__main__":
    main()
