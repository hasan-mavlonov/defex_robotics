"""Conventional baselines D (spiral search), E (vision + RCC) and F (spiral + RCC)."""

import numpy as np
import pytest

from defex.config import MM, CompliantStageConfig
from defex.control.registry import CONTROLLERS, make_controller
from defex.logging.metrics import TrialResult, is_escape, mcnemar_exact, throughput_uph
from defex.sim.backend import SceneParams
from defex.sim.mujoco_backend import MuJoCoBackend
from defex.sim.scene_builder import build_workcell_xml
from defex.tasks.conditions import conditions_by_name
from defex.tasks.scenarios import sample_scenario
from defex.utils.transforms import Pose


def test_all_six_controllers_are_registered():
    assert {"fixed", "correction", "adaptive", "spiral", "correction_rcc", "spiral_rcc"} <= set(CONTROLLERS)
    assert make_controller("correction_rcc").compliant_wrist and make_controller("spiral_rcc").compliant_wrist
    assert not make_controller("spiral").compliant_wrist


def test_rigid_scene_is_unchanged_by_the_compliance_option():
    assert "rcc_x" not in build_workcell_xml()
    assert "rcc_x" in build_workcell_xml(compliance=CompliantStageConfig())


def test_rcc_stage_deflects_at_its_datasheet_stiffness(spec):
    """A static lateral push on the plug tip deflects the stage by F / k."""
    be = MuJoCoBackend()
    be.load(SceneParams(spec, spec.friction, Pose.identity(), compliance=CompliantStageConfig()))
    m, d = be.model, be.data
    jx = m.joint("rcc_x").qposadr[0]
    be.set_tcp_setpoint(be.home_tcp_pose)
    plug = m.body("connector").id
    force = 2.0  # N, well inside the 1.65 mm travel
    for _ in range(3000):
        d.xfrc_applied[plug, :3] = (force, 0.0, 0.0)
        be.step(0.0005)
    k = CompliantStageConfig().lateral_stiffness_n_per_mm / MM
    servo = 1e4  # the stiff x servo deflects too, in series
    assert d.qpos[jx] == pytest.approx(force / k, rel=0.05)
    assert d.qpos[jx] < force / k + force / servo


def test_escape_and_throughput_definitions():
    def r(success, stop=False, declared=None, cycle=5.0):
        return TrialResult("x", "c", "g", 0, 0, success, "none", success, declared, cycle, 0, 0, 0, False,
                           15, 0, 0, 0, 0, stop, False, 0.3, 0.3)

    assert not is_escape(r(True))
    assert is_escape(r(False))  # no self-check, no stop: the bad unit leaves the cell
    assert not is_escape(r(False, stop=True))
    assert not is_escape(r(False, declared=False))
    assert is_escape(r(False, declared=True))  # false accept
    rs = [r(True), r(False, stop=True)]
    assert throughput_uph(rs, 0.0) == pytest.approx(360.0)
    assert throughput_uph(rs, 60.0) == pytest.approx(3600.0 / 70.0)
    assert mcnemar_exact(1, 9) == pytest.approx(0.021484375)
    assert mcnemar_exact(4, 4) == 1.0


@pytest.mark.slow
@pytest.mark.parametrize("ctrl", ["spiral", "correction_rcc", "spiral_rcc"])
def test_conventional_baselines_insert_on_the_nominal_socket(task, ctrl):
    sc = sample_scenario(conditions_by_name()["nominal"], 0, 2026, task.backend.nominal_socket_pose)
    res = task.run(make_controller(ctrl), sc)
    assert res.success, res.failure_reason
    assert res.max_penetration_mm < 0.05


@pytest.mark.slow
def test_spiral_search_finds_a_hole_outside_the_lead_in(task):
    # Vision noise 1 mm: on development trial 1 the first touch lands on the face and the spiral finds the hole.
    found = False
    for i in range(6):
        sc = sample_scenario(conditions_by_name()["noise_1mm"], i, 2026, task.backend.nominal_socket_pose)
        res = task.run(make_controller("spiral"), sc)
        kinds = [k for _, k, _ in res.events]
        if "hole_found" in kinds and res.success:
            found = True
            break
    assert found


