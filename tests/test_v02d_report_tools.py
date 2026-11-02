import csv
import gzip
import json
import sys

import pytest

from experiments import cp2_audit, v02c_paired, v02d_headline
from experiments.checkpoint_report import J, c_vs_fair, c_vs_fair_bad, defect_decision, j_decisions, j_vs, split

FIELDS = ["controller", "condition", "group", "trial_index", "success", "failure_reason", "gt_seated",
          "declared_success", "cycle_time_s", "final_depth_mm", "final_lateral_mm", "final_tilt_deg",
          "final_yaw_deg", "protective_stop", "peak_contact_force_n", "peak_measured_torque_nm"]


def row(ctrl, i, ok, cond="nominal", group="standard", escape=False, cycle=4.0):
    return {"controller": ctrl, "condition": cond, "group": group, "trial_index": str(i), "success": str(ok),
            "failure_reason": "none" if ok else "false_accept" if escape else "jam", "gt_seated": str(ok),
            "declared_success": "True" if ok or escape else "False", "cycle_time_s": str(cycle),
            "final_depth_mm": "14.5", "final_lateral_mm": "0.1", "final_tilt_deg": "3.5", "final_yaw_deg": "0.0",
            "protective_stop": "False", "peak_contact_force_n": "20", "peak_measured_torque_nm": "0.1"}


def cell(ctrl_ok: dict, n: int, **kw):
    """Rows for each controller: trial i succeeds iff i >= ctrl_ok[ctrl] (so failures are the first trials)."""
    return [row(c, i, i >= k, **kw) for c, k in ctrl_ok.items() for i in range(n)]


