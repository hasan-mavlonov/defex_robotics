"""v0.2d tilt check: what C (and G) observe at every VERIFY, next to the true tilt (offline; uses ground truth).

    python -m experiments.v02d_tilt_features --backend arm --suite latching --conditions mf_noise_1mm \\
        --seeds 3001-3010 --trials 40 --workers 3 --out results/v0.2d_tilt_check/features/arm_mf.jsonl.gz

One JSON object per trial: identifiers, the trial outcome (as in trials.csv), and per VERIFY
the controller-visible quantities (wrench windows, seat-conform outcome, wall probes, commanded
and measured orientation relative to C's socket-axis estimate) plus the true connector tilt at
that moment. Ground truth is attached here, after the controller has read the observation; it
never reaches a controller. The controller runs unchanged (instance methods are wrapped, and
the tilt verdict, when present, is evaluated in shadow: its result is recorded, not acted on).
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import time
from collections import deque
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from defex.config import DEG, MM

DEV_SEEDS = frozenset((2026, 2027, *range(3001, 3041)))

_TASK = None


def parse_seeds(text: str) -> list[int]:
    out: list[int] = []
    for part in text.split(","):
        if "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    bad = [s for s in out if s not in DEV_SEEDS]
    if bad:
        raise SystemExit(f"development seeds only (2026, 2027, 3001-3040), not {bad}")
    return out


def all_conditions(suite: str):
    from defex.tasks.conditions import (
        heldout_conditions,
        latch_spread_conditions,
        latching_conditions,
        standard_conditions,
    )

    return {"standard": standard_conditions, "heldout": heldout_conditions, "latching": latching_conditions,
            "latch_spread": latch_spread_conditions}[suite]()


def _rv_deg(R: np.ndarray) -> list[float]:
    from defex.utils.transforms import matrix_to_rotvec

    return (matrix_to_rotvec(R) / DEG).tolist()


def _tilt_deg(R: np.ndarray) -> float:
    return float(np.degrees(np.arccos(np.clip(R[2, 2], -1.0, 1.0))))


def instrument(ctrl, gt_box: dict) -> dict:
    """Wrap the VERIFY entry points of a C-family controller instance; returns the record it fills."""
    from defex.utils.transforms import rotvec_to_matrix

    rec: dict = {"verifies": [], "slid_in": [], "folds": []}
    buf: deque = deque(maxlen=100)

    def orient(obs) -> dict:
        Rc = ctrl.R_corr
        rel = obs.rel_pose.R
        cmd = (rotvec_to_matrix(ctrl.adm_rot.x) @ rotvec_to_matrix(ctrl.adm_conf.x))
        return {
            "est_vs_vision_rv": _rv_deg(rel),
            "est_vs_corr_rv": _rv_deg(rel @ Rc.T),
            "est_tilt_vs_corr": _tilt_deg(Rc.T @ rel),
            "est_tilt_vs_vision": _tilt_deg(rel),
            "R_corr_rv": _rv_deg(Rc),
            "adm_rot_deg": (np.asarray(ctrl.adm_rot.x) / DEG).tolist(),
            "adm_conf_deg": (np.asarray(ctrl.adm_conf.x) / DEG).tolist(),
            "cmd_offset_rv": _rv_deg(cmd),
            "yaw_adj_deg": float(ctrl.yaw_adj / DEG),
            "lag_deg": (ctrl._orientation_lag(obs) / DEG).tolist(),
        }

    def window(phase: str | None = None, n: int = 25) -> dict:
        rows = [b for b in buf if phase is None or b[0] == phase][-n:]
        if not rows:
            return {}
        F = np.mean([r[2] for r in rows], axis=0)
        T = np.mean([r[3] for r in rows], axis=0)
        fz = max(float(F[2]), 1e-6)
        return {"F": F.tolist(), "T": T.tolist(), "cop_mm": [float(-T[1] / fz / MM), float(T[0] / fz / MM)],
                "n": len(rows)}

    def gt() -> dict:
        g = gt_box.get("rel")
        if g is None:
            return {}
        return {"tilt_deg": _tilt_deg(g.R), "rv_deg": _rv_deg(g.R), "depth_mm": float(-g.p[2] / MM),
                "lat_mm": (g.p[:2] / MM).tolist()}

    def snap(obs, kind: str) -> dict:
        d = ctrl.diagnosis
        out = {"kind": kind, "t": float(obs.t - ctrl.t_start), "attempt": int(ctrl.attempts), "phase": ctrl.phase,
               "depth_mm": float(ctrl._corrected_depth(obs) / MM), "touch_calibrated": bool(ctrl.touch_calibrated),
               **orient(obs), "gt": gt(), "win": window()}
        if d is not None:
            out["diag"] = {"kind": d.kind, "trigger": d.trigger, "depth_mm": float(d.depth / MM),
                           "axial_n": float(d.axial_force), "lat_n": np.asarray(d.lateral_force, float).tolist(),
                           "torque": np.asarray(d.torque, float).tolist(),
                           "cop_mm": None if d.cop is None else (np.asarray(d.cop) / MM).tolist()}
        if hasattr(ctrl, "_tilt_verdict"):
            out["shadow"] = ctrl._tilt_verdict(obs, record=True)
        return out

    orig = {k: getattr(ctrl, k) for k in ("_begin_verify", "_verify_step", "_succeed", "_lateral_verdict",
                                          "_wall_yaw_verdict", "_detect_step", "_conclude_detect", "_enter")}

    def begin_verify(obs):
        rec["verifies"].append({"begin": snap(obs, "begin"), "events": []})
        return orig["_begin_verify"](obs)

    def verify_step(obs):
        ph = ctrl.phase
        F, T = ctrl._wrench(obs)
        buf.append((ph, obs.t, F.copy(), T.copy()))
        cmd = orig["_verify_step"](obs)
        v = rec["verifies"][-1] if rec["verifies"] else None
        if v is not None and ph == "seat_conform" and ctrl.phase != "seat_conform":
            v["seat_conform"] = {"rc_flat": ctrl._rc_flat.tolist(), "rc_done": ctrl._rc_done.tolist(),
                                 "rc_dir": None if ctrl._rc_dir is None else ctrl._rc_dir.tolist(),
                                 "win": window("seat_conform"), **orient(obs), "gt": gt()}
        if v is not None and ph == "pull" and ctrl.phase != "pull":
            v["pull"] = {"win": window("pull", 10), **orient(obs), "gt": gt()}
        if v is not None and ph == "preload" and ctrl.phase != "preload":
            v["preload"] = {"win": window("preload"), **orient(obs), "gt": gt()}
        return cmd

    def lateral_verdict(obs):
        v = rec["verifies"][-1]
        v["lateral"] = {"results": [[float(r), float(t / MM)] for r, t in ctrl._verify_results],
                        "contacts": [[float(p / MM), float(r), float(tz)] for p, r, tz in ctrl._wall_contacts[-2:]],
                        "gt": gt()}
        return orig["_lateral_verdict"](obs)

    def wall_yaw_verdict(obs):
        v = rec["verifies"][-1]
        v.setdefault("wall_yaw", []).append(
            {"contacts": [[float(p / MM), float(r), float(tz)] for p, r, tz in ctrl._wall_contacts[-2:]],
             "need_mm": float(max(ctrl._wall_half_travel(ctrl.cfg.wall_yaw_tolerance_deg * DEG),
                                  ctrl.cfg.wall_yaw_min_free_fraction * ctrl._wall_half_travel(0.0)) / MM)})
        return orig["_wall_yaw_verdict"](obs)

    def succeed(obs):
        if rec["verifies"]:
            rec["verifies"][-1]["pass"] = snap(obs, "pass")
        return orig["_succeed"](obs)

    def detect_step(obs):
        ph, st = ctrl.phase, ctrl.state
        conf = np.asarray(ctrl.adm_conf.x).copy()
        cmd = orig["_detect_step"](obs)
        if st == "DETECT" and ph in ("conform", "measure") and ctrl.state == "INSERT":
            rec["slid_in"].append({"t": float(obs.t - ctrl.t_start), "attempt": int(ctrl.attempts),
                                   "adm_conf_deg": (conf / DEG).tolist(), "gt": gt()})
        return cmd

    def conclude_detect(obs, window_):
        before = ctrl.R_corr.copy()
        cmd = orig["_conclude_detect"](obs, window_)
        if not np.allclose(before, ctrl.R_corr):
            rec["folds"].append({"t": float(obs.t - ctrl.t_start), "R_corr_rv": _rv_deg(ctrl.R_corr), "gt": gt()})
        return cmd

    def enter(t, state, phase="", detail=""):
        if rec["verifies"] and ctrl.state == "VERIFY" and state != "VERIFY":
            rec["verifies"][-1]["exit"] = {"to": state, "detail": detail, "t": float(t - ctrl.t_start)}
        return orig["_enter"](t, state, phase, detail)

    ctrl._begin_verify = begin_verify
    ctrl._verify_step = verify_step
    ctrl._succeed = succeed
    ctrl._lateral_verdict = lateral_verdict
    ctrl._wall_yaw_verdict = wall_yaw_verdict
    ctrl._detect_step = detect_step
    ctrl._conclude_detect = conclude_detect
    ctrl._enter = enter
    return rec


def _init() -> None:
    global _TASK
    from defex.tasks.insertion import InsertionTask
    from experiments.runner import make_backend

    os.environ.setdefault("OMP_NUM_THREADS", "1")
    _TASK = InsertionTask(backend=make_backend())


def run_job(job: tuple) -> list[dict]:
    from defex.control.registry import make_controller
    from defex.tasks.scenarios import sample_scenario
    from experiments.runner import nominal_socket_pose

    suite, cond_name, controller, seed, indices = job
    if _TASK is None:
        _init()
    cond = {c.name: c for c in all_conditions(suite)}[cond_name]
    nominal = nominal_socket_pose(cond, _TASK.fixture)
    out = []
    for i in indices:
        scenario = sample_scenario(cond, i, seed, nominal)
        ctrl = make_controller(controller)
        gt_box: dict = {}
        rec = instrument(ctrl, gt_box)

        def on_step(info, gt_box=gt_box):
            gt_box["rel"] = info.gt.socket_pose.inv() @ info.gt.connector_pose

        res = _TASK.run(ctrl, scenario, on_step=on_step)
        row = res.to_row()
        row.update(base_seed=seed, suite=suite)
        row["record"] = rec
        row["events"] = [e for e in res.events if e[1] in ("verify", "wall_yaw", "seat_conform", "latch", "tilt",
                                                             "reseat", "conform", "surface_alignment", "finish")]
        out.append(row)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--backend", choices=["gantry", "arm"], default="arm")
    ap.add_argument("--suite", choices=["standard", "heldout", "latching", "latch_spread"], default="standard")
    ap.add_argument("--conditions", default="", help="comma-separated (default: every condition of the suite)")
    ap.add_argument("--controllers", default="adaptive")
    ap.add_argument("--seeds", required=True)
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--first-trial", type=int, default=0)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--chunk", type=int, default=5)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.environ["DEFEX_BACKEND"] = args.backend
    seeds = parse_seeds(args.seeds)
    conds = [c.name for c in all_conditions(args.suite)]
    if args.conditions:
        wanted = args.conditions.split(",")
        unknown = set(wanted) - set(conds)
        if unknown:
            raise SystemExit(f"unknown conditions: {sorted(unknown)}")
        conds = [c for c in conds if c in wanted]
    idx = list(range(args.first_trial, args.first_trial + args.trials))
    jobs = [(args.suite, c, ctrl, s, tuple(idx[k:k + args.chunk]))
            for s in seeds for c in conds for ctrl in args.controllers.split(",") for k in range(0, len(idx), args.chunk)]
    total = sum(len(j[4]) for j in jobs)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    from experiments.runner import environment_info

    meta = {"args": vars(args), "environment": environment_info(), "trials": total}
    out.with_suffix("").with_suffix(".meta.json").write_text(json.dumps(meta, indent=1))
    t0 = time.time()
    done = 0
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=_init) as pool:
        for fut in as_completed([pool.submit(run_job, j) for j in jobs]):
            rows.extend(fut.result())
            done = len(rows)
            el = time.time() - t0
            print(f"\r  {done}/{total} trials, {done / max(el, 1e-6):.1f}/s, elapsed {el:.0f} s", end="", flush=True)
    print()
    rows.sort(key=lambda r: (r["base_seed"], r["condition"], r["controller"], r["trial_index"]))
    with gzip.open(out, "wt") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
