"""Parallel, reproducible experiment runner shared by the experiment scripts.

Every trial is fully determined by (base seed, condition name, trial index,
controller), so results do not depend on how trials are distributed across worker
processes. Each worker owns one :class:`~defex.tasks.insertion.InsertionTask`
(and therefore one MuJoCo model cache).
"""

from __future__ import annotations

import gzip
import json
import os
import platform
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np

from defex.config import REPO_ROOT, Condition, FixtureConfig, SafetyConfig, SimConfig, SuccessCriteria, to_dict
from defex.control.registry import make_controller
from defex.logging.metrics import TrialResult, flatten_summary, summarize, write_csv, write_json
from defex.sim.scene_builder import WorkcellLayout
from defex.tasks.insertion import InsertionTask, TrajectoryRecorder
from defex.tasks.scenarios import resolve_connector, sample_scenario
from defex.utils.transforms import Pose

_TASK: InsertionTask | None = None


@dataclass(frozen=True)
class Job:
    condition: Condition
    controller: str
    trial_indices: tuple[int, ...]
    base_seed: int
    record: bool
    traj_dir: str | None


def nominal_socket_pose(condition: Condition, fixture: FixtureConfig) -> Pose:
    layout = WorkcellLayout.from_spec(resolve_connector(condition), fixture)
    return Pose(layout.socket_mouth.copy(), np.eye(3))


def _init_worker() -> None:
    global _TASK
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    _TASK = InsertionTask()


def save_trajectory(path: Path, recorder: TrajectoryRecorder, result: TrialResult, scenario) -> None:
    arrays = recorder.to_arrays()
    meta = {
        "controller": result.controller,
        "condition": result.condition,
        "trial_index": result.trial_index,
        "seed": result.seed,
        "success": result.success,
        "failure_reason": result.failure_reason,
        "socket_pose": scenario.socket_pose.as_array().tolist(),
        "grasp_offset": scenario.grasp_offset.as_array().tolist(),
        "friction": scenario.friction,
        "connector": to_dict(scenario.connector),
        "events": result.events,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, meta=json.dumps(meta), **arrays)


def _run_job(job: Job) -> list[TrialResult]:
    global _TASK
    if _TASK is None:
        _init_worker()
    task = _TASK
    out = []
    nominal = nominal_socket_pose(job.condition, task.fixture)
    for i in job.trial_indices:
        scenario = sample_scenario(job.condition, i, job.base_seed, nominal)
        controller = make_controller(job.controller)
        recorder = TrajectoryRecorder() if job.record else None
        result = task.run(controller, scenario, recorder=recorder)
        if recorder is not None and job.traj_dir:
            fname = f"{job.condition.name}__{job.controller}__{i:03d}.npz"
            save_trajectory(Path(job.traj_dir) / fname, recorder, result, scenario)
        out.append(result)
    return out


def git_revision() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def environment_info() -> dict:
    import matplotlib
    import mujoco

    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "mujoco": mujoco.__version__,
        "numpy": np.__version__,
        "matplotlib": matplotlib.__version__,
        "git_commit": git_revision(),
        "cpu_count": os.cpu_count(),
    }


def run_suite(
    conditions: Iterable[Condition],
    controllers: Iterable[str],
    n_trials: int,
    base_seed: int,
    workers: int,
    out_dir: Path,
    record_trajectories: int = 0,
    chunk: int = 5,
    progress: bool = True,
) -> list[TrialResult]:
    conditions = list(conditions)
    controllers = list(controllers)
    out_dir.mkdir(parents=True, exist_ok=True)
    traj_dir = out_dir / "trajectories" if record_trajectories > 0 else None
    jobs: list[Job] = []
    for cond in conditions:
        for ctrl in controllers:
            idx = list(range(n_trials))
            rec_idx = [i for i in idx if i < record_trajectories]
            plain = [i for i in idx if i >= record_trajectories]
            if rec_idx:
                jobs.append(Job(cond, ctrl, tuple(rec_idx), base_seed, True, str(traj_dir)))
            for k in range(0, len(plain), chunk):
                jobs.append(Job(cond, ctrl, tuple(plain[k : k + chunk]), base_seed, False, None))
    total = sum(len(j.trial_indices) for j in jobs)
    started = time.time()
    meta = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "n_trials_per_condition": n_trials,
        "base_seed": base_seed,
        "controllers": controllers,
        "conditions": [to_dict(c) for c in conditions],
        "sim": to_dict(SimConfig()),
        "fixture": to_dict(FixtureConfig()),
        "safety": to_dict(SafetyConfig()),
        "success_criteria": to_dict(SuccessCriteria()),
        "environment": environment_info(),
        "workers": workers,
    }
    write_json(meta, out_dir / "config.json")
    results: list[TrialResult] = []
    done = 0
    if workers <= 1:
        _init_worker()
        for job in jobs:
            res = _run_job(job)
            results.extend(res)
            done += len(res)
            if progress:
                _progress(done, total, started)
    else:
        with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker) as pool:
            futures = [pool.submit(_run_job, j) for j in jobs]
            for fut in as_completed(futures):
                res = fut.result()
                results.extend(res)
                done += len(res)
                if progress:
                    _progress(done, total, started)
    if progress:
        print()
    order = {c.name: i for i, c in enumerate(conditions)}
    corder = {c: i for i, c in enumerate(controllers)}
    results.sort(key=lambda r: (order[r.condition], corder[r.controller], r.trial_index))
    write_outputs(results, out_dir, wall_time_s=time.time() - started)
    return results


def write_outputs(results: list[TrialResult], out_dir: Path, wall_time_s: float | None = None) -> None:
    write_csv([r.to_row() for r in results], out_dir / "trials.csv")
    summary = summarize(results)
    write_json({"summary": summary, "wall_time_s": wall_time_s}, out_dir / "summary.json")
    write_csv(flatten_summary(summary), out_dir / "summary.csv")
    events = {f"{r.condition}|{r.controller}|{r.trial_index}": r.events for r in results}
    with gzip.open(out_dir / "events.json.gz", "wt") as fh:
        json.dump(events, fh)


def _progress(done: int, total: int, started: float) -> None:
    el = time.time() - started
    rate = done / max(el, 1e-6)
    eta = (total - done) / max(rate, 1e-6)
    sys.stdout.write(f"\r  {done}/{total} trials  {rate:5.1f} trials/s  elapsed {el:6.0f}s  eta {eta:6.0f}s")
    sys.stdout.flush()


def default_workers() -> int:
    return max(1, (os.cpu_count() or 2) - 1)
