"""v0.2f friction diagnosis (POST HOC): why C loses arm friction_1 under MuJoCo's pyramidal friction cone.

Diagnosis only. Nothing here changes a controller; every controller runs as registered.

    # replay and trace one named failure of the randomized arm run (seed 20261205, variant k)
    python -m experiments.friction_diagnosis_v02f trace --source simrand --variant 4 --index 0 --controller adaptive
    # one named benchmark_v0.2e arm friction_1 failure (seed 20261130, nominal simulator)
    python -m experiments.friction_diagnosis_v02f trace --source nominal --seed 20261130 --index 8
    # development counts: nominal against a cone-only variant (pyramidal, every other parameter nominal)
    python -m experiments.friction_diagnosis_v02f counts --seeds 2026,2027 --trials 20 --workers 2 \\
        --name v0.2f_friction_diagnosis/dev_counts

Sources: ``simrand`` rebuilds variant k of experiments/sim_randomization_v02f.py exactly as that run did
(draw_variant, make_task); ``nominal`` is the nominal arm (variant 0, what experiments.runner builds);
``cone`` is the nominal arm with only ``SimConfig.cone`` replaced (``--cone``); servo stiffness,
latency and every other contact parameter stay nominal.

Seeds: development seeds 2026 and 2027 for anything; 20261205 (randomized run) and 20261130
(benchmark_v0.2e) only to replay friction_1 trials those reports already name as failures.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

DEV_SEEDS = (2026, 2027)
REPLAY_SEEDS = {20261205: "simrand", 20261130: "nominal"}  # named-failure replays only
SIMRAND_SEED = 20261205


# --------------------------------------------------------------------------- building the workcell
def build_variant(source: str, variant: int = 0, cone: str = "pyramidal", impratio: float | None = None,
                  friction_timeconst_s: float | None = None):
    """The Variant (experiments.sim_randomization_v02f) for a source."""
    from defex.config import FixtureConfig, SimConfig
    from defex.sim.arm_backend import ArmConfig
    from experiments.sim_randomization_v02f import Variant, draw_variant

    if source == "simrand":
        return draw_variant(variant, SIMRAND_SEED, "arm")
    if source == "nominal":
        return draw_variant(0, SIMRAND_SEED, "arm")  # variant 0 is the nominal arm whatever the seed
    if source == "cone":
        # k = 1000 so make_task takes the non-nominal path; servo factors 1.0 leave Menagerie's servos as built.
        sim = replace(SimConfig(), cone=cone)
        if impratio is not None:
            sim = replace(sim, impratio=impratio)
        if friction_timeconst_s is not None:
            sim = replace(sim, contact_friction_timeconst_s=friction_timeconst_s)
        return Variant(1000, sim, FixtureConfig(), ArmConfig().latency_s, 1.0, 1.0)
    raise ValueError(source)


def build_task(source: str, variant: int = 0, cone: str = "pyramidal", impratio: float | None = None,
               friction_timeconst_s: float | None = None):
    os.environ["DEFEX_BACKEND"] = "arm"
    from experiments.sim_randomization_v02f import make_task

    return make_task(build_variant(source, variant, cone, impratio, friction_timeconst_s), "arm")


def scenario_for(task, condition: str, index: int, seed: int):
    from defex.tasks.scenarios import sample_scenario
    from experiments.runner import nominal_socket_pose
    from experiments.sim_randomization_v02f import all_conditions

    cond = all_conditions()[("standard", condition)]
    return sample_scenario(cond, index, seed, nominal_socket_pose(cond, task.fixture))


# --------------------------------------------------------------------------- per-tick trace
CLASSES = ("floor", "wall_x", "wall_y", "lead_in", "other")


def _contact_breakdown(backend, R_socket: np.ndarray) -> dict[str, np.ndarray]:
    """Force on the held parts per socket feature, socket frame, split into normal and friction parts.

    Returns {class: [Fn_x, Fn_y, Fn_z, Ft_x, Ft_y, Ft_z, normal magnitude, friction magnitude, count]}.
    """
    import mujoco

    m, d = backend.model, backend.data
    out = {k: np.zeros(9) for k in CLASSES}
    buf = np.zeros(6)
    held, sock = backend._held_mask, backend._socket_mask
    for i in range(d.ncon):
        con = d.contact[i]
        g1, g2 = con.geom1, con.geom2
        if not ((held[g1] and sock[g2]) or (held[g2] and sock[g1])):
            continue
        mujoco.mj_contactForce(m, d, i, buf)
        frame = con.frame.reshape(3, 3)  # rows: normal, tangent 1, tangent 2 (world)
        sign = 1.0 if held[g2] else -1.0  # buf is the force on geom2
        fn = sign * buf[0] * frame[0]
        ft = sign * (buf[1] * frame[1] + buf[2] * frame[2])
        fn_s, ft_s = R_socket.T @ fn, R_socket.T @ ft
        sg = m.geom(int(g2 if sock[g2] else g1)).name
        n_s = np.abs(R_socket.T @ frame[0])
        if "floor" in sg or "pcb" in sg:
            cls = "floor"
        elif "wall" in sg:
            pos_s = R_socket.T @ (con.pos - backend._socket_pose_true.p)
            if pos_s[2] > -0.0009 and n_s[2] > 0.3:  # on the chamfer near the mouth
                cls = "lead_in"
            else:
                cls = "wall_x" if n_s[0] >= n_s[1] else "wall_y"
        else:
            cls = "other"
        o = out[cls]
        o[0:3] += fn_s
        o[3:6] += ft_s
        o[6] += abs(buf[0])
        o[7] += float(np.hypot(buf[1], buf[2]))
        o[8] += 1
    return out


def run_trace(task, scenario, controller: str):
    from defex.config import MM
    from defex.utils.transforms import matrix_to_rotvec, twist_about_axis
    from experiments.sim_randomization_v02f import build_controller

    ctrl = build_controller(controller, "arm", "pinned")
    rows: dict[str, list] = defaultdict(list)

    def on_step(info) -> None:
        c, o, gt = info.controller, info.obs, info.gt
        bf = getattr(c, "bias_f", np.zeros(3))
        bt = getattr(c, "bias_t", np.zeros(3))
        # J runs C's VERIFY inside its verifier: read the verifier's phase while it verifies.
        inner = getattr(c, "verifier", None) if getattr(c, "_verifying", False) else None
        src = inner if inner is not None else c
        rows["t"].append(o.t)
        rows["state"].append(str(c.state))
        rows["phase"].append(str(getattr(src, "phase", "")))
        Rs = gt.socket_pose.R
        rows["F"].append(o.force - bf)
        rows["T"].append(o.torque - bt)
        rows["lateral"].append(np.asarray(o.lateral, dtype=float).copy())
        rows["depth"].append(float(o.depth))
        rel = gt.socket_pose.inv() @ gt.connector_pose
        rows["true_p"].append(rel.p.copy())
        rows["true_yaw"].append(float(twist_about_axis(rel.R)))
        rows["true_rv"].append(matrix_to_rotvec(rel.R))
        rows["sp_rv"].append(matrix_to_rotvec(gt.socket_pose.R.T @ info.setpoint.R))
        rows["tcp_rv"].append(matrix_to_rotvec(gt.socket_pose.R.T @ o.fixture_tcp.R))
        rows["sp_p"].append((gt.socket_pose.inv() @ info.setpoint).p.copy())
        br = _contact_breakdown(info.backend, Rs)
        for k in CLASSES:
            rows["c_" + k].append(br[k])
        adm = getattr(src, "adm_conf", None)
        rows["adm_conf"].append(np.array(getattr(adm, "x", np.zeros(3)), dtype=float)[:3])
        rows["contact_norm"].append(gt.contact_force_norm)
        rows["t_norm"].append(float(o.torque_norm))
        rows["f_norm"].append(float(o.force_norm))

    result = task.run(ctrl, scenario, on_step=on_step)
    arrays = {k: np.asarray(v) for k, v in rows.items()}
    arrays["_mm"] = np.array(MM)
    return result, arrays


def probe_summary(a: dict) -> list[dict]:
    """One line per VERIFY wall probe (probe_out segment): where it stopped and what stopped it."""
    from defex.config import DEG, MM

    ph = a["phase"]
    out = []
    k = 0
    n = len(ph)
    while k < n:
        if ph[k] != "probe_out":
            k += 1
            continue
        s = k
        while k < n and ph[k] == "probe_out":
            k += 1
        e = k - 1
        Fy = float(a["F"][e][1])
        d = 1.0 if Fy < 0 else -1.0  # the probe direction is opposite the wall reaction
        row = {
            "t_start": round(float(a["t"][s]), 3), "t_end": round(float(a["t"][e]), 3),
            "dir": "+y" if d > 0 else "-y",
            "ft_reaction_n": round(-d * Fy, 2),
            "setpoint_travel_mm": round(d * float(a["sp_p"][e][1] - a["sp_p"][s][1]) / MM, 3),
            "true_travel_mm": round(d * float(a["true_p"][e][1] - a["true_p"][s][1]) / MM, 3),
            "true_y_end_mm": round(float(a["true_p"][e][1]) / MM, 3),
            "true_yaw_deg": round(float(a["true_yaw"][e]) / DEG, 2),
            "true_tilt_deg": [round(float(x) / DEG, 2) for x in a["true_rv"][e][:2]],
            "depth_mm": round(float(a["true_p"][e][2]) / MM * -1, 2),
        }
        fl = a["c_floor"][s:e + 1]
        row["floor_N_mean"] = round(float(fl[:, 6].mean()), 2)
        row["floor_N_max"] = round(float(fl[:, 6].max()), 2)
        row["floor_zero_ticks"] = round(float((fl[:, 6] < 1e-6).mean()), 2)  # fraction of ticks with no floor force
        row["floor_fric_over_N"] = round(float(fl[:, 7].sum() / max(fl[:, 6].sum(), 1e-9)), 2)
        for cls in CLASSES:
            c = a["c_" + cls][e]
            row[f"{cls}_N"] = round(float(c[6]), 2)
            row[f"{cls}_fric_N"] = round(float(c[7]), 2)
            row[f"{cls}_Fy_normal"] = round(float(-d * c[1]), 2)  # resisting the probe = positive
            row[f"{cls}_Fy_friction"] = round(float(-d * c[4]), 2)
        out.append(row)
    return out


def print_trace(result, a: dict, out: Path | None, label: str) -> None:
    from defex.config import DEG, MM

    print(f"== {label}: success={result.success} reason={result.failure_reason} depth={result.final_depth_mm:.2f} mm "
          f"retries={result.retries} cycle={result.cycle_time_s:.2f} s")
    for e in result.events:
        print(f"  {e[0]:7.3f} {e[1]:18s} {e[2]}")
    probes = probe_summary(a)
    print("  wall probes (resisting force along the probe, N: wall normal / friction, per feature):")
    for p in probes:
        parts = " ".join(f"{c}={p[f'{c}_Fy_normal']:+.2f}/{p[f'{c}_Fy_friction']:+.2f}(N {p[f'{c}_N']:.1f})"
                         for c in CLASSES if p[f"{c}_N"] > 0 or abs(p[f"{c}_Fy_friction"]) > 0)
        print(f"   t={p['t_start']:.3f}-{p['t_end']:.3f} {p['dir']} F/T {p['ft_reaction_n']:.2f} N, setpoint "
              f"{p['setpoint_travel_mm']:.3f} mm, plug {p['true_travel_mm']:.3f} mm (y {p['true_y_end_mm']:+.3f}), "
              f"yaw {p['true_yaw_deg']:+.2f} tilt {p['true_tilt_deg']} deg | floor N mean {p['floor_N_mean']:.2f} "
              f"max {p['floor_N_max']:.1f}, zero {p['floor_zero_ticks']:.0%} of ticks, friction/N {p['floor_fric_over_N']:.2f} "
              f"| at stop: {parts}")
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out.parent / (out.name + ".probes.csv"), "w", newline="") as fh:
            if probes:
                w = csv.DictWriter(fh, fieldnames=[k for k in probes[0] if k != "true_tilt_deg"] + ["tilt_x_deg", "tilt_y_deg"])
                w.writeheader()
                for p in probes:
                    q = {k: v for k, v in p.items() if k != "true_tilt_deg"}
                    q["tilt_x_deg"], q["tilt_y_deg"] = p["true_tilt_deg"]
                    w.writerow(q)
        with open(out.parent / (out.name + ".events.txt"), "w") as fh:
            fh.write(f"{label}: success={result.success} reason={result.failure_reason} "
                     f"depth={result.final_depth_mm:.2f} mm retries={result.retries}\n")
            for e in result.events:
                fh.write(f"  {e[0]:7.3f} {e[1]:18s} {e[2]}\n")


# --------------------------------------------------------------------------- development counts
_TASKS: dict = {}


SIMS = {
    "elliptic_nominal": ("variant 0: the nominal arm (cone elliptic, solreffriction 20 ms)", dict(source="nominal")),
    "pyramidal_cone_only": ("nominal arm with SimConfig.cone = pyramidal; every other parameter nominal",
                            dict(source="cone", cone="pyramidal")),
    "elliptic_fric_2ms": ("nominal arm (elliptic) with contact_friction_timeconst_s = 2 ms, the normal solref: "
                          "what a pyramidal cone does to solreffriction (MuJoCo ignores it there)",
                          dict(source="cone", cone="elliptic", friction_timeconst_s=0.002)),
}
_HALF = re.compile(r"half free travel (-?[0-9.]+) mm")


def _init_worker() -> None:
    os.environ["DEFEX_BACKEND"] = "arm"
    os.environ.setdefault("OMP_NUM_THREADS", "1")


def _count_job(sim: str, seed: int, condition: str, controller: str, indices: tuple[int, ...]) -> list[dict]:
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    from experiments.sim_randomization_v02f import build_controller

    if sim not in _TASKS:
        _TASKS[sim] = build_task(**SIMS[sim][1])
    task = _TASKS[sim]
    rows = []
    for i in indices:
        r = task.run(build_controller(controller, "arm", "pinned"), scenario_for(task, condition, i, seed))
        half = [float(m.group(1)) for e in r.events if e[1] == "wall_yaw" for m in [_HALF.search(e[2])] if m]
        rows.append({"sim": sim, "base_seed": seed, **r.to_row(),
                     "verify_failed_events": sum("verify_failed" in str(e[2]) for e in r.events if e[1] == "state"),
                     "wall_yaw_checks": len(half),
                     "wall_yaw_min_half_travel_mm": min(half) if half else "",
                     "events_tail": " | ".join(f"{e[1]}: {e[2]}" for e in r.events[-3:])})
    return rows


def counts(seeds: list[int], conditions: list[str], controllers: list[str], trials: int, workers: int,
           out: Path, sims: list[str]) -> None:
    from defex.logging.metrics import write_csv, write_json
    from experiments.runner import environment_info

    for s in seeds:
        if s not in DEV_SEEDS:
            raise SystemExit("counts: development seeds only (2026, 2027)")
    arms = tuple(sims)
    jobs = [(arm, s, c, k, tuple(range(a, min(trials, a + 5))))
            for arm in arms for s in seeds for c in conditions for k in controllers for a in range(0, trials, 5)]
    out.mkdir(parents=True, exist_ok=True)
    write_json({"argv": sys.argv, "seeds": seeds, "conditions": conditions, "controllers": controllers,
                "trials": trials, "sims": {k: SIMS[k][0] for k in sims},
                "environment": environment_info(), "post_hoc": True}, out / "config.json")
    t0 = time.time()
    rows: list[dict] = []
    with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker) as pool:
        futs = [pool.submit(_count_job, *j) for j in jobs]
        for n, f in enumerate(as_completed(futs), 1):
            rows += f.result()
            if n % 10 == 0 or n == len(futs):
                print(f"  {n}/{len(futs)} jobs, {time.time() - t0:.0f} s", flush=True)
    rows.sort(key=lambda r: (arms.index(r["sim"]), int(r["base_seed"]), conditions.index(r["condition"]),
                             controllers.index(r["controller"]), int(r["trial_index"])))
    write_csv(rows, out / "trials.csv")
    write_csv(summarise(rows), out / "summary.csv")
    write_json({"wall_time_s": time.time() - t0, "trials": len(rows)}, out / "run_time.json")
    print(format_summary(summarise(rows)))


def _b(x) -> bool:
    return x is True or x == "True"


def summarise(rows: list[dict]) -> list[dict]:
    g: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        g[(r["sim"], int(r["base_seed"]), r["condition"], r["controller"])].append(r)
    out = []
    for (sim, seed, cond, ctrl), rs in g.items():
        reasons: dict[str, int] = defaultdict(int)
        verify_fail_trials = sum(int(r["verify_failed_events"]) > 0 for r in rs)
        half = [float(r["wall_yaw_min_half_travel_mm"]) for r in rs if r["wall_yaw_min_half_travel_mm"] != ""]
        for r in rs:
            if not _b(r["success"]):
                reasons[r["failure_reason"]] += 1
        out.append({"sim": sim, "base_seed": seed, "condition": cond, "controller": ctrl, "n": len(rs),
                    "successes": sum(_b(r["success"]) for r in rs),
                    "failures": "; ".join(f"{k} {v}" for k, v in sorted(reasons.items())),
                    "verify_fail_trials": verify_fail_trials,
                    "trials_with_wall_yaw_check": len(half),
                    "median_min_half_travel_mm": round(float(np.median(half)), 3) if half else ""})
    return out


def format_summary(summary: list[dict]) -> str:
    lines = ["sim, seed, condition, controller: seated / n (failure reasons)"]
    for s in summary:
        lines.append(f"{s['sim']:20s} {s['base_seed']} {s['condition']:12s} {s['controller']:18s} "
                     f"{s['successes']:2d}/{s['n']}  verify failed in {s['verify_fail_trials']}, median min half travel "
                     f"{s['median_min_half_travel_mm']} mm ({s['failures']})")
    return "\n".join(lines)


# --------------------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("trace")
    t.add_argument("--source", choices=["simrand", "nominal", "cone"], default="simrand")
    t.add_argument("--variant", type=int, default=0)
    t.add_argument("--cone", choices=["elliptic", "pyramidal"], default="pyramidal")
    t.add_argument("--impratio", type=float, default=None, help="--source cone only: also replace impratio")
    t.add_argument("--friction-timeconst", type=float, default=None,
                   help="--source cone only: also replace SimConfig.contact_friction_timeconst_s (solreffriction)")
    t.add_argument("--seed", type=int, default=SIMRAND_SEED)
    t.add_argument("--condition", default="friction_1")
    t.add_argument("--index", type=int, required=True)
    t.add_argument("--controller", default="adaptive")
    t.add_argument("--out", type=Path, default=None, help="write <out>.probes.csv and <out>.events.txt")
    c = sub.add_parser("counts")
    c.add_argument("--seeds", default="2026,2027")
    c.add_argument("--conditions", default="friction_1,friction_0.6,nominal")
    c.add_argument("--controllers", default="adaptive,spiral_rcc,spiral_rcc_verify")
    c.add_argument("--trials", type=int, default=20)
    c.add_argument("--workers", type=int, default=2)
    c.add_argument("--sims", default=",".join(SIMS))
    c.add_argument("--name", required=True)
    args = ap.parse_args()
    from defex.config import REPO_ROOT

    if args.cmd == "trace":
        if args.seed not in DEV_SEEDS:
            if REPLAY_SEEDS.get(args.seed) is None or args.condition != "friction_1":
                raise SystemExit("trace: development seeds, or friction_1 replays of 20261205 / 20261130 only")
            if args.source == "simrand" and args.seed != SIMRAND_SEED:
                raise SystemExit("--source simrand replays seed 20261205")
        task = build_task(args.source, args.variant, args.cone, args.impratio, args.friction_timeconst)
        result, a = run_trace(task, scenario_for(task, args.condition, args.index, args.seed), args.controller)
        label = (f"{args.source} variant {args.variant if args.source == 'simrand' else '-'} cone "
                 f"{task.sim.cone} impratio {task.sim.impratio:g} solreffriction {task.sim.contact_friction_timeconst_s:g} s seed {args.seed} {args.condition} "
                 f"{args.controller} #{args.index}")
        out = REPO_ROOT / args.out if args.out is not None and not args.out.is_absolute() else args.out
        print_trace(result, a, out, label)
    else:
        counts([int(s) for s in args.seeds.split(",")], args.conditions.split(","), args.controllers.split(","),
               args.trials, args.workers, REPO_ROOT / "results" / args.name, args.sims.split(","))


if __name__ == "__main__":
    main()
