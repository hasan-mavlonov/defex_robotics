"""v0.2e: H and I's pull retry, rule version 5 (results/v0.2e_pull_retry).

(a) the second pull starts only from a re-push held at the target inside INSERT's seat window,
(b) INSERT's lateral compliance runs through the pull, re-push and re-seat,
(c) the pull retry counts in ``retries``.
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from defex.config import MM, ConnectorSpec, FixtureConfig, SensorNoiseConfig
from defex.control.base import ControllerContext
from defex.control.registry import make_controller
from defex.perception.state_estimator import Observation
from defex.utils.transforms import Pose

FACE_MM = 0.2


def _ctrl(name: str = "spiral_pull", **overrides):
    spec = ConnectorSpec.load("microfit3_4ckt")
    ctx = ControllerContext(spec, Pose.identity(), Pose.identity(), 0.002, FixtureConfig(), SensorNoiseConfig())
    c = make_controller(name)
    c.reset(ctx)
    if overrides:
        c.cfg = replace(c.cfg, **overrides)
    c.S = c.G = ctx.home_pose
    c.t_start = 0.0
    c.face_depth = FACE_MM * MM
    return c


def _obs(t: float, depth_mm: float, f_ax: float, f_lat=(0.0, 0.0)) -> Observation:
    p = Pose(np.array([0.0, 0.0, -depth_mm * MM]), np.eye(3))
    z3 = np.zeros(3)
    return Observation(t, p, p, p, Pose.identity(), Pose.identity(), p, depth_mm * MM, np.zeros(2),
                       np.array([f_lat[0], f_lat[1], f_ax]), z3, z3, z3, True)


def _at_failed_pull(c, depth_mm: float = 7.9):
    """Seated by INSERT at depth_mm, then a pull that slides out past the limit."""
    c._succeed(_obs(0.0, depth_mm, c.cfg.insert_force_n))
    assert c.state == "VERIFY" and c._pull_phase == "pull"
    c._pull_step(_obs(0.002, depth_mm - c._pull_limit / MM - 0.1, -5.0))
    return c


def _repush(c, depth_mm: float, f_ax: float, seconds: float, t0: float = 0.002):
    t = t0
    while t < t0 + seconds and c.state == "VERIFY" and c._pull_phase == "repush":
        t += c.ctx.control_period_s
        c._pull_step(_obs(t, depth_mm, f_ax))
    return c


@pytest.mark.parametrize("name", ["spiral_pull", "spiral_rcc_pull"])
def test_v5_switches_are_on_for_h_and_i_only(name):
    base = {"spiral_pull": "spiral", "spiral_rcc_pull": "spiral_rcc"}[name]
    for attr in ("cfg", "stiff_fixture_cfg"):
        cp, cb = getattr(make_controller(name), attr), getattr(make_controller(base), attr)
        assert cp.repush_seat_gate and cp.verify_lateral_compliance
        assert not cb.repush_seat_gate and not cb.verify_lateral_compliance


def test_failed_pull_counts_as_a_retry():
    c = _at_failed_pull(_ctrl())
    assert c._pull_phase == "repush" and c.retries == 1
    assert ("retry", "pull failed: push again at 35.2 N and pull once more") in [(e.kind, e.detail) for e in c.events]


def test_no_retry_left_rejects_without_counting():
    c = _ctrl()
    c._pull_retries_left = 0
    _at_failed_pull(c)
    assert c.state == "FAILURE" and c._fail_reason == "retention_failed" and c.retries == 0


@pytest.mark.parametrize("depth_mm,pulls_again", [(7.9, True), (6.5, False)])
def test_second_pull_only_from_the_seat_window(depth_mm, pulls_again):
    """Held at the target: pull again only at INSERT's seat depth (H gantry: 8 - 0.5 mm below the face)."""
    c = _ctrl()
    gain_needed = c.depth - c.cfg.seat_margin_mm * MM
    assert (depth_mm * MM - c.face_depth >= gain_needed) is pulls_again
    _repush(_at_failed_pull(c), depth_mm, c.cfg.insert_force_n, 1.0)
    if pulls_again:
        assert c.state == "VERIFY" and c._pull_phase == "pull" and c._pull_start == pytest.approx(depth_mm * MM)
    else:
        assert c.state == "FAILURE" and c._fail_reason == "repush_short_of_seat"
        assert any(e.kind == "verify" and "short of the seat depth" in e.detail for e in c.events)


