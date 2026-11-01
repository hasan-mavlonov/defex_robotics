"""Tables for results/v0.2c_learned_prior from committed trials.csv files (v0.2c).

    python -m experiments.v02c_tables closed-loop DIR [DIR ...] --refs adaptive,adaptive_learned [--title T]
    python -m experiments.v02c_tables offline FILE.json [FILE.json ...]

closed-loop: one row per controller variant over the pooled directories: successes with
the 95% Wilson interval, bad units passed, protective stops, median and p95 cycle time of
successes, and paired McNemar (exact) against each reference controller, plus the same
per condition. offline: the combined-posterior table of experiments.train_contact_likelihood
evaluate outputs.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from defex.logging.metrics import is_escape, mcnemar_exact, read_trials_csv, wilson_interval


def _cyc(rs):
    ok = [r.cycle_time_s for r in rs if r.success]
    return (float(np.median(ok)), float(np.percentile(ok, 95))) if ok else (None, None)


def _pair(a, b):
    ka = {(r.condition, r.trial_index): r for r in a}
    kb = {(r.condition, r.trial_index): r for r in b}
    keys = ka.keys() & kb.keys()
    a_only = sum(ka[k].success and not kb[k].success for k in keys)
    b_only = sum(kb[k].success and not ka[k].success for k in keys)
    return a_only, b_only, mcnemar_exact(a_only, b_only), len(keys)


def closed_loop(dirs: list[Path], refs: list[str], title: str) -> str:
    results = [r for d in dirs for r in read_trials_csv(d / "trials.csv")]
    by: dict[str, list] = defaultdict(list)
    seen: dict[tuple, object] = {}
    for r in results:
        key = (r.controller, r.condition, r.trial_index, r.seed)
        if key in seen:  # the same trial in two run parts (C is re-run as each part's paired reference)
            a, b = seen[key].to_row(), r.to_row()
            if any(a[k] != b[k] for k in a if k != "wall_time_s"):
                raise SystemExit(f"trial {key} differs between run parts")
            continue
        seen[key] = r
        by[r.controller].append(r)
    conds = list(dict.fromkeys(r.condition for r in results))
    lines = [f"### {title}", "", "Sources: " + ", ".join(f"`{d}`" for d in dirs), ""]
    ref_cols = " | ".join(f"vs {x}: ref-only / this-only (p)" for x in refs)
    lines += [f"| Variant | Trials | Successes (95% CI) | Bad units | Stops | Median / p95 cycle (s) | {ref_cols} |",
              "|---|---|---|---|---|---|" + "---|" * len(refs)]
    for ctl, rs in by.items():
        k, n = sum(r.success for r in rs), len(rs)
        lo, hi = wilson_interval(k, n)
        med, p95 = _cyc(rs)
        cells = []
        for ref in refs:
            if ref == ctl or ref not in by:
                cells.append("-")
                continue
            a, b, p, _ = _pair(by[ref], rs)
            cells.append(f"{a} / {b} ({p:.2g})")
        lines.append(f"| {ctl} | {n} | {k} ({100 * lo:.1f}-{100 * hi:.1f}%) | {sum(is_escape(r) for r in rs)} | "
                     f"{sum(r.protective_stop for r in rs)} | {med:.2f} / {p95:.2f} | " + " | ".join(cells) + " |"
                     if med is not None else f"| {ctl} | {n} | {k} | - | - | - | " + " | ".join(cells) + " |")
    lines += ["", "Per condition, successes (bad units, stops):", "",
              "| Condition | " + " | ".join(by) + " |", "|---|" + "---|" * len(by)]
    for c in conds:
        row = []
        for ctl, rs in by.items():
            rc = [r for r in rs if r.condition == c]
            row.append(f"{sum(r.success for r in rc)}/{len(rc)} ({sum(is_escape(r) for r in rc)}, "
                       f"{sum(r.protective_stop for r in rc)})")
        lines.append(f"| {c} | " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def offline(files: list[Path]) -> str:
    lines = []
    for f in files:
        d = json.loads(f.read_text())
        lines += [f"### {d['backend']}: `{f}`", ""]
        for split, s in d["splits"].items():
            lines += [f"Split `{split}`: {s['n_on_grid']} contacts on the grid ({s['n_first_contact']} first contacts); "
                      f"replay max deviation from C's recorded posterior mean {s['replay_max_dev_mm']} mm", "",
                      "| Candidate | w | Grid NLL all / first (nats) | Mean error all / first (mm) | "
                      "Outside 50% HPD (exp. 0.50) | Outside 95% HPD (exp. 0.05) | Next probe in capture all / first |",
                      "|---|---|---|---|---|---|---|"]
            for name, r in s["candidates"].items():
                a, fc = r["all"], r["first_contact"]
                lines.append(f"| {name} | {r['weight']:g} | {a['grid_nll_nats']:.3f} / {fc['grid_nll_nats']:.3f} | "
                             f"{a['mean_radial_error_mm']:.2f} / {fc['mean_radial_error_mm']:.2f} | "
                             f"{a['outside_hpd50']:.2f} | {a['outside_hpd95']:.3f} | "
                             f"{a['next_probe_in_capture']:.3f} / {fc['next_probe_in_capture']:.3f} |")
            lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("closed-loop")
    c.add_argument("dirs", type=Path, nargs="+")
    c.add_argument("--refs", default="adaptive,adaptive_learned")
    c.add_argument("--title", default="Closed loop")
    o = sub.add_parser("offline")
    o.add_argument("files", type=Path, nargs="+")
    args = ap.parse_args()
    if args.cmd == "closed-loop":
        print(closed_loop(args.dirs, args.refs.split(","), args.title))
    else:
        print(offline(args.files))


if __name__ == "__main__":
    main()
