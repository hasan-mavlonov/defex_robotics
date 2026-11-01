"""W5b: fixture-dynamics rules are exact no-ops on every gantry (nominal and randomized) and active on the UR5e arm."""

import numpy as np
import pytest

from dataclasses import replace

from defex.config import DEG, MM, AdaptiveConfig, ConnectorSpec, FixtureConfig, SensorNoiseConfig
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
from defex.sim.backend import FixtureDynamics, SceneParams
from defex.sim.mujoco_backend import MuJoCoBackend
from defex.utils.transforms import Pose
from experiments.sim_randomization import BANDS

CFG = AdaptiveConfig()


def _ctx(spec, fd: FixtureDynamics | None) -> ControllerContext:
    return ControllerContext(spec, Pose.identity(), Pose.identity(), 0.002, FixtureConfig(), SensorNoiseConfig(),
                             fixture_dynamics=fd)


def _arm_dynamics() -> FixtureDynamics:
    # The UR5e values the arm backend reports (results/w5b_development/REPORT.md).
    return FixtureDynamics(8.0, 400.0, 6.32, 0.006, tilt_stiffness_nm_per_rad=822.0, following_lag_s=0.2,
                           rotational_following_lag_s=0.2)


def _assert_c_as_tuned_on_the_gantry(ctx: ControllerContext) -> None:
    """C's reset leaves every W5b quantity at its pre-W5b value (the only places W5b enters C)."""
    assert rotational_damping_scale(ctx, CFG.stiff_wrist_min_ratio) == (1.0, 1.0)
    assert excess_following_lag(ctx, CFG.lagging_servo_min_ratio) == 0.0
    assert excess_following_lag(ctx, CFG.lagging_servo_min_ratio, rotational=True) == 0.0
    # The W5 formula, unchanged: budget / (stiffness x (latency + filter + period)).
    reaction = 1.0 / (2.0 * np.pi * ctx.vision_accuracy.ft_filter_cutoff_hz) + 0.002
    k = ctx.fixture_dynamics.yaw_stiffness_nm_per_rad
    assert max_rotation_speed(ctx, 0.28, CFG.lagging_servo_min_ratio) == pytest.approx(0.28 / (k * reaction), rel=1e-12)
    c = AdaptiveInsertionController()
    d0 = (c.adm_rot.d, c.adm_conf.d)
    c.reset(ctx)
    assert (c.adm_rot.d, c.adm_conf.d) == d0  # the same objects: dampings untouched
    assert not c._rate_conform and c._yaw_sweep and c._probe_lead == 0.0
    assert c._yaw_probe_rate == c.cfg.yaw_probe_speed_deg_s * DEG
    # v0.2c rules: off, and INSERT's timeout is the configured one.
    assert not (c._cavity_tilt or c._floor_impact or c._reaim_verify)
    assert c.monitor.timeout_s == c.cfg.insert_timeout_s


def test_gantry_backend_reports_reference_dynamics(backend):
    fd = backend.fixture_dynamics
    assert fd.tilt_stiffness_nm_per_rad == REFERENCE_ROTATIONAL_STIFFNESS_NM_PER_RAD == fd.yaw_stiffness_nm_per_rad
    assert 0.0 < fd.following_lag_s <= REFERENCE_FOLLOWING_LAG_S  # critically damped servos, slowest axis x
    assert 0.0 < fd.rotational_following_lag_s < fd.following_lag_s  # wrist servos are faster than the carriage


def test_rules_are_exact_no_ops_on_the_nominal_gantry(backend, spec):
    _assert_c_as_tuned_on_the_gantry(_ctx(spec, backend.fixture_dynamics))


def test_rules_are_exact_no_ops_on_every_gantry_of_the_randomization_bands(spec):
    """Checkpoint 2 review: experiments/sim_randomization.py draws the wrist servos from 10-25 N m/rad and the
    linear servos from 5-20 kN/m; before the thresholds, any wrist above 15 N m/rad switched C to rate mode."""
    lo_k, hi_k = BANDS["angular_kp_nm_per_rad"]
    lo_l, hi_l = BANDS["linear_kp_n_per_m"]
    corners = [(l, k) for l in (lo_l, hi_l) for k in (lo_k, hi_k)] + [(9677.0, 15.01)]  # dev 2026 variant 12
    for lin_kp, ang_kp in corners:
        be = MuJoCoBackend(fixture=replace(FixtureConfig(), linear_kp_n_per_m=lin_kp, angular_kp_nm_per_rad=ang_kp))
        be.load(SceneParams(spec, spec.friction, Pose.identity()))
        fd = be.fixture_dynamics
        assert fd.yaw_stiffness_nm_per_rad == fd.tilt_stiffness_nm_per_rad == ang_kp
        assert fd.following_lag_s < CFG.lagging_servo_min_ratio * REFERENCE_FOLLOWING_LAG_S, (lin_kp, fd)
        _assert_c_as_tuned_on_the_gantry(_ctx(spec, fd))
    # The thresholds stay clear of the bands (widening a band past them fails here).
    assert hi_k / REFERENCE_ROTATIONAL_STIFFNESS_NM_PER_RAD < CFG.stiff_wrist_min_ratio
    # and of the Micro-Fit fixture, whose tool mass differs.
    mf = ConnectorSpec.load("microfit3_4ckt")
    be = MuJoCoBackend(fixture=replace(FixtureConfig(), linear_kp_n_per_m=lo_l, angular_kp_nm_per_rad=hi_k))
    be.load(SceneParams(mf, mf.friction, Pose.identity()))
    _assert_c_as_tuned_on_the_gantry(_ctx(mf, be.fixture_dynamics))


