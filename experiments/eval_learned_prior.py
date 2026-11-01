"""Paired closed-loop comparison of G (C + learned contact prior) against C (W9).

    python -m experiments.eval_learned_prior variants.json --seed 4001 --trials 60 \\
        --conditions noise_0.5mm,noise_1mm,noise_2mm,mf_noise_1mm --name validation/weights --workers 4
    python -m experiments.eval_learned_prior --analyze results/w9_development/dev2026/standard

``variants.json`` maps a variant name to {"controller": "adaptive" | "adaptive_learned",
optional "model_path", "weight"}; the C variant must be named "adaptive" (the paired
reference). Only W9 seeds are accepted (development 2026/2027, training 3001-3040,
validation 4001). Output under results/w9_development/<name>/: trials.csv, summary.json
(the runner's format), paired.json and paired.md (G minus C, trial by trial).
``--analyze`` writes paired.json / paired.md for any run directory with a trials.csv
(e.g. an experiments.robustness run with --controllers adaptive,adaptive_learned).
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from defex.config import REPO_ROOT, LearnedPriorConfig
from defex.control.adaptive_fsm import AdaptiveInsertionController
from defex.control.adaptive_learned import AdaptiveLearnedController
from defex.logging.metrics import TrialResult, is_escape, mcnemar_exact, read_trials_csv
from defex.tasks.insertion import InsertionTask
from defex.tasks.scenarios import sample_scenario
from experiments.collect_contacts import all_conditions, check_seed
from experiments.runner import environment_info, make_backend, nominal_socket_pose, write_outputs

OUT = REPO_ROOT / "results" / "w9_development"
_TASK: InsertionTask | None = None


def build(name: str, spec: dict):
    if spec["controller"] == "adaptive":
        ctl = AdaptiveInsertionController()
    elif spec["controller"] == "adaptive_learned":
        path = spec.get("model_path")
        ctl = AdaptiveLearnedController(
            prior_cfg=LearnedPriorConfig(weight=spec.get("weight")),
            model_path=None if path is None else REPO_ROOT / path,
        )
    else:
        raise ValueError(f"unknown controller {spec['controller']}")
    ctl.name = name
    return ctl


def _job(name: str, spec: dict, cond_name: str, seed: int, idx: tuple[int, ...]) -> list[TrialResult]:
    global _TASK
    if _TASK is None:
        os.environ.setdefault("OMP_NUM_THREADS", "1")
        _TASK = InsertionTask(backend=make_backend())
    cond = all_conditions()[cond_name]
    nominal = nominal_socket_pose(cond, _TASK.fixture)
    return [_TASK.run(build(name, spec), sample_scenario(cond, i, seed, nominal)) for i in idx]


def _boot_ci(x: np.ndarray, n_boot: int = 2000) -> list[float] | None:
    if x.size == 0:
        return None
    rng = np.random.default_rng(0)
    means = x[rng.integers(0, x.size, (n_boot, x.size))].mean(axis=1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def _cell(ref: list[TrialResult], other: list[TrialResult]) -> dict:
    a = {(r.condition, r.trial_index): r for r in ref}
    b = {(r.condition, r.trial_index): r for r in other}
    keys = sorted(a.keys() & b.keys())
    ra, rb = [a[k] for k in keys], [b[k] for k in keys]
    ref_only = sum(x.success and not y.success for x, y in zip(ra, rb))
    oth_only = sum(y.success and not x.success for x, y in zip(ra, rb))
    both = [(x, y) for x, y in zip(ra, rb) if x.success and y.success]
    dcyc = np.array([y.cycle_time_s - x.cycle_time_s for x, y in both])
    dret = np.array([y.retries - x.retries for x, y in zip(ra, rb)], dtype=float)
    differ = sum(x.cycle_time_s != y.cycle_time_s or x.success != y.success for x, y in zip(ra, rb))

    def cyc(rs):
        ok = [r.cycle_time_s for r in rs if r.success]
        return {"median": float(np.median(ok)) if ok else None, "p95": float(np.percentile(ok, 95)) if ok else None,
                "mean": float(np.mean(ok)) if ok else None}

    return {
        "pairs": len(keys), "trials_that_differ": int(differ),
        "success": {"reference": sum(x.success for x in ra), "other": sum(y.success for y in rb)},
        "reference_only_success": int(ref_only), "other_only_success": int(oth_only),
        "mcnemar_p": mcnemar_exact(ref_only, oth_only),
        "bad_units_passed": {"reference": sum(is_escape(x) for x in ra), "other": sum(is_escape(y) for y in rb)},
        "protective_stops": {"reference": sum(x.protective_stop for x in ra), "other": sum(y.protective_stop for y in rb)},
        "mean_retries": {"reference": float(np.mean([x.retries for x in ra])) if ra else None,
                         "other": float(np.mean([y.retries for y in rb])) if rb else None},
        "retries_diff_mean": float(dret.mean()) if dret.size else None, "retries_diff_ci95": _boot_ci(dret),
        "cycle_s": {"reference": cyc(ra), "other": cyc(rb)},
        "cycle_diff_both_success_mean_s": float(dcyc.mean()) if dcyc.size else None,
        "cycle_diff_both_success_ci95_s": _boot_ci(dcyc), "both_success": len(both),
    }


def paired_report(results: list[TrialResult], reference: str = "adaptive") -> dict:
    by: dict[str, list[TrialResult]] = defaultdict(list)
    for r in results:
        by[r.controller].append(r)
    if reference not in by:
        raise SystemExit(f"no '{reference}' trials to pair against")
    conds = list(dict.fromkeys(r.condition for r in results))
    out = {}
    for ctl, rs in by.items():
        if ctl == reference:
            continue
        out[ctl] = {"overall": _cell(by[reference], rs),
                    "by_condition": {c: _cell([r for r in by[reference] if r.condition == c],
                                              [r for r in rs if r.condition == c]) for c in conds}}
    return out


def _fmt(x, f="{:.2f}"):
    return "n/a" if x is None else f.format(x)


def paired_markdown(rep: dict, reference: str = "adaptive") -> str:
    lines = []
    for ctl, d in rep.items():
        lines += [f"### {ctl} vs {reference} (paired)", "",
                  "| Condition | Pairs | Differ | Success C / G | C-only / G-only (McNemar p) | Bad units C / G | "
                  "Stops C / G | Mean retries C / G (diff, 95% CI) | Median cycle C / G (s) | p95 cycle C / G (s) | "
                  "Cycle diff, both succeeded (s, 95% CI) |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
        for name, c in [*d["by_condition"].items(), ("all", d["overall"])]:
            ci = c["retries_diff_ci95"]
            cc = c["cycle_diff_both_success_ci95_s"]
            lines.append(
                f"| {name} | {c['pairs']} | {c['trials_that_differ']} | {c['success']['reference']} / {c['success']['other']} | "
                f"{c['reference_only_success']} / {c['other_only_success']} ({c['mcnemar_p']:.2g}) | "
                f"{c['bad_units_passed']['reference']} / {c['bad_units_passed']['other']} | "
                f"{c['protective_stops']['reference']} / {c['protective_stops']['other']} | "
                f"{_fmt(c['mean_retries']['reference'])} / {_fmt(c['mean_retries']['other'])} "
                f"({_fmt(c['retries_diff_mean'], '{:+.2f}')}, {_fmt(ci and ci[0], '{:+.2f}')} to {_fmt(ci and ci[1], '{:+.2f}')}) | "
                f"{_fmt(c['cycle_s']['reference']['median'])} / {_fmt(c['cycle_s']['other']['median'])} | "
                f"{_fmt(c['cycle_s']['reference']['p95'])} / {_fmt(c['cycle_s']['other']['p95'])} | "
                f"{_fmt(c['cycle_diff_both_success_mean_s'], '{:+.2f}')} "
                f"({_fmt(cc and cc[0], '{:+.2f}')} to {_fmt(cc and cc[1], '{:+.2f}')}) |")
        lines.append("")
    return "\n".join(lines)


def write_paired(results: list[TrialResult], out: Path) -> dict:
    rep = paired_report(results)
    (out / "paired.json").write_text(json.dumps(rep, indent=2))
    (out / "paired.md").write_text(paired_markdown(rep))
    return rep


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("variants", type=Path, nargs="?")
    ap.add_argument("--analyze", type=Path, help="write paired.json/paired.md for an existing run directory")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--conditions", default="noise_0.5mm,noise_1mm,noise_2mm,mf_noise_1mm")
    ap.add_argument("--trials", type=int, default=60)
    ap.add_argument("--name")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--backend", choices=["gantry", "arm"], default="gantry")
    args = ap.parse_args()
    if args.analyze:
        d = args.analyze.resolve()
        print(paired_markdown(write_paired(read_trials_csv(d / "trials.csv"), d)))
        return
    if args.variants is None or args.seed is None or not args.name:
        raise SystemExit("need variants.json, --seed and --name (or --analyze DIR)")
    check_seed(args.seed)
    os.environ["DEFEX_BACKEND"] = args.backend
    variants = json.loads(args.variants.read_text())
    if "adaptive" not in variants:
        raise SystemExit("variants must include C as 'adaptive' (the paired reference)")
    conds = [c for c in args.conditions.split(",") if c]
    out = OUT / args.name
    out.mkdir(parents=True, exist_ok=True)
    jobs = [(v, spec, c, args.seed, tuple(range(a, min(a + 5, args.trials))))
            for c in conds for v, spec in variants.items() for a in range(0, args.trials, 5)]
    t0 = time.time()
    results: list[TrialResult] = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = [pool.submit(_job, *j) for j in jobs]
        for n, f in enumerate(as_completed(futs), 1):
            results += f.result()
            if n % 20 == 0 or n == len(futs):
                print(f"  {len(results)} trials, {time.time() - t0:.0f} s", flush=True)
    corder = {c: i for i, c in enumerate(conds)}
    vorder = {v: i for i, v in enumerate(variants)}
    results.sort(key=lambda r: (corder[r.condition], vorder[r.controller], r.trial_index))
    write_outputs(results, out, wall_time_s=time.time() - t0)
    (out / "variants.json").write_text(json.dumps(variants, indent=2))
    (out / "config.json").write_text(json.dumps({
        "description": "W9 development measurement (paired G vs C), not a reported benchmark",
        "base_seed": args.seed, "conditions": conds, "trials": args.trials, "backend": args.backend,
        "variants": variants, "environment": environment_info(),
    }, indent=2))
    print(paired_markdown(write_paired(results, out)))


if __name__ == "__main__":
    main()
