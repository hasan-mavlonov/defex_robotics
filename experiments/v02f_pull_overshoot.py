"""v0.2f: force overshoot in the latching pull test (development measurement, seeds 2026/2027 only).

    python -m experiments.v02f_pull_overshoot --backend gantry --suite latching --seed 2026 --trials 10 \
        --controllers adaptive,adaptive_learned,spiral_pull,spiral_rcc_pull,spiral_rcc_verify \
        --out results/v0.2f_realtime/pull/gantry_latching_s2026

Runs every trial single-process through the normal harness (InsertionTask.run) with a read-only
per-tick callback, and records for every guarded pull (C/G/J: VERIFY phase "pull"; H/I: VERIFY
_pull_phase "pull"):

* the commanded pull force (the controller's own _pull_target),
* the measured axial force the guard acts on (tared, filtered F/T, socket axis), at the trip tick
  and its most negative value from the pull start to ``--post-s`` after the trip,
* the true latch-hook force from the simulator's mating model, at physics rate (2 kHz), over the
  same window and over the whole trial, and whether and where the latch broke,
* the peak 10 ms housing contact force (the damage criterion) and the peak measured |F| (the
  protective-stop input) over the window.

``--hook-damping`` and ``--hook-stiffness`` change the simulator's latch hook in this process only
(counterfactual: is the overshoot the undamped hook?). Defaults leave the model unchanged; any
non-default value is written to config.json and the folder must not be quoted as the model.

Outputs in ``--out``: trials.csv, summary.json, summary.csv, events.json.gz (runner.write_outputs),
episodes.csv (one row per pull), config.json. The controllers are not changed.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
from pathlib import Path

import numpy as np

DEV_SEEDS = (2026, 2027)


def _install_hook_probe(damping: float, stiffness: float | None):
    """Wrap MatingForce.axial_force: record the hook force each physics step (optionally change the hook)."""
    import defex.sim.mating as mating

    probe = {"tick_max": 0.0, "trial_max": 0.0, "broke_t": None, "sub": []}
    orig = mating.MatingForce.axial_force
    k_hook = mating._LATCH_STIFFNESS if stiffness is None else stiffness
    k_saved = mating._LATCH_STIFFNESS
    if stiffness is not None:
        mating._LATCH_STIFFNESS = stiffness

    def axial_force(self, d, v_in, lateral):
        was_broken = self.state.broken
        was_latched = self.state.latched
        f = orig(self, d, v_in, lateral)
        st = self.state
        pull = self.snap - mating._LATCH_PLAY - d
        hold = 0.0
        if (st.latched or (st.broken and not was_broken)) and pull > 0.0 and (was_latched or st.latched):
            hold = k_hook * pull
            if damping > 0.0 and st.latched:
                # Counterfactual only: viscous term on the engaged hook (resists the plug's outward speed).
                extra = damping * max(-v_in, 0.0)
                f -= extra
                hold += extra
        probe["tick_max"] = max(probe["tick_max"], hold)
        probe["trial_max"] = max(probe["trial_max"], hold)
        if st.broken and not was_broken:
            probe["broke_t"] = True
        return f

    def restore():
        mating.MatingForce.axial_force = orig
        if stiffness is not None:
            mating._LATCH_STIFFNESS = k_saved

    mating.MatingForce.axial_force = axial_force
    probe["restore"] = restore
    return probe


def _pull_view(ctrl):
    """(in_pull, target, wrench owner, state label, phase) for C/G/J (C's VERIFY) and H/I (spiral pull)."""
    v = getattr(ctrl, "verifier", None)
    if v is not None:
        if not getattr(ctrl, "_verifying", False):
            return False, None, ctrl, ctrl.state, ""
        ctrl = v
    if hasattr(ctrl, "_pull_phase"):  # H, I (spiral_search VERIFY)
        phase = getattr(ctrl, "_pull_phase", "")
        on = ctrl.state == "VERIFY" and bool(getattr(ctrl.cfg, "retention_pull", False)) and phase == "pull"
        return on, getattr(ctrl, "_pull_target", None), ctrl, ctrl.state, phase
    phase = getattr(ctrl, "phase", "")
    on = ctrl.state == "VERIFY" and getattr(ctrl, "latching", False) and phase == "pull"
    return on, getattr(ctrl, "_pull_target", None), ctrl, ctrl.state, phase


class PullRecorder:
    def __init__(self, probe: dict, post_s: float) -> None:
        self.probe = probe
        self.post_s = post_s
        self.episodes: list[dict] = []
        self.cur: dict | None = None
        self.window: list[float] = []
        self.trace: list[tuple] = []

    def reset(self) -> None:
        self.episodes, self.cur, self.window, self.trace = [], None, [], []
        self.probe.update(tick_max=0.0, trial_max=0.0, broke_t=None)

    def __call__(self, info) -> None:
        hook = self.probe["tick_max"]
        self.probe["tick_max"] = 0.0
        broke_now = bool(self.probe["broke_t"])
        self.probe["broke_t"] = None
        on, target, owner, state, phase = _pull_view(info.controller)
        F = info.obs.force - getattr(owner, "bias_f", np.zeros(3))
        f_ax = float(F[2])
        self.window.append(info.gt.contact_force_norm)
        if len(self.window) > 5:
            self.window.pop(0)
        c10 = sum(self.window) / len(self.window)
        self.trace.append((info.t, state, phase, f_ax, hook))
        if len(self.trace) > 400:
            self.trace.pop(0)
        if broke_now:
            self.break_info = {"t": info.t, "state": state, "phase": phase, "in_pull_window": self.cur is not None}
        cur = self.cur
        if on and (cur is None or cur.get("trip_t") is not None):
            if cur is not None:
                self._close()
            cur = self.cur = {"t0": info.t, "target_n": float(target), "trip_t": None, "trip_f_ax": None,
                              "min_f_ax_pull": f_ax, "min_f_ax": f_ax, "hook_max_pull": hook, "hook_max": hook,
                              "contact10_max": c10, "fnorm_max": info.obs.force_norm, "broke": False,
                              "phase_after": "", "state_after": "", "trace": list(self.trace[-60:])}
            return
        if cur is None:
            return
        if broke_now:
            cur["broke"] = True
        cur["min_f_ax"] = min(cur["min_f_ax"], f_ax)
        cur["hook_max"] = max(cur["hook_max"], hook)
        cur["contact10_max"] = max(cur["contact10_max"], c10)
        cur["fnorm_max"] = max(cur["fnorm_max"], info.obs.force_norm)
        if cur["trip_t"] is None:
            # The tick on which the guard ends the pull: its obs is the one the guard judged.
            cur["min_f_ax_pull"] = min(cur["min_f_ax_pull"], f_ax)
            cur["hook_max_pull"] = max(cur["hook_max_pull"], hook)
            if len(cur["trace"]) < 3000:
                cur["trace"].append(self.trace[-1])
            if not on:
                cur["trip_t"], cur["trip_f_ax"] = info.t, f_ax
                cur["state_after"], cur["phase_after"] = state, phase
        else:
            if len(cur["trace"]) < 3000:
                cur["trace"].append(self.trace[-1])
            if info.t - cur["trip_t"] >= self.post_s:
                self._close()

    def _close(self) -> None:
        if self.cur is not None:
            self.episodes.append(self.cur)
        self.cur = None

    def finish(self) -> list[dict]:
        self._close()
        return self.episodes


CTRL_LABEL = {"adaptive": "C", "adaptive_learned": "G", "spiral_pull": "H", "spiral_rcc_pull": "I",
              "spiral_rcc_verify": "J"}


def _load_episodes(root: Path, counterfactual: bool = False) -> list[dict]:
    """Model runs only, or (counterfactual=True) counterfactual runs only, each tagged with its variant."""
    rows = []
    for f in sorted(root.glob("*/episodes.csv")):
        cfg = json.loads((f.parent / "config.json").read_text())
        if bool(cfg.get("counterfactual")) != counterfactual:
            continue
        a = cfg["args"]
        variant = f"damping {a['hook_damping']:g} N s/m" if a["hook_damping"] else ""
        if a.get("hook_stiffness") is not None:
            variant = (variant + ", " if variant else "") + f"stiffness {a['hook_stiffness']:g} N/m"
        with f.open() as fh:
            for r in csv.DictReader(fh):
                r["backend"] = r["backend"] + (f" ({variant})" if variant else "")
                rows.append(r)
    return rows


def _f(x) -> float:
    return float(x) if x not in (None, "", "None") else float("nan")


def tables(root: Path) -> None:
    cf = "counterfactual" in root.name
    rows = _load_episodes(root, cf)
    eps = [r for r in rows if r["episode"] not in ("-1", "")]
    trials = {(r["backend"], r["suite"], r["seed"], r["condition"], r["controller"], r["trial_index"]): r for r in rows}
    out = ["# v0.2f pull overshoot tables", "",
           "Development measurement, seeds 2026 and 2027, made by `python -m experiments.v02f_pull_overshoot "
           f"--tables {root}` from the episodes.csv files in this folder "
           + ("(counterfactual hook runs only: NOT the model)." if cf else "(model runs only, counterfactual runs excluded)."),
           "Peak = most negative tared, filtered axial F/T force from the pull start to 0.1 s after the guard ends "
           "the pull, sign flipped. Hook = the simulator's latch-hook force (2 kHz). Retention and latch break "
           "threshold: 58 N.", ""]
    out += ["## Pulls per machine and controller", "",
            "| machine | ctrl | trials | pulls | held (guard tripped on force) | target N | peak/target p50 | p99 | max | "
            "> 1.10 | > 1.25 | max peak N | max hook N (window) | hook > 58 N | max meas. abs(F) N | abs(F) > 48 N |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    machines = sorted({r["backend"] for r in rows}, key=lambda m: (not m.startswith("gantry"), m))
    for b in machines:
        for c, lab in CTRL_LABEL.items():
            e = [r for r in eps if r["backend"] == b and r["controller"] == c]
            n_tr = len({k for k in trials if k[0] == b and k[4] == c})
            if not n_tr:
                continue
            ratio = np.array([_f(r["ratio_meas"]) for r in e]) if e else np.array([np.nan])
            tg = sorted({r["target_n"] for r in e})
            hook = [_f(r["hook_max_n"]) for r in e] or [np.nan]
            fn = [_f(r["fnorm_max_n"]) for r in e] or [np.nan]
            out.append(f"| {b} | {lab} | {n_tr} | {len(e)} | {sum(r['held'] == 'True' for r in e)} | {'/'.join(tg)} | "
                       f"{np.nanpercentile(ratio, 50):.3f} | {np.nanpercentile(ratio, 99):.3f} | {np.nanmax(ratio):.3f} | "
                       f"{int((ratio > 1.10).sum())} | {int((ratio > 1.25).sum())} | "
                       f"{max(_f(r['peak_pull_meas_n']) for r in e) if e else float('nan'):.1f} | {max(hook):.1f} | "
                       f"{sum(h > 58.0 for h in hook)} | {max(fn):.1f} | {sum(x > 48.0 for x in fn)} |")
    out += ["", "## Pulls over 1.10 x target", "",
            "| machine | suite | seed | condition | ctrl | trial | pull | target N | trip N | peak N | ratio | hook N | "
            "held | after | outcome |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    big = sorted((r for r in eps if _f(r["ratio_meas"]) > 1.10), key=lambda r: -_f(r["ratio_meas"]))
    for r in big[:60]:
        out.append(f"| {r['backend']} | {r['suite']} | {r['seed']} | {r['condition']} | {CTRL_LABEL[r['controller']]} | "
                   f"{r['trial_index']} | {r['episode']} | {r['target_n']} | {r['trip_f_ax_n']} | {r['peak_pull_meas_n']} | "
                   f"{_f(r['ratio_meas']):.3f} | {r['hook_max_n']} | {r['held']} | {r['phase_after']} | "
                   f"{r['failure_reason']} |")
    if len(big) > 60:
        out.append(f"| ... {len(big) - 60} more | | | | | | | | | | | | | | |")
    out += ["", "## Latch breaks (whole trial)", "",
            "| machine | ctrl | trials with a broken latch | in a pull window | where (state/phase) | max hook N in trial |",
            "|---|---|---|---|---|---|"]
    for b in machines:
        for c, lab in CTRL_LABEL.items():
            tr = [r for k, r in trials.items() if k[0] == b and k[4] == c]
            if not tr:
                continue
            brk = [r for r in tr if r.get("trial_latch_broken") == "True"]
            inwin = sum(1 for r in eps if r["backend"] == b and r["controller"] == c
                        and r["latch_broke_in_window"] == "True")
            where: dict[str, int] = {}
            for r in brk:
                where[r.get("break_state", "")] = where.get(r.get("break_state", ""), 0) + 1
            mh = max(_f(r["trial_hook_max_n"]) for r in tr)
            out.append(f"| {b} | {lab} | {len(brk)} | {inwin} | {', '.join(f'{k}: {v}' for k, v in where.items())} | "
                       f"{mh:.1f} |")
    out += ["", "## Good parts: guard-tripped pulls by trial outcome", "",
            "| machine | ctrl | held pulls on good parts | of those, trial not seated | not-seated with latch broken |",
            "|---|---|---|---|---|"]
    for b in machines:
        for c, lab in CTRL_LABEL.items():
            e = [r for r in eps if r["backend"] == b and r["controller"] == c and not r["defect"] and r["held"] == "True"]
            if not e:
                continue
            ns = [r for r in e if r["gt_seated"] != "True"]
            out.append(f"| {b} | {lab} | {len(e)} | {len(ns)} | {sum(r['trial_latch_broken'] == 'True' for r in ns)} |")
    (root / "TABLES.md").write_text("\n".join(out) + "\n")
    print(f"wrote {root / 'TABLES.md'}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--backend", choices=["gantry", "arm"])
    ap.add_argument("--suite", choices=["latching", "latch_spread"])
    ap.add_argument("--seed", type=int)
    ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--first", type=int, default=0, help="first trial index")
    ap.add_argument("--conditions", default="")
    ap.add_argument("--controllers", default="adaptive,adaptive_learned,spiral_pull,spiral_rcc_pull,spiral_rcc_verify")
    ap.add_argument("--post-s", type=float, default=0.1, help="window after the trip tick")
    ap.add_argument("--hook-damping", type=float, default=0.0, help="counterfactual N s/m on the engaged hook")
    ap.add_argument("--hook-stiffness", type=float, default=None, help="counterfactual N/m (model: 2e5)")
    ap.add_argument("--traces", type=int, default=0, help="keep the per-tick trace of the N largest overshoots")
    ap.add_argument("--out")
    ap.add_argument("--tables", default="", help="write TABLES.md from every episodes.csv under this folder")
    args = ap.parse_args()
    if args.tables:
        tables(Path(args.tables))
        return
    if not (args.backend and args.suite and args.seed and args.out):
        raise SystemExit("--backend, --suite, --seed and --out are required for a run")
    if args.seed not in DEV_SEEDS:
        raise SystemExit("development seeds 2026 and 2027 only")
    os.environ["DEFEX_BACKEND"] = args.backend
    os.environ.setdefault("OMP_NUM_THREADS", "1")

    probe = _install_hook_probe(args.hook_damping, args.hook_stiffness)

    from defex.control.registry import make_controller
    from defex.tasks.conditions import latch_spread_conditions, latching_conditions
    from defex.tasks.insertion import InsertionTask
    from defex.tasks.scenarios import sample_scenario
    from experiments.runner import environment_info, make_backend, nominal_socket_pose, write_outputs

    conds = (latching_conditions if args.suite == "latching" else latch_spread_conditions)()
    if args.conditions:
        want = set(args.conditions.split(","))
        conds = [c for c in conds if c.name in want]
    controllers = [c for c in args.controllers.split(",") if c]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    task = InsertionTask(backend=make_backend())
    rec = PullRecorder(probe, args.post_s)
    results, rows, traces = [], [], []
    load0 = os.getloadavg()
    t_start = time.time()
    for cond in conds:
        nominal = nominal_socket_pose(cond, task.fixture)
        for name in controllers:
            for i in range(args.first, args.first + args.trials):
                scenario = sample_scenario(cond, i, args.seed, nominal)
                ctrl = make_controller(name)
                rec.reset()
                rec.break_info = None
                res = task.run(ctrl, scenario, on_step=rec)
                results.append(res)
                eps = rec.finish()
                brk = rec.break_info
                for k, e in enumerate(eps):
                    peak = -min(e["min_f_ax"], 0.0)
                    row = {
                        "backend": args.backend, "suite": args.suite, "seed": args.seed, "condition": cond.name,
                        "group": cond.group, "defect": cond.defect or "", "controller": name, "trial_index": i,
                        "episode": k, "t0": round(e["t0"], 4), "target_n": round(e["target_n"], 3),
                        "trip_t": None if e["trip_t"] is None else round(e["trip_t"], 4),
                        "trip_f_ax_n": None if e["trip_f_ax"] is None else round(e["trip_f_ax"], 3),
                        "held": bool(e["trip_f_ax"] is not None and e["trip_f_ax"] <= -e["target_n"]),
                        "peak_pull_meas_pull_n": round(-min(e["min_f_ax_pull"], 0.0), 3),
                        "peak_pull_meas_n": round(peak, 3),
                        "ratio_meas": round(peak / e["target_n"], 4),
                        "hook_max_pull_n": round(e["hook_max_pull"], 3), "hook_max_n": round(e["hook_max"], 3),
                        "contact10_max_n": round(e["contact10_max"], 3), "fnorm_max_n": round(e["fnorm_max"], 3),
                        "latch_broke_in_window": e["broke"], "state_after": e["state_after"],
                        "phase_after": e["phase_after"],
                        "trial_hook_max_n": round(probe["trial_max"], 3),
                        "trial_latch_broken": bool(brk is not None),
                        "success": res.success, "failure_reason": res.failure_reason, "gt_seated": res.gt_seated,
                    }
                    rows.append(row)
                    if args.traces:
                        traces.append((peak / e["target_n"], row, e["trace"]))
                        traces.sort(key=lambda x: -x[0])
                        del traces[args.traces:]
                if not eps:
                    rows.append({"backend": args.backend, "suite": args.suite, "seed": args.seed,
                                 "condition": cond.name, "group": cond.group, "defect": cond.defect or "",
                                 "controller": name, "trial_index": i, "episode": -1,
                                 "trial_hook_max_n": round(probe["trial_max"], 3),
                                 "trial_latch_broken": bool(brk is not None),
                                 "break_state": "" if brk is None else f"{brk['state']}/{brk['phase']}",
                                 "success": res.success, "failure_reason": res.failure_reason,
                                 "gt_seated": res.gt_seated})
                elif brk is not None:
                    rows[-1]["break_state"] = f"{brk['state']}/{brk['phase']}"
        print(f"{cond.name}: {len(results)} trials, {time.time() - t_start:.0f} s, load {os.getloadavg()}", flush=True)
    write_outputs(results, out, wall_time_s=time.time() - t_start)
    keys: list[str] = []
    for r in rows:
        keys.extend(k for k in r if k not in keys)
    with (out / "episodes.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    for n, (ratio, row, tr) in enumerate(traces):
        with (out / f"trace_{n}.csv").open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["# " + json.dumps({k: row[k] for k in ("condition", "controller", "trial_index", "episode",
                                                                "target_n", "peak_pull_meas_n", "hook_max_n")})])
            w.writerow(["t", "state", "phase", "f_ax_meas_n", "hook_n"])
            w.writerows([(round(a, 4), b, c, round(d, 3), round(e, 3)) for a, b, c, d, e in tr])
    cfg = {"script": "experiments/v02f_pull_overshoot.py", "args": vars(args), "environment": environment_info(),
           "load_avg_start": load0, "load_avg_end": os.getloadavg(), "wall_s": time.time() - t_start,
           "counterfactual": bool(args.hook_damping or args.hook_stiffness is not None),
           "label": "development measurement"}
    (out / "config.json").write_text(json.dumps(cfg, indent=1))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
