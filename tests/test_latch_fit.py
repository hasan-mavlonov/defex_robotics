"""v0.2f: the latch-model fitter matches mating.py and recovers known parameters (no MuJoCo)."""

import subprocess
import sys

import numpy as np
import pytest

from defex.calibration.latch_fit import (LoggedMove, Tolerance, fit_latch, identifiable, model_force,
                                         nominal_params)
from defex.config import MM, ConnectorSpec, PartVariation
from defex.sim.mating import MatingForce

SPEC = ConnectorSpec.load("microfit3_4ckt")
SEAT = SPEC.socket.depth_mm


def _truth(v: PartVariation | None) -> dict:
    p = nominal_params(SPEC)
    if v is not None:
        p["terminal_peak_n"] *= v.terminal_scale
        p["terminal_slide_n"] *= v.terminal_scale
        p["latch_peak_n"] *= v.latch_peak_scale
        p["post_snap_stroke_mm"] -= v.latch_shift_mm
    return p


def _path(pull_to_mm: float, step_mm: float = 0.002):
    push = np.arange(-0.5, SEAT + 1e-9, step_mm)
    pull = np.arange(SEAT - step_mm, pull_to_mm, -step_mm)
    return np.concatenate([push, pull]), push.size


def _mating_trace(v: PartVariation | None, pull_to_mm: float):
    d, n_push = _path(pull_to_mm)
    mf = MatingForce(SPEC, variation=v)
    f = np.array([mf.axial_force(x * MM, 0.0, np.zeros(2)) for x in d])
    return d, f, n_push


@pytest.mark.parametrize("v", [None, PartVariation(0.2, 0.5, 1.6), PartVariation(-0.2, 1.5, 0.8)])
def test_forward_model_equals_mating_py_along_a_push_and_pull(v):
    p = _truth(v)
    snap = SEAT - p["post_snap_stroke_mm"]
    d, f_ref, n_push = _mating_trace(v, pull_to_mm=snap - 0.2)
    pull = np.arange(d.size) >= n_push
    f = model_force(d, pull, SEAT, p, SEAT, latch=True, floor_k=0.0)
    np.testing.assert_allclose(f, f_ref, atol=1e-6)


def _synthetic(v, offset_mm, bias_n, seed, latch=True):
    d, f, n_push = _mating_trace(v, pull_to_mm=SEAT - 0.75) if latch else (None, None, None)
    if not latch:
        d, n_push = _path(SEAT - 1.0)
        mf = MatingForce(SPEC, defect="broken_latch", variation=v)
        f = np.array([mf.axial_force(x * MM, 0.0, np.zeros(2)) for x in d])
    floor = 2000.0 * np.maximum(d - SEAT, 0.0)
    rng = np.random.default_rng(seed)
    meas_d = d + offset_mm + rng.normal(0.0, 0.002, d.size)
    meas_f = f + floor + bias_n + rng.normal(0.0, 0.03, d.size)
    return LoggedMove(np.arange(d.size) * 0.002, meas_d, meas_f, latch=latch)


@pytest.mark.parametrize("v", [None, PartVariation(0.15, 0.7, 1.3)])
def test_fit_recovers_parameters_of_a_mating_py_curve(v, tmp_path):
    move = _synthetic(v, offset_mm=0.37, bias_n=0.25, seed=2027)
    move.write_csv(tmp_path / "push_pull.csv")
    move = LoggedMove.read_csv(tmp_path / "push_pull.csv")
    fit = fit_latch(SPEC, [move], starts=6, seed=2027)
    truth, tol = _truth(v), Tolerance()
    assert set(fit.free) == set(truth)  # a latched pull identifies every part parameter
    for name in fit.free:
        assert abs(fit.params[name] - truth[name]) <= tol.allowed(name, truth[name]), (name, fit.params[name])
    assert abs(fit.seat_mm[0] - (SEAT + 0.37)) < 0.02
    assert abs(fit.force_offset_n[0] - 0.25) < 0.1
    assert fit.median_abs_error_n < 0.05


def test_latch_disabled_push_shares_the_terminals():
    v = PartVariation(0.0, 1.0, 1.2)
    a = _synthetic(v, 0.1, 0.0, 1, latch=True)
    b = _synthetic(v, -0.2, 0.1, 2, latch=False)
    fit = fit_latch(SPEC, [a, b], starts=4, seed=2027)
    assert abs(fit.params["terminal_slide_n"] - 14.4) < 0.3
    assert abs(fit.seat_mm[1] - (SEAT - 0.2)) < 0.03


def test_identifiable_sets_follow_the_data():
    v = PartVariation()
    push_pull = _synthetic(v, 0.0, 0.0, 3)
    push = LoggedMove(push_pull.t_s[:4300], push_pull.depth_mm[:4300], push_pull.fz_n[:4300])
    assert not push.has_pull and push_pull.has_pull
    only_push = identifiable([push])
    assert "snap_drop" not in only_push and "latch_play_mm" not in only_push
    assert "snap_drop" in identifiable([push, _synthetic(v, 0.0, 0.0, 4, latch=False)])
    assert "latch_stiffness_n_per_mm" in identifiable([push_pull])
    assert identifiable([_synthetic(v, 0.0, 0.0, 5, latch=False)]) == (
        "terminal_wipe_mm", "terminal_lead_mm", "terminal_peak_n", "terminal_slide_n")


def test_pull_ends_at_the_first_rebound():
    d = np.concatenate([np.linspace(0, 8, 400), np.linspace(8, 7.4, 300), 7.4 + 0.05 * np.sin(np.linspace(0, 6, 60))])
    m = LoggedMove(np.arange(d.size) * 0.002, d, np.zeros(d.size))
    j = m.pull_end()
    assert 695 <= j <= 702, j


def test_latch_fit_does_not_import_mujoco():
    code = "import sys, defex.calibration.latch_fit; assert 'mujoco' not in sys.modules"
    subprocess.run([sys.executable, "-c", code], check=True)


@pytest.mark.slow
def test_fit_recovers_the_nominal_part_from_a_mujoco_push_and_pull():
    from experiments.latch_fit_sim import PushPull, simulate_logged_move

    move, extras = simulate_logged_move(SPEC, PushPull(), depth_offset_mm=0.2, seed=2027)
    assert extras["latched"] and not extras["broken"]
    fit = fit_latch(SPEC, [move], starts=8, seed=2027)
    truth, tol = _truth(None), Tolerance(floors={"mm": 0.03, "n": 0.5, "snap_drop": 0.15})
    for name in fit.free:
        assert abs(fit.params[name] - truth[name]) <= tol.allowed(name, truth[name]), (name, fit.params[name])
    assert abs(fit.seat_mm[0] - (SEAT + 0.2)) < 0.03