def test_re_push_that_never_holds_is_rejected():
    c = _ctrl()
    _repush(_at_failed_pull(c), 7.9, 0.5 * c.cfg.insert_force_n, 2.5 * c.cfg.pull_test_max_s)
    assert c.state == "FAILURE" and c._fail_reason == "repush_not_held"


def test_gate_off_keeps_the_v4_behaviour():
    c = _ctrl(repush_seat_gate=False)
    _repush(_at_failed_pull(c), 6.5, c.cfg.insert_force_n, 1.0)
    assert c.state == "VERIFY" and c._pull_phase == "pull"


@pytest.mark.parametrize("phase", ["pull", "repush", "reseat"])
@pytest.mark.parametrize("on", [True, False])
def test_lateral_compliance_through_the_latch_check(phase, on):
    """INSERT's zero-stiffness admittance gives way to side load in every VERIFY phase (v4: frozen)."""
    c = _ctrl(verify_lateral_compliance=on)
    c._succeed(_obs(0.0, 7.9, c.cfg.insert_force_n))
    c._pull_phase = phase
    c._repush_t_force, c._repush_peak, c._repush_depth0 = None, 0.0, 0.0
    x0 = c.adm.x.copy()
    f_ax = {"pull": -5.0, "repush": 20.0, "reseat": 0.0}[phase]
    for k in range(20):
        c._pull_step(_obs(0.002 * (k + 1), 7.9, f_ax, f_lat=(4.0, 0.0)))
    assert c.state == "VERIFY"
    moved = c.adm.x - x0
    if on:
        assert moved[0] > 0.0 and abs(moved[1]) < 1e-12
    else:
        assert np.allclose(moved, 0.0)


def test_insert_seat_rule_unchanged_by_the_helper():
    """The seat window helper is INSERT's arithmetic: face known, and went straight in (vision window)."""
    c = _ctrl()
    gain, need = c._seat_window(_obs(0.0, 7.9, 0.0))
    assert gain == pytest.approx(7.9 * MM - c.face_depth) and need == pytest.approx(c.depth - c.cfg.seat_margin_mm * MM)
    c.face_depth = None
    gain, need = c._seat_window(_obs(0.0, 7.9, 0.0))
    assert gain == pytest.approx(7.9 * MM)
    assert need == pytest.approx(c.depth - c.cfg.seat_margin_mm * MM - 3.0 * c.sigma_z)


@pytest.mark.slow
def test_arm_h_re_push_no_longer_trips_the_lateral_limit():
    """Dev seed 2026, arm, broken latch at terminal max, trial 3: v4 aborted on excess_lateral_force 2 ms into the
    re-push (side load left by the pull); v5 re-pushes, pulls again and rejects on the pull."""
    from defex.sim.arm_backend import MuJoCoArmBackend, menagerie_available
    from defex.tasks.conditions import latch_spread_conditions
    from defex.tasks.insertion import InsertionTask
    from defex.tasks.scenarios import sample_scenario
    from experiments.runner import nominal_socket_pose

    if not menagerie_available():
        pytest.skip("MuJoCo Menagerie UR5e not fetched")
    task = InsertionTask(backend=MuJoCoArmBackend())
    cond = {c.name: c for c in latch_spread_conditions()}["mf_terminal_max_broken_latch"]
    sc = sample_scenario(cond, 3, 2026, nominal_socket_pose(cond, task.fixture))
    res = task.run(make_controller("spiral_pull"), sc)
    assert res.failure_reason == "aborted:retention_failed" and not res.protective_stop
    assert res.retries == 1
