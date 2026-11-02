"""v0.2d: controller C's tilt check at the start of the latching VERIFY (unit level, plus one arm trial)."""

from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from defex.config import DEG, MM, AdaptiveConfig, ConnectorSpec, FixtureConfig, SensorNoiseConfig
from defex.control.adaptive_fsm import RECOVER, VERIFY, AdaptiveInsertionController
from defex.control.base import ControllerContext
from defex.recovery.failure_detector import ContactDiagnosis
from defex.utils.transforms import Pose, rotvec_to_matrix


def _ctrl(connector: str = "microfit3_4ckt", **overrides) -> AdaptiveInsertionController:
    spec = ConnectorSpec.load(connector)
    c = AdaptiveInsertionController(replace(AdaptiveConfig(), **overrides))
    c.reset(ControllerContext(spec, Pose.identity(), Pose.identity(), 0.002, FixtureConfig(), SensorNoiseConfig()))
    c.S = Pose.identity()
    c.G = Pose.identity()
    return c


def _obs(tilt_rv_deg=(0.0, 0.0, 0.0), cop_mm=(0.0, 0.0), fz=25.0, t=1.0):
    """Observation of a plug pressed at the bottom: plug axis turned by ``tilt_rv_deg`` in the estimated socket
    frame, bottoming wrench with its centre of pressure at ``cop_mm``."""
    R = rotvec_to_matrix(np.asarray(tilt_rv_deg, dtype=float) * DEG)
    x, y = np.asarray(cop_mm) * MM
    return SimpleNamespace(t=t, force=np.array([0.0, 0.0, fz]), torque=np.array([y * fz, -x * fz, 0.0]),
                           rel_pose=Pose(np.array([0.0, 0.0, -7.7 * MM]), R), lateral=np.zeros(2), depth=7.7 * MM,
                           setpoint=Pose(np.zeros(3), np.eye(3)), fixture_tcp=Pose(np.zeros(3), np.eye(3)))


def _fill(c: AdaptiveInsertionController, obs) -> None:
    for _ in range(c.cfg.recent_samples):
        c._recent.append(obs)


def test_evidence_is_the_plug_axis_against_the_socket_estimate_and_the_cop_edge_fraction():
    c = _ctrl()
    o = _obs(tilt_rv_deg=(-2.3, 2.3, 0.0), cop_mm=(3.1, -0.5))
    _fill(c, o)
    tilt, edge = c._tilt_evidence(o)
    assert tilt / DEG == pytest.approx(np.hypot(2.3, 2.3), rel=1e-3)
    assert edge == pytest.approx(3.1 * MM / c.plug_half[0], rel=1e-6)
    # Measured against R_corr (flat-face folds), not the camera's frame: a plug along the folded axis is aligned.
    c.R_corr = rotvec_to_matrix(np.array([-2.3, 2.3, 0.0]) * DEG)
    assert c._tilt_evidence(o)[0] / DEG == pytest.approx(0.0, abs=1e-6)
    # Yaw is not tilt.
    o2 = _obs(tilt_rv_deg=(0.0, 0.0, 5.0))
    c.R_corr = np.eye(3)
    assert c._tilt_evidence(o2)[0] == pytest.approx(0.0, abs=1e-9)


