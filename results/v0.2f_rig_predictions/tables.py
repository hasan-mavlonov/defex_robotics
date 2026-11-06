"""Frozen simulation predictions for the rig test (v0.2f), and the rule that compares a rig run with them.

    PYTHONPATH=. python results/v0.2f_rig_predictions/tables.py results/v0.2f_rig_predictions > results/v0.2f_rig_predictions/TABLES.md
    PYTHONPATH=. python results/v0.2f_rig_predictions/tables.py results/v0.2f_rig_predictions --rig results/hil_<name>

The second form is for later: ``results/hil_<name>/<machine>_<suite>/trials.csv`` in the same row format, with
the rig's ``success``/``protective_stop``/``declared_success`` set by TEST_PROTOCOL.md section 5. Rows are paired
on (machine, condition, controller, trial_index). The rule is fixed in PREREGISTRATION.md, "Comparison with a
rig result".
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

CTRL = [("fixed", "A"), ("adaptive", "C"), ("spiral_rcc", "F"), ("spiral_pull", "H"), ("spiral_rcc_pull", "I"),
        ("spiral_rcc_verify", "J")]
LETTER = dict(CTRL)
PROTOCOL = {"nominal", "lateral_3mm", "noise_1mm", "noise_2mm", "mf_nominal", "mf_moderate", "mf_noise_1mm",
            "mf_half_latched", "mf_broken_latch", "mf_stubbed_terminal", "mf_wrong_polarization"}
PAIRS = [("adaptive", "spiral_rcc_pull"), ("adaptive", "spiral_rcc_verify"), ("adaptive", "spiral_rcc")]
DELTA = 0.05  # agreement band for rates, absolute
RATIO_BAND = (0.8, 1.25)  # agreement band for cycle-time ratios rig / sim
BOOT = 10_000
BOOT_SEED = 20261201


def ok(r: dict) -> bool:
    return r["success"] == "True"


def stop(r: dict) -> bool:
    return r["protective_stop"] == "True"


def escape(r: dict) -> bool:
    return not ok(r) and not stop(r) and r["declared_success"] != "False"


def bad_part(r: dict) -> bool:
    return r["group"] == "bad_part"


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
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def newcombe_paired(a: int, b: int, c: int, d: int, z: float = 1.96) -> tuple[float, float, float]:
    """Difference p1 - p2 of two paired proportions and its 95% interval (Newcombe 1998, method 10).

    a: both 1; b: first 1, second 0; c: first 0, second 1; d: both 0. p1 = (a + b) / n, p2 = (a + c) / n.
    """
    n = a + b + c + d
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    p1, p2 = (a + b) / n, (a + c) / n
    l1, u1 = wilson(a + b, n, z)
    l2, u2 = wilson(a + c, n, z)
    den = (a + b) * (c + d) * (a + c) * (b + d)
    phi = (a * d - b * c) / math.sqrt(den) if den > 0 else 0.0
    t = p1 - p2
    lo = t - math.sqrt(max(0.0, (p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2))
    hi = t + math.sqrt(max(0.0, (u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2))
    return t, max(-1.0, lo), min(1.0, hi)


def classify(lo: float, hi: float, band: tuple[float, float], null: float) -> str:
    """agrees: interval inside the band; disagrees: interval excludes ``null`` and is not inside the band."""
    if band[0] <= lo and hi <= band[1]:
        return "agrees"
    if lo > null or hi < null:
        return "disagrees"
    return "inconclusive"


def quantile(x: list[float], q: float) -> float:
    return float(np.percentile(x, q)) if x else float("nan")


def ratio_ci(rig: list[float], sim: list[float], q: float, seed: int = BOOT_SEED) -> tuple[float, float, float]:
    """Ratio of the q-th percentiles rig / sim and a 95% percentile-bootstrap interval (each set resampled)."""
    if not rig or not sim:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    r, s = np.asarray(rig), np.asarray(sim)
    br = np.percentile(r[rng.integers(0, len(r), (BOOT, len(r)))], q, axis=1)
    bs = np.percentile(s[rng.integers(0, len(s), (BOOT, len(s)))], q, axis=1)
    ratio = br / bs
    return float(np.percentile(r, q) / np.percentile(s, q)), float(np.percentile(ratio, 2.5)), \
        float(np.percentile(ratio, 97.5))


def load(root: Path) -> dict[tuple[str, str, str, int], dict]:
    """Rows of the protocol conditions and controllers in ``root/<machine>_<suite>/trials.csv``."""
    rows = {}
    for f in sorted(root.glob("*_*/trials.csv")):
        machine = f.parent.name.split("_", 1)[0]
        for r in csv.DictReader(open(f)):
            if r["controller"] not in LETTER or r["condition"] not in PROTOCOL:
                continue
            r["machine"] = machine
            rows[(machine, r["condition"], r["controller"], int(r["trial_index"]))] = r
    return rows


def part(r: dict) -> str:
    if r["condition"].startswith("mf_"):
        return "Micro-Fit bad parts" if bad_part(r) else "Micro-Fit good parts"
    return "housing-only"


def pct(k: int, n: int) -> str:
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({100 * lo:.1f}-{100 * hi:.1f}%)"


def cell_rows(rows: dict) -> dict[tuple[str, str, str], list[dict]]:
    out = defaultdict(list)
    for (m, _cond, ctrl, _i), r in rows.items():
        out[(m, part(r), ctrl)].append(r)
    return out


def seeds(root: Path) -> str:
    s = sorted({str(json.loads(f.read_text()).get("base_seed")) for f in root.glob("*_*/config.json")})
    return ", ".join(s) or "unknown"


def prediction_tables(rows: dict, root: Path) -> list[str]:
    cells = cell_rows(rows)
    machines = [m for m in ("gantry", "arm") if any(k[0] == m for k in cells)]
    out = [f"# Rig-protocol conditions and controllers in {root.name}", "",
           f"From `trials.csv` under `{root}` (base seed {seeds(root)}), the TEST_PROTOCOL conditions and "
           "controllers A, C, F, H, I, J only. Rates are k/n with Wilson 95% intervals. "
           "Cycle times are of successful trials (good parts) or of all trials (bad parts: time to reject).", ""]
    for p in ("housing-only", "Micro-Fit good parts"):
        out += [f"## {p}: pooled over the protocol conditions", "",
                "| Machine | Ctrl | Success | Bad units passed | Protective stops | Cycle p50 / p95 (s) |",
                "|---|---|---|---|---|---|"]
        for m in machines:
            for ctrl, letter in CTRL:
                rs = cells.get((m, p, ctrl), [])
                if not rs:
                    continue
                n = len(rs)
                cyc = [float(r["cycle_time_s"]) for r in rs if ok(r)]
                out.append(f"| {m} | {letter} | {pct(sum(map(ok, rs)), n)} | {pct(sum(map(escape, rs)), n)} | "
                           f"{pct(sum(map(stop, rs)), n)} | {quantile(cyc, 50):.2f} / {quantile(cyc, 95):.2f} |")
        out.append("")
    out += ["## Micro-Fit deliberately bad parts, pooled over the four defects", "",
            "| Machine | Ctrl | Bad parts passed | Protective stops | Time to reject p50 / p95 (s) |",
            "|---|---|---|---|---|"]
    for m in machines:
        for ctrl, letter in CTRL:
            rs = cells.get((m, "Micro-Fit bad parts", ctrl), [])
            if rs:
                cyc = [float(r["cycle_time_s"]) for r in rs if not escape(r)]
                out.append(f"| {m} | {letter} | {pct(sum(map(escape, rs)), len(rs))} | "
                           f"{pct(sum(map(stop, rs)), len(rs))} | {quantile(cyc, 50):.2f} / {quantile(cyc, 95):.2f} |")
    out += ["", "## Per condition", "",
            "| Machine | Condition | Ctrl | Success | Bad units or bad parts passed | Stops | Cycle p50 / p95 (s) |",
            "|---|---|---|---|---|---|---|"]
    by_cond = defaultdict(list)
    for (m, cond, ctrl, _i), r in rows.items():
        by_cond[(m, cond, ctrl)].append(r)
    conds = sorted({k[1] for k in by_cond}, key=lambda c: (c.startswith("mf_"), "bad" in part(
        next(r for k, r in rows.items() if k[1] == c)), c))
    for m in machines:
        for cond in conds:
            for ctrl, letter in CTRL:
                rs = by_cond.get((m, cond, ctrl), [])
                if not rs:
                    continue
                cyc = [float(r["cycle_time_s"]) for r in rs if ok(r)]
                out.append(f"| {m} | {cond} | {letter} | {pct(sum(map(ok, rs)), len(rs))} | "
                           f"{pct(sum(map(escape, rs)), len(rs))} | {sum(map(stop, rs))} | "
                           f"{quantile(cyc, 50):.2f} / {quantile(cyc, 95):.2f} |")
    out += ["", "## Predicted differences between controllers (paired, same trials)", "",
            "C-only / other-only: trials where only C (only the other) succeeded, or only C (only the other) "
            "passed a bad unit or bad part. Exact McNemar p. The difference is C minus the other, with its "
            "Newcombe paired 95% interval.", "",
            "| Machine | Part | C vs | Metric | C / other | C-only / other-only | p | C - other (95% CI) |",
            "|---|---|---|---|---|---|---|---|"]
    for m in machines:
        for p in ("housing-only", "Micro-Fit good parts", "Micro-Fit bad parts"):
            for a, o in PAIRS:
                ra = {(r["condition"], r["trial_index"]): r for r in cells.get((m, p, a), [])}
                ro = {(r["condition"], r["trial_index"]): r for r in cells.get((m, p, o), [])}
                keys = sorted(ra.keys() & ro.keys())
                if not keys:
                    continue
                metrics = [("bad parts passed", escape)] if "bad" in p else [("success", ok), ("bad units", escape)]
                for name, f in metrics:
                    x = [(f(ra[k]), f(ro[k])) for k in keys]
                    aa = sum(u and v for u, v in x)
                    b = sum(u and not v for u, v in x)
                    c = sum(v and not u for u, v in x)
                    d = len(x) - aa - b - c
                    t, lo, hi = newcombe_paired(aa, b, c, d)
                    out.append(f"| {m} | {p} | {LETTER[o]} | {name} | {aa + b} / {aa + c} of {len(x)} | {b} / {c} | "
                               f"{mcnemar(b, c):.2g} | {100 * t:+.1f} ({100 * lo:+.1f} to {100 * hi:+.1f}) points |")
    out += ["", "## Final pose of the bad units passed on good parts", "",
            "What the rig's pose measurement has to resolve. Depth is from the socket mouth (housing-only full "
            "depth 15 mm, Micro-Fit 8 mm); the pass limits are depth >= full - 0.5 mm and abs(tilt), abs(yaw) <= 3 deg.",
            "", "| Machine | Part | Ctrl | Bad units | At full depth | Of those, tilt > 3 deg / yaw > 3 deg | "
            "max of abs(tilt), abs(yaw), range (deg) |", "|---|---|---|---|---|---|---|"]
    for m in machines:
        for p in ("housing-only", "Micro-Fit good parts"):
            full = 14.5 if p == "housing-only" else 7.5
            for ctrl, letter in CTRL:
                esc = [r for r in cells.get((m, p, ctrl), []) if escape(r)]
                if not esc:
                    continue
                fd = [r for r in esc if float(r["final_depth_mm"]) >= full]
                ti = sum(abs(float(r["final_tilt_deg"])) > 3 for r in fd)
                ya = sum(abs(float(r["final_yaw_deg"])) > 3 for r in fd)
                ang = [max(abs(float(r["final_tilt_deg"])), abs(float(r["final_yaw_deg"]))) for r in fd]
                rng = f"{min(ang):.2f}-{max(ang):.2f}" if ang else "-"
                out.append(f"| {m} | {p} | {letter} | {len(esc)} | {len(fd)} | {ti} / {ya} | {rng} |")
    return out


def compare_tables(sim: dict, rig: dict) -> list[str]:
    """The pre-registered sim-against-rig comparison (PREREGISTRATION.md, "Comparison with a rig result")."""
    keys = sorted(sim.keys() & rig.keys())
    groups = defaultdict(list)
    for k in keys:
        groups[(k[0], part(sim[k]), k[2])].append(k)
    out = ["# Rig against the frozen predictions", "",
           f"Paired on (machine, condition, controller, trial index): {len(keys)} pairs. Difference = rig - sim, "
           f"Newcombe paired 95% interval. agrees: inside +/-{100 * DELTA:.0f} points (ratios: inside "
           f"{RATIO_BAND[0]}-{RATIO_BAND[1]}); disagrees: excludes 0 (ratios: 1) and not inside the band; "
           "else inconclusive.", "",
           "| Machine | Part | Ctrl | Metric | Rig / sim | Rig - sim or rig / sim (95% CI) | Class |",
           "|---|---|---|---|---|---|---|"]
    order = {c: i for i, (c, _) in enumerate(CTRL)}
    for (m, p, ctrl), ks in sorted(groups.items(), key=lambda g: (g[0][0] != "gantry", g[0][1], order.get(g[0][2], 99))):
        metrics = [("bad parts passed", escape), ("protective stops", stop)] if "bad" in p else \
            [("success", ok), ("bad units", escape), ("protective stops", stop)]
        for name, f in metrics:
            x = [(f(rig[k]), f(sim[k])) for k in ks]
            a = sum(u and v for u, v in x)
            b = sum(u and not v for u, v in x)
            c = sum(v and not u for u, v in x)
            t, lo, hi = newcombe_paired(a, b, c, len(x) - a - b - c)
            out.append(f"| {m} | {p} | {LETTER.get(ctrl, ctrl)} | {name} | {a + b} / {a + c} of {len(x)} | "
                       f"{100 * t:+.1f} ({100 * lo:+.1f} to {100 * hi:+.1f}) points | "
                       f"{classify(lo, hi, (-DELTA, DELTA), 0.0)} |")
        if "bad" not in p:
            rc = [float(rig[k]["cycle_time_s"]) for k in ks if ok(rig[k])]
            sc = [float(sim[k]["cycle_time_s"]) for k in ks if ok(sim[k])]
            for q in (50, 95):
                t, lo, hi = ratio_ci(rc, sc, q)
                out.append(f"| {m} | {p} | {LETTER.get(ctrl, ctrl)} | cycle p{q} | {quantile(rc, q):.2f} / "
                           f"{quantile(sc, q):.2f} s | {t:.2f} ({lo:.2f} to {hi:.2f}) | "
                           f"{classify(lo, hi, RATIO_BAND, 1.0)} |")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--rig", type=Path, default=None)
    a = ap.parse_args()
    sim = load(a.root)
    lines = prediction_tables(sim, a.root) if a.rig is None else compare_tables(sim, load(a.rig))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
