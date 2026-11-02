"""benchmark_v0.2d headline tables, from the per-trial rows and checkpoint_report's rule functions.

    python -m experiments.v02d_headline results/benchmark_v0.2d [--compare results/benchmark_v0.2c]

(a) The pre-registered headline: per machine and suite, C against the best fair baseline (D, E, F, H, I) by
    checkpoint_report.c_vs_fair, and the deliberately bad parts passed, C against H and I (the comparison that
    counts) by checkpoint_report.c_vs_fair_bad. The layout is the headline table of
    results/benchmark_v0.2c/REPORT.md.
(b) J against C and against I per machine and suite, paired (checkpoint_report.j_vs).
(c) Throughput per controller: median successful cycle, good units per hour at 0 s and 60 s per stop.
(d) With --compare: success rates per controller in both runs side by side (different seeds, not paired).

Reads only run folders <run>/<backend>_<suite>/ that hold summary.json (written after trials.csv when a run
finishes). On the latching suites the success figures are good parts only.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np

from defex.logging.metrics import STOP_RESET_S
from experiments.checkpoint_report import (
    FAIR,
    J,
    LETTER,
    c_vs_fair,
    c_vs_fair_bad,
    controllers,
    escape,
    fmt_p,
    j_vs,
    load,
    ok,
    split,
    uph,
    wilson,
)

C, H, I = "adaptive", "spiral_pull", "spiral_rcc_pull"
MACHINES = ("gantry", "arm")
SUITES = ("standard", "latching", "heldout", "latch_spread")
NAME = {"standard": "standard", "latching": "latching", "heldout": "mis-characterized vision",
        "latch_spread": "latch_spread"}
GOOD_NAME = {**NAME, "latching": "latching good parts", "latch_spread": "latch_spread good parts"}
OUTCOME = {"ahead": "C ahead", "below": "**C below**", "matches": "**baseline matches C**"}
BAD_OUTCOME = {"same": "no difference", "fewer": "C passes fewer", "more": "**C passes more**"}


def load_run(root: Path) -> dict[tuple[str, str], list[dict]]:
    """{(machine, suite): rows} for every finished run folder, gantry before arm, suites in the run order."""
    cells = {}
    for p in root.iterdir():
        if (p / "summary.json").exists() and (p / "trials.csv").exists():
            machine, _, suite = p.name.partition("_")
            cells[(machine, suite)] = load(p)

    def order(k):
        m, s = k
        return (MACHINES.index(m) if m in MACHINES else len(MACHINES), m,
                SUITES.index(s) if s in SUITES else len(SUITES), s)

    return {k: cells[k] for k in sorted(cells, key=order)}


def seed(root: Path) -> str:
    for p in sorted(root.iterdir()):
        cfg = p / "config.json"
        if (p / "summary.json").exists() and cfg.exists():
            return str(json.loads(cfg.read_text()).get("base_seed", "?"))
    return "?"


def hp(p: float) -> str:
    """fmt_p as the README writes it: '< 1e-6', '4.9e-5'."""
    return re.sub(r"e-0(\d)", r"e-\1", fmt_p(p)).replace("<1e-6", "< 1e-6")


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def upper(k: int, n: int) -> str:
    """Wilson 95% upper bound, in percent: two decimals below 1%."""
    u = 100 * wilson(k, n)[1]
    return f"{u:.2f}%" if u < 1 else f"{u:.1f}%"


def headline(cells: dict) -> list[str]:
    out = ["## (a) Pre-registered headline", "",
           "C against the best fair baseline (highest success rate among D, E, F, H, I; exact McNemar on paired "
           "trials), rule outcome by `checkpoint_report.c_vs_fair`. Baselines tied with the best are joined "
           "with /; any other fair baseline that C is not ahead of by the same rule is given in brackets with "
           "its own p.", "",
           "| Machine, suite | C | Best fair baseline | p | Rule outcome |", "|---|---|---|---|---|"]
    bad_rows, per_cell_bad = [], []
    for (m, s), rows in cells.items():
        good, bad = split(s, rows)
        if bad:
            bad_rows += [{**r, "condition": f"{m}_{s}/{r['condition']}"} for r in bad]
            if d := c_vs_fair_bad(bad):
                per_cell_bad.append((f"{m}, {s}", d))
        d = c_vs_fair(good)
        if not d:
            continue
        rate, best = d["rate"], d["best"]
        tied = [c for c in d["fair"] if rate[c] == rate[best]]
        vs = {c: c_vs_fair(good, (c,)) for c in d["fair"] if c != best}
        groups: dict[tuple[float, float], list[str]] = {}
        for c in d["fair"]:
            if c not in tied and vs[c]["outcome"] != "ahead":
                groups.setdefault((rate[c], vs[c]["p"]), []).append(c)
        base = "/".join(LETTER[c] for c in tied) + f" {pct(rate[best])}"
        if groups:
            base += " (" + ", ".join(f"{'/'.join(LETTER[c] for c in g)} {pct(r)}" for (r, _), g in groups.items()) + ")"
        ps = [(LETTER[c], vs[c]["p"]) for c in tied if c != best and vs[c]["p"] != d["p"]]
        ps += [("/".join(LETTER[c] for c in g), q) for (_, q), g in groups.items()]
        p = hp(d["p"]) + (" (" + ", ".join(f"{k}: {hp(q)}" for k, q in ps) + ")" if ps else "")
        out.append(f"| {m}, {GOOD_NAME.get(s, s)} | {pct(rate[C])} | {base} | {p} | {OUTCOME[d['outcome']]} |")
    if bad_rows:
        out += bad_parts(bad_rows, per_cell_bad)
    return out


def bad_parts(rows: list[dict], per_cell: list[tuple[str, dict]]) -> list[str]:
    """The pooled bad-part row (C against H and I, pairs kept within machine and suite), then the rule per cell."""
    machines = list(dict.fromkeys(r["condition"].split("_", 1)[0] for r in rows))
    where = "both" if set(machines) == set(MACHINES) else ", ".join(machines)
    vs = {c: d for c in (H, I) if (d := c_vs_fair_bad(rows, (c,)))}
    out = []
    if vs:
        d0 = next(iter(vs.values()))
        esc, n = d0["escapes"], d0["n"]
        ns = {n[c] for c in vs}
        others = (", ".join(f"{LETTER[c]} {esc[c]}" for c in vs) + f" of {n[next(iter(vs))]:,}" if len(ns) == 1
                  else ", ".join(f"{LETTER[c]} {esc[c]} of {n[c]:,}" for c in vs))
        pv = {hp(d["p"]) for d in vs.values()}
        p = pv.pop() if len(pv) == 1 else ", ".join(f"{LETTER[c]}: {hp(d['p'])}" for c, d in vs.items())
        oc = {d["outcome"] for d in vs.values()}
        outcome = (BAD_OUTCOME[oc.pop()] if len(oc) == 1 else
                   "; ".join(f"{LETTER[c]}: {BAD_OUTCOME[d['outcome']]}" for c, d in vs.items()))
        out.append(f"| {where}, deliberately bad parts passed | {esc[C]} of {n[C]:,} | {others} | {p} | {outcome} |")
        bounds = ", ".join(f"{LETTER[c]} <= {upper(esc[c], n[c])}" for c in (C, *vs))
        out += ["", f"Bad parts: C against {' and '.join(LETTER[c] for c in vs)}, which run the same pull test (the "
                f"pre-registered comparison that counts), pooled over machines and bad-part suites with pairs kept "
                f"within each. Wilson 95% upper bounds on the false-accept rate: {bounds}."]
    if per_cell:
        out += ["", "Bad parts per machine and suite, the rule as `checkpoint_report.c_vs_fair_bad` applies it "
                "(C against the fair baseline that passed the fewest):", "",
                "| Machine, suite | C | Fewest of " + "/".join(LETTER[c] for c in FAIR) + " | p | Rule outcome |",
                "|---|---|---|---|---|"]
        for name, d in per_cell:
            esc, n, b = d["escapes"], d["n"], d["best"]
            out.append(f"| {name} | {esc[C]} of {n[C]:,} (<= {upper(esc[C], n[C])}) | "
                       f"{LETTER[b]} {esc[b]} of {n[b]:,} | {hp(d['p'])} | {BAD_OUTCOME[d['outcome']]} |")
    return out


def j_table(cells: dict) -> list[str]:
    out = ["", "## (b) J against C and against I", ""]
    if not any(J in controllers(rows) for rows in cells.values()):
        return out + [f"No J ({J}) trials in this run."]
    out += ["Paired on the same trials, exact McNemar (`checkpoint_report.j_vs`). Seated: good parts. Bad units "
            "passed: escapes on the same trials (on standard and mis-characterized vision every trial is a good "
            "part). Bad parts passed: the deliberately bad parts of the latching suites.", "",
            "| Machine, suite | J vs | Seated, J / other | p | Bad units passed, J / other | p | "
            "Bad parts passed, J / other | p |", "|---|---|---|---|---|---|---|---|"]

    def cell(d, other):
        if not d:
            return "", ""
        return f"{d['k'][J]} / {d['k'][other]} of {d['n'][J]:,}", hp(d["p"])

    for (m, s), rows in cells.items():
        good, bad = split(s, rows)
        for other in (C, I):
            if not j_vs(good, other):
                continue
            row = [*cell(j_vs(good, other), other), *cell(j_vs(good, other, escape), other),
                   *(cell(j_vs(bad, other, escape), other) if bad else ("", ""))]
            out.append(f"| {m}, {NAME.get(s, s)} | {LETTER[other]} | " + " | ".join(row) + " |")
    return out


def throughput(cells: dict) -> list[str]:
    ctrls = controllers([r for rows in cells.values() for r in rows])
    out = ["", "## (c) Throughput", "",
           f"Good units per hour of cell time, 0 s / {STOP_RESET_S:.0f} s per protective stop; median successful "
           f"cycle in brackets. Good parts on the latching suites. From the per-trial rows (`checkpoint_report.uph`).",
           "", "| Machine, suite | " + " | ".join(LETTER[c] for c in ctrls) + " |", "|---" * (len(ctrls) + 1) + "|"]
    for (m, s), rows in cells.items():
        good, _ = split(s, rows)
        vals = []
        for c in ctrls:
            rs = [r for r in good if r["controller"] == c]
            if not rs:
                vals.append("")
                continue
            ct = [float(r["cycle_time_s"]) for r in rs if ok(r)]
            med = f"{float(np.median(ct)):.2f} s" if ct else "n/a"
            vals.append(f"{uph(rs, 0.0):,.0f} / {uph(rs, STOP_RESET_S):,.0f} ({med})")
        out.append(f"| {m}, {GOOD_NAME.get(s, s)} | " + " | ".join(vals) + " |")
    return out


def compare(cells: dict, other: dict, name: str, other_name: str, seeds: tuple[str, str]) -> list[str]:
    keys = list(cells) + [k for k in other if k not in cells]
    present = {r["controller"] for d in (cells, other) for rows in d.values() for r in rows}
    ctrls = controllers([{"controller": c} for c in present])
    out = ["", f"## (d) Success rates beside {other_name}: different seeds, not paired", "",
           f"{name} (seed {seeds[0]}) / {other_name} (seed {seeds[1]}). Different seeds, not paired: no test "
           f"across the two runs. Good parts on the latching suites; blank where a controller did not run.", "",
           "| Machine, suite | " + " | ".join(LETTER[c] for c in ctrls) + " |", "|---" * (len(ctrls) + 1) + "|"]

    def rate(d, k, c):
        if k not in d:
            return None
        rs = [r for r in split(k[1], d[k])[0] if r["controller"] == c]
        return sum(ok(r) for r in rs) / len(rs) if rs else None

    for k in keys:
        vals = []
        for c in ctrls:
            a, b = rate(cells, k, c), rate(other, k, c)
            vals.append("" if a is None and b is None else
                        f"{pct(a) if a is not None else '-'} / {pct(b) if b is not None else '-'}")
        out.append(f"| {k[0]}, {GOOD_NAME.get(k[1], k[1])} | " + " | ".join(vals) + " |")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run", type=Path)
    ap.add_argument("--compare", type=Path, default=None, help="another benchmark folder, shown beside (d)")
    args = ap.parse_args()
    cells = load_run(args.run)
    cmd = f"python -m experiments.v02d_headline {args.run}" + (f" --compare {args.compare}" if args.compare else "")
    lines = [f"# Headline for {args.run.name}", "",
             f"Generated by `{cmd}` from the per-trial rows of the finished run folders "
             f"({', '.join(f'{m}_{s}' for m, s in cells) or 'none'}).", ""]
    lines += headline(cells)
    lines += j_table(cells)
    lines += throughput(cells)
    if args.compare:
        lines += compare(cells, load_run(args.compare), args.run.name, args.compare.name,
                         (seed(args.run), seed(args.compare)))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
