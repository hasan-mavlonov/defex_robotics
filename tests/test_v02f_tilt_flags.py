"""v0.2f tilt diagnosis: the default-off options (results/v0.2f_tilt_diagnosis)."""

from __future__ import annotations

import pytest

from defex.config import AdaptiveConfig
from defex.control.adaptive_fsm import RECOVER, VERIFY
from defex.control.registry import make_controller
from test_tilt_check import _ctrl, _fill, _obs


def test_both_options_are_off_by_default():
    assert AdaptiveConfig().tilt_check_push_below_floor is False
    for name in ("spiral_rcc_verify", "spiral_rcc_verify_reject", "spiral_rcc_verify_research"):
        j = make_controller(name)
        assert j.handover_window is False and j.verifier.cfg.tilt_check_push_below_floor is False
    for name in ("adaptive", "adaptive_learned"):
        assert make_controller(name).cfg.tilt_check_push_below_floor is False


def test_off_a_low_window_gives_no_verdict_and_goes_to_the_pull():
    c = _ctrl()
    o = _obs(tilt_rv_deg=(-2.4, 2.4, 0.0), cop_mm=(3.2, 0.0), fz=5.0)
    _fill(c, o)
    c._trace = []
    c._begin_latch_verify(o)
    assert c.state == VERIFY and c.phase == "pull"
    assert not any(e.kind == "tilt_push" for e in c.events)


def test_on_a_low_window_first_pushes_at_the_proof_force():
    c = _ctrl(tilt_check_push_below_floor=True)
    o = _obs(tilt_rv_deg=(-2.4, 2.4, 0.0), cop_mm=(3.2, 0.0), fz=5.0)
    _fill(c, o)
    c._trace = []
    c._begin_latch_verify(o)
    assert c.state == VERIFY and c.phase == "bottom_proof" and c._proof_t_force is None
    assert [e.kind for e in c.events if e.kind in ("tilt", "tilt_push")] == ["tilt_push"]
    # The push held: the verdict comes from the push's window, under the same bounds.
    wedged = _obs(tilt_rv_deg=(-2.4, 2.4, 0.0), cop_mm=(3.2, 0.0), fz=36.0)
    _fill(c, wedged)
    c._begin_latch_verify(wedged)
    assert c.state == RECOVER and c.diagnosis.kind == "verify_failed"
    assert [e.detail.endswith("FAIL") for e in c.events if e.kind == "tilt"] == [True]


def test_on_an_empty_window_also_pushes():
    c = _ctrl(tilt_check_push_below_floor=True)
    o = _obs(tilt_rv_deg=(-3.0, 3.0, 0.0))
    c._trace = []
    c._begin_latch_verify(o)
    assert c.phase == "bottom_proof" and [e.kind for e in c.events if e.kind in ("tilt", "tilt_push")] == ["tilt_push"]


def test_on_a_push_that_stays_under_the_floor_gives_no_verdict_and_no_second_push():
    c = _ctrl(tilt_check_push_below_floor=True)
    o = _obs(tilt_rv_deg=(-2.4, 2.4, 0.0), cop_mm=(3.2, 0.0), fz=5.0)
    _fill(c, o)
    c._trace = []
    c.phase = "bottom_proof"  # the push timed out (or the slide-out proof push did)
    c._begin_latch_verify(o)
    assert c.state == VERIFY and c.phase == "pull"
    assert [e.detail for e in c.events if e.kind == "tilt"][-1].endswith("no verdict")
    assert not any(e.kind == "tilt_push" for e in c.events)


@pytest.mark.parametrize("on", [False, True])
def test_a_window_over_the_floor_is_checked_the_same_with_the_option_on_or_off(on):
    c = _ctrl(tilt_check_push_below_floor=on)
    o = _obs(tilt_rv_deg=(0.2, 0.1, 0.0), cop_mm=(2.0, 2.0), fz=25.0)
    _fill(c, o)
    c._trace = []
    c._begin_latch_verify(o)
    assert c.state == VERIFY and c.phase == "pull"
    assert [e.detail.endswith("PASS") for e in c.events if e.kind == "tilt"] == [True]


def test_housing_only_or_check_off_never_pushes():
    c = _ctrl("rect_12x8", tilt_check_push_below_floor=True)
    assert not c.latching
    c2 = _ctrl(tilt_check=False, tilt_check_push_below_floor=True)
    o = _obs(fz=2.0)
    _fill(c2, o)
    c2._trace = []
    c2._begin_latch_verify(o)
    assert c2.phase == "pull" and not any(e.kind in ("tilt", "tilt_push") for e in c2.events)


def _j_first_check(task, handover_window: bool):
    from defex.tasks.conditions import latching_conditions_by_name
    from defex.tasks.scenarios import sample_scenario
    from experiments.runner import nominal_socket_pose

    c = latching_conditions_by_name()["mf_nominal"]
    sc = sample_scenario(c, 0, 2026, nominal_socket_pose(c, task.fixture))
    j = make_controller("spiral_rcc_verify")
    j.handover_window = handover_window
    seen = []
    orig = j.verifier._begin_latch_verify

    def wrap(obs):
        seen.append(len(j.verifier._recent))
        return orig(obs)

    j.verifier._begin_latch_verify = wrap
    res = task.run(j, sc)
    tilt = [d for _, k, d in res.events if k == "tilt"]
    return res, seen, tilt


def test_j_hand_over_window(task):
    off, seen_off, tilt_off = _j_first_check(task, False)
    on, seen_on, tilt_on = _j_first_check(task, True)
    assert seen_off[0] == 0 and tilt_off[0].endswith("no verdict")
    n = AdaptiveConfig().recent_samples
    assert seen_on[0] == n and (tilt_on[0].endswith("PASS") or tilt_on[0].endswith("FAIL"))
    assert off.declared_success == on.declared_success
