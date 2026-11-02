"""v0.2d force budget: before (insert target 30 N) against after (35.2 N), every controller, paired.

    python -m experiments.v02d_force_budget_tables results/v0.2d_force_budget > results/v0.2d_force_budget/TABLES.md

Reads <root>/{before,after}/<backend>_<suite>_s<seed>/trials.csv for the latching and latch_spread suites,
pairs each trial before and after on (base seed, condition, trial index) and pools the seeds.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from defex.config import ConnectorSpec
from defex.logging.metrics import STOP_RESET_S
from experiments.checkpoint_report import LETTER, ORDER, escape, false_reject, fmt_p, load, mcnemar, ok, stop, uph

SUITES = ("latching", "latch_spread")
BACKENDS = ("gantry", "arm")
SAFETY_DAMAGE_N = 45.0  # SafetyConfig.damage_contact_force_n, the housing-only connector's damage bound


def good(r: dict) -> bool:
    return r["group"] != "bad_part"


def f10(r: dict) -> float:
    return float(r["peak_contact_force_10ms_n"])


def phase(root: Path, name: str, backend: str, suite: str) -> tuple[dict, list[str]]:
    rows, meta = {}, []
    for folder in sorted(root.glob(f"{name}/{backend}_{suite}_s*")):
        if not (folder / "summary.json").exists():
            continue
        cfg = json.loads((folder / "config.json").read_text())
        env = cfg["environment"]
        seed = cfg["base_seed"]
        meta.append(f"`{folder.relative_to(root.parent)}` (seed {seed}, commit {env['git_commit'][:7]}, "
                    f"dirty {env['git_dirty']})")
        for r in load(folder):
            rows[(r["controller"], seed, r["condition"], r["trial_index"])] = r
    return rows, meta


def ctrl_rows(rows: dict, c: str, pred=lambda r: True) -> list[dict]:
    return [r for k, r in rows.items() if k[0] == c and pred(r)]


def pair(before: dict, after: dict, c: str, pred=good) -> tuple[int, int, int]:
    keys = [k for k in before if k[0] == c and k in after and pred(before[k])]
    lost = sum(ok(before[k]) and not ok(after[k]) for k in keys)
    gained = sum(ok(after[k]) and not ok(before[k]) for k in keys)
    return lost, gained, len(keys)


def summary(rs: list[dict], damage_n: float) -> dict:
    g = [r for r in rs if good(r)]
    b = [r for r in rs if not good(r)]
    ct = [float(r["cycle_time_s"]) for r in g if ok(r)]
    return {
        "seated": f"{sum(ok(r) for r in g)}/{len(g)}",
        "bad_passed": f"{sum(escape(r) for r in b)}/{len(b)}",
        "esc_good": str(sum(escape(r) for r in g)),
        "false_rej": str(sum(false_reject(r) for r in g)),
        "stops": f"{sum(stop(r) for r in g)} + {sum(stop(r) for r in b)}",
        "damage": str(sum(f10(r) > damage_n for r in rs)),
        "over45": str(sum(f10(r) > SAFETY_DAMAGE_N for r in rs)),
        "max10": f"{max(f10(r) for r in rs):.1f}",
        "maxmeas": f"{max(float(r['peak_measured_force_n']) for r in rs):.1f}",
        "cycle": f"{np.median(ct):.2f}" if ct else "n/a",
        "uph": f"{uph(g, STOP_RESET_S):.0f}",
    }


COLUMNS = [("seated", "Good parts seated"), ("bad_passed", "Bad parts passed"),
           ("esc_good", "Bad units passed on good parts"), ("false_rej", "False rejects"),
           ("stops", "Protective stops (good + bad parts)"), ("damage", "Damage events"),
           ("over45", "Trials > 45 N (10 ms contact)"), ("max10", "Max 10 ms contact (N)"),
           ("maxmeas", "Max measured F/T (N)"), ("cycle", "Median good cycle (s)"),
           ("uph", "Good units/h (60 s per stop)")]


def main_table(before: dict, after: dict, damage_n: float) -> list[str]:
    ctrls = [c for c in ORDER if any(k[0] == c for k in before)]
    out = ["| Controller | " + " | ".join(t for _, t in COLUMNS) + " | Good parts lost / gained (McNemar p) |",
           "|---" * (len(COLUMNS) + 2) + "|"]
    for c in ctrls:
        sb, sa = summary(ctrl_rows(before, c), damage_n), summary(ctrl_rows(after, c), damage_n)
        lost, gained, _ = pair(before, after, c)
        cells = [sb[k] if sb[k] == sa[k] else f"{sb[k]} -> {sa[k]}" for k, _ in COLUMNS]
        out.append(f"| {LETTER[c]} {c} | " + " | ".join(cells) + f" | {lost} / {gained} ({fmt_p(mcnemar(lost, gained))}) |")
    return out


def conditions(rows: dict, pred) -> list[str]:
    return list(dict.fromkeys(r["condition"] for r in rows.values() if pred(r)))


def per_condition(before: dict, after: dict, pred, what: str, count) -> list[str]:
    ctrls = [c for c in ORDER if any(k[0] == c for k in before)]
    out = [f"| Condition ({what}) | " + " | ".join(LETTER[c] for c in ctrls) + " |", "|---" * (len(ctrls) + 1) + "|"]
    for cd in conditions(before, pred):
        cells = []
        for c in ctrls:
            b = [r for k, r in before.items() if k[0] == c and k[2] == cd]
            a = [r for k, r in after.items() if k[0] == c and k[2] == cd]
            kb, ka = sum(count(r) for r in b), sum(count(r) for r in a)
            cells.append(f"{kb}" if kb == ka else f"{kb} -> {ka}")
        n = sum(1 for k in before if k[0] == ctrls[0] and k[2] == cd)
        out.append(f"| {cd} (of {n}) | " + " | ".join(cells) + " |")
    return out


def c_against(rows: dict, other: str) -> list[str]:
    out = []
    for cd in conditions(rows, good):
        keys = [k for k in rows if k[0] == "adaptive" and k[2] == cd and (other,) + k[1:] in rows]
        co = sum(ok(rows[k]) and not ok(rows[(other,) + k[1:]]) for k in keys)
        oo = sum(ok(rows[(other,) + k[1:]]) and not ok(rows[k]) for k in keys)
        reasons = Counter(rows[(other,) + k[1:]]["failure_reason"] for k in keys if not ok(rows[(other,) + k[1:]]))
        missed = Counter(rows[(other,) + k[1:]]["failure_reason"] for k in keys
                         if ok(rows[k]) and not ok(rows[(other,) + k[1:]]))
        out.append(f"| {cd} | {sum(ok(rows[k]) for k in keys)}/{len(keys)} | "
                   f"{sum(ok(rows[(other,) + k[1:]]) for k in keys)}/{len(keys)} | {co} / {oo} ({fmt_p(mcnemar(co, oo))}) | "
                   f"{fmt(missed)} | {fmt(reasons)} |")
    keys = [k for k in rows if k[0] == "adaptive" and good(rows[k]) and (other,) + k[1:] in rows]
    co = sum(ok(rows[k]) and not ok(rows[(other,) + k[1:]]) for k in keys)
    oo = sum(ok(rows[(other,) + k[1:]]) and not ok(rows[k]) for k in keys)
    out.append(f"| all good parts | {sum(ok(rows[k]) for k in keys)}/{len(keys)} | "
               f"{sum(ok(rows[(other,) + k[1:]]) for k in keys)}/{len(keys)} | {co} / {oo} ({fmt_p(mcnemar(co, oo))}) | | |")
    return out


def fmt(c: Counter) -> str:
    return ", ".join(f"{k} {v}" for k, v in c.most_common()) or "-"


def changed(before: dict, after: dict, c: str) -> list[str]:
    out = []
    for k in sorted(k for k in before if k[0] == c and k in after):
        b, a = before[k], after[k]
        if ok(b) != ok(a) or escape(b) != escape(a) or stop(b) != stop(a):
            out.append(f"| {k[1]} | {k[2]} | {k[3]} | {b['failure_reason']} | {a['failure_reason']} | "
                       f"{float(b['cycle_time_s']):.2f} -> {float(a['cycle_time_s']):.2f} | "
                       f"{f10(b):.1f} -> {f10(a):.1f} |")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    root = ap.parse_args().root
    mf = ConnectorSpec.load("microfit3_4ckt")
    fb = mf.force_budget
    lines = [f"# Tables for {root.name}", "",
             f"Generated by `python -m experiments.v02d_force_budget_tables {root}` from the per-trial rows. "
             "Each cell is before -> after (one number when unchanged), seeds 2026 and 2027 pooled, 20 trials per "
             "condition and seed. Before: insert target 30 N (b94b971). After: the connector file's current "
             f"budget, insert target {fb.insert_target_n:g} N, abort {fb.abort_n:g} N, protective stop "
             f"{fb.protective_stop_n:g} N, damage {fb.damage_n:g} N (10 ms average of the ground-truth housing "
             f"contact force); datasheet maximum mating force {mf.mating.mating_force_max_n:g} N.", "",
             "Bad units passed = failed and neither stopped nor declared failed. False rejects = seated in ground "
             "truth but declared failed. Damage events = 10 ms contact peak above the budget's damage force. "
             f"Trials > 45 N counts trials whose 10 ms contact peak exceeds {SAFETY_DAMAGE_N:g} N "
             "(SafetyConfig.damage_contact_force_n; the Micro-Fit's budget replaces it with 58 N). Median cycle "
             f"and good units per hour over good-part trials, {STOP_RESET_S:.0f} s per protective stop. "
             "Lost / gained: good-part trials that succeeded only before / only after, exact McNemar."]
    for backend in BACKENDS:
        for suite in SUITES:
            before, mb = phase(root, "before", backend, suite)
            after, ma = phase(root, "after", backend, suite)
            if not before or not after:
                continue
            lines += [f"\n## {backend}, {suite}", "", "Runs: " + "; ".join(mb + ma) + ".", ""]
            lines += main_table(before, after, fb.damage_n)
            lines += ["", "Good parts seated per condition:", ""]
            lines += per_condition(before, after, good, "good parts seated", ok)
            lines += ["", "Bad parts passed per condition:", ""]
            lines += per_condition(before, after, lambda r: not good(r), "bad parts passed", escape)
            lines += ["", "Protective stops per condition:", ""]
            lines += per_condition(before, after, lambda r: True, "protective stops", stop)
            for label, rows in (("before", before), ("after", after)):
                lines += ["", f"C against H and I, good parts, {label} the fix (failure reasons of the other "
                              "controller: where C seated and it did not / all its failures):", ""]
                lines += ["| Condition | C | other | C-only / other-only (p) | missed where C seated | "
                          "all failures |", "|---|---|---|---|---|---|"]
                for other in ("spiral_pull", "spiral_rcc_pull"):
                    lines += [f"| **{LETTER[other]} {other}** | | | | | |"] + c_against(rows, other)
            ch = changed(before, after, "adaptive")
            lines += ["", f"C's trials whose outcome changed (success, bad unit passed or protective stop): {len(ch)}",
                      ""]
            if ch:
                lines += ["| Seed | Condition | Trial | Reason before | Reason after | Cycle (s) | 10 ms contact (N) |",
                          "|---|---|---|---|---|---|---|", *ch]
    print("\n".join(lines))


if __name__ == "__main__":
    main()
