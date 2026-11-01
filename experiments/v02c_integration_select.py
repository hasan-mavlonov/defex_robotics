"""Apply results/v0.2c_integration/prior/SELECTION_RULE.md to the seed-4002 runs of one backend.

    python -m experiments.v02c_integration_select results/v0.2c_integration/prior/validation/gantry

Reads ranking/trials.csv and safety/trials.csv. Candidates are every variant except adaptive, g_v1 and
g_lp (g_lp is reported, not ranked). Gate: 0 bad units (escapes, experiments/checkpoint_report.py's
definition) over both runs. Rank the eligible candidates and g_v1 on the ranking run: most successes,
then lower median, then lower p95 cycle time of successes. Prints the ranking and the decision.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

REFS = ("adaptive", "g_v1", "g_lp")


def load(path: Path) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    with path.open() as fh:
        for r in csv.DictReader(fh):
            out.setdefault(r["controller"], []).append(r)
    return out


def escape(r: dict) -> bool:
    return r["success"] != "True" and r["protective_stop"] != "True" and r["declared_success"] != "False"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", type=Path)
    args = ap.parse_args()
    ranking = load(args.folder / "ranking" / "trials.csv")
    safety = load(args.folder / "safety" / "trials.csv")
    rows = []
    for v, rs in ranking.items():
        bad = sum(escape(r) for r in rs) + sum(escape(r) for r in safety.get(v, []))
        ct = [float(r["cycle_time_s"]) for r in rs if r["success"] == "True"]
        rows.append({"variant": v, "succ": sum(r["success"] == "True" for r in rs), "n": len(rs), "bad": bad,
                     "p50": float(np.percentile(ct, 50)), "p95": float(np.percentile(ct, 95))})
    print(f"Rule applied to `{args.folder}` (ranking + safety runs, seed 4002).\n")
    print("| Variant | Role | Successes | Bad units (both runs) | Median / p95 cycle (s) | Eligible |")
    print("|---|---|---|---|---|---|")
    ranked = []
    for r in rows:
        role = {"adaptive": "C (reported)", "g_v1": "reference", "g_lp": "reported only"}.get(r["variant"], "candidate")
        eligible = r["variant"] == "g_v1" or (r["variant"] not in REFS and r["bad"] == 0)
        if eligible:
            ranked.append(r)
        print(f"| {r['variant']} | {role} | {r['succ']}/{r['n']} | {r['bad']} | {r['p50']:.2f} / {r['p95']:.2f} | "
              f"{'yes' if eligible else 'no'} |")
    ranked.sort(key=lambda r: (-r["succ"], r["p50"], r["p95"]))
    print("\nRanking (successes, then median, then p95): " + " > ".join(r["variant"] for r in ranked))
    top = next((r for r in ranked if r["variant"] != "g_v1"), None)
    v1_pos = [r["variant"] for r in ranked].index("g_v1")
    if top is not None and [r["variant"] for r in ranked].index(top["variant"]) < v1_pos:
        print(f"\nDecision: install `{top['variant']}` (ranks above g_v1).")
    else:
        print("\nDecision: no candidate ranks above g_v1; install the v1 model.")


if __name__ == "__main__":
    main()
