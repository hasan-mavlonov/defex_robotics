"""v0.2c arm tuning of D, E and F: every table of results/v0.2c_arm_baselines, from committed files.

    python -m experiments.v02c_arm_tables > results/v0.2c_arm_baselines/tables.md

Development measurements (seeds 2026 and 2027). Numbers are recomputed from trials.csv,
events.json.gz and the tuning CSVs.
"""

from __future__ import annotations

import csv
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from defex.config import REPO_ROOT
from defex.logging.metrics import STOP_RESET_S
from experiments.checkpoint_report import DEFECTS, LETTER, escape, fmt_p, load, mcnemar, ok, stop, uph, wilson

ROOT = REPO_ROOT / "results" / "v0.2c_arm_baselines"
ALL = ["fixed", "correction", "correction_rcc", "spiral", "spiral_rcc", "adaptive", "adaptive_learned"]
DEF = ["spiral", "correction_rcc", "spiral_rcc"]
SETS = [  # (folder, title)
    ("arm_dev2026_standard5", "Arm, dev seed 2026, standard 5-condition set, 20 trials (tuning seed)"),
    ("arm_dev2026_latching", "Arm, dev seed 2026, latching suite, 20 trials (tuning seed)"),
    ("arm_dev2027_standard5", "Arm, dev seed 2027, standard 5-condition set, 20 trials"),
    ("arm_dev2027_latching", "Arm, dev seed 2027, latching suite, 20 trials"),
    ("arm_dev2027_standard20", "Arm, dev seed 2027, all 20 standard conditions, 5 trials"),
    ("gantry_rule3_standard", "Gantry, dev seed 2026, rule-3 set (noise_1mm, noise_2mm, friction_1), 20 trials"),
    ("gantry_rule3_latching", "Gantry, dev seed 2026, latching suite, 10 trials"),
]


def rel(p: Path) -> str:
    return p.relative_to(REPO_ROOT).as_posix()


def provenance(folder: Path) -> str:
    c = json.loads((folder / "config.json").read_text())
    e = c["environment"]
    return f"`{rel(folder)}`: commit {e['git_commit'][:7]}, dirty {e['git_dirty']}, seed {c['base_seed']}, backend {c['backend']}"


def cyc(rs: list[dict], q: float) -> str:
    ct = [float(r["cycle_time_s"]) for r in rs if ok(r)]
    return f"{np.percentile(ct, q):.2f}" if ct else "n/a"


def good(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r["condition"] not in DEFECTS]


def bad(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r["condition"] in DEFECTS]


def by_ctrl(rows: list[dict]) -> dict[str, list[dict]]:
    out = defaultdict(list)
    for r in rows:
        out[r["controller"]].append(r)
    return out


def pair_counts(a_rows: list[dict], b_rows: list[dict], pred=ok) -> tuple[int, int, int]:
    """(a-only, b-only, pairs) matched on (condition, trial_index)."""
    a = {(r["condition"], r["trial_index"]): pred(r) for r in a_rows}
    b = {(r["condition"], r["trial_index"]): pred(r) for r in b_rows}
    keys = [k for k in a if k in b]
    return sum(a[k] and not b[k] for k in keys), sum(b[k] and not a[k] for k in keys), len(keys)


def fails(rs: list[dict]) -> str:
    c = Counter(r["failure_reason"].replace("aborted:", "") for r in rs if not ok(r))
    return ", ".join(f"{k} {v}" for k, v in c.most_common()) or "-"


# ---------------------------------------------------------------------------------------------- diagnosis
def diagnosis() -> list[str]:
    out = ["## Diagnosis: D, E, F on the arm before any arm work (dev seed 2026)", ""]
    for name in ("arm_dev2026_standard5", "arm_dev2026_latching"):
        folder = ROOT / "before" / name
        if not (folder / "trials.csv").exists():
            continue
        rows = load(folder)
        out += [f"From {provenance(folder)}.", "",
                "| Controller | Condition | Success | Escapes | Stops | Failures | Median cycle (s) |",
                "|---|---|---|---|---|---|---|"]
        for c in DEF + ["adaptive", "adaptive_learned"]:
            rc = [r for r in rows if r["controller"] == c]
            for cond in dict.fromkeys(r["condition"] for r in rc):
                rs = [r for r in rc if r["condition"] == cond]
                out.append(f"| {LETTER[c]} {c} | {cond} | {sum(ok(r) for r in rs)}/{len(rs)} | "
                           f"{sum(escape(r) for r in rs)} | {sum(stop(r) for r in rs)} | {fails(rs)} | {cyc(rs, 50)} |")
        out.append("")
        out += event_sequences(folder)
    return out


