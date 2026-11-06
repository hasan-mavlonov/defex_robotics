"""v0.2f latch fit: synthetic recovery, identifiability and the worked example.

Pass rule: results/v0.2f_latch_fit/RULE.md (committed before this ran).

    PYTHONPATH=. python -m experiments.latch_fit_recovery --workers 2 --out results/v0.2f_latch_fit
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import time
from dataclasses import asdict, dataclass
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from defex.calibration.latch_fit import LoggedMove, Tolerance, fit_latch, model_force, nominal_params
from defex.config import ConnectorSpec, FixtureConfig, PartVariation, SensorNoiseConfig
from experiments.latch_fit_sim import PushPull, simulate_logged_move, stress_noise

SPEC_NAME = "microfit3_4ckt"
SEED = 2026
JUDGED = ("terminal_wipe_mm", "terminal_lead_mm", "terminal_peak_n", "terminal_slide_n", "latch_onset_to_seat_mm",
          "latch_rise_mm", "latch_peak_n", "latch_fall_mm", "snap_drop", "post_snap_stroke_mm", "latch_play_mm",
          "latch_stiffness_n_per_mm", "bristle_mm", "seat_error_mm")
TOL = Tolerance(rel=0.15, floors={"mm": 0.03, "n": 0.5, "snap_drop": 0.15})
DESIGNS = {
    "main": "one push + guarded pull, 1 mm/s, sensor-model noise (JUDGED)",
    "noise10": "as main, F/T white noise x10 (0.3 N)",
    "push_only": "one push, no pull, 1 mm/s",
    "speed_0.5": "as main at 0.5 mm/s",
    "speed_2": "as main at 2 mm/s",
    "speed_5": "as main at 5 mm/s",
    "stiff_rig": "as main, gantry servo 200 N/mm instead of 10 N/mm",
    "plus_disabled": "main plus one latch-disabled push + pull of the same part",
}


@dataclass(frozen=True)
class PartSet:
    name: str
    variation: PartVariation
    depth_offset_mm: float
    sensor_seed: int


def part_sets(seed: int = SEED) -> list[PartSet]:
    rng = np.random.default_rng(seed)
    sets = [PartSet("nominal", PartVariation(), float(rng.uniform(-0.5, 0.5)), int(rng.integers(2**31)))]
    for i in range(10):
        v = PartVariation(float(rng.uniform(-0.2, 0.2)), float(rng.uniform(0.5, 1.5)), float(rng.uniform(0.8, 1.6)))
        sets.append(PartSet(f"off{i + 1:02d}", v, float(rng.uniform(-0.5, 0.5)), int(rng.integers(2**31))))
    return sets


def truth_params(spec: ConnectorSpec, v: PartVariation) -> dict:
    p = nominal_params(spec)
    p["terminal_peak_n"] *= v.terminal_scale
    p["terminal_slide_n"] *= v.terminal_scale
    p["latch_peak_n"] *= v.latch_peak_scale
    p["post_snap_stroke_mm"] -= v.latch_shift_mm
    return p


def with_derived(p: dict) -> dict:
    out = dict(p)
    out["latch_onset_to_seat_mm"] = p["latch_rise_mm"] + p["latch_fall_mm"] + p["post_snap_stroke_mm"]
    return out


def allowed(name: str, truth: float) -> float:
    return TOL.allowed("x_mm" if name == "seat_error_mm" else name, truth)


def run_case(args) -> list[dict]:
    design, ps = args
    spec = ConnectorSpec.load(SPEC_NAME)
    speed = {"speed_0.5": 0.5, "speed_2": 2.0, "speed_5": 5.0}.get(design, 1.0)
    noise = stress_noise(10.0) if design == "noise10" else SensorNoiseConfig()
    fixture = FixtureConfig(linear_kp_n_per_m=2e5) if design == "stiff_rig" else None
    move = PushPull(speed_mm_s=speed, pull=design != "push_only")
    t0 = time.time()
    m, ex = simulate_logged_move(spec, move, ps.variation, noise=noise, depth_offset_mm=ps.depth_offset_mm,
                                 seed=ps.sensor_seed, fixture=fixture)
    moves = [m]
    if design == "plus_disabled":
        m2, _ = simulate_logged_move(spec, move, ps.variation, defect="broken_latch", noise=noise,
                                     depth_offset_mm=ps.depth_offset_mm - 0.25, seed=ps.sensor_seed + 1)
        moves.append(m2)
    fit = fit_latch(spec, moves, seed=SEED)
    truth = with_derived(truth_params(spec, ps.variation))
    got = with_derived(fit.params)
    got["seat_error_mm"] = fit.seat_mm[0] - (spec.socket.depth_mm + ps.depth_offset_mm)
    truth["seat_error_mm"] = 0.0
    rows = []
    for name in JUDGED:
        fitted = name in fit.free or name in ("seat_error_mm", "latch_onset_to_seat_mm")
        err = got[name] - truth[name]
        tol = allowed(name, truth[name])
        rows.append({"design": design, "set": ps.name, "parameter": name, "truth": truth[name], "fit": got[name],
                     "error": err, "rel_error": err / truth[name] if truth[name] else float("nan"),
                     "tolerance": tol, "fitted": fitted, "within": bool(fitted and abs(err) <= tol),
                     "latched": ex["latched"], "median_abs_error_n": fit.median_abs_error_n,
                     "rms_error_n": fit.rms_error_n, "seconds": time.time() - t0})
    return rows


# --------------------------------------------------------------------------- identifiability
def jacobian_study(spec: ConnectorSpec) -> dict:
    """Local identifiability at the nominal part from the fitter's own model (noise-free, sigma 0.03 N per sample).

    Correlations of the parameter estimates (from the Gauss-Newton information matrix) for three
    data designs. |corr| near 1: the pair trades against each other on that data.
    """
    p = nominal_params(spec)
    seat = spec.socket.depth_mm
    step = 0.002  # 1 mm/s at a 2 ms log period
    push = np.arange(-0.5, seat + 0.03, step)
    snap = seat - p["post_snap_stroke_mm"]
    catch = snap - p["latch_play_mm"]
    pull = np.arange(seat + 0.03, catch - 0.085, -step)  # to the 29 N guard pull: 12 N slide + 17 N on the hook
    designs = {
        "push_only": [(push, np.zeros(push.size, bool), True)],
        "push_pull": [(np.concatenate([push, pull]), np.r_[np.zeros(push.size, bool), np.ones(pull.size, bool)], True)],
        "push_pull_plus_disabled": [
            (np.concatenate([push, pull]), np.r_[np.zeros(push.size, bool), np.ones(pull.size, bool)], True),
            (np.concatenate([push, np.arange(seat + 0.03, seat - 1.0, -step)]),
             np.r_[np.zeros(push.size, bool), np.ones(np.arange(seat + 0.03, seat - 1.0, -step).size, bool)], False)],
    }
    names = ["terminal_wipe_mm", "terminal_lead_mm", "terminal_peak_n", "terminal_slide_n", "latch_rise_mm",
             "latch_peak_n", "latch_fall_mm", "snap_drop", "post_snap_stroke_mm", "latch_play_mm",
             "latch_stiffness_n_per_mm", "bristle_mm"]
    out = {}
    for dname, moves in designs.items():
        use = [n for n in names if dname != "push_only" or n not in ("latch_play_mm", "latch_stiffness_n_per_mm",
                                                                       "bristle_mm")]
        cols = []
        labels = use + [f"seat_{k}" for k in range(len(moves))] + [f"offset_{k}" for k in range(len(moves))]

        def f_all(pp, seats, offs):
            return np.concatenate([model_force(d, pl, d.max(), pp, seats[k], lt, 2000.0) + offs[k]
                                   for k, (d, pl, lt) in enumerate(moves)])

        seats, offs = [seat] * len(moves), [0.0] * len(moves)
        base = f_all(p, seats, offs)
        for n in use:
            h = 1e-4 * max(abs(p[n]), 0.1)
            q = dict(p)
            q[n] = p[n] + h
            cols.append((f_all(q, seats, offs) - base) / h)
        for k in range(len(moves)):
            s2 = list(seats)
            s2[k] += 1e-4
            cols.append((f_all(p, s2, offs) - base) / 1e-4)
        for k in range(len(moves)):
            o2 = list(offs)
            o2[k] += 1e-3
            cols.append((f_all(p, seats, o2) - base) / 1e-3)
        J = np.array(cols).T
        info = J.T @ J / 0.03**2
        cov = np.linalg.pinv(info)
        sd = np.sqrt(np.clip(np.diag(cov), 0.0, None))
        corr = cov / np.outer(sd, sd)
        pairs = sorted(((abs(corr[i, j]), labels[i], labels[j], corr[i, j]) for i in range(len(labels))
                        for j in range(i + 1, len(labels))), reverse=True)
        out[dname] = {"sd": {labels[i]: float(sd[i]) for i in range(len(labels))},
                      "rank": int(np.linalg.matrix_rank(J)), "n_params": len(labels),
                      "top_correlations": [(a, b, round(float(c), 4)) for _, a, b, c in pairs[:8]]}
    return out


# --------------------------------------------------------------------------- worked example
def worked_example(spec: ConnectorSpec, out: Path) -> dict:
    from experiments.latch_fit_report import band_stats, overlay

    wdir = out / "worked"
    wdir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED + 1)
    offset = float(rng.uniform(-0.5, 0.5))
    m, _ = simulate_logged_move(spec, PushPull(speed_mm_s=1.0), None, depth_offset_mm=offset,
                                seed=int(rng.integers(2**31)))
    m.write_csv(wdir / "datasheet_curve.csv")
    # Rounded corners: the part's curve smoothed over depth (Gaussian, sigma 0.05 mm), a stand-in for a real part
    # whose curve is not piecewise linear (outside the model family). Built on a 0.01 mm grid of the true model,
    # push and pull separately, and added to the log as (smoothed - sharp), away from the floor contact.

    truth = truth_params(spec, PartVariation())
    seat_log = spec.socket.depth_mm + offset
    d = m.depth_mm
    i = m.turnaround()
    pull = np.arange(d.size) > i
    d_turn = float(np.median(d[max(0, i - 5):i + 6]))
    grid = np.arange(d.min() - 0.3, d_turn + 0.01, 0.01)
    k = np.arange(-20, 21) * 0.01
    g = np.exp(-0.5 * (k / 0.05) ** 2)
    g /= g.sum()
    sm = m.fz_n.copy()
    for seg in (~pull, pull):
        sharp = model_force(grid, np.full(grid.size, bool(seg[-1])), d_turn, truth, seat_log, True, 0.0)
        soft = np.convolve(np.pad(sharp, 20, mode="edge"), g, mode="valid")
        use = seg & (d < seat_log - 0.1)
        sm[use] += np.interp(d[use], grid, soft - sharp)
    LoggedMove(m.t_s, d, sm).write_csv(wdir / "rounded_curve.csv")
    res = {}
    for name in ("datasheet_curve", "rounded_curve"):
        logged = LoggedMove.read_csv(wdir / f"{name}.csv")
        fit = fit_latch(spec, [logged], seed=SEED)
        overlay(spec, [logged], fit, wdir / f"{name}.png", title=f"{name}: fitted model against the log")
        res[name] = {"params": with_derived(fit.params), "seat_mm": fit.seat_mm[0],
                     "force_offset_n": fit.force_offset_n[0], "median_abs_error_n": fit.median_abs_error_n,
                     "rms_error_n": fit.rms_error_n, **band_stats(logged, fit, 0)}
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", default="results/v0.2f_latch_fit")
    ap.add_argument("--designs", default=",".join(DESIGNS))
    ap.add_argument("--only-worked", action="store_true", help="recompute only the worked example in summary.json")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    spec = ConnectorSpec.load(SPEC_NAME)
    if a.only_worked:
        s = json.loads((out / "summary.json").read_text())
        s["worked_example"] = worked_example(spec, out)
        s["worked_example_git_commit"] = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                                                        text=True).stdout.strip()
        (out / "summary.json").write_text(json.dumps(s, indent=1, default=float))
        print(json.dumps({k: {a: v[a] for a in v if a != "params"} for k, v in s["worked_example"].items()}, default=float))
        return
    sets = part_sets()
    jobs = [(d, ps) for d in a.designs.split(",") for ps in sets]
    t0 = time.time()
    with Pool(a.workers) as pool:
        rows = [r for rs in pool.map(run_case, jobs) for r in rs]
    with (out / "recovery.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    verdict = {}
    for design in a.designs.split(","):
        per = {}
        for name in JUDGED:
            rs = [r for r in rows if r["design"] == design and r["parameter"] == name]
            nom = [r for r in rs if r["set"] == "nominal"][0]
            off = [r for r in rs if r["set"] != "nominal"]
            n_ok = sum(r["within"] for r in off)
            per[name] = {"nominal_within": nom["within"], "off_nominal_within": n_ok, "off_nominal_n": len(off),
                         "fitted": nom["fitted"], "pass": bool(nom["within"] and n_ok >= 8),
                         "max_abs_error": max(abs(r["error"]) for r in rs)}
        verdict[design] = {"params": per, "pass": all(v["pass"] for v in per.values())}
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain", "--untracked-files=no", "--", "defex", "experiments",
                                 "tests"],
                                capture_output=True, text=True).stdout.strip())
    summary = {"git_commit": commit, "git_dirty": dirty, "seed": SEED, "designs": DESIGNS,
               "tolerance": asdict(TOL), "sets": [{**asdict(s), "variation": asdict(s.variation)} for s in sets],
               "verdict": verdict, "seconds": time.time() - t0}
    summary["identifiability"] = jacobian_study(spec)
    summary["worked_example"] = worked_example(spec, out)
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=float))
    from experiments.latch_fit_report import recovery_plot

    recovery_plot(spec, sets[0], out / "recovery_nominal_overlay.png")
    print(json.dumps({d: v["pass"] for d, v in verdict.items()}))


if __name__ == "__main__":
    main()
