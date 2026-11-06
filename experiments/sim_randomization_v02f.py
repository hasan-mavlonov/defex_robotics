"""v0.2f simulator randomization: the current comparisons on randomized MuJoCo simulators.

Like experiments/sim_randomization.py (v0.2a, gantry, standard conditions), but for either
machine, any suite and any controllers, with per-cell trial counts. Variant 0 is the
nominal simulator: its rows equal experiments.robustness rows for the same seed, conditions
and trials (tests/test_sim_randomization_v02f.py). Variants 1..K draw:

* contact parameters from experiments.sim_randomization.BANDS and CONES, the same draw for
  the same (seed, k) on both machines;
* gantry: the linear and wrist servo stiffness from the same BANDS (unchanged from v0.2a);
* arm: ARM_BANDS, a stiffness factor for the shoulder and elbow servos, one for the three
  wrist servos (each joint's damping scaled by the square root, so its damping ratio stays
  as Menagerie's, as the gantry keeps its dampratio), and the command latency.

Controllers are told the drawn servo stiffness and latency through the fixture dynamics
the backend reports, as on the nominal machines; they are not told the contact parameters.
G (adaptive_learned) looks its model up by those fixture dynamics within 1%, so on every
randomized variant it would find none and run as C. By default (``--g-model pinned``) G
runs the machine's one nominal model whatever the fixture reports; ``--g-model lookup``
keeps the as-built lookup. On variant 0 both give the same rows.

    python -m experiments.sim_randomization_v02f --backend gantry --variants 12 --seed S --workers 4 \\
        --cells standard:noise_1mm:20,latching:mf_noise_1mm:20 \\
        --controllers adaptive,spiral_rcc --name sim_randomization_v0.2f/gantry
    python -m experiments.sim_randomization_v02f --analyse results/sim_randomization_v0.2f

Output: results/<name>/variants.json, config.json, trials.csv (one row per trial: variant,
suite, the drawn parameters as sim_* columns, and every TrialResult column), summary.csv,
events.json.gz (keyed "variant|condition|controller|trial_index").
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

from defex.config import REPO_ROOT, Condition, FixtureConfig, LearnedPriorConfig, SimConfig, to_dict
from defex.control.registry import make_controller
from defex.logging.metrics import write_csv, write_json
from defex.tasks.conditions import heldout_conditions, latch_spread_conditions, latching_conditions, standard_conditions
from defex.tasks.insertion import InsertionTask
from defex.tasks.scenarios import sample_scenario
from experiments.runner import environment_info, nominal_socket_pose
from experiments.sim_randomization import BANDS, CONES, variant_configs

SUITES = {"standard": standard_conditions, "heldout": heldout_conditions, "latching": latching_conditions,
          "latch_spread": latch_spread_conditions}

# Arm servo bands (uniform in log for the factors, so the median is the nominal model; uniform for
# latency). Factor 0.5-2 on the joint stiffness is the gantry band's span around its nominal
# (5-20 N/mm around 10). Latency 4-8 ms is the brief's W5 band around the 6 ms default.
ARM_BANDS = {
    "arm_shoulder_elbow_kp_scale": (0.5, 2.0),
    "arm_wrist_kp_scale": (0.5, 2.0),
    "arm_latency_s": (0.004, 0.008),
}
_LOG_UNIFORM = ("arm_shoulder_elbow_kp_scale", "arm_wrist_kp_scale")
SHOULDER_ELBOW = ("shoulder_pan", "shoulder_lift", "elbow")
WRIST = ("wrist_1", "wrist_2", "wrist_3")
GANTRY_SERVO = ("linear_kp_n_per_m", "angular_kp_nm_per_rad")
CONTACT = ("contact_timeconst_s", "contact_dampratio", "contact_friction_timeconst_s", "solimp_dmin", "solimp_dmax",
           "solimp_width_m", "impratio", "cone")


@dataclass(frozen=True)
class Variant:
    k: int
    sim: SimConfig
    fixture: FixtureConfig
    arm_latency_s: float | None = None
    shoulder_elbow_scale: float = 1.0
    wrist_scale: float = 1.0

    def params(self, backend: str) -> dict:
        """The effective simulator parameters of this variant (nominal values on variant 0)."""
        s = self.sim
        d = {
            "contact_timeconst_s": s.contact_timeconst_s, "contact_dampratio": s.contact_dampratio,
            "contact_friction_timeconst_s": s.contact_friction_timeconst_s, "solimp_dmin": s.contact_solimp[0],
            "solimp_dmax": s.contact_solimp[1], "solimp_width_m": s.contact_solimp[2], "impratio": s.impratio,
            "cone": s.cone,
        }
        if backend == "gantry":
            d.update(linear_kp_n_per_m=self.fixture.linear_kp_n_per_m,
                     angular_kp_nm_per_rad=self.fixture.angular_kp_nm_per_rad)
        else:
            d.update(arm_shoulder_elbow_kp_scale=self.shoulder_elbow_scale, arm_wrist_kp_scale=self.wrist_scale,
                     arm_latency_s=self.arm_latency_s)
        return d


def draw_variant(k: int, seed: int, backend: str) -> Variant:
    """Variant k. Contact (and gantry servo) draws are experiments.sim_randomization's, unchanged."""
    sim, fix, _ = variant_configs(k, seed)
    if backend == "gantry":
        return Variant(k, sim, fix)
    from defex.sim.arm_backend import ArmConfig

    nominal_latency = ArmConfig().latency_s
    if k == 0:
        return Variant(0, sim, FixtureConfig(), nominal_latency)
    rng = np.random.default_rng([seed, k, 1])  # own stream: the contact draw stays the gantry's
    d = {}
    for name, (lo, hi) in ARM_BANDS.items():
        d[name] = float(math.exp(rng.uniform(math.log(lo), math.log(hi)))) if name in _LOG_UNIFORM \
            else float(rng.uniform(lo, hi))
    # The arm has no gantry servos: keep FixtureConfig nominal (layout, motion limits).
    return Variant(k, sim, FixtureConfig(), d["arm_latency_s"], d["arm_shoulder_elbow_kp_scale"],
                   d["arm_wrist_kp_scale"])