@pytest.mark.slow
def test_optional_retention_pull_on_the_spiral_baseline(task):
    """v0.2c review: F with retention_pull fails a broken latch it would pass on depth; off by default."""
    from dataclasses import replace as _replace

    from defex.control.registry import make_controller
    from defex.tasks.conditions import latching_conditions_by_name
    from defex.tasks.scenarios import sample_scenario

    assert not make_controller("spiral_rcc").cfg.retention_pull
    out = {}
    for cond in ("mf_nominal", "mf_broken_latch"):
        sc = sample_scenario(latching_conditions_by_name()[cond], 0, 2026, task.backend.nominal_socket_pose)
        ctrl = make_controller("spiral_rcc")
        ctrl.cfg = _replace(ctrl.cfg, retention_pull=True)
        out[cond] = task.run(ctrl, sc)
    assert out["mf_nominal"].success
    assert not out["mf_broken_latch"].declared_success
    assert out["mf_broken_latch"].failure_reason == "aborted:retention_failed"


def test_h_and_i_are_d_and_f_with_cs_retention_pull():
    from dataclasses import asdict

    from defex.config import AdaptiveConfig
    from defex.control.registry import make_controller

    a = AdaptiveConfig()
    for base, pulled in (("spiral", "spiral_pull"), ("spiral_rcc", "spiral_rcc_pull")):
        b, p = make_controller(base), make_controller(pulled)
        for cb, cp in ((b.cfg, p.cfg), (b.stiff_fixture_cfg, p.stiff_fixture_cfg)):
            diff = {k for k, v in asdict(cp).items() if asdict(cb)[k] != v}
            assert diff <= {"retention_pull", "pull_test_mating_factor", "pull_limit_wipe_fraction"}
            assert cp.retention_pull
            assert cp.pull_test_mating_factor == a.pull_test_mating_factor
            assert cp.pull_limit_wipe_fraction == a.pull_limit_wipe_fraction


J_NAMES = ("spiral_rcc_verify", "spiral_rcc_verify_reject", "spiral_rcc_verify_research", "spiral_rcc_verify_reject_no_rcc")


def test_j_is_f_with_cs_verify():
    """v0.2d: J runs F's settings and code up to the hand-over, then C's own VERIFY code with C's settings."""
    from dataclasses import asdict

    from defex.config import AdaptiveConfig
    from defex.control.adaptive_fsm import AdaptiveInsertionController
    from defex.control.spiral_search import CompliantSpiralSearchController, SpiralSearchController
    from defex.control.spiral_verify import CompliantSpiralSearchVerifyController, _Verifier

    f = make_controller("spiral_rcc")
    for name in J_NAMES:
        j = make_controller(name)
        assert j.compliant_wrist and isinstance(j, CompliantSpiralSearchController)
        assert asdict(j.cfg) == asdict(f.cfg) and asdict(j.stiff_fixture_cfg) == asdict(f.stiff_fixture_cfg)
        assert type(j.verifier) is _Verifier and asdict(j.verifier.cfg) == asdict(AdaptiveConfig())
    assert make_controller("spiral_rcc_verify").on_verify_fail == "research"  # the selection rule's pick
    assert make_controller("spiral_rcc_verify").rcc_terms
    assert make_controller("spiral_rcc_verify_reject").on_verify_fail == "reject"
    assert make_controller("spiral_rcc_verify_research").on_verify_fail == "research"
    assert not make_controller("spiral_rcc_verify_reject_no_rcc").rcc_terms
    # Reused, not reimplemented: J overrides only the hand-over points of F, the verifier only C's planner.
    f_methods = {k for cls in (CompliantSpiralSearchController, SpiralSearchController) for k, v in vars(cls).items()
                 if callable(v)}
    j_methods = {k for k, v in vars(CompliantSpiralSearchVerifyController).items() if callable(v)}
    assert j_methods & f_methods == {"__init__", "reset", "step", "_succeed"}
    c_methods = {k for k, v in vars(AdaptiveInsertionController).items() if callable(v)}
    assert {k for k, v in vars(_Verifier).items() if callable(v)} == {"__init__", "_plan_correction"} <= c_methods


