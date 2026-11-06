"""H and I pull retry, rule version 4 (before) against version 5 (after), dev seeds 2026 and 2027 (v0.2e).

python -m experiments.v02e_pull_retry_tables > results/v0.2e_pull_retry/TABLES.md

Before: results/v0.2d_pull_retry/dev4 (H and I code as at 966a5f5). After: results/v0.2e_pull_retry/after.
Identity: results/v0.2e_pull_retry/identity/{before,after} (all ten controllers, seed 2027, 2 trials).
"""

from __future__ import annotations

import gzip
import json
from collections import Counter
from pathlib import Path
from statistics import median

from experiments.checkpoint_report import escape, fmt_p, load, mcnemar, ok, stop

ROOT = Path("results")
BEFORE = ROOT / "v0.2d_pull_retry/dev4"
AFTER = ROOT / "v0.2e_pull_retry/after"
IDENT = ROOT / "v0.2e_pull_retry/identity"
MACHINES = ("gantry", "arm")
SUITES = ("latching", "latch_spread")
SEEDS = (2026, 2027)
HI = {"spiral_pull": "H", "spiral_rcc_pull": "I"}
LETTER = {"fixed": "A", "correction": "B", "adaptive": "C", "spiral": "D", "correction_rcc": "E", "spiral_rcc": "F",
          "adaptive_learned": "G", "spiral_pull": "H", "spiral_rcc_pull": "I", "spiral_rcc_verify": "J"}
IGNORE = {"wall_time_s"}


def key(seed: int, r: dict) -> tuple:
    return seed, r["controller"], r["condition"], r["trial_index"]


def events(folder: Path) -> dict[str, list]:
    with gzip.open(folder / "events.json.gz", "rt") as fh:
        return json.load(fh)


def cell(root: Path, m: str, suites=SUITES, seeds=SEEDS) -> tuple[dict, dict]:
    rows, evs = {}, {}
    for s in suites:
        for seed in seeds:
            f = root / f"{m}_{s}_s{seed}"
            for r in load(f):
                rows[key(seed, r)] = r
            for k, v in events(f).items():
                cond, ctrl, i = k.split("|")
                evs[(seed, ctrl, cond, i)] = v
    return rows, evs


def retry_stats(ev: list) -> Counter:
    """Re-pushes and how each ended: pulled again, rejected by the v5 gate, or aborted on a limit."""
    c = Counter()
    t0 = None
    seated = False
    for t, kind, det in ev:
        if kind == "seated":
            seated = True
        elif kind == "protective_stop" and seated:
            c["stop_in_check"] += 1
        if kind == "retry" and det.startswith("pull failed"):
            c["repush"] += 1
            t0 = t
        elif t0 is not None and kind == "verify" and det.startswith("re-push"):
            if det.endswith("pull again"):
                c["pulled_again"] += 1
            elif "short of the seat depth" in det:
                c["gate_depth"] += 1
            elif "not held" in det:
                c["gate_not_held"] += 1
            t0 = None
        elif t0 is not None and kind == "abort":
            c["abort_" + det] += 1
            if det == "excess_lateral_force" and t - t0 <= 0.05:
                c["lateral_50ms"] += 1
            t0 = None
    return c


def diff_rows(a: dict, b: dict, keys) -> int:
    return sum(any(a[k][f] != b[k][f] for f in a[k] if f not in IGNORE) for k in keys)


def stats(R: dict, E: dict, keys: list) -> dict:
    good = [k for k in keys if R[k]["group"] != "bad_part"]
    bad = [k for k in keys if R[k]["group"] == "bad_part"]
    rc = Counter()
    for k in keys:
        rc += retry_stats(E[k])
    cyc = [float(R[k]["cycle_time_s"]) for k in good if ok(R[k])]
    return {
        "good": good, "bad": bad,
        "seated": sum(ok(R[k]) for k in good),
        "esc_good": sum(escape(R[k]) for k in good),
        "esc_bad": sum(escape(R[k]) for k in bad),
        "stop_good": sum(stop(R[k]) for k in good), "stop_bad": sum(stop(R[k]) for k in bad),
        "retry_trials": sum(int(R[k]["retries"]) > 0 for k in keys),
        "retries": sum(int(R[k]["retries"]) for k in keys),
        "cyc": median(cyc) if cyc else float("nan"),
        "rc": rc,
    }


