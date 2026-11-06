"""Do the results depend on one tuning of MuJoCo? Re-run the comparison on randomized simulators.

Each variant draws contact and servo parameters uniformly within plausible bands
(below), builds its own workcell, and runs every controller on the same paired
trials. Variant 0 is the nominal simulator. The question is whether the ranking
and the size of C's lead survive, not whether every rate stays put.

    python -m experiments.sim_randomization --variants 12 --trials 20 --seed 20261108

Output: results/<name>/variants.json, trials.csv, summary.json, sim_randomization.png.
"""

from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np

from defex.config import REPO_ROOT, FixtureConfig, SimConfig, to_dict
from defex.control.registry import BENCHMARK_CONTROLLERS as CONTROLLERS
from defex.control.registry import make_controller
from defex.logging.metrics import TrialResult, summarize_overall, write_csv
from defex.tasks.conditions import conditions_by_name
from defex.tasks.insertion import InsertionTask
from defex.tasks.scenarios import sample_scenario
from experiments.evaluate import CONTROLLER_ORDER, LABELS, THEMES
from experiments.runner import default_workers, environment_info, nominal_socket_pose

CONDITIONS = ("nominal", "lateral_3mm", "noise_1mm", "noise_2mm", "friction_1", "generalization_tight")

# Bands (uniform). Normal-contact time constant must stay >= 2 x the 0.5 ms step.
BANDS = {
    "contact_timeconst_s": (0.0015, 0.004),
    "contact_dampratio": (0.7, 1.3),
    "contact_friction_timeconst_s": (0.01, 0.04),
    "solimp_dmin": (0.90, 0.97),
    "solimp_dmax": (0.98, 0.995),
    "solimp_width_m": (0.0001, 0.0005),
    "impratio": (3.0, 20.0),
    "linear_kp_n_per_m": (5000.0, 20000.0),
    "angular_kp_nm_per_rad": (10.0, 25.0),
}
CONES = ("elliptic", "pyramidal")

_TASKS: dict[int, InsertionTask] = {}


def variant_configs(k: int, seed: int) -> tuple[SimConfig, FixtureConfig, dict]:
    sim, fix = SimConfig(), FixtureConfig()
    if k == 0:
        return sim, fix, {"variant": 0, "nominal": True}
    rng = np.random.default_rng([seed, k])
    d = {name: float(rng.uniform(*b)) for name, b in BANDS.items()}
    d["cone"] = CONES[int(rng.integers(2))]
    solimp = (d["solimp_dmin"], d["solimp_dmax"], d["solimp_width_m"], sim.contact_solimp[3], sim.contact_solimp[4])
    sim = replace(
        sim,
        contact_timeconst_s=d["contact_timeconst_s"],
        contact_dampratio=d["contact_dampratio"],
        contact_friction_timeconst_s=d["contact_friction_timeconst_s"],
        contact_solimp=solimp,
        impratio=d["impratio"],
        cone=d["cone"],
    )
    fix = replace(fix, linear_kp_n_per_m=d["linear_kp_n_per_m"], angular_kp_nm_per_rad=d["angular_kp_nm_per_rad"])
    return sim, fix, {"variant": k, "nominal": False, **d}


def _job(k: int, seed: int, ctrl: str, cond_name: str, indices: tuple[int, ...]) -> list[dict]:
    if k not in _TASKS:
        sim, fix, _ = variant_configs(k, seed)
        _TASKS[k] = InsertionTask(sim=sim, fixture=fix)
    task = _TASKS[k]
    cond = conditions_by_name()[cond_name]
    nominal = nominal_socket_pose(cond, task.fixture)
    out = []
    for i in indices:
        r = task.run(make_controller(ctrl), sample_scenario(cond, i, seed, nominal))
        row = r.to_row()
        row["variant"] = k
        out.append(row)
    return out


def _row_to_result(row: dict) -> TrialResult:
    keep = {f: row[f] for f in TrialResult.__dataclass_fields__ if f in row and f not in ("disturbance", "events")}
    return TrialResult(**keep)


def plot(per_variant: dict[int, dict[str, float]], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    th = THEMES["light"]
    ctrls = [c for c in CONTROLLER_ORDER if any(c in v for v in per_variant.values())]
    fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=150, facecolor=th["page"])
    ax.set_facecolor(th["surface"])
    for j, c in enumerate(ctrls):
        ys = [100 * v[c] for k, v in sorted(per_variant.items()) if k != 0]
        xs = j + np.linspace(-0.22, 0.22, len(ys))
        ax.scatter(xs, ys, s=16, color=th["series"][c], alpha=0.85, zorder=3)
        ax.scatter([j], [100 * per_variant[0][c]], s=90, marker="_", color=th["ink"], zorder=4, linewidths=2)
    ax.set_xticks(range(len(ctrls)), [LABELS[c] for c in ctrls], fontsize=7.5, rotation=12)
    ax.set_ylabel("success (%)")
    ax.set_ylim(0, 102)
    ax.grid(axis="y", color=th["grid"], lw=0.6)
    ax.set_title("Success per randomized simulator (dots); nominal simulator (black bar)", fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(path, facecolor=th["page"])
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variants", type=int, default=12, help="randomized variants (variant 0 = nominal is added)")
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--name", default="sim_randomization_v0.2")
    ap.add_argument("--workers", type=int, default=default_workers())
    args = ap.parse_args()
    out = REPO_ROOT / "results" / args.name
    out.mkdir(parents=True, exist_ok=True)
    variants = [variant_configs(k, args.seed)[2] for k in range(args.variants + 1)]
    (out / "variants.json").write_text(json.dumps({
        "seed": args.seed, "conditions": CONDITIONS, "trials": args.trials, "bands": BANDS, "cones": CONES,
        "variants": variants, "environment": environment_info(),
        "nominal_sim": to_dict(SimConfig()), "nominal_fixture": to_dict(FixtureConfig()),
    }, indent=2))
    ctrls = list(CONTROLLERS)
    jobs = [(k, c, cond) for k in range(args.variants + 1) for c in ctrls for cond in CONDITIONS]
    print(f"{len(jobs)} jobs x {args.trials} trials = {len(jobs) * args.trials} trials")
    t0 = time.time()
    rows: list[dict] = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = [pool.submit(_job, k, args.seed, c, cond, tuple(range(args.trials))) for k, c, cond in jobs]
        for n, f in enumerate(futs, 1):
            rows += f.result()
            if n % 50 == 0:
                print(f"  {n}/{len(futs)} jobs, {time.time() - t0:.0f} s", flush=True)
    write_csv(rows, out / "trials.csv")
    per_variant: dict[int, dict[str, float]] = {}
    summary = {}
    for k in range(args.variants + 1):
        res = [_row_to_result(r) for r in rows if r["variant"] == k]
        ov = summarize_overall(res)
        summary[k] = ov
        per_variant[k] = {o["controller"]: o["success_rate"] for o in ov}
    gaps = {k: v["adaptive"] - max(v[c] for c in ("spiral", "correction_rcc", "spiral_rcc")) for k, v in per_variant.items()}
    (out / "summary.json").write_text(json.dumps({
        "per_variant_success": per_variant, "c_minus_best_fair_baseline": gaps,
        "overall_per_variant": summary, "wall_time_s": time.time() - t0,
    }, indent=2, default=float))
    plot(per_variant, out / "sim_randomization.png")
    print("C minus best of D/E/F, per variant (points):", {k: round(100 * g, 1) for k, g in gaps.items()})


if __name__ == "__main__":
    main()
