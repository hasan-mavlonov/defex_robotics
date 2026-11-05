"""v0.2f evidence pack: where C's remaining edge comes from, from committed benchmark files only.

    python -m experiments.v02f_evidence --out results/v0.2f_evidence

Reads results/benchmark_v0.2d (seed 20261123), results/benchmark_v0.2d_rep (seed 20261124)
and results/benchmark_v0.2e (seed 20261130): trials.csv, config.json and events.json.gz of
the eight runs in each. Runs no simulation. Writes these tables:

- PERCOND.md        per condition and seed: seated counts, discordant pairs (part 1)
- CONCENTRATION.md  where C's wins and losses concentrate, and what the other cell did (part 1)
- BAD_UNITS.md      every bad unit on good-part trials, with the checks it failed (part 2)
- bad_units.csv     every declared_success=True, gt_seated=False row, bad parts included (part 2)
- TOLERANCE.md      can gt_seated be recomputed from the logged pose columns? (part 3)
- PHASES.md         time per phase from events.json.gz, p95/median, C's slow trials (part 4)
- SEEDS.md          the same comparisons on each seed, and which hold on all three (part 5)
- CHECKPOINT_TABLE.md  the per-controller table of CHECKPOINT_REPORT.md (seed 20261130)
- KEY_NUMBERS.md    every number quoted in REPORT.md and CHECKPOINT_REPORT.md

Per-condition breakdowns and anything about the 3 deg tolerance were chosen after the
benchmark results were seen: they are post hoc. p-values are exact McNemar, per seed, never
pooled across seeds (v0.2d and v0.2e ran different code), and never corrected.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from experiments.checkpoint_report import LETTER, mcnemar, uph
from defex.logging.metrics import STOP_RESET_S

RUNS = {
    "20261123": ("results/benchmark_v0.2d", "v0.2d code 42df5c8"),
    "20261124": ("results/benchmark_v0.2d_rep", "v0.2d code 42df5c8"),
    "20261130": ("results/benchmark_v0.2e", "v0.2e code ddd0d34"),
}
SEEDS = tuple(RUNS)
MACHINES = ("gantry", "arm")
SUITES = ("standard", "latching", "heldout", "latch_spread")
ORDER10 = ("fixed", "correction", "spiral", "correction_rcc", "spiral_rcc", "spiral_pull", "spiral_rcc_pull",
           "adaptive", "adaptive_learned", "spiral_rcc_verify")
C, G, I, F, H, J, D = ("adaptive", "adaptive_learned", "spiral_rcc_pull", "spiral_rcc", "spiral_pull",
                       "spiral_rcc_verify", "spiral")
VS_C = (I, F, H, J)  # C against each of these, and G against C
PHASE_CTRLS = (C, F, H, I, J)
NOISY = ("noise_1mm", "noise_2mm", "generalization_combined")
BUCKETS = ("approach", "align", "first_insert", "retry", "verify", "reinsert_after_verify")
ANGLE_BINS = ((3.0, 3.5), (3.5, 4.0), (4.0, 5.0), (5.0, 90.0))


def L(c: str) -> str:
    return LETTER[c]


def fp(p: float) -> str:
    return "<1e-6" if p < 1e-6 else f"{p:.2g}"


# ------------------------------------------------------------------------------------------
# Loading
# ------------------------------------------------------------------------------------------


def connector_specs(repo: Path) -> dict[str, dict]:
    out = {}
    for f in sorted((repo / "assets" / "connectors").glob("*.json")):
        spec = json.loads(f.read_text())
        out[spec["name"]] = spec["socket"]
    return out


class Run:
    """One run folder: rows, per-condition scoring parameters, and as-run tolerances."""

    def __init__(self, folder: Path, sockets: dict[str, dict]):
        self.folder = folder
        cfg = json.loads((folder / "config.json").read_text())
        self.crit = cfg["success_criteria"]
        self.commit = cfg["environment"]["git_commit"]
        self.dirty = cfg["environment"]["git_dirty"]
        self.base_seed = str(cfg["base_seed"])
        self.cond = {}
        self.cond_order = []
        for c in cfg["conditions"]:
            sock = sockets[c["connector"]]
            clearance = c["clearance_mm"] if c["clearance_mm"] is not None else sock["clearance_mm"]
            self.cond[c["name"]] = {
                "defect": c["defect"],
                "connector": c["connector"],
                "depth_mm": sock["depth_mm"],
                "lat_limit_mm": clearance + self.crit["lateral_margin_mm"],
            }
            self.cond_order.append(c["name"])
        with (folder / "trials.csv").open() as fh:
            self.rows = list(csv.DictReader(fh))
        self.by = {(r["condition"], r["controller"], r["trial_index"]): r for r in self.rows}
        self.ctrl_rows = defaultdict(list)
        for r in self.rows:
            self.ctrl_rows[r["controller"]].append(r)
        self._events = None

    def good(self, cond: str) -> bool:
        return self.cond[cond]["defect"] is None

    def good_conds(self) -> list[str]:
        return [c for c in self.cond_order if self.good(c)]

    def events(self) -> dict:
        if self._events is None:
            with gzip.open(self.folder / "events.json.gz", "rt") as fh:
                raw = json.load(fh)
            self._events = {k: v for k, v in raw.items() if k.split("|")[1] in PHASE_CTRLS}
        return self._events


def load_all(repo: Path) -> dict[tuple[str, str, str], Run]:
    sockets = connector_specs(repo)
    runs = {}
    for seed, (folder, _) in RUNS.items():
        for m in MACHINES:
            for s in SUITES:
                run = Run(repo / folder / f"{m}_{s}", sockets)
                assert run.base_seed == seed, (folder, m, s, run.base_seed)
                runs[(seed, m, s)] = run
    return runs


# ------------------------------------------------------------------------------------------
# Per-row predicates
# ------------------------------------------------------------------------------------------


def ok(r: dict) -> bool:
    return r["success"] == "True"


def bad_unit(r: dict) -> bool:
    """Declared success, not seated by the ground-truth check."""
    return r["declared_success"] == "True" and r["gt_seated"] == "False"


def stop(r: dict) -> bool:
    return r["protective_stop"] == "True"


def other_outcome(r: dict) -> str:
    """Why a trial did not count as seated, in four classes."""
    if ok(r):
        return "seated"
    if bad_unit(r):
        return "bad unit"
    if stop(r):
        return "protective stop"
    if r["declared_success"] == "False":
        return "rejected or aborted"
    return "other (" + r["failure_reason"] + ")"


def failed_checks(r: dict, cond: dict, crit: dict) -> list[str]:
    """Checks the logged pose shows failing, from the four pose columns alone.

    The code checks lateral offset per socket axis (|x|, |y| <= limit); trials.csv logs the
    radial offset only. A radius above sqrt(2) x limit fails for certain, a radius at or
    under the limit passes for certain, and the band between is 'lateral?'. The settled
    (TCP speed) and latched checks are not logged at all: a row whose logged pose passes
    every check it can show is 'not logged'.
    """
    out = []
    if float(r["final_depth_mm"]) < cond["depth_mm"] - crit["depth_tolerance_mm"]:
        out.append("depth")
    lat, lim = float(r["final_lateral_mm"]), cond["lat_limit_mm"]
    if lat > lim * math.sqrt(2.0):
        out.append("lateral")
    elif lat > lim:
        out.append("lateral?")
    if abs(float(r["final_yaw_deg"])) > crit["max_yaw_deg"]:
        out.append("yaw")
    if float(r["final_tilt_deg"]) > crit["max_tilt_deg"]:
        out.append("tilt")
    return out or ["not logged"]


def recomputed_seated(r: dict, cond: dict, crit: dict) -> bool:
    """gt_seated recomputed from final_depth_mm, final_lateral_mm, final_tilt_deg, final_yaw_deg."""
    return (float(r["final_depth_mm"]) >= cond["depth_mm"] - crit["depth_tolerance_mm"]
            and float(r["final_lateral_mm"]) <= cond["lat_limit_mm"]
            and float(r["final_tilt_deg"]) <= crit["max_tilt_deg"]
            and abs(float(r["final_yaw_deg"])) <= crit["max_yaw_deg"])


def max_angle(r: dict) -> float:
    return max(abs(float(r["final_yaw_deg"])), float(r["final_tilt_deg"]))


# ------------------------------------------------------------------------------------------
# Paired counts
# ------------------------------------------------------------------------------------------


def seated(run: Run, cond: str, ctrl: str) -> int:
    return sum(ok(r) for r in run.ctrl_rows[ctrl] if r["condition"] == cond)


def discordant(run: Run, conds, a: str, b: str) -> tuple[int, int, list[tuple[str, str]]]:
    """(a-only, b-only, a-only keys) over the given conditions, paired on trial index."""
    ao, bo, keys = 0, 0, []
    for r in run.ctrl_rows[a]:
        cd, ti = r["condition"], r["trial_index"]
        if cd not in conds:
            continue
        other = run.by.get((cd, b, ti))
        if other is None:
            continue
        if ok(r) and not ok(other):
            ao += 1
            keys.append((cd, ti))
        elif ok(other) and not ok(r):
            bo += 1
    return ao, bo, keys


def direction(pairs: list[tuple[int, int]]) -> str:
    signs = {(a > b) - (a < b) for a, b in pairs}
    if signs == {1}:
        return "C ahead on all 3"
    if signs == {-1}:
        return "other ahead on all 3"
    if signs == {0}:
        return "equal on all 3"
    return "mixed"


# ------------------------------------------------------------------------------------------
# Phases from events
# ------------------------------------------------------------------------------------------


def phase_times(events: list, cycle_time_s: float) -> tuple[dict[str, float], float]:
    """Seconds per bucket for one trial, and the gap between the summed phases and cycle_time_s.

    The trial clock starts at the first state event (APPROACH); the cycle ends at the
    finish event. Buckets: approach (the first APPROACH), align (ALIGN, TARE on the first
    attempt), first_insert (INSERT, DETECT, DESCEND, SPIRAL before any retry), retry
    (RECOVER, ALIGN: retry n, APPROACH: retry and every insertion state after one),
    verify (every VERIFY state; for I and H this includes the pull retry), and
    reinsert_after_verify (from RECOVER: verify_failed to the next VERIFY).
    """
    states = [(float(t), text) for t, kind, text in events if kind == "state"]
    fin = [float(t) for t, kind, _ in events if kind == "finish"]
    end = fin[-1] if fin else states[0][0] + cycle_time_s
    acc = dict.fromkeys(BUCKETS, 0.0)
    retried = vfail = False
    for (t0, s), (t1, _) in zip(states, states[1:] + [(end, "END")]):
        if s.startswith("SUCCESS") or s.startswith("FAILURE"):
            b = None
        elif s.startswith("VERIFY"):
            b, vfail = "verify", False
        elif s == "RECOVER: verify_failed":
            b, vfail = "reinsert_after_verify", True
        elif vfail:
            b = "reinsert_after_verify"
        elif s.startswith("RECOVER") or s.startswith("ALIGN: retry") or s == "APPROACH: retry":
            b, retried = "retry", True
        elif s == "APPROACH":
            b = "approach"
        elif s in ("ALIGN", "TARE"):
            b = "retry" if retried else "align"
        else:  # INSERT, DETECT: ..., DESCEND, SPIRAL
            b = "retry" if retried else "first_insert"
        if b is not None:
            acc[b] += t1 - t0
    gap = (end - states[0][0]) - cycle_time_s
    return acc, gap


def pct(xs, q) -> float:
    return float(np.percentile(xs, q)) if len(xs) else float("nan")


# ------------------------------------------------------------------------------------------
# Report sections
# ------------------------------------------------------------------------------------------


class Out:
    def __init__(self):
        self.files: dict[str, list[str]] = defaultdict(list)
        self.key: list[str] = []

    def w(self, name: str, *lines: str) -> None:
        self.files[name].extend(lines)

    def k(self, line: str) -> None:
        self.key.append(line)


HEADER = ("Generated by `python -m experiments.v02f_evidence` from committed results/benchmark_v0.2d "
          "(seed 20261123), benchmark_v0.2d_rep (20261124) and benchmark_v0.2e (20261130). "
          "v0.2d and its replication ran the v0.2d code (42df5c8); v0.2e ran the v0.2e code "
          "(ddd0d34). Simulation only.")


def part1(runs, out: Out) -> None:
    f = "PERCOND.md"
    out.w(f, "# Per condition, per seed: C against I, F, H, J, and G against C", "", HEADER, "",
          "POST HOC: the per-condition breakdown was chosen after the benchmark results were seen. "
          "Good-part conditions only (on latching and latch_spread the deliberately bad parts are in "
          "BAD_UNITS.md). Seated = `success` in trials.csv. Discordant pairs are on the same trial "
          "index: `C-only / X-only` counts trials that C seats and X does not, then the reverse; for G "
          "the pair is `G-only / C-only`. No per-condition p-values; the cell total line gives the "
          "exact McNemar p on that seed, as `checkpoint_report` does.", "",
          "On housing-only suites (standard, heldout) I has no pull to run, and its rows equal F's.", "")
    for seed in SEEDS:
        for m in MACHINES:
            for s in SUITES:
                run = runs[(seed, m, s)]
                conds = run.good_conds()
                out.w(f, f"## seed {seed}, {m} {s}", "",
                      "| Condition | n | C | I | F | H | J | G | C/I | C/F | C/H | C/J | G/C |",
                      "|---|---|---|---|---|---|---|---|---|---|---|---|---|")
                tot = defaultdict(int)
                for cd in conds:
                    n = sum(1 for r in run.rows if r["condition"] == cd and r["controller"] == C)
                    cells = [str(seated(run, cd, c)) for c in (C, I, F, H, J, G)]
                    pairs = [discordant(run, (cd,), C, x)[:2] for x in VS_C] + [discordant(run, (cd,), G, C)[:2]]
                    tot["n"] += n
                    for c, v in zip((C, I, F, H, J, G), cells):
                        tot[c] += int(v)
                    out.w(f, f"| {cd} | {n} | " + " | ".join(cells) + " | "
                          + " | ".join(f"{a} / {b}" for a, b in pairs) + " |")
                tp = [discordant(run, conds, C, x)[:2] for x in VS_C] + [discordant(run, conds, G, C)[:2]]
                out.w(f, f"| **total** | {tot['n']} | " + " | ".join(str(tot[c]) for c in (C, I, F, H, J, G))
                      + " | " + " | ".join(f"{a} / {b} (p {fp(mcnemar(a, b))})" for a, b in tp) + " |", "")


def part1_concentration(runs, out: Out) -> dict:
    f = "CONCENTRATION.md"
    out.w(f, "# Where C's wins and losses concentrate", "", HEADER, "",
          "POST HOC throughout: the condition grouping (noise_1mm, noise_2mm, generalization_combined) "
          "was named by an independent review after the results were seen.", "")
    # (a) per cell: totals, top conditions, losses
    out.w(f, "## (a) C against each controller, per cell and seed", "",
          "`C-only / X-only` over the good-part trials of the cell, exact McNemar p on that seed. "
          "`C wins in` lists the conditions holding C's wins, largest first. `X ahead in` lists "
          "every condition where X seats more trials than C (X-only > C-only).", "",
          "| Seed | Cell | X | C-only / X-only (p) | C wins in | X ahead in |", "|---|---|---|---|---|---|")
    stats = {}
    for x in VS_C:
        for m in MACHINES:
            for s in SUITES:
                for seed in SEEDS:
                    run = runs[(seed, m, s)]
                    conds = run.good_conds()
                    a, b, _ = discordant(run, conds, C, x)
                    per = {cd: discordant(run, (cd,), C, x)[:2] for cd in conds}
                    wins = sorted(((v[0], cd) for cd, v in per.items() if v[0]), reverse=True)
                    loss = [(cd, v) for cd, v in per.items() if v[1] > v[0]]
                    stats[(seed, m, s, x)] = (a, b, per)
                    out.w(f, f"| {seed} | {m} {s} | {L(x)} | {a} / {b} ({fp(mcnemar(a, b))}) | "
                          + (", ".join(f"{cd} {k}" for k, cd in wins) or "none") + " | "
                          + (", ".join(f"{cd} {v[0]}/{v[1]}" for cd, v in loss) or "none") + " |")
    out.w(f, "")
    # (b) share in the three high camera-error conditions
    out.w(f, "## (b) Share of C's wins in noise_1mm, noise_2mm and generalization_combined (standard)", "",
          "| Seed | Machine | X | C-only total | in the 3 conditions | elsewhere (condition: count) | "
          "X-only total | X-only in the 3 |", "|---|---|---|---|---|---|---|---|")
    for x in VS_C:
        for m in MACHINES:
            for seed in SEEDS:
                a, b, per = stats[(seed, m, "standard", x)]
                inn = sum(per[cd][0] for cd in NOISY)
                ell = ", ".join(f"{cd}: {v[0]}" for cd, v in per.items() if cd not in NOISY and v[0]) or "none"
                binn = sum(per[cd][1] for cd in NOISY)
                out.w(f, f"| {seed} | {m} | {L(x)} | {a} | {inn} | {ell} | {b} | {binn} |")
                if x == I:
                    out.k(f"standard, seed {seed}, {m}: C-only vs I {a}, of which {inn} in noise_1mm/noise_2mm/"
                          f"generalization_combined; elsewhere: {ell}; I-only {b} "
                          "(CONCENTRATION.md (b), post hoc)")
    out.w(f, "")
    # (c) what the other controller did on C's wins, and C on its losses
    out.w(f, "## (c) What the other controller did on the trials C wins, and C on the trials C loses", "",
          "Outcome classes: bad unit (declared success, not seated), rejected or aborted (declared "
          "failure), protective stop, other.", "",
          "| Seed | Cell | X | X on C-only trials | C on X-only trials |", "|---|---|---|---|---|")
    for x in (I, J):
        for m in MACHINES:
            for s in ("standard", "heldout", "latching", "latch_spread"):
                for seed in SEEDS:
                    run = runs[(seed, m, s)]
                    conds = run.good_conds()
                    _, _, keys = discordant(run, conds, C, x)
                    xo = Counter(other_outcome(run.by[(cd, x, ti)]) for cd, ti in keys)
                    _, _, rkeys = discordant(run, conds, x, C)
                    co = Counter(other_outcome(run.by[(cd, C, ti)]) for cd, ti in rkeys)
                    out.w(f, f"| {seed} | {m} {s} | {L(x)} | {dict(xo.most_common()) or '-'} | "
                          f"{dict(co.most_common()) or '-'} |")
                    if x == I and s == "standard":
                        out.k(f"standard, seed {seed}, {m}: I's outcome on the {len(keys)} C-only trials: "
                              f"{dict(xo.most_common())} (CONCENTRATION.md (c))")
    out.w(f, "")
    # (d) decomposition on housing-only parts: C vs J isolates the insertion, J vs F the VERIFY
    out.w(f, "## (d) Insertion against VERIFY, on housing-only suites", "",
          "J runs F's insertion and then C's VERIFY. On housing-only parts I equals F. So, on the "
          "same trials, C against J compares the two insertions with the same VERIFY, and J against "
          "F (= I) compares the same insertion with and without C's VERIFY. Not a fair-baseline "
          "comparison (J is not a fair baseline). Seated pairs, then bad units.", "",
          "| Seed | Cell | C-only / J-only seated | J-only / F-only seated | bad units C / J / F | "
          "J on F's bad-unit trials |", "|---|---|---|---|---|---|")
    for m in MACHINES:
        for s in ("standard", "heldout"):
            for seed in SEEDS:
                run = runs[(seed, m, s)]
                conds = run.good_conds()
                cj = discordant(run, conds, C, J)[:2]
                jf = discordant(run, conds, J, F)[:2]
                bu = {c: sum(bad_unit(r) for r in run.rows if r["controller"] == c) for c in (C, J, F)}
                fb = [(r["condition"], r["trial_index"]) for r in run.rows if r["controller"] == F and bad_unit(r)]
                jo = Counter(other_outcome(run.by[(cd, J, ti)]) for cd, ti in fb)
                out.w(f, f"| {seed} | {m} {s} | {cj[0]} / {cj[1]} | {jf[0]} / {jf[1]} | "
                      f"{bu[C]} / {bu[J]} / {bu[F]} | {dict(jo.most_common())} |")
                if s == "standard":
                    out.k(f"standard, seed {seed}, {m}: C-only/J-only {cj[0]}/{cj[1]} (p {fp(mcnemar(*cj))}); "
                          f"J-only/F-only {jf[0]}/{jf[1]} (p {fp(mcnemar(*jf))}); bad units C {bu[C]}, J {bu[J]}, "
                          f"F=I {bu[F]}; J on F's bad-unit trials {dict(jo.most_common())} (CONCENTRATION.md (d))")
    out.w(f, "")
    # (e) every condition, direction across the three seeds
    out.w(f, "## (e) Per condition, direction across the three seeds", "",
          "`C-only / X-only` on each seed; the last column says whether the sign is the same on all "
          "three. Rows where neither side has a discordant trial on any seed are left out.", "")
    for x in VS_C:
        out.w(f, f"### C against {L(x)}", "", "| Cell | Condition | 20261123 | 20261124 | 20261130 | Direction |",
              "|---|---|---|---|---|---|")
        for m in MACHINES:
            for s in SUITES:
                for cd in runs[(SEEDS[0], m, s)].good_conds():
                    ps = [stats[(seed, m, s, x)][2][cd] for seed in SEEDS]
                    if not any(a or b for a, b in ps):
                        continue
                    out.w(f, f"| {m} {s} | {cd} | " + " | ".join(f"{a} / {b}" for a, b in ps)
                          + f" | {direction(ps)} |")
        out.w(f, "")
    return stats


def part1_losses(runs, stats, out: Out) -> None:
    """Conditions where a fair baseline seats more than C on all three seeds, and why C fails there."""
    f = "CONCENTRATION.md"
    out.w(f, "## (f) Why C fails where I seats more on all three seeds", "",
          "Failure reasons of C's and I's unsuccessful trials in those conditions (`failure_reason`).", "",
          "| Cell | Condition | Seed | C failures | I failures |", "|---|---|---|---|---|")
    for (seed, m, s, x), (_, _, per) in sorted(stats.items()):
        if x != I or seed != SEEDS[0]:
            continue
        for cd in per:
            ps = [stats[(sd, m, s, I)][2][cd] for sd in SEEDS]
            if direction(ps) != "other ahead on all 3":
                continue
            for sd in SEEDS:
                rr = runs[(sd, m, s)]
                fc = Counter(r["failure_reason"] for r in rr.ctrl_rows[C] if r["condition"] == cd and not ok(r))
                fi = Counter(r["failure_reason"] for r in rr.ctrl_rows[I] if r["condition"] == cd and not ok(r))
                out.w(f, f"| {m} {s} | {cd} | {sd} | {dict(fc.most_common()) or '-'} | {dict(fi.most_common()) or '-'} |")
    out.w(f, "")
    for x in (I, F, H):
        rows = []
        for (seed, m, s, xx), (_, _, per) in stats.items():
            if xx != x or seed != SEEDS[0]:
                continue
            for cd in per:
                ps = [stats[(sd, m, s, x)][2][cd] for sd in SEEDS]
                if direction(ps) == "other ahead on all 3":
                    rows.append(f"{m} {s} {cd} (" + ", ".join(f"{a}/{b}" for a, b in ps) + ")")
        out.k(f"conditions where {L(x)} seats more than C on all 3 seeds (C-only/{L(x)}-only per seed): "
              + ("; ".join(rows) or "none") + " (CONCENTRATION.md (e), post hoc)")


SEAT_RE = re.compile(r"tilt aligned to floor by \(([+-]?[\d.]+),([+-]?[\d.]+)\) deg")
YAW_RE = re.compile(r"(?:corrected|turn) ([+-]?[\d.]+) deg")


def verify_corrections(events: list) -> tuple[float | None, float]:
    """(tilt alignment magnitude in deg or None, summed |yaw turn| in deg) from one trial's VERIFY events."""
    tilt, yaw = None, 0.0
    for _, kind, text in events:
        if kind == "seat_conform":
            mt = SEAT_RE.search(text)
            if mt:
                tilt = (tilt or 0.0) + math.hypot(float(mt.group(1)), float(mt.group(2)))
        elif kind in ("yaw_centering", "wall_yaw"):
            my = YAW_RE.search(text)
            if my:
                yaw += abs(float(my.group(1)))
    return tilt, yaw


