"""v0.2f friction diagnosis (post hoc): workcell reconstruction, the probe summary, the event classifier, seed guards."""

import sys

import mujoco
import numpy as np
import pytest

from defex.config import FixtureConfig, SimConfig
from defex.sim.arm_backend import menagerie_available
from experiments import friction_diagnosis_v02f as fd
from experiments import friction_diagnosis_v02f_classify as fc
from experiments import sim_randomization_v02f as sr

needs_arm = pytest.mark.skipif(not menagerie_available(), reason="UR5e model not fetched")


def test_simrand_source_is_the_run_variant():
    for k in (0, 4, 12):
        assert fd.build_variant("simrand", k) == sr.draw_variant(k, 20261205, "arm")
    assert fd.build_variant("nominal") == sr.draw_variant(0, 20261205, "arm")


def test_cone_source_changes_only_what_it_is_told():
    v = fd.build_variant("cone", cone="pyramidal")
    assert v.sim == SimConfig(cone="pyramidal") and v.fixture == FixtureConfig()
    assert (v.shoulder_elbow_scale, v.wrist_scale, v.arm_latency_s) == (1.0, 1.0, 0.006)
    assert v.k != 0  # make_task takes the non-nominal path, servo factors 1.0
    w = fd.build_variant("cone", cone="elliptic", impratio=1.0, friction_timeconst_s=0.002)
    assert w.sim == SimConfig(impratio=1.0, contact_friction_timeconst_s=0.002)


@needs_arm
def test_cone_task_compiles_the_requested_cone():
    task = fd.build_task("cone", cone="pyramidal")
    sc = fd.scenario_for(task, "friction_1", 0, 2026)
    task.run(sr.build_controller("fixed", "arm", "pinned"), sc)
    assert task.backend.model.opt.cone == mujoco.mjtCone.mjCONE_PYRAMIDAL
    assert np.allclose(task.backend.model.pair_friction[:, 0], 1.0)


def _arrays(phases, fy, sp_y, true_y):
    n = len(phases)
    a = {"phase": np.array(phases), "t": np.arange(n) * 0.002, "F": np.zeros((n, 3)), "sp_p": np.zeros((n, 3)),
         "true_p": np.zeros((n, 3)), "true_yaw": np.zeros(n), "true_rv": np.zeros((n, 3))}
    a["F"][:, 1] = fy
    a["sp_p"][:, 1] = sp_y
    a["true_p"][:, 1] = true_y
    for c in fd.CLASSES:
        a["c_" + c] = np.zeros((n, 9))
    a["c_floor"][:, 6] = [1.0, 2.0, 0.0, 3.0][:n]
    a["c_floor"][:, 7] = [1.0, 2.0, 0.0, 3.0][:n]
    return a


def test_probe_summary_reports_setpoint_and_plug_travel():
    a = _arrays(["preload", "probe_out", "probe_out", "probe_back"], [0.0, 0.0, -2.0, 0.0],
                [0.0, 0.0, 0.0003, 0.0], [0.0, 0.0, 0.00005, 0.0])
    (p,) = fd.probe_summary(a)
    assert p["dir"] == "+y" and p["ft_reaction_n"] == 2.0
    assert p["setpoint_travel_mm"] == pytest.approx(0.3) and p["true_travel_mm"] == pytest.approx(0.05)
    assert p["floor_N_max"] == 2.0 and p["floor_zero_ticks"] == 0.5


def test_classifier():
    seat = [[5.8, "detect", "seated_candidate [bottomed] depth=14.6 mm"], [7.8, "state", "RECOVER: verify_failed"]]
    assert fc.classify(seat, False) == "verify_reject"
    assert fc.classify(seat, True) == "seated"
    mouth = [[4.2, "detect", "surface_block [stall] depth=0.00 mm"], [6.4, "detect", "no_contact [stall]"]]
    assert fc.classify(mouth, False) == "mouth_stall"
    assert fc.classify([[5.8, "protective_stop", "|T|=0.65"]], False) == "other"


def test_trace_refuses_unnamed_seeds(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["x", "trace", "--seed", "20261123", "--index", "0"])
    with pytest.raises(SystemExit):
        fd.main()
    monkeypatch.setattr(sys, "argv", ["x", "trace", "--seed", "20261205", "--condition", "nominal", "--index", "0"])
    with pytest.raises(SystemExit):
        fd.main()
    with pytest.raises(SystemExit):
        fd.counts([20261205], ["friction_1"], ["adaptive"], 1, 1, fd.Path("/nonexistent"), ["elliptic_nominal"])


@needs_arm
@pytest.mark.slow
def test_pyramidal_floor_friction_stops_cs_wall_probe_dev_seed():
    """Dev seed 2026, friction_1 #0: under the pyramidal cone C's wall probes stop on floor friction."""
    task = fd.build_task("cone", cone="pyramidal")
    result, a = fd.run_trace(task, fd.scenario_for(task, "friction_1", 0, 2026), "adaptive")
    probes = fd.probe_summary(a)
    assert probes and min(p["true_travel_mm"] for p in probes) < 0.15
