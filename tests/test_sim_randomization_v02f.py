"""v0.2f simulator randomization: variant draws, arm servo scaling, G pinning, equivalence with
experiments.robustness on variant 0, and the pre-registered decision rules."""

import json
import math

import pytest

from defex.config import FixtureConfig, SimConfig
from defex.control.base import outside_reference_family
from defex.sim.arm_backend import menagerie_available
from defex.sim.backend import SceneParams
from defex.tasks.conditions import conditions_by_name
from defex.tasks.scenarios import sample_scenario
from experiments import sim_randomization_v02f as sr
from experiments import sim_randomization_v02f_tables as tb
from experiments.runner import nominal_socket_pose
from experiments.sim_randomization import BANDS

needs_arm = pytest.mark.skipif(not menagerie_available(), reason="UR5e model not fetched")


def test_variant_zero_is_nominal_on_both_machines():
    for backend in ("gantry", "arm"):
        v = sr.draw_variant(0, 2026, backend)
        assert v.sim == SimConfig() and v.fixture == FixtureConfig()
        assert (v.shoulder_elbow_scale, v.wrist_scale) == (1.0, 1.0)
    assert sr.draw_variant(0, 1, "arm").arm_latency_s == 0.006


def test_gantry_draws_reproduce_v02a_variants():
    """Same bands, same draw: seed 20261108 gives results/sim_randomization_v0.2/variants.json."""
    old = json.loads((sr.REPO_ROOT / "results" / "sim_randomization_v0.2" / "variants.json").read_text())
    for rec in old["variants"][1:]:
        p = sr.draw_variant(rec["variant"], 20261108, "gantry").params("gantry")
        for k, x in rec.items():
            if k in ("variant", "nominal"):
                continue
            assert p[k] == pytest.approx(x, rel=1e-12) if k != "cone" else p[k] == x


def test_draws_within_bands_and_arm_shares_contact_draw():
    for k in range(1, 40):
        g = sr.draw_variant(k, 7, "gantry").params("gantry")
        a = sr.draw_variant(k, 7, "arm").params("arm")
        for name in sr.CONTACT:
            assert g[name] == a[name]
        for name, (lo, hi) in BANDS.items():
            assert lo <= g[name] <= hi
        for name, (lo, hi) in sr.ARM_BANDS.items():
            assert lo <= a[name] <= hi
        assert sr.draw_variant(k, 7, "arm").fixture == FixtureConfig()  # no gantry servo draw on the arm


def test_parse_cells():
    assert sr.parse_cells("standard:nominal:3,latching:mf_noise_1mm:2") == [("standard", "nominal", 3),
                                                                            ("latching", "mf_noise_1mm", 2)]
    with pytest.raises(SystemExit):
        sr.parse_cells("standard:mf_noise_1mm:2")


def _load_nominal(be):
    c = conditions_by_name()["nominal"]
    s = sample_scenario(c, 0, 2026, nominal_socket_pose(c, FixtureConfig()))
    be.load(SceneParams(s.connector, s.friction, s.socket_pose))


@needs_arm
def test_arm_servo_scaling_reaches_the_model_and_the_reported_dynamics():
    from defex.sim.arm_backend import MuJoCoArmBackend

    nominal = MuJoCoArmBackend()
    _load_nominal(nominal)
    v = sr.Variant(3, SimConfig(), FixtureConfig(), 0.004, 2.0, 0.5)
    be = sr.make_arm_backend(v)
    _load_nominal(be)
    _load_nominal(be)  # cached model: scaled once only
    for n in sr.SHOULDER_ELBOW + sr.WRIST:
        s = 2.0 if n in sr.SHOULDER_ELBOW else 0.5
        a0, a = nominal.model.actuator("ur_" + n).id, be.model.actuator("ur_" + n).id
        assert be.model.actuator_gainprm[a, 0] == pytest.approx(s * nominal.model.actuator_gainprm[a0, 0])
        assert be.model.actuator_biasprm[a, 1] == pytest.approx(s * nominal.model.actuator_biasprm[a0, 1])
        assert be.model.actuator_biasprm[a, 2] == pytest.approx(math.sqrt(s) * nominal.model.actuator_biasprm[a0, 2])
    fd0, fd = nominal.fixture_dynamics, be.fixture_dynamics
    assert fd.command_latency_s == 0.004
    # Yaw: wrist_3 (x 0.5) in series with the stiffer shoulder and elbow (x 2): between the two.
    assert 0.5 * fd0.yaw_stiffness_nm_per_rad < fd.yaw_stiffness_nm_per_rad < fd0.yaw_stiffness_nm_per_rad
    assert fd.following_lag_s != fd0.following_lag_s


@needs_arm
def test_every_arm_band_corner_stays_outside_the_gantry_family():
    """The controllers keep their arm settings on every arm variant (and the gantry ones on every gantry)."""
    from defex.config import AdaptiveConfig
    from defex.control.base import ControllerContext
    from defex.config import SensorNoiseConfig
    from defex.utils.transforms import Pose

    c = conditions_by_name()["nominal"]
    spec = sample_scenario(c, 0, 2026, nominal_socket_pose(c, FixtureConfig())).connector
    cfg = AdaptiveConfig()
    for se in (0.5, 2.0):
        for w in (0.5, 2.0):
            be = sr.make_arm_backend(sr.Variant(1, SimConfig(), FixtureConfig(), 0.008, se, w))
            _load_nominal(be)
            ctx = ControllerContext(spec, Pose.identity(), Pose.identity(), 0.002, FixtureConfig(),
                                    SensorNoiseConfig(), fixture_dynamics=be.fixture_dynamics)
            assert outside_reference_family(ctx, cfg.stiff_wrist_min_ratio, cfg.lagging_servo_min_ratio)


