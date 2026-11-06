"""Paired runs of C / G variants that differ only in AdaptiveConfig values (v0.2c development).

    python -m experiments.v02c_variants variants.json --suite latching --seed 4002 --trials 20 \\
        --backend gantry --name v0.2c_defect_verdict/validation/gantry --workers 3

``variants.json`` maps a variant name to {"controller": "adaptive" | "adaptive_learned",
"overrides": {AdaptiveConfig field: value}}. Every variant faces the same trials (paired
seeds). Seeds: development 2026/2027, training 3001-3030 and 3033-3040, validation 4002.
Writes trials.csv, summary.json, events.json.gz (the runner's format), variants.json and
config.json under results/<name>/.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import replace
from pathlib import Path

from defex.config import REPO_ROOT, AdaptiveConfig
from defex.control.adaptive_fsm import AdaptiveInsertionController
from defex.control.adaptive_learned import AdaptiveLearnedController
from defex.logging.metrics import TrialResult
from defex.tasks.conditions import latching_conditions, standard_conditions
from defex.tasks.insertion import InsertionTask
from defex.tasks.scenarios import sample_scenario
from experiments.runner import environment_info, make_backend, nominal_socket_pose, write_outputs

ALLOWED_SEEDS = {2026, 2027, 4002} | set(range(3001, 3031)) | set(range(3033, 3041))
_TASK: InsertionTask | None = None


def build(name: str, spec: dict):
    cfg = replace(AdaptiveConfig(), **spec.get("overrides", {}))
    if spec["controller"] == "adaptive":
        ctl = AdaptiveInsertionController(cfg)
    elif spec["controller"] == "adaptive_learned":
        ctl = AdaptiveLearnedController(cfg)
    else:
        raise ValueError(f"unknown controller {spec['controller']}")
    ctl.name = name
    return ctl


def _conditions(suite: str):
    return {c.name: c for c in (latching_conditions() if suite == "latching" else standard_conditions())}


def _job(name: str, spec: dict, suite: str, cond_name: str, seed: int, idx: tuple[int, ...]) -> list[TrialResult]:
    global _TASK
    if _TASK is None:
        os.environ.setdefault("OMP_NUM_THREADS", "1")
        _TASK = InsertionTask(backend=make_backend())
    cond = _conditions(suite)[cond_name]
    nominal = nominal_socket_pose(cond, _TASK.fixture)
    return [_TASK.run(build(name, spec), sample_scenario(cond, i, seed, nominal)) for i in idx]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("variants", type=Path)
    ap.add_argument("--suite", choices=["latching", "standard"], default="latching")
    ap.add_argument("--conditions", default="")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--name", required=True)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--backend", choices=["gantry", "arm"], default="gantry")
    args = ap.parse_args()
    if args.seed not in ALLOWED_SEEDS:
        raise SystemExit(f"seed {args.seed} is not a v0.2c development, training or validation seed")
    os.environ["DEFEX_BACKEND"] = args.backend
    variants = json.loads(args.variants.read_text())
    for spec in variants.values():
        replace(AdaptiveConfig(), **spec.get("overrides", {}))  # fail early on unknown fields
    conds = [c for c in args.conditions.split(",") if c] or list(_conditions(args.suite))
    out = REPO_ROOT / "results" / args.name
    out.mkdir(parents=True, exist_ok=True)
    jobs = [(v, spec, args.suite, c, args.seed, tuple(range(a, min(a + 5, args.trials))))
            for c in conds for v, spec in variants.items() for a in range(0, args.trials, 5)]
    t0 = time.time()
    results: list[TrialResult] = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = [pool.submit(_job, *j) for j in jobs]
        for n, f in enumerate(as_completed(futs), 1):
            results += f.result()
            if n % 10 == 0 or n == len(futs):
                print(f"  {len(results)} trials, {time.time() - t0:.0f} s", flush=True)
    corder = {c: i for i, c in enumerate(conds)}
    vorder = {v: i for i, v in enumerate(variants)}
    results.sort(key=lambda r: (corder[r.condition], vorder[r.controller], r.trial_index))
    write_outputs(results, out, wall_time_s=time.time() - t0)
    (out / "variants.json").write_text(json.dumps(variants, indent=2))
    (out / "config.json").write_text(json.dumps({
        "description": "v0.2c development measurement (paired variants), not a reported benchmark",
        "base_seed": args.seed, "suite": args.suite, "conditions": conds, "n_trials_per_condition": args.trials,
        "backend": args.backend, "variants": variants, "environment": environment_info(),
    }, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
