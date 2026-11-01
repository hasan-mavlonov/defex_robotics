"""Checkpoint 2 prep: the arm contact prior and controller G on the UR5e."""

from dataclasses import asdict, replace

import pytest

from defex.config import LearnedPriorConfig
from defex.control.adaptive_learned import AdaptiveLearnedController
from defex.recovery.learned_prior import DEFAULT_MODEL_DIR, ContactPrior, find_model
from defex.sim.arm_backend import menagerie_available
from defex.tasks.conditions import conditions_by_name, latching_conditions_by_name
from defex.tasks.scenarios import sample_scenario
from defex.sim.backend import FixtureDynamics
from experiments.train_contact_prior import (
    characterized_fixture_dynamics,
    complete_fixture_dynamics,
    consistent_fixture_dynamics,
)

ARM_MODEL = DEFAULT_MODEL_DIR / "contact_prior_arm.json"
GANTRY_MODEL = DEFAULT_MODEL_DIR / "contact_prior_gantry.json"
needs_arm = pytest.mark.skipif(not (menagerie_available() and ARM_MODEL.exists()),
                               reason="needs the Menagerie UR5e (scripts/fetch_menagerie.py) and the arm model")
BLOCKING_ARM_TRIAL = ("noise_2mm", 3, 2026)  # development seed; C blocks once on the arm, then seats


@pytest.fixture(scope="module")
def arm_task():
    from defex.config import ConnectorSpec
    from defex.sim.arm_backend import MuJoCoArmBackend
    from defex.sim.backend import SceneParams
    from defex.tasks.insertion import InsertionTask
    from defex.utils.transforms import Pose

    be = MuJoCoArmBackend()
    spec = ConnectorSpec.load("rect_12x8")
    be.load(SceneParams(spec, spec.friction, Pose.identity()))
    return InsertionTask(backend=be)


def _fixture_after_trial(task, cond):
    from defex.control.registry import make_controller

    task.run(make_controller("fixed"), sample_scenario(cond, 0, 2026, task.backend.nominal_socket_pose))
    return task.backend.fixture_dynamics


def test_fixture_dynamics_agree_within_the_match_tolerance():
    tol = LearnedPriorConfig().fixture_match_rel_tol
    a = {"translational_stiffness_n_per_mm": 8.0086, "effective_mass_kg": 6.3222, "following_lag_s": 0.2,
         "tilt_stiffness_nm_per_rad": None}
    b = {**a, "effective_mass_kg": 6.3106}  # Micro-Fit vs generic plug on the arm: 0.2 %
    assert consistent_fixture_dynamics([a, b], tol) == a
    with pytest.raises(SystemExit):
        consistent_fixture_dynamics([a, {**a, "effective_mass_kg": 6.0}], tol)
    with pytest.raises(SystemExit):
        consistent_fixture_dynamics([a, {k: v for k, v in a.items() if k != "following_lag_s"}], tol)


def test_models_are_only_written_with_characterized_fixture_dynamics():
    """Checkpoint 2 review: the pipeline accepted None (not characterized), giving a model G never uses."""
    full = asdict(FixtureDynamics(8.0, 400.0, 6.3, 0.006, 822.0, 0.2, 0.2))
    assert characterized_fixture_dynamics(full) == full
    for bad in ({**full, "tilt_stiffness_nm_per_rad": None},
                {k: v for k, v in full.items() if k != "rotational_following_lag_s"},
                {**full, "unknown_field_s": 1.0}, None):
        with pytest.raises(SystemExit):
            characterized_fixture_dynamics(bad)


def test_completing_a_model_adds_missing_fields_and_checks_the_stored_ones():
    tol = LearnedPriorConfig().fixture_match_rel_tol
    measured = [asdict(FixtureDynamics(10.0, 15.0, 0.884, 0.0, 15.0, 0.0367, 0.0244)),
                asdict(FixtureDynamics(10.0, 15.0, 0.881, 0.0, 15.0, 0.0367, 0.0244))]
    w9 = {"translational_stiffness_n_per_mm": 10.0, "yaw_stiffness_nm_per_rad": 15.0, "effective_mass_kg": 0.884,
          "command_latency_s": 0.0}  # stored before W5b added the servo terms
    done, added = complete_fixture_dynamics(w9, measured, tol)
    assert added == ["tilt_stiffness_nm_per_rad", "following_lag_s", "rotational_following_lag_s"]
    assert {k: done[k] for k in w9} == w9 and characterized_fixture_dynamics(done) == done
    with pytest.raises(SystemExit):  # a stored value the backend contradicts is never overwritten
        complete_fixture_dynamics({**w9, "yaw_stiffness_nm_per_rad": 400.0}, measured, tol)


@needs_arm
@pytest.mark.slow
def test_arm_model_matches_the_arm_for_both_connectors_and_not_the_gantry(arm_task, task):
    model = ContactPrior.from_json(ARM_MODEL)
    assert model.backend == "arm" and model.integration_weight is not None
    assert {"tilt_stiffness_nm_per_rad", "following_lag_s", "rotational_following_lag_s"} <= set(model.fixture_dynamics)
    meta = model.data["metadata"]
    assert meta["train_base_seeds"] == [3001, 3030] and meta["validation_base_seed"] == 4001
    for cond in (conditions_by_name()["noise_1mm"], latching_conditions_by_name()["mf_noise_1mm"]):
        fd = _fixture_after_trial(arm_task, cond)
        assert model.matches(fd, LearnedPriorConfig().fixture_match_rel_tol), (cond.name, asdict(fd))
        found = find_model(fd)
        assert found is not None and found.backend == "arm"
    gantry_fd = task.backend.fixture_dynamics
    assert not model.matches(gantry_fd, LearnedPriorConfig().fixture_match_rel_tol)
    if GANTRY_MODEL.exists():
        assert find_model(gantry_fd).backend == "gantry"
        assert not ContactPrior.from_json(GANTRY_MODEL).matches(fd, LearnedPriorConfig().fixture_match_rel_tol)
    # A different servo lag alone is enough to refuse the arm model.
    assert not model.matches(replace(fd, following_lag_s=fd.following_lag_s * 0.5), 0.01)
    assert not model.matches(replace(fd, rotational_following_lag_s=fd.rotational_following_lag_s * 0.5), 0.01)


@needs_arm
@pytest.mark.slow
def test_g_uses_the_arm_model_on_the_arm(arm_task):
    cond = conditions_by_name()[BLOCKING_ARM_TRIAL[0]]
    sc = sample_scenario(cond, BLOCKING_ARM_TRIAL[1], BLOCKING_ARM_TRIAL[2], arm_task.backend.nominal_socket_pose)
    g = AdaptiveLearnedController()
    res = arm_task.run(g, sc)
    assert g.prior is not None and g.prior.backend == "arm"
    assert g.prior_weight == ContactPrior.from_json(ARM_MODEL).integration_weight > 0
    used = [r for r in g.contact_records if "learned_mean_mm" in r]
    assert used and all(r["kind"] == "surface_block" for r in used)
    assert any(e[1] == "learned_prior" and "contact_prior_arm.json" in e[2] for e in res.events)
