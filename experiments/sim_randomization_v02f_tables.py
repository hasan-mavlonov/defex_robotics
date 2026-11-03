"""Tables and pre-registered verdicts for results/sim_randomization_v0.2f.

    python -m experiments.sim_randomization_v02f_tables results/sim_randomization_v0.2f
    python -m experiments.sim_randomization_v02f_tables --references results/benchmark_v0.2e

The rules are in results/sim_randomization_v0.2f/PREREGISTRATION.md; this module applies
them and nothing else. ``--references`` prints the reference classes from a benchmark
folder (``<machine>_<suite>/trials.csv``) on the same conditions.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

LETTER = {"adaptive": "C", "spiral_rcc": "F", "spiral_pull": "H", "spiral_rcc_pull": "I", "spiral_rcc_verify": "J",
          "adaptive_learned": "G"}
CODE = {v: k for k, v in LETTER.items()}
MACHINES = ("gantry", "arm")

# (group, [(suite, condition)]) fixed in the pre-registration.
GROUPS = {
    "c_favourable": [("standard", "noise_1mm"), ("standard", "noise_2mm"), ("standard", "generalization_combined")],
    "neutral": [("standard", "nominal"), ("standard", "lateral_3mm"), ("standard", "friction_1")],
    "c_unfavourable": [("heldout", "heldout_worst_case"), ("heldout", "heldout_handeye_bias_1.5mm")],
    "latching_good": [("latching", "mf_noise_1mm")],
}
BAD_PARTS = [("latching", "mf_half_latched"), ("latching", "mf_broken_latch"), ("latching", "mf_stubbed_terminal")]
ALL_GOOD = "all_good_parts"  # union of GROUPS; used for bad units only
# (X, Y): X against Y. Primary: C against F, H, I. Secondary: J and G against C.
PRIMARY = [("C", "F"), ("C", "H"), ("C", "I")]
SECONDARY = [("J", "C"), ("G", "C")]
BAD_PART_PAIRS = [("C", "H"), ("C", "I"), ("J", "C"), ("G", "C")]
ALPHA = 0.05
BENCHMARK = Path(__file__).resolve().parents[1] / "results" / "benchmark_v0.2e"
MIN_HOLD = 10  # of the randomized variants (12): at most 2 may fail
LOW_POWER = 0.2  # chance that trial noise alone fails a directional reference: above it, "not resolved"


def mcnemar(b: int, c: int) -> float:
    n = b + c
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def wilson_upper(k: int, n: int, z: float = 1.96) -> float:
    if n == 0:
        return float("nan")
    p = k / n
    d = 1 + z * z / n
    return min(1.0, (p + z * z / (2 * n) + z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d)


def _b(x: str) -> bool:
    return x == "True"


def ok(r: dict) -> bool:
    return _b(r["success"])


def escape(r: dict) -> bool:
    return not ok(r) and not _b(r["protective_stop"]) and r["declared_success"] != "False"


METRICS = {"success": ok, "bad_units": escape}


def better(metric: str, x: dict, y: dict) -> bool:
    """X did better than Y on this paired trial."""
    if metric == "success":
        return ok(x) and not ok(y)
    return escape(y) and not escape(x)  # bad units: fewer is better


def classify(b: int, c: int) -> str:
    """'better' / 'worse' (X against Y) with exact McNemar p < ALPHA, else 'n.s.'."""
    if mcnemar(b, c) < ALPHA:
        return "better" if b > c else "worse"
    return "n.s."


def paired(rows: dict, conds: list[tuple[str, str]], x: str, y: str, metric: str, variant=None):
    """(b, c, n, count_x, count_y) for X against Y on the given conditions (and variant)."""
    b = c = n = cx = cy = 0
    f = METRICS[metric]
    for key, rx in rows.items():
        v, ctrl, cond, i = key
        if ctrl != CODE[x] or (variant is not None and v != variant) or not any(cond == cc for _, cc in conds):
            continue
        ry = rows.get((v, CODE[y], cond, i))
        if ry is None:
            continue
        n += 1
        b += better(metric, rx, ry)
        c += better(metric, ry, rx)
        cx += f(rx)
        cy += f(ry)
    return b, c, n, cx, cy


def scenario_sign_test(rows: dict, conds, x: str, y: str, metric: str, variants: list[int]):
    """Pooled over variants with the scenario (condition, trial) as the unit: per scenario the
    number of variants where X did better minus where Y did better; exact sign test over the
    scenarios where that is not zero. Returns (scenarios X ahead, scenarios Y ahead, p)."""
    s: dict[tuple, int] = defaultdict(int)
    vs = set(variants)
    for (v, ctrl, cond, i), rx in rows.items():
        if v not in vs or ctrl != CODE[x] or not any(cond == cc for _, cc in conds):
            continue
        ry = rows.get((v, CODE[y], cond, i))
        if ry is None:
            continue
        s[(cond, i)] += int(better(metric, rx, ry)) - int(better(metric, ry, rx))
    up = sum(1 for d in s.values() if d > 0)
    dn = sum(1 for d in s.values() if d < 0)
    return up, dn, mcnemar(up, dn)


def holds(reference: str, b: int, c: int) -> bool:
    """A variant keeps the reference: same sign for a directional reference (a tie does not
    keep it), no significant difference for an 'n.s.' reference."""
    if reference == "better":
        return b > c
    if reference == "worse":
        return b < c
    return classify(b, c) == "n.s."


def pooled_class(up: int, dn: int) -> str:
    return classify(up, dn)


def pooled_ok(reference: str, pooled: str) -> bool:
    """Directional reference: the pooled test must not give the opposite class (it need not be
    significant: the direction itself was established by the benchmark). 'n.s.' reference: the
    pooled test must give 'n.s.' too."""
    if reference == "n.s.":
        return pooled == "n.s."
    return pooled != {"better": "worse", "worse": "better"}[reference]


def load_run(path: Path) -> dict:
    rows = {}
    with open(path / "trials.csv") as fh:
        for r in csv.DictReader(fh):
            rows[(int(r["variant"]), r["controller"], r["condition"], int(r["trial_index"]))] = r
    return rows


def load_benchmark(root: Path, machine: str) -> dict:
    """A benchmark's rows for one machine as variant 0, keyed like load_run."""
    rows = {}
    for suite in ("standard", "heldout", "latching"):
        p = root / f"{machine}_{suite}" / "trials.csv"
        if not p.exists():
            continue
        with open(p) as fh:
            for r in csv.DictReader(fh):
                rows[(0, r["controller"], r["condition"], int(r["trial_index"]))] = r
    return rows


