"""v0.2c integration: the merged rule sets switch on where each workstream meant them to, together."""

from __future__ import annotations

import csv
from dataclasses import replace
from pathlib import Path

from defex.config import AdaptiveConfig, ConnectorSpec, FixtureConfig, SensorNoiseConfig
from defex.control.adaptive_fsm import AdaptiveInsertionController
from defex.control.base import ControllerContext
from defex.sim.backend import FixtureDynamics
from defex.utils.transforms import Pose

ARM = FixtureDynamics(8.0, 400.0, 6.32, 0.006, tilt_stiffness_nm_per_rad=822.0, following_lag_s=0.2,
                      rotational_following_lag_s=0.2)
GANTRY = FixtureDynamics(10.0, 15.0, 0.88, 0.0)
ROBUSTNESS = ("_cavity_tilt", "_floor_impact", "_reaim_verify", "_unjam", "_rate_conform")


def _c(connector: str, fd: FixtureDynamics, cfg: AdaptiveConfig | None = None) -> AdaptiveInsertionController:
    c = AdaptiveInsertionController(cfg)
    c.reset(ControllerContext(ConnectorSpec.load(connector), Pose.identity(), Pose.identity(), 0.002, FixtureConfig(),
                              SensorNoiseConfig(), fixture_dynamics=fd))
    return c


def test_arm_latching_part_runs_both_rule_sets():
    c = _c("microfit3_4ckt", ARM)
    assert c._verdict
    assert all(getattr(c, a) for a in ROBUSTNESS)
    assert c.monitor.timeout_s > c.cfg.insert_timeout_s  # scaled insert timeout (W5 speed scale < 1 on the arm)
    assert c._wall_reprobes_left == c.cfg.wall_yaw_reprobes


def test_gantry_latching_part_runs_only_the_verdict():
    c = _c("microfit3_4ckt", GANTRY)
    assert c._verdict
    assert not any(getattr(c, a) for a in ROBUSTNESS)
    assert c.monitor.timeout_s == c.cfg.insert_timeout_s


def test_arm_housing_only_part_runs_only_the_arm_rules():
    c = _c("rect_12x8", ARM)
    assert not c._verdict
    assert all(getattr(c, a) for a in ROBUSTNESS)


def test_switches_turn_each_set_off_independently():
    off = replace(AdaptiveConfig(), defect_verdict=False, cavity_tilt_compliance=False, settle_floor_impact=False,
                  reaim_after_verify_fail=False, unjam_in_cavity=False, scale_insert_timeout=False)
    c = _c("microfit3_4ckt", ARM, off)
    assert not c._verdict
    assert not any(getattr(c, a) for a in ("_cavity_tilt", "_floor_impact", "_reaim_verify", "_unjam"))
    assert c.monitor.timeout_s == c.cfg.insert_timeout_s


def _write(path: Path, rows: list[dict]) -> None:
    path.mkdir(parents=True)
    with (path / "trials.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def _row(ctrl, cond, i, success, wall="1.0", declared=None, stop="False"):
    return {"controller": ctrl, "condition": cond, "trial_index": str(i), "seed": "7", "success": success,
            "declared_success": declared if declared is not None else success, "gt_seated": success,
            "protective_stop": stop, "cycle_time_s": "5.0", "wall_time_s": wall}


def test_integration_compare_matches_common_trials_and_ignores_wall_time(tmp_path):
    from experiments.v02c_integration_compare import compare, mcnemar

    a = [_row("adaptive", "noise_1mm", i, "True") for i in range(3)] + [_row("adaptive", "mf_broken_latch", 0, "False")]
    b = [_row("adaptive", "noise_1mm", i, "True" if i else "False", wall="9.9") for i in range(5)]
    b += [_row("adaptive", "mf_broken_latch", 0, "False", declared="True")]
    _write(tmp_path / "a", a)
    _write(tmp_path / "b", b)
    line = [x for x in compare(tmp_path / "a", tmp_path / "b", None) if x.startswith("| adaptive")][0]
    cells = [c.strip() for c in line.split("|")]
    assert cells[2] == "4" and cells[3] == "2"  # 4 common trials; trial 0 and the bad part differ
    assert cells[4].startswith("3 / 2 of 3 (1 / 0")
    assert cells[5] == "0 / 1 of 1"  # the bad part passed as good on side B only
    assert mcnemar(0, 0) == 1.0 and abs(mcnemar(0, 6) - 0.03125) < 1e-12


def test_prior_output_root_follows_the_environment(monkeypatch):
    import importlib

    import experiments.train_contact_likelihood as tcl

    monkeypatch.setenv("DEFEX_PRIOR_OUT", "results/v0.2c_integration/prior")
    assert importlib.reload(tcl).OUT.parts[-2:] == ("v0.2c_integration", "prior")
    monkeypatch.delenv("DEFEX_PRIOR_OUT")
    assert importlib.reload(tcl).OUT.name == "v0.2c_learned_prior"


def test_installed_models_state_every_fixture_field_and_their_selection():
    import json

    from defex.recovery.learned_prior import DEFAULT_MODEL_DIR
    from experiments.train_contact_prior import characterized_fixture_dynamics

    for backend in ("gantry", "arm"):
        data = json.loads((Path(DEFAULT_MODEL_DIR) / f"contact_prior_{backend}.json").read_text())
        characterized_fixture_dynamics(data["fixture_dynamics"])  # raises on a missing or unset field
        assert data["backend"] == backend
    gantry = json.loads((Path(DEFAULT_MODEL_DIR) / "contact_prior_gantry.json").read_text())
    if gantry.get("format") is not None and "selection_rule" in gantry.get("metadata", {}):
        assert gantry["metadata"]["selection_rule"].endswith("SELECTION_RULE.md")


def test_variants_reach_the_config_each_machine_runs(tmp_path, monkeypatch):
    """Review fix: a D/E/F variant also changes the arm's stiff_fixture_cfg, and A/B pick up a dwell override."""
    import json

    from defex.control.registry import make_controller

    path = tmp_path / "variants.json"
    path.write_text(json.dumps({"v": {"insert_speed_mm_s": 1.5}, "d": {"dwell_s": 0.7}}))
    monkeypatch.setenv("DEFEX_CONTROLLER_VARIANTS", str(path))
    for name in ("spiral", "correction_rcc", "spiral_rcc"):
        ctrl = make_controller(f"{name}@v")
        assert ctrl.cfg.insert_speed_mm_s == 1.5 and ctrl.stiff_fixture_cfg.insert_speed_mm_s == 1.5
    for name in ("fixed", "correction"):
        ctrl = make_controller(f"{name}@d")
        assert ctrl.dwell_s == 0.7
