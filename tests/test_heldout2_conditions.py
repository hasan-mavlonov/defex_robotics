"""v0.2f held-out families (heldout2): unseen socket rotation, unseen in-hand error, F/T drift, part tolerance."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import replace

import numpy as np
import pytest

from defex.config import DEG, MM, REPO_ROOT, SensorNoiseConfig
from defex.perception.sensors import SensorSuite
from defex.sim.backend import RawSensorData
from defex.tasks.conditions import (
    HELDOUT2_FAMILIES,
    heldout2_conditions,
    heldout2_conditions_by_name,
    heldout_conditions,
    latch_spread_conditions,
    latching_conditions,
    standard_conditions,
)
from defex.tasks.scenarios import sample_scenario
from defex.utils.transforms import Pose, axis_angle_between, twist_about_axis

NOMINAL = Pose(np.array([0.0, 0.0, 0.03]), np.eye(3))
EARLIER = standard_conditions() + heldout_conditions() + latching_conditions() + latch_spread_conditions()


def h2(name: str):
    return heldout2_conditions_by_name()[name]


def test_five_families_two_levels_each_and_new_names():
    conds = heldout2_conditions()
    assert len(conds) == 10
    for fam in HELDOUT2_FAMILIES:
        assert sum(c.group == fam for c in conds) == 2
    assert not {c.name for c in conds} & {c.name for c in EARLIER}
    for c in conds:
        assert c.connector in ("rect_12x8", "microfit3_4ckt")
        assert c.defect is None and c.part_spread is None


def test_earlier_conditions_get_no_heldout2_fields_or_draws():
    for c in EARLIER:
        sc = sample_scenario(c, 3, 2026, NOMINAL)
        assert sc.vision_target_pose is None and sc.measured_grasp_offset is None
        assert sc.characterized_connector is None
        assert not any(k.startswith(("unseen_", "grasp_unseen_", "actual_")) for k in sc.disturbance)
        assert sc.noise.ft_drift_force_n_per_s == 0.0 and sc.noise.ft_drift_torque_nm_per_s == 0.0


def test_heldout2_draws_leave_the_moderate_draws_unchanged():
    """The unseen errors are drawn after every other value: the seen socket pose and grasp equal the
    draw of the same condition without them."""
    for name in ("h2_tilt_unseen_3deg", "h2_yaw_unseen_4deg", "h2_mf_grasp_unseen_2deg", "h2_mf_tol_0.05mm"):
        c = h2(name)
        plain = replace(c, disturbance=replace(c.disturbance, unseen_tilt_deg=0.0, unseen_yaw_deg=0.0,
                                               grasp_unseen_lateral_mm=0.0, grasp_unseen_tilt_deg=0.0),
                        actual_clearance_mm=None, actual_chamfer_mm=None)
        for i in range(5):
            a, b = sample_scenario(c, i, 2026, NOMINAL), sample_scenario(plain, i, 2026, NOMINAL)
            seen = a.socket_pose if a.vision_target_pose is None else a.vision_target_pose
            assert np.array_equal(seen.p, b.socket_pose.p) and np.array_equal(seen.R, b.socket_pose.R)
            g = a.grasp_offset if a.measured_grasp_offset is None else a.measured_grasp_offset
            assert np.array_equal(g.p, b.grasp_offset.p) and np.array_equal(g.R, b.grasp_offset.R)


@pytest.mark.parametrize("deg", [2.0, 3.0])
def test_unseen_tilt_rotates_the_true_socket_away_from_what_the_camera_sees(deg):
    for i in range(10):
        sc = sample_scenario(h2(f"h2_tilt_unseen_{deg:g}deg"), i, 2026, NOMINAL)
        rel = sc.vision_target_pose.R.T @ sc.socket_pose.R
        assert axis_angle_between(rel[:, 2], np.array([0.0, 0.0, 1.0])) == pytest.approx(deg * DEG, abs=1e-9)
        assert twist_about_axis(rel) == pytest.approx(0.0, abs=1e-9)
        assert np.array_equal(sc.socket_pose.p, sc.vision_target_pose.p)
        assert sc.disturbance["unseen_tilt_deg"] == deg


def test_unseen_yaw_has_fixed_magnitude_and_both_signs():
    signs = set()
    for i in range(20):
        sc = sample_scenario(h2("h2_yaw_unseen_4deg"), i, 2026, NOMINAL)
        rel = sc.vision_target_pose.R.T @ sc.socket_pose.R
        assert abs(twist_about_axis(rel)) == pytest.approx(4.0 * DEG, abs=1e-9)
        assert axis_angle_between(rel[:, 2], np.array([0.0, 0.0, 1.0])) == pytest.approx(0.0, abs=1e-9)
        signs.add(np.sign(sc.disturbance["unseen_yaw_deg"]))
    assert signs == {-1.0, 1.0}


def test_unseen_grasp_error_is_along_the_grasps_free_directions():
    for i in range(10):
        sc = sample_scenario(h2("h2_mf_grasp_unseen_2deg"), i, 2026, NOMINAL)
        m, t = sc.measured_grasp_offset, sc.grasp_offset
        assert m.p == pytest.approx(np.zeros(3)) and np.allclose(m.R, np.eye(3))  # MODERATE: nominal grasp
        assert abs(sc.disturbance["grasp_unseen_lateral_mm"]) == 0.4
        assert abs(sc.disturbance["grasp_unseen_tilt_deg"]) == 2.0
        rv_angle = np.arccos(np.clip(t.R[1, 1], -1.0, 1.0))  # rotation about x only
        assert rv_angle == pytest.approx(2.0 * DEG, abs=1e-9) and t.R[0, 0] == pytest.approx(1.0)
        assert t.p[0] == pytest.approx(0.0, abs=1e-12)
        # Rotation about the grip centre (12 mm above the tip) plus the 0.4 mm slip.
        th, lat = sc.disturbance["grasp_unseen_tilt_deg"] * DEG, sc.disturbance["grasp_unseen_lateral_mm"] * MM
        gc = 12.0 * MM
        assert t.p[1] == pytest.approx(lat * np.cos(th) + gc * np.sin(th), abs=1e-12)


def test_part_tolerance_simulates_the_tight_part_and_tells_the_drawing():
    sc = sample_scenario(h2("h2_mf_tol_0.05mm"), 0, 2026, NOMINAL)
    assert sc.connector.socket.clearance_mm == 0.05 and sc.connector.socket.chamfer_mm == 0.2
    told = sc.characterized_connector
    assert told.socket.clearance_mm == 0.15 and told.socket.chamfer_mm == 0.4
    assert told.plug == sc.connector.plug and told.mating == sc.connector.mating


def _raw(t: float) -> RawSensorData:
    return RawSensorData(t, np.zeros(6), Pose.identity(), np.zeros(3), np.zeros(3))


def test_ft_drift_is_linear_after_the_first_reading_and_leaves_other_streams_unchanged():
    on = replace(SensorNoiseConfig(), ft_drift_force_n_per_s=0.3, ft_drift_torque_nm_per_s=0.003)
    for seed in range(5):
        a, b = SensorSuite(on, seed), SensorSuite(SensorNoiseConfig(), seed)
        assert np.linalg.norm(a.ft_force_drift) == pytest.approx(0.3)
        assert np.linalg.norm(a.ft_torque_drift) == pytest.approx(0.003)
        assert np.array_equal(a.ft_force_bias, b.ft_force_bias)
        assert np.array_equal(a.vision_measurement(NOMINAL).p, b.vision_measurement(NOMINAL).p)
        for t in (0.5, 1.0, 5.0, 10.0):
            ra, rb = a.measure(_raw(t)), b.measure(_raw(t))
            assert ra.ft_force - rb.ft_force == pytest.approx(a.ft_force_drift * (t - 0.5), abs=1e-12)
            assert ra.ft_torque - rb.ft_torque == pytest.approx(a.ft_torque_drift * (t - 0.5), abs=1e-12)
            assert np.array_equal(ra.tcp_pose.p, rb.tcp_pose.p)


def test_controllers_are_told_nominal_accuracy_and_the_drawing(task):
    from defex.control.registry import make_controller

    for name in ("h2_ft_drift_0.3", "h2_mf_tol_0.05mm", "h2_tilt_unseen_3deg"):
        sc = sample_scenario(h2(name), 0, 2026, task.backend.nominal_socket_pose)
        ctrl = make_controller("fixed")
        task.run(ctrl, sc)
        va = ctrl.ctx.vision_accuracy
        assert va == SensorNoiseConfig()
        assert ctrl.ctx.connector.socket.clearance_mm == (0.15 if "mf_" in name else 0.5)


def test_suite_needs_an_explicit_seed():
    r = subprocess.run([sys.executable, "-m", "experiments.robustness", "--suite", "heldout2", "--trials", "1"],
                       cwd=REPO_ROOT, capture_output=True, text=True)
    assert r.returncode != 0 and "explicit --seed" in r.stderr