def group_conds(group: str) -> list[tuple[str, str]]:
    if group == ALL_GOOD:
        return [c for g in GROUPS.values() for c in g]
    if group == "bad_parts":
        return BAD_PARTS
    return GROUPS[group]


def comparisons():
    """Every pre-registered comparison: (group, metric, X, Y, tier)."""
    out = []
    for g in GROUPS:
        for metric in ("success", "bad_units"):
            out += [(g, metric, x, y, "primary") for x, y in PRIMARY]
            out += [(g, metric, x, y, "secondary") for x, y in SECONDARY]
    out += [(ALL_GOOD, "bad_units", x, y, "primary") for x, y in PRIMARY]
    out += [(ALL_GOOD, "bad_units", x, y, "secondary") for x, y in SECONDARY]
    out += [("bad_parts", "bad_units", x, y, "primary" if x == "C" else "secondary") for x, y in BAD_PART_PAIRS]
    return out


def references(bench: Path) -> dict:
    """{(machine, group, metric, X, Y): (class, b, c, n, count_x, count_y, p)} from a benchmark."""
    out = {}
    for m in MACHINES:
        rows = load_benchmark(bench, m)
        for g, metric, x, y, _ in comparisons():
            b, c, n, cx, cy = paired(rows, group_conds(g), x, y, metric, 0)
            out[(m, g, metric, x, y)] = (classify(b, c), b, c, n, cx, cy, mcnemar(b, c))
    return out


def _p(p: float) -> str:
    s = f"{p:.2g}"
    return s + " *" if 0.01 <= p < 0.05 else s