def scale_arm_servos(model, shoulder_elbow: float, wrist: float) -> None:
    """Joint stiffness x factor and damping x sqrt(factor) (same damping ratio), in place."""
    for names, s in ((SHOULDER_ELBOW, shoulder_elbow), (WRIST, wrist)):
        for n in names:
            a = model.actuator("ur_" + n).id
            model.actuator_gainprm[a, 0] *= s
            model.actuator_biasprm[a, 1] *= s
            model.actuator_biasprm[a, 2] *= math.sqrt(s)


def make_arm_backend(v: Variant):
    from defex.sim.arm_backend import ArmConfig, MuJoCoArmBackend

    if v.k == 0:
        return MuJoCoArmBackend()  # exactly what experiments.runner builds

    class ServoScaledArmBackend(MuJoCoArmBackend):
        def __init__(self) -> None:
            super().__init__(v.sim, v.fixture, ArmConfig(latency_s=v.arm_latency_s))
            self._scaled: set[int] = set()

        def _index_model(self) -> None:
            m = self.model
            if id(m) not in self._scaled:  # each compiled model once (models stay cached)
                scale_arm_servos(m, v.shoulder_elbow_scale, v.wrist_scale)
                self._scaled.add(id(m))
            super()._index_model()

    return ServoScaledArmBackend()


def make_task(v: Variant, backend: str) -> InsertionTask:
    if backend == "gantry":
        return InsertionTask() if v.k == 0 else InsertionTask(sim=v.sim, fixture=v.fixture)
    return InsertionTask(backend=make_arm_backend(v)) if v.k == 0 else \
        InsertionTask(sim=v.sim, fixture=v.fixture, backend=make_arm_backend(v))


def make_g_pinned(backend: str):
    """G with the machine's nominal model, whatever fixture dynamics the variant reports."""
    from defex.control.adaptive_learned import AdaptiveLearnedController

    path = REPO_ROOT / "assets" / "models" / f"contact_prior_{backend}.json"
    return AdaptiveLearnedController(prior_cfg=replace(LearnedPriorConfig(), fixture_match_rel_tol=math.inf),
                                     model_path=path)


def build_controller(name: str, backend: str, g_model: str):
    if name == "adaptive_learned" and g_model == "pinned":
        return make_g_pinned(backend)
    return make_controller(name)


def all_conditions() -> dict[tuple[str, str], Condition]:
    return {(s, c.name): c for s, f in SUITES.items() for c in f()}


def parse_cells(text: str) -> list[tuple[str, str, int]]:
    """'suite:condition:trials,...' -> [(suite, condition, trials)]."""
    known = all_conditions()
    cells = []
    for item in filter(None, (t.strip() for t in text.split(","))):
        parts = item.split(":")
        if len(parts) != 3:
            raise SystemExit(f"cell {item!r}: expected suite:condition:trials")
        suite, cond, n = parts
        if (suite, cond) not in known:
            raise SystemExit(f"unknown cell {suite}:{cond} "
                             f"(see python -m experiments.robustness --suite {suite} --list)")
        cells.append((suite, cond, int(n)))
    return cells


