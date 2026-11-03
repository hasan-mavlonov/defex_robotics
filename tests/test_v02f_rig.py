import csv
import importlib.util
import math
from pathlib import Path

import numpy as np
import pytest

from experiments import v02f_rig_power as pw
from experiments.checkpoint_report import mcnemar

ROOT = Path(__file__).resolve().parents[1]


def tables():
    spec = importlib.util.spec_from_file_location("v02f_tables", ROOT / "results/v0.2f_rig_predictions/tables.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_critical_value_matches_the_benchmarks_mcnemar():
    for d in range(1, 120):
        m = pw.critical(d)
        for b in range(d + 1):
            assert (min(b, d - b) <= m) == (mcnemar(b, d - b) <= 0.05), (d, b)


def test_power_matches_monte_carlo():
    rng = np.random.default_rng(7)
    n, p10, p01 = 300, 0.03, 0.01
    hits = 0
    for _ in range(3000):
        u = rng.random(n)
        b = int((u < p10).sum())
        c = int(((u >= p10) & (u < p10 + p01)).sum())
        hits += mcnemar(b, c) <= 0.05
    assert abs(hits / 3000 - pw.power(n, p10, p01)) < 0.03


def test_power_edges_and_sample_size():
    assert pw.power(0, 0.1, 0.0) == 0.0
    assert pw.power(100, 0.0, 0.0) == 0.0
    assert pw.n_for_power(0.01, 0.01) is None
    # 0 against p: rejection needs 6 one-sided discordant pairs; 80% power at about n p = 8.
    n = pw.n_for_power(0.0, 0.016)
    assert 450 <= n <= 560
    assert pw.power(n, 0.0, 0.016) >= 0.8
    assert pw.power(100, 0.0, 0.016) < 0.05


def test_normal_branch_is_continuous_with_the_exact_one():
    d = pw.NORMAL_D
    exact = pw.reject_given_d(d, 0.47)
    pw_normal = pw.NORMAL_D
    try:
        pw.NORMAL_D = d - 1
        approx = pw.reject_given_d(d, 0.47)
    finally:
        pw.NORMAL_D = pw_normal
    assert abs(exact - approx) < 0.02


def test_wilson_zero_bound():
    assert pw.wilson_upper_zero(100) == pytest.approx(tables().wilson(0, 100)[1])
    n = pw.n_for_zero_upper(0.016)
    assert pw.wilson_upper_zero(n) < 0.016 <= pw.wilson_upper_zero(n - 1)


def test_newcombe_paired_reproduces_the_published_example():
    # Newcombe (1998), Stat. Med. 17:2635, paired example a=36, b=12, c=2, d=0: method 10 gives 0.0569 to 0.3404.
    t, lo, hi = tables().newcombe_paired(36, 12, 2, 0)
    assert t == pytest.approx(0.2)
    assert lo == pytest.approx(0.0569, abs=1e-4)
    assert hi == pytest.approx(0.3404, abs=1e-4)


def test_classify():
    cl = tables().classify
    assert cl(-0.03, 0.04, (-0.05, 0.05), 0.0) == "agrees"
    assert cl(0.01, 0.04, (-0.05, 0.05), 0.0) == "agrees"
    assert cl(0.02, 0.09, (-0.05, 0.05), 0.0) == "disagrees"
    assert cl(-0.02, 0.09, (-0.05, 0.05), 0.0) == "inconclusive"
    assert cl(0.85, 1.2, (0.8, 1.25), 1.0) == "agrees"
    assert cl(1.3, 1.6, (0.8, 1.25), 1.0) == "disagrees"


FIELDS = ["controller", "condition", "group", "trial_index", "success", "protective_stop", "declared_success",
          "cycle_time_s", "final_depth_mm", "final_tilt_deg", "final_yaw_deg"]


def write(folder, rows):
    folder.mkdir(parents=True)
    with (folder / "trials.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, FIELDS)
        w.writeheader()
        w.writerows(rows)


def r(ctrl, i, ok, cond="noise_2mm", group="pose_uncertainty", esc=False, cycle=5.0):
    return {"controller": ctrl, "condition": cond, "group": group, "trial_index": str(i), "success": str(ok),
            "protective_stop": "False", "declared_success": "True" if ok or esc else "False",
            "cycle_time_s": str(cycle), "final_depth_mm": "15.0", "final_tilt_deg": "0.2", "final_yaw_deg": "3.4"}


def test_prediction_tables_and_rig_comparison(tmp_path):
    t = tables()
    sim = tmp_path / "sim"
    rows = [r("adaptive", i, True) for i in range(10)] + \
        [r("spiral_rcc_pull", i, i >= 2, esc=i < 2) for i in range(10)] + \
        [r("adaptive", i, True, cond="friction_1") for i in range(10)]  # not a protocol condition: dropped
    write(sim / "gantry_standard", rows)
    loaded = t.load(sim)
    assert len(loaded) == 20
    out = "\n".join(t.prediction_tables(loaded, sim))
    assert "| gantry | C | 10/10" in out
    assert "| gantry | I | 8/10" in out and "2/10" in out
    assert "| gantry | housing-only | I | bad units | 0 / 2 of 10 | 0 / 2 |" in out
    assert "| gantry | housing-only | I | 2 | 2 | 0 / 2 | 3.40-3.40 |" in out
    rig = tmp_path / "rig"
    write(rig / "gantry_standard", [r("adaptive", i, i != 0, cycle=5.5) for i in range(10)])
    cmp = "\n".join(t.compare_tables(loaded, t.load(rig)))
    assert "| gantry | housing-only | C | success | 9 / 10 of 10 |" in cmp
    assert "cycle p50" in cmp


def test_power_report_runs_on_the_committed_benchmarks():
    if not (ROOT / "results/benchmark_v0.2e/gantry_standard/trials.csv").exists():
        pytest.skip("benchmark rows not present")
    pairs = pw.load_pairs(ROOT / "results/benchmark_v0.2e")
    d = pairs[("gantry", "standard", "spiral_rcc_pull")]
    # benchmark_v0.2e REPORT.md: gantry standard, C 0 bad units, I 32, of 2,000.
    assert d["n"] == 2000 and d["ecc"] == 0 and d["eco"] == 32
    assert math.isclose(d["sc"] / d["n"], 0.991, abs_tol=0.0005)
