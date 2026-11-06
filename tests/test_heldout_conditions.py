"""W2 held-out families: outliers, mis-characterized vision, hidden bias."""

from dataclasses import replace

import numpy as np

from defex.config import MM, SensorNoiseConfig
from defex.perception.sensors import SensorSuite
from defex.tasks.conditions import conditions_by_name, heldout_conditions, heldout_conditions_by_name
from defex.tasks.scenarios import sample_scenario
from defex.utils.transforms import Pose


def test_heldout_families_are_not_reachable_from_the_development_conditions():
    names = {c.name for c in heldout_conditions()}
    assert len(names) == 5
    assert not names & set(conditions_by_name())


def test_outlier_option_leaves_existing_vision_streams_unchanged():
    """The vision draw must equal V0.1's algorithm exactly (reimplemented here) when outliers are off."""
    from defex.config import DEG
    from defex.utils.transforms import rotvec_to_matrix

    noise = SensorNoiseConfig()
    S = Pose(np.array([0.0, 0.0, 0.03]), np.eye(3))
    for seed in range(20):
        got = SensorSuite(noise, seed).vision_measurement(S)
        ss = np.random.SeedSequence(seed)
        vision_ss, _, ft_ss, _ = ss.spawn(4)
        r = np.random.default_rng(vision_ss)
        bias_dir = r.uniform(0.0, 2.0 * np.pi)  # drawn in the constructor (V0.1)
        dp = np.array([r.normal(0.0, noise.vision_xy_sigma_mm), r.normal(0.0, noise.vision_xy_sigma_mm),
                       r.normal(0.0, noise.vision_z_sigma_mm)]) * MM
        tilt = np.array([r.normal(0.0, noise.vision_tilt_sigma_deg), r.normal(0.0, noise.vision_tilt_sigma_deg), 0.0]) * DEG
        yaw = r.normal(0.0, noise.vision_yaw_sigma_deg) * DEG
        R = rotvec_to_matrix(tilt) @ rotvec_to_matrix(np.array([0.0, 0.0, yaw]))
        bias = noise.vision_bias_mm * MM * np.array([np.cos(bias_dir), np.sin(bias_dir), 0.0])
        assert np.array_equal(got.p, S.p + dp + bias) and np.array_equal(got.R, S.R @ R)


def test_outliers_occur_at_the_configured_rate_and_size():
    noise = replace(SensorNoiseConfig(), vision_outlier_probability=0.05)
    S = Pose(np.zeros(3), np.eye(3))
    err = np.array([np.hypot(*SensorSuite(noise, s).vision_measurement(S).p[:2]) for s in range(4000)]) / MM
    big = err > 2.5  # nominal sigma is 0.3 mm, so >2.5 mm is an outlier
    assert 0.04 < big.mean() < 0.06
    assert err[big].min() > 2.0 and err[big].max() < 7.0


def test_controllers_are_told_the_characterized_not_the_true_accuracy(task):
    from defex.control.registry import make_controller

    cond = heldout_conditions_by_name()["heldout_mischar_2mm"]
    sc = sample_scenario(cond, 0, 2026, task.backend.nominal_socket_pose)
    assert sc.noise.vision_xy_sigma_mm == 2.0 and sc.characterized_noise.vision_xy_sigma_mm == 0.5
    ctrl = make_controller("fixed")
    task.run(ctrl, sc)
    assert ctrl.ctx.vision_accuracy.vision_xy_sigma_mm == 0.5
