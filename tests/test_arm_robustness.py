"""v0.2c: controller C's rules for a stiff, lagging arm under poor vision (unit level; no simulator)."""

from dataclasses import replace
from types import SimpleNamespace

import json
import numpy as np
import pytest

from defex.config import DEG, MM, AdaptiveConfig, FixtureConfig, SensorNoiseConfig
from defex.control.adaptive_fsm import RECOVER, AdaptiveInsertionController
from defex.control.base import ControllerContext
from defex.control.registry import make_controller
from defex.recovery.failure_detector import ContactDiagnosis, InsertionMonitor
from defex.sim.backend import FixtureDynamics
from defex.utils.transforms import Pose

ARM = FixtureDynamics(8.0, 400.0, 6.32, 0.006, tilt_stiffness_nm_per_rad=822.0, following_lag_s=0.2,
                      rotational_following_lag_s=0.2)


def _arm_c(spec, **overrides) -> AdaptiveInsertionController:
    c = AdaptiveInsertionController(replace(AdaptiveConfig(), **overrides))
    c.reset(ControllerContext(spec, Pose.identity(), Pose.identity(), 0.002, FixtureConfig(), SensorNoiseConfig(),
                              fixture_dynamics=ARM))
    return c


def _obs(t=0.0, lag_rv=(0.0, 0.0, 0.0)):
    from defex.utils.transforms import rotvec_to_matrix

    return SimpleNamespace(t=t, fixture_tcp=Pose(np.zeros(3), rotvec_to_matrix(np.array(lag_rv))),
                           setpoint=Pose(np.zeros(3), np.eye(3)), lateral=np.zeros(2), depth=0.0,
                           force=np.zeros(3), torque=np.zeros(3))


def test_monitor_timeout_override():
    cfg = AdaptiveConfig()
    m = InsertionMonitor(cfg, timeout_s=10.0)
    m.reset(0.0)
    zero = np.zeros(3)
    assert m.update_values(9.0, 0.001 * 9.0, zero, zero, cfg.insert_force_n) is None
    assert m.update_values(10.01, 0.0101, zero, zero, cfg.insert_force_n) == "insert_timeout"
    assert InsertionMonitor(cfg).timeout_s == cfg.insert_timeout_s


def test_cavity_tilt_turns_towards_wall_torque_beyond_the_deadband(spec):
    c = _arm_c(spec)
    cfg = c.cfg
    c.S = Pose.identity()
    f_ax = 6.0
    dead = cfg.cavity_tilt_lever_mm * MM * f_ax
    c._cavity_tilt_step(np.array([-3.0 * dead, 0.5 * dead, 0.0]), f_ax, 0.002)
    step = cfg.rate_seat_conform_speed_deg_s * DEG * 0.002
    np.testing.assert_allclose(c.adm_rot.x, [-step, 0.0, 0.0])
    for _ in range(100000):  # bounded by the admittance limit
        c._cavity_tilt_step(np.array([1.0, 1.0, 0.0]), f_ax, 0.002)
    assert np.linalg.norm(c.adm_rot.x) == pytest.approx(c.adm_rot.limit)


def test_seat_conform_in_cavity_follows_walls_and_skips_noise_axes(spec):
    c = _arm_c(spec)
    c.S = Pose.identity()
    cfg = c.cfg
    f_ax = 6.0
    wall = cfg.rate_conform_wall_factor * f_ax * float(np.hypot(*c.plug_half))
    F = np.array([0.0, 0.0, f_ax])
    T = np.array([2.0 * wall, 0.2 * cfg.cavity_tilt_lever_mm * MM * f_ax, 0.0])  # x: walls push; y: noise
    rate = cfg.rate_seat_conform_speed_deg_s * DEG
    c._rc_dir = None
    c._rate_conform_step(_obs(), F, T, 0.002, rate, in_cavity=True)
    assert c.adm_conf.x[0] == pytest.approx(rate * 0.002) and c.adm_conf.x[1] == 0.0
    assert not c._rc_done[0] and c._rc_done[1]
    # The pre-v0.2c rule (in_cavity False) stops x at once (a "wall") and turns y on the noise sign.
    c.adm_conf.reset()
    c._rc_dir = None
    c._rate_conform_step(_obs(), F, T, 0.002, rate, in_cavity=False)
    assert c._rc_done[0] and c.adm_conf.x[0] == 0.0 and c.adm_conf.x[1] == pytest.approx(rate * 0.002)