# --------------------------------------------------------------------------- workers
_TASKS: dict[tuple[str, int, int], InsertionTask] = {}  # (backend, seed, variant)


def _init_worker(backend: str) -> None:
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ["DEFEX_BACKEND"] = backend


def run_job(k: int, seed: int, backend: str, suite: str, cond_name: str, ctrl: str, indices: tuple[int, ...],
            g_model: str = "pinned") -> list[tuple[dict, list]]:
    v = draw_variant(k, seed, backend)
    key = (backend, seed, k)
    if key not in _TASKS:
        _TASKS[key] = make_task(v, backend)
    task = _TASKS[key]
    cond = all_conditions()[(suite, cond_name)]
    nominal = nominal_socket_pose(cond, task.fixture)
    extra = {"variant": k, "suite": suite, **{f"sim_{n}": x for n, x in v.params(backend).items()}}
    out = []
    for i in indices:
        r = task.run(build_controller(ctrl, backend, g_model), sample_scenario(cond, i, seed, nominal))
        out.append(({**r.to_row(), **extra}, r.events))
    return out


def run(backend: str, cells: list[tuple[str, str, int]], controllers: list[str], variants: list[int], seed: int,
        workers: int, out: Path, g_model: str = "pinned", chunk: int = 5) -> list[dict]:
    out.mkdir(parents=True, exist_ok=True)
    os.environ["DEFEX_BACKEND"] = backend
    vs = [draw_variant(k, seed, backend) for k in variants]
    write_json({
        "seed": seed, "backend": backend, "cells": cells, "controllers": controllers, "variants": variants,
        "bands": BANDS, "cones": CONES, "arm_bands": ARM_BANDS if backend == "arm" else None,
        "draws": [{"variant": v.k, **v.params(backend)} for v in vs],
        "nominal_sim": to_dict(SimConfig()), "nominal_fixture": to_dict(FixtureConfig()),
    }, out / "variants.json")
    write_json({
        "argv": sys.argv, "seed": seed, "backend": backend, "g_model": g_model, "workers": workers,
        "environment": environment_info(),
        "controller_configs": {c: to_dict(getattr(build_controller(c, backend, g_model), "cfg", None))
                               for c in controllers},
        "g_prior_cfg": to_dict(build_controller("adaptive_learned", backend, g_model).prior_cfg),
    }, out / "config.json")
    jobs = []
    for k in variants:
        for suite, cond, n in cells:
            for ctrl in controllers:
                for a in range(0, n, chunk):
                    jobs.append((k, seed, backend, suite, cond, ctrl, tuple(range(a, min(n, a + chunk))), g_model))
    total = sum(len(j[6]) for j in jobs)
    print(f"{backend}: {len(variants)} variants x {len(cells)} cells x {len(controllers)} controllers = "
          f"{total} trials on {workers} workers -> {out}", flush=True)
    t0 = time.time()
    results: list[tuple[dict, list]] = []
    if workers <= 1:
        _init_worker(backend)
        for j in jobs:
            results += run_job(*j)
    else:
        with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker, initargs=(backend,)) as pool:
            futs = [pool.submit(run_job, *j) for j in jobs]
            for n, f in enumerate(as_completed(futs), 1):
                results += f.result()
                if n % 20 == 0 or n == len(futs):
                    done = sum(1 for _ in results)
                    el = time.time() - t0
                    print(f"  {done}/{total} trials, {el:.0f} s, eta {el * (total - done) / max(done, 1):.0f} s",
                          flush=True)
    vorder = {k: i for i, k in enumerate(variants)}
    corder = {c[1]: i for i, c in enumerate(cells)}
    korder = {c: i for i, c in enumerate(controllers)}
    results.sort(key=lambda x: (vorder[x[0]["variant"]], corder[x[0]["condition"]], korder[x[0]["controller"]],
                                x[0]["trial_index"]))
    rows = [r for r, _ in results]
    write_csv(rows, out / "trials.csv")
    write_csv(summary_rows(rows), out / "summary.csv")
    with gzip.open(out / "events.json.gz", "wt") as fh:
        json.dump({f"{r['variant']}|{r['condition']}|{r['controller']}|{r['trial_index']}": ev for r, ev in results},
                  fh)
    wall = time.time() - t0
    write_json({"wall_time_s": wall, "trials": total, "workers": workers}, out / "run_time.json")
    print(f"wrote {out / 'trials.csv'} ({total} trials, {wall:.0f} s)")
    return rows


