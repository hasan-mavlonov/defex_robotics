"""v0.2d: tables for controller J (F + C's verify) from the development and validation runs.

    python -m experiments.v02d_j_tables results/v0.2d_j_verify > results/v0.2d_j_verify/TABLES.md

Expects <root>/<run>/<backend>_<suite>/trials.csv and events.json.gz, run = dev2026, dev2027, val4003.
Every number is recomputed from the per-trial rows and event logs.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from defex.config import SuccessCriteria
from defex.logging.metrics import STOP_RESET_S
from experiments.checkpoint_report import escape, false_reject, fmt_p, mcnemar, ok, stop, uph, wilson

C, F, I = "adaptive", "spiral_rcc", "spiral_rcc_pull"
JA, JB = "spiral_rcc_verify_reject", "spiral_rcc_verify_research"
CANDIDATES = (JA, JB)
J0 = "spiral_rcc_verify_reject_no_rcc"
NAME = {C: "C", F: "F", I: "I", JA: "J(a) reject", JB: "J(b) re-search", J0: "J(a) without the RCC terms",
        "spiral_rcc_verify": "J"}
SHOWN = (C, F, I, JA, JB, J0)
SUITES = ("standard", "latching", "heldout", "latch_spread")
MACHINES = ("gantry", "arm")
DEPTH_MM = {"standard": 15.0, "heldout": 15.0, "latching": 8.0, "latch_spread": 8.0}
CLEARANCE_MM = {"standard": 0.5, "heldout": 0.5, "latching": 0.15, "latch_spread": 0.15}


def good(r: dict) -> bool:
    return r["group"] != "bad_part"


def load_run(folder: Path) -> dict[tuple[str, str], list[dict]]:
    out = {}
    for m in MACHINES:
        for s in SUITES:
            p = folder / f"{m}_{s}" / "trials.csv"
            if p.exists():
                with p.open() as fh:
                    out[(m, s)] = list(csv.DictReader(fh))
    return out


def load_events(folder: Path, m: str, s: str) -> dict[str, list]:
    p = folder / f"{m}_{s}" / "events.json.gz"
    if not p.exists():
        return {}
    with gzip.open(p, "rt") as fh:
        return json.load(fh)


def stats(rows: list[dict], ctrl: str) -> dict:
    rs = [r for r in rows if r["controller"] == ctrl]
    g = [r for r in rs if good(r)]
    b = [r for r in rs if not good(r)]
    ct = [float(r["cycle_time_s"]) for r in g if ok(r)]
    return {
        "n": len(g), "ok": sum(ok(r) for r in g), "esc": sum(escape(r) for r in g),
        "bad_n": len(b), "bad_esc": sum(escape(r) for r in b), "fr": sum(false_reject(r) for r in g),
        "stops": sum(stop(r) for r in g), "bad_stops": sum(stop(r) for r in b),
        "cycle": float(np.median(ct)) if ct else float("nan"), "cycles": ct,
        "uph": uph(g, STOP_RESET_S) if g else float("nan"),
    }


def main_table(runs: dict[str, dict], title: str, ctrls=SHOWN) -> list[str]:
    out = [f"\n### {title}\n",
           "| Machine, suite | Controller | Good parts seated | Bad units passed (good parts) | Bad parts passed | "
           "False rejects | Protective stops (good / bad parts) | Median good cycle (s) | Good units/h (60 s per stop) |",
           "|---|---|---|---|---|---|---|---|---|"]
    for m in MACHINES:
        for s in SUITES:
            rows = [r for run in runs.values() for r in run.get((m, s), [])]
            if not rows:
                continue
            for c in ctrls:
                x = stats(rows, c)
                if not x["n"]:
                    continue
                bad = f"{x['bad_esc']}/{x['bad_n']}" if x["bad_n"] else "n/a"
                stops = f"{x['stops']} / {x['bad_stops']}" if x["bad_n"] else f"{x['stops']}"
                out.append(f"| {m}, {s} | {NAME[c]} | {x['ok']}/{x['n']} ({100 * x['ok'] / x['n']:.1f}%) | {x['esc']} | "
                           f"{bad} | {x['fr']} | {stops} | {x['cycle']:.2f} | {x['uph']:.0f} |")
    return out


def totals_table(runs: dict[str, dict], title: str, ctrls=SHOWN) -> list[str]:
    out = [f"\n### {title}\n",
           "| Machine | Controller | Good parts seated | Bad units passed (good parts) | Bad parts passed | False rejects | "
           "Protective stops (good parts) | Median good cycle (s) | Good units/h (60 s per stop) |",
           "|---|---|---|---|---|---|---|---|---|"]
    for m in MACHINES + ("both",):
        rows = [r for run in runs.values() for (mm, _), rs in run.items() if m in ("both", mm) for r in rs]
        for c in ctrls:
            x = stats(rows, c)
            if not x["n"]:
                continue
            esc_hi = 100 * wilson(x["esc"], x["n"])[1]
            out.append(f"| {m} | {NAME[c]} | {x['ok']}/{x['n']} ({100 * x['ok'] / x['n']:.1f}%) | {x['esc']} "
                       f"(<= {esc_hi:.2f}%) | {x['bad_esc']}/{x['bad_n']} | {x['fr']} | {x['stops']} | {x['cycle']:.2f} | "
                       f"{x['uph']:.0f} |")
    return out


def selection(run: dict, label: str) -> list[str]:
    """The committed rule (SELECTION_RULE.md): fewer bad units passed, then more good parts seated, then lower
    median good cycle; all machines and suites pooled; equal at every step: (a)."""
    rows = [r for rs in run.values() for r in rs]
    x = {c: stats(rows, c) for c in CANDIDATES}
    if not all(x[c]["n"] for c in CANDIDATES):
        return []
    key = {c: (x[c]["esc"] + x[c]["bad_esc"], -x[c]["ok"], x[c]["cycle"]) for c in CANDIDATES}
    pick = JB if key[JB] < key[JA] else JA
    step = next((i for i in range(3) if key[JA][i] != key[JB][i]), None)
    why = ["fewer bad units passed", "more good parts seated", "lower median good cycle"][step] if step is not None \
        else "equal at every step: (a)"
    out = [f"\n### Selection rule, {label}\n",
           "| Candidate | Bad units passed (good-part escapes + bad parts passed) | Good parts seated | "
           "Median good cycle (s) | Good units/h (60 s per stop) |", "|---|---|---|---|---|"]
    for c in CANDIDATES:
        out.append(f"| {NAME[c]} | {x[c]['esc'] + x[c]['bad_esc']} ({x[c]['esc']} + {x[c]['bad_esc']}) | "
                   f"{x[c]['ok']}/{x[c]['n']} | {x[c]['cycle']:.3f} | {x[c]['uph']:.0f} |")
    out.append(f"\nRule outcome: **{NAME[pick]}** ({why}).")
    return out


def paired_rows(rows: list[dict], a: str, b: str, keep) -> list[tuple[dict, dict]]:
    idx = {(r["controller"], r["condition"], r["trial_index"]): r for r in rows}
    return [(r, idx[(b, r["condition"], r["trial_index"])]) for r in rows
            if r["controller"] == a and keep(r) and (b, r["condition"], r["trial_index"]) in idx]


def paired_table(runs: dict[str, dict], j: str, title: str) -> list[str]:
    out = [f"\n### {title}\n",
           "| Machine, suite | J vs | Good-part pairs | Seated J / other | J-only / other-only | McNemar p | "
           "Bad units passed (good parts) J / other | discordant | p | Bad parts passed J / other | discordant | p |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in MACHINES + ("both",):
        for s in SUITES + ("all",):
            if (m == "both") != (s == "all"):
                continue
            rows = [r for run in runs.values() for (mm, ss), rs in run.items()
                    if m in ("both", mm) and s in ("all", ss) for r in rs]
            if not rows:
                continue
            for other in (C, I):
                g = paired_rows(rows, j, other, good)
                b = paired_rows(rows, j, other, lambda r: not good(r))
                if not g:
                    continue
                jo = sum(ok(x) and not ok(y) for x, y in g)
                oo = sum(ok(y) and not ok(x) for x, y in g)
                ej = sum(escape(x) and not escape(y) for x, y in g)
                eo = sum(escape(y) and not escape(x) for x, y in g)
                bad = "n/a | | "
                if b:
                    bj = sum(escape(x) and not escape(y) for x, y in b)
                    bo = sum(escape(y) and not escape(x) for x, y in b)
                    bad = (f"{sum(escape(x) for x, _ in b)} / {sum(escape(y) for _, y in b)} of {len(b)} | {bj} / {bo} | "
                           f"{fmt_p(mcnemar(bj, bo))}")
                out.append(f"| {m}, {s} | {NAME[other]} | {len(g)} | {sum(ok(x) for x, _ in g)} / {sum(ok(y) for _, y in g)} | "
                           f"{jo} / {oo} | {fmt_p(mcnemar(jo, oo))} | {sum(escape(x) for x, _ in g)} / "
                           f"{sum(escape(y) for _, y in g)} | {ej} / {eo} | {fmt_p(mcnemar(ej, eo))} | {bad} |")
    return out


def failed_criteria(r: dict, suite: str) -> list[str]:
    crit = SuccessCriteria()
    out = []
    if float(r["final_depth_mm"]) < DEPTH_MM[suite] - crit.depth_tolerance_mm:
        out.append("depth")
    if float(r["final_tilt_deg"]) > crit.max_tilt_deg:
        out.append("tilt")
    if abs(float(r["final_yaw_deg"])) > crit.max_yaw_deg:
        out.append("yaw")
    if float(r["final_lateral_mm"]) > CLEARANCE_MM[suite] + crit.lateral_margin_mm:
        out.append("lateral")
    return out or ["none of depth/tilt/yaw/lateral (latch or per-axis lateral)"]


def escape_table(runs: dict[str, dict], ctrls=SHOWN) -> list[str]:
    out = ["\n### Bad units passed on good-part trials, by the criterion they fail (seeds pooled)\n",
           "A unit can fail more than one criterion. Lateral is checked here on the offset's norm "
           "(the run checks each axis).\n",
           "| Machine | Controller | Escapes | depth | tilt | yaw | lateral | other | Conditions |", "|---|---|---|---|---|---|---|---|---|"]
    for m in MACHINES:
        for c in ctrls:
            esc = [(s, r) for run in runs.values() for (mm, s), rs in run.items() if mm == m
                   for r in rs if r["controller"] == c and good(r) and escape(r)]
            k = Counter()
            for s, r in esc:
                for f in failed_criteria(r, s):
                    k[f if f in ("depth", "tilt", "yaw", "lateral") else "other"] += 1
            conds = Counter(r["condition"] for _, r in esc)
            top = ", ".join(f"{cd} {n}" for cd, n in conds.most_common(4))
            out.append(f"| {m} | {NAME[c]} | {len(esc)} | {k['depth']} | {k['tilt']} | {k['yaw']} | {k['lateral']} | "
                       f"{k['other']} | {top} |")
    return out


def reasons_table(runs: dict[str, dict], ctrls=SHOWN) -> list[str]:
    """Why each controller's failed trials failed (seeds pooled), good parts and bad parts apart."""
    out = ["\n### Failure reasons (seeds pooled)\n", "| Machine | Controller | Parts | Failed | Reasons (count) |",
           "|---|---|---|---|---|"]
    for m in MACHINES:
        for c in ctrls:
            for label, keep in (("good", good), ("bad", lambda r: not good(r))):
                rs = [r for run in runs.values() for (mm, _), rows in run.items() if mm == m for r in rows
                      if r["controller"] == c and keep(r) and not ok(r)]
                if rs:
                    top = ", ".join(f"{k} {n}" for k, n in Counter(r["failure_reason"] for r in rs).most_common(6))
                    out.append(f"| {m} | {NAME[c]} | {label} | {len(rs)} | {top} |")
    return out


