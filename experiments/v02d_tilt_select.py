"""v0.2d tilt check: which trials a candidate acts on, and the selection tables (results/v0.2d_tilt_check).

    python -m experiments.v02d_tilt_select fired --variants results/v0.2d_tilt_check/variants.json \\
        --out 'reruns_{backend}.json' base1.jsonl.gz base2.jsonl.gz
    python -m experiments.v02d_tilt_select table --variants results/v0.2d_tilt_check/variants.json \\
        --base base1.jsonl.gz,base2.jsonl.gz --reruns rerun.jsonl.gz [--candidates tilt_k1]

Inputs are files written by ``experiments.v02d_tilt_features``. The base files come from C and G with the
check off; they hold the check's evidence at every start of a latch check. A candidate changes a trial only
from the first latch check where its verdict fails (the evidence is a pure function and a passing verdict
changes no state), so every trial where it never fails is the base trial, and the trials where it does are
re-run with the candidate switched on (``fired`` writes that list, plus every trial with a latch check whose
evidence was not recorded). ``table`` combines the two, checks that no needed re-run is missing, and applies
the gates of SELECTION_RULE.md.
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
from pathlib import Path

MAX_TILT_DEG = 3.0  # SuccessCriteria.max_tilt_deg
SUITE_ORDER = ("latching", "latch_spread", "standard", "heldout")
EQUAL_FIELDS = ("success", "failure_reason", "declared_success", "cycle_time_s", "retries", "final_depth_mm",
                "final_tilt_deg", "final_lateral_mm", "final_yaw_deg", "peak_contact_force_n", "sim_time_s")


def load(paths: list[str]) -> list[dict]:
    rows = []
    for p in paths:
        with gzip.open(p, "rt") as fh:
            rows += [json.loads(line) for line in fh]
    return rows


def latch_checks(row: dict) -> list[dict]:
    rec = row["record"]
    if "latch_checks" in rec:
        return rec["latch_checks"]
    return [c for v in rec.get("verifies", []) for c in v.get("latch_checks", [])]


def observed(row: dict) -> bool:
    """Every latch check of the trial has its evidence recorded (one "latch ... click" event per check).

    The collector of 91bfd9a recorded a latch check only inside a VERIFY entered through _begin_verify, so a
    check after a held re-seat in an attempt without one was missed; such trials are re-run like fired ones."""
    n = sum(1 for e in row["events"] if e[1] == "latch" and e[2].startswith("click"))
    return n == len(latch_checks(row))


def fires(row: dict, cand: dict) -> bool:
    """True if the candidate's verdict fails at some latch-check start of this base trial."""
    return any(c["tilt_deg"] > cand["tilt_check_deg"] and c["edge"] > cand["tilt_check_edge_fraction"]
               for c in latch_checks(row))


def needs_rerun(row: dict, cand: dict) -> bool:
    return fires(row, cand) or not observed(row)


def acted(row: dict) -> bool:
    return any(e[1] == "tilt" and e[2].endswith("FAIL") for e in row["events"])


def key(row: dict, controller: str | None = None) -> tuple:
    return (row["backend"], row["suite"], row["condition"], controller or row["controller"], row["base_seed"],
            row["trial_index"])


def outcome(row: dict) -> dict:
    good = row["group"] != "bad_part"
    declared = row["declared_success"] is True
    escape = declared and not row["gt_seated"] and not row["protective_stop"]
    return {
        "good": good,
        "success": bool(row["success"]),
        "false_reject": bool(row["gt_seated"] and row["declared_success"] is False),
        "tilt_escape": escape and good and row["final_tilt_deg"] > MAX_TILT_DEG,
        "other_escape": escape and good and row["final_tilt_deg"] <= MAX_TILT_DEG,
        "bad_passed": declared and not good,
        "stop": bool(row["protective_stop"]),
        "cycle": float(row["cycle_time_s"]),
    }


def cmd_fired(args) -> None:
    variants = json.loads(Path(args.variants).read_text())
    names = args.candidates.split(",") if args.candidates else list(variants)
    by_backend: dict[str, list] = {}
    for row in load(args.files):
        if "@" in row["controller"]:
            continue
        for k in names:
            if needs_rerun(row, variants[k]):
                by_backend.setdefault(row["backend"], []).append(
                    [row["suite"], row["condition"], f"{row['controller']}@{k}", row["base_seed"], row["trial_index"]])
    for backend in ("gantry", "arm"):
        entries = by_backend.get(backend, [])
        path = Path(args.out.format(backend=backend))
        path.write_text(json.dumps(entries))
        print(f"{backend}: {len(entries)} re-runs -> {path}")


def cell_name(k: tuple) -> tuple:
    return (k[0], k[1], k[3].split("@")[0])