# --------------------------------------------------------------------------- summaries
def _b(x) -> bool:
    return x is True or x == "True"


def escaped(r: dict) -> bool:
    """is_escape on a row: failed, no protective stop, not declared failed."""
    d = r["declared_success"]
    declared = None if d in (None, "", "None") else _b(d)
    return (not _b(r["success"])) and (not _b(r["protective_stop"])) and declared is not False


def summary_rows(rows: list[dict]) -> list[dict]:
    g: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        g[(int(r["variant"]), r["suite"], r["condition"], r["controller"])].append(r)
    out = []
    for (k, suite, cond, ctrl), rs in g.items():
        out.append({"variant": k, "suite": suite, "condition": cond, "controller": ctrl, "n": len(rs),
                    "successes": sum(_b(r["success"]) for r in rs), "escapes": sum(escaped(r) for r in rs),
                    "protective_stops": sum(_b(r["protective_stop"]) for r in rs),
                    "gt_seated": sum(_b(r["gt_seated"]) for r in rs)})
    return out


def compare_rows(ours: list[dict], theirs: list[dict], ignore=("wall_time_s",)) -> list[str]:
    """Differences between variant-0 rows and experiments.robustness rows, field by field as text
    (both as read from trials.csv), on the robustness columns; [] when identical."""
    key = lambda r: (r["condition"], r["controller"], str(r["trial_index"]))  # noqa: E731
    a, b = {key(r): r for r in ours if str(r.get("variant", "0")) == "0"}, {key(r): r for r in theirs}
    diffs = [f"trial sets differ: {len(a)} vs {len(b)} rows"] if set(a) != set(b) else []
    for k in sorted(set(a) & set(b)):
        for f, x in b[k].items():
            if f in ignore:
                continue
            if f not in a[k] or str(a[k][f]) != str(x):
                diffs.append(f"{k} {f}: {a[k].get(f)!r} vs {x!r}")
    return diffs


def equivalence_report(ours: Path, theirs: list[Path]) -> str:
    import csv

    def read(p: Path) -> list[dict]:
        with open(p / "trials.csv") as fh:
            return list(csv.DictReader(fh))

    a = read(ours)
    b = [r for p in theirs for r in read(p)]
    diffs = compare_rows(a, b)
    fields = len(b[0]) - 1 if b else 0
    head = (f"{ours} variant 0 against {', '.join(map(str, theirs))}: {len(b)} robustness rows, "
            f"{fields} fields each compared as text (wall_time_s excluded)")
    return head + ("\nidentical\n" if not diffs else f"\n{len(diffs)} differences:\n" + "\n".join(diffs[:50]) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--backend", choices=["gantry", "arm"], default="gantry")
    ap.add_argument("--cells", default="", help="suite:condition:trials,... (names from experiments.robustness --list)")
    ap.add_argument("--controllers", default="adaptive,spiral_rcc,spiral_pull,spiral_rcc_pull,spiral_rcc_verify,"
                                             "adaptive_learned")
    ap.add_argument("--variants", type=int, default=12, help="randomized variants; variant 0 (nominal) is added")
    ap.add_argument("--only-variants", default="", help="comma-separated variant ids to run instead (e.g. 0)")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--g-model", choices=["pinned", "lookup"], default="pinned")
    ap.add_argument("--name", default="")
    ap.add_argument("--analyse", type=Path, default=None, metavar="DIR",
                    help="print the pre-registered tables for this result folder (gantry/ and arm/ inside)")
    ap.add_argument("--equivalence", nargs="+", type=Path, default=None, metavar="DIR",
                    help="OURS ROBUSTNESS_DIR...: compare variant-0 rows with experiments.robustness rows")
    args = ap.parse_args()
    if args.equivalence is not None:
        print(equivalence_report(args.equivalence[0], args.equivalence[1:]), end="")
        return
    if args.analyse is not None:
        from experiments.sim_randomization_v02f_tables import main as tables

        tables([args.analyse])
        return
    if args.seed is None or not args.name or not args.cells:
        raise SystemExit("--seed, --name and --cells are required")
    variants = [int(x) for x in args.only_variants.split(",")] if args.only_variants else \
        list(range(args.variants + 1))
    run(args.backend, parse_cells(args.cells), [c for c in args.controllers.split(",") if c], variants, args.seed,
        args.workers, REPO_ROOT / "results" / args.name, args.g_model)


if __name__ == "__main__":
    main()
