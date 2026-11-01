"""v0.2c: per-machine settings for the conventional cells D, E and F.

On every gantry (nominal and sim-randomized) D, E and F run exactly the config they were
tuned with on the gantry; only fixtures outside the gantry family (the UR5e) select the
stiff-fixture config tuned on the arm.
"""

from dataclasses import fields, replace

import numpy as np
import pytest

from defex.config import (
    CompliantSpiralSearchConfig,
    CompliantSpiralSearchStiffFixtureConfig,
    ConnectorSpec,
    FixtureConfig,
    PassiveComplianceConfig,
    PassiveComplianceStiffFixtureConfig,
    PositionCorrectionConfig,
    SensorNoiseConfig,
    SpiralSearchConfig,
    SpiralSearchStiffFixtureConfig,
    AdaptiveConfig,
)
from defex.control.base import (
    REFERENCE_FOLLOWING_LAG_S,
    REFERENCE_ROTATIONAL_STIFFNESS_NM_PER_RAD,
    ControllerContext,
    budgeted,
    outside_reference_family,
)
from defex.control.baselines import PassiveComplianceController, PositionCorrectionController
from defex.control.spiral_search import CompliantSpiralSearchController, SpiralSearchController
from defex.sim.backend import FixtureDynamics, SceneParams
from defex.sim.mujoco_backend import MuJoCoBackend
from defex.utils.transforms import Pose
from experiments.sim_randomization import BANDS

ARM = FixtureDynamics(8.0, 400.0, 6.32, 0.006, tilt_stiffness_nm_per_rad=822.0, following_lag_s=0.2,
                      rotational_following_lag_s=0.2)
SPIRALS = (SpiralSearchController, CompliantSpiralSearchController)


def _ctx(spec, fd):
    return ControllerContext(spec, Pose.identity(), Pose.identity(), 0.002, FixtureConfig(), SensorNoiseConfig(),
                             fixture_dynamics=fd)


def _gantries(spec):
    lo_k, hi_k = BANDS["angular_kp_nm_per_rad"]
    lo_l, hi_l = BANDS["linear_kp_n_per_m"]
    out = []
    for lin_kp, ang_kp in [(10000.0, 15.0)] + [(l, k) for l in (lo_l, hi_l) for k in (lo_k, hi_k)]:
        be = MuJoCoBackend(fixture=replace(FixtureConfig(), linear_kp_n_per_m=lin_kp, angular_kp_nm_per_rad=ang_kp))
        be.load(SceneParams(spec, spec.friction, Pose.identity()))
        out.append(be.fixture_dynamics)
    return out


def test_thresholds_match_c_and_sit_outside_the_randomization_bands():
    a = AdaptiveConfig()
    for cfg in (SpiralSearchConfig(), CompliantSpiralSearchConfig(), PassiveComplianceConfig()):
        assert (cfg.stiff_wrist_min_ratio, cfg.lagging_servo_min_ratio) == (a.stiff_wrist_min_ratio,
                                                                           a.lagging_servo_min_ratio)
    assert BANDS["angular_kp_nm_per_rad"][1] / REFERENCE_ROTATIONAL_STIFFNESS_NM_PER_RAD < a.stiff_wrist_min_ratio
    # B is not part of this workstream: its config has no per-machine fields.
    assert "stiff_wrist_min_ratio" not in {f.name for f in fields(PositionCorrectionConfig)}
    assert not hasattr(PositionCorrectionController(), "stiff_fixture_cfg")


@pytest.mark.parametrize("connector", ["rect_12x8", "microfit3_4ckt"])
def test_every_gantry_runs_the_gantry_config(connector):
    spec = ConnectorSpec.load(connector)
    for fd in _gantries(spec):
        ctx = _ctx(spec, fd)
        assert not outside_reference_family(ctx, 4.0, 2.0), fd
        for cls in SPIRALS:
            c = cls()
            gantry_cfg = c.cfg
            c.reset(ctx)
            expect = budgeted(cls(), ctx, insert_force_n="insert_target_n", max_force_n="abort_n")
            assert c.cfg == expect and c._user_cfg is gantry_cfg
            assert not c.cfg.hole_at_measured_position
        e = PassiveComplianceController()
        gantry_cfg, dwell = e.cfg, e.dwell_s
        e.reset(ctx)
        assert e.cfg is gantry_cfg and e.dwell_s == dwell
    assert not outside_reference_family(_ctx(spec, None), 4.0, 2.0)