def part1_verify(runs, out: Out) -> None:
    f = "CONCENTRATION.md"
    out.w(f, "## (g) What C's VERIFY does on housing-only parts", "",
          "From the `seat_conform` (\"tilt aligned to floor by (a, b) deg\"), `yaw_centering` (gantry, "
          "\"corrected x deg\") and `wall_yaw` (arm, \"turn x deg\") events. Tilt = |(a, b)|, yaw = summed "
          "|turn|. Over the trials that reached VERIFY; then over the trials where F (= I on these suites) "
          "passed a bad unit, for J, which ran C's VERIFY after F's insertion on the same trial.", "",
          "| Seed | Cell | Ctrl | trials with VERIFY | tilt aligned: median / p95 / max (deg) | yaw turned > 0 | "
          "yaw turn: median / p95 / max (deg) |", "|---|---|---|---|---|---|---|")
    for seed in SEEDS:
        for m in MACHINES:
            for s in ("standard", "heldout"):
                run = runs[(seed, m, s)]
                ev = run.events()
                fb = {(r["condition"], r["trial_index"]) for r in run.ctrl_rows[F] if bad_unit(r)}
                for label, c, keyset in ((L(C), C, None), (L(J), J, None), ("J on F's bad units", J, fb)):
                    tilts, yaws = [], []
                    for r in run.ctrl_rows[c]:
                        if keyset is not None and (r["condition"], r["trial_index"]) not in keyset:
                            continue
                        e = ev[f"{r['condition']}|{c}|{r['trial_index']}"]
                        if not any(k == "state" and t.startswith("VERIFY") for _, k, t in e):
                            continue
                        t, y = verify_corrections(e)
                        if t is not None:
                            tilts.append(t)
                        yaws.append(y)
                    if not yaws:
                        continue
                    ya = np.array(yaws)
                    out.w(f, f"| {seed} | {m} {s} | {label} | {len(yaws)} | "
                          + (f"{pct(tilts, 50):.2f} / {pct(tilts, 95):.2f} / {max(tilts):.2f}" if tilts else "-")
                          + f" | {int((ya > 0).sum())} | {pct(ya, 50):.2f} / {pct(ya, 95):.2f} / {ya.max():.2f} |")
                    if seed == "20261130" and s == "standard" and keyset is not None:
                        out.k(f"seed 20261130, {m} standard: on the {len(yaws)} trials where F passed a bad unit and J "
                              f"reached VERIFY, C's VERIFY (run by J) aligned tilt by median {pct(tilts, 50):.2f} deg "
                              f"(max {max(tilts):.2f}) and turned yaw on {int((ya > 0).sum())} (median "
                              f"{pct(ya, 50):.2f}, max {ya.max():.2f} deg) (CONCENTRATION.md (g))")
    out.w(f, "")


