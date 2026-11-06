"""v0.2f tilt diagnosis: a candidate's rows against the flags-off rows of the same trials (results/v0.2f_tilt_diagnosis/RULE.md).

    python experiments/v02f_tilt_compare.py --base runs/arm_latch_cg.jsonl.gz,... --cand runs/fix_P_arm.jsonl.gz,... \\
        --bound 3 --name P

Trials missing from --cand are taken as unchanged (the re-run shortcut of the rule); the control trials in --cand
must then be identical to the base. Prints a Markdown section; exit status 0 either way.
"""

from __future__ import annotations

import argparse
import gzip
import json
from collections import Counter, defaultdict

IGNORE = {"wall_time_s", "checks", "seats", "ev"}
LABEL = {"adaptive": "C", "adaptive_learned": "G", "spiral_rcc_verify": "J"}


def load(paths: str) -> dict:
    rows = {}
    for p in paths.split(","):
        with gzip.open(p, "rt") as fh:
            for line in fh:
                r = json.loads(line)
                rows[(r["backend"], r["suite"], r["condition"], r["controller"], r["base_seed"], r["trial_index"])] = r
    return rows


def metrics(r: dict) -> Counter:
    good = r["group"] != "bad_part"
    c = Counter()
    if good:
        c["good"] += 1
        c["good_rejected"] += not r["success"]
        c["bad_unit"] += bool(r["declared_success"]) and not r["success"] and not r["protective_stop"]
    else:
        c["bad_part"] += 1
        c["bad_passed"] += bool(r["declared_success"])
    c["stop"] += bool(r["protective_stop"])
    c["verdicts"] += sum(x["verdict"] in ("PASS", "FAIL") for x in r["checks"])
    c["tilt_fail"] += sum(x["verdict"] == "FAIL" for x in r["checks"])
    return c


def outcome(r):
    if r["success"]:
        return "seated"
    if r["declared_success"] and not r["protective_stop"]:
        return "BAD UNIT" if r["group"] != "bad_part" else "BAD PART PASSED"
    return r["failure_reason"] or "failed"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--cand", required=True)
    ap.add_argument("--bound", type=int, required=True)
    ap.add_argument("--name", required=True)
    args = ap.parse_args()
    base, cand = load(args.base), load(args.cand)
    if not set(cand) <= set(base):
        raise SystemExit(f"{len(set(cand) - set(base))} candidate trials not in the base")
    cells = defaultdict(lambda: [Counter(), Counter()])
    changed, cycle = [], []
    for k, b in base.items():
        a = cand.get(k, b)
        cell = (k[0], LABEL[k[3]])
        cells[cell][0].update(metrics(b))
        cells[cell][1].update(metrics(a))
        diff = [f for f in b if f not in IGNORE and b[f] != a[f]]
        if diff:
            changed.append((k, b, a, diff))
            if b["success"] and a["success"]:
                cycle.append(a["cycle_time_s"] - b["cycle_time_s"])
    out = [f"### Candidate {args.name}", "",
           f"Base trials {len(base)}, re-run {len(cand)}, rows changed {len(changed)}.", "",
           "| Machine | Ctrl | Good-part trials | Rejected base / cand | Bad units base / cand | Bad parts | Passed base / cand | Stops base / cand | Tilt verdicts base / cand | Tilt FAILs base / cand |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    tot = [Counter(), Counter()]
    for cell, (b, a) in sorted(cells.items()):
        tot[0].update(b)
        tot[1].update(a)
        out.append(f"| {cell[0]} | {cell[1]} | {b['good']} | {b['good_rejected']} / {a['good_rejected']} | "
                   f"{b['bad_unit']} / {a['bad_unit']} | {b['bad_part']} | {b['bad_passed']} / {a['bad_passed']} | "
                   f"{b['stop']} / {a['stop']} | {b['verdicts']} / {a['verdicts']} | {b['tilt_fail']} / {a['tilt_fail']} |")
    b, a = tot
    added_bu = sum(max(0, cells[c][1]["bad_unit"] - cells[c][0]["bad_unit"]) for c in cells)
    added_bp = sum(max(0, cells[c][1]["bad_passed"] - cells[c][0]["bad_passed"]) for c in cells)
    rej = a["good_rejected"] - b["good_rejected"]
    stops = a["stop"] - b["stop"]
    keep = added_bu == 0 and added_bp == 0 and rej <= args.bound and stops <= args.bound
    out += ["", f"- Bad units added (any cell): {added_bu}; bad parts passed added: {added_bp}.",
            f"- Net good-part rejections added: {rej} (bound {args.bound}); net protective stops added: {stops} "
            f"(bound {args.bound}).",
            f"- Bad units removed: {b['bad_unit'] - a['bad_unit'] + added_bu}.",
            f"- Cycle time change on trials seated both ways (s): "
            + (f"n {len(cycle)}, mean {sum(cycle) / len(cycle):+.3f}, max {max(cycle):+.3f}" if cycle else "none"),
            f"- **Rule verdict: {'KEEP' if keep else 'DROP'}**", "", "Changed trials:", ""]
    for k, b, a, diff in changed:
        out.append(f"- {k[0]} {LABEL[k[3]]} seed {k[4]} {k[2]} {k[5]}: {outcome(b)} -> {outcome(a)} "
                   f"(final tilt {b['final_tilt_deg']:.2f} -> {a['final_tilt_deg']:.2f}; fields {len(diff)})")
    if not changed:
        out.append("- none")
    print("\n".join(out))


if __name__ == "__main__":
    main()