def test_arm_runs_the_stiff_fixture_config(spec):
    ctx = _ctx(spec, ARM)
    assert outside_reference_family(ctx, 4.0, 2.0)
    for cls, stiff_cls in ((SpiralSearchController, SpiralSearchStiffFixtureConfig),
                           (CompliantSpiralSearchController, CompliantSpiralSearchStiffFixtureConfig)):
        c = cls()
        assert isinstance(c.stiff_fixture_cfg, stiff_cls)
        c.reset(ctx)
        assert c.cfg is c.stiff_fixture_cfg  # housing-only connector: no force budget to apply
        # Back on the gantry, the gantry config again (never compounded with the arm's).
        c.reset(_ctx(spec, _gantries(spec)[0]))
        assert c.cfg is c._user_cfg and not isinstance(c.cfg, stiff_cls)
    e = PassiveComplianceController()
    assert isinstance(e.stiff_fixture_cfg, PassiveComplianceStiffFixtureConfig)
    e.reset(ctx)
    assert e.cfg is e.stiff_fixture_cfg and e.dwell_s == e.stiff_fixture_cfg.dwell_s
    e.reset(_ctx(spec, _gantries(spec)[0]))
    assert type(e.cfg) is PassiveComplianceConfig


def test_each_axis_alone_switches_the_machine():
    spec = ConnectorSpec()
    r, q = 4.0, 2.0
    below = FixtureDynamics(10.0, 0.99 * r * 15.0, 0.88, 0.0, 0.99 * r * 15.0, 0.99 * q * REFERENCE_FOLLOWING_LAG_S,
                            0.99 * q * REFERENCE_FOLLOWING_LAG_S)
    assert not outside_reference_family(_ctx(spec, below), r, q)
    for change in (dict(tilt_stiffness_nm_per_rad=r * 15.0), dict(yaw_stiffness_nm_per_rad=r * 15.0),
                   dict(following_lag_s=q * REFERENCE_FOLLOWING_LAG_S),
                   dict(rotational_following_lag_s=q * REFERENCE_FOLLOWING_LAG_S)):
        assert outside_reference_family(_ctx(spec, replace(below, **change)), r, q), change


def test_force_budget_applies_on_the_arm_too():
    mf = ConnectorSpec.load("microfit3_4ckt")
    c = SpiralSearchController()
    c.reset(_ctx(mf, ARM))
    assert c.cfg.insert_force_n == mf.force_budget.insert_target_n
    assert c.cfg.max_force_n == mf.force_budget.abort_n
    assert type(c.cfg) is SpiralSearchStiffFixtureConfig


def test_scripts_may_still_swap_the_gantry_config(spec):
    c = SpiralSearchController()
    c.cfg = replace(c.cfg, spiral_pitch_mm=0.5)
    c.reset(_ctx(spec, _gantries(spec)[0]))
    assert c.cfg.spiral_pitch_mm == 0.5
    c.reset(_ctx(spec, _gantries(spec)[0]))  # not compounded
    assert c.cfg.spiral_pitch_mm == 0.5


def test_hole_found_at_the_measured_position_when_enabled():
    """With the flag on, INSERT continues from the measured tip position (obs.lateral)."""
    from types import SimpleNamespace

    spec = ConnectorSpec()
    for flag, expect in ((False, [0.4e-3, 0.0]), (True, [0.1e-3, -0.2e-3])):
        c = SpiralSearchController(stiff_fixture_cfg=replace(SpiralSearchStiffFixtureConfig(), hole_at_measured_position=flag))
        c.reset(_ctx(spec, ARM))
        c.S, c.G, c.t_start = Pose.identity(), Pose.identity(), 0.0
        c.state, c.face_depth, c.theta = "SPIRAL", 0.0, 0.0
        c.xy = np.array([0.4e-3, 0.0])
        obs = SimpleNamespace(t=1.0, force=np.array([0.0, 0.0, c.cfg.search_force_n]), torque=np.zeros(3),
                              depth=c.cfg.hole_push_mm * 1e-3 + 1e-4, lateral=np.array([0.1e-3, -0.2e-3]),
                              setpoint=Pose.identity())
        c._spiral_step(obs)
        assert c.state == "INSERT"
        np.testing.assert_allclose(c.xy, expect)
