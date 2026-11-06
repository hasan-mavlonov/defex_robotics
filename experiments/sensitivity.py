"""One-at-a-time sensitivity of controller C to every constant in AdaptiveConfig.

Each numeric field is scaled by 0.5, 0.8, 1.2 and 1.5 (integers rounded, at
least 1) with all others at their defaults, and C runs on a fixed development
subset. A constant is flagged as a cliff when a +/-20% change costs more than
10 points of success; +/-50% changes are reported but not flagged.

    python -m experiments.sensitivity                 # full sweep, development seed 2026
    python -m experiments.evaluate ... (not needed; this script writes its own plot)

Output: results/<out>/sensitivity.csv, sensitivity.json and sensitivity.png.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import fields, replace
from pathlib import Path

import numpy as np

from defex.config import REPO_ROOT, AdaptiveConfig
from defex.control.adaptive_fsm import AdaptiveInsertionController
from defex.tasks.conditions import conditions_by_name
from defex.tasks.insertion import InsertionTask
from defex.tasks.scenarios import sample_scenario
from experiments.runner import default_workers, nominal_socket_pose

DEV_SEED = 2026
CONDITIONS = ("noise_1mm", "noise_2mm", "friction_1")
SCALES = (0.5, 0.8, 1.2, 1.5)
CLIFF_POINTS = 10.0

_TASK: InsertionTask | None = None


def numeric_fields() -> list[str]:
    return [f.name for f in fields(AdaptiveConfig) if f.type in ("float", "int")]


def perturbed(name: str, scale: float) -> dict:
    base = getattr(AdaptiveConfig(), name)
    if isinstance(base, int):
        return {name: max(1, int(round(base * scale)))}
    return {name: base * scale}


def _job(overrides: dict, cond_name: str, indices: tuple[int, ...]) -> list[tuple[bool, float, str]]:
    global _TASK
    if _TASK is None:
        _TASK = InsertionTask()
    cond = conditions_by_name()[cond_name]
    nominal = nominal_socket_pose(cond, _TASK.fixture)
    out = []
    for i in indices:
        try:
            ctrl = AdaptiveInsertionController(replace(AdaptiveConfig(), **overrides))
            r = _TASK.run(ctrl, sample_scenario(cond, i, DEV_SEED, nominal))
            out.append((r.success, r.cycle_time_s, r.failure_reason))
        except Exception as exc:  # noqa: BLE001 - a crash under perturbation is a result, not an abort
            out.append((False, float("nan"), f"crash:{type(exc).__name__}"))
    return out


def plot(rows: list[dict], base_rate: float, path: Path, top: int = 30) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = sorted({r["field"] for r in rows})
    worst = {n: min(r["success_rate"] for r in rows if r["field"] == n) for n in names}
    names = sorted(names, key=lambda n: worst[n])[:top]
    grid = np.array([[next(r["success_rate"] for r in rows if r["field"] == n and r["scale"] == s) for s in SCALES]
                     for n in names]) * 100
    fig, ax = plt.subplots(figsize=(7.5, 0.28 * len(names) + 1.6), dpi=150)
    im = ax.imshow(grid, cmap="RdYlGn", vmin=max(0, base_rate * 100 - 40), vmax=100, aspect="auto")
    ax.set_xticks(range(len(SCALES)), [f"{int(round((s - 1) * 100)):+d}%" for s in SCALES])
    ax.set_yticks(range(len(names)), names, fontsize=7)
    for i in range(len(names)):
        for j in range(len(SCALES)):
            ax.text(j, i, f"{grid[i, j]:.0f}", ha="center", va="center", fontsize=6.5)
    ax.set_title(f"C success under one-at-a-time perturbation ({top} most sensitive constants)\n"
                 f"baseline {base_rate * 100:.1f}% on {', '.join(CONDITIONS)}, dev seed {DEV_SEED}", fontsize=8.5)
    fig.colorbar(im, ax=ax, label="success (%)", shrink=0.6)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--fields", default="", help="comma-separated subset of AdaptiveConfig fields")
    ap.add_argument("--out", default="sensitivity_v0.2")
    ap.add_argument("--workers", type=int, default=default_workers())
    args = ap.parse_args()
    names = args.fields.split(",") if args.fields else numeric_fields()
    settings = [("baseline", 1.0, {})] + [(n, s, perturbed(n, s)) for n in names for s in SCALES]
    out = REPO_ROOT / "results" / args.out
    out.mkdir(parents=True, exist_ok=True)
    total = len(settings) * len(CONDITIONS) * args.trials
    print(f"{len(settings)} settings x {len(CONDITIONS)} conditions x {args.trials} trials = {total} trials")
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = [(k, pool.submit(_job, ov, c, tuple(range(args.trials))))
                for k, (_, _, ov) in enumerate(settings) for c in CONDITIONS]
        acc: dict[int, list] = {k: [] for k in range(len(settings))}
        for done, (k, f) in enumerate(futs, 1):
            acc[k] += f.result()
            if done % 100 == 0:
                print(f"  {done}/{len(futs)} jobs, {time.time() - t0:.0f} s", flush=True)
    rows = []
    for k, (name, scale, ov) in enumerate(settings):
        res = acc[k]
        ok = [r for r in res if r[0]]
        rows.append({
            "field": name, "scale": scale, "value": next(iter(ov.values())) if ov else None,
            "default": getattr(AdaptiveConfig(), name) if ov else None,
            "n": len(res), "successes": len(ok), "success_rate": len(ok) / len(res),
            "median_cycle_s": float(np.median([r[1] for r in ok])) if ok else float("nan"),
            "crashes": sum(r[2].startswith("crash") for r in res),
        })
    base = rows[0]["success_rate"]
    for r in rows[1:]:
        r["delta_points"] = 100 * (r["success_rate"] - base)
    cliffs = sorted({r["field"] for r in rows[1:] if r["scale"] in (0.8, 1.2) and r["delta_points"] < -CLIFF_POINTS})
    with (out / "sensitivity.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[1]))
        w.writeheader()
        w.writerows(rows[1:])
    (out / "sensitivity.json").write_text(json.dumps({
        "seed": DEV_SEED, "conditions": CONDITIONS, "trials": args.trials, "scales": SCALES,
        "baseline_success_rate": base, "baseline_median_cycle_s": rows[0]["median_cycle_s"],
        "cliff_rule": f"+/-20% costs more than {CLIFF_POINTS:g} points", "cliffs": cliffs,
    }, indent=2))
    plot(rows[1:], base, out / "sensitivity.png")
    print(f"baseline {base * 100:.1f}%; cliffs: {cliffs}")


if __name__ == "__main__":
    main()
