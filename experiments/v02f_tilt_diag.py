"""v0.2f tilt diagnosis: where C's, G's and J's tilt evidence differs from the true plug tilt (offline, ground truth).

    python experiments/v02f_tilt_diag.py trace --backend arm --suite latching --condition mf_noise_1mm \\
        --controller adaptive_learned --index 130 --seed 20261130
    python experiments/v02f_tilt_diag.py run --backend arm --suite latching,latch_spread --seeds 2026,2027 \\
        --trials 50 --controllers adaptive,adaptive_learned --workers 2 --out runs/arm_latch.jsonl.gz

``trace`` replays one trial and prints, at every latch check and at the end, the decomposition of the tilt
evidence: the true plug axis, C's socket-axis estimate (camera plus R_corr) and its plug-axis estimate (encoders
plus the in-hand estimate), each against the true socket axis. Benchmark seeds are allowed only for the trials
the v0.2e report names (results/benchmark_v0.2e/REPORT.md), and only for diagnosis.

``run`` is the v0.2e tilt-guard collector (experiments/v02e_tilt_guard.py) plus ground truth: at every latch check
(``_begin_latch_verify``) and at every declared seat (``_succeed``) it records the controller's evidence and the
true poses. It reads ground truth from the backend between ticks; the controller never sees it. Dev seeds only.

Small-angle tilt vectors are (x, y) components, in degrees, of an axis expressed in the true socket frame.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import replace
from pathlib import Path

import numpy as np

DEV_SEEDS = frozenset((2026, 2027))
VALIDATION_SEEDS = frozenset((4007,))
# (seed, backend, condition, controller, trial) that results/benchmark_v0.2e/REPORT.md names as failures.
NAMED = {
    (20261130, "arm", "mf_noise_1mm", "adaptive_learned", 130),  # G's bad unit
    (20261130, "arm", "mf_noise_1mm", "adaptive", 130),  # C on the same trial (time limit)
    (20261130, "arm", "mf_noise_1mm", "spiral_rcc_verify", 46),  # J's arm bad unit
}
C_FAMILY = ("adaptive", "adaptive_learned", "spiral_rcc_verify")
_TASK = None


def _deg(x: float) -> float:
    return float(np.degrees(x))


def _angle(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.arccos(np.clip(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)), -1.0, 1.0)))


def _vec(R_sock_true: np.ndarray, axis_world: np.ndarray) -> list[float]:
    a = R_sock_true.T @ axis_world
    return [_deg(np.arcsin(np.clip(a[0], -1, 1))), _deg(np.arcsin(np.clip(a[1], -1, 1)))]


def decompose(v, obs, gt) -> dict:
    """Controller evidence against ground truth at one observation (v: C's code, obs: what it was given)."""
    from defex.utils.transforms import matrix_to_rotvec, twist_about_axis

    Rs = gt.socket_pose.R
    z_true_sock = Rs[:, 2]
    z_true_plug = gt.connector_pose.R[:, 2]
    z_cam = obs.socket_pose.R[:, 2]
    z_est_sock = obs.socket_pose.R @ v.R_corr[:, 2]
    z_est_plug = obs.connector_pose.R[:, 2]
    rel_true = gt.socket_pose.inv() @ gt.connector_pose
    return {
        "true_tilt": _deg(_angle(z_true_plug, z_true_sock)),
        "true_yaw": _deg(twist_about_axis(rel_true.R)),
        "true_depth_mm": float(-rel_true.p[2] * 1e3),
        "meas_tilt": _deg(_angle(z_est_plug, z_est_sock)),
        "cam_err": _deg(_angle(z_cam, z_true_sock)),
        "sock_err": _deg(_angle(z_est_sock, z_true_sock)),
        "plug_err": _deg(_angle(z_est_plug, z_true_plug)),
        "v_true": _vec(Rs, z_true_plug),
        "v_sock": _vec(Rs, z_est_sock),
        "v_cam": _vec(Rs, z_cam),
        "v_plug": _vec(Rs, z_est_plug),
        "rcorr_deg": [_deg(x) for x in matrix_to_rotvec(v.R_corr)],
        "est_yaw": _deg(twist_about_axis(obs.rel_pose.R)),
    }


def _would_fail(v, tilt: float, edge: float) -> bool:
    c = v.cfg
    held = edge > c.tilt_check_edge_fraction or v._tilt_failed_attempt == v.attempts
    return bool(tilt > c.tilt_check_deg * np.pi / 180.0 and held)


def instrument(ctrl, backend) -> tuple[list[dict], list[dict]]:
    """Wrap C's latch-check entry and its _succeed in ``ctrl`` (C, G, or J's verifier)."""
    v = getattr(ctrl, "verifier", ctrl)
    checks: list[dict] = []
    seats: list[dict] = []
    orig_latch = v._begin_latch_verify
    orig_succeed = v._succeed

    def begin_latch_verify(obs):
        recent = list(v._recent)[len(v._recent) // v.cfg.detect_discard_divisor:]
        f_ax = float(np.mean([o.force[2] for o in recent]) - v.bias_f[2]) if recent else None
        if v.phase == "held_reseat":
            path = "held_reseat"
        elif v.phase == "bottom_proof":
            held = v._proof_t_force is not None and obs.t - v._proof_t_force >= v.cfg.proof_push_s
            path = "proof" if held else "proof_timeout"
        elif v is not ctrl and not v._recent:
            path = "handover"
        else:
            path = f"detect:{v._trigger}"
        tilt, edge = v._tilt_evidence(obs)
        rec = {"t": float(obs.t - v.t_start), "attempt": int(v.attempts), "path": path, "f_ax": f_ax,
               "n": len(recent), "tilt_deg": _deg(tilt), "edge": edge, "would_fail": _would_fail(v, tilt, edge),
               "floor": float(v._tilt_force_floor())}
        rec.update(decompose(v, obs, backend.ground_truth()))
        n_ev = len(v.events)
        cmd = orig_latch(obs)
        logged = [e.detail for e in v.events[n_ev:] if e.kind == "tilt"]
        verdict = "none"
        if logged:
            d = logged[0]
            verdict = "PASS" if d.endswith("PASS") else "FAIL" if d.endswith("FAIL") else "no verdict"
        rec["verdict"] = verdict
        checks.append(rec)
        return cmd

    def succeed(obs):
        tilt, edge = v._tilt_evidence(obs)
        recent = list(v._recent)[len(v._recent) // v.cfg.detect_discard_divisor:]
        f_ax = float(np.mean([o.force[2] for o in recent]) - v.bias_f[2]) if recent else None
        rec = {"t": float(obs.t - v.t_start), "attempt": int(v.attempts), "phase": v.phase, "f_ax": f_ax,
               "tilt_deg": _deg(tilt), "edge": edge}
        rec.update(decompose(v, obs, backend.ground_truth()))
        seats.append(rec)
        return orig_succeed(obs)

    v._begin_latch_verify = begin_latch_verify
    v._succeed = succeed
    return checks, seats


def all_conditions(suite: str):
    from defex.tasks.conditions import latch_spread_conditions, latching_conditions, standard_conditions

    return {"latching": latching_conditions, "latch_spread": latch_spread_conditions,
            "standard": standard_conditions}[suite]()


def _init() -> None:
    global _TASK
    from defex.tasks.insertion import InsertionTask
    from experiments.runner import make_backend

    os.environ.setdefault("OMP_NUM_THREADS", "1")
    _TASK = InsertionTask(backend=make_backend())


def _make(controller: str, overrides: dict | None):
    from defex.control.registry import make_controller

    ctrl = make_controller(controller)
    if overrides:
        v = getattr(ctrl, "verifier", ctrl)
        v.cfg = replace(v.cfg, **overrides)
    return ctrl


def run_job(job: tuple) -> list[dict]:
    from defex.tasks.scenarios import sample_scenario
    from experiments.runner import nominal_socket_pose

    suite, cond_name, controller, seed, indices, overrides, j_overrides = job
    if _TASK is None:
        _init()
    cond = {c.name: c for c in all_conditions(suite)}[cond_name]
    nominal = nominal_socket_pose(cond, _TASK.fixture)
    out = []
    for i in indices:
        ctrl = _make(controller, overrides)
        for k, val in (j_overrides or {}).items():
            if hasattr(ctrl, "verifier"):
                setattr(ctrl, k, val)
        checks, seats = instrument(ctrl, _TASK.backend) if controller in C_FAMILY else ([], [])
        res = _TASK.run(ctrl, sample_scenario(cond, i, seed, nominal))
        row = res.to_row()
        row.update(base_seed=seed, suite=suite, backend=os.environ.get("DEFEX_BACKEND", "gantry"), checks=checks,
                   seats=seats, ev=[[t, k, d] for t, k, d in res.events
                                    if k in ("tilt", "wall_yaw", "yaw", "verify", "latch", "verify_handover")])
        out.append(row)
    return out


def _parse_overrides(s: str) -> dict:
    out = {}
    for kv in filter(None, s.split(",")):
        k, val = kv.split("=")
        out[k] = {"true": True, "false": False}.get(val.lower(), None)
        if out[k] is None:
            out[k] = float(val)
    return out


def cmd_run(args) -> None:
    os.environ["DEFEX_BACKEND"] = args.backend
    seeds = [int(s) for s in args.seeds.split(",")]
    allowed = DEV_SEEDS | (VALIDATION_SEEDS if args.validation else frozenset())
    if not set(seeds) <= allowed:
        raise SystemExit(f"seeds {sorted(set(seeds) - allowed)} not allowed (dev 2026, 2027; 4007 with --validation)")
    conds = [(su, c.name) for su in args.suite.split(",") for c in all_conditions(su)]
    if args.conditions:
        conds = [(su, c) for su, c in conds if c in args.conditions.split(",")]
    overrides = _parse_overrides(args.cfg)
    j_overrides = _parse_overrides(args.j)
    idx = list(range(args.trials))
    jobs = [(su, c, ctrl, s, tuple(idx[k:k + args.chunk]), overrides, j_overrides) for s in seeds for su, c in conds
            for ctrl in args.controllers.split(",") for k in range(0, len(idx), args.chunk)]
    total = sum(len(j[4]) for j in jobs)
    import defex

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    meta = {"args": vars(args), "defex": str(Path(defex.__file__).parent), "trials": total}
    out.with_suffix("").with_suffix(".meta.json").write_text(json.dumps(meta, indent=1))
    t0, rows = time.time(), []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=_init) as pool:
        for fut in as_completed([pool.submit(run_job, j) for j in jobs]):
            rows.extend(fut.result())
            print(f"\r  {len(rows)}/{total} trials, elapsed {time.time() - t0:.0f} s", end="", flush=True)
    print()
    rows.sort(key=lambda r: (r["base_seed"], r["suite"], r["condition"], r["controller"], r["trial_index"]))
    with gzip.open(out, "wt") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(f"wrote {out} ({defex.__file__})")


def cmd_trace(args) -> None:
    key = (args.seed, args.backend, args.condition, args.controller, args.index)
    if args.seed not in DEV_SEEDS and key not in NAMED:
        raise SystemExit("dev seeds, or a trial the v0.2e report names")
    os.environ["DEFEX_BACKEND"] = args.backend
    from defex.tasks.scenarios import sample_scenario
    from experiments.runner import nominal_socket_pose

    _init()
    cond = {c.name: c for c in all_conditions(args.suite)}[args.condition]
    ctrl = _make(args.controller, _parse_overrides(args.cfg))
    for k, val in _parse_overrides(args.j).items():
        setattr(ctrl, k, val)
    checks, seats = instrument(ctrl, _TASK.backend)
    v = getattr(ctrl, "verifier", ctrl)
    ticks: list[dict] = []

    def on_step(info) -> None:
        if v.S is None:
            return
        d = decompose(v, info.obs, info.gt)
        d.update(t=float(info.obs.t), state=str(getattr(ctrl, "state", "")), phase=str(getattr(v, "phase", "")),
                 fz=float(info.obs.force[2] - v.bias_f[2]))
        ticks.append(d)

    res = _TASK.run(ctrl, sample_scenario(cond, args.index, args.seed, nominal_socket_pose(cond, _TASK.fixture)),
                    on_step=on_step if args.ticks else None)
    row = res.to_row()
    print(f"{key}: success={row['success']} reason={row['failure_reason']} declared={row['declared_success']} "
          f"depth={row['final_depth_mm']:.2f} tilt={row['final_tilt_deg']:.2f} yaw={row['final_yaw_deg']:.2f} "
          f"cycle={row['cycle_time_s']:.2f}")
    print(f"scenario: dist_tilt={row['dist_tilt_deg']:.2f} az={row['dist_tilt_azimuth_deg']:.1f} "
          f"grasp_tilt={row['dist_grasp_tilt_deg']:.2f}")
    for e in res.events:
        if args.events or e[1] in ("tilt", "latch", "verify", "detect", "conform", "verify_handover", "proof_push",
                                   "protective_stop", "insert", "reseat", "gentle_retract"):
            print(f"  {e[0]:7.3f} {e[1]:16s} {e[2]}")
    fmt = ("  {label}: f_ax={f} edge={edge:.2f} meas={meas_tilt:.2f} true={true_tilt:.2f} cam_err={cam_err:.2f} "
           "sock_err={sock_err:.2f} plug_err={plug_err:.2f} v_true={vt} v_sock={vs} v_cam={vc} v_plug={vp} "
           "rcorr={rc} depth={true_depth_mm:.2f}")
    for c in checks:
        print(fmt.format(label=f"latch check t={c['t']:.3f} {c['path']} {c['verdict']}",
                         f="none" if c["f_ax"] is None else f"{c['f_ax']:.1f}",
                         vt=np.round(c["v_true"], 2).tolist(), vs=np.round(c["v_sock"], 2).tolist(),
                         vc=np.round(c["v_cam"], 2).tolist(), vp=np.round(c["v_plug"], 2).tolist(),
                         rc=np.round(c["rcorr_deg"], 2).tolist(), **c))
    if args.ticks and ticks:
        out = Path(args.ticks)
        out.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(out, "wt") as fh:
            json.dump(ticks, fh)
        print(f"wrote {len(ticks)} ticks to {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--backend", choices=["gantry", "arm"], default="arm")
    r.add_argument("--suite", default="latching,latch_spread")
    r.add_argument("--conditions", default="")
    r.add_argument("--controllers", default=",".join(C_FAMILY))
    r.add_argument("--seeds", default="2026,2027")
    r.add_argument("--trials", type=int, default=20)
    r.add_argument("--workers", type=int, default=1)
    r.add_argument("--chunk", type=int, default=5)
    r.add_argument("--cfg", default="", help="AdaptiveConfig overrides on C's code, k=v,...")
    r.add_argument("--j", default="", help="attribute overrides on J's controller, k=v,...")
    r.add_argument("--validation", action="store_true", help="allow the fresh validation seed 4007")
    r.add_argument("--out", required=True)
    t = sub.add_parser("trace")
    t.add_argument("--backend", default="arm")
    t.add_argument("--suite", default="latching")
    t.add_argument("--condition", required=True)
    t.add_argument("--controller", required=True)
    t.add_argument("--index", type=int, required=True)
    t.add_argument("--seed", type=int, required=True)
    t.add_argument("--cfg", default="")
    t.add_argument("--j", default="")
    t.add_argument("--events", action="store_true")
    t.add_argument("--ticks", default="", help="write a per-tick decomposition (json.gz)")
    args = ap.parse_args()
    {"run": cmd_run, "trace": cmd_trace}[args.cmd](args)


if __name__ == "__main__":
    main()
