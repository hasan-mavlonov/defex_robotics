"""Markdown tables for the Checkpoint 2 preparation runs, from the committed files only.

    python -m experiments.cp2_tables > results/checkpoint2_prep/tables.md

Every table names the files it is computed from. All numbers are development
measurements in simulation (seeds 2026, 3001-3030, 4001), not reported results.
"""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

from defex.config import REPO_ROOT
from defex.logging.metrics import is_escape, read_trials_csv

ROOT = REPO_ROOT / "results" / "checkpoint2_prep"
ORDER = ("fixed", "correction", "adaptive", "spiral", "correction_rcc", "spiral_rcc", "adaptive_learned")
LETTER = {"fixed": "A", "correction": "B", "adaptive": "C", "spiral": "D", "correction_rcc": "E", "spiral_rcc": "F",
          "adaptive_learned": "G"}


def rel(p: Path) -> str:
    return str(p.relative_to(REPO_ROOT))


def _f(x, fmt="{:.2f}"):
    return "-" if x is None else fmt.format(x)


def text_file(path: Path) -> str:
    return f"From `{rel(path)}`:\n\n```\n{path.read_text().strip()}\n```"


# ------------------------------------------------------------------ offline model metrics
def model_table(metrics_paths: list[Path]) -> str:
    out = ["| Model | Split | n | NLL (nats) | Radial error L / A / V, all contacts (mm) | "
           "L / A / V, first contacts (mm) | Inside 1 / 2 sigma (expected 0.39 / 0.86) | Yaw error L / V (deg) |",
           "|---|---|---|---|---|---|---|---|"]
    for p in metrics_paths:
        m = json.loads(p.read_text())
        for split in ("train", "validation", "dev_seed2026"):
            s = m.get(split) or {}
            if not s.get("n"):
                continue
            a, f = s["mae_mm"], s["mae_mm_first_contact"]

            def lav(d):
                return " / ".join(_f((d[k] or {}).get("radial_mean")) for k in
                                  ("learned", "analytic_posterior_mean", "vision_estimate"))

            c = s["calibration_xy"]["learned"]
            out.append(f"| {m['feature_set']} | {split} | {s['n']} | {s['nll_nats']:.2f} | {lav(a)} | {lav(f)} | "
                       f"{c['inside_1sigma']:.2f} / {c['inside_2sigma']:.2f} | "
                       f"{s['yaw_mae_deg']['learned']:.2f} / {s['yaw_mae_deg']['vision_estimate']:.2f} |")
    sel = []
    for p in metrics_paths:
        m = json.loads(p.read_text())
        rep = (m.get("validation") or {}).get("first_contact_integration_replay") or {}
        pm = rep.get("posterior_mean_mae_mm") or {}
        sel.append(f"- `{m['feature_set']}`: selected {m['selected']['hidden']} lr {m['selected']['lr']:g} "
                   f"wd {m['selected']['weight_decay']:g}, best epoch {m['selected']['best_epoch']}; validation "
                   f"first-contact replay, posterior-mean radial error at w = 0 / 0.25 / 0.5 / 1: "
                   + " / ".join(_f((pm.get(w) or {}).get("radial_mean")) for w in ("0.0", "0.25", "0.5", "1.0"))
                   + f" mm (replay matches the recorded posterior to {_f(rep.get('replay_matches_recorded_mm'), '{:.1e}')} mm)")
    src = ", ".join(f"`{rel(p)}`" for p in metrics_paths)
    return "\n".join(out + [""] + sel + ["", f"L = learned mean, A = C's analytic posterior mean after the same "
                                             f"contact, V = vision estimate. Files: {src}."])


# ------------------------------------------------------------------ paired G vs C
def paired_overall_table(paired: Path, trials: Path) -> str:
    rep = json.loads(paired.read_text())
    res = read_trials_csv(trials)
    by = defaultdict(list)
    for r in res:
        by[r.controller].append(r)

    def fails(rs):
        d = defaultdict(int)
        for r in rs:
            if not r.success:
                d[r.failure_reason or "unknown"] += 1
        return ", ".join(f"{k} {v}" for k, v in sorted(d.items())) or "none"

    out = ["| Variant | Successes | C-only / G-only (McNemar p) | Bad units passed | Protective stops | "
           "Mean retries | Mean cycle of successes (s) | Cycle diff vs C, both succeeded (s, 95% CI) | Failures |",
           "|---|---|---|---|---|---|---|---|---|"]
    c = next(iter(rep.values()))["overall"]
    out.append(f"| C (adaptive) | {c['success']['reference']}/{c['pairs']} | - | {c['bad_units_passed']['reference']} | "
               f"{c['protective_stops']['reference']} | {_f(c['mean_retries']['reference'])} | "
               f"{_f(c['cycle_s']['reference']['mean'])} | - | {fails(by['adaptive'])} |")
    for name, d in rep.items():
        o = d["overall"]
        ci = o["cycle_diff_both_success_ci95_s"]
        out.append(f"| {name} | {o['success']['other']}/{o['pairs']} | {o['reference_only_success']} / "
                   f"{o['other_only_success']} ({o['mcnemar_p']:.2g}) | {o['bad_units_passed']['other']} | "
                   f"{o['protective_stops']['other']} | {_f(o['mean_retries']['other'])} | "
                   f"{_f(o['cycle_s']['other']['mean'])} | {_f(o['cycle_diff_both_success_mean_s'], '{:+.2f}')} "
                   f"({_f(ci and ci[0], '{:+.2f}')} to {_f(ci and ci[1], '{:+.2f}')}) | {fails(by[name])} |")
    return "\n".join(out + ["", f"Files: `{rel(paired)}`, `{rel(trials)}`."])