def handover_check(root: Path, runs: list[str]) -> list[str]:
    """J is F up to the handover: on every trial F declared seated, J's events up to F's "seated" equal F's
    and J hands over at F's finish time; where F never declared seated, J's row equals F's."""
    out = ["\n### J before the handover is F\n",
           "| Run | Machine, suite | Candidate | F declared seated: J's events equal F's up to it, handover at F's finish | "
           "F never declared seated: J's row equals F's (all fields but controller and wall time) |",
           "|---|---|---|---|---|"]
    for run in runs:
        folder = root / run
        data = load_run(folder)
        for (m, s), rows in data.items():
            ev = load_events(folder, m, s)
            idx = {(r["controller"], r["condition"], r["trial_index"]): r for r in rows}
            for j in CANDIDATES + (J0,):
                seated, seated_ok, never, never_ok = 0, 0, 0, 0
                for (c, cd, i), fr in idx.items():
                    if c != F or (j, cd, i) not in idx:
                        continue
                    fe, je = ev[f"{cd}|{F}|{i}"], ev[f"{cd}|{j}|{i}"]
                    if fr["declared_success"] == "True":
                        seated += 1
                        k = max(n for n, e in enumerate(fe) if e[1] == "seated")
                        fin = [e for e in fe if e[1] == "finish"][0][0]
                        hand = next((e for e in je[k + 1:k + 2] if e[1] == "verify_handover"), None)
                        seated_ok += je[:k + 1] == fe[:k + 1] and hand is not None and hand[0] == fin
                    else:
                        never += 1
                        jr = idx[(j, cd, i)]
                        same = all(jr[f] == fr[f] for f in fr if f not in ("controller", "wall_time_s"))
                        never_ok += same and je == fe
                out.append(f"| {run} | {m}, {s} | {NAME[j]} | {seated_ok}/{seated} | {never_ok}/{never} |")
    return out


