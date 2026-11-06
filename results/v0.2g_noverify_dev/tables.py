"""Tables for results/v0.2g_noverify_dev: C with and without its housing-only VERIFY, I and J."""
import csv, math, statistics, sys
from collections import defaultdict
from pathlib import Path

run = Path(sys.argv[1])
NAMES = {"adaptive": "C  Defex", "adaptive@noverify": "C without VERIFY",
         "spiral_rcc_pull": "I  spiral + pull", "spiral_rcc_verify": "J  spiral + Defex VERIFY"}
T = lambda v: v == "True"

def mcnemar(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)

out = []
for cell in sorted(p for p in run.iterdir() if (p / "trials.csv").exists()):
    rows = list(csv.DictReader(open(cell / "trials.csv")))
    by = defaultdict(dict)
    for r in rows:
        by[r["controller"]][(r["condition"], r["trial_index"])] = r
    n = len(next(iter(by.values())))
    out += [f"## {cell.name} (seed 2026, {n} trials per controller)", "",
            "| Controller | Seated correctly | Said 'done' on a bad plug | ...of which over 3 deg | Median time, good parts (s) | Good parts per hour |",
            "|---|---|---|---|---|---|"]
    for ctl in NAMES:
        d = by.get(ctl)
        if not d:
            continue
        s = sum(T(r["success"]) for r in d.values())
        esc = [r for r in d.values() if T(r["declared_success"]) and not T(r["gt_seated"])]
        ang = sum(max(abs(float(r["final_yaw_deg"])), abs(float(r["final_tilt_deg"]))) > 3 for r in esc)
        cyc = [float(r["cycle_time_s"]) for r in d.values() if T(r["success"])]
        tot = sum(float(r["cycle_time_s"]) for r in d.values())
        out.append(f"| {NAMES[ctl]} | {s}/{n} ({100*s/n:.1f}%) | {len(esc)} | {ang} | {statistics.median(cyc):.2f} | {3600*s/tot:,.0f} |")
    out.append("")
    a, b = by["adaptive"], by["adaptive@noverify"]
    co = sum(T(a[k]["success"]) and not T(b[k]["success"]) for k in a)
    vo = sum(T(b[k]["success"]) and not T(a[k]["success"]) for k in a)
    out.append(f"Paired, C vs C without VERIFY: C-only {co}, without-VERIFY-only {vo}, exact McNemar p = {mcnemar(co, vo):.2g}.")
    out += ["", "Per condition, where any of the four differ (seated correctly / bad plugs called 'done'):", "",
            "| Condition | " + " | ".join(NAMES[c] for c in NAMES) + " |", "|---|" + "---|" * len(NAMES)]
    conds = list(dict.fromkeys(k[0] for k in a))
    for cond in conds:
        cells = []
        for ctl in NAMES:
            d = by[ctl]
            ks = [k for k in d if k[0] == cond]
            s = sum(T(d[k]["success"]) for k in ks)
            e = sum(T(d[k]["declared_success"]) and not T(d[k]["gt_seated"]) for k in ks)
            cells.append((s, e))
        if len(set(cells)) > 1:
            out.append(f"| {cond} | " + " | ".join(f"{s} / {e}" for s, e in cells) + " |")
    out.append("")
print("\n".join(out))
