"""Tables for results/v0.2c_defect_verdict (development measurements; dev seeds 2026 and 2027).

    python -m experiments.v02c_tables [--root results/v0.2c_defect_verdict] > results/v0.2c_defect_verdict/tables.md

Reads before/ (commit 54f3097, untouched) and after/ (this branch) runs of the latching suite,
pairs them trial by trial, and reports good-part success (Wilson 95% intervals, exact McNemar),
false rejects, bad parts passed, time per bad part, protective stops and good units per hour.
"""

from __future__ import annotations

import argparse
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from defex.config import REPO_ROOT
from defex.logging.metrics import STOP_RESET_S, is_escape, mcnemar_exact, read_trials_csv, throughput_uph, wilson_interval

GOOD = ("mf_nominal", "mf_moderate", "mf_noise_1mm")
BAD = ("mf_half_latched", "mf_broken_latch", "mf_stubbed_terminal", "mf_wrong_polarization")
CTRL = {"adaptive": "C", "adaptive_learned": "G"}


def _load(path: Path):
    rows = read_trials_csv(path / "trials.csv")
    ev = json.loads(gzip.open(path / "events.json.gz").read())
    for r in rows:
        aborts = [e[2] for e in ev.get(f"{r.condition}|{r.controller}|{r.trial_index}", []) if e[1] == "abort"]
        r.abort = aborts[0] if aborts else ""  # the controller's own reason, also for seated parts (false rejects)
    return rows


def _meta(path: Path) -> str:
    cfg = json.loads((path / "config.json").read_text())
    env = cfg.get("environment", cfg)
    commit = str(env.get("git_commit", "?"))[:7]
    return f"commit `{commit}`, dirty {env.get('git_dirty')}, seed {cfg.get('base_seed')}, {cfg.get('n_trials_per_condition')} trials per cell"


def _pct(k: int, n: int) -> str:
    lo, hi = wilson_interval(k, n)
    return f"{k}/{n} ({100 * lo:.0f}-{100 * hi:.0f}%)"


def _q(xs, q):
    return f"{np.percentile(xs, q):.2f}" if len(xs) else "n/a"


def _key(r):
    return (r.controller, r.condition, r.trial_index, r.seed)


