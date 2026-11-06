"""Apply results/v0.2c_defect_verdict/validation/SELECTION_RULE.md to the seed-4002 runs.

    python -m experiments.v02c_selection results/v0.2c_defect_verdict/validation/gantry \\
        results/v0.2c_defect_verdict/validation/arm > results/v0.2c_defect_verdict/validation/selection.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from defex.config import REPO_ROOT
from defex.logging.metrics import STOP_RESET_S, is_escape, mcnemar_exact, read_trials_csv, throughput_uph, wilson_interval

GOOD = ("mf_nominal", "mf_moderate", "mf_noise_1mm")
CANDIDATES = ("off", "r2", "r3")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", type=Path)
    args = ap.parse_args()
    rows = []
    for run in args.runs:
        run = run if run.is_absolute() else REPO_ROOT / run
        cfg = json.loads((run / "config.json").read_text())
        env = cfg["environment"]
        print(f"- `{run.relative_to(REPO_ROOT)}`: backend {cfg['backend']}, seed {cfg['base_seed']}, "
              f"{cfg['n_trials_per_condition']} trials per cell, commit `{env['git_commit'][:7]}`, dirty {env['git_dirty']}")
        for r in read_trials_csv(run / "trials.csv"):
            r.backend = cfg["backend"]
            rows.append(r)
    print()
    by: dict[str, list] = {c: [] for c in CANDIDATES}
    for r in rows:
        ctrl, cand = r.controller.split("_", 1)
        r.base = ctrl
        by[cand].append(r)

    def key(r):
        return (r.backend, r.base, r.condition, r.trial_index)

    idx = {c: {key(r): r for r in by[c]} for c in CANDIDATES}
    stats = {}
    for c in CANDIDATES:
        rs = by[c]
        good = [r for r in rs if r.condition in GOOD]
        bad = [r for r in rs if r.condition not in GOOD]
        succ = [r for r in good if r.success]
        cyc = [r.cycle_time_s for r in succ]
        stats[c] = {
            "n": len(rs), "escapes": sum(is_escape(r) for r in bad), "good": len(succ), "n_good": len(good),
            "uph60": throughput_uph(rs, STOP_RESET_S), "uph0": throughput_uph(rs, 0.0),
            "p50": float(np.median(cyc)), "p95": float(np.percentile(cyc, 95)),
            "stops_bad": sum(r.protective_stop for r in bad), "stops_good": sum(r.protective_stop for r in good),
            "t_bad": float(np.mean([r.cycle_time_s for r in bad])),
            "false_rejects": sum(r.failure_reason == "false_reject" for r in good),
        }

    def paired(a, b):
        ks = [k for k in idx[a] if k[2] in GOOD and k in idx[b]]
        x = sum(idx[a][k].success and not idx[b][k].success for k in ks)
        y = sum(idx[b][k].success and not idx[a][k].success for k in ks)
        return x, y, mcnemar_exact(x, y)

    print("| Candidate | Trials | Bad parts passed | Good parts seated (95% CI) | vs off: off-only / cand-only (p) | "
          "False rejects | Stops good / bad | Time per bad part (s) | Good units per hour, no reset / 60 s per stop | "
          "Cycle p50 / p95, good successes (s) |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for c in CANDIDATES:
        s = stats[c]
        lo, hi = wilson_interval(s["good"], s["n_good"])
        pr = "reference" if c == "off" else "{} / {} ({:.2g})".format(*paired("off", c))
        print(f"| {c} | {s['n']} | {s['escapes']} | {s['good']}/{s['n_good']} ({100 * lo:.1f}-{100 * hi:.1f}%) | {pr} | "
              f"{s['false_rejects']} | {s['stops_good']} / {s['stops_bad']} | {s['t_bad']:.2f} | {s['uph0']:.0f} / {s['uph60']:.0f} | "
              f"{s['p50']:.2f} / {s['p95']:.2f} |")
    print()
    alive = [c for c in CANDIDATES if stats[c]["escapes"] == 0]
    print(f"Step 1 (no bad part passed): {', '.join(alive) or 'none'}.")
    best = max(alive, key=lambda c: stats[c]["good"])
    tied = [c for c in alive if c == best or paired(best, c)[2] >= 0.05]
    print(f"Step 2 (good-part success; most: {best}, {stats[best]['good']}): tied with it (McNemar p >= 0.05): "
          f"{', '.join(tied)}.")
    ranked = sorted(tied, key=lambda c: (-round(stats[c]["uph60"], 6), stats[c]["p50"], stats[c]["p95"]))
    print(f"Steps 3-4 (good units per hour with 60 s per stop, then p50, p95): "
          + ", ".join(f"{c} ({stats[c]['uph60']:.1f})" for c in ranked) + ".")
    print(f"\n**Chosen: {ranked[0]}.**")


if __name__ == "__main__":
    main()