def test_wall_yaw_reprobes_once_on_inconsistent_levers(spec):
    c = _arm_c(spec)
    c.S, c.G = Pose.identity(), Pose.identity()
    c.phase = "center"
    r = 2.0
    # Free travel well short of the 2 deg bound, levers +5 / -6.6 mm: not a rigid yawed plug.
    c._wall_contacts = [(0.05 * MM, r, -5.0 * MM * r), (0.25 * MM, r, 6.6 * MM * r)]
    c._wall_yaw_verdict(_obs())
    assert c.phase == "probe_out" and c._wall_reprobes_left == 0 and c._verify_results == []
    assert any("probe again" in e.detail for e in c.events)
    # The same pattern again fails the check.
    c._wall_contacts = [(0.05 * MM, r, -5.0 * MM * r), (0.25 * MM, r, 6.6 * MM * r)]
    c._wall_yaw_verdict(_obs())
    assert c.state == RECOVER and c.diagnosis.kind == "verify_failed"


def test_verify_fail_reaims_with_what_the_attempt_learned(spec):
    c = _arm_c(spec)
    c.S, c.G = Pose.identity(), Pose.identity()
    c.attempts = 1
    c.adm_rot.x = np.array([1.0, -0.5, 0.2]) * DEG
    c.adm_conf.x = np.array([0.5, 0.0, 0.0]) * DEG
    c.adm_lat.x = np.array([0.1, -0.2]) * MM
    c.diagnosis = ContactDiagnosis("verify_failed", 0.0, 0.0, np.zeros(2), np.zeros(3), None, np.zeros(2), "verify")
    c._plan_correction(_obs())
    from defex.utils.transforms import matrix_to_rotvec

    np.testing.assert_allclose(matrix_to_rotvec(c.R_corr) / DEG, [1.5, -0.5, 0.2], atol=1e-9)
    np.testing.assert_allclose(c.xy / MM, [0.1, -0.2], atol=1e-12)
    assert any("re-aim" in e.detail for e in c.events if e.kind == "recover")
    old = _arm_c(spec, reaim_after_verify_fail=False)
    old.S, old.G, old.attempts = Pose.identity(), Pose.identity(), 1
    old.adm_rot.x = np.array([1.0, -0.5, 0.2]) * DEG
    old.diagnosis = c.diagnosis
    old._plan_correction(_obs())
    np.testing.assert_allclose(old.R_corr, np.eye(3))
    assert [e.detail for e in old.events if e.kind == "recover"] == ["retry at same probe"]


def test_registry_variants(tmp_path, monkeypatch):
    path = tmp_path / "v.json"
    path.write_text(json.dumps({"no_tilt": {"cavity_tilt_compliance": False}}))
    monkeypatch.setenv("DEFEX_CONTROLLER_VARIANTS", str(path))
    c = make_controller("adaptive@no_tilt")
    assert c.name == "adaptive@no_tilt" and c.cfg.cavity_tilt_compliance is False
    assert make_controller("adaptive").cfg == AdaptiveConfig()
    monkeypatch.delenv("DEFEX_CONTROLLER_VARIANTS")
    with pytest.raises(ValueError):
        make_controller("adaptive@no_tilt")


def test_rate_conform_at_the_limit_waits_for_the_plug(spec):
    """v0.2c: at the tilt limit the axis stays open while the plug still trails the setpoint (servo lag)."""
    c = _arm_c(spec)
    c.S = Pose.identity()
    cfg = c.cfg
    f_ax = 8.0
    F = np.array([0.0, 0.0, f_ax])
    T = np.array([-0.03, 0.0, 0.0])  # pivoting: torque well above the noise lever, never reversed yet
    rate = cfg.rate_conform_speed_deg_s * DEG
    c._rc_dir = None
    c._rate_conform_step(_obs(), F, T, 0.002, rate)
    c.adm_conf.x[0] = -cfg.conform_limit_deg * DEG
    lagging = _obs(lag_rv=(0.7 * DEG, 0.0, 0.0))
    c._rate_conform_step(lagging, F, T, 0.002, rate)
    assert not c._rc_done[0]
    c._rate_conform_step(_obs(), F, T, 0.002, rate)  # caught up, still no reversal: tipped
    assert c._rc_done[0] and not c._rc_flat[0]
    old = _arm_c(spec, conform_limit_waits_for_plug=False)
    old.S = Pose.identity()
    old._rc_dir = None
    old._rate_conform_step(_obs(), F, T, 0.002, rate)
    old.adm_conf.x[0] = -cfg.conform_limit_deg * DEG
    old._rate_conform_step(lagging, F, T, 0.002, rate)
    assert old._rc_done[0]