def event_sequences(folder: Path) -> list[str]:
    ev = json.loads(gzip.open(folder / "events.json.gz", "rt").read())
    out = ["D and F event paths (contact, hole found, retries, aborts), trials per path:", "",
           "| Controller | Path | Trials |", "|---|---|---|"]
    for ctl in ("spiral", "spiral_rcc"):
        c = Counter()
        for k, e in ev.items():
            cond, cn, _ = k.split("|")
            if cn != ctl or cond in DEFECTS:
                continue
            seq = [x[1] + (":" + x[2].split(":")[0] if x[1] in ("retry", "abort") else "")
                   for x in e if x[1] in ("hole_found", "retry", "abort", "seated")]
            c[" > ".join(seq) or "-"] += 1
        for s, n in c.most_common():
            out.append(f"| {LETTER[ctl]} {ctl} | {s} | {n} |")
    return out + [""]


def jam_after_hole() -> list[str]:
    """Jam retries after a found hole, gantry against arm, before v0.2c, on the conditions both sets ran."""
    out = ["Jam retries after the hole was found, before v0.2c (noise_1mm, noise_2mm, friction_1; dev seed 2026):", "",
           "| Machine | Controller | Trials with hole found | Of which a jam retry followed |", "|---|---|---|---|"]
    for machine, name in (("gantry", "gantry_rule3_standard"), ("arm", "arm_dev2026_standard5")):
        path = ROOT / "before" / name / "events.json.gz"
        if not path.exists():
            continue
        ev = json.loads(gzip.open(path, "rt").read())
        for ctl in ("spiral", "spiral_rcc"):
            hf = jam = 0
            for k, e in ev.items():
                cond, cn, _ = k.split("|")
                if cn != ctl or cond not in ("noise_1mm", "noise_2mm", "friction_1"):
                    continue
                idx = [j for j, x in enumerate(e) if x[1] == "hole_found"]
                if idx:
                    hf += 1
                    jam += any(x[1] == "retry" and "jam" in x[2] for x in e[idx[0]:])
            out.append(f"| {machine} | {LETTER[ctl]} {ctl} | {hf} | {jam} |")
    diag = ROOT / "diagnosis"
    for f in sorted(diag.glob("*.json")) if diag.exists() else []:
        d = json.loads(f.read_text())
        out += ["", f"`{rel(f)}` (mode {d['mode']}, seed {d['seed']}, commit {d['git_commit'][:7]}, dirty {d['git_dirty']}):", ""]
        for r in d["rows"]:
            out.append("- " + ", ".join(f"{k} {v:.2f}" if isinstance(v, float) else f"{k} {v}"
                                        for k, v in r.items() if k != "events"))
    return out + [""]


# ---------------------------------------------------------------------------------------------- tuning
def tuning() -> list[str]:
    tdir = ROOT / "tuning"
    out = ["## Arm tuning (dev seed 2026, SELECTION_RULE.md)", ""]
    if not tdir.exists():
        return out + ["(not run yet)", ""]
    for ctl in DEF:
        for stage in ("coarse", "fine", "speed", "speed2", "confirm"):
            path = tdir / f"tuning_{ctl}_{stage}.csv"
            if not path.exists():
                continue
            meta = json.loads(path.with_suffix(".json").read_text())
            rows = list(csv.DictReader(path.open()))
            skip = {"setting", "n", "ok", "stops", "false_accepts", "escapes", "time_limits", "success_rate",
                    "median_cycle_s", "p95_cycle_s"}
            keys = [k for k in rows[0] if k not in skip]
            out += [f"### {LETTER[ctl]} {ctl}, {stage}: {len(rows)} settings x {len(meta['conditions'])} conditions x "
                    f"{meta['trials']} trials (commit {meta.get('git_commit', '?')[:7]}, dirty {meta.get('git_dirty')}, "
                    f"{meta.get('wall_time_s', 0) / 60:.0f} min)", "",
                    f"File: `{rel(path)}`. Top {min(5, len(rows))} by the ranking rule:", "",
                    "| Rank | " + " | ".join(keys) + " | Success | Median / p95 cycle (s) | Escapes | Stops | Time limits |",
                    "|---|" + "---|" * len(keys) + "---|---|---|---|---|"]
            for i, r in enumerate(rows[:5], 1):
                out.append(f"| {i} | " + " | ".join(r[k] for k in keys) + f" | {r['ok']}/{r['n']} | "
                           f"{float(r['median_cycle_s']):.2f} / {float(r['p95_cycle_s']):.2f} | {r['escapes']} | "
                           f"{r['stops']} | {r['time_limits']} |")
            ranks = sorted(rows, key=lambda r: -int(r["ok"]))
            out += ["", f"Spread: best {ranks[0]['ok']}/{ranks[0]['n']}, worst {ranks[-1]['ok']}/{ranks[-1]['n']}; "
                    f"settings tied with the best on success: {sum(r['ok'] == ranks[0]['ok'] for r in rows)}.", ""]
    return out


