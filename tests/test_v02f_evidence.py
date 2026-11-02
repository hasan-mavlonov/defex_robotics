from collections import defaultdict
from pathlib import Path

import pytest

from experiments import v02f_evidence as ev

REPO = Path(__file__).resolve().parents[1]
CRIT = {"depth_tolerance_mm": 0.5, "lateral_margin_mm": 0.15, "max_tilt_deg": 3.0, "max_yaw_deg": 3.0}
HOUSING = {"defect": None, "connector": "rect_12x8", "depth_mm": 15.0, "lat_limit_mm": 0.65}


def row(depth=15.0, lat=0.1, yaw=0.0, tilt=0.0, **kw):
    r = {"final_depth_mm": str(depth), "final_lateral_mm": str(lat), "final_yaw_deg": str(yaw),
         "final_tilt_deg": str(tilt), "success": "True", "declared_success": "True", "gt_seated": "True",
         "protective_stop": "False", "failure_reason": "none"}
    r.update(kw)
    return r


def test_failed_checks_reads_each_tolerance():
    assert ev.failed_checks(row(), HOUSING, CRIT) == ["not logged"]
    assert ev.failed_checks(row(depth=14.49), HOUSING, CRIT) == ["depth"]
    assert ev.failed_checks(row(yaw=-3.01), HOUSING, CRIT) == ["yaw"]
    assert ev.failed_checks(row(tilt=3.2, yaw=3.5), HOUSING, CRIT) == ["yaw", "tilt"]
    # radius above the per-axis limit but inside sqrt(2) x limit: undecidable from the radius
    assert ev.failed_checks(row(lat=0.8), HOUSING, CRIT) == ["lateral?"]
    assert ev.failed_checks(row(lat=0.95), HOUSING, CRIT) == ["lateral"]


def test_recomputed_seated_matches_the_code_rule_on_clear_cases():
    assert ev.recomputed_seated(row(depth=14.5, yaw=3.0, tilt=3.0, lat=0.65), HOUSING, CRIT)
    assert not ev.recomputed_seated(row(depth=14.499), HOUSING, CRIT)
    assert not ev.recomputed_seated(row(tilt=3.001), HOUSING, CRIT)


def test_bad_unit_and_outcome_classes():
    assert ev.bad_unit(row(success="False", gt_seated="False"))
    assert not ev.bad_unit(row(success="False", gt_seated="False", declared_success="False"))
    assert ev.other_outcome(row(success="False", gt_seated="False")) == "bad unit"
    assert ev.other_outcome(row(success="False", declared_success="False")) == "rejected or aborted"
    assert ev.other_outcome(row(success="False", declared_success="", protective_stop="True")) == "protective stop"


def test_phase_times_buckets_sum_to_the_cycle():
    events = [
        [0.2, "state", "APPROACH"], [1.7, "state", "ALIGN"], [1.8, "attempt", "#1"], [1.8, "state", "INSERT"],
        [2.5, "state", "DETECT: stall"], [3.0, "state", "RECOVER: surface_block"], [3.3, "state", "ALIGN: retry 1"],
        [3.5, "state", "INSERT"], [5.0, "state", "VERIFY"], [6.0, "state", "RECOVER: verify_failed"],
        [6.5, "state", "ALIGN: retry 2"], [6.7, "state", "INSERT"], [7.5, "state", "VERIFY"],
        [9.0, "state", "SUCCESS"], [9.0, "finish", "success=True"],
    ]
    acc, gap = ev.phase_times(events, 8.8)
    assert gap == pytest.approx(0.0)
    assert acc["approach"] == pytest.approx(1.5)
    assert acc["align"] == pytest.approx(0.1)
    assert acc["first_insert"] == pytest.approx(1.2)
    assert acc["retry"] == pytest.approx(2.0)
    assert acc["verify"] == pytest.approx(2.5)
    assert acc["reinsert_after_verify"] == pytest.approx(1.5)
    assert sum(acc.values()) == pytest.approx(8.8)


def test_phase_times_spiral_retry():
    events = [[0.2, "state", "APPROACH"], [1.7, "state", "TARE"], [1.8, "state", "DESCEND"],
              [2.6, "state", "APPROACH: retry"], [3.0, "state", "TARE"], [3.1, "state", "DESCEND"],
              [3.9, "state", "SUCCESS"], [3.9, "finish", "x"]]
    acc, gap = ev.phase_times(events, 3.7)
    assert gap == pytest.approx(0.0)
    assert acc["align"] == pytest.approx(0.1)
    assert acc["first_insert"] == pytest.approx(0.8)
    assert acc["retry"] == pytest.approx(1.3)


def test_discordant_and_direction():
    run = object.__new__(ev.Run)
    rows = [{"condition": "a", "controller": "adaptive", "trial_index": str(i), "success": s}
            for i, s in enumerate(["True", "True", "False", "True"])]
    rows += [{"condition": "a", "controller": "spiral_rcc", "trial_index": str(i), "success": s}
             for i, s in enumerate(["True", "False", "True", "False"])]
    run.by = {(r["condition"], r["controller"], r["trial_index"]): r for r in rows}
    run.ctrl_rows = defaultdict(list)
    for r in rows:
        run.ctrl_rows[r["controller"]].append(r)
    a, b, keys = ev.discordant(run, ("a",), "adaptive", "spiral_rcc")
    assert (a, b) == (2, 1)
    assert keys == [("a", "1"), ("a", "3")]
    assert ev.direction([(2, 1), (5, 0), (1, 0)]) == "C ahead on all 3"
    assert ev.direction([(0, 1), (0, 5), (1, 3)]) == "other ahead on all 3"
    assert ev.direction([(2, 1), (0, 1), (0, 0)]) == "mixed"


def test_v02e_gantry_standard_numbers_from_the_committed_run():
    folder = REPO / "results/benchmark_v0.2e/gantry_standard"
    if not (folder / "trials.csv").exists():
        pytest.skip("benchmark_v0.2e not present")
    run = ev.Run(folder, ev.connector_specs(REPO))
    a, b, keys = ev.discordant(run, run.good_conds(), ev.C, ev.I)
    assert (a, b) == (53, 8)  # benchmark_v0.2e REPORT.md, gantry standard
    assert all(cd in ev.NOISY for cd, _ in keys)
    assert sum(ev.bad_unit(r) for r in run.ctrl_rows[ev.I]) == 32
    assert sum(ev.bad_unit(r) for r in run.ctrl_rows[ev.C]) == 0


def test_verify_corrections_parses_tilt_and_yaw_events():
    events = [[1.0, "state", "VERIFY"], [1.1, "seat_conform", "tilt aligned to floor by (+0.95,-1.36) deg"],
              [1.5, "yaw_centering", "limits (-2.9,+7.0) deg -> corrected +2.08 deg"],
              [1.9, "wall_yaw", "half free travel 0.155 mm (>= 0.293 for 2.0 deg), levers (-4.9,-5.0) mm -> turn -3.36 deg"]]
    tilt, yaw = ev.verify_corrections(events)
    assert tilt == pytest.approx((0.95 ** 2 + 1.36 ** 2) ** 0.5)
    assert yaw == pytest.approx(2.08 + 3.36)
    assert ev.verify_corrections([[0.0, "state", "VERIFY"]]) == (None, 0.0)


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