def p_direction(pb: float, pc: float, n: int, ref: str) -> float:
    """P(X-better > Y-better) ('better') or P(<) ('worse') on n paired trials, each X-better with
    probability pb and Y-better with pc (a trinomial)."""
    tot = 0.0
    q = pc / (1 - pb) if pb < 1 else 0.0
    for b in range(n + 1):
        pB = math.comb(n, b) * pb**b * (1 - pb) ** (n - b)
        m = n - b
        cs = range(0, min(b, m + 1)) if ref == "better" else range(b + 1, m + 1)
        tot += pB * sum(math.comb(m, c) * q**c * (1 - q) ** (m - c) for c in cs)
    return tot


def p_verdict_fails(p_hold: float, k: int = 12, need: int = MIN_HOLD) -> float:
    """P(fewer than ``need`` of ``k`` independent variants hold) when each holds with p_hold."""
    need = min(need, k)
    return sum(math.comb(k, f) * (1 - p_hold) ** f * p_hold ** (k - f) for f in range(k - need + 1, k + 1))


def print_power(bench: Path, trials: dict[str, int], k: int = 12) -> None:
    """Chance that each directional reference fails the per-variant rule from trial noise alone,
    if every variant had the benchmark's per-trial rates. ``trials``: per-condition trials per group,
    keyed "group" (both machines) or "machine.group" (that machine, overriding)."""
    print(f"| Machine | Group | Metric | X vs Y | Reference | Benchmark X-better / Y-better rate | n per variant | "
          f"P(variant holds) | P(fewer than {MIN_HOLD} of {k} hold) |")
    print("|---|---|---|---|---|---|---|---|---|")
    for (m, g, metric, x, y), (cls, b, c, n, cx, cy, p) in references(bench).items():
        if cls == "n.s.":
            continue
        t = {gg: trials.get(f"{m}.{gg}", trials.get(gg, 0)) for gg in GROUPS}
        nn = sum(t[gg] * len(GROUPS[gg]) for gg in GROUPS) if g == ALL_GOOD else t[g] * len(group_conds(g))
        ph = p_direction(b / n, c / n, nn, cls)
        flag = " (low power)" if p_verdict_fails(ph, k) > 0.2 else ""
        print(f"| {m} | {g} | {metric} | {x} vs {y} | {cls} | {b / n:.3f} / {c / n:.3f} | {nn} | {ph:.3f} | "
              f"{p_verdict_fails(ph, k):.3f}{flag} |")


def print_references(bench: Path) -> None:
    print(f"# Reference classes from {bench} (same conditions, exact McNemar)\n")
    print("| Machine | Group | Metric | X vs Y | n | X / Y count | X-better / Y-better | p | Reference |")
    print("|---|---|---|---|---|---|---|---|---|")
    for (m, g, metric, x, y), (cls, b, c, n, cx, cy, p) in references(bench).items():
        print(f"| {m} | {g} | {metric} | {x} vs {y} | {n} | {cx} / {cy} | {b} / {c} | {_p(p)} | {cls} |")


def verdicts(root: Path, bench: Path) -> list[dict]:
    refs = references(bench)
    out = []
    for m in MACHINES:
        if not (root / m / "trials.csv").exists():
            continue
        rows = load_run(root / m)
        variants = sorted({k[0] for k in rows})
        randomized = [v for v in variants if v != 0]
        for g, metric, x, y, tier in comparisons():
            conds = group_conds(g)
            ref = refs[(m, g, metric, x, y)][0]
            per = []
            for v in variants:
                b, c, n, cx, cy = paired(rows, conds, x, y, metric, v)
                per.append({"variant": v, "b": b, "c": c, "n": n, "cx": cx, "cy": cy, "p": mcnemar(b, c),
                            "class": classify(b, c), "holds": holds(ref, b, c)})
            v0 = next((p for p in per if p["variant"] == 0), None)
            rnd = [p for p in per if p["variant"] != 0]
            n_hold = sum(p["holds"] for p in rnd)
            opposite = {"better": "worse", "worse": "better"}.get(ref)
            reversals = [p["variant"] for p in rnd if opposite and p["class"] == opposite] if opposite else \
                [p["variant"] for p in rnd if p["class"] != "n.s."]
            n_conf = sum(1 for p in rnd if opposite and p["class"] == ref)
            up, dn, pp = scenario_sign_test(rows, conds, x, y, metric, randomized)
            pcls = pooled_class(up, dn)
            verdict = "holds" if (n_hold >= min(MIN_HOLD, len(rnd)) and pooled_ok(ref, pcls)) else "does not hold"
            rcls, rb, rc, rn = refs[(m, g, metric, x, y)][:4]
            p_fail = None
            if opposite and v0 is not None and rn:
                p_fail = p_verdict_fails(p_direction(rb / rn, rc / rn, v0["n"], ref), len(rnd))
                if verdict == "does not hold" and p_fail > LOW_POWER:
                    verdict = "not resolved (low power)"
            out.append({"machine": m, "group": g, "metric": metric, "x": x, "y": y, "tier": tier, "reference": ref,
                        "variant0": v0, "per_variant": rnd, "n_hold": n_hold, "n_randomized": len(rnd),
                        "departures": reversals, "pooled": (up, dn, pp, pcls), "verdict": verdict,
                        "n_confirmed": n_conf, "p_noise_fail": p_fail,
                        "v0_reproduces": v0 is not None and holds(ref, v0["b"], v0["c"])})
    return out


