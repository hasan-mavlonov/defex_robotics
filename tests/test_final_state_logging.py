import pytest


def test_final_state_logs_per_axis_offset_speed_and_latch():
    from types import SimpleNamespace

    import numpy as np

    from defex.config import MM, SuccessCriteria
    from defex.sim.backend import GroundTruth
    from defex.tasks.insertion import evaluate_final_state
    from defex.utils.transforms import Pose

    sock = SimpleNamespace(clearance_mm=0.5)
    scen = SimpleNamespace(connector=SimpleNamespace(socket=sock, depth=15.0 * MM))
    eye = np.eye(3)

    def gt(x, y, speed, latched=None, broken=False):
        return GroundTruth(0.0, Pose(np.zeros(3), eye), Pose(np.array([x, y, -15.0 * MM]), eye), np.zeros(3),
                           0.0, 0.0, 0, speed, False, False, latched=latched, latch_broken=broken)

    # corner: radius 0.85 mm > 0.65 mm, but each axis 0.6 mm passes
    f = evaluate_final_state(gt(0.6 * MM, -0.6 * MM, 0.001), scen, SuccessCriteria())
    assert f["seated"] and f["x_mm"] == pytest.approx(0.6) and f["y_mm"] == pytest.approx(-0.6)
    assert f["tcp_speed_mm_s"] == pytest.approx(1.0) and f["latched"] is None and f["latch_intact"] is None
    f = evaluate_final_state(gt(0.0, 0.0, 0.003), scen, SuccessCriteria())
    assert not f["seated"] and f["failed_checks"] == ["settled"]
    f = evaluate_final_state(gt(0.0, 0.0, 0.0, latched=True, broken=True), scen, SuccessCriteria())
    assert not f["seated"] and f["latched"] is True and f["latch_intact"] is False


def test_trial_result_new_columns_round_trip(tmp_path):
    from defex.logging.metrics import TrialResult, read_trials_csv, write_csv

    r = TrialResult("c", "x", "g", 0, 1, True, "none", True, True, 4.0, 1.0, 1.0, 0, False, 15.0, 0.1, 0.0, 0.0,
                    0.0, False, False, 0.3, 0.3, final_x_mm=0.1, final_y_mm=-0.2, final_tcp_speed_mm_s=0.5,
                    final_latched=True, final_latch_intact=False)
    write_csv([r.to_row()], tmp_path / "t.csv")
    back = read_trials_csv(tmp_path / "t.csv")[0]
    assert (back.final_x_mm, back.final_y_mm, back.final_tcp_speed_mm_s) == (0.1, -0.2, 0.5)
    assert back.final_latched is True and back.final_latch_intact is False
