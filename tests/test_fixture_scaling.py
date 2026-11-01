"""W5b: fixture-dynamics rules are exact no-ops on the gantry and active on the UR5e arm."""

import numpy as np
import pytest

from defex.config import DEG, MM, FixtureConfig, SensorNoiseConfig
from defex.control.adaptive_fsm import AdaptiveInsertionController
from defex.control.base import (
    REFERENCE_FOLLOWING_LAG_S,
    REFERENCE_ROTATIONAL_STIFFNESS_NM_PER_RAD,
    ControllerContext,
    excess_following_lag,
    max_rotation_speed,
    rotational_damping_scale,
)
from defex.sim.arm_backend import menagerie_available
from defex.sim.backend import FixtureDynamics
from defex.utils.transforms import Pose


def _ctx(spec, fd: FixtureDynamics | None) -> ControllerContext:
    return ControllerContext(spec, Pose.identity(), Pose.identity(), 0.002, FixtureConfig(), SensorNoiseConfig(),
                             fixture_dynamics=fd)


def _arm_dynamics() -> FixtureDynamics:
    # The UR5e values the arm backend reports (results/w5b_development/REPORT.md).
    return FixtureDynamics(8.0, 400.0, 6.32, 0.006, tilt_stiffness_nm_per_rad=822.0, following_lag_s=0.2)


def test_gantry_backend_reports_reference_dynamics(backend):
    fd = backend.fixture_dynamics
    assert fd.tilt_stiffness_nm_per_rad == REFERENCE_ROTATIONAL_STIFFNESS_NM_PER_RAD == fd.yaw_stiffness_nm_per_rad
    assert 0.0 < fd.following_lag_s <= REFERENCE_FOLLOWING_LAG_S  # critically damped servos, slowest axis x


def test_rules_are_exact_no_ops_on_the_gantry(backend, spec):
    ctx = _ctx(spec, backend.fixture_dynamics)
    assert rotational_damping_scale(ctx) == (1.0, 1.0)
    assert excess_following_lag(ctx) == 0.0
    # The W5 formula, unchanged: budget / (stiffness x (latency + filter + period)).
    reaction = 1.0 / (2.0 * np.pi * ctx.vision_accuracy.ft_filter_cutoff_hz) + 0.002
    assert max_rotation_speed(ctx, 0.28) == pytest.approx(0.28 / (15.0 * reaction), rel=1e-12)
    c = AdaptiveInsertionController()
    d0 = (c.adm_rot.d, c.adm_conf.d)
    c.reset(ctx)
    assert (c.adm_rot.d, c.adm_conf.d) == d0  # the same objects: dampings untouched
    assert not c._rate_conform and c._yaw_sweep and c._probe_lead == 0.0
    assert c._yaw_probe_rate == c.cfg.yaw_probe_speed_deg_s * DEG


def test_rules_are_active_on_the_arm(spec):
    ctx = _ctx(spec, _arm_dynamics())
    s_tilt, s_yaw = rotational_damping_scale(ctx)
    assert s_tilt == pytest.approx(822.0 / 15.0) and s_yaw == pytest.approx(400.0 / 15.0)
    assert excess_following_lag(ctx) == pytest.approx(0.2 - REFERENCE_FOLLOWING_LAG_S)
    c = AdaptiveInsertionController()
    c.reset(ctx)
    cfg = c.cfg
    # Loop gains (stiffness / damping) back at their gantry values.
    np.testing.assert_allclose(822.0 / c.adm_conf.d, 15.0 / cfg.conform_damping_nm_s_per_rad)
    np.testing.assert_allclose([822.0, 822.0, 400.0] / c.adm_rot.d, 15.0 / cfg.rot_damping_nm_s_per_rad)
    assert c._rate_conform and not c._yaw_sweep
    assert c._probe_lead > 0.0
    assert c._yaw_probe_rate < cfg.yaw_sweep_min_speed_deg_s * DEG
    # Resetting on the gantry afterwards restores the original dampings exactly.
    c.reset(_ctx(spec, FixtureDynamics(10.0, 15.0, 0.88, 0.0, 15.0, 0.037)))
    assert (c.adm_rot.d, c.adm_conf.d) == (cfg.rot_damping_nm_s_per_rad, cfg.conform_damping_nm_s_per_rad)


def test_wall_free_travel_geometry(spec):
    c = AdaptiveInsertionController()
    c.reset(_ctx(spec, _arm_dynamics()))
    clearance = spec.socket.clearance_mm * MM
    assert c._wall_half_travel(0.0) == pytest.approx(clearance)
    for yaw_deg in (0.5, 1.0, 2.0, 3.0, 4.0):
        half = c._wall_half_travel(yaw_deg * DEG)
        assert half < clearance
        assert c._yaw_from_free_travel(2.0 * half) == pytest.approx(yaw_deg * DEG, abs=1e-9)
    assert c._yaw_from_free_travel(2.0 * clearance) == pytest.approx(0.0, abs=1e-12)
    assert c._yaw_from_free_travel(3.0 * clearance) == 0.0  # more travel than the drawing: no yaw


@pytest.mark.skipif(not menagerie_available(), reason="run scripts/fetch_menagerie.py")
def test_arm_backend_reports_its_stiffness_and_lag(spec):
    from defex.sim.arm_backend import MuJoCoArmBackend
    from defex.sim.backend import SceneParams

    be = MuJoCoArmBackend()
    be.load(SceneParams(spec, spec.friction, Pose.identity()))
    fd = be.fixture_dynamics
    assert fd.following_lag_s == pytest.approx(0.2)  # Menagerie kv / kp on every joint
    assert 500.0 < fd.tilt_stiffness_nm_per_rad < 1000.0
    assert rotational_damping_scale(_ctx(spec, fd))[0] > 30.0
