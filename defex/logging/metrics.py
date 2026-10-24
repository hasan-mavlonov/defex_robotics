"""Trial results, aggregation and file output.

Every number reported by the experiment scripts is computed here from logged
ground-truth measurements. Success rates carry Wilson score 95% intervals, which
stay well-behaved near 0% and 100% (the regime robotics benchmarks live in).
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

import numpy as np


@dataclass
class TrialResult:
    controller: str
    condition: str
    group: str
    trial_index: int
    seed: int
    success: bool
    failure_reason: str  # "none" on success
    gt_seated: bool
    declared_success: bool | None  # None for controllers that do not self-verify
    cycle_time_s: float
    peak_contact_force_n: float  # ground truth, net contact force on held parts (500 Hz samples)
    peak_measured_force_n: float  # filtered F/T magnitude seen by the controller
    retries: int
    recovered: bool  # succeeded after at least one recovery
    final_depth_mm: float
    final_lateral_mm: float
    final_tilt_deg: float
    final_yaw_deg: float
    max_penetration_mm: float
    protective_stop: bool
    timeout: bool
    friction: float
    vision_sigma_mm: float
    disturbance: dict[str, float] = field(default_factory=dict)
    events: list[tuple[float, str, str]] = field(default_factory=list)
    peak_contact_force_10ms_n: float = 0.0  # ground truth, 10 ms moving average (sustained load)
    sim_time_s: float = 0.0
    wall_time_s: float = 0.0

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row.pop("events")
        dist = row.pop("disturbance")
        for k, v in dist.items():
            row[f"dist_{k}"] = v
        return row


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def _stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {"mean": float("nan"), "median": float("nan"), "p95": float("nan"), "max": float("nan")}
    a = np.asarray(values, dtype=float)
    return {
        "mean": float(a.mean()),
        "median": float(np.median(a)),
        "p95": float(np.percentile(a, 95)),
        "max": float(a.max()),
    }


def summarize(results: Iterable[TrialResult]) -> list[dict[str, Any]]:
    """Aggregate per (condition, controller)."""
    groups: dict[tuple[str, str], list[TrialResult]] = defaultdict(list)
    order: list[tuple[str, str]] = []
    for r in results:
        key = (r.condition, r.controller)
        if key not in groups:
            order.append(key)
        groups[key].append(r)
    out = []
    for key in order:
        rs = groups[key]
        n = len(rs)
        k = sum(r.success for r in rs)
        lo, hi = wilson_interval(k, n)
        succ = [r for r in rs if r.success]
        with_recovery = [r for r in rs if r.retries > 0]
        declared = [r for r in rs if r.declared_success is not None]
        out.append(
            {
                "condition": key[0],
                "group": rs[0].group,
                "controller": key[1],
                "n": n,
                "successes": k,
                "success_rate": k / n,
                "success_ci_low": lo,
                "success_ci_high": hi,
                "cycle_time_s_success": _stats([r.cycle_time_s for r in succ]),
                "cycle_time_s_all": _stats([r.cycle_time_s for r in rs]),
                "peak_contact_force_n": _stats([r.peak_contact_force_n for r in rs]),
                "peak_contact_force_10ms_n": _stats([r.peak_contact_force_10ms_n for r in rs]),
                "peak_measured_force_n": _stats([r.peak_measured_force_n for r in rs]),
                "retries_mean": float(np.mean([r.retries for r in rs])),
                "retries_max": int(max(r.retries for r in rs)),
                "trials_with_recovery": len(with_recovery),
                "recovery_success_rate": (
                    sum(r.success for r in with_recovery) / len(with_recovery) if with_recovery else float("nan")
                ),
                "final_depth_mm": _stats([r.final_depth_mm for r in rs]),
                "max_penetration_mm": float(max(r.max_penetration_mm for r in rs)),
                "protective_stops": int(sum(r.protective_stop for r in rs)),
                "false_accepts": int(sum(1 for r in declared if r.declared_success and not r.gt_seated)),
                "false_rejects": int(sum(1 for r in declared if (r.declared_success is False) and r.gt_seated)),
                "failure_reasons": dict(Counter(r.failure_reason for r in rs if not r.success)),
            }
        )
    return out


def flatten_summary(summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for s in summary:
        row: dict[str, Any] = {}
        for k, v in s.items():
            if isinstance(v, dict) and k != "failure_reasons":
                for kk, vv in v.items():
                    row[f"{k}_{kk}"] = vv
            elif k == "failure_reasons":
                row[k] = "; ".join(f"{kk}:{vv}" for kk, vv in sorted(v.items()))
            else:
                row[k] = v
        rows.append(row)
    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _json_default(o: Any) -> Any:
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"not JSON serializable: {type(o)}")


def write_json(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=_json_default, allow_nan=True))


def read_trials_csv(path: Path) -> list[TrialResult]:
    """Load trial rows back into :class:`TrialResult` objects (for re-plotting)."""
    out = []
    with path.open() as fh:
        for row in csv.DictReader(fh):
            dist = {k[5:]: float(v) for k, v in row.items() if k.startswith("dist_") and v != ""}
            ds = row["declared_success"]
            out.append(
                TrialResult(
                    controller=row["controller"],
                    condition=row["condition"],
                    group=row["group"],
                    trial_index=int(row["trial_index"]),
                    seed=int(row["seed"]),
                    success=row["success"] == "True",
                    failure_reason=row["failure_reason"],
                    gt_seated=row["gt_seated"] == "True",
                    declared_success=None if ds in ("", "None") else ds == "True",
                    cycle_time_s=float(row["cycle_time_s"]),
                    peak_contact_force_n=float(row["peak_contact_force_n"]),
                    peak_measured_force_n=float(row["peak_measured_force_n"]),
                    retries=int(row["retries"]),
                    recovered=row["recovered"] == "True",
                    final_depth_mm=float(row["final_depth_mm"]),
                    final_lateral_mm=float(row["final_lateral_mm"]),
                    final_tilt_deg=float(row["final_tilt_deg"]),
                    final_yaw_deg=float(row["final_yaw_deg"]),
                    max_penetration_mm=float(row["max_penetration_mm"]),
                    protective_stop=row["protective_stop"] == "True",
                    timeout=row["timeout"] == "True",
                    friction=float(row["friction"]),
                    vision_sigma_mm=float(row["vision_sigma_mm"]),
                    disturbance=dist,
                    sim_time_s=float(row.get("sim_time_s", 0.0) or 0.0),
                    peak_contact_force_10ms_n=float(row.get("peak_contact_force_10ms_n", 0.0) or 0.0),
                    wall_time_s=float(row.get("wall_time_s", 0.0) or 0.0),
                )
            )
    return out