def test_thresholds_switch_each_rule_on_its_own_axis(spec):
    ref_k, ref_lag = REFERENCE_ROTATIONAL_STIFFNESS_NM_PER_RAD, REFERENCE_FOLLOWING_LAG_S
    r, q = CFG.stiff_wrist_min_ratio, CFG.lagging_servo_min_ratio
    below = FixtureDynamics(10.0, 0.99 * r * ref_k, 0.88, 0.0, 0.99 * r * ref_k, 0.99 * q * ref_lag, 0.99 * q * ref_lag)
    _assert_c_as_tuned_on_the_gantry(_ctx(spec, below))
    # A stiff tilt axis alone: tilt damping scaled, rate-mode conform on, yaw untouched.
    tilt_only = replace(below, tilt_stiffness_nm_per_rad=r * ref_k)
    assert rotational_damping_scale(_ctx(spec, tilt_only), r) == (pytest.approx(r), 1.0)
    c = AdaptiveInsertionController()
    c.reset(_ctx(spec, tilt_only))
    assert c._rate_conform
    # A slow linear axis with fast wrist servos: probe lead only, the yaw rate keeps the W5 formula.
    slow_linear = replace(below, following_lag_s=0.2, rotational_following_lag_s=0.02)
    ctx = _ctx(spec, slow_linear)
    assert excess_following_lag(ctx, q) == pytest.approx(0.2 - ref_lag)
    assert excess_following_lag(ctx, q, rotational=True) == 0.0
    reaction = 1.0 / (2.0 * np.pi * ctx.vision_accuracy.ft_filter_cutoff_hz) + 0.002
    assert max_rotation_speed(ctx, 0.28, q) == pytest.approx(0.28 / (below.yaw_stiffness_nm_per_rad * reaction))
    c.reset(ctx)
    assert c._probe_lead > 0.0 and not c._rate_conform
    # Not characterized (None): no lag correction; rotational falls back to the translational lag.
    assert excess_following_lag(_ctx(spec, FixtureDynamics(10.0, 15.0, 0.88, 0.0)), q, rotational=True) == 0.0
    assert FixtureDynamics(10.0, 15.0, 0.88, 0.0, following_lag_s=0.2).rotational_following_lag == 0.2


def test_rules_are_active_on_the_arm(spec):
    ctx = _ctx(spec, _arm_dynamics())
    s_tilt, s_yaw = rotational_damping_scale(ctx, CFG.stiff_wrist_min_ratio)
    assert s_tilt == pytest.approx(822.0 / 15.0) and s_yaw == pytest.approx(400.0 / 15.0)
    for rotational in (False, True):
        assert excess_following_lag(ctx, CFG.lagging_servo_min_ratio, rotational) == pytest.approx(
            0.2 - REFERENCE_FOLLOWING_LAG_S)
    c = AdaptiveInsertionController()
    c.reset(ctx)
    cfg = c.cfg
    # Loop gains (stiffness / damping) back at their gantry values.
    np.testing.assert_allclose(822.0 / c.adm_conf.d, 15.0 / cfg.conform_damping_nm_s_per_rad)
    np.testing.assert_allclose([822.0, 822.0, 400.0] / c.adm_rot.d, 15.0 / cfg.rot_damping_nm_s_per_rad)
    assert c._rate_conform and not c._yaw_sweep
    assert c._probe_lead > 0.0
    assert c._yaw_probe_rate < cfg.yaw_sweep_min_speed_deg_s * DEG
    # v0.2c: on, and the insert timeout counts at the scaled contact speeds (sqrt(6.32) x 6 s).
    assert c._cavity_tilt and c._floor_impact and c._reaim_verify
    assert c.monitor.timeout_s == pytest.approx(cfg.insert_timeout_s * 6.32 ** 0.5)
    off = AdaptiveInsertionController(replace(AdaptiveConfig(), scale_insert_timeout=False, cavity_tilt_compliance=False,
                                              settle_floor_impact=False, reaim_after_verify_fail=False))
    off.reset(ctx)
    assert not (off._cavity_tilt or off._floor_impact or off._reaim_verify)
    assert off.monitor.timeout_s == cfg.insert_timeout_s
    # Resetting on the gantry afterwards restores the original dampings exactly.
    c.reset(_ctx(spec, FixtureDynamics(10.0, 15.0, 0.88, 0.0, 15.0, 0.037, 0.024)))
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
    assert fd.following_lag_s == fd.rotational_following_lag_s == pytest.approx(0.2)  # Menagerie kv / kp on every joint
    assert 500.0 < fd.tilt_stiffness_nm_per_rad < 1000.0
    assert rotational_damping_scale(_ctx(spec, fd), CFG.stiff_wrist_min_ratio)[0] > 30.0
