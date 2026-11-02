"""Review fix: C with every v0.2c switch off is Checkpoint 2's C (54f3097), on trials where the v0.2c rules matter.

Trials are the first ones (dev seed 2026, latching suite) where the committed integration snapshot's C differs
from the committed 54f3097 run; with the switches off the merged C must reproduce the 54f3097 row.
"""

from __future__ import annotations

import csv
import json
from dataclasses import replace
from pathlib import Path

import pytest

from defex.config import REPO_ROOT, AdaptiveConfig
from defex.control.adaptive_fsm import AdaptiveInsertionController
from defex.tasks.conditions import latching_conditions_by_name
from defex.tasks.scenarios import sample_scenario

RF = REPO_ROOT / "results/v0.2c_integration/review_fixes"
FIELDS = ("success", "failure_reason", "declared_success", "cycle_time_s", "retries", "final_depth_mm",
          "peak_contact_force_n")


def _rows(path: Path) -> dict[tuple, dict]:
    with path.open() as fh:
        return {(r["condition"], r["trial_index"]): r for r in csv.DictReader(fh) if r["controller"] == "adaptive"}


def _cases(backend: str, n: int = 2) -> list[tuple[str, int, dict]]:
    cp2 = _rows(RF / f"cp2_54f3097/{backend}_latching/trials.csv")
    snap = _rows(REPO_ROOT / f"results/v0.2c_integration/snapshot_seed2026/{backend}_latching/trials.csv")
    diff = [k for k in cp2 if k in snap and any(cp2[k][f] != snap[k][f] for f in FIELDS)]
    return [(c, int(i), cp2[(c, i)]) for c, i in diff[:n]]


def _all_off() -> AdaptiveConfig:
    return replace(AdaptiveConfig(), tilt_check=False, **json.loads((RF / "variants.json").read_text())["cp2"])


def _checkpoint2_budget(sc):
    """Checkpoint 2 ran with the Micro-Fit's old 30 N insert target (35.2 N since v0.2d)."""
    fb = replace(sc.connector.force_budget, insert_target_n=30.0)
    return replace(sc, connector=replace(sc.connector, force_budget=fb))


def _task(backend: str, monkeypatch):
    from defex.sim.arm_backend import menagerie_available
    from experiments import runner

    if backend == "arm" and not menagerie_available():
        pytest.skip("run scripts/fetch_menagerie.py")
    monkeypatch.setenv("DEFEX_BACKEND", backend)
    return runner.InsertionTask(backend=runner.make_backend())


@pytest.mark.slow
@pytest.mark.parametrize("backend", ["gantry", "arm"])
def test_all_v02c_switches_off_reproduce_checkpoint2(backend, monkeypatch):
    from experiments.runner import nominal_socket_pose

    cases = _cases(backend)
    assert cases, "the v0.2c rules should change some latching trials on seed 2026"
    task = _task(backend, monkeypatch)
    for cond, i, ref in cases:
        c = latching_conditions_by_name()[cond]
        sc = _checkpoint2_budget(sample_scenario(c, i, 2026, nominal_socket_pose(c, task.fixture)))
        r = task.run(AdaptiveInsertionController(_all_off()), sc).to_row()
        assert {f: str(r[f]) for f in FIELDS} == {f: ref[f] for f in FIELDS}, (cond, i)