def write(folder, rows, summary=True, events=None):
    folder.mkdir(parents=True)
    with (folder / "trials.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, FIELDS)
        w.writeheader()
        w.writerows(rows)
    if summary:
        (folder / "summary.json").write_text("{}")
        (folder / "config.json").write_text(json.dumps({"base_seed": 99}))
    if events is not None:
        with gzip.open(folder / "events.json.gz", "wt") as fh:
            json.dump(events, fh)


def run(module, monkeypatch, capsys, *argv) -> str:
    monkeypatch.setattr(sys, "argv", ["x", *map(str, argv)])
    module.main()
    return capsys.readouterr().out


def test_j_vs_and_j_decisions():
    rows = cell({J: 0, "adaptive": 12, "spiral_rcc_pull": 0}, 40)
    s = j_vs(rows, "adaptive")
    assert s["k"] == {J: 40, "adaptive": 28} and (s["j_only"], s["other_only"]) == (12, 0) and s["p"] < 0.001
    assert j_vs(rows, "spiral_pull") is None
    out = j_decisions("x", rows)
    assert len(out) == 4 and "J ahead of C" in out[0] and "J matches I" in out[2]
    bad = [row(J, i, False, escape=i < 10) for i in range(20)] + [row("adaptive", i, False) for i in range(20)]
    out = j_decisions("x", bad, good=False)
    assert len(out) == 1 and "J passes more than C" in out[0]
    assert j_decisions("x", cell({"adaptive": 0, "spiral_rcc_pull": 0}, 5)) == []


def test_bad_part_rule_reports_c_passing_more():
    bad = [row("adaptive", i, False, escape=True) for i in range(20)]
    bad += [row("spiral_pull", i, False) for i in range(20)]
    assert c_vs_fair_bad(bad)["outcome"] == "more"
    assert "C passes more bad parts, p < 0.05" in defect_decision("x", bad)[0]


def test_c_vs_fair_single_baseline():
    rows = cell({"adaptive": 0, "spiral": 12, "spiral_rcc": 1}, 40)
    assert c_vs_fair(rows)["best"] == "spiral_rcc" and c_vs_fair(rows)["outcome"] == "matches"
    assert c_vs_fair(rows, ("spiral",))["outcome"] == "ahead"


def latching(ctrls_ok, ctrls_esc, n=20, nbad=10):
    good = cell(ctrls_ok, n, cond="mf_nominal", group="latching")
    bad = [row(c, i, False, cond="mf_broken_latch", group="bad_part", escape=i < k)
           for c, k in ctrls_esc.items() for i in range(nbad)]
    return good + bad


def test_split():
    rows = latching({"adaptive": 0}, {"adaptive": 0})
    good, bad = split("latching", rows)
    assert len(good) == 20 and len(bad) == 10
    assert split("standard", rows) == (rows, [])


def test_headline(tmp_path, monkeypatch, capsys):
    root = tmp_path / "bench"
    write(root / "gantry_standard", cell({"adaptive": 0, "spiral_rcc": 10, "spiral_rcc_pull": 10, J: 2}, 40))
    seated = {"adaptive": 8, "spiral_rcc": 0, "spiral_rcc_pull": 0, "spiral_pull": 1, J: 0}
    passed = {"adaptive": 0, "spiral_rcc": 9, "spiral_rcc_pull": 0, "spiral_pull": 0, J: 0}
    write(root / "gantry_latching", latching(seated, passed))
    write(root / "arm_standard", cell({"adaptive": 0, "spiral": 0}, 10), summary=False)  # unfinished: ignored
    out = run(v02d_headline, monkeypatch, capsys, root)
    assert "| arm," not in out and "arm_standard" not in out
    assert "| gantry, standard | 100.0% | F/I 75.0% | 0.002 | C ahead |" in out
    assert "| gantry, latching good parts | 60.0% | F/I 100.0% (H 95.0%) | 0.0078 (H: 0.016) | **C below** |" in out
    assert "| gantry, deliberately bad parts passed | 0 of 10 | H 0, I 0 of 10 | 1 | no difference |" in out
    assert "| gantry, standard | C | 38 / 40 of 40 | 0.5 |" in out
    assert "| gantry, latching | I | 20 / 20 of 20 | 1 | 0 / 0 of 20 | 1 | 0 / 0 of 10 | 1 |" in out
    assert "(d)" not in out
    other = tmp_path / "old"
    write(other / "gantry_standard", cell({"adaptive": 4, "spiral_rcc": 0}, 40))
    out = run(v02d_headline, monkeypatch, capsys, root, "--compare", other)
    assert "different seeds, not paired" in out
    assert "| Machine, suite | F | H | I | J | C |" in out
    assert "| gantry, standard | 75.0% / 100.0% |  | 75.0% / - | 95.0% / - | 100.0% / 90.0% |" in out


def test_headline_throughput():
    rows = [row("adaptive", i, i < 2, cycle=2.0 * (i + 1)) for i in range(3)]
    out = v02d_headline.throughput({("gantry", "standard"): rows})
    assert out[-1] == "| gantry, standard | 600 / 600 (3.00 s) |"


def test_headline_without_j(tmp_path, monkeypatch, capsys):
    root = tmp_path / "bench"
    write(root / "gantry_standard", cell({"adaptive": 0, "spiral_rcc": 10}, 40))
    out = run(v02d_headline, monkeypatch, capsys, root)
    assert "No J (spiral_rcc_verify) trials in this run." in out


@pytest.fixture
def paired_root(tmp_path):
    def make(with_j):
        root = tmp_path / ("j" if with_j else "nj")
        ctrls = {"adaptive": 0, "spiral_rcc_pull": 3, "spiral_pull": 5, **({J: 1} if with_j else {})}
        rows = cell(ctrls, 20)
        rows += [row("spiral_rcc_pull", 20 + i, False, escape=True) for i in range(2)]
        rows += [row(c, 20 + i, True) for c in ctrls if c != "spiral_rcc_pull" for i in range(2)]
        write(root / "gantry_standard", rows)
        return root
    return make


def test_paired_j_rows(paired_root, monkeypatch, capsys):
    without = run(v02c_paired, monkeypatch, capsys, paired_root(False))
    with_j = run(v02c_paired, monkeypatch, capsys, paired_root(True))
    assert "J" not in without.replace("# Paired comparisons for nj", "")
    assert "| Machine | C | G | D | F | H | I |" in without
    assert "## J against C and against I" in with_j and "| Machine | C | G | D | F | H | I | J |" in with_j
    assert "| gantry_standard, good parts | C | 22 | 21 / 22 | 0 / 1 | 1 | 0 / 0 | 1 |" in with_j
    assert "| gantry_standard, good parts | I | 22 | 21 / 17 | 4 / 0 | 0.12 | 0 / 2 | 0.5 |" in with_j
    c_table = [out.split("\n## ")[0].split("\n", 1)[1] for out in (without, with_j)]
    assert c_table[0] == c_table[1]


def test_audit_j_sections(tmp_path, monkeypatch, capsys):
    rows = [row("adaptive", 0, True), row("adaptive_learned", 0, False, escape=True),
            row(J, 0, False, escape=True), row(J, 1, True)]
    wy = "half free travel 0.5 mm (>= {} for 2.0 deg), levers (+4.6) mm -> PASS"
    events = {
        "nominal|adaptive_learned|0": [[1.0, "detect", "seated_candidate [bottomed] depth=7.11 mm Fax=27.1 N"]],
        f"nominal|{J}|0": [[1.0, "verify_handover", "F seated at 11.01 mm (face not touched): C's VERIFY"],
                           [2.0, "wall_yaw", wy.format(-0.1)]],
        f"nominal|{J}|1": [[2.0, "wall_yaw", wy.format(0.29)]],
    }
    write(tmp_path / "b" / "arm_standard", rows, events=events)
    out = run(cp2_audit, monkeypatch, capsys, tmp_path / "b")
    assert out.startswith("# Audit tables for b\n")
    assert "| arm_standard | G | nominal | 0 | 14.50 | 3.50 | 0.00 | [bottomed] depth=7.11 mm | not used |" in out
    assert ("| arm_standard | J | nominal | 0 | 14.50 | 3.50 | 0.00 | F seated at 11.01 mm (face not touched) | "
            "half free travel 0.5 mm (>= -0.1 for 2.0 deg) |") in out
    assert out.split("## Every bad unit J passed")[0].count("| J |") == 0
    assert "| arm_standard | J | 2 | 1 |" in out
    write(tmp_path / "c" / "arm_standard", [r for r in rows if r["controller"] != J], events={})
    out = run(cp2_audit, monkeypatch, capsys, tmp_path / "c")
    assert "bad unit J" not in out and "| J |" not in out and out.count("## ") == 2