def test_evidence_averages_the_recent_wrench_less_its_first_third():
    c = _ctrl()
    early = _obs(cop_mm=(0.0, 0.0))
    late = _obs(cop_mm=(0.0, 3.0))
    n = c.cfg.recent_samples
    for k in range(n):
        c._recent.append(early if k < n // c.cfg.detect_discard_divisor else late)
    assert c._tilt_evidence(late)[1] == pytest.approx(3.0 * MM / c.plug_half[1])


@pytest.mark.parametrize("tilt, cop, ok", [
    ((-2.4, 2.4, 0.0), (3.2, 0.0), False),  # turned off the axis and held by the walls
    ((-2.4, 2.4, 0.0), (2.0, 2.0), True),  # turned, but the push goes through the floor (CoP at a floor corner)
    ((0.3, 0.2, 0.0), (3.6, 0.0), True),  # walls loaded, plug along the socket estimate
    ((0.0, 1.9, 0.0), (0.0, 4.0), True),  # just inside the tilt bound
])
def test_verdict_needs_both_tilt_and_wall_held_cop(tilt, cop, ok):
    c = _ctrl(tilt_check_deg=2.0)
    o = _obs(tilt_rv_deg=tilt, cop_mm=cop)
    _fill(c, o)
    assert c._tilt_verdict(o) is ok
    assert c.events[-1].kind == "tilt" and c.events[-1].detail.endswith("PASS" if ok else "FAIL")


def test_installed_setting_and_switch():
    cfg = AdaptiveConfig()
    assert cfg.tilt_check and cfg.tilt_check_deg == 2.5 and cfg.tilt_check_edge_fraction == 0.875
    import json

    from defex.config import REPO_ROOT

    picked = json.loads((REPO_ROOT / "results/v0.2d_tilt_check/variants.json").read_text())["tilt_k2"]
    assert all(getattr(cfg, k) == v for k, v in picked.items())


def test_with_the_switch_off_the_latch_check_runs_as_before():
    c = _ctrl(tilt_check=False)
    o = _obs(tilt_rv_deg=(-2.4, 2.4, 0.0), cop_mm=(3.2, 0.0))
    _fill(c, o)
    c._trace = []
    c._begin_latch_verify(o)
    assert c.state == VERIFY and c.phase == "pull"
    assert not any(e.kind == "tilt" for e in c.events)


def test_failed_tilt_check_takes_the_normal_verify_failure_path():
    c = _ctrl(tilt_check=True, tilt_check_deg=2.0)
    o = _obs(tilt_rv_deg=(-2.4, 2.4, 0.0), cop_mm=(3.2, 0.0))
    _fill(c, o)
    c._trace = []
    c.diagnosis = ContactDiagnosis("seated_candidate", 7.7 * MM, 25.0, np.zeros(2), np.zeros(3), np.array([3.2, 0.0]) * MM,
                                   np.zeros(2), "bottomed")
    c._begin_latch_verify(o)
    assert c.state == RECOVER and c.diagnosis.kind == "verify_failed"
    assert [e.detail.endswith("FAIL") for e in c.events if e.kind == "tilt"] == [True]
    # A plug that passes the check goes on to the pull, exactly as without the check.
    c2 = _ctrl(tilt_check=True)
    o2 = _obs(tilt_rv_deg=(0.2, 0.1, 0.0), cop_mm=(2.0, 2.0))
    _fill(c2, o2)
    c2._trace = []
    c2._begin_latch_verify(o2)
    assert c2.state == VERIFY and c2.phase == "pull"


def test_housing_only_connector_never_runs_the_check():
    c = _ctrl("rect_12x8", tilt_check=True)
    assert not c.latching
    calls = []
    c._tilt_verdict = lambda obs: calls.append(obs) or True
    o = _obs()
    _fill(c, o)
    c._begin_verify(o)
    assert c.phase == "seat_conform" and not calls


@pytest.mark.slow
def test_training_seed_tilt_escape_is_rejected_on_the_arm():
    """Seed 3004, mf_noise_1mm, trial 17 (training seeds): C passes a latched plug 3.2 deg tilted. With the check
    VERIFY fails, the retract is held by the latch, and C leaves the plug in place without declaring it seated."""
    pytest.importorskip("mujoco")
    import os

    from defex.tasks.conditions import latching_conditions_by_name
    from defex.tasks.insertion import InsertionTask
    from defex.tasks.scenarios import sample_scenario
    from experiments.runner import nominal_socket_pose

    try:
        from defex.sim.arm_backend import MuJoCoArmBackend

        backend = MuJoCoArmBackend()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"arm backend unavailable: {exc}")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    task = InsertionTask(backend=backend)
    cond = latching_conditions_by_name()["mf_noise_1mm"]
    scenario = sample_scenario(cond, 17, 3004, nominal_socket_pose(cond, task.fixture))
    base = task.run(AdaptiveInsertionController(replace(AdaptiveConfig(), tilt_check=False)), scenario)
    assert base.failure_reason == "false_accept" and base.final_tilt_deg > 3.0
    checked = task.run(AdaptiveInsertionController(), scenario)
    assert checked.declared_success is False and checked.failure_reason == "aborted:stuck_during_retract"
    assert any(k == "tilt" and d.endswith("FAIL") for _, k, d in checked.events)


def test_a_failed_check_holds_for_the_rest_of_the_attempt_while_the_plug_stays_turned():
    c = _ctrl(tilt_check=True, tilt_check_deg=2.0)
    c.attempts = 3
    wedged = _obs(tilt_rv_deg=(-2.4, 2.4, 0.0), cop_mm=(3.2, 0.0))
    _fill(c, wedged)
    assert not c._tilt_verdict(wedged)
    # Re-seated after a held retract: the walls are unloaded, the plug is still turned.
    reseated = _obs(tilt_rv_deg=(-2.3, 2.3, 0.0), cop_mm=(2.0, 2.0))
    _fill(c, reseated)
    assert not c._tilt_verdict(reseated)
    # Turned back within the bound, or a new attempt: the CoP is needed again.
    _fill(c, _obs(tilt_rv_deg=(0.5, 0.5, 0.0), cop_mm=(2.0, 2.0)))
    assert c._tilt_verdict(_obs(tilt_rv_deg=(0.5, 0.5, 0.0)))
    c.attempts = 4
    _fill(c, reseated)
    assert c._tilt_verdict(reseated)