def part2(runs, out: Out, outdir: Path) -> None:
    f = "BAD_UNITS.md"
    out.w(f, "# Bad units: declared success, not seated", "", HEADER, "",
          "A bad unit is a row with `declared_success` True and `gt_seated` False. On good-part "
          "trials it is a connector the cell would ship as good that the ground truth scores out of "
          "tolerance. On deliberately bad parts it is a bad part passed. For controllers that "
          "declare (C, D, F, G, H, I, J) this set equals the `escape` count of the benchmark tables. "
          "A, B and E never declare and are not listed.", "",
          "Failed checks come from the four logged pose columns (`failed_checks` in the script): "
          "`depth` (depth < socket depth - 0.5 mm), `yaw` (|yaw| > 3 deg), `tilt` (tilt > 3 deg), "
          "`lateral` (radial offset > sqrt 2 x the per-axis limit, so certain), `lateral?` (radial "
          "offset between the limit and sqrt 2 x the limit: the code checks per axis, the radius alone "
          "cannot tell), and `not logged` (the pose passes every check it shows, so the failure is the "
          "settled check, the latched check, or a per-axis lateral fail; none is logged). As-run "
          "tolerances: depth 0.5 mm, lateral clearance + 0.15 mm per axis, tilt and yaw 3 deg "
          "(README 'Success tolerances': an assumed seating specification).", "")
    allbu = []
    for seed in SEEDS:
        for m in MACHINES:
            for s in SUITES:
                run = runs[(seed, m, s)]
                for r in run.rows:
                    if bad_unit(r):
                        cond = run.cond[r["condition"]]
                        allbu.append((seed, m, s, r, cond, failed_checks(r, cond, run.crit)))
    with (outdir / "bad_units.csv").open("w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["seed", "machine", "suite", "controller", "letter", "condition", "defect", "trial_index",
                     "final_depth_mm", "socket_depth_mm", "final_lateral_mm", "lateral_limit_mm", "final_yaw_deg",
                     "final_tilt_deg", "failed_checks", "failure_reason", "cycle_time_s"])
        for seed, m, s, r, cond, fc in allbu:
            wr.writerow([seed, m, s, r["controller"], L(r["controller"]), r["condition"], cond["defect"] or "",
                         r["trial_index"], f"{float(r['final_depth_mm']):.3f}", cond["depth_mm"],
                         f"{float(r['final_lateral_mm']):.3f}", f"{cond['lat_limit_mm']:.2f}",
                         f"{float(r['final_yaw_deg']):.2f}", f"{float(r['final_tilt_deg']):.2f}", "+".join(fc),
                         r["failure_reason"], f"{float(r['cycle_time_s']):.2f}"])
    good = [x for x in allbu if x[4]["defect"] is None]
    bad = [x for x in allbu if x[4]["defect"] is not None]

    # (a) good-part summary per seed and controller (all suites, both machines)
    n_good = {}
    for seed in SEEDS:
        n_good[seed] = sum(1 for m in MACHINES for s in SUITES for r in runs[(seed, m, s)].rows
                           if r["controller"] == C and runs[(seed, m, s)].good(r["condition"]))
    ctrls = (C, G, J, H, I, D, F)
    out.w(f, "## (a) Bad units on good-part trials, per seed, both machines and all four suites", "",
          "| Controller | " + " | ".join(f"{sd} (of {n_good[sd]})" for sd in SEEDS) + " |",
          "|---" * (len(SEEDS) + 1) + "|")
    for c in ctrls:
        cnt = [sum(1 for x in good if x[0] == sd and x[3]["controller"] == c) for sd in SEEDS]
        out.w(f, f"| {L(c)} {c} | " + " | ".join(map(str, cnt)) + " |")
        out.k(f"bad units on good-part trials, {L(c)}, per seed {'/'.join(SEEDS)}: {'/'.join(map(str, cnt))} "
              f"(of {n_good[SEEDS[0]]} each; BAD_UNITS.md (a))")
    out.w(f, "")

    # (b) per cell, with failed-check classes
    out.w(f, "## (b) Bad units on good-part trials, per cell, with the checks they failed", "",
          "A row can fail more than one check, so the check columns can sum past n. `angle only` = the "
          "pose shows only yaw and/or tilt failing (depth and lateral pass for certain).", "",
          "| Seed | Cell | Ctrl | n | conditions | depth | lateral | lateral? | yaw | tilt | not logged | "
          "angle only | depth range (mm) | max(yaw, tilt) range (deg) |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for seed in SEEDS:
        for m in MACHINES:
            for s in SUITES:
                for c in ctrls:
                    xs = [x for x in good if x[:3] == (seed, m, s) and x[3]["controller"] == c]
                    if not xs:
                        continue
                    fc = Counter(k for x in xs for k in x[5])
                    conds = Counter(x[3]["condition"] for x in xs)
                    ang = sum(1 for x in xs if set(x[5]) <= {"yaw", "tilt"})
                    dep = [float(x[3]["final_depth_mm"]) for x in xs]
                    an = [max_angle(x[3]) for x in xs]
                    out.w(f, f"| {seed} | {m} {s} | {L(c)} | {len(xs)} | "
                          + ", ".join(f"{k} {v}" for k, v in conds.most_common()) + " | "
                          + " | ".join(str(fc.get(k, 0)) for k in ("depth", "lateral", "lateral?", "yaw", "tilt",
                                                                    "not logged"))
                          + f" | {ang} | {min(dep):.2f}-{max(dep):.2f} | {min(an):.2f}-{max(an):.2f} |")
    out.w(f, "")

    # (c) the recorded angle of I's and H's bad units on housing-only suites (description only)
    out.w(f, "## (c) Recorded max(|yaw|, tilt) of the housing-only bad units", "",
          "A description of the logged pose, not a rescoring: the logs cannot say whether a row with a "
          "smaller angle error would have passed (TOLERANCE.md). Bins are (lower, upper] in degrees; "
          "rows whose angles are both within 3 deg are in `<= 3`.", "",
          "| Seed | Machine | Ctrl | n | <= 3 | " + " | ".join(f"{a}-{b if b < 90 else ''}" for a, b in ANGLE_BINS)
          + " | depth < 14.5 mm |", "|---|---|---|---|---|---|---|---|---|---|")
    for seed in SEEDS:
        for m in MACHINES:
            for c in (I, H, D, F, J, G):
                xs = [x for x in good if x[0] == seed and x[1] == m and x[2] in ("standard", "heldout")
                      and x[3]["controller"] == c]
                if not xs:
                    continue
                an = [max_angle(x[3]) for x in xs]
                bins = [sum(1 for v in an if lo < v <= hi) for lo, hi in ANGLE_BINS]
                short = sum(1 for x in xs if "depth" in x[5])
                out.w(f, f"| {seed} | {m} | {L(c)} | {len(xs)} | {sum(1 for v in an if v <= 3.0)} | "
                      + " | ".join(map(str, bins)) + f" | {short} |")
    for seed in SEEDS:
        for m in MACHINES:
            xs = [x for x in good if x[:3] == (seed, m, "standard") and x[3]["controller"] == I]
            dep = [float(x[3]["final_depth_mm"]) for x in xs]
            an = [max_angle(x[3]) for x in xs]
            conds = Counter(x[3]["condition"] for x in xs)
            out.k(f"standard, seed {seed}, {m}: I's {len(xs)} bad units in {dict(conds.most_common())}; depth "
                  f"{min(dep):.2f}-{max(dep):.2f} mm; max(|yaw|, tilt) {min(an):.2f}-{max(an):.2f} deg; "
                  f"{sum(v > 4.0 for v in an)} above 4 deg; {sum('depth' in x[5] for x in xs)} short of 14.5 mm "
                  "(BAD_UNITS.md (b), (c))")
    out.w(f, "")

    # (d) bad parts passed
    out.w(f, "## (d) Deliberately bad parts passed, per seed (latching and latch_spread, both machines)", "",
          "| Seed | Ctrl | n passed | of | by defect | failed checks shown by the pose |", "|---|---|---|---|---|---|")
    for seed in SEEDS:
        nbad = sum(1 for m in MACHINES for s in SUITES for r in runs[(seed, m, s)].rows
                   if r["controller"] == C and not runs[(seed, m, s)].good(r["condition"]))
        for c in (C, G, J, H, I, D, F):
            xs = [x for x in bad if x[0] == seed and x[3]["controller"] == c]
            dfc = Counter(x[4]["defect"] for x in xs)
            fc = Counter(k for x in xs for k in x[5])
            out.w(f, f"| {seed} | {L(c)} | {len(xs)} | {nbad} | {dict(dfc.most_common()) or '-'} | "
                  f"{dict(fc.most_common()) or '-'} |")
            if c in (C, D, F, I):
                out.k(f"bad parts passed, seed {seed}, {L(c)}: {len(xs)} of {nbad} (BAD_UNITS.md (d))")
    out.w(f, "", "The latched check (latched and latch not broken) is not logged in trials.csv, so most "
          "bad parts passed show `not logged`.", "")

    # (e) full list, good-part trials
    out.w(f, "## (e) Every bad unit on a good-part trial", "",
          "| Seed | Cell | Ctrl | Condition | Trial | Depth (mm) | Lateral (mm, limit) | Yaw (deg) | Tilt (deg) | "
          "Failed |", "|---|---|---|---|---|---|---|---|---|---|")
    for seed, m, s, r, cond, fc in good:
        out.w(f, f"| {seed} | {m} {s} | {L(r['controller'])} | {r['condition']} | {r['trial_index']} | "
              f"{float(r['final_depth_mm']):.2f} | {float(r['final_lateral_mm']):.2f} ({cond['lat_limit_mm']:.2f}) | "
              f"{float(r['final_yaw_deg']):+.2f} | {float(r['final_tilt_deg']):.2f} | {'+'.join(fc)} |")
    out.w(f, "")


def part3(runs, out: Out) -> bool:
    f = "TOLERANCE.md"
    out.w(f, "# Tolerance sensitivity: can gt_seated be recomputed from the logged pose?", "", HEADER, "",
          "POST HOC: this part exists because the bad units were seen to sit just past 3 deg.", "",
          "## How gt_seated is computed", "",
          "`defex/tasks/insertion.py`, `evaluate_final_state`: `seated` is the AND of",
          "- depth >= socket depth - `depth_tolerance_mm` (0.5 mm);",
          "- lateral, checked per socket axis: |x| <= limit and |y| <= limit, limit = clearance + "
          "`lateral_margin_mm` (0.15 mm);",
          "- tilt <= `max_tilt_deg` (3 deg) and |yaw| <= `max_yaw_deg` (3 deg);",
          "- settled: TCP speed <= `max_final_speed_mm_s` (2 mm/s);",
          "- on latching connectors only: latched and latch not broken.",
          "",
          "`trials.csv` logs depth, tilt and yaw exactly, but lateral only as the radius "
          "sqrt(x^2 + y^2), and does not log the TCP speed or the latch state.", "",
          "## Recomputation at the as-run tolerances", "",
          "Rule: depth and tilt and yaw as above, lateral radius <= limit (the only reading of the radius "
          "that never passes a trial the code fails).", "",
          "| Seed | Cell | rows | match | recomputed fail, gt seated (radius in the sqrt 2 band) | "
          "recomputed seated, gt not (by failure_reason) |", "|---|---|---|---|---|---|")
    total = mism = 0
    by_kind = Counter()
    lenient_house = Counter()
    for seed in SEEDS:
        for m in MACHINES:
            for s in SUITES:
                run = runs[(seed, m, s)]
                a = Counter()
                b = Counter()
                for r in run.rows:
                    cond = run.cond[r["condition"]]
                    rec = recomputed_seated(r, cond, run.crit)
                    gt = r["gt_seated"] == "True"
                    total += 1
                    if rec == gt:
                        pass
                    elif gt:
                        lat, lim = float(r["final_lateral_mm"]), cond["lat_limit_mm"]
                        a["in band" if lim < lat <= lim * math.sqrt(2) else "outside band"] += 1
                    else:
                        b[r["failure_reason"].split(":")[0] if not r["failure_reason"].startswith("seated_out")
                          else r["failure_reason"]] += 1
                    if s in ("standard", "heldout"):
                        lat, lim = float(r["final_lateral_mm"]), cond["lat_limit_mm"]
                        len_ok = rec or (lim < lat <= lim * math.sqrt(2)
                                         and recomputed_seated({**r, "final_lateral_mm": "0"}, cond, run.crit))
                        if len_ok != gt:
                            lenient_house[seed] += 1
                n = len(run.rows)
                mm = sum(a.values()) + sum(b.values())
                mism += mm
                by_kind["band"] += sum(a.values())
                by_kind["latching" if run.cond[run.cond_order[0]]["connector"] != "rect_12x8" else "housing"] += \
                    sum(b.values())
                out.w(f, f"| {seed} | {m} {s} | {n} | {n - mm} | {dict(a) or 0} | {dict(b) or 0} |")
    exact = mism == 0
    out.w(f, "", f"Rows: {total}. Mismatches: {mism}. "
          + ("The recomputation reproduces gt_seated exactly." if exact else
             "**The recomputation does not reproduce gt_seated.** So no figure is rescored from the four "
             "logged columns. The exact rescoring further down uses a replay with the missing values "
             "logged."), "",
          "Why it does not match:", "",
          f"- {by_kind['band']} rows are seated by the code but have a lateral radius above the per-axis "
          "limit (all inside the sqrt 2 band): a plug sitting toward a corner of the rectangular cavity. "
          "The radius cannot tell these from plugs that fail per axis.",
          f"- {by_kind['latching']} rows on the latching suites pass every logged pose check but are not "
          "seated: the latched check (`seated_out_of_tolerance:latched`, and `false_accept` on bad parts) "
          "or the settled check; neither is logged.",
          f"- {by_kind['housing']} rows on the housing-only suites pass every logged pose check but are "
          "not seated: the settled (TCP speed) check, which is not logged.", "",
          "A reading of the radius that passes every row in the sqrt 2 band when depth, tilt and yaw pass "
          "(an assumption, not the code's rule) leaves these mismatches on the housing-only suites "
          "(standard and heldout): "
          + ", ".join(f"seed {sd}: {lenient_house[sd]}" for sd in SEEDS)
          + ". Zero on one seed does not make the rule exact: it only says no row in that seed's data "
          "sat in the band and failed per axis. This is reported so the lead can decide whether a "
          "bounded rescoring is worth doing; it is not used.", "")
    out.k(f"gt_seated recomputed from the four pose columns at the as-run tolerances: {mism} of {total} rows "
          f"differ ({by_kind['band']} lateral-radius band, {by_kind['latching']} latched or settled check, "
          f"{by_kind['housing']} settled check); no rescoring from these columns (TOLERANCE.md)")
    return exact


# ------------------------------------------------------------------------------------------
# Part 3b: exact rescoring from the seed-20261130 replay with the missing values logged
# ------------------------------------------------------------------------------------------

REPLAYS = {seed: f"results/v0.2f_evidence/replay_{seed}" for seed in SEEDS}
RESCORE_SUITES = ("standard", "heldout", "latching")
RESCORE_CTRLS = (C, F, I, J)
ANGLE_TOLS = (2.0, 2.5, 3.0, 3.5, 4.0, 5.0)
DEPTH_TOLS = (0.5, 1.0)
BLOCKERS = ("protective_stop", "penetration_violation", "excessive_contact_force", "workspace_limit", "timeout")
NEW_COLS = ("final_x_mm", "final_y_mm", "final_tcp_speed_mm_s", "final_latched", "final_latch_intact")


def exact_seated(r: dict, cond: dict, crit: dict, depth_tol: float, angle_tol: float) -> bool:
    """`evaluate_final_state`'s rule, from a row that carries the v0.2f columns."""
    lim = cond["lat_limit_mm"]
    ok_ = (float(r["final_depth_mm"]) >= cond["depth_mm"] - depth_tol
           and abs(float(r["final_x_mm"])) <= lim and abs(float(r["final_y_mm"])) <= lim
           and float(r["final_tilt_deg"]) <= angle_tol and abs(float(r["final_yaw_deg"])) <= angle_tol
           and float(r["final_tcp_speed_mm_s"]) <= crit["max_final_speed_mm_s"])
    if r["final_latched"] not in ("", "None"):
        ok_ = ok_ and r["final_latched"] == "True" and r["final_latch_intact"] == "True"
    return ok_


def logged_seated(r: dict, cond: dict, crit: dict, depth_tol: float, angle_tol: float) -> bool | None:
    """Rescored seated from an old row, or None when the old columns cannot decide it.

    seated(tol) = depth(tol) and angles(tol) and R, where R (per-axis lateral, settled,
    latched) does not depend on these tolerances. Seated as run means R holds; not seated
    as run with depth and angles passing means R fails.
    """
    def da(dt, at):
        return (float(r["final_depth_mm"]) >= cond["depth_mm"] - dt and float(r["final_tilt_deg"]) <= at
                and abs(float(r["final_yaw_deg"])) <= at)

    now = da(depth_tol, angle_tol)
    if r["gt_seated"] == "True":
        return now
    if da(crit["depth_tolerance_mm"], crit["max_tilt_deg"]) or not now:
        return False
    if float(r["final_lateral_mm"]) > cond["lat_limit_mm"] * math.sqrt(2.0):
        return False
    return None


def rescored_success(r: dict, seated_: bool) -> bool:
    return seated_ and r["failure_reason"] not in BLOCKERS and r["declared_success"] != "False"


def _rescore_seed(runs, rep: dict, seed: str) -> tuple[dict, tuple[int, int, int, int]]:
    """Rescored seated value of every good-part C/F/I/J row of one seed, at every tolerance."""
    undecided_outside = agree = disagree = undecided_in_rep = 0
    seated_t = {}
    for m in MACHINES:
        for s in RESCORE_SUITES:
            old = runs[(seed, m, s)]
            rr = rep.get((m, s))
            repconds = {r["condition"] for r in rr.rows} if rr else set()
            for c in RESCORE_CTRLS:
                for r in old.ctrl_rows[c]:
                    if not old.good(r["condition"]):
                        continue
                    cond = old.cond[r["condition"]]
                    key = (m, s, c, r["condition"], r["trial_index"])
                    for dt in DEPTH_TOLS:
                        for at in ANGLE_TOLS:
                            lg = logged_seated(r, cond, old.crit, dt, at)
                            if r["condition"] in repconds:
                                rx = rr.by[(r["condition"], c, r["trial_index"])]
                                ex = exact_seated(rx, cond, old.crit, dt, at)
                                if lg is None:
                                    undecided_in_rep += 1
                                else:
                                    agree += lg == ex
                                    disagree += lg != ex
                                val = ex
                            else:
                                if lg is None:
                                    undecided_outside += 1
                                    continue
                                val = lg
                            seated_t[key + (dt, at)] = (val, r)
    return seated_t, (agree, disagree, undecided_in_rep, undecided_outside)


def _drift_margin(lst, old) -> tuple[float, int] | None:
    """Smallest (distance to a threshold) / (pose drift) over drifted rows the old columns cannot decide."""
    worst, rows = None, set()
    for m, s, r, o in lst:
        cond = old.cond[r["condition"]]
        drift = max(abs(float(o[k]) - float(r[k]))
                    for k in ("final_depth_mm", "final_tilt_deg", "final_yaw_deg", "final_lateral_mm"))
        for dt in DEPTH_TOLS:
            for at in ANGLE_TOLS:
                if logged_seated(o, cond, old.crit, dt, at) is not None:
                    continue
                rows.add((r["controller"], r["trial_index"]))
                lim = cond["lat_limit_mm"]
                margin = min(abs(float(r["final_tilt_deg"]) - at), abs(abs(float(r["final_yaw_deg"])) - at),
                             abs(float(r["final_depth_mm"]) - (cond["depth_mm"] - dt)),
                             abs(abs(float(r["final_x_mm"])) - lim), abs(abs(float(r["final_y_mm"])) - lim),
                             abs(float(r["final_tcp_speed_mm_s"]) - old.crit["max_final_speed_mm_s"]))
                if drift > 0:
                    worst = margin / drift if worst is None else min(worst, margin / drift)
    return None if worst is None else (worst, len(rows))


def _rescore_cell(runs, seated_t, seed, m, s, dt, at):
    """Rescored success per controller, (C-only, I-only), (C-only, F-only), bad units per controller."""
    old = runs[(seed, m, s)]
    trials = sorted({(r["condition"], r["trial_index"]) for r in old.ctrl_rows[C] if old.good(r["condition"])})
    succ, bu = {}, {}
    for c in RESCORE_CTRLS:
        sc, b = {}, 0
        for cd, ti in trials:
            val, r = seated_t[(m, s, c, cd, ti, dt, at)]
            sc[(cd, ti)] = rescored_success(r, val)
            b += r["declared_success"] == "True" and not val
            if dt == 0.5 and at == 3.0:
                assert sc[(cd, ti)] == ok(r) and (r["declared_success"] == "True" and not val) == bad_unit(r)
        succ[c], bu[c] = sc, b
    pairs = []
    for x in (I, F):
        a = sum(succ[C][k] and not succ[x][k] for k in trials)
        b_ = sum(succ[x][k] and not succ[C][k] for k in trials)
        pairs.append((a, b_))
    return succ, pairs, bu


def part3b(runs, repo: Path, out: Out) -> None:
    f = "TOLERANCE.md"
    reps = {}
    for seed, folder in REPLAYS.items():
        rep = {}
        for m in MACHINES:
            for s in RESCORE_SUITES:
                p = repo / folder / f"{m}_{s}"
                if (p / "trials.csv").exists():
                    rep[(m, s)] = Run(p, connector_specs(repo))
        if rep:
            reps[seed] = rep
    if not reps:
        return
    seeds = [sd for sd in SEEDS if sd in reps]
    out.w(f, "## Exact rescoring from replays (seeds " + ", ".join(seeds) + ")", "",
          "POST HOC throughout. Every number in this section is a rescoring under tolerances that were not "
          "pre-registered. None replaces a pre-registered result. p-values are exact McNemar per seed, "
          "descriptive, never pooled across seeds (seeds 20261123 and 20261124 ran the v0.2d code 42df5c8, "
          "seed 20261130 the v0.2e code ddd0d34).", "",
          "`results/v0.2f_evidence/replay_<seed>/`: the conditions whose rows the old logs cannot rescore, "
          "replayed for C, F, I and J on the benchmark's own code plus a logging-only commit that adds five "
          "columns (`" + "`, `".join(NEW_COLS) + "`): 9197b9c on the v0.2e code for seed 20261130 (branch "
          "v0.2f/pack), its cherry-pick 22ef683 on 42df5c8 for the other two (branch v0.2f/replay-v02d). Each "
          "plan was written before its run (`RUN_PLAN.md` in replay_20261130 and replay_20261123).", "")
    # (1) identity with the committed rows
    out.w(f, "### (1) The replays reproduce the committed rows", "",
          "| Seed | Run | replayed conditions | rows | rows identical in every committed column but wall_time_s | "
          "differing cells | gt_seated recomputed exactly (as-run tolerances) | commit | dirty |",
          "|---|---|---|---|---|---|---|---|---|")
    allsame = allexact = allrows = 0
    drift_rows = {sd: [] for sd in seeds}
    for seed in seeds:
        tot_rows = tot_same = tot_exact = 0
        for (m, s), rr in reps[seed].items():
            old = runs[(seed, m, s)]
            assert rr.base_seed == seed
            same = diff_cells = exact = 0
            for r in rr.rows:
                o = old.by[(r["condition"], r["controller"], r["trial_index"])]
                d = sum(1 for k in o if k != "wall_time_s" and o[k] != r[k])
                same += d == 0
                diff_cells += d
                if d:
                    drift_rows[seed].append((m, s, r, o))
                cond = rr.cond[r["condition"]]
                exact += exact_seated(r, cond, rr.crit, rr.crit["depth_tolerance_mm"], rr.crit["max_tilt_deg"]) == \
                    (r["gt_seated"] == "True")
            n = len(rr.rows)
            tot_rows += n
            tot_same += same
            tot_exact += exact
            conds = sorted({r["condition"] for r in rr.rows})
            out.w(f, f"| {seed} | {m} {s} | {', '.join(conds)} | {n} | {same} | {diff_cells} | {exact} | "
                  f"{rr.commit[:7]} | {rr.dirty} |")
        out.k(f"replay seed {seed}: {tot_same} of {tot_rows} rows identical to the committed benchmark in every "
              f"column but wall_time_s; gt_seated recomputed exactly on {tot_exact} of {tot_rows} (TOLERANCE.md (1))")
        allsame += tot_same
        allexact += tot_exact
        allrows += tot_rows
    # The only tolerated differences: benchmark_v0.2d's disclosed limit (its PREREGISTRATION.md, "Known
    # limits"): on the arm's generalization_combined the fixture dynamics depended on the previous trial in
    # the same worker, so rows reproduce only to the last digits. v0.2e fixed it (seed 20261130 shows none).
    outcome_cols = ("success", "failure_reason", "gt_seated", "declared_success", "protective_stop", "timeout")
    for sd, lst in drift_rows.items():
        for m, s, r, o in lst:
            assert sd != "20261130" and (m, s, r["condition"]) == ("arm", "standard", "generalization_combined"), \
                (sd, m, s, r["condition"], r["controller"], r["trial_index"])
            assert all(o[k] == r[k] for k in outcome_cols)
    assert allexact == allrows, "gt_seated not recomputed exactly"
    for sd in seeds:
        lst = drift_rows[sd]
        if not lst:
            continue
        ctr = Counter(r["controller"] for _, _, r, _ in lst)
        pose = max(abs(float(o[k]) - float(r[k])) for _, _, r, o in lst
                   for k in ("final_depth_mm", "final_tilt_deg", "final_yaw_deg", "final_lateral_mm"))
        cyc = sum(o["cycle_time_s"] != r["cycle_time_s"] for _, _, r, o in lst)
        cmax = max(abs(float(o["cycle_time_s"]) - float(r["cycle_time_s"])) for _, _, r, o in lst)
        out.w(f, f"Seed {sd}: the rows that are not identical are all arm standard generalization_combined, "
              f"{', '.join(f'{L(c)} {n}' for c, n in sorted(ctr.items()))}. This is benchmark_v0.2d's disclosed "
              "reproducibility limit (its PREREGISTRATION.md: on that condition the arm's fixture dynamics depend "
              "on the previous trial in the same worker; fixed in v0.2e). Success, failure reason, gt_seated, "
              f"declared success, stop and timeout are identical on every one. The final pose differs by at most "
              f"{pose:.3g} (mm or deg), and the cycle time differs by at most {cmax * 1000:.0f} ms (rows: {cyc}).")
        out.k(f"replay seed {sd}: non-identical rows only on arm standard generalization_combined "
              f"({', '.join(f'{L(c)} {n}' for c, n in sorted(ctr.items()))}), outcome columns identical, pose drift "
              f"<= {pose:.3g}, the v0.2d code's disclosed limit (TOLERANCE.md (1))")
    out.w(f, "")
    out.w(f, "", "On seed 20261130, `dirty` is True for the five runs that started after the analysis files "
          "`experiments/v02f_evidence.py` and `tests/test_v02f_evidence.py` were edited during that replay "
          "(git_dirty counts any tracked change outside results/). Neither file is imported by the runner or "
          "the simulation; `git diff 2dc7009 -- . ':!results'` lists only those two files. The row identity "
          "above is the direct check.", "")

    # (2) the rule check
    out.w(f, "### (2) How every other row is rescored, and a check of that rule", "",
          "Rows in replayed conditions use the replayed values (`exact_seated`). All other rows use "
          "`logged_seated`: seated as run means the per-axis lateral, settled and latched checks passed, "
          "so only depth and angle decide; not seated as run with depth and angles passing means one of "
          "those checks failed, so the row stays unseated. Rows the rule cannot decide must all be in "
          "replayed conditions (asserted). Success = rescored seated and none of the logged outcome "
          "blockers (stop, penetration, damage, workspace limit, timeout, declared failure).", "",
          "| Seed | rule agrees with replay | cases settled only by the replay | undecided outside the replay |",
          "|---|---|---|---|")
    st = {}
    drift_note = []
    for seed in seeds:
        seated_t, (agree, disagree, und_in, und_out) = _rescore_seed(runs, reps[seed], seed)
        st[seed] = seated_t
        ratio = _drift_margin(drift_rows[seed], runs[(seed, "arm", "standard")])
        if ratio is not None:
            drift_note.append((seed, ratio))
        out.w(f, f"| {seed} | {agree} of {agree + disagree} | {und_in} | {und_out} |")
        out.k(f"rescoring rule check, seed {seed}: logged-columns rule agrees with the replay on {agree} of "
              f"{agree + disagree} (row, tolerance) cases; {und_in} settled only by the replay; {und_out} undecided "
              "outside it (TOLERANCE.md (2))")
        assert und_out == 0 and disagree == 0, f"rescoring incomplete on seed {seed}"
    out.w(f, "")
    for sd, (ratio, n) in drift_note:
        out.w(f, f"Seed {sd}: {n} of the drifted rows are cases the old columns cannot decide, so their rescoring "
              "uses replayed values from a trajectory that differs in the last digits. On every such (row, "
              "tolerance) case, the replayed depth, angles, per-axis offsets and speed sit at least "
              "(the per-axis drift is taken as the radius drift, which is all the old log shows) "
              f"{ratio:.1f} times that row's own pose drift away from the threshold, so the rescored outcome "
              "would be the same on the committed trajectory.", "")
        out.k(f"rescoring on drifted rows, seed {sd}: {n} undecided rows; threshold margin >= {ratio:.1f} x the row's "
              "pose drift (TOLERANCE.md (2))")
        assert ratio > 1.0

    # (3) full tables per seed
    out.w(f, "### (3) Rescored seated counts, C's lead and bad units, every seed (POST HOC)", "",
          "Good-part trials only: standard 2,000, heldout 500, latching good parts 600 per machine and seed. "
          "Yaw and tilt share one tolerance. Lateral margin and settled speed as run. Rows marked `as run` are "
          "the pre-registered scoring; the script checks them against the logged `success` and bad units. "
          "C-only / X-only are discordant pairs on the same trials, exact McNemar p on that seed only.", "",
          "| Seed | Machine | Suite | Depth tol (mm) | Yaw/tilt tol (deg) | Seated C / F / I / J | C-only / I-only (p) | "
          "C-only / F-only (p) | Bad units C / F / I / J |", "|---|---|---|---|---|---|---|---|---|")
    summ = {}
    for seed in seeds:
        for m in MACHINES:
            for s in RESCORE_SUITES:
                for dt in DEPTH_TOLS:
                    for at in ANGLE_TOLS:
                        succ, pairs, bu = _rescore_cell(runs, st[seed], seed, m, s, dt, at)
                        summ[(seed, m, s, dt, at)] = (pairs, bu)
                        tag = " (as run)" if (dt == 0.5 and at == 3.0) else ""
                        out.w(f, f"| {seed} | {m} | {s} | {dt}{tag} | {at}{tag} | "
                              + " / ".join(str(sum(succ[c].values())) for c in RESCORE_CTRLS) + " | "
                              + " | ".join(f"{a} / {b_} ({fp(mcnemar(a, b_))})" for a, b_ in pairs) + " | "
                              + " / ".join(str(bu[c]) for c in RESCORE_CTRLS) + " |")
                        if dt == 0.5:
                            out.k(f"POST HOC rescore, seed {seed}, {m} {s}, yaw/tilt {at} deg: seated C/F/I/J "
                                  + "/".join(str(sum(succ[c].values())) for c in RESCORE_CTRLS)
                                  + f"; C-only/I-only {pairs[0][0]}/{pairs[0][1]} (p {fp(mcnemar(*pairs[0]))}); "
                                  f"C-only/F-only {pairs[1][0]}/{pairs[1][1]}; bad units C/F/I/J "
                                  + "/".join(str(bu[c]) for c in RESCORE_CTRLS) + " (TOLERANCE.md (3))")
    out.w(f, "")

    # (4) the three-seed table
    out.w(f, "### (4) Three seeds side by side (POST HOC, depth tolerance 0.5 mm)", "",
          "Per seed: C-only / I-only (exact McNemar p on that seed), then bad units C / F / I / J. On housing-only "
          "suites F equals I. The 1.0 mm depth rows are in (3).", "",
          "| Machine | Suite | Yaw/tilt (deg) | " + " | ".join(f"{sd}: C-only / I-only (p) | {sd}: bad units C / F / I / J"
                                                      for sd in seeds) + " |",
          "|---|---|---|" + "---|---|" * len(seeds))
    for m in MACHINES:
        for s in RESCORE_SUITES:
            for at in ANGLE_TOLS:
                cells = []
                for sd in seeds:
                    pairs, bu = summ[(sd, m, s, 0.5, at)]
                    a, b_ = pairs[0]
                    cells += [f"{a} / {b_} ({fp(mcnemar(a, b_))})", " / ".join(str(bu[c]) for c in RESCORE_CTRLS)]
                tag = " (as run)" if at == 3.0 else ""
                out.w(f, f"| {m} | {s} | {at}{tag} | " + " | ".join(cells) + " |")
    out.w(f, "")

    # (5) the one-seed conclusions, checked on every seed
    def lead(sd, m, s, at, dt=0.5):
        a, b_ = summ[(sd, m, s, dt, at)][0][0]
        return a, b_, mcnemar(a, b_)

    out.w(f, "### (5) Which rescored findings hold on every seed (POST HOC)", "",
          "| Finding | " + " | ".join(seeds) + " | All |", "|---|" + "---|" * len(seeds) + "---|")

    def line(name, test, fmt):
        vals = [(test(sd), fmt(sd)) for sd in seeds]
        allv = all(v for v, _ in vals)
        out.w(f, f"| {name} | " + " | ".join(t for _, t in vals) + f" | {'yes' if allv else 'no'} |")
        out.k(f"POST HOC rescore, {name}: " + "; ".join(f"{sd} {t}" for sd, (_, t) in zip(seeds, vals))
              + f" -> {'holds on all' if allv else 'not on all'} (TOLERANCE.md (5))")

    def fl(sd, m, s, at):
        a, b_, p = lead(sd, m, s, at)
        return f"{a}/{b_}, p {fp(p)}"

    for at in (3.5, 4.0, 5.0):
        line(f"gantry standard: C ahead of I at {at} deg (C-only > I-only, p < 0.05)",
             lambda sd, at=at: lead(sd, "gantry", "standard", at)[0] > lead(sd, "gantry", "standard", at)[1]
             and lead(sd, "gantry", "standard", at)[2] < 0.05,
             lambda sd, at=at: fl(sd, "gantry", "standard", at))
    for at in (3.5, 4.0, 5.0):
        line(f"arm standard: C's lead over I not significant at {at} deg (p >= 0.05)",
             lambda sd, at=at: lead(sd, "arm", "standard", at)[2] >= 0.05,
             lambda sd, at=at: fl(sd, "arm", "standard", at))
    for m in MACHINES:
        line(f"{m} standard: C passes 0 bad units at 2.5-5 deg",
             lambda sd, m=m: all(summ[(sd, m, "standard", 0.5, at)][1][C] == 0 for at in ANGLE_TOLS if at >= 2.5),
             lambda sd, m=m: "/".join(str(summ[(sd, m, "standard", 0.5, at)][1][C]) for at in ANGLE_TOLS))
        line(f"{m} standard: I's bad units at 5 deg are under a fifth of those at 3 deg",
             lambda sd, m=m: summ[(sd, m, "standard", 0.5, 5.0)][1][I] * 5 < summ[(sd, m, "standard", 0.5, 3.0)][1][I],
             lambda sd, m=m: "/".join(str(summ[(sd, m, "standard", 0.5, at)][1][I]) for at in ANGLE_TOLS))
        line(f"{m} heldout: I has more discordant wins than C at 5 deg",
             lambda sd, m=m: lead(sd, m, "heldout", 5.0)[1] > lead(sd, m, "heldout", 5.0)[0],
             lambda sd, m=m: fl(sd, m, "heldout", 5.0))
        line(f"{m} standard: C's lead over I at 2 deg is larger than at 3 deg",
             lambda sd, m=m: lead(sd, m, "standard", 2.0)[0] - lead(sd, m, "standard", 2.0)[1]
             > lead(sd, m, "standard", 3.0)[0] - lead(sd, m, "standard", 3.0)[1],
             lambda sd, m=m: fl(sd, m, "standard", 2.0))
    maxd = max(abs(summ[(sd, m, s, 1.0, at)][1][c] - summ[(sd, m, s, 0.5, at)][1][c])
               for sd in seeds for m in MACHINES for s in RESCORE_SUITES for at in ANGLE_TOLS for c in RESCORE_CTRLS)
    out.w(f, "", f"Depth tolerance 1.0 mm against 0.5 mm: the largest change in any bad-unit count, over every seed, "
          f"cell, angle and controller, is {maxd}.", "")
    out.k(f"POST HOC rescore: 1.0 mm instead of 0.5 mm depth tolerance changes any bad-unit count by at most {maxd} "
          "(TOLERANCE.md (5))")


def part4(runs, out: Out) -> dict:
    f = "PHASES.md"
    out.w(f, "# Cycle time by phase, and the p95 / median ratio", "", HEADER, "",
          "Successful trials only (good parts), as the benchmark's cycle-time columns. Phases come from "
          "the `state` events in events.json.gz; the buckets are defined in `phase_times`. For each "
          "successful trial the summed phases equal `cycle_time_s` (largest gap printed below). On the "
          "housing-only suites I runs no pull and equals F; the pull test is the `verify` bucket of H "
          "and I on the latching suites (it includes the pull retry). C's `verify` on housing-only parts "
          "is the wall probe plus the tilt alignment (`seat_conform`) and yaw centring "
          "(`yaw_centering`, `wall_yaw` on the arm). Mean seconds per successful trial.", "")
    res = {}
    maxgap = 0.0
    for seed in SEEDS:
        for m in MACHINES:
            for s in SUITES:
                run = runs[(seed, m, s)]
                ev = run.events()
                for c in PHASE_CTRLS:
                    rs = [r for r in run.rows if r["controller"] == c and ok(r)]
                    acc = {b: [] for b in BUCKETS}
                    ct = []
                    retried = []
                    for r in rs:
                        p, gap = phase_times(ev[f"{r['condition']}|{c}|{r['trial_index']}"], float(r["cycle_time_s"]))
                        maxgap = max(maxgap, abs(gap))
                        for b in BUCKETS:
                            acc[b].append(p[b])
                        ct.append(float(r["cycle_time_s"]))
                        retried.append(p["retry"] > 0 or p["reinsert_after_verify"] > 0)
                    res[(seed, m, s, c)] = {"n": len(rs), "ct": np.array(ct), "acc": {b: np.array(v) for b, v in acc.items()},
                                            "retried": np.array(retried, dtype=bool), "rows": rs}
    out.w(f, f"Largest |sum of phases - cycle_time_s| over all successful trials: {maxgap:.2g} s.", "")

    out.w(f, "## (a) Mean seconds per phase, successful trials", "",
          "| Seed | Cell | Ctrl | n | median | p95 | approach | align/tare | first insert | retries | verify | "
          "re-insert after failed verify |", "|---|---|---|---|---|---|---|---|---|---|---|---|")
    for seed in SEEDS:
        for m in MACHINES:
            for s in SUITES:
                for c in PHASE_CTRLS:
                    x = res[(seed, m, s, c)]
                    out.w(f, f"| {seed} | {m} {s} | {L(c)} | {x['n']} | {pct(x['ct'], 50):.2f} | {pct(x['ct'], 95):.2f} | "
                          + " | ".join(f"{x['acc'][b].mean():.2f}" for b in BUCKETS) + " |")
    out.w(f, "")

    out.w(f, "## (b) Time cost of C's VERIFY, the pull test, and C's extra insertion time", "",
          "`insertion` = align/tare + first insert + retries (+ re-insert after a failed verify). "
          "C - F columns are differences of means over each controller's own successful trials (not "
          "paired).", "",
          "| Seed | Cell | C verify | J verify | I verify (pull) | H verify (pull) | C insertion | F insertion | "
          "C - F insertion | of which first insert | of which retries | C - F total (mean) |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|")
    for seed in SEEDS:
        for m in MACHINES:
            for s in SUITES:
                g = lambda c, b: res[(seed, m, s, c)]["acc"][b].mean()  # noqa: E731
                ins = lambda c: g(c, "align") + g(c, "first_insert") + g(c, "retry") + g(c, "reinsert_after_verify")  # noqa: E731
                dc = ins(C) - ins(F)
                d1 = g(C, "first_insert") - g(F, "first_insert")
                dr = (g(C, "retry") + g(C, "reinsert_after_verify")) - (g(F, "retry") + g(F, "reinsert_after_verify"))
                dt = res[(seed, m, s, C)]["ct"].mean() - res[(seed, m, s, F)]["ct"].mean()
                out.w(f, f"| {seed} | {m} {s} | {g(C, 'verify'):.2f} | {g(J, 'verify'):.2f} | {g(I, 'verify'):.2f} | "
                      f"{g(H, 'verify'):.2f} | {ins(C):.2f} | {ins(F):.2f} | {dc:+.2f} | {d1:+.2f} | {dr:+.2f} | {dt:+.2f} |")
                if seed == "20261130" and s in ("standard", "latching"):
                    out.k(f"seed 20261130, {m} {s}, mean s per successful trial: C verify {g(C, 'verify'):.2f}, "
                          f"J verify {g(J, 'verify'):.2f}, I pull {g(I, 'verify'):.2f}; C insertion {ins(C):.2f} vs F "
                          f"{ins(F):.2f} ({dc:+.2f}: first insert {d1:+.2f}, retries {dr:+.2f}); C - F mean cycle "
                          f"{dt:+.2f} (PHASES.md (b))")
    out.w(f, "")

    # (c) p95/median for every controller and run
    out.w(f, "## (c) p95 / median of successful cycle time, every controller and run (W6 target <= 1.5)", "",
          "Over all successful trials of the run, as `checkpoint_report`'s cycle column.", "")
    for seed in SEEDS:
        out.w(f, f"### seed {seed}", "", "| Ctrl | " + " | ".join(f"{m} {s}" for m in MACHINES for s in SUITES) + " |",
              "|---" * 9 + "|")
        for c in ORDER10:
            cells = []
            for m in MACHINES:
                for s in SUITES:
                    ct = [float(r["cycle_time_s"]) for r in runs[(seed, m, s)].rows if r["controller"] == c and ok(r)]
                    cells.append(f"{pct(ct, 95) / pct(ct, 50):.2f}" if ct else "n/a")
            out.w(f, f"| {L(c)} {c} | " + " | ".join(cells) + " |")
            if c in (C, F, I, J) and seed == "20261130":
                out.k(f"seed 20261130, p95/median, {L(c)}, " + ", ".join(
                    f"{m} {s} {v}" for (m, s), v in zip([(m, s) for m in MACHINES for s in SUITES], cells))
                      + " (PHASES.md (c))")
        out.w(f, "")

    # (d) C's slow trials
    out.w(f, "## (d) C's slowest successful trials", "",
          "`slow` = successful cycle above 1.5 x the run's median (the W6 target line). `retried` = the "
          "trial spent time in a retry or a re-insert after a failed verify. The last column is the "
          "p95 / median ratio over C's successful trials that never retried, with their count.", "",
          "| Seed | Cell | median | p95 | p95/median | successes | retried | slow | slow and retried | "
          "mean retry s on slow | slow by condition (top 5) | no-retry p95/median (n) |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|")
    for seed in SEEDS:
        for m in MACHINES:
            for s in SUITES:
                x = res[(seed, m, s, C)]
                med, p95 = pct(x["ct"], 50), pct(x["ct"], 95)
                slow = x["ct"] > 1.5 * med
                rt = x["acc"]["retry"] + x["acc"]["reinsert_after_verify"]
                conds = Counter(r["condition"] for r, sl in zip(x["rows"], slow) if sl)
                nr = x["ct"][~x["retried"]]
                out.w(f, f"| {seed} | {m} {s} | {med:.2f} | {p95:.2f} | {p95 / med:.2f} | {x['n']} | {int(x['retried'].sum())} | "
                      f"{int(slow.sum())} | {int((slow & x['retried']).sum())} | "
                      f"{rt[slow].mean() if slow.any() else 0:.2f} | "
                      + ", ".join(f"{k} {v}" for k, v in conds.most_common(5))
                      + f" | {pct(nr, 95) / med:.2f} ({len(nr)}) |")
                if seed == "20261130" and s in ("standard", "latching"):
                    out.k(f"seed 20261130, {m} {s}, C: median {med:.2f} s, p95 {p95:.2f} s ({p95 / med:.2f}x); "
                          f"{int(x['retried'].sum())} of {x['n']} successes retried; {int(slow.sum())} above 1.5x median, "
                          f"{int((slow & x['retried']).sum())} of them retried; no-retry p95/median {pct(nr, 95) / med:.2f} "
                          "(PHASES.md (d))")
    out.w(f, "")

    # (d2) C's wins over I, against C's slow trials
    out.w(f, "## (d2) C's wins over I on standard, and C's slow trials", "",
          "Trials C seats and I does not, on standard: how many C seated only after a retry, their median "
          "cycle, and how many of C's slow trials (above 1.5 x median) they are.", "",
          "| Seed | Machine | C-only vs I | of them retried | their median cycle (s) | of them slow | "
          "C's slow trials | C's retried successes in noise_1mm, noise_2mm, generalization_combined |",
          "|---|---|---|---|---|---|---|---|")
    for seed in SEEDS:
        for m in MACHINES:
            run = runs[(seed, m, "standard")]
            x = res[(seed, m, "standard", C)]
            med = pct(x["ct"], 50)
            _, _, keys = discordant(run, run.good_conds(), C, I)
            kset = set(keys)
            idx = [i for i, r in enumerate(x["rows"]) if (r["condition"], r["trial_index"]) in kset]
            rt = x["retried"][idx]
            cts = x["ct"][idx]
            slow = x["ct"] > 1.5 * med
            rnoisy = sum(1 for r, rr in zip(x["rows"], x["retried"]) if rr and r["condition"] in NOISY)
            out.w(f, f"| {seed} | {m} | {len(idx)} | {int(rt.sum())} | {pct(cts, 50):.2f} | {int((cts > 1.5 * med).sum())} | "
                  f"{int(slow.sum())} | {rnoisy} of {int(x['retried'].sum())} |")
            out.k(f"standard, seed {seed}, {m}: of C's {len(idx)} wins over I, {int(rt.sum())} retried, median "
                  f"{pct(cts, 50):.2f} s vs C's median {med:.2f} s, {int((cts > 1.5 * med).sum())} of C's {int(slow.sum())} "
                  f"slow trials; {rnoisy} of C's {int(x['retried'].sum())} retried successes are in the 3 noisy "
                  "conditions (PHASES.md (d2), post hoc)")
    out.w(f, "")

    # (e) C's failures: what they cost in time
    out.w(f, "## (e) C's unsuccessful good-part trials: reason and time", "",
          "These do not enter the cycle-time percentiles but take cell time (and so throughput).", "",
          "| Seed | Cell | n failed | reasons | mean time (s) |", "|---|---|---|---|---|")
    for seed in SEEDS:
        for m in MACHINES:
            for s in SUITES:
                run = runs[(seed, m, s)]
                fl = [r for r in run.rows if r["controller"] == C and not ok(r) and run.good(r["condition"])]
                if not fl:
                    continue
                rc = Counter(r["failure_reason"] for r in fl)
                out.w(f, f"| {seed} | {m} {s} | {len(fl)} | {dict(rc.most_common())} | "
                      f"{np.mean([float(r['cycle_time_s']) for r in fl]):.2f} |")
    out.w(f, "")
    return res


def part5(runs, out: Out) -> None:
    f = "SEEDS.md"
    out.w(f, "# The same comparisons on each seed", "", HEADER, "",
          "Different seeds, not paired across seeds. No p-value is pooled across seeds, because "
          "v0.2d and v0.2e ran different code. `Direction` says whether the sign of (C-only - X-only) "
          "is the same on all three seeds.", "")
    out.w(f, "## (a) Seated good parts, C against each controller, per cell", "",
          "| Cell | X | 20261123: C-only / X-only (p) | 20261124 | 20261130 | Direction |", "|---|---|---|---|---|---|")
    for m in MACHINES:
        for s in SUITES:
            for x in VS_C + (G,):
                ps, txt = [], []
                for seed in SEEDS:
                    run = runs[(seed, m, s)]
                    a, b, _ = discordant(run, run.good_conds(), C, x)
                    ps.append((a, b))
                    txt.append(f"{a} / {b} ({fp(mcnemar(a, b))})")
                out.w(f, f"| {m} {s} | {L(x)} | " + " | ".join(txt) + f" | {direction(ps)} |")
                if x in (I, F) or (x == G):
                    out.k(f"{m} {s}, C-only/{L(x)}-only per seed: " + "; ".join(txt) + f"; {direction(ps)} (SEEDS.md (a))")
    out.w(f, "")
    out.w(f, "## (b) Seated good parts per controller, per cell and seed", "",
          "| Cell | Ctrl | 20261123 | 20261124 | 20261130 |", "|---|---|---|---|---|")
    for m in MACHINES:
        for s in SUITES:
            for c in (C, G, J, I, F, H, D):
                cells = []
                for seed in SEEDS:
                    run = runs[(seed, m, s)]
                    rs = [r for r in run.rows if r["controller"] == c and run.good(r["condition"])]
                    cells.append(f"{sum(ok(r) for r in rs)} / {len(rs)} ({100 * sum(ok(r) for r in rs) / len(rs):.1f}%)")
                out.w(f, f"| {m} {s} | {L(c)} | " + " | ".join(cells) + " |")
    out.w(f, "")
    out.w(f, "## (c) Which findings hold in the same direction on all three seeds", "",
          "Each line is checked on every seed by the script; `yes` means it holds on all three. POST HOC: "
          "every line was chosen after the benchmark results were seen, and the thresholds in the first "
          "lines (90%, half) were set by the writer; they describe, they do not test.", "",
          "| Finding | 20261123 | 20261124 | 20261130 | All three |", "|---|---|---|---|---|")

    def line(name, vals):
        allv = all(v[0] for v in vals)
        out.w(f, f"| {name} | " + " | ".join(v[1] for v in vals) + f" | {'yes' if allv else 'no'} |")
        out.k(f"{name}: " + "; ".join(v[1] for v in vals) + f" -> {'holds on all 3' if allv else 'not on all 3'} (SEEDS.md (c))")

    for m in MACHINES:
        vals = []
        for seed in SEEDS:
            run = runs[(seed, m, "standard")]
            conds = run.good_conds()
            a, b, keys = discordant(run, conds, C, I)
            inn = sum(1 for cd, _ in keys if cd in NOISY)
            vals.append((a > b and inn >= 0.9 * a, f"{inn}/{a}"))
        line(f"{m} standard: >= 90% of C's wins over I in noise_1mm, noise_2mm, generalization_combined (post hoc)", vals)
        vals = []
        for seed in SEEDS:
            run = runs[(seed, m, "standard")]
            xs = [r for r in run.rows if r["controller"] == I and bad_unit(r)]
            inn = sum(1 for r in xs if r["condition"] in NOISY)
            vals.append((inn == len(xs), f"{inn}/{len(xs)}"))
        line(f"{m} standard: all of I's bad units in those three conditions (post hoc)", vals)
        vals = []
        for seed in SEEDS:
            run = runs[(seed, m, "standard")]
            _, _, keys = discordant(run, run.good_conds(), C, I)
            nb = sum(1 for cd, ti in keys if bad_unit(run.by[(cd, I, ti)]))
            vals.append((len(keys) > 0 and nb >= 0.5 * len(keys), f"{nb}/{len(keys)}"))
        line(f"{m} standard: at least half of C's wins over I are I bad units", vals)
        vals = []
        for seed in SEEDS:
            run = runs[(seed, m, "standard")]
            a, b, _ = discordant(run, run.good_conds(), J, F)
            bj = sum(bad_unit(r) for r in run.rows if r["controller"] == J)
            bf = sum(bad_unit(r) for r in run.rows if r["controller"] == F)
            vals.append((a > b and bj < bf, f"J/F {a}/{b}, bad {bj} vs {bf}"))
        line(f"{m} standard: J (F + C's VERIFY) seats more than F and passes fewer bad units", vals)
        vals = []
        for seed in SEEDS:
            run = runs[(seed, m, "standard")]
            a, b, _ = discordant(run, run.good_conds(), C, J)
            vals.append((a > b, f"C/J {a}/{b}"))
        line(f"{m} standard: C seats more than J (same VERIFY, different insertion)", vals)
        vals = []
        for seed in SEEDS:
            run = runs[(seed, m, "heldout")]
            per = {cd: discordant(run, (cd,), C, I)[:2] for cd in run.good_conds()}
            a, b = per["heldout_worst_case"]
            vals.append((b > a, f"{a}/{b}"))
        line(f"{m} heldout_worst_case: I seats more than C (C-only/I-only)", vals)
        vals = []
        for seed in SEEDS:
            run = runs[(seed, m, "heldout")]
            a, b = discordant(run, ("heldout_handeye_bias_1.5mm",), C, I)[:2]
            vals.append((b > a, f"{a}/{b}"))
        line(f"{m} heldout_handeye_bias_1.5mm: I seats more than C (C-only/I-only)", vals)
    for m in MACHINES:
        vals = []
        for seed in SEEDS:
            run = runs[(seed, m, "standard")]
            a, b = discordant(run, ("friction_1",), C, I)[:2]
            vals.append((b > a, f"{a}/{b}"))
        line(f"{m} standard friction_1: I seats more than C (C-only/I-only)", vals)
    vals = []
    for seed in SEEDS:
        n = sum(1 for m in MACHINES for s in SUITES for r in runs[(seed, m, s)].rows
                if r["controller"] == C and bad_unit(r))
        vals.append((n == 0, str(n)))
    line("C passes no bad unit and no bad part (all eight runs)", vals)
    vals = []
    for seed in SEEDS:
        ratios = []
        for m in MACHINES:
            for s in SUITES:
                ct = [float(r["cycle_time_s"]) for r in runs[(seed, m, s)].rows if r["controller"] == C and ok(r)]
                ratios.append(pct(ct, 95) / pct(ct, 50))
        vals.append((min(ratios) > 1.5, f"{min(ratios):.2f}-{max(ratios):.2f}"))
    line("C's p95/median above 1.5 on every run", vals)
    vals = []
    for seed in SEEDS:
        good, txt = [], []
        for m in MACHINES:
            run = runs[(seed, m, "standard")]
            u = {c: uph([r for r in run.rows if r["controller"] == c], STOP_RESET_S) for c in (C, F)}
            good.append(u[C] < u[F])
            txt.append(f"{m} {u[C]:.0f} vs {u[F]:.0f}")
        vals.append((all(good), ", ".join(txt)))
    line("C makes fewer good units per hour than F on standard, both machines (60 s per protective stop)", vals)
    out.w(f, "")


def checkpoint_table(runs, out: Out) -> None:
    f = "CHECKPOINT_TABLE.md"
    seed = "20261130"
    out.w(f, "# Checkpoint table, seed 20261130 (benchmark_v0.2e, v0.2e code ddd0d34)", "", HEADER, "",
          "Seated = success on standard (2,000 trials per machine). p95 and good units per hour (60 s "
          "per protective stop) on standard. Bad parts passed: latching + latch_spread, both machines. "
          "Bad units: every good-part trial of the eight runs. Protective stops: all trials of the eight "
          "runs.", "",
          "| Ctrl | Seated, gantry std | Seated, arm std | p95 cycle s, gantry / arm std | good units/h, "
          "gantry / arm std | Bad parts passed | Bad units | Protective stops |", "|---|---|---|---|---|---|---|---|")
    for c in ORDER10:
        cells = []
        for m in MACHINES:
            rs = [r for r in runs[(seed, m, "standard")].rows if r["controller"] == c]
            cells.append(f"{100 * sum(ok(r) for r in rs) / len(rs):.1f}%")
        p95, upht = [], []
        for m in MACHINES:
            rs = [r for r in runs[(seed, m, "standard")].rows if r["controller"] == c]
            p95.append(f"{pct([float(r['cycle_time_s']) for r in rs if ok(r)], 95):.2f}")
            upht.append(f"{uph(rs, STOP_RESET_S):.0f}")
        allr = [(runs[(seed, m, s)], r) for m in MACHINES for s in SUITES for r in runs[(seed, m, s)].rows
                if r["controller"] == c]
        nbp = sum(1 for run, r in allr if not run.good(r["condition"]))
        bp = sum(1 for run, r in allr if not run.good(r["condition"]) and bad_unit(r))
        ng = sum(1 for run, r in allr if run.good(r["condition"]))
        bu = sum(1 for run, r in allr if run.good(r["condition"]) and bad_unit(r))
        ps = sum(stop(r) for _, r in allr)
        psg = sum(stop(r) for run, r in allr if run.good(r["condition"]))
        declares = c not in ("fixed", "correction", "correction_rcc")
        bpt = f"{bp} / {nbp}" if declares else f"n/a ({nbp} trials)"
        but = f"{bu} / {ng}" if declares else "n/a"
        out.w(f, f"| {L(c)} {c} | {cells[0]} | {cells[1]} | {' / '.join(p95)} | {' / '.join(upht)} | {bpt} | {but} | "
              f"{ps} / {len(allr)} ({psg} on good parts, {ps - psg} on bad) |")
        out.k(f"checkpoint, seed 20261130, {L(c)}: seated gantry std {cells[0]}, arm std {cells[1]}; p95 {'/'.join(p95)} s; "
              f"units/h at 60 s per stop {'/'.join(upht)}; bad parts {bpt}; bad units {but}; stops {ps} ({psg} good, {ps - psg} bad) "
              "(CHECKPOINT_TABLE.md)")
    out.w(f, "", "A, B and E do not declare success or failure, so bad parts passed and bad units do not apply.", "")
    for c in (C, F, I, J):
        st = Counter(f"{m} {r['condition']}" for m in MACHINES for s in SUITES
                     for r in runs[(seed, m, s)].ctrl_rows[c] if stop(r))
        line = ", ".join(f"{k} {v}" for k, v in st.most_common())
        out.w(f, f"{L(c)}'s protective stops by machine and condition: {line or 'none'}.", "")
        out.k(f"seed 20261130, {L(c)} protective stops by condition: {line or 'none'} (CHECKPOINT_TABLE.md)")


def v01_numbers(repo: Path, out: Out) -> None:
    rs = [r for r in csv.DictReader((repo / "results/benchmark_v0.1/trials.csv").open()) if r["controller"] == C]
    ct = [float(r["cycle_time_s"]) for r in rs if ok(r)]
    out.k(f"benchmark_v0.1 (seed 20261025), C: {sum(ok(r) for r in rs)}/{len(rs)} seated, median {pct(ct, 50):.2f} s, "
          f"p95 {pct(ct, 95):.2f} s ({pct(ct, 95) / pct(ct, 50):.2f}x), max {max(ct):.2f} s over successes and "
          f"{max(float(r['cycle_time_s']) for r in rs):.2f} s over all trials, stops {sum(stop(r) for r in rs)}, "
          f"bad units {sum(bad_unit(r) for r in rs)}, good units/h {uph(rs, STOP_RESET_S):.0f} "
          "(results/benchmark_v0.1/trials.csv)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="results/v0.2f_evidence")
    ap.add_argument("--repo", default=".")
    args = ap.parse_args()
    repo = Path(args.repo)
    outdir = repo / args.out
    outdir.mkdir(parents=True, exist_ok=True)
    runs = load_all(repo)
    for (seed, m, s), run in runs.items():
        assert not run.dirty, (seed, m, s)
    out = Out()
    part1(runs, out)
    stats = part1_concentration(runs, out)
    part1_losses(runs, stats, out)
    part1_verify(runs, out)
    part2(runs, out, outdir)
    part3(runs, out)
    part3b(runs, repo, out)
    part4(runs, out)
    part5(runs, out)
    checkpoint_table(runs, out)
    v01_numbers(repo, out)
    for name, lines in out.files.items():
        (outdir / name).write_text("\n".join(lines) + "\n")
    (outdir / "KEY_NUMBERS.md").write_text(
        "# Key numbers\n\n" + HEADER + "\n\nEvery number quoted in this folder's REPORT.md and CHECKPOINT_REPORT.md (not results/v0.2f_checkpoint/CHECKPOINT_REPORT.md), "
        "with the table it comes from.\n\n" + "\n".join(f"- {k}" for k in out.key) + "\n")


if __name__ == "__main__":
    main()