def cmd_table(args) -> None:
    variants = json.loads(Path(args.variants).read_text())
    names = args.candidates.split(",") if args.candidates else list(variants)
    base = {key(r): r for r in load(args.base.split(",")) if "@" not in r["controller"]}
    reruns = {key(r): r for r in load(args.reruns.split(","))} if args.reruns else {}
    out = []
    totals = {}
    for k in names:
        cells: dict[tuple, dict] = {}
        fired = 0
        for bk, br in base.items():
            fk = bk[:3] + (f"{bk[3]}@{k}",) + bk[4:]
            if needs_rerun(br, variants[k]):
                if fk not in reruns:
                    raise SystemExit(f"missing re-run {fk}")
                kr = reruns[fk]
                if not acted(kr):
                    # The check passed every time: the re-run must be the base trial, field for field.
                    same = [f for f in EQUAL_FIELDS if kr[f] != br[f]]
                    if fires(br, variants[k]) or same:
                        raise SystemExit(f"re-run {fk} differs from its base trial without a failed check: {same}")
                    kr = br
            else:
                kr = br
            fired += int(kr is not br)
            b, c = outcome(br), outcome(kr)
            cell = cells.setdefault(cell_name(bk), {f: [0, 0] for f in (
                "n_good", "n_bad", "success", "lost", "gained", "false_reject", "tilt_escape", "other_escape",
                "bad_passed", "stop", "fired")})
            cell["n_good" if b["good"] else "n_bad"][0] += 1
            cell["fired"][0] += int(kr is not br)
            for f in ("success", "false_reject", "tilt_escape", "other_escape", "bad_passed", "stop"):
                if f == "success" and not b["good"]:
                    continue
                cell[f][0] += int(b[f])
                cell[f][1] += int(c[f])
            if b["good"]:
                cell["lost"][0] += int(b["success"] and not c["success"])
                cell["gained"][0] += int(c["success"] and not b["success"])
        totals[k] = (cells, fired)
    for k in names:
        cells, fired = totals[k]
        cand = variants[k]
        out.append(f"### Candidate {k}: tilt > {cand['tilt_check_deg']} deg and CoP > "
                   f"{cand['tilt_check_edge_fraction']} of the half-width ({fired} trials acted on)\n")
        out.append("| Machine | Suite | Ctrl | Good trials | Seated base / check (lost, gained) | False rejects | "
                   "Tilt escapes | Other escapes | Bad parts passed | Stops | Acted on |")
        out.append("|---|---|---|---|---|---|---|---|---|---|---|")
        order = sorted(cells, key=lambda c: (c[0], SUITE_ORDER.index(c[1]) if c[1] in SUITE_ORDER else 9, c[2]))
        for c in order:
            s = cells[c]
            out.append(f"| {c[0]} | {c[1]} | {'G' if c[2] == 'adaptive_learned' else 'C'} | {s['n_good'][0]} | "
                       f"{s['success'][0]} / {s['success'][1]} ({s['lost'][0]}, {s['gained'][0]}) | "
                       f"{s['false_reject'][0]} / {s['false_reject'][1]} | {s['tilt_escape'][0]} / {s['tilt_escape'][1]} | "
                       f"{s['other_escape'][0]} / {s['other_escape'][1]} | {s['bad_passed'][0]} / {s['bad_passed'][1]} | "
                       f"{s['stop'][0]} / {s['stop'][1]} | {s['fired'][0]} |")
        out.append("")
    out.append("### Gates (SELECTION_RULE.md)\n")
    first = "V1 not more tilt escapes" if args.validation else "G1 removes half"
    out.append(f"| Candidate | Tilt escapes base / check | {first} | Net good lost (allowed) | G2 cost | "
               "G3 false rejects | G4 no new bad passes, escapes, stops | Passes |")
    out.append("|---|---|---|---|---|---|---|---|")
    passing = []
    for k in names:
        cells, fired = totals[k]
        t0 = sum(s["tilt_escape"][0] for s in cells.values())
        t1 = sum(s["tilt_escape"][1] for s in cells.values())
        removed = t0 - t1
        g1 = t0 > 0 and removed >= max(1, math.ceil(t0 / 2))
        net = sum(s["lost"][0] - s["gained"][0] for s in cells.values())
        allowed = 2 * max(removed, 1 if args.validation else 0)
        per_cell_ok = all(s["lost"][0] - s["gained"][0] <= max(2, math.floor(0.01 * s["n_good"][0])) for s in cells.values())
        g2 = net <= allowed and per_cell_ok
        g3 = all(s["false_reject"][1] - s["false_reject"][0] <= max(2, math.floor(0.01 * s["n_good"][0]))
                 for s in cells.values())
        g4 = all(s["bad_passed"][1] <= s["bad_passed"][0] and s["other_escape"][1] <= s["other_escape"][0]
                 and s["stop"][1] - s["stop"][0] <= 1 for s in cells.values())
        if args.validation:
            g1 = t1 <= t0
        ok = g1 and g2 and g3 and g4
        if ok:
            passing.append((t1, net, fired, k))
        out.append(f"| {k} | {t0} / {t1} | {'yes' if g1 else 'no'} | {net} ({allowed}) | {'yes' if g2 else 'no'} | "
                   f"{'yes' if g3 else 'no'} | {'yes' if g4 else 'no'} | {'yes' if ok else 'no'} |")
    out.append("")
    if args.validation:
        out.append(f"Validation verdict: {'GO' if passing else 'NO-GO'}")
    else:
        pick = min(passing)[3] if passing else None
        out.append(f"Selected: {pick or 'none (the check is not installed)'}")
    print("\n".join(out))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fired")
    f.add_argument("files", nargs="+")
    f.add_argument("--variants", required=True)
    f.add_argument("--candidates", default="")
    f.add_argument("--out", required=True, help="path with {backend}: one jobs file per machine")
    t = sub.add_parser("table")
    t.add_argument("--variants", required=True)
    t.add_argument("--base", required=True)
    t.add_argument("--reruns", default="")
    t.add_argument("--candidates", default="")
    t.add_argument("--validation", action="store_true", help="the go/no-go gates (SELECTION_RULE.md, validation)")
    args = ap.parse_args()
    {"fired": cmd_fired, "table": cmd_table}[args.cmd](args)


if __name__ == "__main__":
    main()