def verify_outcomes(root: Path, runs: list[str]) -> list[str]:
    """What C's VERIFY did inside J: handovers, checks failed, and the arm's wall-yaw readings."""
    out = ["\n### What VERIFY did inside J (seeds pooled)\n",
           "| Machine, suite | Candidate | Trials | Handovers | Trials with a failed check | ... then seated (good parts) | "
           "Retries after a failed check | Wall-yaw PASS / FAIL | Yaw centrings |", "|---|---|---|---|---|---|---|---|---|"]
    half = defaultdict(list)
    for m in MACHINES:
        for s in SUITES:
            for j in CANDIDATES + (J0,):
                tr = hand = failed = rescued = retries = wy_pass = wy_fail = yc = 0
                for run in runs:
                    folder = root / run
                    rows = {(r["condition"], r["trial_index"]): r for r in load_run(folder).get((m, s), [])
                            if r["controller"] == j}
                    if not rows:
                        continue
                    ev = load_events(folder, m, s)
                    for (cd, i), r in rows.items():
                        e = ev[f"{cd}|{j}|{i}"]
                        tr += 1
                        h = sum(x[1] == "verify_handover" for x in e)
                        hand += h
                        n_fail = sum(x[1] == "abort" and x[2] == "verify_failed" or
                                     x[1] == "retry" and x[2].startswith("verify_failed") for x in e)
                        failed += n_fail > 0
                        rescued += n_fail > 0 and good(r) and ok(r)
                        retries += sum(x[1] == "retry" and x[2].startswith("verify_failed") for x in e)
                        for x in e:
                            if x[1] == "wall_yaw" and x[2].endswith("PASS"):
                                wy_pass += 1
                                half[(m, j)].append(float(x[2].split("half free travel ")[1].split(" mm")[0]))
                            elif x[1] == "wall_yaw" and x[2].endswith("FAIL"):
                                wy_fail += 1
                            yc += x[1] == "yaw_centering"
                if tr:
                    out.append(f"| {m}, {s} | {NAME[j]} | {tr} | {hand} | {failed} | {rescued} | {retries} | "
                               f"{wy_pass} / {wy_fail} | {yc} |")
    for (m, c) in [(m, C) for m in MACHINES]:
        for run in runs:
            folder = root / run
            for s in SUITES:
                ev = load_events(folder, m, s)
                for k, e in ev.items():
                    if k.split("|")[1] == c:
                        half[(m, c)] += [float(x[2].split("half free travel ")[1].split(" mm")[0])
                                         for x in e if x[1] == "wall_yaw" and x[2].endswith("PASS")]
    out += ["", "Half free travel between the walls on wall-yaw passes (mm, encoder positions at the two wall "
                "contacts; C on the stiff wrist, J through the RCC stage):", "",
            "| Machine | Controller | Passes | p5 | median | p95 |", "|---|---|---|---|---|---|"]
    for (m, c), v in sorted(half.items()):
        if v:
            q = np.percentile(v, [5, 50, 95])
            out.append(f"| {m} | {NAME[c]} | {len(v)} | {q[0]:.3f} | {q[1]:.3f} | {q[2]:.3f} |")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--pick", default="", help="the candidate SELECTION_RULE.md picked, shown as J")
    args = ap.parse_args()
    root = args.root
    runs = {r: load_run(root / r) for r in ("dev2026", "dev2027", "val4003") if (root / r).exists()}
    lines = [f"# Tables for {root.name}", "",
             f"Generated by `python -m experiments.v02d_j_tables {root}` from the per-trial rows and event logs. "
             "Bad units passed = failed and neither stopped nor declared failed (defex.logging.metrics.is_escape). "
             "False rejects = seated in ground truth but declared failed. Good units per hour over good-part "
             f"trials, {STOP_RESET_S:.0f} s per protective stop. Exact McNemar on paired trials."]
    if args.pick:
        lines.append(f"\nJ = {NAME[args.pick]} (`{args.pick}`), the candidate the selection rule picked.")
    for label, run in (("dev seed 2026 (ranks the candidates)", "dev2026"), ("validation seed 4003", "val4003")):
        if run in runs:
            lines += selection(runs[run], label)
    dev = {k: v for k, v in runs.items() if k.startswith("dev")}
    lines.append("\n## Development seeds 2026 and 2027, pooled")
    lines += totals_table(dev, "Totals over the four suites")
    lines += main_table(dev, "Per machine and suite")
    for j in CANDIDATES:
        lines += paired_table(dev, j, f"Paired, {NAME[j]} against C and I (seeds pooled)")
    lines += escape_table(dev)
    lines += reasons_table(dev)
    for run in sorted(runs):
        lines.append(f"\n## {run}")
        lines += totals_table({run: runs[run]}, f"Totals, {run}")
        lines += main_table({run: runs[run]}, f"Per machine and suite, {run}")
    lines += handover_check(root, sorted(runs))
    lines += verify_outcomes(root, sorted(dev))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
