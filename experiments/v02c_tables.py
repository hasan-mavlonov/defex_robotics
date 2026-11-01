"""Before/after tables for the v0.2c arm-robustness workstream (paired by condition and trial index).

    python -m experiments.v02c_tables BEFORE_DIR:CTRL AFTER_DIR:CTRL [--title T] [...more pairs]

Each pair compares controller CTRL in BEFORE_DIR/trials.csv with controller CTRL in AFTER_DIR/trials.csv
(the same scenarios: same seed, condition and trial index). Prints a markdown table per pair: success with
Wilson 95% intervals, before-only / after-only successes with the exact McNemar p, escapes (failed units the
cell did not stop and the controller did not declare failed), protective stops, failure reasons and the
median / p95 cycle of successes. Bad-part conditions are counted as escapes only.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

import numpy as np

from experiments.checkpoint_report import DEFECTS, escape, fmt_p, mcnemar, ok, stop, wilson


def _load(spec: str) -> tuple[str, str, dict]:
    folder, ctrl = spec.rsplit(":", 1)
    rows = {(r["condition"], r["trial_index"]): r for r in csv.DictReader(open(Path(folder) / "trials.csv"))
            if r["controller"] == ctrl}
    return folder, ctrl, rows


def _cyc(rows: list[dict]) -> str:
    c = [float(r["cycle_time_s"]) for r in rows if ok(r)]
    return f"{np.median(c):.2f} / {np.percentile(c, 95):.2f}" if c else "-"


def _fail(rows: list[dict]) -> str:
    n = Counter(r["failure_reason"] for r in rows if not ok(r))
    return ", ".join(f"{k} {v}" for k, v in sorted(n.items())) or "-"


def table(before: str, after: str) -> list[str]:
    fb, cb, rb = _load(before)
    fa, ca, ra = _load(after)
    keys = sorted(rb.keys() & ra.keys(), key=lambda k: (k[0], int(k[1])))
    conds = list(dict.fromkeys(k[0] for k in keys))
    out = [f"`{fb}` ({cb}) -> `{fa}` ({ca}), {len(keys)} paired trials", "",
           "| Condition | n | Success before | Success after | 95% CI after | Before-only / after-only (McNemar p) "
           "| Escapes before / after | Stops before / after | Cycle p50 / p95 before (s) | after (s) | Failures after |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]

    def row(name: str, ks: list) -> str:
        b = [rb[k] for k in ks]
        a = [ra[k] for k in ks]
        good = [k for k in ks if k[0] not in DEFECTS]
        sb = sum(ok(rb[k]) for k in good)
        sa = sum(ok(ra[k]) for k in good)
        bo = sum(ok(rb[k]) and not ok(ra[k]) for k in good)
        ao = sum(ok(ra[k]) and not ok(rb[k]) for k in good)
        lo, hi = wilson(sa, len(good))
        ci = f"{100 * lo:.0f}-{100 * hi:.0f}%" if good else "-"
        succ = (f"{sb}/{len(good)}", f"{sa}/{len(good)}") if good else ("-", "-")
        return (f"| {name} | {len(ks)} | {succ[0]} | {succ[1]} | {ci} | {bo} / {ao} ({fmt_p(mcnemar(bo, ao))}) | "
                f"{sum(map(escape, b))} / {sum(map(escape, a))} | {sum(map(stop, b))} / {sum(map(stop, a))} | "
                f"{_cyc([r for r in b if r['condition'] not in DEFECTS])} | "
                f"{_cyc([r for r in a if r['condition'] not in DEFECTS])} | {_fail([r for r in a if r['condition'] not in DEFECTS])} |")

    for cond in conds:
        out.append(row(cond, [k for k in keys if k[0] == cond]))
    if len(conds) > 1:
        out.append(row("**all**", keys))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pairs", nargs="+", help="BEFORE_DIR:CTRL AFTER_DIR:CTRL, repeated")
    args = ap.parse_args()
    assert len(args.pairs) % 2 == 0
    for i in range(0, len(args.pairs), 2):
        print("\n".join(table(args.pairs[i], args.pairs[i + 1])) + "\n")


if __name__ == "__main__":
    main()
