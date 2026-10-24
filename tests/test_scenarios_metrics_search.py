import numpy as np

from defex.config import MM, Condition, DisturbanceSpec
from defex.logging.metrics import TrialResult, read_trials_csv, summarize, wilson_interval, write_csv
from defex.perception.sensors import SensorSuite
from defex.recovery.search_policy import HoleLocalizer, predicted_cop
from defex.tasks.conditions import conditions_by_name, standard_conditions
from defex.tasks.scenarios import sample_scenario
from defex.utils.transforms import Pose, axis_angle_between, twist_about_axis

NOMINAL = Pose(np.array([0.0, 0.0, 0.0366]), np.eye(3))


def test_paired_scenarios_are_identical_across_calls():
    cond = conditions_by_name()["generalization_combined"]
    a = sample_scenario(cond, 7, 2026, NOMINAL)
    b = sample_scenario(cond, 7, 2026, NOMINAL)
    np.testing.assert_array_equal(a.socket_pose.as_array(), b.socket_pose.as_array())
    np.testing.assert_array_equal(a.grasp_offset.as_array(), b.grasp_offset.as_array())
    # The vision measurement drawn for a trial is the same for every controller.
    va = SensorSuite(a.noise, a.seed).vision_measurement(a.socket_pose)
    vb = SensorSuite(b.noise, b.seed).vision_measurement(b.socket_pose)
    np.testing.assert_array_equal(va.as_array(), vb.as_array())
    c = sample_scenario(cond, 8, 2026, NOMINAL)
    assert not np.allclose(a.socket_pose.p, c.socket_pose.p)


def test_fixed_magnitude_disturbances():
    for i in range(20):
        sc = sample_scenario(Condition("t", "t", DisturbanceSpec(lateral_mm=3.0)), i, 1, NOMINAL)
        assert abs(np.linalg.norm(sc.socket_pose.p[:2] - NOMINAL.p[:2]) - 3 * MM) < 1e-12
        sc = sample_scenario(Condition("t", "t", DisturbanceSpec(yaw_deg=5.0)), i, 1, NOMINAL)
        assert abs(abs(np.rad2deg(twist_about_axis(sc.socket_pose.R))) - 5.0) < 1e-9
        sc = sample_scenario(Condition("t", "t", DisturbanceSpec(tilt_deg=10.0)), i, 1, NOMINAL)
        assert abs(np.rad2deg(axis_angle_between(sc.socket_pose.R[:, 2], np.array([0, 0, 1.0]))) - 10.0) < 1e-9


def test_standard_conditions_cover_the_brief():
    groups = {c.group for c in standard_conditions()}
    assert {"nominal", "lateral", "angular_yaw", "angular_tilt", "pose_uncertainty", "contact_variation",
            "generalization"} <= groups


def test_wilson_interval():
    lo, hi = wilson_interval(50, 100)
    assert abs(lo - 0.4038) < 1e-3 and abs(hi - 0.5962) < 1e-3
    lo, hi = wilson_interval(100, 100)
    assert abs(hi - 1.0) < 1e-12 and abs(lo - 0.9630) < 1e-3


def _result(ctrl, success, retries=0, reason="none"):
    return TrialResult(ctrl, "c", "g", 0, 1, success, reason, success, None, 4.0, 5.0, 5.0, retries,
                       success and retries > 0, 15.0, 0.1, 0.5, 0.2, 0.004, False, False, 0.3, 0.3, {"dx_mm": 1.0})


def test_summary_and_csv_round_trip(tmp_path):
    rs = [_result("adaptive", True, 2), _result("adaptive", False, 3, "aborted:retry_limit"), _result("fixed", True)]
    s = {(x["condition"], x["controller"]): x for x in summarize(rs)}
    assert s[("c", "adaptive")]["recovery_success_rate"] == 0.5
    assert s[("c", "adaptive")]["failure_reasons"] == {"aborted:retry_limit": 1}
    write_csv([r.to_row() for r in rs], tmp_path / "t.csv")
    back = read_trials_csv(tmp_path / "t.csv")
    assert [b.success for b in back] == [r.success for r in rs]
    assert back[0].disturbance["dx_mm"] == 1.0


def test_localizer_converges_on_synthetic_contacts(spec, rng):
    """Probing with forward-model observations finds the opening within a few probes."""
    found = 0
    trials = 25
    for _ in range(trials):
        true = rng.uniform(-4.0, 4.0, 2) * MM
        loc = HoleLocalizer(spec, prior_sigma=2.5 * MM, extent=7 * MM, resolution=0.25 * MM, cop_sigma=0.5 * MM)
        probe = np.zeros(2)
        cx, cy = loc.table.capture_half
        for _ in range(8):
            o = probe - true
            if abs(o[0]) <= cx and abs(o[1]) <= cy:
                found += 1
                break
            cop = predicted_cop(spec, o)
            noisy = None if cop is None else cop + rng.normal(0, 0.15 * MM, 2)
            loc.update_blocked(probe, noisy)
            probe, _ = loc.best_probe(6.5 * MM)
    assert found >= 0.9 * trials