def zero_check(root: Path) -> list[str]:
    """Bad units and bad parts passed per controller, per variant (counts, Wilson upper bound)."""
    lines = ["| Machine | Controller | Good-part trials | Bad units (all variants) | Wilson 95% upper | "
             "Variants with any | Bad parts passed / trials | Wilson 95% upper | Variants with any |",
             "|---|---|---|---|---|---|---|---|---|"]
    good = {c for _, c in group_conds(ALL_GOOD)}
    bad = {c for _, c in BAD_PARTS}
    for m in MACHINES:
        if not (root / m / "trials.csv").exists():
            continue
        rows = load_run(root / m)
        for code, L in LETTER.items():
            g = [(k[0], r) for k, r in rows.items() if k[1] == code and k[2] in good]
            bp = [(k[0], r) for k, r in rows.items() if k[1] == code and k[2] in bad]
            if not g and not bp:
                continue
            eg = [v for v, r in g if escape(r)]
            eb = [v for v, r in bp if escape(r)]
            lines.append(f"| {m} | {L} | {len(g)} | {len(eg)} | {100 * wilson_upper(len(eg), len(g)):.2f}% | "
                         f"{len(set(eg))} | {len(eb)} / {len(bp)} | {100 * wilson_upper(len(eb), len(bp)):.2f}% | "
                         f"{len(set(eb))} |")
    return lines