def selection_ranking(paired: Path) -> str:
    """The pre-registered rule (arm_prior/SELECTION_RULE.txt) applied to the validation sweep."""
    rep = json.loads(paired.read_text())
    key = {n: (-d["overall"]["success"]["other"], d["overall"]["bad_units_passed"]["other"],
               d["overall"]["protective_stops"]["other"], d["overall"]["cycle_s"]["other"]["mean"])
           for n, d in rep.items()}
    ranked = sorted(key, key=key.get)
    return ("Selection rule (most successes, then fewest bad units, fewest stops, lowest mean cycle of "
            "successes), ranked: " + ", ".join(f"{n} ({-key[n][0]}, {key[n][1]}, {key[n][2]}, {key[n][3]:.2f} s)"
                                                 for n in ranked) + f". Chosen: {ranked[0]}.")


def paired_md(path: Path) -> str:
    return path.read_text().strip() + f"\n\nFile: `{rel(path)}`."


# ------------------------------------------------------------------ benchmark snapshot
def snapshot_tables(run: Path) -> str:
    summary = json.loads((run / "summary.json").read_text())
    overall = {o["controller"]: o for o in summary["overall"]}
    res = read_trials_csv(run / "trials.csv")
    ctrls = [c for c in ORDER if c in overall]
    out = ["| Controller | Success | 95% CI | Escapes (failed units passed as good) | Protective stops | "
           "Median / p95 cycle of successes (s) | Mean retries |", "|---|---|---|---|---|---|---|"]
    for c in ctrls:
        o = overall[c]
        cy = o["cycle_time_s_success"]
        out.append(f"| {LETTER[c]} {c} | {o['successes']}/{o['n']} ({o['success_rate']:.0%}) | "
                   f"{o['success_ci_low']:.0%}-{o['success_ci_high']:.0%} | {o['escapes']} | {o['protective_stops']} | "
                   f"{_f(cy.get('median'))} / {_f(cy.get('p95'))} | {_f(o.get('retries_mean'))} |")
    cell = defaultdict(lambda: [0, 0, 0, 0])  # successes, trials, escapes, stops
    for r in res:
        k = (r.condition, r.controller)
        cell[k][0] += r.success
        cell[k][1] += 1
        cell[k][2] += is_escape(r)
        cell[k][3] += r.protective_stop
    conds = list(dict.fromkeys(r.condition for r in res))
    out += ["", "Successes per condition; in brackets when nonzero: e = escapes (failed units passed as good), "
                "s = protective stops:", "",
            "| Condition | " + " | ".join(LETTER[c] for c in ctrls) + " |", "|---|" + "---|" * len(ctrls)]
    for cond in conds:
        cells = []
        for c in ctrls:
            s, n, e, st = cell[(cond, c)]
            tag = " ".join(t for t in (f"e{e}" if e else "", f"s{st}" if st else "") if t)
            cells.append(f"{s}/{n}" + (f" [{tag}]" if tag else ""))
        out.append(f"| {cond} | " + " | ".join(cells) + " |")
    pv = summary.get("paired_vs_adaptive", {}).get("adaptive_learned")
    if pv:
        out += ["", f"G vs C paired over this run: {pv['pairs']} pairs, C-only {pv['reference_only_success']}, "
                    f"G-only {pv['controller_only_success']}, McNemar p = {pv['mcnemar_p']:.2g}."]
    cfg = json.loads((run / "config.json").read_text())
    env = cfg.get("environment", {})
    out += ["", f"Files: `{rel(run / 'summary.json')}`, `{rel(run / 'trials.csv')}` (commit "
                f"{str(env.get('git_commit', 'unknown'))[:7]}, dirty: {env.get('git_dirty')}, backend: "
                f"{cfg.get('backend')}, seed {cfg.get('base_seed')}, {cfg.get('n_trials_per_condition')} trials per cell)."]
    return "\n".join(out)