def _ticks(task, ctrl, sc):
    ticks = []
    res = task.run(ctrl, sc, on_step=lambda s: ticks.append(
        (s.obs.t, s.obs.fixture_tcp.as_array(), s.obs.force.copy(), s.obs.torque.copy(), s.setpoint.as_array())))
    return res, ticks


def _assert_hands_over_where_f_seats(task, sc):
    rf, tf = _ticks(task, make_controller("spiral_rcc"), sc)
    assert rf.declared_success
    t_f = next(t for t, kind, _ in rf.events if kind == "finish")
    k = next(i for i, e in enumerate(rf.events) if e[1] == "seated")
    for name in J_NAMES:
        rj, tj = _ticks(task, make_controller(name), sc)
        assert rj.events[:k + 1] == rf.events[:k + 1]
        assert rj.events[k + 1][:2] == (t_f, "verify_handover")
        before = [x for x in tf if x[0] <= t_f]
        assert len(tj) > len(before) and [x[0] for x in tj[:len(before)]] == [x[0] for x in before]
        for a, b in zip(before, tj):
            for u, v in zip(a[1:4], b[1:4]):  # the observation: pose, force, torque
                assert np.array_equal(u, v)
            if a[0] < t_f:  # the command; at the hand-over tick J's first command is VERIFY's
                assert np.array_equal(a[4], b[4])


@pytest.mark.slow
@pytest.mark.parametrize("cond,i", [("nominal", 0), ("noise_1mm", 1), ("mf_nominal", 0)])
def test_j_hands_over_where_f_declares_seated(task, cond, i):
    """Floor contact (went straight in), a face contact then the spiral, and a latching part (gantry)."""
    from defex.tasks.conditions import latching_conditions_by_name
    from experiments.runner import nominal_socket_pose

    c = {**conditions_by_name(), **latching_conditions_by_name()}[cond]
    sc = sample_scenario(c, i, 2026, nominal_socket_pose(c, task.fixture))
    _assert_hands_over_where_f_seats(task, sc)


@pytest.mark.slow
def test_j_hands_over_where_f_declares_seated_on_the_arm():
    from defex.sim.arm_backend import MuJoCoArmBackend, menagerie_available
    from defex.tasks.insertion import InsertionTask
    from experiments.runner import nominal_socket_pose

    if not menagerie_available():
        pytest.skip("MuJoCo Menagerie UR5e not fetched")
    task = InsertionTask(backend=MuJoCoArmBackend())
    c = conditions_by_name()["noise_1mm"]
    _assert_hands_over_where_f_seats(task, sample_scenario(c, 1, 2026, nominal_socket_pose(c, task.fixture)))


@pytest.mark.slow
def test_j_after_a_failed_check_rejects_or_searches_again(task):
    """A broken latch fails the pull: (a) rejects; (b) gives F its second attempt, then rejects."""
    from defex.tasks.conditions import latching_conditions_by_name
    from experiments.runner import nominal_socket_pose

    c = latching_conditions_by_name()["mf_broken_latch"]
    sc = sample_scenario(c, 0, 2026, nominal_socket_pose(c, task.fixture))
    ra = task.run(make_controller("spiral_rcc_verify_reject"), sc)
    rb = task.run(make_controller("spiral_rcc_verify_research"), sc)
    for r in (ra, rb):
        assert r.declared_success is False and r.failure_reason == "aborted:verify_failed"
    kinds = lambda r: [k for _, k, _ in r.events]  # noqa: E731
    assert kinds(ra).count("verify_handover") == 1 and ra.retries == 0
    assert kinds(rb).count("verify_handover") == 2 and rb.retries == 1
    n = kinds(ra).index("abort")
    assert rb.events[:n] == ra.events[:n] and rb.events[n][1] == "retry"
