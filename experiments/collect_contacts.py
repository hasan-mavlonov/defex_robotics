"""Collect C's DETECT contact records and label them offline (W9 learned contact prior).

Runs controller C (or another C-family controller) through the normal harness on
development seeds, keeps the observation-only feature dict C writes at every DETECT
diagnosis (``controller.contact_records``) and attaches, after the trial, the true
mouth offset in the estimated socket frame. The label is computed here from the
scenario's ground truth and the controller's own vision estimate; it never reaches
a controller.

    python -m experiments.collect_contacts --seeds 3001-3030 --trials 20 \\
        --conditions noise_1mm,noise_2mm,mf_noise_1mm --name train --workers 4
    python -m experiments.collect_contacts --backend arm --seeds 3001-3030 ...

Output under results/w9_development/data/<backend>/<name>/: contacts.jsonl.gz (one
JSON object per record: identifiers, the record exactly as the controller wrote it,
``label``), trials.csv (one row per trial, with ``base_seed``), summary.json (counts,
fixture dynamics, environment, arguments).
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict

import numpy as np

from defex.config import DEG, MM, REPO_ROOT
from defex.control.registry import make_controller
from defex.logging.metrics import summarize, summarize_overall, write_csv, write_json
from defex.tasks.conditions import conditions_by_name, latching_conditions_by_name
from defex.tasks.insertion import InsertionTask
from defex.tasks.scenarios import Scenario, sample_scenario
from defex.utils.transforms import axis_angle_between, twist_about_axis
from experiments.runner import environment_info, make_backend, nominal_socket_pose

# Seeds this work may touch (development, training, validation). Everything else is
# refused, in particular the reported runs and the pre-registered Checkpoint 2 seeds.
TRAIN_SEEDS = tuple(range(3001, 3041))
VALIDATION_SEED = 4001
DEV_SEEDS = (2026, 2027)
ALLOWED_SEEDS = frozenset((*DEV_SEEDS, *TRAIN_SEEDS, VALIDATION_SEED))
RESERVED_SEEDS = frozenset((20261024, 20261025, 20261031, 20261102, 20261107, 20261108, 20261109))

# Families where C blocks often enough to produce contacts (W9 development choice).
BLOCKING_FAMILIES = ("noise_0.5mm", "noise_1mm", "noise_2mm", "friction_0.6", "friction_1", "lateral_3mm",
                     "yaw_5deg", "tilt_5deg", "mf_noise_1mm")

_TASK: InsertionTask | None = None


def check_seed(seed: int) -> int:
    if seed in RESERVED_SEEDS or seed not in ALLOWED_SEEDS:
        raise SystemExit(f"seed {seed} is not a W9 development/training/validation seed; refusing to run it")
    return seed


def parse_seeds(text: str) -> list[int]:
    out: list[int] = []
    for part in text.split(","):
        if "-" in part:
            a, b = (int(x) for x in part.split("-"))
            out += list(range(a, b + 1))
        elif part:
            out.append(int(part))
    return [check_seed(s) for s in out]


def all_conditions() -> dict:
    return {**conditions_by_name(), **latching_conditions_by_name()}


def offline_label(scenario: Scenario, controller) -> dict:
    """True mouth offset in the controller's estimated socket frame (ground truth: offline only)."""
    S = controller.S  # the vision estimate C used for the whole trial
    rel = S.inv() @ scenario.socket_pose
    G_est = controller.G
    # In-hand estimate error at the tip, expressed in the estimated socket frame (connector aligned
    # with it): the part of the plug-to-hole offset the label alone does not carry (about 0.1 mm).
    grasp_err = G_est.R.T @ (scenario.grasp_offset.p - G_est.p)
    return {
        "x_mm": float(rel.p[0] / MM),
        "y_mm": float(rel.p[1] / MM),
        "z_mm": float(rel.p[2] / MM),
        "yaw_deg": float(twist_about_axis(rel.R) / DEG),
        "tilt_deg": float(axis_angle_between(rel.R[:, 2], np.array([0.0, 0.0, 1.0])) / DEG),
        "grasp_err_xy_mm": (grasp_err[:2] / MM).tolist(),
    }


