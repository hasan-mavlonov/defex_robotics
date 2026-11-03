"""v0.2f measurement scripts: the hook probe reads the model's hook force, and the tick replay is exact."""

import numpy as np
import pytest

from defex.config import MM, ConnectorSpec
from defex.sim.mating import MatingForce

SPEC = ConnectorSpec.load("microfit3_4ckt")


def _latched(mf):
    for d in np.linspace(0.0, SPEC.depth, 400):
        mf.axial_force(d, 1e-3, np.zeros(2))
    assert mf.state.latched


def test_hook_probe_reports_the_hook_force_and_leaves_the_model_unchanged():
    from experiments.v02f_pull_overshoot import _install_hook_probe

    ref = MatingForce(SPEC)
    _latched(ref)
    depths = np.linspace(SPEC.depth, SPEC.depth - 1.0 * MM, 2000)
    f_ref = [ref.axial_force(d, -1e-3, np.zeros(2)) for d in depths]
    probe = _install_hook_probe(0.0, None)
    try:
        mf = MatingForce(SPEC)
        _latched(mf)
        probe["trial_max"] = 0.0
        f = [mf.axial_force(d, -1e-3, np.zeros(2)) for d in depths]
        assert f == f_ref  # no damping, no stiffness change: the model's forces exactly
        assert mf.state.broken
        # The hook breaks above the rated retention; the probe saw the force that broke it.
        assert probe["trial_max"] > SPEC.mating.latch_retention_force_n
        assert probe["trial_max"] < SPEC.mating.latch_retention_force_n * 1.01
    finally:
        probe["restore"]()
    assert MatingForce.axial_force.__qualname__ == "MatingForce.axial_force"


def test_hook_probe_counterfactual_damping_only_while_engaged():
    from experiments.v02f_pull_overshoot import _install_hook_probe

    probe = _install_hook_probe(500.0, None)
    try:
        mf = MatingForce(SPEC)
        free = mf.axial_force(0.5 * SPEC.depth, -0.01, np.zeros(2))  # not latched: no hook term
        _latched(mf)
        d = mf.snap - 0.2 * MM  # 0.1 mm past the free play
        a = mf.axial_force(d, 0.0, np.zeros(2))
        b = mf.axial_force(d, -0.01, np.zeros(2))  # moving out at 10 mm/s
        assert a - b == pytest.approx(500.0 * 0.01)
    finally:
        probe["restore"]()
    assert free == MatingForce(SPEC).axial_force(0.5 * SPEC.depth, -0.01, np.zeros(2))


def test_tick_replay_reproduces_the_trial_commands():
    import os

    os.environ["DEFEX_BACKEND"] = "gantry"
    from defex.control.registry import make_controller
    from defex.tasks.conditions import standard_conditions
    from defex.tasks.insertion import InsertionTask
    from defex.tasks.scenarios import sample_scenario
    from experiments.runner import nominal_socket_pose
    from experiments.v02f_tick_timing import STATE, instrument_controller, replay

    cond = {c.name: c for c in standard_conditions()}["lateral_3mm"]
    task = InsertionTask()
    scenario = sample_scenario(cond, 0, 2026, nominal_socket_pose(cond, task.fixture))
    ctrl = make_controller("adaptive")
    instrument_controller(ctrl)
    STATE["ticks"], STATE["obs"], STATE["cmds"] = [], [], []
    res = task.run(ctrl, scenario)
    assert len(STATE["obs"]) == len(STATE["ticks"]) > 100
    best = replay("adaptive", STATE["ctx"], STATE["obs"], STATE["cmds"], 1)  # raises on any differing command
    assert best.shape == (len(STATE["obs"]),) and np.all(best > 0)
    assert res.controller == "adaptive"
    STATE["ticks"] = STATE["obs"] = STATE["cmds"] = None
