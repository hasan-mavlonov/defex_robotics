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
    S = Pose(np.array([0.0, 0.0, 0.03]), np.eye(3))
    for seed in range(20):
        a = SensorSuite(SensorNoiseConfig(), seed).vision_measurement(S)
        b = SensorSuite(replace(SensorNoiseConfig(), vision_outlier_probability=0.0), seed).vision_measurement(S)
        assert np.array_equal(a.p, b.p) and np.array_equal(a.R, b.R)


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
