"""v0.2c: controller C's defect verdict, gentle retract and polarization guard (latching parts)."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from defex.config import MM, AdaptiveConfig, ConnectorSpec
from defex.control.adaptive_fsm import AdaptiveInsertionController
from defex.control.registry import make_controller
from defex.recovery.failure_detector import ContactDiagnosis
from defex.tasks.conditions import conditions_by_name, latching_conditions_by_name
from defex.tasks.scenarios import sample_scenario


def _ctrl(connector: str, cfg: AdaptiveConfig | None = None) -> AdaptiveInsertionController:
    """C reset on a context with the given connector (no simulator)."""
    from defex.config import FixtureConfig, SensorNoiseConfig
    from defex.control.base import ControllerContext
    from defex.utils.transforms import Pose

    spec = ConnectorSpec.load(connector)
    ctx = ControllerContext(spec, Pose.identity(), Pose.identity(), 0.002, FixtureConfig(), SensorNoiseConfig())
    c = AdaptiveInsertionController(cfg)
    c.reset(ctx)
    return c


def _diag(kind="partial_jam", trigger="stall", depth_mm=6.5, cop_mm=(0.05, 0.0), fax=29.0, lat=(0.2, 0.0)):
    return ContactDiagnosis(kind, depth_mm * MM, fax, np.array(lat), np.zeros(3),
                            None if cop_mm is None else np.array(cop_mm) * MM, np.zeros(2), trigger)


def test_verdict_rules_are_off_on_housing_only_connectors_and_with_the_switch():
    assert not _ctrl("rect_12x8")._verdict
    assert _ctrl("microfit3_4ckt")._verdict
    assert not _ctrl("microfit3_4ckt", replace(AdaptiveConfig(), defect_verdict=False))._verdict


def test_proof_force_and_retract_cap_come_from_the_datasheet_and_budget():
    c = _ctrl("microfit3_4ckt")
    m = c.ctx.connector.mating
    assert c._proof_force == pytest.approx(1.1 * m.mating_force_max_n)
    assert c._proof_force < c.ctx.connector.force_budget.abort_n
    assert c.cfg.pull_test_fraction * m.latch_retention_force_n < c._retract_pull_cap < c.ctx.connector.force_budget.protective_stop_n


def test_hard_stop_candidates():
    c = _ctrl("microfit3_4ckt")
    assert c._stop_candidate(_diag())
    assert not c._stop_candidate(_diag(cop_mm=(1.5, 0.0)))  # off-centre support: a strip of face
    assert not c._stop_candidate(_diag(lat=(12.0, 0.0)))  # wedged sideways
    assert not c._stop_candidate(_diag(trigger="insert_timeout"))
    assert not c._stop_candidate(_diag(cop_mm=None))
    assert not c._stop_candidate(_diag(kind="surface_block", depth_mm=0.2, cop_mm=(3.5, 0.0)))  # tipped on an edge


class _Obs:
    t = 1.0
    depth = 0.0


def test_two_identical_stops_in_the_cavity_give_the_verdict_and_different_depths_do_not():
    c = _ctrl("microfit3_4ckt")
    c.S = c.G = c.ctx.home_pose
    c.state = "DETECT"
    c.touch_calibrated, c.depth_offset = True, 0.0
    assert c._confirm_stop(_Obs(), c._stop_entry(_diag(depth_mm=6.47), True)) is None
    assert c._confirm_stop(_Obs(), c._stop_entry(_diag(depth_mm=5.9), True)) is None  # another depth
    c._fail = lambda obs, reason: reason  # noqa: E731 (capture the reason, do not run the FSM)
    assert c._confirm_stop(_Obs(), c._stop_entry(_diag(depth_mm=6.40), True)) == "defect_suspected:hard_stop_short"


def test_stops_inside_the_lead_in_are_not_in_the_cavity():
    c = _ctrl("microfit3_4ckt")
    c.touch_calibrated, c.depth_offset = True, 0.0
    lead_in = c.ctx.connector.chamfer
    assert not c._in_cavity(lead_in)  # a yawed plug resting on the chamfer
    assert c._in_cavity(lead_in + 4 * c.cfg.touch_depth_sigma_mm * MM)
    c.touch_calibrated = False  # until the face is touched, the camera's depth sigma applies
    assert not c._in_cavity(lead_in + 4 * c.cfg.touch_depth_sigma_mm * MM)


@pytest.mark.slow
@pytest.mark.parametrize("cond,reason", [
    ("mf_wrong_polarization", "aborted:defect_suspected:hard_stop_short"),
    ("mf_stubbed_terminal", "aborted:defect_suspected:hard_stop_short"),
    ("mf_broken_latch", "aborted:defect_suspected:no_retention"),
])
def test_bad_parts_get_an_early_verdict_without_a_stop(task, cond, reason):
    sc = sample_scenario(latching_conditions_by_name()[cond], 0, 2026, task.backend.nominal_socket_pose)
    r = task.run(make_controller("adaptive"), sc)
    assert r.failure_reason == reason and not r.protective_stop
    assert r.cycle_time_s < 12.0  # Checkpoint 2 code: 14-26 s on these trials (dev seed 2026)
    assert any(k == "defect_verdict" for _, k, _ in r.events)


@pytest.mark.slow
def test_good_latching_part_still_seats(task):
    sc = sample_scenario(latching_conditions_by_name()["mf_nominal"], 0, 2026, task.backend.nominal_socket_pose)
    r = task.run(make_controller("adaptive"), sc)
    assert r.success and r.declared_success is True
    assert not any(k in ("defect_verdict", "proof_push", "capture_probe") for _, k, _ in r.events)


@pytest.mark.slow
def test_housing_only_connector_never_runs_the_new_rules(task):
    sc = sample_scenario(conditions_by_name()["noise_2mm"], 3, 2026, task.backend.nominal_socket_pose)
    r = task.run(make_controller("adaptive"), sc)
    kinds = {k for _, k, _ in r.events}
    assert not kinds & {"defect_verdict", "proof_push", "capture_probe", "hard_stop", "gentle_retract"}


def test_latch_phases_entered_before_a_latch_check_have_their_state():
    """Regression: a plug held while backing out on the first attempt enters the latch phases before any pull."""
    c = _ctrl("microfit3_4ckt")
    assert c._pull_start == 0.0 and not c._held_reseated and not c._no_retract


def test_slide_out_counts_as_evidence_only_from_a_flat_bottom():
    c = _ctrl("microfit3_4ckt")
    px = c.plug_half[0]
    assert c._seat_on_face(_diag(kind="seated_candidate", cop_mm=(0.2, -0.1)))
    assert c._seat_on_face(_diag(kind="seated_candidate", cop_mm=(2.0, -1.9)))  # stiff wrist, plug on the floor
    assert not c._seat_on_face(_diag(kind="seated_candidate", cop_mm=(px / MM + 1.5, -1.9)))  # off the face: wedged
    assert not c._seat_on_face(None)


def _held_obs(t: float, depth_mm: float, f_ax: float):
    from defex.perception.state_estimator import Observation
    from defex.utils.transforms import Pose

    p = Pose(np.array([0.0, 0.0, -depth_mm * MM]), np.eye(3))
    z3 = np.zeros(3)
    return Observation(t, p, p, p, Pose.identity(), Pose.identity(), p, depth_mm * MM, np.zeros(2),
                       np.array([0.0, 0.0, f_ax]), z3, z3, z3, True)


@pytest.mark.parametrize("depth_mm,checked", [(6.0, False), (8.0, True)])
def test_held_reseat_checks_the_latch_only_at_the_seat_depth(depth_mm, checked):
    """Review fix: a plug held while backing out is re-pushed; it is checked only if it reaches the seat depth
    (the gate a seated_candidate passes), otherwise it is failed in place without a pull."""
    c = _ctrl("microfit3_4ckt")
    c.S = c.G = c.ctx.home_pose
    c.touch_calibrated, c.depth_offset = True, 0.0
    c._held_reseated, c._bottom_since = True, None
    c._enter(0.0, "VERIFY", "held_reseat")
    f = c.cfg.insert_force_n
    t = 0.0
    while t < 2 * c.cfg.bottom_hold_s and c.phase == "held_reseat" and c.state == "VERIFY":
        t += c.ctx.control_period_s
        c._latch_verify_step(_held_obs(t, depth_mm, f))
    if checked:
        assert c.phase == "pull" and c._pull_start == pytest.approx(depth_mm * MM)
    else:
        assert c.state == "FAILURE" and c._fail_reason == "stuck_during_retract" and c._no_retract


def _at_pull(cfg: AdaptiveConfig | None = None) -> AdaptiveInsertionController:
    c = _ctrl("microfit3_4ckt", cfg)
    c.S = c.G = c.ctx.home_pose
    c.touch_calibrated, c.depth_offset = True, 0.0
    c._trace = []  # a flat trace: no click
    c._begin_latch_verify(_held_obs(1.0, 8.0, c.cfg.insert_force_n))
    return c


W3 = dict(click_required=True, pull_limit_wipe_fraction=0.0, pull_test_mating_factor=0.0)


def test_pull_limit_from_the_model_stroke_or_the_datasheet_wipe():
    m = ConnectorSpec.load("microfit3_4ckt").mating
    w3 = _at_pull(replace(AdaptiveConfig(), **W3))
    assert w3._pull_limit == pytest.approx((m.latch_post_snap_stroke_mm + 0.3) * MM)  # W3: 0.8 mm
    assert _at_pull()._pull_limit == pytest.approx(0.6 * m.terminal_wipe_mm * MM)  # installed (w60f): 1.05 mm


@pytest.mark.parametrize("required,phase", [(True, "latched_reseat"), (False, "release")])
def test_a_held_pull_without_a_click_passes_only_when_the_click_is_not_required(required, phase):
    c = _at_pull(replace(AdaptiveConfig(), click_required=required))
    assert not c._clicked and c.phase == "pull"
    c._latch_verify_step(_held_obs(1.1, 7.5, -c._pull_target - 1.0))  # held, 0.5 mm back
    assert c.phase == phase


def test_pull_force_covers_the_datasheet_maximum_mating_force():
    m = ConnectorSpec.load("microfit3_4ckt").mating
    assert _at_pull(replace(AdaptiveConfig(), **W3))._pull_target == pytest.approx(0.5 * m.latch_retention_force_n)
    c = _at_pull()  # installed: 35.2 N
    assert c._pull_target == pytest.approx(1.1 * m.mating_force_max_n)  # 35.2 N
    assert c._pull_target < c._retract_pull_cap < c.ctx.connector.force_budget.protective_stop_n


def test_installed_latch_check_is_the_selected_candidate():
    import json

    from defex.config import REPO_ROOT

    v = json.loads((REPO_ROOT / "results/v0.2c_integration/review_fixes/variants.json").read_text())["w60f"]
    c = AdaptiveConfig()
    assert {k: getattr(c, k) for k in v} == v