def _job(controller: str, cond_name: str, base_seed: int, idx: tuple[int, ...]):
    global _TASK
    if _TASK is None:
        os.environ.setdefault("OMP_NUM_THREADS", "1")
        _TASK = InsertionTask(backend=make_backend())
    task = _TASK
    cond = all_conditions()[cond_name]
    nominal = nominal_socket_pose(cond, task.fixture)
    results, records = [], []
    for i in idx:
        sc = sample_scenario(cond, i, base_seed, nominal)
        ctl = make_controller(controller)
        res = task.run(ctl, sc)
        results.append((base_seed, res))
        if ctl.S is None:
            continue
        label = offline_label(sc, ctl)
        for k, rec in enumerate(ctl.contact_records):
            records.append({
                "condition": cond_name, "base_seed": base_seed, "trial_index": i, "trial_seed": sc.seed,
                "record_index": k, "n_records": len(ctl.contact_records), "controller": res.controller,
                "trial_success": res.success, "trial_retries": res.retries, "trial_failure": res.failure_reason,
                "record": rec, "label": label,
            })
    fd = getattr(task.backend, "fixture_dynamics", None)
    return results, records, (None if fd is None else asdict(fd))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--backend", choices=["gantry", "arm"], default="gantry")
    ap.add_argument("--seeds", required=True, help="base seeds, e.g. 3001-3030 or 4001")
    ap.add_argument("--conditions", default=",".join(BLOCKING_FAMILIES))
    ap.add_argument("--trials", type=int, default=20, help="trials per base seed and condition")
    ap.add_argument("--controller", default="adaptive")
    ap.add_argument("--name", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--chunk", type=int, default=5)
    args = ap.parse_args()
    os.environ["DEFEX_BACKEND"] = args.backend
    seeds = parse_seeds(args.seeds)
    conds = [c for c in args.conditions.split(",") if c]
    unknown = set(conds) - set(all_conditions())
    if unknown:
        raise SystemExit(f"unknown conditions: {sorted(unknown)}")
    out = REPO_ROOT / "results" / "w9_development" / "data" / args.backend / args.name
    out.mkdir(parents=True, exist_ok=True)
    jobs = [(args.controller, c, s, tuple(range(a, min(a + args.chunk, args.trials))))
            for s in seeds for c in conds for a in range(0, args.trials, args.chunk)]
    total = len(seeds) * len(conds) * args.trials
    print(f"collect: {len(seeds)} seeds x {len(conds)} conditions x {args.trials} trials = {total} trials "
          f"({args.backend}, {args.workers} workers) -> {out}")
    t0 = time.time()
    results, records, fd = [], [], None
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = [pool.submit(_job, *j) for j in jobs]
        for n, f in enumerate(as_completed(futs), 1):
            res, rec, fd_ = f.result()
            results += res
            records += rec
            fd = fd or fd_
            if n % 20 == 0 or n == len(futs):
                el = time.time() - t0
                print(f"  {len(results)}/{total} trials, {len(records)} records, {el:.0f} s", flush=True)
    key = {c: i for i, c in enumerate(conds)}
    results.sort(key=lambda br: (br[0], key[br[1].condition], br[1].trial_index))
    records.sort(key=lambda r: (r["base_seed"], key[r["condition"]], r["trial_index"], r["record_index"]))
    with gzip.open(out / "contacts.jsonl.gz", "wt") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
    write_csv([{"base_seed": b, **r.to_row()} for b, r in results], out / "trials.csv")
    kinds: dict[str, dict[str, int]] = {}
    for r in records:
        kinds.setdefault(r["condition"], {}).setdefault(r["record"]["kind"], 0)
        kinds[r["condition"]][r["record"]["kind"]] += 1
    trial_results = [r for _, r in results]
    write_json({
        "description": "W9 development data: C's DETECT records with offline labels (not a benchmark)",
        "backend": args.backend, "controller": args.controller, "base_seeds": seeds, "conditions": conds,
        "trials_per_seed_and_condition": args.trials, "n_trials": len(results), "n_records": len(records),
        "records_by_condition_and_kind": kinds, "fixture_dynamics": fd,
        "overall": summarize_overall(trial_results), "summary": summarize(trial_results),
        "environment": environment_info(), "wall_time_s": time.time() - t0,
    }, out / "summary.json")
    print(f"wrote {len(records)} records from {len(results)} trials to {out}")


if __name__ == "__main__":
    main()