def latching_table(before: list, after: list, title: str) -> str:
    b = {_key(r): r for r in before}
    a = {_key(r): r for r in after}
    keys = sorted(b.keys() & a.keys())
    lines = [f"### {title}", ""]
    lines.append("| Controller | Run | Good parts seated (95% CI) | Before-only / after-only (McNemar p) | False rejects | "
                 "Defect verdicts on good parts | Left latched, unverified | Stops on good parts | Cycle p50 / p95, good successes (s) | "
                 "Bad parts passed | Stops on bad parts | Time per bad part, mean / p50 / p95 (s) | Good units per hour, no reset / 60 s per stop |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for ctrl in CTRL:
        ks = [k for k in keys if k[0] == ctrl]
        if not ks:
            continue
        for run, rows in (("before", b), ("after", a)):
            rs = [rows[k] for k in ks]
            good = [r for r in rs if r.condition in GOOD]
            bad = [r for r in rs if r.condition in BAD]
            gs = sum(r.success for r in good)
            if run == "after":
                bo = sum(b[k].success and not a[k].success for k in ks if k[1] in GOOD)
                ao = sum(a[k].success and not b[k].success for k in ks if k[1] in GOOD)
                pair = f"{bo} / {ao} ({mcnemar_exact(bo, ao):.2g})"
            else:
                pair = "reference"
            fr = sum(r.failure_reason == "false_reject" for r in good)
            dv = sum(r.abort.startswith("defect_suspected") for r in good)
            un = sum(r.abort.startswith("unverified") for r in good)
            st_g = sum(r.protective_stop for r in good)
            cyc = [r.cycle_time_s for r in good if r.success]
            esc = sum(is_escape(r) for r in bad)
            st_b = sum(r.protective_stop for r in bad)
            tb = [r.cycle_time_s for r in bad]
            uph0 = throughput_uph(rs, 0.0)
            uph60 = throughput_uph(rs, STOP_RESET_S)
            lines.append(
                f"| {CTRL[ctrl]} | {run} | {_pct(gs, len(good))} | {pair} | {fr} | {dv} | {un} | {st_g} | "
                f"{_q(cyc, 50)} / {_q(cyc, 95)} | {esc} of {len(bad)} | {st_b} | "
                f"{np.mean(tb):.2f} / {_q(tb, 50)} / {_q(tb, 95)} | {uph0:.0f} / {uph60:.0f} |")
    lines.append("")
    return "\n".join(lines)


def defect_table(before: list, after: list, title: str) -> str:
    b = {_key(r): r for r in before}
    a = {_key(r): r for r in after}
    keys = sorted(b.keys() & a.keys())
    lines = [f"### {title}", ""]
    lines.append("| Controller | Condition | Run | Passed as good | Stops (force / torque trips) | Time p50 / p95 (s) | Mean retries | Outcomes |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for ctrl in CTRL:
        for cond in GOOD + BAD:
            ks = [k for k in keys if k[0] == ctrl and k[1] == cond]
            if not ks:
                continue
            for run, rows in (("before", b), ("after", a)):
                rs = [rows[k] for k in ks]
                stops = [r for r in rs if r.protective_stop]
                ft = sum(r.peak_measured_force_n > 48.0 for r in stops)
                tt = len(stops) - ft
                out = Counter("seated" if r.success else r.failure_reason.replace("aborted:", "")
                              + (f" ({r.abort})" if r.failure_reason == "false_reject" and r.abort else "") for r in rs)
                tb = [r.cycle_time_s for r in rs]
                lines.append(
                    f"| {CTRL[ctrl]} | {cond} | {run} | {sum(is_escape(r) for r in rs)} | {len(stops)} ({ft} / {tt}) | "
                    f"{_q(tb, 50)} / {_q(tb, 95)} | {np.mean([r.retries for r in rs]):.2f} | "
                    + ", ".join(f"{k} {v}" for k, v in sorted(out.items(), key=lambda kv: -kv[1])) + " |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="results/v0.2c_defect_verdict")
    args = ap.parse_args()
    root = REPO_ROOT / args.root
    print("# v0.2c defect verdict: development tables\n")
    print("Generated by `python -m experiments.v02c_tables` from committed runs. Development measurements in "
          "simulation (dev seeds 2026 and 2027); not reported benchmark results. before = commit 54f3097 "
          "(Checkpoint 2 code, untouched), after = this branch.\n")
    for f in sorted(root.glob("equivalence*/comparison*.txt")):
        print(f"## Equivalence: `{f.relative_to(REPO_ROOT)}`\n\n```\n{f.read_text().strip()}\n```\n")
    for backend in ("gantry", "arm"):
        pooled_b, pooled_a, metas = [], [], []
        for seed in (2026, 2027):
            pb, pa = root / "before" / f"{backend}_latching_s{seed}", root / "after" / f"{backend}_latching_s{seed}"
            if not (pb / "trials.csv").exists() or not (pa / "trials.csv").exists():
                continue
            rb, ra = _load(pb), _load(pa)
            pooled_b += rb
            pooled_a += ra
            metas.append(f"seed {seed}: before {_meta(pb)}; after {_meta(pa)}")
        if not pooled_b:
            continue
        print(f"## {backend}: latching suite\n")
        for m in metas:
            print(f"- {m}")
        print(f"- files: `{args.root}/{{before,after}}/{backend}_latching_s{{2026,2027}}/trials.csv`\n")
        print(latching_table(pooled_b, pooled_a, f"{backend}, seeds 2026 + 2027 pooled"))
        for seed in (2026, 2027):
            sb = [r for r in pooled_b if r.seed == seed]
            sa = [r for r in pooled_a if r.seed == seed]
            if sb and sa:
                print(latching_table(sb, sa, f"{backend}, seed {seed}"))
        print(defect_table(pooled_b, pooled_a, f"{backend}, per condition, seeds 2026 + 2027 pooled"))


if __name__ == "__main__":
    main()
