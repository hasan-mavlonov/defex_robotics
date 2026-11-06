"""v0.2f: wall time of one control tick on the rig-PC side (development measurement on a laptop).

    python -m experiments.v02f_tick_timing --backend gantry --seeds 2026,2027 --suites standard,latching \
        --trials 2 --replays 3 --out results/v0.2f_realtime/timing/run1_gantry

What is timed, per 500 Hz control tick, single process, inside the normal trial loop
(InsertionTask.run, unchanged):

* ``est``: StateEstimator.update (payload compensation, tare, F/T filter, frames),
* ``ctrl``: controller.step (the FSM with its localizer, learned prior, diagnosis and VERIFY code),
* ``motion``: CartesianMotionGenerator.update (bounded-velocity setpoint).

Not timed: MuJoCo physics, the backend's IK (the UR controller does it behind servoL; the
gantry's is closed form), the simulator's synthetic sensor noise, and the I/O a rig adds
(F/T UDP read, servoL send). ``cpu`` is the thread CPU time of est + ctrl + motion: wall minus
cpu is time the process was not running (preemption by other load).

``replay``: after each trial the observation stream the controller saw is fed again to fresh
controllers ``--replays`` times without physics; the per-tick minimum is the intrinsic cost
with scheduling noise mostly removed. The first replay must reproduce every command exactly
(checked; a mismatch aborts).

Inclusive sub-timers (seconds spent inside, per tick) are kept for the localizer updates,
probe selection, the learned prior, the contact diagnosis and VERIFY helpers. Python GC
collections during a tick are flagged. Uptime load averages are recorded per trial.

Outputs in ``--out``: summary.csv (per controller and FSM state), subtimers.csv, worst_ticks.json,
config.json; raw per-tick arrays go to ``--raw`` (an .npz path outside git) when given.
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import os
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

DEV_SEEDS = (2026, 2027)
CONTROLLERS = "adaptive,adaptive_learned,spiral_rcc_verify,spiral_rcc,spiral_rcc_pull"
BUDGET_S = 0.002

_pc = time.perf_counter
_tt = time.thread_time

STATE = {"pending_est": 0.0, "pending_cpu0": None, "sub": defaultdict(float), "in_step": 0, "gc_t0": None,
         "gc_s": 0.0, "gc_n": 0, "ticks": None, "obs": None, "cmds": None}


def _gc_cb(phase, info):
    if phase == "start":
        STATE["gc_t0"] = _pc()
    elif STATE["gc_t0"] is not None:
        STATE["gc_s"] += _pc() - STATE["gc_t0"]
        STATE["gc_n"] += 1
        STATE["gc_t0"] = None


def _sub(name, fn):
    def wrapped(*a, **k):
        t0 = _pc()
        try:
            return fn(*a, **k)
        finally:
            if STATE["in_step"]:
                STATE["sub"][name] += _pc() - t0
    wrapped.__wrapped__ = fn
    return wrapped


def install_wrappers() -> list[str]:
    from defex.control.adaptive_fsm import AdaptiveInsertionController
    from defex.control.adaptive_learned import AdaptiveLearnedController
    from defex.control.motion import CartesianMotionGenerator
    from defex.perception.state_estimator import StateEstimator
    from defex.recovery.contact_likelihood import ContactLikelihood
    from defex.recovery.failure_detector import ContactDiagnoser
    from defex.recovery.learned_prior import ContactPrior
    from defex.recovery.search_policy import HoleLocalizer
    from defex.recovery.yaw_localizer import YawHoleLocalizer

    names = []
    for cls, meths in (
        (HoleLocalizer, ("update_blocked", "update_entered", "best_probe", "update_gaussian", "update_log_term",
                         "entry_probability_at")),
        (YawHoleLocalizer, ("update_blocked", "update_entered", "best_probe")),
        (ContactPrior, ("localizer_term",)),
        (ContactLikelihood, ("localizer_log_term", "mixture_mean_mm")),
        (ContactDiagnoser, ("diagnose",)),
        (AdaptiveInsertionController, ("_diagnose", "_plan_correction", "_click_in_trace", "_tilt_verdict",
                                       "_begin_verify", "_begin_latch_verify", "_record_contact")),
        (AdaptiveLearnedController, ("_contact_prior_update",)),
    ):
        for m in meths:
            if m in cls.__dict__:
                setattr(cls, m, _sub(f"{cls.__name__}.{m}", cls.__dict__[m]))
                names.append(f"{cls.__name__}.{m}")

    est_update = StateEstimator.update

    def timed_est(self, readings, setpoint):
        STATE["pending_cpu0"] = _tt()
        t0 = _pc()
        obs = est_update(self, readings, setpoint)
        STATE["pending_est"] = _pc() - t0
        return obs

    StateEstimator.update = timed_est

    mot_update = CartesianMotionGenerator.update

    def timed_motion(self, cmd):
        t0 = _pc()
        pose = mot_update(self, cmd)
        dt = _pc() - t0
        ticks = STATE["ticks"]
        if ticks is not None and ticks and ticks[-1]["motion"] is None:
            ticks[-1]["motion"] = dt
            ticks[-1]["cpu"] = _tt() - ticks[-1]["cpu"]
        return pose

    CartesianMotionGenerator.update = timed_motion
    return names


def instrument_controller(ctrl) -> None:
    step = ctrl.step
    reset = ctrl.reset

    def timed_reset(ctx):
        t0 = _pc()
        reset(ctx)
        STATE["reset_s"] = _pc() - t0
        STATE["ctx"] = ctx

    def timed_step(obs):
        before = ctrl.state
        STATE["sub"] = defaultdict(float)
        gc_s0, gc_n0 = STATE["gc_s"], STATE["gc_n"]
        STATE["in_step"] = 1
        t0 = _pc()
        cmd = step(obs)
        dt = _pc() - t0
        STATE["in_step"] = 0
        STATE["ticks"].append({"state": before, "after": ctrl.state, "est": STATE["pending_est"], "ctrl": dt,
                               "motion": None, "cpu": STATE["pending_cpu0"], "t": obs.t,
                               "gc": STATE["gc_n"] - gc_n0, "gc_s": STATE["gc_s"] - gc_s0,
                               "sub": dict(STATE["sub"]) if STATE["sub"] else None})
        STATE["obs"].append(obs)
        STATE["cmds"].append(np.concatenate([cmd.target.p, cmd.target.R.ravel(),
                                             [cmd.max_linear_speed, cmd.max_angular_speed]]))
        return cmd

    ctrl.step = timed_step
    ctrl.reset = timed_reset


def replay(name: str, ctx, obs_seq, cmds, repeats: int) -> np.ndarray:
    """Per-tick minimum controller.step wall time over ``repeats`` replays of the recorded observations."""
    from defex.control.registry import make_controller

    best = np.full(len(obs_seq), np.inf)
    for r in range(repeats):
        c = make_controller(name)
        c.reset(ctx)
        for k, obs in enumerate(obs_seq):
            t0 = _pc()
            cmd = c.step(obs)
            dt = _pc() - t0
            if dt < best[k]:
                best[k] = dt
            if r == 0:
                got = np.concatenate([cmd.target.p, cmd.target.R.ravel(), [cmd.max_linear_speed, cmd.max_angular_speed]])
                if not np.array_equal(got, cmds[k]):
                    raise RuntimeError(f"replay of {name} differs at tick {k}: the controller is not a function of obs")
    return best


def write_summary(arr: dict, backend: str, controllers: list[str], out: Path) -> None:
    """summary.csv per controller and FSM state. best = min(in-loop controller.step, its replays): the
    intrinsic cost; nogc = ticks without a Python GC collection."""
    arr = dict(arr)
    arr["best"] = np.fmin(arr["ctrl"], arr["replay"])
    nogc = arr["gc"] == 0
    summary = []
    for name in controllers:
        m = arr["controller"] == name
        states = ["ALL"] + sorted(set(arr["state"][m]))
        for st in states:
            sel = m if st == "ALL" else m & (arr["state"] == st)
            row = {"backend": backend, "controller": name, "state": st, "ticks": int(sel.sum())}
            for col in ("total", "ctrl", "est", "motion", "cpu", "replay", "best"):
                x = arr[col][sel]
                x = x[np.isfinite(x)]
                for q, lab in ((50, "p50"), (99, "p99"), (99.9, "p999")):
                    row[f"{col}_{lab}_us"] = round(pct(x, q) * 1e6, 1)
                row[f"{col}_max_us"] = round(float(x.max()) * 1e6, 1) if x.size else float("nan")
            for thr in (0.0005, 0.001, BUDGET_S):
                row[f"total_over_{thr * 1e3:g}ms"] = int((arr["total"][sel] > thr).sum())
                rp = arr["replay"][sel]
                row[f"replay_over_{thr * 1e3:g}ms"] = int((rp[np.isfinite(rp)] > thr).sum())
            row["ticks_with_gc"] = int((arr["gc"][sel] > 0).sum())
            row["total_over_2ms_with_gc"] = int(((arr["total"] > BUDGET_S) & ~nogc)[sel].sum())
            row["cpu_over_2ms"] = int((arr["cpu"][sel] > BUDGET_S).sum())
            row["cpu_over_2ms_with_gc"] = int(((arr["cpu"] > BUDGET_S) & ~nogc)[sel].sum())
            for col in ("total", "cpu", "best"):
                x = arr[col][sel & nogc]
                x = x[np.isfinite(x)]
                row[f"{col}_nogc_max_us"] = round(float(x.max()) * 1e6, 1) if x.size else float("nan")
            for thr in (0.0005, 0.001, BUDGET_S):
                row[f"best_over_{thr * 1e3:g}ms"] = int((arr["best"][sel] > thr).sum())
            summary.append(row)
    with (out / "summary.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)


def pct(x: np.ndarray, q: float) -> float:
    return float(np.percentile(x, q)) if x.size else float("nan")


LABEL = {"adaptive": "C", "adaptive_learned": "G", "spiral_rcc_verify": "J", "spiral_rcc": "F", "spiral_rcc_pull": "I"}


def tables(root: Path) -> None:
    out = ["# v0.2f tick timing tables", "",
           "Development measurement on an Apple M5 laptop (4 performance + 6 efficiency cores) shared with other "
           f"jobs; not the rig PC. Made by `python -m experiments.v02f_tick_timing --tables {root}`. Times in "
           "microseconds per 500 Hz tick (budget 2000 us). total = StateEstimator.update + controller.step + "
           "CartesianMotionGenerator.update, wall clock, in the trial loop. replay = per-tick minimum of "
           "controller.step over 3 replays of the recorded observations (intrinsic cost, scheduling noise mostly "
           "removed). best = min(in-loop controller.step, its replays). cpu = thread CPU time of the same work as total. "
           "nogc = ticks without a Python GC collection.", ""]
    for run in sorted(p for p in root.iterdir() if (p / "summary.csv").exists()):
        cfg = json.loads((run / "config.json").read_text())
        with (run / "summary.csv").open() as fh:
            rows = list(csv.DictReader(fh))
        tag = "loaded" if cfg["loaded"] else "not loaded"
        out += [f"## {run.name} ({tag})", "",
                f"{cfg['trials']} trials, {cfg['ticks']} ticks, commit {cfg['environment']['git_commit'][:7]}, "
                f"1-min load average per trial: min {cfg['load1_min']:.1f}, mean {cfg['load1_mean']:.1f}, "
                f"max {cfg['load1_max']:.1f}. Controller reset (before the cycle, outside the loop), ms p50/max: "
                + ", ".join(f"{LABEL.get(k, k)} {v['p50']:.2f}/{v['max']:.2f}" for k, v in cfg["controller_reset_ms"].items())
                + ".", "",
                "| ctrl | state | ticks | total p50 | p99 | p99.9 | max | total > 2 ms (with GC) | cpu p99.9 | "
                "cpu max nogc | cpu > 2 ms (with GC) | best p50 | p99 | p99.9 | max | best > 0.5 ms | > 1 ms | > 2 ms | "
                "ticks with GC |",
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            out.append(f"| {LABEL.get(r['controller'], r['controller'])} | {r['state']} | {r['ticks']} | "
                       f"{r['total_p50_us']} | {r['total_p99_us']} | {r['total_p999_us']} | {r['total_max_us']} | "
                       f"{r['total_over_2ms']} ({r['total_over_2ms_with_gc']}) | {r['cpu_p999_us']} | "
                       f"{r['cpu_nogc_max_us']} | {r['cpu_over_2ms']} ({r['cpu_over_2ms_with_gc']}) | "
                       f"{r['best_p50_us']} | {r['best_p99_us']} | {r['best_p999_us']} | {r['best_max_us']} | "
                       f"{r['best_over_0.5ms']} | {r['best_over_1ms']} | {r['best_over_2ms']} | {r['ticks_with_gc']} |")
        worst = json.loads((run / "worst_ticks.json").read_text())
        worst.sort(key=lambda w: -min(w["ctrl_ms"], w["replay_min_ctrl_ms"] or np.inf))
        out += ["", "Slowest ticks by best controller.step time (intrinsic cost):", "",
                "| ctrl | condition | seed | trial | t s | state -> after | best ms | in-loop total ms | cpu ms | "
                "GC | largest sub-timers ms |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for w in worst[:15]:
            subs = sorted(w["sub_ms"].items(), key=lambda kv: -kv[1])[:3]
            out.append(f"| {LABEL.get(w['controller'], w['controller'])} | {w['condition']} | {w['seed']} | "
                       f"{w['trial_index']} | {w['t']} | {w['state']} -> {w['after']} | "
                       f"{min(w['ctrl_ms'], w['replay_min_ctrl_ms'] or np.inf):.3f} | {w['total_ms']:.3f} | {w['cpu_ms']:.3f} | "
                       f"{w['gc_collections']} | " + "; ".join(f"{k.split('.')[-1]} {v:.3f}" for k, v in subs) + " |")
        with (run / "subtimers.csv").open() as fh:
            subs = list(csv.DictReader(fh))
        out += ["", "Sub-timers (inclusive, in-loop wall time, per tick that called them):", "",
                "| ctrl | function | ticks | p50 us | p99 us | max us |", "|---|---|---|---|---|---|"]
        for r in subs:
            out.append(f"| {LABEL.get(r['controller'], r['controller'])} | {r['function']} | {r['ticks']} | "
                       f"{r['p50_us']} | {r['p99_us']} | {r['max_us']} |")
        out.append("")
    (root / "TABLES.md").write_text("\n".join(out) + "\n")
    print(f"wrote {root / 'TABLES.md'}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--backend", choices=["gantry", "arm"])
    ap.add_argument("--seeds", default="2026,2027")
    ap.add_argument("--suites", default="standard,latching")
    ap.add_argument("--trials", type=int, default=2)
    ap.add_argument("--controllers", default=CONTROLLERS)
    ap.add_argument("--conditions", default="", help="restrict to these condition names")
    ap.add_argument("--replays", type=int, default=3)
    ap.add_argument("--out")
    ap.add_argument("--tables", default="", help="write TABLES.md from every run folder under this folder")
    ap.add_argument("--raw", default="", help="optional .npz for the per-tick arrays (keep out of git)")
    ap.add_argument("--from-raw", default="", help="rewrite --out/summary.csv from this --raw file and exit")
    args = ap.parse_args()
    if args.tables:
        tables(Path(args.tables))
        return
    if not (args.backend and args.out):
        raise SystemExit("--backend and --out are required for a run")
    if args.from_raw:
        raw = dict(np.load(args.from_raw))
        write_summary(raw, args.backend, [c for c in args.controllers.split(",") if c], Path(args.out))
        return
    seeds = [int(s) for s in args.seeds.split(",")]
    if any(s not in DEV_SEEDS for s in seeds):
        raise SystemExit("development seeds 2026 and 2027 only")
    os.environ["DEFEX_BACKEND"] = args.backend
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    sub_names = install_wrappers()
    gc.callbacks.append(_gc_cb)

    from defex.control.registry import make_controller
    from defex.tasks.conditions import latch_spread_conditions, latching_conditions, standard_conditions
    from defex.tasks.insertion import InsertionTask
    from defex.tasks.scenarios import sample_scenario
    from experiments.runner import environment_info, make_backend, nominal_socket_pose

    suites = {"standard": standard_conditions, "latching": latching_conditions, "latch_spread": latch_spread_conditions}
    conds = [c for s in args.suites.split(",") for c in suites[s]()]
    if args.conditions:
        want = set(args.conditions.split(","))
        conds = [c for c in conds if c.name in want]
    controllers = [c for c in args.controllers.split(",") if c]
    task = InsertionTask(backend=make_backend())
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    rows: dict[str, list] = defaultdict(list)  # per-tick arrays (all controllers)
    subs: dict[tuple[str, str], list[float]] = defaultdict(list)
    worst: list[dict] = []
    resets: dict[str, list[float]] = defaultdict(list)
    loads = []
    t_start = time.time()
    n_trials = 0
    for name in controllers:
        for seed in seeds:
            for cond in conds:
                nominal = nominal_socket_pose(cond, task.fixture)
                for i in range(args.trials):
                    scenario = sample_scenario(cond, i, seed, nominal)
                    ctrl = make_controller(name)
                    instrument_controller(ctrl)
                    STATE["ticks"], STATE["obs"], STATE["cmds"] = [], [], []
                    la = os.getloadavg()
                    res = task.run(ctrl, scenario)
                    ticks = STATE["ticks"]
                    STATE["ticks"] = None
                    rep = replay(name, STATE["ctx"], STATE["obs"], STATE["cmds"], args.replays) if args.replays else None
                    STATE["obs"] = STATE["cmds"] = None
                    resets[name].append(STATE["reset_s"])
                    loads.append(la[0])
                    n_trials += 1
                    trial_rows: dict[str, list] = defaultdict(list)
                    for k, tk in enumerate(ticks):
                        if tk["motion"] is None:  # the last tick of a trial that ended in this step
                            tk["motion"], tk["cpu"] = 0.0, float("nan")
                        total = tk["est"] + tk["ctrl"] + tk["motion"]
                        trial_rows["state"].append(tk["state"])
                        trial_rows["est"].append(tk["est"])
                        trial_rows["ctrl"].append(tk["ctrl"])
                        trial_rows["motion"].append(tk["motion"])
                        trial_rows["total"].append(total)
                        trial_rows["cpu"].append(tk["cpu"])
                        trial_rows["replay"].append(rep[k] if rep is not None else np.nan)
                        trial_rows["gc"].append(tk["gc"])
                        if tk["sub"]:
                            for s, v in tk["sub"].items():
                                subs[(name, s)].append(v)
                        if total > 0.0005 or (rep is not None and rep[k] > 0.0003):
                            worst.append({"controller": name, "seed": seed, "condition": cond.name, "trial_index": i,
                                          "tick": k, "t": round(tk["t"], 4), "state": tk["state"], "after": tk["after"],
                                          "total_ms": total * 1e3, "est_ms": tk["est"] * 1e3, "ctrl_ms": tk["ctrl"] * 1e3,
                                          "motion_ms": tk["motion"] * 1e3, "cpu_ms": tk["cpu"] * 1e3,
                                          "replay_min_ctrl_ms": None if rep is None else rep[k] * 1e3,
                                          "best_ctrl_ms": min(tk["ctrl"], rep[k] if rep is not None else np.inf) * 1e3,
                                          "gc_collections": tk["gc"], "gc_ms": tk["gc_s"] * 1e3, "load1": la[0],
                                          "sub_ms": {s: v * 1e3 for s, v in (tk["sub"] or {}).items()}})
                    # Per-trial numpy chunks: millions of floats in Python lists made the collector's full
                    # passes (and so the GC-flagged ticks) far slower than the controller's own heap would.
                    n = len(ticks)
                    for key, v in trial_rows.items():
                        rows[key].append(np.asarray(v))
                    rows["controller"].append(np.full(n, name))
                    rows["load1"].append(np.full(n, la[0]))
                    del trial_rows, ticks
                    worst.sort(key=lambda w: -w.get("best_ctrl_ms", w["replay_min_ctrl_ms"] or w["total_ms"]))
                    del worst[300:]
            print(f"{name} seed {seed}: {n_trials} trials, {time.time() - t_start:.0f} s, load {os.getloadavg()}",
                  flush=True)

    arr = {k: np.concatenate(v) for k, v in rows.items()}
    if args.raw:
        Path(args.raw).parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(args.raw, **arr)
    write_summary(arr, args.backend, controllers, out)
    with (out / "subtimers.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["backend", "controller", "function", "ticks", "p50_us", "p99_us", "max_us"])
        for (name, s), v in sorted(subs.items()):
            x = np.asarray(v)
            w.writerow([args.backend, name, s, x.size, round(pct(x, 50) * 1e6, 1), round(pct(x, 99) * 1e6, 1),
                        round(float(x.max()) * 1e6, 1)])
    (out / "worst_ticks.json").write_text(json.dumps(worst[:100], indent=1))
    cfg = {"script": "experiments/v02f_tick_timing.py", "args": vars(args), "environment": environment_info(),
           "trials": n_trials, "ticks": int(arr["total"].size), "wall_s": time.time() - t_start,
           "load1_min": min(loads), "load1_max": max(loads), "load1_mean": float(np.mean(loads)),
           "loaded": bool(np.mean(loads) > 8.0),
           "controller_reset_ms": {k: {"p50": pct(np.asarray(v), 50) * 1e3, "max": max(v) * 1e3}
                                   for k, v in resets.items()},
           "subtimers_installed": sub_names, "budget_s": BUDGET_S,
           "label": "development measurement, Apple M5 laptop shared with other jobs, not the rig PC"}
    (out / "config.json").write_text(json.dumps(cfg, indent=1))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