def listed_escapes(root: Path) -> list[str]:
    """Rules 6 and 7: every bad unit C or G passes on good parts, and every bad part C, G, H, I or J passes."""
    lines = ["| Machine | Variant | Controller | Condition | Trial | Depth mm | Lateral mm | Tilt deg | Yaw deg | "
             "Failure | gt_seated | declared |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    good = {c for _, c in group_conds(ALL_GOOD)}
    bad = {c for _, c in BAD_PARTS}
    n = 0
    for m in MACHINES:
        if not (root / m / "trials.csv").exists():
            continue
        for (v, ctrl, cond, i), r in sorted(load_run(root / m).items()):
            if not escape(r):
                continue
            if (cond in good and LETTER.get(ctrl) in ("C", "G")) or \
                    (cond in bad and LETTER.get(ctrl) in ("C", "G", "H", "I", "J")):
                n += 1
                lines.append(f"| {m} | {v} | {LETTER[ctrl]} | {cond} | {i} | {float(r['final_depth_mm']):.2f} | "
                             f"{float(r['final_lateral_mm']):.2f} | {float(r['final_tilt_deg']):.2f} | "
                             f"{float(r['final_yaw_deg']):.2f} | {r['failure_reason']} | {r['gt_seated']} | "
                             f"{r['declared_success']} |")
    return lines if n else ["None."]


def control_check(root: Path) -> list[str]:
    """F's bad parts passed per variant (positive control) and every controller's success on
    `nominal` per variant (flag only; no variant is excluded)."""
    bad = [c for _, c in BAD_PARTS]
    lines = ["| Machine | Variant | " + " | ".join(f"F passed `{c}`" for c in bad) +
             " | lowest `nominal` success over controllers | flag |",
             "|---|---|" + "---|" * len(bad) + "---|---|"]
    for m in MACHINES:
        if not (root / m / "trials.csv").exists():
            continue
        rows = load_run(root / m)
        for v in sorted({k[0] for k in rows}):
            cells, flags = [], []
            for c in bad:
                f = [r for k, r in rows.items() if k[0] == v and k[1] == "spiral_rcc" and k[2] == c]
                cells.append(f"{sum(escape(r) for r in f)} / {len(f)}")
                if f and not any(escape(r) for r in f):
                    flags.append(f"F passed no `{c}`")
            nom = defaultdict(list)
            for k, r in rows.items():
                if k[0] == v and k[2] == "nominal":
                    nom[k[1]].append(ok(r))
            mn = min((sum(x) / len(x) for x in nom.values()), default=float("nan"))
            if mn < 0.9:
                flags.append("a controller under 90% on `nominal`")
            lines.append(f"| {m} | {v} | " + " | ".join(cells) + f" | {100 * mn:.0f}% | {'; '.join(flags) or '-'} |")
    return lines


def main(paths: list[Path] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", type=Path, nargs="?")
    ap.add_argument("--references", type=Path, default=None)
    ap.add_argument("--benchmark", type=Path, default=BENCHMARK)
    ap.add_argument("--power", type=str, default="",
                    help="[machine.]group:trials,... (with --references): noise-only failure chance")
    args = ap.parse_args(None if paths is None else [str(p) for p in paths])
    if args.references is not None:
        if args.power:
            print_power(args.references, {g: int(n) for g, n in (t.split(":") for t in args.power.split(","))})
        else:
            print_references(args.references)
        return
    root = args.root
    vs = verdicts(root, args.benchmark)
    print(f"# Simulator randomization v0.2f: tables for {root}\n")
    print(f"Reference classes from {args.benchmark} on the same conditions. 'holds' = same sign "
          f"(directional reference) or no significant difference ('n.s.' reference) in at least {MIN_HOLD} of the "
          "randomized variants AND the pooled scenario sign test over the randomized variants is not the opposite "
          "class (directional reference) or is 'n.s.' ('n.s.' reference). * = 0.01 <= p < 0.05.\n")
    print("## Verdicts\n")
    print("| Tier | Machine | Group | Metric | X vs Y | Reference | Variant 0: X / Y, X-better / Y-better, p | "
          "Variants holding (of which p < 0.05) | Departing variants | Pooled X / Y scenarios, p | "
          "P(noise alone fails) | Verdict |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for t in ("primary", "secondary"):
        for d in vs:
            if d["tier"] != t:
                continue
            v0 = d["variant0"]
            v0s = f"{v0['cx']} / {v0['cy']} of {v0['n']}, {v0['b']} / {v0['c']}, {_p(v0['p'])}" if v0 else "-"
            if v0 and not d["v0_reproduces"]:
                v0s += " (not reproduced)"
            up, dn, pp, pc = d["pooled"]
            dep = ",".join(map(str, d["departures"])) or "none"
            conf = d["n_confirmed"] if d["reference"] != "n.s." else "-"
            print(f"| {t} | {d['machine']} | {d['group']} | {d['metric']} | {d['x']} vs {d['y']} | {d['reference']} | "
                  f"{v0s} | {d['n_hold']} / {d['n_randomized']} ({conf}) | {dep} | "
                  f"{up} / {dn}, {_p(pp)} ({pc}) | "
                  f"{'-' if d['p_noise_fail'] is None else format(d['p_noise_fail'], '.2f')} | {d['verdict']} |")
    print("\n## Per variant (X / Y count of n, X-better / Y-better, p)\n")
    for d in vs:
        cells = "; ".join(f"{p['variant']}: {p['cx']}/{p['cy']} of {p['n']}, {p['b']}/{p['c']}"
                          f"{'' if p['holds'] else ' x'}" for p in d["per_variant"])
        print(f"- {d['machine']} {d['group']} {d['metric']} {d['x']} vs {d['y']} (ref {d['reference']}): {cells}")
    print("\n## Bad units and bad parts passed, all variants\n")
    print("\n".join(zero_check(root)))
    print("\n## Every bad unit C or G passed, every bad part C, G, H, I or J passed\n")
    print("\n".join(listed_escapes(root)))
    print("\n## Controls (flag only)\n")
    print("\n".join(control_check(root)))


if __name__ == "__main__":
    main()