# ---------------------------------------------------------------------------------------------- before / after
def before_after(name: str, title: str) -> list[str]:
    b_dir, a_dir = ROOT / "before" / name, ROOT / "after" / name
    if not (b_dir / "trials.csv").exists() or not (a_dir / "trials.csv").exists():
        return []
    b_rows, a_rows = load(b_dir), load(a_dir)
    latching = any(r["condition"] in DEFECTS for r in b_rows)
    bb, ab = by_ctrl(good(b_rows)), by_ctrl(good(a_rows))
    out = [f"### {title}", "", f"Before: {provenance(b_dir)}. After: {provenance(a_dir)}.", ""]
    head = "good-part conditions only; " if latching else ""
    out += [f"Success ({head}Wilson 95%), escapes, stops and cycle of successes, before -> after:", "",
            "| Controller | Success before | Success after | After vs before: after-only / before-only (McNemar p) | "
            "Escapes | Stops | Time limits | Cycle p50 (s) | Cycle p95 (s) | Good units/h, 0 s / 60 s per stop |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for c in ALL:
        if c not in bb or c not in ab:
            continue
        rb, ra = bb[c], ab[c]
        kb, ka, n = sum(map(ok, rb)), sum(map(ok, ra)), len(ra)
        lb, hb = wilson(kb, len(rb))
        la, ha = wilson(ka, n)
        ao, bo, _ = pair_counts(ra, rb)
        tl = lambda rs: sum(r["failure_reason"] == "aborted:time_limit" for r in rs)  # noqa: E731
        out.append(f"| {LETTER[c]} {c} | {kb}/{len(rb)} ({100 * lb:.0f}-{100 * hb:.0f}%) | {ka}/{n} ({100 * la:.0f}-{100 * ha:.0f}%) | "
                   f"{ao} / {bo} ({fmt_p(mcnemar(ao, bo))}) | {sum(map(escape, rb))} -> {sum(map(escape, ra))} | "
                   f"{sum(map(stop, rb))} -> {sum(map(stop, ra))} | {tl(rb)} -> {tl(ra)} | {cyc(rb, 50)} -> {cyc(ra, 50)} | "
                   f"{cyc(rb, 95)} -> {cyc(ra, 95)} | {uph(rb, 0.0):.0f} / {uph(rb, STOP_RESET_S):.0f} -> "
                   f"{uph(ra, 0.0):.0f} / {uph(ra, STOP_RESET_S):.0f} |")
    if latching:
        bbad, abad = by_ctrl(bad(b_rows)), by_ctrl(bad(a_rows))
        out += ["", "Deliberately bad parts passed as good (escapes / trials, Wilson 95% upper bound), before -> after:", "",
                "| Controller | " + " | ".join(DEFECTS) + " | All four |", "|---|" + "---|" * (len(DEFECTS) + 1)]
        for c in ALL:
            if c not in abad:
                continue
            cells = []
            for d in DEFECTS + ("all",):
                rb = [r for r in bbad[c] if d == "all" or r["condition"] == d]
                ra = [r for r in abad[c] if d == "all" or r["condition"] == d]
                eb, ea = sum(map(escape, rb)), sum(map(escape, ra))
                cells.append(f"{eb} -> {ea}/{len(ra)} (<= {100 * wilson(ea, len(ra))[1]:.0f}%)")
            out.append(f"| {LETTER[c]} {c} | " + " | ".join(cells) + " |")
    out += ["", "Per condition, successes before -> after (escapes after in brackets):", "",
            "| Condition | " + " | ".join(f"{LETTER[c]} {c}" for c in ALL if c in ab) + " |",
            "|---|" + "---|" * sum(c in ab for c in ALL)]
    for cond in dict.fromkeys(r["condition"] for r in a_rows):
        cells = []
        for c in ALL:
            if c not in ab:
                continue
            rb = [r for r in b_rows if r["controller"] == c and r["condition"] == cond]
            ra = [r for r in a_rows if r["controller"] == c and r["condition"] == cond]
            cells.append(f"{sum(map(ok, rb))} -> {sum(map(ok, ra))} ({sum(map(escape, ra))})")
        out.append(f"| {cond} | " + " | ".join(cells) + " |")
    out += ["", "After: C and G against each conventional cell, paired (good-part conditions):", "",
            "| Pair | C-only / other-only (p) | G-only / other-only (p) |", "|---|---|---|"]
    for c in ("fixed", "correction", "correction_rcc", "spiral", "spiral_rcc"):
        if c not in ab:
            continue
        co, oo, _ = pair_counts(ab["adaptive"], ab[c])
        go, o2, _ = pair_counts(ab["adaptive_learned"], ab[c])
        out.append(f"| {LETTER[c]} {c} | {co} / {oo} ({fmt_p(mcnemar(co, oo))}) | {go} / {o2} ({fmt_p(mcnemar(go, o2))}) |")
    return out + [""]


def pooled_2027() -> list[str]:
    """Seed 2027 (not used for tuning), standard 5-condition set and latching good parts together."""
    names = ("arm_dev2027_standard5", "arm_dev2027_latching")
    if not all((ROOT / t / n / "trials.csv").exists() for t in ("before", "after") for n in names):
        return []
    rows = {t: [r for n in names for r in good(load(ROOT / t / n))] for t in ("before", "after")}
    bb, ab = by_ctrl(rows["before"]), by_ctrl(rows["after"])
    out = ["### Arm, dev seed 2027, standard 5-condition set and latching good parts pooled (160 trials per controller)", "",
           "| Controller | Success before -> after | After vs before (p) | Before: C-only / other-only (p) | "
           "After: C-only / other-only (p) | After: G-only / other-only (p) | Cycle p50 before -> after (s) | "
           "Good units/h, 60 s per stop, before -> after |",
           "|---|---|---|---|---|---|---|---|"]
    for c in ALL:
        rb, ra = bb[c], ab[c]
        ao, bo, _ = pair_counts(ra, rb)
        cells = []
        for ref, side, rows_c in (("adaptive", bb, rb), ("adaptive", ab, ra), ("adaptive_learned", ab, ra)):
            if c == ref:
                cells.append("-")
                continue
            r_only, o_only, _ = pair_counts(side[ref], rows_c)
            cells.append(f"{r_only} / {o_only} ({fmt_p(mcnemar(r_only, o_only))})")
        out.append(f"| {LETTER[c]} {c} | {sum(map(ok, rb))} -> {sum(map(ok, ra))} | {ao} / {bo} ({fmt_p(mcnemar(ao, bo))}) | "
                   f"{' | '.join(cells)} | {cyc(rb, 50)} -> {cyc(ra, 50)} | {uph(rb, STOP_RESET_S):.0f} -> {uph(ra, STOP_RESET_S):.0f} |")
    return out + [""]


def equivalence() -> list[str]:
    out = ["## Field identity (scripts/compare_trials.py, wall_time_s ignored)", ""]
    for path in sorted((ROOT / "equivalence").glob("*.txt")) if (ROOT / "equivalence").exists() else []:
        out += [f"From `{rel(path)}`:", "", "```", path.read_text().strip(), "```", ""]
    return out


def main() -> None:
    lines = ["# v0.2c arm tuning of D, E and F: tables", "",
             "Generated by `python -m experiments.v02c_arm_tables` from committed files under "
             "`results/v0.2c_arm_baselines/`. Development measurements in simulation (dev seeds 2026 and 2027).", ""]
    lines += diagnosis() + jam_after_hole() + tuning()
    lines += ["## Before and after", ""]
    for name, title in SETS:
        lines += before_after(name, title)
    lines += pooled_2027()
    lines += equivalence()
    print("\n".join(lines))


if __name__ == "__main__":
    main()
