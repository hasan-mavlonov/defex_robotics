"""Conventional baselines D (spiral search), E (vision + RCC) and F (spiral + RCC)."""

import pytest

from defex.config import MM, CompliantStageConfig
from defex.control.registry import CONTROLLERS, make_controller
from defex.logging.metrics import TrialResult, is_escape, mcnemar_exact, throughput_uph
from defex.sim.backend import SceneParams
from defex.sim.mujoco_backend import MuJoCoBackend
from defex.sim.scene_builder import build_workcell_xml
from defex.tasks.conditions import conditions_by_name
from defex.tasks.scenarios import sample_scenario
from defex.utils.transforms import Pose


def test_all_six_controllers_are_registered():
    assert {"fixed", "correction", "adaptive", "spiral", "correction_rcc", "spiral_rcc"} <= set(CONTROLLERS)
    assert make_controller("correction_rcc").compliant_wrist and make_controller("spiral_rcc").compliant_wrist
    assert not make_controller("spiral").compliant_wrist


def test_rigid_scene_is_unchanged_by_the_compliance_option():
    assert "rcc_x" not in build_workcell_xml()
    assert "rcc_x" in build_workcell_xml(compliance=CompliantStageConfig())


def test_rcc_stage_deflects_at_its_datasheet_stiffness(spec):
    """A static lateral push on the plug tip deflects the stage by F / k."""
    be = MuJoCoBackend()
    be.load(SceneParams(spec, spec.friction, Pose.identity(), compliance=CompliantStageConfig()))
    m, d = be.model, be.data
    jx = m.joint("rcc_x").qposadr[0]
    be.set_tcp_setpoint(be.home_tcp_pose)
    plug = m.body("connector").id
    force = 2.0  # N, well inside the 1.65 mm travel
    for _ in range(3000):
        d.xfrc_applied[plug, :3] = (force, 0.0, 0.0)
        be.step(0.0005)
    k = CompliantStageConfig().lateral_stiffness_n_per_mm / MM
    servo = 1e4  # the stiff x servo deflects too, in series
    assert d.qpos[jx] == pytest.approx(force / k, rel=0.05)
    assert d.qpos[jx] < force / k + force / servo


def test_escape_and_throughput_definitions():
    def r(success, stop=False, declared=None, cycle=5.0):
        return TrialResult("x", "c", "g", 0, 0, success, "none", success, declared, cycle, 0, 0, 0, False,
                           15, 0, 0, 0, 0, stop, False, 0.3, 0.3)

    assert not is_escape(r(True))
    assert is_escape(r(False))  # no self-check, no stop: the bad unit leaves the cell
    assert not is_escape(r(False, stop=True))
    assert not is_escape(r(False, declared=False))
    assert is_escape(r(False, declared=True))  # false accept
    rs = [r(True), r(False, stop=True)]
    assert throughput_uph(rs, 0.0) == pytest.approx(360.0)
    assert throughput_uph(rs, 60.0) == pytest.approx(3600.0 / 70.0)
    assert mcnemar_exact(1, 9) == pytest.approx(0.021484375)
    assert mcnemar_exact(4, 4) == 1.0


@pytest.mark.slow
@pytest.mark.parametrize("ctrl", ["spiral", "correction_rcc", "spiral_rcc"])
def test_conventional_baselines_insert_on_the_nominal_socket(task, ctrl):
    sc = sample_scenario(conditions_by_name()["nominal"], 0, 2026, task.backend.nominal_socket_pose)
    res = task.run(make_controller(ctrl), sc)
    assert res.success, res.failure_reason
    assert res.max_penetration_mm < 0.05


@pytest.mark.slow
def test_spiral_search_finds_a_hole_outside_the_lead_in(task):
    # Vision noise 1 mm: on development trial 1 the first touch lands on the face and the spiral finds the hole.
    found = False
    for i in range(6):
        sc = sample_scenario(conditions_by_name()["noise_1mm"], i, 2026, task.backend.nominal_socket_pose)
        res = task.run(make_controller("spiral"), sc)
        kinds = [k for _, k, _ in res.events]
        if "hole_found" in kinds and res.success:
            found = True
            break
    assert found
