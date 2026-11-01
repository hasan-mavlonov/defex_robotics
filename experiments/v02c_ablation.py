"""Paired variant table for one trials.csv holding several ``adaptive@variant`` controllers (v0.2c).

    python -m experiments.v02c_ablation results/<run> [--reference adaptive@all]

Per variant: successes on good parts, reference-only / variant-only successes with the exact McNemar p,
escapes, protective stops, median / p95 cycle of successes; per condition and pooled.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

from experiments.checkpoint_report import DEFECTS, escape, fmt_p, mcnemar, ok, stop, wilson


def report(run: Path, reference: str) -> list[str]:
    rows = list(csv.DictReader(open(run / "trials.csv")))
    by: dict = defaultdict(dict)
    for r in rows:
        by[r["controller"]][(r["condition"], r["trial_index"])] = r
    ref = by[reference]
    conds = list(dict.fromkeys(r["condition"] for r in rows))
    out = [f"`{run}`, reference `{reference}`", "",
           "| Variant | Condition | Success | 95% CI | Ref-only / variant-only (McNemar p) | Escapes | Stops | Cycle p50 / p95 (s) |",
           "|---|---|---|---|---|---|---|---|"]
    for v, d in by.items():
        for cond in conds + ["all"]:
            ks = [k for k in d if (cond == "all" or k[0] == cond) and k in ref]
            good = [k for k in ks if k[0] not in DEFECTS]
            s = sum(ok(d[k]) for k in good)
            ro = sum(ok(ref[k]) and not ok(d[k]) for k in good)
            vo = sum(ok(d[k]) and not ok(ref[k]) for k in good)
            lo, hi = wilson(s, len(good))
            cyc = [float(d[k]["cycle_time_s"]) for k in good if ok(d[k])]
            c = f"{np.median(cyc):.2f} / {np.percentile(cyc, 95):.2f}" if cyc else "-"
            out.append(f"| {v} | {cond} | {s}/{len(good)} | {100 * lo:.0f}-{100 * hi:.0f}% | {ro} / {vo} "
                       f"({fmt_p(mcnemar(ro, vo))}) | {sum(escape(d[k]) for k in ks)} | {sum(stop(d[k]) for k in ks)} | {c} |")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run", type=Path)
    ap.add_argument("--reference", default="adaptive@all")
    args = ap.parse_args()
    print("\n".join(report(args.run, args.reference)))


if __name__ == "__main__":
    main()
