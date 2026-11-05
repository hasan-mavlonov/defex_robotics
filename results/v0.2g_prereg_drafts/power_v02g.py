"""Discordance rates and exact McNemar power for the v0.2g draft pre-registrations.

    PYTHONPATH=. python results/v0.2g_prereg_drafts/power_v02g.py > results/v0.2g_prereg_drafts/POWER.md

Reads committed trials.csv only. No simulation. Power uses experiments.v02f_rig_power (exact two-sided McNemar
at 0.05, exact power from the two discordant-pair rates).
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from experiments.v02f_rig_power import escape, n_for_power, ok, power

R = Path("results")
BENCH = (("benchmark_v0.2d", "20261123"), ("benchmark_v0.2d_rep", "20261124"), ("benchmark_v0.2e", "20261130"))
H2 = ("heldout2_v0.2f", "20261207")
CODE = {"adaptive": "C", "spiral": "D", "correction_rcc": "E", "spiral_rcc": "F", "spiral_pull": "H",
        "spiral_rcc_pull": "I", "spiral_rcc_verify": "J"}
NAME = {v: k for k, v in CODE.items()}
FAIR = ("D", "E", "F", "H", "I")
LATCH_GOOD = {"mf_nominal", "mf_moderate", "mf_noise_1mm"}
SPREAD_GOOD = {"mf_spread", "mf_latch_early", "mf_latch_late", "mf_latch_weak", "mf_terminal_max", "mf_terminal_min"}


def rows(path: Path) -> dict:
    out = {}
    for r in csv.DictReader(open(path)):
        out[(r["controller"], r["condition"], r["trial_index"])] = r
    return out


def pairs(data: dict, x: str, y: str, conds) -> list[tuple[dict, dict]]:
    a, b = NAME[x], NAME[y]
    return [(data[k], data[(b,) + k[1:]]) for k in data if k[0] == a and k[1] in conds and (b,) + k[1:] in data]


def disc(ps, f=ok) -> tuple[int, int, int]:
    return len(ps), sum(f(p) and not f(q) for p, q in ps), sum(f(q) and not f(p) for p, q in ps)


HOLM4 = 0.05 / 4


def pw(n, p10, p01, alpha=0.05):
    return power(n, p10, p01, alpha=alpha) if n else 0.0


def fmt_n(p10, p01):
    n = n_for_power(p10, p01)
    if n is None:
        return "no difference" if p10 == p01 else "> 1,000,000"
    return f"{n:,}"


def load_bench(machine: str, suite: str) -> list[tuple[str, dict]]:
    return [(seed, rows(R / run / f"{machine}_{suite}" / "trials.csv")) for run, seed in BENCH]


def main() -> None:
    p = print
    p("# v0.2g draft pre-registrations: discordance rates and power\n")
    p("Made by `PYTHONPATH=. python results/v0.2g_prereg_drafts/power_v02g.py > results/v0.2g_prereg_drafts/POWER.md` "
      "from committed trials.csv only: benchmark_v0.2d (seed 20261123), benchmark_v0.2d_rep (20261124), "
      "benchmark_v0.2e (20261130) and heldout2_v0.2f (20261207). Simulation rates. Test: exact two-sided McNemar at "
      "0.05 on paired trials. Power is exact, from the two discordant-pair rates (`experiments/v02f_rig_power.py`). "
      "'n for 80%' is paired trials in the cell, rounded up to 10.\n")
    p("Scenario rates are assumptions, not data. f = the fraction of the fixable trials that a change fixes. "
      "'Fixable' = trials where C fails and the named reference controller seats, on the same trial. "
      "h = a harm rate: trials the change newly loses, per paired trial.\n")

    # (1) Observed discordance in the target cells.
    p("## (1) Observed discordance in the cells each C fix targets\n")
    p("| Fix | Cell (source, seed) | C vs | Pairs | C-only / other-only | C-only / other-only rate | C failures |")
    p("|---|---|---|---|---|---|---|")
    targets = {}
    h2 = {m: rows(R / H2[0] / f"{m}_heldout2" / "trials.csv") for m in ("gantry", "arm")}
    fam = {"ft_drift": {"h2_ft_drift_0.1", "h2_ft_drift_0.3"},
           "grasp": {"h2_mf_grasp_unseen_1deg", "h2_mf_grasp_unseen_2deg"},
           "tilt": {"h2_tilt_unseen_2deg", "h2_tilt_unseen_3deg"},
           "yaw": {"h2_yaw_unseen_2.5deg", "h2_yaw_unseen_4deg"}}
    for fix, m, f, ref in (("1 depth hold", "arm", "ft_drift", "D"), ("3 jam progress", "gantry", "grasp", "F"),
                           ("3 jam progress", "arm", "grasp", "F")):
        ps = pairs(h2[m], "C", ref, fam[f])
        n, b, c = disc(ps)
        cf = sum(not ok(x) for x, _ in ps)
        p(f"| {fix} | {m} heldout2 {f} (20261207) | {ref} | {n} | {b} / {c} | {b/n:.2%} / {c/n:.2%} | {cf} |")
        targets[(fix, m)] = (n, b / n, c / n)
        if fix.startswith("1"):
            n, b, c = disc(ps, escape)
            p(f"| 1 depth hold | {m} heldout2 {f}, bad units (20261207) | {ref} | {n} | {b} / {c} | "
              f"{b/n:.2%} / {c/n:.2%} | - |")
            targets[("1 bad", m)] = (n, b / n, c / n)
    for cond in ("friction_1", "friction_0.6"):
        tot = [0, 0, 0, 0]
        per = []
        for seed, d in load_bench("arm", "standard"):
            ps = pairs(d, "C", "I", {cond})
            n, b, c = disc(ps)
            tot[0] += n; tot[1] += b; tot[2] += c; tot[3] += sum(not ok(x) for x, _ in ps)
            per.append(f"{b}/{c}")
        n, b, c, cf = tot
        p(f"| 2 wall signature | arm standard {cond} (3 seeds: {', '.join(per)}) | I | {n} | {b} / {c} | "
          f"{b/n:.2%} / {c/n:.2%} | {cf} |")
        targets[("2", cond)] = (n, b / n, c / n)
    for m in ("gantry", "arm"):
        tot = [0, 0, 0, 0]
        for seed, d in [(s, rows(R / run / f"{m}_heldout" / "trials.csv")) for run, s in BENCH]:
            ps = pairs(d, "C", "J", {"heldout_mischar_2mm"})
            n, b, c = disc(ps)
            tot[0] += n; tot[1] += b; tot[2] += c; tot[3] += sum(not ok(x) for x, _ in ps)
        n, b, c, cf = tot
        p(f"| 3 jam progress (secondary) | {m} heldout heldout_mischar_2mm (3 seeds) | J | {n} | {b} / {c} | "
          f"{b/n:.2%} / {c/n:.2%} | {cf} |")
    p("\nFix 4 (socket-axis reference) has no outcome cell: C passed 0 tilted bad units on every seed, and G's one "
      "(benchmark_v0.2e arm mf_noise_1mm trial 130) is about 1 in 600. Its effect endpoint is a measurement "
      "(tilt verdicts that read more than 1 deg under the true tilt: 234 of 8,320 on the development seeds, "
      "`results/v0.2f_tilt_diagnosis/REPORT.md` item 1), not a McNemar test.\n")

    # (2) Power for C2 against C in the target cells.
    p("## (2) Power of C2 against C in each target cell (scenarios)\n")
    p("p(C2-only) = f x fixable rate; p(C-only) = h. Fixable rate from table (1): the other-only rate.\n")
    p("| Cell | Fixable rate | f | h | n for 80% | power at the planned n | the same at alpha 0.0125 (Holm, 4 tests) |")
    p("|---|---|---|---|---|---|---|")
    plan = {("1 depth hold", "arm"): 200, ("1 bad", "arm"): 200, ("3 jam progress", "gantry"): 200,
            ("3 jam progress", "arm"): 200, ("2", "friction_1"): 400}
    label = {("1 depth hold", "arm"): "arm heldout2 ft_drift, success vs D-fixable",
             ("1 bad", "arm"): "arm heldout2 ft_drift, bad units (C's own)",
             ("3 jam progress", "gantry"): "gantry heldout2 grasp, success vs F-fixable",
             ("3 jam progress", "arm"): "arm heldout2 grasp, success vs F-fixable",
             ("2", "friction_1"): "arm standard friction_1, success vs I-fixable"}
    for key, (n, b, c) in targets.items():
        if key not in plan:
            continue
        rate = b if key[0] == "1 bad" else c
        for f in (1.0, 0.75, 0.5):
            for h in (0.0, 0.005):
                p10, p01 = f * rate, h
                p(f"| {label[key]} | {rate:.2%} | {f} | {h:.1%} | {fmt_n(p10, p01)} | "
                  f"{pw(plan[key], p10, p01):.2f} at {plan[key]} | {pw(plan[key], p10, p01, HOLM4):.2f} |")
    p("\nThe heldout2 rates are from one seed, 80 pairs per family. The friction rates pool three seeds, "
      "300 pairs per condition.\n")

    # (3) No-harm detection on whole suites.
    p("## (3) Harm detection: C2 against C on a whole cell\n")
    p("p(C-only) = h (trials C2 newly loses), p(C2-only) = g (trials it newly wins elsewhere in the cell).\n")
    p("| Pairs in the cell | h | g | power to see C2 below C |")
    p("|---|---|---|---|")
    for n in (600, 900, 1000, 2000):
        for h, g in ((0.0025, 0.0), (0.005, 0.0), (0.01, 0.0), (0.01, 0.005)):
            p(f"| {n:,} | {h:.2%} | {g:.2%} | {power(n, h, g):.2f} |")
    p("\nZero bad units in n trials has a Wilson 95% upper bound of 3.84 / (n + 3.84): 1.9% at 200, 0.64% at 600, "
      "0.19% at 2,000.\n")

    # (4) Seat-and-align scenarios on the standard suite and heldout2.
    p("## (4) Seat-and-align scenarios: C against K (I plus a seat-and-align step; K2 = F plus the same step)\n")
    p("Scenario: K turns a fraction f of I's bad units (declared, not seated) into seated parts and changes "
      "nothing else. Then C-only(K) = C-only(I) minus f x (C-only trials where I passed a bad unit), and "
      "K-only = I-only plus f x (trials where both C and I failed and I passed a bad unit). "
      "Standard: the three benchmark seeds pooled, 6,000 pairs per machine. heldout2: seed 20261207, 80 pairs "
      "per family.\n")
    p("| Cell | Pairs | C-only / I-only (observed) | C-only where I bad unit | both fail, I bad unit | f | "
      "C-only / K-only rate | n for 80% | power at the planned n | the same at alpha 0.0125 |")
    p("|---|---|---|---|---|---|---|---|---|---|")
    sa_cells = []
    for m in ("gantry", "arm"):
        allp = []
        for seed, d in load_bench(m, "standard"):
            allp += pairs(d, "C", "I", {k[1] for k in d})
        sa_cells.append((f"{m} standard (3 seeds)", allp, 2000))
        for f in ("tilt", "yaw"):
            sa_cells.append((f"{m} heldout2 {f}", pairs(h2[m], "C", "I", fam[f]), 200))
    for name, ps, planned in sa_cells:
        n, b, c = disc(ps)
        bi = sum(ok(x) and escape(y) for x, y in ps)
        both = sum(not ok(x) and escape(y) for x, y in ps)
        for f in (1.0, 0.5):
            p10, p01 = (b - f * bi) / n, (c + f * both) / n
            p(f"| {name} | {n:,} | {b} / {c} | {bi} | {both} | {f} | {p10:.2%} / {p01:.2%} | {fmt_n(p10, p01)} | "
              f"{pw(planned, p10, p01):.2f} at {planned:,} | {pw(planned, p10, p01, HOLM4):.2f} |")
    p("\nK against I on bad units: p(I-only bad unit) = f x I's bad-unit rate, p(K-only) = 0.\n")
    p("| Cell | I bad-unit rate | f | n for 80% | power at the planned n | the same at alpha 0.0125 |")
    p("|---|---|---|---|---|---|")
    for name, ps, planned in sa_cells:
        n = len(ps)
        r = sum(escape(y) for _, y in ps) / n
        for f in (1.0, 0.5):
            p(f"| {name} | {r:.2%} | {f} | {fmt_n(f * r, 0.0)} | {pw(planned, f * r, 0.0):.2f} at {planned:,} | "
              f"{pw(planned, f * r, 0.0, HOLM4):.2f} |")

    # (5) Gentle retract: torn latches on development seeds.
    p("\n## (5) Gentle retract: torn good latches (development seeds, v0.2f code)\n")
    p("From `results/v0.2f_baseline_retract_cap/dev/*/trials.csv`, uncapped controllers only (the v0.2e "
      "behaviour), seeds 2026 and 2027, 20 trials per condition. The benchmarks before v0.2f do not log "
      "`final_latch_intact`.\n")
    p("| Machine | Suite | Ctrl | Good-part trials | Torn on good parts | Rate | f | n for 80% (gentle vs uncapped) | "
      "power at 600 | power at 1,200 | power at 1,200, alpha 0.0125 |")
    p("|---|---|---|---|---|---|---|---|---|---|---|")
    for m in ("gantry", "arm"):
        for suite in ("latching", "latch_spread"):
            tr = defaultdict(lambda: [0, 0])
            for fpath in sorted((R / "v0.2f_baseline_retract_cap" / "dev").glob(f"{m}_{suite}_s*/trials.csv")):
                for r in csv.DictReader(open(fpath)):
                    if r["group"] == "bad_part" or "@" in r["controller"]:
                        continue
                    k = CODE.get(r["controller"])
                    tr[k][0] += 1
                    tr[k][1] += r["final_latch_intact"] == "False"
            for k in ("D", "F", "H", "I", "J"):
                n, t = tr[k]
                rate = t / n if n else 0.0
                fs = (1.0, 0.5) if t else (1.0,)
                for f in fs:
                    p(f"| {m} | {suite} | {k} | {n} | {t} | {rate:.2%} | {f} | {fmt_n(f * rate, 0.0)} | "
                      f"{pw(600, f * rate, 0.0):.2f} | {pw(1200, f * rate, 0.0):.2f} | "
                      f"{pw(1200, f * rate, 0.0, HOLM4):.2f} |")
    p("\n600 = latching 3 good conditions x 200 trials (as v0.2e), or latch_spread 6 good conditions x 100; "
      "1,200 = latching at 400 trials per condition. D's and H's tears were the same two gantry `mf_noise_1mm` trials, seed 2027 trials 17 and 19 (`results/v0.2f_baseline_retract_cap/REPORT.md`).\n")

    # (6) CPU per trial.
    p("## (6) CPU seconds per trial (mean `wall_time_s`), per run and controller\n")
    p("Load differed between runs; benchmark_v0.2e ran at --workers 9 on a quiet machine, heldout2 at --workers 2 "
      "at load 40-50. Sum of `wall_time_s` / workers matched both runs' wall time to within about 10%.\n")
    ctrls = list(CODE)
    cpu = defaultdict(list)
    for run, _ in BENCH + (H2,):
        for fpath in sorted((R / run).glob("*_*/trials.csv")):
            for r in csv.DictReader(open(fpath)):
                cpu[(fpath.parent.name, r["controller"])].append(float(r["wall_time_s"]))
    p("| Run folder | " + " | ".join(CODE[c] for c in ctrls) + " |")
    p("|---|" + "---|" * len(ctrls))
    for run in ("gantry_standard", "gantry_latching", "gantry_heldout", "gantry_latch_spread", "gantry_heldout2",
                "arm_standard", "arm_latching", "arm_heldout", "arm_latch_spread", "arm_heldout2"):
        vals = []
        for c in ctrls:
            t = cpu[(run, c)]
            vals.append(f"{sum(t)/len(t):.2f}" if t else "-")
        p(f"| {run} | " + " | ".join(vals) + " |")
    p("\nThe benchmark folders appear three times (three seeds); the means pool them.")


if __name__ == "__main__":
    main()
