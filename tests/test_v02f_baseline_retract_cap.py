"""v0.2f: C's gentle-retract cap on the fair spiral baselines (results/v0.2f_baseline_retract_cap).

SpiralSearchConfig.retract_pull_cap: on a latching part, a retract pull past
AdaptiveConfig.retract_pull_cap_fraction x the protective stop (36 N on the Micro-Fit) stops pulling.
The first hold on a retry retract re-seats the plug and runs INSERT's seat rule again; a second hold, or a
hold on the failure retract, leaves the plug in place and fails the part.
"""

from __future__ import annotations

import json
from dataclasses import replace

import numpy as np
import pytest

from defex.config import MM, AdaptiveConfig, ConnectorSpec, FixtureConfig, SensorNoiseConfig
from defex.control.base import ControllerContext
from defex.control.registry import make_controller
from defex.perception.state_estimator import Observation
from defex.utils.transforms import Pose

BASELINES = ("spiral", "spiral_rcc", "spiral_pull", "spiral_rcc_pull", "spiral_rcc_verify")


def _ctrl(name: str = "spiral_pull", cap: bool = True, connector: str = "microfit3_4ckt"):
    spec = ConnectorSpec.load(connector) if connector else ConnectorSpec()
    ctx = ControllerContext(spec, Pose.identity(), Pose.identity(), 0.002, FixtureConfig(), SensorNoiseConfig())
    c = make_controller(name)
    c.cfg = replace(c.cfg, retract_pull_cap=cap)
    c.stiff_fixture_cfg = replace(c.stiff_fixture_cfg, retract_pull_cap=cap)
    c.reset(ctx)
    c.S = c.G = ctx.home_pose
    c.t_start = 0.0
    c.face_depth = 0.2 * MM
    c.attempts = 1
    return c


def _obs(t: float, depth_mm: float, f_ax: float) -> Observation:
    p = Pose(np.array([0.0, 0.0, -depth_mm * MM]), np.eye(3))
    z3 = np.zeros(3)
    return Observation(t, p, p, p, Pose.identity(), Pose.identity(), p, depth_mm * MM, np.zeros(2),
                       np.array([0.0, 0.0, f_ax]), z3, z3, z3, True)


def _retry(c, t: float = 0.0):
    c._jam_or_fail(_obs(t, 7.9, 0.0), "excess_torque")
    assert c.state == "APPROACH" and c._retry_retract


@pytest.mark.parametrize("name", BASELINES)
def test_flag_default_and_cap_value(name):
    c = make_controller(name)
    assert c.cfg.retract_pull_cap is False and c.stiff_fixture_cfg.retract_pull_cap is False
    k = _ctrl(name)
    a = AdaptiveConfig()
    assert k._cap_on and k._retract_pull_cap == pytest.approx(a.retract_pull_cap_fraction * 48.0) == 36.0


def test_cap_matches_c_on_the_same_connector():
    spec = ConnectorSpec.load("microfit3_4ckt")
    ctx = ControllerContext(spec, Pose.identity(), Pose.identity(), 0.002, FixtureConfig(), SensorNoiseConfig())
    cc = make_controller("adaptive")
    cc.reset(ctx)
    assert _ctrl()._retract_pull_cap == pytest.approx(cc._retract_pull_cap)


@pytest.mark.parametrize("name", ["spiral", "spiral_pull"])
def test_first_hold_on_a_retry_reseats_second_fails_in_place(name):
    c = _ctrl(name)
    _retry(c)
    c.step(_obs(0.002, 7.8, -30.0))  # below the cap: keeps backing out
    assert c.state == "APPROACH" and not c._no_retract
    c.step(_obs(0.004, 7.8, -37.0))
    assert c.state == "INSERT" and c._held_reseated and not c._no_retract
    assert c.z == pytest.approx(-7.8 * MM)
    assert ("gentle_retract", "held while backing out: re-seat and check") in [(e.kind, e.detail) for e in c.events]
    _retry(c, 0.006)
    c.step(_obs(0.008, 7.8, -37.0))
    assert c.state == "FAILURE" and c._fail_reason == "stuck_during_retract" and c._no_retract
    assert c.z == pytest.approx(-7.8 * MM)
    c.step(_obs(0.010, 7.8, -37.0))
    assert c.done and not c.declared_success and c.z == pytest.approx(-7.8 * MM)


