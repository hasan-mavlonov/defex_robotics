"""v0.2f: baselines with and without C's gentle-retract cap, paired (results/v0.2f_baseline_retract_cap/RULE.md).

    python -m experiments.v02f_retract_cap_compare results/v0.2f_baseline_retract_cap/dev [--suffix @cap]

Reads every <run>/*/trials.csv and events.json.gz under the folder. Each folder holds a controller X and its
capped twin X<suffix> on the same trials. Per pair: success on good parts, latches torn (final_latch_intact
False), bad units passed on good parts, bad parts passed (checkpoint_report.escape), cap trips (a
"gentle_retract" event) and rows that differ in a trial without a trip. Writes TABLES.md and trips.csv into
the folder and prints the rule's verdict.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path

from experiments.checkpoint_report import LETTER, escape, load, ok

BASE = ("spiral", "spiral_rcc", "spiral_pull", "spiral_rcc_pull", "spiral_rcc_verify")
SKIP = {"controller", "wall_time_s"}
MAX_SUCCESS_LOSS = 2


def torn(r: dict) -> bool:
    return r.get("final_latch_intact") == "False"


def _run_meta(folder: Path) -> tuple[str, str, str]:
    cfg = json.loads((folder / "config.json").read_text())
    suite = folder.name.rsplit("_s", 1)[0].split("_", 1)[1]
    return cfg["backend"], suite, str(cfg["base_seed"])


def compare(root: Path, suffix: str) -> tuple[list[str], bool]:
    cells: dict[tuple, dict] = defaultdict(lambda: defaultdict(int))
    trips, failures = [], []
    for folder in sorted(p.parent for p in root.glob("*/trials.csv")):
        backend, suite, seed = _run_meta(folder)
        rows = load(folder)
        with gzip.open(folder / "events.json.gz", "rt") as fh:
            events = json.load(fh)
        idx = {(r["controller"], r["condition"], r["trial_index"]): r for r in rows}
        for (ctrl, cond, i), u in idx.items():
            if ctrl not in BASE or (ctrl + suffix, cond, i) not in idx:
                continue
            k = idx[(ctrl + suffix, cond, i)]
            gk = [e for e in events[f"{cond}|{ctrl + suffix}|{i}"] if e[1] == "gentle_retract"]
            gu = [e for e in events[f"{cond}|{ctrl}|{i}"] if e[1] == "gentle_retract"]
            # J's VERIFY is C's code and logs C's own gentle retract in both: a trip is an event only k has.
            gentle = gk[len(gu):] if gk[:len(gu)] == gu else gk
            good = u["group"] != "bad_part"
            cell = cells[(backend, suite, ctrl)]
            cell["trials"] += 1
            cell["tripped"] += bool(gentle)
            if good:
                cell["good"] += 1
                cell["ok_u"] += ok(u)
                cell["ok_k"] += ok(k)
                cell["ok_gain"] += ok(k) and not ok(u)
                cell["ok_loss"] += ok(u) and not ok(k)
                cell["unit_u"] += escape(u)
                cell["unit_k"] += escape(k)
                cell["unit_new"] += escape(k) and not escape(u)
            else:
                cell["badpart_u"] += escape(u)
                cell["badpart_k"] += escape(k)
                cell["badpart_new"] += escape(k) and not escape(u)
            cell["torn_u"] += torn(u)
            cell["torn_k"] += torn(k)
            cell["torn_new"] += torn(k) and not torn(u)
            cell["stop_u"] += u["protective_stop"] == "True"
            cell["stop_k"] += k["protective_stop"] == "True"
            differs = [c for c in u if c not in SKIP and u[c] != k[c]]
            if not gentle and differs:
                cell["untripped_diff"] += 1
                failures.append(f"{backend} {suite} s{seed} {cond} {ctrl} #{i}: differs without a trip in {differs[:6]}")
            if gentle:
                trips.append({"backend": backend, "suite": suite, "seed": seed, "condition": cond,
                              "group": u["group"], "controller": ctrl, "trial_index": i,
                              "uncapped": f"{u['success']}/{u['failure_reason']}/torn={torn(u)}/stop={u['protective_stop']}",
                              "capped": f"{k['success']}/{k['failure_reason']}/torn={torn(k)}/stop={k['protective_stop']}",
                              "rows_differ": bool(differs), "first_trip": gentle[0][2], "trips": len(gentle)})
    out = [f"# Retract cap, paired: {root}", "",
           f"Made by `python -m experiments.v02f_retract_cap_compare {root}`. u = v0.2e baseline (flag off), "
           f"k = the same controller with `retract_pull_cap` on (`{suffix}`), same trials. Good = good-part trials "
           "(success; bad units = escapes on good parts); bad = deliberately bad parts passed. Torn = "
           "`final_latch_intact` False, any trial. Tripped = trials with a `gentle_retract` event in k that u does "
           "not have (J's VERIFY logs C's own).", "",
           "| machine | suite | ctrl | trials | tripped | good seated u -> k (gain/loss) | torn u -> k (new) | "
           "bad units u -> k (new) | bad parts u -> k (new) | stops u -> k | rows differing without a trip | verdict |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    all_pass = True
    verdicts: dict[str, bool] = defaultdict(lambda: True)
    for (b, s, ctrl), c in sorted(cells.items(), key=lambda kv: (kv[0][0] != "gantry", kv[0][1], BASE.index(kv[0][2]))):
        fails = []
        if c["torn_new"]:
            fails.append("tears")
        if c["unit_new"]:
            fails.append("bad unit")
        if c["badpart_new"]:
            fails.append("bad part")
        if c["ok_u"] - c["ok_k"] > MAX_SUCCESS_LOSS:
            fails.append("success")
        if c["untripped_diff"]:
            fails.append("identity")
        verdicts[ctrl] &= not fails
        out.append(f"| {b} | {s} | {LETTER[ctrl]} | {c['trials']} | {c['tripped']} | {c['ok_u']} -> {c['ok_k']} of "
                   f"{c['good']} (+{c['ok_gain']}/-{c['ok_loss']}) | {c['torn_u']} -> {c['torn_k']} ({c['torn_new']}) | "
                   f"{c['unit_u']} -> {c['unit_k']} ({c['unit_new']}) | {c['badpart_u']} -> {c['badpart_k']} "
                   f"({c['badpart_new']}) | {c['stop_u']} -> {c['stop_k']} | {c['untripped_diff']} | "
                   f"{'pass' if not fails else 'FAIL: ' + ', '.join(fails)} |")
    out += ["", "Per controller over all cells: " + ", ".join(f"{LETTER[c]} {'pass' if v else 'FAIL'}"
                                                         for c, v in verdicts.items())]
    fair_pass = all(verdicts[c] for c in BASE[:4] if c in verdicts)
    all_pass = fair_pass and all(verdicts.values())
    out += [f"D, F, H and I all pass: {fair_pass}. J passes: {verdicts.get('spiral_rcc_verify')}.", ""]
    if failures:
        out += ["## Rows that differ without a trip", ""] + [f"- {f}" for f in failures[:50]] + [""]
    out += ["## Trials with a trip", "", "| machine | suite | seed | condition | ctrl | trial | uncapped | capped | "
            "rows differ | first trip |", "|---|---|---|---|---|---|---|---|---|---|"]
    for t in trips:
        out.append(f"| {t['backend']} | {t['suite']} | {t['seed']} | {t['condition']} | {LETTER[t['controller']]} | "
                   f"{t['trial_index']} | {t['uncapped']} | {t['capped']} | {t['rows_differ']} | {t['first_trip']} |")
    (root / "TABLES.md").write_text("\n".join(out) + "\n")
    if trips:
        with (root / "trips.csv").open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(trips[0]))
            w.writeheader()
            w.writerows(trips)
    return out, all_pass


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--suffix", default="@cap")
    args = ap.parse_args()
    out, _ = compare(args.root, args.suffix)
    print("\n".join(out[:60]))


if __name__ == "__main__":
    main()
