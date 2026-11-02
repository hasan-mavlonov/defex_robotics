"""Checkpoint report: every table for a multi-suite, multi-backend benchmark, from trials.csv.

    python -m experiments.checkpoint_report results/benchmark_v0.2b > results/benchmark_v0.2b/TABLES.md

Expects results/<run>/<backend>_<suite>/trials.csv. Numbers are recomputed from the
per-trial rows, not read from summary.json, so the tables also audit the summaries.
The last section applies the decision rules of the pre-registration mechanically.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from defex.logging.metrics import STOP_RESET_S

ORDER = ["fixed", "correction", "correction_rcc", "spiral", "spiral_rcc", "spiral_pull", "spiral_rcc_pull",
         "spiral_rcc_verify", "spiral_rcc_verify_reject", "spiral_rcc_verify_research",
         "spiral_rcc_verify_reject_no_rcc", "adaptive", "adaptive_learned"]
LETTER = {"fixed": "A", "correction": "B", "correction_rcc": "E", "spiral": "D", "spiral_rcc": "F",
          "adaptive": "C", "adaptive_learned": "G", "spiral_pull": "H", "spiral_rcc_pull": "I",
          "spiral_rcc_verify": "J", "spiral_rcc_verify_reject": "J(a)", "spiral_rcc_verify_research": "J(b)",
          "spiral_rcc_verify_reject_no_rcc": "J(a) no RCC terms"}
# J (v0.2d) runs C's VERIFY: not a conventional baseline, so not in FAIR.
FAIR = ("spiral", "correction_rcc", "spiral_rcc", "spiral_pull", "spiral_rcc_pull")  # D, E, F, H, I
DEFECTS = ("mf_half_latched", "mf_broken_latch", "mf_stubbed_terminal", "mf_wrong_polarization")


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def mcnemar(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / (1 << n))


def ok(r: dict) -> bool:
    return r["success"] == "True"


def stop(r: dict) -> bool:
    return r["protective_stop"] == "True"


def escape(r: dict) -> bool:
    return not ok(r) and not stop(r) and r["declared_success"] != "False"


def false_reject(r: dict) -> bool:
    return r["gt_seated"] == "True" and r["declared_success"] == "False"


def uph(rs: list[dict], reset_s: float) -> float:
    busy = sum(float(r["cycle_time_s"]) for r in rs) + reset_s * sum(stop(r) for r in rs)
    return 3600.0 * sum(ok(r) for r in rs) / busy if busy > 0 else float("nan")


def fmt_p(p: float) -> str:
    return "<1e-6" if p < 1e-6 else f"{p:.2g}"


def load(folder: Path) -> list[dict]:
    with (folder / "trials.csv").open() as fh:
        return list(csv.DictReader(fh))


def paired(rows: list[dict], a: str, b: str, pred=ok) -> tuple[int, int, int]:
    """(a-only, b-only, pairs): trials where pred holds for one controller only, over trials both ran."""
    idx = {(r["controller"], r["condition"], r["trial_index"]): pred(r) for r in rows}
    keys = [(cd, i) for (cc, cd, i) in idx if cc == a and (b, cd, i) in idx]
    ao = sum(idx[(a, cd, i)] and not idx[(b, cd, i)] for cd, i in keys)
    bo = sum(idx[(b, cd, i)] and not idx[(a, cd, i)] for cd, i in keys)
    return ao, bo, len(keys)


def controllers(rows: list[dict]) -> list[str]:
    present = {r["controller"] for r in rows}
    return [c for c in ORDER if c in present]


def success_table(rows: list[dict], title: str) -> list[str]:
    by = defaultdict(list)
    for r in rows:
        by[r["controller"]].append(r)
    out = [f"\n{title}\n",
           "| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | "
           "Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | "
           "p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for c in controllers(rows):
        rs = by[c]
        k, n = sum(ok(r) for r in rs), len(rs)
        lo, hi = wilson(k, n)
        ct = [float(r["cycle_time_s"]) for r in rs if ok(r)]
        cyc = "/".join(f"{np.percentile(ct, q):.2f}" for q in (50, 95, 99)) if ct else "n/a"
        f95 = np.percentile([float(r["peak_contact_force_n"]) for r in rs], 95)
        t95 = np.percentile([float(r["peak_measured_torque_nm"]) for r in rs], 95)
        if c == "adaptive":
            pair = "reference"
        else:
            co, oo, m = paired(rows, "adaptive", c)
            pair = f"{co} / {oo} ({fmt_p(mcnemar(co, oo))})" if m else "n/a"
        out.append(f"| {LETTER[c]} {c} | {100 * k / n:.1f}% ({100 * lo:.1f}-{100 * hi:.1f}) | "
                   f"{sum(escape(r) for r in rs)} | {sum(false_reject(r) for r in rs)} | {sum(stop(r) for r in rs)} | "
                   f"{cyc} | {uph(rs, 0.0):.0f} / {uph(rs, STOP_RESET_S):.0f} | {f95:.1f} | {t95:.2f} | {pair} |")
    return out


def per_condition(rows: list[dict]) -> list[str]:
    ctrls = controllers(rows)
    conds: list[str] = []
    for r in rows:
        if r["condition"] not in conds:
            conds.append(r["condition"])
    cell = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        x = cell[(r["condition"], r["controller"])]
        x[0] += ok(r)
        x[1] += 1
        x[2] += escape(r)
    out = ["", "Successes per condition (bad units passed in brackets when not zero):", "",
           "| Condition | " + " | ".join(LETTER[c] for c in ctrls) + " |", "|---" * (len(ctrls) + 1) + "|"]
    for cd in conds:
        cells = []
        for c in ctrls:
            k, n, e = cell[(cd, c)]
            cells.append(f"{k}/{n}" + (f" ({e})" if e else ""))
        out.append(f"| {cd} | " + " | ".join(cells) + " |")
    return out


def defect_table(rows: list[dict], good: list[dict] | None = None) -> list[str]:
    """Bad parts passed per defect; with ``good``, each controller's good-part success in the same suite
    underneath (a controller that rarely seats a good part also rarely passes a bad one)."""
    ctrls = controllers(rows)
    defects = list(dict.fromkeys(r["condition"] for r in rows))
    total = "all four" if set(defects) <= set(DEFECTS) else f"all {len(defects)} bad-part conditions"
    if set(defects) <= set(DEFECTS):
        defects = [d for d in DEFECTS if d in defects] if defects else list(DEFECTS)
    out = ["", "Deliberately bad parts passed as good (escapes / trials; Wilson 95% upper bound of the "
           "false-accept rate). Protective stops on bad parts in the second table.", "",
           "| Defect | " + " | ".join(LETTER[c] for c in ctrls) + " |", "|---" * (len(ctrls) + 1) + "|"]
    stops = ["", "| Defect, protective stops | " + " | ".join(LETTER[c] for c in ctrls) + " |",
             "|---" * (len(ctrls) + 1) + "|"]
    for d in defects + [total]:
        cells, sc = [], []
        for c in ctrls:
            rs = [r for r in rows if r["controller"] == c and (r["condition"] in defects if d == total
                                                               else r["condition"] == d)]
            if not rs:
                cells.append("")
                sc.append("")
                continue
            e = sum(escape(r) for r in rs)
            cells.append(f"{e}/{len(rs)} (<= {100 * wilson(e, len(rs))[1]:.1f}%)")
            sc.append(f"{sum(stop(r) for r in rs)}/{len(rs)}")
        out.append(f"| {d} | " + " | ".join(cells) + " |")
        stops.append(f"| {d} | " + " | ".join(sc) + " |")
    cells = []
    for c in ctrls:
        cyc = [float(r["cycle_time_s"]) for r in rows if r["controller"] == c]
        cells.append(f"{float(np.median(cyc)):.1f}" if cyc else "")
    out.append("| median cycle per bad part (s) | " + " | ".join(cells) + " |")
    if good:
        cells = []
        for c in ctrls:
            rs = [r for r in good if r["controller"] == c]
            cells.append(f"{sum(ok(r) for r in rs)}/{len(rs)}" if rs else "")
        out.append("| for reference: good parts seated | " + " | ".join(cells) + " |")
    return out + stops


def decisions(name: str, rows: list[dict]) -> list[str]:
    """The pre-registered decision rules, applied to one backend and suite (good parts on latching)."""
    present = controllers(rows)
    if "adaptive" not in present:
        return []
    rate = {c: sum(ok(r) for r in rows if r["controller"] == c) / max(1, sum(r["controller"] == c for r in rows))
            for c in present}
    out = []
    fair = [c for c in FAIR if c in present]
    if fair:
        best = max(fair, key=lambda c: rate[c])
        co, bo, _ = paired(rows, "adaptive", best)
        p = mcnemar(co, bo)
        gap = 100 * (rate["adaptive"] - rate[best])
        if gap < 0 and p < 0.05:
            verdict = "C below the best fair baseline, p < 0.05: goes in the README headline"
        elif p >= 0.05 or gap < 1.0:
            verdict = "a fair baseline matches C: goes in the README headline; Hasan decides the pitch"
        else:
            verdict = "C ahead of every fair baseline"
        out.append(f"| {name} | C vs best of {"/".join(LETTER[c] for c in fair)} ({LETTER[best]}) | {100 * rate['adaptive']:.1f}% vs "
                   f"{100 * rate[best]:.1f}% ({gap:+.1f} pts) | {co} / {bo} | {fmt_p(p)} | {verdict} |")
    if "adaptive_learned" in present:
        co, go, _ = paired(rows, "adaptive", "adaptive_learned")
        p = mcnemar(co, go)
        gap = 100 * (rate["adaptive_learned"] - rate["adaptive"])
        verdict = ("G helps" if gap > 0 and p < 0.05 else "G worse" if gap < 0 and p < 0.05
                   else "no measurable gain from G")
        out.append(f"| {name} | G vs C | {100 * rate['adaptive_learned']:.1f}% vs {100 * rate['adaptive']:.1f}% "
                   f"({gap:+.1f} pts) | {co} / {go} (C-only / G-only) | {fmt_p(p)} | {verdict} |")
    return out


def defect_decision(name: str, rows: list[dict]) -> list[str]:
    present = controllers(rows)
    fair = [c for c in FAIR if c in present]
    if "adaptive" not in present or not fair:
        return []
    esc = {c: sum(escape(r) for r in rows if r["controller"] == c) for c in present}
    n = {c: sum(r["controller"] == c for r in rows) for c in present}
    best = min(fair, key=lambda c: esc[c])
    co, bo, _ = paired(rows, "adaptive", best, escape)
    p = mcnemar(co, bo)
    hi = 100 * wilson(esc["adaptive"], n["adaptive"])[1]
    verdict = ("C passes fewer bad parts, p < 0.05" if esc["adaptive"] < esc[best] and p < 0.05
               else "no significant difference in bad parts passed")
    out = [f"| {name} | bad parts passed, C vs fewest of {"/".join(LETTER[c] for c in fair)} ({LETTER[best]}) | {esc['adaptive']}/{n['adaptive']} "
           f"(<= {hi:.1f}%) vs {esc[best]}/{n[best]} | {co} / {bo} | {fmt_p(p)} | {verdict} |"]
    if "adaptive_learned" in present:
        out.append(f"| {name} | bad parts passed, G | {esc['adaptive_learned']}/{n['adaptive_learned']} (<= "
                   f"{100 * wilson(esc['adaptive_learned'], n['adaptive_learned'])[1]:.1f}%) | | | |")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run", type=Path)
    args = ap.parse_args()
    lines = [f"# Tables for {args.run.name}", "",
             f"Generated by `python -m experiments.checkpoint_report {args.run}` from the per-trial rows. "
             f"Bad units passed = failed and neither stopped nor declared failed (defex.logging.metrics.is_escape). "
             f"False rejects = seated in ground truth but declared failed. Good units per hour count every "
             f"cycle, plus {STOP_RESET_S:.0f} s per protective stop in the second figure (assumed reset time)."]
    rules = []
    for folder in sorted(p for p in args.run.iterdir() if (p / "trials.csv").exists()):
        rows = load(folder)
        backend, _, suite = folder.name.partition("_")
        lines.append(f"\n## {backend}, {suite} suite")
        if suite in ("latching", "latch_spread"):
            good = [r for r in rows if r["group"] != "bad_part"]
            bad = [r for r in rows if r["group"] == "bad_part"]
            lines += success_table(good, "Good parts:")
            lines += per_condition(good)
            lines += defect_table(bad, good)
            rules += decisions(f"{backend}, {suite} (good parts)", good)
            rules += defect_decision(f"{backend}, {suite} (bad parts)", bad)
        else:
            lines += success_table(rows, "All conditions:")
            lines += per_condition(rows)
            rules += decisions(f"{backend}, {suite}", rows)
    if rules:
        lines += ["\n## Pre-registered decision rules, applied", "",
                  "| Backend, suite | Comparison | Success | Discordant pairs | McNemar p | Rule outcome |",
                  "|---|---|---|---|---|---|", *rules]
    print("\n".join(lines))


if __name__ == "__main__":
    main()