def test_failure_retract_holds_the_plug():
    c = _ctrl("spiral_rcc_pull")
    c._fail(_obs(0.0, 7.9, -40.0), "retention_failed")
    assert c._no_retract and c.z == pytest.approx(-7.9 * MM)
    assert ("abort", "plug held while backing out: left in place") in [(e.kind, e.detail) for e in c.events]


@pytest.mark.parametrize("cap,connector", [(False, "microfit3_4ckt"), (True, "")])
def test_off_or_housing_only_never_holds(cap, connector):
    c = _ctrl("spiral", cap=cap, connector=connector)
    assert not c._cap_on
    _retry(c)
    c.step(_obs(0.002, 7.8, -45.0))
    assert c.state == "APPROACH" and not c._no_retract
    c._fail(_obs(0.004, 7.8, -45.0), "time_limit")
    assert not c._no_retract and c.z > 0.0


def test_reseated_h_runs_its_latch_check():
    c = _ctrl("spiral_pull")
    _retry(c)
    c.step(_obs(0.002, 7.9, -37.0))
    assert c.state == "INSERT"
    t = 0.002
    while c.state == "INSERT" and t < 1.0:
        t += 0.002
        c.step(_obs(t, 7.9, c.cfg.insert_force_n))
    assert c.state == "VERIFY" and c._pull_phase == "pull"


def test_variant_reaches_j_insertion(tmp_path, monkeypatch):
    f = tmp_path / "v.json"
    f.write_text(json.dumps({"cap": {"retract_pull_cap": True}}))
    monkeypatch.setenv("DEFEX_CONTROLLER_VARIANTS", str(f))
    for name in BASELINES:
        c = make_controller(f"{name}@cap")
        assert c.cfg.retract_pull_cap and c.stiff_fixture_cfg.retract_pull_cap


def _write_run(folder, rows, events):
    import csv
    import gzip

    folder.mkdir(parents=True)
    (folder / "config.json").write_text(json.dumps({"backend": folder.name.split("_")[0], "base_seed": 2026}))
    with (folder / "trials.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with gzip.open(folder / "events.json.gz", "wt") as fh:
        json.dump(events, fh)


def _row(ctrl, i, success="True", intact="True", depth="8.0"):
    return {"controller": ctrl, "condition": "mf_noise_1mm", "group": "latching", "trial_index": str(i),
            "success": success, "protective_stop": "False", "declared_success": "True" if success == "True" else "False",
            "final_latch_intact": intact, "final_depth_mm": depth, "failure_reason": "none", "wall_time_s": str(i + 0.5)}


def test_compare_counts_trips_tears_and_identity(tmp_path):
    from experiments.v02f_retract_cap_compare import compare

    trip = [[1.0, "gentle_retract", "pull 37.0 N above 36.0 N: stop pulling, plug held at 7.80 mm"]]
    rows = [_row("spiral", 0), _row("spiral@cap", 0),
            _row("spiral", 1, success="False", intact="False"), _row("spiral@cap", 1, depth="7.8")]
    ev = {"mf_noise_1mm|spiral|0": [], "mf_noise_1mm|spiral@cap|0": [],
          "mf_noise_1mm|spiral|1": [], "mf_noise_1mm|spiral@cap|1": trip}
    _write_run(tmp_path / "a" / "gantry_latch_spread_s2026", rows, ev)
    out, passed = compare(tmp_path / "a", "@cap")
    assert passed
    line = next(x for x in out if x.startswith("| gantry | latch_spread | D |"))
    assert "| 2 | 1 | 1 -> 2 of 2 (+1/-0) | 1 -> 0 (0) |" in line
    rows[1] = _row("spiral@cap", 0, depth="7.9")  # differs without a trip
    _write_run(tmp_path / "b" / "gantry_latching_s2026", rows, ev)
    out, passed = compare(tmp_path / "b", "@cap")
    assert not passed and any("differs without a trip" in x for x in out)


def test_compare_with_a_twin_folder(tmp_path):
    from experiments.v02f_retract_cap_compare import compare

    _write_run(tmp_path / "bench" / "arm_latching_s2026", [_row("spiral_pull", 0)], {"mf_noise_1mm|spiral_pull|0": []})
    _write_run(tmp_path / "unc" / "arm_latching_s2026", [_row("spiral_pull@nocap", 0)],
               {"mf_noise_1mm|spiral_pull@nocap|0": []})
    out, passed = compare(tmp_path / "bench", "", "@nocap", tmp_path / "unc")
    assert passed and any(x.startswith("| arm | latching | H | 1 | 0 |") for x in out)