def overlap_check(a: Path, b: Path, ignore=("wall_time_s",)) -> str:
    """Rows present in both trials.csv files (same controller, condition, trial index, seed) compared field by field."""
    import csv

    def load(p):
        with p.open() as fh:
            return {(r["controller"], r["condition"], r["trial_index"], r["seed"]): r for r in csv.DictReader(fh)}

    ra, rb = load(a), load(b)
    keys = sorted(ra.keys() & rb.keys())
    diff_rows = [k for k in keys if any(ra[k][f] != rb[k].get(f) for f in ra[k] if f not in ignore)]
    ctrls = sorted({k[0] for k in keys})
    by = {c: sum(k[0] == c for k in diff_rows) for c in ctrls}
    return (f"| `{rel(a)}` | `{rel(b)}` | {len(keys)} | {', '.join(ctrls)} | {len(diff_rows)} | "
            + ", ".join(f"{c} {n}" for c, n in by.items() if n) + " |")


def median_cycle(rs) -> float | None:
    v = [r.cycle_time_s for r in rs if r.success]
    return statistics.median(v) if v else None


def main() -> None:
    parts = ["# Checkpoint 2 preparation: development tables", "",
             "Generated by `python -m experiments.cp2_tables` from committed files under "
             "`results/checkpoint2_prep/`. Development measurements in simulation; not reported results.", ""]
    eq = ROOT / "equivalence" / "comparison.txt"
    if eq.exists():
        parts += ["## Rule-3 gantry equivalence after the merge", "", text_file(eq), ""]
    gr = ROOT / "gantry_g_recheck"
    if (gr / "pooled" / "paired.md").exists():
        parts += ["## Gantry G vs C on dev seed 2026 after the merge", "",
                  text_file(gr / "comparison_vs_w9_dev2026.txt"), "", paired_md(gr / "pooled" / "paired.md"), ""]
    ap = ROOT / "arm_prior"
    mp = [p for p in (ap / "models" / "arm_contact_metrics.json", ap / "models" / "arm_all_metrics.json") if p.exists()]
    if mp:
        parts += ["## Arm contact prior: offline model quality", "", model_table(mp), ""]
    vw = ap / "validation" / "weights"
    if (vw / "paired.json").exists():
        parts += ["## Arm validation sweep (seed 4001)", "", paired_overall_table(vw / "paired.json", vw / "trials.csv"),
                  "", selection_ranking(vw / "paired.json"), "", "Per condition:", "", paired_md(vw / "paired.md"), ""]
    vl = ap / "validation" / "latching_suite" / "paired.md"
    if vl.exists():
        parts += ["## Arm G vs C on validation seed 4001, whole latching suite (after the choice)", "",
                  paired_md(vl), ""]
    for name, title in (("pooled", "pooled"), ("standard", "standard noise families and friction_1"),
                        ("latching", "latching suite")):
        p = ap / "dev2026" / name / "paired.md"
        if p.exists():
            parts += [f"## Arm G vs C on dev seed 2026 ({title})", "", paired_md(p), ""]
    snap = ROOT / "snapshot"
    for name, title in (("gantry_standard", "Gantry, standard suite"), ("gantry_latching", "Gantry, latching suite"),
                        ("arm_standard5", "UR5e arm, five-condition set"), ("arm_latching", "UR5e arm, latching suite")):
        if (snap / name / "summary.json").exists():
            parts += [f"## Snapshot, dev seed 2026: {title}", "", snapshot_tables(snap / name), ""]
    pairs = [
        (snap / "gantry_standard" / "trials.csv", ROOT / "equivalence" / "after_standard" / "trials.csv"),
        (snap / "gantry_latching" / "trials.csv", ROOT / "equivalence" / "after_latching" / "trials.csv"),
        (snap / "gantry_standard" / "trials.csv", gr / "standard" / "trials.csv"),
        (snap / "gantry_latching" / "trials.csv", gr / "latching" / "trials.csv"),
        (snap / "arm_standard5" / "trials.csv", REPO_ROOT / "results" / "w5b_development" / "after" / "arm_standard_seed2026" / "trials.csv"),
        (snap / "arm_latching" / "trials.csv", REPO_ROOT / "results" / "w5b_development" / "after" / "arm_latching_seed2026" / "trials.csv"),
        (snap / "arm_standard5" / "trials.csv", ap / "dev2026" / "standard" / "trials.csv"),
        (snap / "arm_latching" / "trials.csv", ap / "dev2026" / "latching" / "trials.csv"),
    ]
    rows = [overlap_check(a, b) for a, b in pairs if a.exists() and b.exists()]
    if rows:
        parts += ["## Overlap checks: the same trials in different runs", "",
                  "Every field except wall_time_s, for rows with the same controller, condition, trial index and seed.",
                  "", "| Run | Earlier run | Shared trials | Controllers | Rows that differ | Differing rows by controller |",
                  "|---|---|---|---|---|---|", *rows, ""]
    print("\n".join(parts).rstrip() + "\n")


if __name__ == "__main__":
    main()
