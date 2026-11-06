"""Tables behind the v0.2c integration review fixes, recomputed from committed per-trial rows and event logs.

    python -m experiments.v02c_review_tables > results/v0.2c_integration/review_fixes/REVIEW_TABLES.md
"""

from __future__ import annotations

import csv
import gzip
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from experiments.checkpoint_report import escape, fmt_p, load, mcnemar, ok, paired, stop, uph

R = Path("results/v0.2c_integration")
SNAP = {2026: R / "snapshot_seed2026", 3032: R / "snapshot_seed3032"}
SUITES = [f"{b}_{s}" for b in ("gantry", "arm") for s in ("standard", "latching", "heldout")]
CLICK = re.compile(r"click (seen|not seen): drop ([\d.]+) N")


def good(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r["group"] != "bad_part"]


def pooled_g_vs_c() -> list[str]:
    out = ["## G against C, paired, good parts (snapshots; pooling not pre-registered)", "",
           "| Seed | Suite | C-only / G-only | McNemar p |", "|---|---|---|---|"]
    for seed, run in SNAP.items():
        tot = {"gantry": [0, 0], "arm": [0, 0]}
        for s in SUITES:
            co, go, _ = paired(good(load(run / s)), "adaptive", "adaptive_learned")
            tot[s.split("_")[0]][0] += co
            tot[s.split("_")[0]][1] += go
            out.append(f"| {seed} | {s} | {co} / {go} | {fmt_p(mcnemar(co, go))} |")
        for b, (co, go) in tot.items():
            out.append(f"| {seed} | {b}, three suites pooled | {co} / {go} | {fmt_p(mcnemar(co, go))} |")
        co, go = tot["gantry"][0] + tot["arm"][0], tot["gantry"][1] + tot["arm"][1]
        out.append(f"| {seed} | all six suites pooled | {co} / {go} | {fmt_p(mcnemar(co, go))} |")
    return out


def throughput() -> list[str]:
    out = ["", "## Good units per hour (good parts, 60 s per protective stop) and stops, C / G / F", "",
           "| Seed | Suite | C | G | F | Stops C / G / F |", "|---|---|---|---|---|---|"]
    for seed, run in SNAP.items():
        for s in SUITES:
            rows = good(load(run / s))
            by = {c: [r for r in rows if r["controller"] == c] for c in ("adaptive", "adaptive_learned", "spiral_rcc")}
            u = [f"{uph(by[c], 60.0):.0f}" for c in by]
            st = " / ".join(str(sum(stop(r) for r in by[c])) for c in by)
            out.append(f"| {seed} | {s} | {u[0]} | {u[1]} | {u[2]} | {st} |")
    return out


def training_escapes() -> list[str]:
    out = ["", "## Escapes of good parts in the integrated C's training and DAgger data (seeds 3001-3040)", "",
           "| Data | Trials | Escapes | Escape rows (condition, trial, final tilt deg, final depth mm) |",
           "|---|---|---|---|"]
    for f in sorted((R / "prior/data").glob("*/*/trials.csv")):
        rows = load(f.parent)
        esc = [r for r in rows if escape(r)]
        cells = "; ".join(f"{r['condition']} #{r['trial_index']} {float(r['final_tilt_deg']):.3f} "
                          f"{float(r['final_depth_mm']):.2f}" for r in esc)
        out.append(f"| {f.parent.relative_to(R)} | {len(rows)} | {len(esc)} | {cells} |")
    return out


def click_stats(folder: Path, ctrls: tuple[str, ...]) -> list[str]:
    ev = json.loads(gzip.open(folder / "events.json.gz").read())
    stats: dict[tuple, Counter] = defaultdict(Counter)
    drops: dict[tuple, list[float]] = defaultdict(list)
    for key, evs in ev.items():
        cond, ctrl, _ = key.split("|")
        if ctrl not in ctrls:
            continue
        for _, _, msg in evs:
            m = CLICK.search(msg)
            if m:
                stats[(ctrl, cond)][m.group(1)] += 1
                drops[(ctrl, cond)].append(float(m.group(2)))
    out = []
    for k in sorted(stats):
        d = drops[k]
        out.append(f"| {folder.relative_to(R)} | {k[0]} | {k[1]} | {stats[k]['seen']} | {stats[k]['not seen']} | "
                   f"{np.median(d):.1f} | {min(d):.1f} |")
    return out


def clicks() -> list[str]:
    out = ["", "## What the W3 click detector sees (latch checks in the event logs; threshold 2.4 N)", "",
           "| Run | Controller | Condition | Click seen | Not seen | Median drop (N) | Min drop (N) |",
           "|---|---|---|---|---|---|---|"]
    for b in ("gantry", "arm"):
        out += click_stats(SNAP[2026] / f"{b}_latching", ("adaptive",))
    spread = R / "review_fixes/spread_dev2026_before"
    for b in ("gantry", "arm"):
        if (spread / f"{b}_latch_spread/events.json.gz").exists():
            out += click_stats(spread / f"{b}_latch_spread", ("adaptive",))
    return out


def baseline_pull() -> list[str]:
    """D and F with C's installed latch check (variant 'pull'), against C, seed 2026, code b57e0db."""
    out = ["", "## D and F with the same retention pull as C (development comparison, seed 2026, code b57e0db)", "",
           "Sources: `review_fixes/snapshot2026_after` (A-G) and `review_fixes/baseline_pull_dev2026` (`@pull`).", "",
           "| Suite | Controller | Good parts seated | Good parts passed unseated | Bad parts passed | "
           "Stops (good parts) | Good units/h (60 s per stop) | vs C: C-only / other-only (p) |",
           "|---|---|---|---|---|---|---|---|"]
    for s in ("gantry_latching", "arm_latching", "gantry_latch_spread", "arm_latch_spread"):
        rows = load(R / "review_fixes/snapshot2026_after" / s) + load(R / "review_fixes/baseline_pull_dev2026" / s)
        for c in ("spiral", "spiral@pull", "spiral_rcc", "spiral_rcc@pull", "adaptive", "adaptive_learned"):
            rs = [r for r in rows if r["controller"] == c]
            g, bad = good(rs), [r for r in rs if r["group"] == "bad_part"]
            pair = "reference" if c == "adaptive" else "{} / {} ({})".format(
                *paired(good(rows), "adaptive", c)[:2], fmt_p(mcnemar(*paired(good(rows), "adaptive", c)[:2])))
            out.append(f"| {s} | {c} | {sum(ok(r) for r in g)}/{len(g)} | {sum(escape(r) for r in g)} | "
                       f"{sum(escape(r) for r in bad)}/{len(bad)} | {sum(stop(r) for r in g)} | {uph(g, 60.0):.0f} | {pair} |")
    return out


def main() -> None:
    lines = ["# v0.2c integration review: recomputed tables", "",
             "Generated by `python -m experiments.v02c_review_tables` from committed trials.csv and events.json.gz "
             "files (paths in each table). Snapshots: code 96a4be3; seed 2026 run at 96a4be3, seed 3032 at 586caed.",
             ""]
    lines += pooled_g_vs_c() + throughput() + training_escapes() + clicks() + baseline_pull()
    print("\n".join(lines))


if __name__ == "__main__":
    main()
