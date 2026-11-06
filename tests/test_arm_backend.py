"""W5: the UR5e backend runs the unchanged harness (skipped if the Menagerie model is not fetched)."""

import numpy as np
import pytest

from defex.config import ConnectorSpec
from defex.sim.arm_backend import menagerie_available
from defex.sim.backend import SceneParams
from defex.utils.transforms import Pose

pytestmark = pytest.mark.skipif(not menagerie_available(), reason="run scripts/fetch_menagerie.py")


@pytest.fixture(scope="module")
def arm_task():
    from defex.sim.arm_backend import MuJoCoArmBackend
    from defex.tasks.insertion import InsertionTask

    be = MuJoCoArmBackend()
    spec = ConnectorSpec.load("rect_12x8")
    be.load(SceneParams(spec, spec.friction, Pose.identity()))
    return InsertionTask(backend=be)


def test_arm_workcell_keeps_the_gantry_contact_model(arm_task):
    be = arm_task.backend
    assert be.model.npair == 24  # same explicit plug/gripper-socket pairs as the gantry
    h = be.home_tcp_pose
    assert np.allclose(h.p, be._layout.home_tcp, atol=1e-6) and np.allclose(h.R, np.eye(3), atol=1e-6)
    assert abs(be.true_payload.mass_kg - 0.034) < 1e-9


@pytest.mark.slow
def test_position_program_seats_on_the_arm(arm_task):
    from defex.control.registry import make_controller
    from defex.tasks.conditions import conditions_by_name
    from defex.tasks.scenarios import sample_scenario

    sc = sample_scenario(conditions_by_name()["nominal"], 0, 2026, arm_task.backend.nominal_socket_pose)
    r = arm_task.run(make_controller("fixed"), sc)
    assert r.success, r.failure_reason


@pytest.mark.slow
def test_adaptive_seats_and_verifies_on_the_arm(arm_task):
    """W5b: before the fix, C tripped the 0.6 N m stop while sweeping yaw in this trial (development seed)."""
    from defex.control.registry import make_controller
    from defex.tasks.conditions import conditions_by_name
    from defex.tasks.scenarios import sample_scenario

    sc = sample_scenario(conditions_by_name()["nominal"], 0, 2026, arm_task.backend.nominal_socket_pose)
    r = arm_task.run(make_controller("adaptive"), sc)
    assert r.success and r.declared_success is True, r.failure_reason
    assert any(k == "wall_yaw" and "PASS" in d for _, k, d in r.events)
    assert r.peak_measured_torque_nm < 0.35
