"""Closed-loop behaviour of the three controllers on representative scenarios."""

import pytest

from defex.control.registry import make_controller
from defex.tasks.conditions import conditions_by_name
from defex.tasks.scenarios import sample_scenario

pytestmark = pytest.mark.slow


def _run(task, ctrl, cond, idx=0):
    sc = sample_scenario(conditions_by_name()[cond], idx, 2026, task.backend.nominal_socket_pose)
    return task.run(make_controller(ctrl), sc)


def test_all_controllers_insert_nominal(task):
    for ctrl in ("fixed", "correction", "adaptive"):
        r = _run(task, ctrl, "nominal")
        assert r.success, (ctrl, r.failure_reason)
        assert r.max_penetration_mm < 0.05


def test_fixed_trajectory_fails_beyond_the_lead_in(task):
    r = _run(task, "fixed", "lateral_3mm")
    assert not r.success and r.failure_reason == "protective_stop"


def test_vision_correction_handles_large_but_well_measured_errors(task):
    assert _run(task, "correction", "lateral_5mm").success
    assert _run(task, "correction", "tilt_10deg").success


def test_adaptive_declares_and_verifies(task):
    r = _run(task, "adaptive", "yaw_10deg")
    assert r.success and r.declared_success is True
    kinds = [k for _, k, _ in r.events]
    assert "verify" in kinds


def test_adaptive_recovers_from_observed_failure(task):
    # A trial where the first attempt is blocked on the top face (vision error 2 mm sigma).
    r = _run(task, "adaptive", "noise_2mm", idx=3)
    assert r.success, r.failure_reason
    assert r.retries >= 1
    kinds = [k for _, k, _ in r.events]
    assert "detect" in kinds and "recover" in kinds


def test_trials_are_deterministic(task):
    a = _run(task, "adaptive", "generalization_combined", idx=2)
    b = _run(task, "adaptive", "generalization_combined", idx=2)
    assert a.success == b.success and a.retries == b.retries
    assert a.cycle_time_s == b.cycle_time_s
    assert a.peak_contact_force_n == b.peak_contact_force_n