def main() -> None:
    out = ["# v0.2e pull retry: H and I, rule version 4 (before) against version 5 (after)", "",
           f"Before: `{BEFORE}` (run at 1f1ca4a; H and I code as at 966a5f5). After: `{AFTER}`. "
           "Dev seeds 2026 and 2027, latching and latch_spread suites, 20 trials per condition and seed. "
           "Good parts: every condition outside the `bad_part` group. Bad units on good parts and bad parts "
           "passed are escapes (not seated as required, no stop, not declared failed).", ""]
    hdr = ("| Machine | Suite | Ctrl | Rows differ | Good seated before -> after | Lost / gained (p) | "
           "Bad units on good parts | Bad parts passed | Stops good+bad | Trials with a retry (retries) | "
           "Median good cycle (s) |")
    sep = "|---|---|---|---|---|---|---|---|---|---|---|"
    out += ["## Outcomes", "", hdr, sep]
    rc_rows, fails, cvs = [], Counter(), []
    for m in MACHINES:
        for suites, label in [((s,), s) for s in SUITES] + [(SUITES, "both")]:
            B, EB = cell(BEFORE, m, suites)
            A, EA = cell(AFTER, m, suites)
            for ctrl, L in HI.items():
                keys = sorted(k for k in A if k[1] == ctrl)
                assert set(keys) == {k for k in B if k[1] == ctrl}
                b, a = stats(B, EB, keys), stats(A, EA, keys)
                lost = sum(ok(B[k]) and not ok(A[k]) for k in b["good"])
                gain = sum(ok(A[k]) and not ok(B[k]) for k in b["good"])
                row = (f"| {m} | {label} | {L} | {diff_rows(A, B, keys)} | {b['seated']} -> {a['seated']} of "
                       f"{len(b['good'])} | {lost} / {gain} ({fmt_p(mcnemar(lost, gain))}) | {b['esc_good']} -> "
                       f"{a['esc_good']} | {b['esc_bad']} -> {a['esc_bad']} of {len(b['bad'])} | "
                       f"{b['stop_good']}+{b['stop_bad']} -> {a['stop_good']}+{a['stop_bad']} | "
                       f"{b['retry_trials']} ({b['retries']}) -> {a['retry_trials']} ({a['retries']}) | "
                       f"{b['cyc']:.2f} -> {a['cyc']:.2f} |")
                out.append(row if label != "both" else row.replace(f"| {label} |", "| **both** |"))
                if label == "both":
                    rc_rows.append((m, L, b["rc"], a["rc"]))
                    for k in a["good"]:
                        if not ok(A[k]):
                            fails[(m, L, k[2], A[k]["failure_reason"])] += 1
                    cg = {k: (k[0], "adaptive") + k[2:] for k in a["good"]}
                    x = sum(ok(A[cg[k]]) and not ok(A[k]) for k in a["good"])
                    y = sum(ok(A[k]) and not ok(A[cg[k]]) for k in a["good"])
                    xb = sum(ok(A[cg[k]]) and not ok(B[k]) for k in a["good"])
                    yb = sum(ok(B[k]) and not ok(A[cg[k]]) for k in a["good"])
                    cbad = [(k[0], "adaptive") + k[2:] for k in a["bad"]]
                    cvs.append((m, L, sum(ok(A[k]) for k in cg.values()), len(cg), xb, yb, x, y,
                                sum(escape(A[k]) for k in cbad), sum(stop(A[k]) for k in cbad) +
                                sum(stop(A[k]) for k in cg.values())))
    out += ["", "## Re-pushes (H and I, both suites, both seeds)", "",
            "A re-push follows every failed first pull. It ends one of three ways: pull again (v4: always, "
            "unless a force limit trips), rejected by the v5 gate (re-push did not hold 0.8 x 35.2 N, or "
            "held short of INSERT's seat depth), or aborted on a force limit during the re-push.", "",
            "| Machine | Ctrl | Re-pushes before -> after | Pulled again | Gate: short of seat depth | "
            "Gate: not held | Aborted on lateral force (within 50 ms) | Aborted on other limits | "
            "Protective stops in the latch check (after INSERT's seat) |", "|---|---|---|---|---|---|---|---|---|"]
    for m, L, b, a in rc_rows:
        oth = lambda c: sum(v for k, v in c.items() if k.startswith("abort_") and k != "abort_excess_lateral_force")  # noqa: E731
        out.append(f"| {m} | {L} | {b['repush']} -> {a['repush']} | {b['pulled_again']} -> {a['pulled_again']} | "
                   f"{b['gate_depth']} -> {a['gate_depth']} | {b['gate_not_held']} -> {a['gate_not_held']} | "
                   f"{b['abort_excess_lateral_force']} ({b['lateral_50ms']}) -> {a['abort_excess_lateral_force']} "
                   f"({a['lateral_50ms']}) | {oth(b)} -> {oth(a)} | {b['stop_in_check']} -> {a['stop_in_check']} |")
    out += ["", "## C against H and I on good parts (both suites, both seeds, paired by trial)", "",
            "C's rows are from the after run (C's code is unchanged; see the identity check).", "",
            "| Machine | Ctrl | C good seated | C-only / other-only, before (p) | C-only / other-only, after (p) | "
            "C bad parts passed | C stops |", "|---|---|---|---|---|---|---|"]
    for m, L, cs, n, xb, yb, x, y, cesc, cst in cvs:
        out.append(f"| {m} | {L} | {cs} of {n} | {xb} / {yb} ({fmt_p(mcnemar(xb, yb))}) | {x} / {y} "
                   f"({fmt_p(mcnemar(x, y))}) | {cesc} | {cst} |")
    out += ["", "## H and I good-part failures after (v5)", "", "| Machine | Ctrl | Condition | Reason | Trials |",
            "|---|---|---|---|---|"]
    out += ["| " + " | ".join(k) + f" | {n} |" for k, n in sorted(fails.items())]
    out += identity()
    print("\n".join(out))