@needs_arm
def test_pinned_g_keeps_its_model_on_a_randomized_arm():
    from defex.recovery.learned_prior import find_model

    be = sr.make_arm_backend(sr.draw_variant(1, 2026, "arm"))
    _load_nominal(be)
    assert find_model(be.fixture_dynamics) is None  # as built, G would run as C here
    g = sr.make_g_pinned("arm")
    assert g.model_path.name == "contact_prior_arm.json"
    assert g.prior_cfg.fixture_match_rel_tol == math.inf


@pytest.mark.slow
@pytest.mark.parametrize("backend", ["gantry", pytest.param("arm", marks=needs_arm)])
def test_variant_zero_rows_equal_robustness_rows(tmp_path, backend, monkeypatch):
    from experiments.runner import run_suite

    monkeypatch.setenv("DEFEX_BACKEND", backend)
    conds = [conditions_by_name()["noise_2mm"]]
    ctrls = ["adaptive", "spiral_rcc_pull", "adaptive_learned"]
    ref = run_suite(conds, ctrls, 2, 2026, 1, tmp_path / "rob", progress=False)
    rows = sr.run(backend, [("standard", "noise_2mm", 2)], ctrls, [0], 2026, 1, tmp_path / "v02f")
    assert sr.compare_rows(rows, [r.to_row() for r in ref]) == []


def _row(ctrl, cond, i, success, escape=False, v=0):
    return {"variant": str(v), "controller": ctrl, "condition": cond, "trial_index": str(i),
            "success": str(success), "protective_stop": "False",
            "declared_success": "True" if (success or escape) else "False"}


def test_rules_are_symmetric_and_ties_do_not_hold():
    assert tb.holds("better", 3, 1) and not tb.holds("better", 1, 3) and not tb.holds("better", 2, 2)
    assert tb.holds("worse", 1, 3) and not tb.holds("worse", 3, 1) and not tb.holds("worse", 2, 2)
    assert tb.holds("n.s.", 3, 1) and not tb.holds("n.s.", 9, 0) and not tb.holds("n.s.", 0, 9)
    assert tb.classify(9, 0) == "better" and tb.classify(0, 9) == "worse" and tb.classify(4, 3) == "n.s."


def test_escape_and_paired_counts():
    rows = {}
    for i in range(10):
        rows[(0, "adaptive", "noise_2mm", i)] = _row("adaptive", "noise_2mm", i, i < 8)
        rows[(0, "spiral_rcc_pull", "noise_2mm", i)] = _row("spiral_rcc_pull", "noise_2mm", i, i < 5, escape=i >= 7)
    conds = [("standard", "noise_2mm")]
    assert tb.paired(rows, conds, "C", "I", "success", 0) == (3, 0, 10, 8, 5)
    assert tb.paired(rows, conds, "C", "I", "bad_units", 0) == (3, 0, 10, 0, 3)
    up, dn, p = tb.scenario_sign_test(rows, conds, "C", "I", "success", [0])
    assert (up, dn) == (3, 0) and p == pytest.approx(0.25)


def test_scenario_sign_test_counts_scenarios_not_variant_pairs():
    rows = {}
    for v in (1, 2, 3):
        for i in range(2):
            rows[(v, "adaptive", "nominal", i)] = _row("adaptive", "nominal", i, True, v=v)
            rows[(v, "spiral_rcc", "nominal", i)] = _row("spiral_rcc", "nominal", i, not (i == 0 and v < 3), v=v)
    up, dn, _ = tb.scenario_sign_test(rows, [("standard", "nominal")], "C", "F", "success", [1, 2, 3])
    assert (up, dn) == (1, 0)


def test_references_from_benchmark_v02e_are_the_preregistered_ones():
    root = sr.REPO_ROOT / "results" / "benchmark_v0.2e"
    if not (root / "gantry_standard" / "trials.csv").exists():
        pytest.skip("benchmark_v0.2e rows not present")
    refs = tb.references(root)
    assert refs[("gantry", "c_favourable", "bad_units", "C", "I")][:3] == ("better", 32, 0)
    assert refs[("arm", "latching_good", "success", "C", "F")][:3] == ("worse", 18, 37)
    assert refs[("gantry", "c_unfavourable", "success", "C", "F")][0] == "worse"
    assert refs[("gantry", "latching_good", "success", "C", "F")][0] == "n.s."


def test_tables_run_on_the_development_timing_slice(capsys):
    root = sr.REPO_ROOT / "results" / "sim_randomization_v0.2f" / "dev_timing"
    if not (root / "gantry" / "trials.csv").exists():
        pytest.skip("development slice not present")
    tb.main([root])
    out = capsys.readouterr().out
    assert "## Verdicts" in out and "## Controls" in out
