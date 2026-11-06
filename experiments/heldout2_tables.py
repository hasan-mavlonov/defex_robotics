"""heldout2 (v0.2f) tables: the pre-registered rules per machine and family, and per machine on the whole suite.

    python -m experiments.heldout2_tables results/heldout2_v0.2f > results/heldout2_v0.2f/HELDOUT2_TABLES.md

Reads <run>/<machine>_heldout2/trials.csv. The rules are checkpoint_report's (C against the best fair baseline,
G against C, J against C and I) and v02c_paired's (bad units on good-part trials, C against H and I), applied to
each family's trials and to the whole suite. Every trial in heldout2 is a good part.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import numpy as np

from defex.logging.metrics import STOP_RESET_S
from defex.tasks.conditions import HELDOUT2_FAMILIES, heldout2_conditions
from experiments.checkpoint_report import (
    LETTER,
    controllers,
    decisions,
    escape,
    fmt_p,
    j_decisions,
    load,
    mcnemar,
    ok,
    paired,
    stop,
    success_table,
    uph,
    wilson,
)

FAMILY = {c.name: c.group for c in heldout2_conditions()}


def cells(run: Path) -> list[tuple[str, str, list[dict]]]:
    """(machine, cell name, rows): per machine the whole suite, then each family in the pre-registered order."""
    out = []
    for machine in ("gantry", "arm"):
        folder = run / f"{machine}_heldout2"
        if not (folder / "trials.csv").exists():
            continue
        rows = load(folder)
        out.append((machine, "all families", rows))
        by = defaultdict(list)
        for r in rows:
            by[FAMILY[r["condition"]]].append(r)
        out += [(machine, fam, by[fam]) for fam in HELDOUT2_FAMILIES if by[fam]]
    return out


def bad_unit_lines(name: str, rows: list[dict]) -> list[str]:
    out = []
    n_c = sum(r["controller"] == "adaptive" for r in rows)
    e_c = sum(escape(r) for r in rows if r["controller"] == "adaptive")
    for other in ("spiral_pull", "spiral_rcc_pull"):
        if other not in controllers(rows):
            continue
        e_o = sum(escape(r) for r in rows if r["controller"] == other)
        co, oo, m = paired(rows, "adaptive", other, escape)
        p = mcnemar(co, oo)
        verdict = (f"C passes fewer than {LETTER[other]}" if e_c < e_o and p < 0.05 else
                   f"C passes more than {LETTER[other]}" if e_c > e_o and p < 0.05 else "no significant difference")
        out.append(f"| {name} | C vs {LETTER[other]} | {e_c}/{n_c} (<= {100 * wilson(e_c, n_c)[1]:.1f}%) vs "
                   f"{e_o}/{m} | {co} / {oo} | {fmt_p(p)} | {verdict} |")
    return out


def throughput_lines(name: str, rows: list[dict]) -> list[str]:
    out = []
    for c in controllers(rows):
        rs = [r for r in rows if r["controller"] == c]
        ct = [float(r["cycle_time_s"]) for r in rs if ok(r)]
        p50, p95 = (np.percentile(ct, 50), np.percentile(ct, 95)) if ct else (float("nan"), float("nan"))
        out.append(f"| {name} | {LETTER[c]} | {100 * sum(ok(r) for r in rs) / len(rs):.1f}% | {p50:.2f} | {p95:.2f} | "
                   f"{sum(stop(r) for r in rs)} | {sum(escape(r) for r in rs)} | {uph(rs, 0.0):.0f} / "
                   f"{uph(rs, STOP_RESET_S):.0f} |")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run", type=Path)
    run = ap.parse_args().run
    cs = cells(run)
    rule_head = ["| Machine, cell | Comparison | Success | Discordant pairs | McNemar p | Rule outcome |",
                 "|---|---|---|---|---|---|"]
    lines = [f"# heldout2 tables: {run.name}", "",
             "From the per-trial rows. Cells: per machine, the whole suite and each family (two levels pooled). "
             "Every heldout2 trial is a good part.", "",
             "## (a) C against the best fair baseline (D, E, F, H, I), and G against C", ""] + rule_head
    for machine, cell, rows in cs:
        lines += decisions(f"{machine}, {cell}", rows)
    lines += ["", "## (b) Bad units passed on good-part trials, C against H and I", "",
              "| Machine, cell | Comparison | Bad units, C vs other | C-only / other-only | McNemar p | Outcome |",
              "|---|---|---|---|---|---|"]
    for machine, cell, rows in cs:
        lines += bad_unit_lines(f"{machine}, {cell}", rows)
    lines += ["", "## (c) J against C and against I", ""] + rule_head
    for machine, cell, rows in cs:
        lines += j_decisions(f"{machine}, {cell}", rows)
    lines += ["", f"## (d) Throughput: success, cycle p50 / p95 of successes (s), protective stops, bad units, "
              f"good units per hour (0 s / {STOP_RESET_S:.0f} s per stop)", "",
              "| Machine, cell | Controller | Success | p50 | p95 | Stops | Bad units | Good units/h |",
              "|---|---|---|---|---|---|---|---|"]
    for machine, cell, rows in cs:
        lines += throughput_lines(f"{machine}, {cell}", rows)
    lines += ["", "## (e) Per-condition success table per machine"]
    for machine, cell, rows in cs:
        if cell != "all families":
            continue
        for cond in [c.name for c in heldout2_conditions()]:
            sub = [r for r in rows if r["condition"] == cond]
            if sub:
                lines += success_table(sub, f"### {machine}, {cond}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