def identity() -> list[str]:
    out = ["", "## Identity check (seed 2027, 2 trials per condition, all ten controllers)", "",
           "`identity/before` at 966a5f5, `identity/after` at the v5 code. Rows compared on every field but "
           "wall time; events compared as logged. H and I before are also compared with `dev4` "
           "(same seed, conditions, trial indices 0-1).", "",
           "| Machine | Suite | Ctrl | Trials | Rows differ | Event logs differ | H/I before vs dev4: rows differ |",
           "|---|---|---|---|---|---|---|"]
    for m in MACHINES:
        for s in SUITES:
            f = f"{m}_{s}_s2027"
            B = {key(2027, r): r for r in load(IDENT / "before" / f)}
            A = {key(2027, r): r for r in load(IDENT / "after" / f)}
            EB, EA = events(IDENT / "before" / f), events(IDENT / "after" / f)
            D = {key(2027, r): r for r in load(BEFORE / f)}
            for ctrl in LETTER:
                keys = sorted(k for k in A if k[1] == ctrl)
                assert set(keys) == {k for k in B if k[1] == ctrl}
                ev = sum(EA[f"{k[2]}|{k[1]}|{k[3]}"] != EB[f"{k[2]}|{k[1]}|{k[3]}"] for k in keys)
                dev4 = str(diff_rows(B, D, keys)) if ctrl in HI else ""
                out.append(f"| {m} | {s} | {LETTER[ctrl]} | {len(keys)} | {diff_rows(A, B, keys)} | {ev} | {dev4} |")
    return out


if __name__ == "__main__":
    main()
