"""W9: learned contact prior (controller G) and C's contact records."""

import json
from dataclasses import asdict, replace

import numpy as np
import pytest

from defex.config import MM, LearnedPriorConfig, ConnectorSpec
from defex.control.adaptive_fsm import AdaptiveInsertionController
from defex.control.adaptive_learned import AdaptiveLearnedController
from defex.control.registry import CONTROLLERS, LABELS, make_controller
from defex.recovery.learned_prior import (
    DEFAULT_MODEL_DIR,
    FEATURE_SETS,
    ContactPrior,
    find_model,
    load_model,
    raw_features,
)
from defex.recovery.search_policy import HoleLocalizer
from defex.sim.backend import FixtureDynamics
from defex.tasks.conditions import conditions_by_name
from defex.tasks.scenarios import sample_scenario
from experiments.runner import nominal_socket_pose
from experiments.train_contact_prior import init_layers, loss_and_grads, model_json, standardize

BLOCKING_TRIAL = ("noise_2mm", 4, 2026)  # development seed; C blocks twice on this trial
ARM_LIKE = FixtureDynamics(8.0, 400.0, 6.3, 0.006, 822.0, 0.2, 0.2)  # UR5e values after W5b (tilt stiffness, servo lags)


@pytest.fixture(scope="module")
def c_run(task):
    cond = conditions_by_name()[BLOCKING_TRIAL[0]]
    sc = sample_scenario(cond, BLOCKING_TRIAL[1], BLOCKING_TRIAL[2], nominal_socket_pose(cond, task.fixture))
    ctl = AdaptiveInsertionController()
    return sc, ctl, task.run(ctl, sc)


def _synthetic_model(tmp_path, records, fixture_dynamics, weight=0.5, name="contact_prior_test.json"):
    names = FEATURE_SETS["contact"]
    x = np.array([[raw_features(r)[n] for n in names] for r in records])
    x_mean, x_std = standardize(x)
    layers = init_layers(np.random.default_rng(0), len(names), (8, 8))
    meta = {"fixture_dynamics": asdict(fixture_dynamics), "metadata": {"description": "test"}}
    data = model_json("gantry", "contact", names, x_mean, x_std, np.zeros(3), np.ones(3), layers, meta)
    data["integration_weight"] = weight
    path = tmp_path / name
    path.write_text(json.dumps(data))
    return path


def test_c_records_every_detect_with_observations_only(c_run):
    _, ctl, res = c_run
    recs = ctl.contact_records
    assert res.retries >= 1 and len(recs) >= res.retries
    assert sum(r["kind"] == "surface_block" for r in recs) >= 1
    json.dumps(recs)  # plain data, no numpy objects
    forbidden = ("true", "gt", "label", "ground", "penetration", "contact_force")
    for r in recs:
        assert not any(f in k for k in r for f in forbidden), sorted(r)
        assert r["attempt"] >= 1
    blocked = [r for r in recs if "analytic_mean_mm" in r]
    assert blocked and all(np.shape(r["analytic_cov_mm2"]) == (2, 2) for r in blocked)


def test_model_json_loads_and_predicts_the_right_shapes(tmp_path, c_run, task):
    recs = [r for r in c_run[1].contact_records if "analytic_mean_mm" in r]
    path = _synthetic_model(tmp_path, recs, task.backend.fixture_dynamics)
    model = load_model(path)
    p = model.predict(recs)
    n = len(recs)
    assert p["mean"].shape == (n, 3) and p["precision_xy"].shape == (n, 2, 2) and p["cov_xy"].shape == (n, 2, 2)
    assert p["sigma_yaw_deg"].shape == (n,) and np.all(p["sigma_yaw_deg"] > 0)
    assert np.all(np.linalg.eigvalsh(p["precision_xy"]) > 0)
    mean_m, prec_m = model.localizer_term(recs[0])
    assert mean_m.shape == (2,) and prec_m.shape == (2, 2)
    assert np.allclose(mean_m / MM, p["mean"][0, :2]) and np.allclose(prec_m * MM**2, p["precision_xy"][0])


def test_installed_models_load_and_match_only_their_fixture(task):
    paths = sorted(DEFAULT_MODEL_DIR.glob("contact_prior_*.json"))
    if not paths:
        pytest.skip("no installed contact prior")
    for path in paths:
        model = load_model(path)
        assert set(model.feature_names) <= set(FEATURE_SETS["all"])
        assert len(model.x_mean) == len(model.feature_names) == model.layers[0][0].shape[0]
        assert model.integration_weight is not None
        if isinstance(model, ContactPrior):
            assert model.layers[-1][0].shape[1] == 7
            keys = ("train_base_seeds", "validation_base_seed", "n_train", "n_val", "git")
        else:  # v0.2c v2 model
            assert model.layers[-1][0].shape[1] == 6 * model.components
            keys = ("fit_base_seeds", "stop_base_seeds", "n_fit", "n_stop", "git", "selection_rule")
            assert not set(model.data["metadata"]["fit_base_seeds"]) & {4001, 3031, 3032, 20261102, 20261116}
        for k in keys:
            assert k in model.data["metadata"], k
    gantry = find_model(task.backend.fixture_dynamics)
    if (DEFAULT_MODEL_DIR / "contact_prior_gantry.json").exists():
        assert gantry is not None and gantry.backend == "gantry"
    arm = find_model(ARM_LIKE)
    if (DEFAULT_MODEL_DIR / "contact_prior_arm.json").exists():
        assert arm is not None and arm.backend == "arm"
    else:
        assert arm is None
    # Without the W5b servo terms the arm model does not apply (they are stored with it).
    assert find_model(FixtureDynamics(8.0, 400.0, 6.3, 0.006)) is None


def _bare_model(fixture_dynamics: dict) -> ContactPrior:
    return ContactPrior({"format": "defex-contact-prior-v1", "feature_names": [], "x_mean": [], "x_std": [],
                         "y_mean": [0, 0, 0], "y_std": [1, 1, 1], "layers": [], "fixture_dynamics": fixture_dynamics})


def test_matching_handles_uncharacterized_values_both_ways():
    """Checkpoint 2 review: a stored None never matched its own fixture, and raised on any other."""
    tol = LearnedPriorConfig().fixture_match_rel_tol
    hw = FixtureDynamics(8.0, 400.0, 6.3, 0.006)  # tilt and lags not characterized (None)
    model = _bare_model(asdict(hw))
    assert model.matches(hw, tol)  # None matches None
    assert not model.matches(ARM_LIKE, tol)  # stored None vs a value: no match, and no exception
    characterized = _bare_model(asdict(ARM_LIKE))
    assert characterized.matches(ARM_LIKE, tol)
    assert not characterized.matches(hw, tol)  # a value vs a running None: no match
    assert not characterized.matches(replace(ARM_LIKE, rotational_following_lag_s=None), tol)


def test_a_model_must_state_every_fixture_field():
    tol = LearnedPriorConfig().fixture_match_rel_tol
    full = asdict(ARM_LIKE)
    assert _bare_model(full).matches(ARM_LIKE, tol)
    for k in full:  # one field missing: refused (it could differ on that field)
        assert not _bare_model({j: v for j, v in full.items() if j != k}).matches(ARM_LIKE, tol), k
    assert not _bare_model({**full, "unknown_field_s": 1.0}).matches(ARM_LIKE, tol)


def test_find_model_needs_a_matching_fixture(tmp_path, c_run, task):
    recs = [r for r in c_run[1].contact_records if "analytic_mean_mm" in r]
    fd = task.backend.fixture_dynamics
    _synthetic_model(tmp_path, recs, fd)
    assert find_model(fd, tmp_path) is not None
    assert find_model(replace(fd, effective_mass_kg=fd.effective_mass_kg * 1.1), tmp_path) is None
    assert find_model(ARM_LIKE, tmp_path) is None
    assert find_model(None, tmp_path) is None
    assert find_model(fd, tmp_path / "missing") is None


def test_g_equals_c_without_a_model(tmp_path, c_run, task):
    sc, ctl_c, res_c = c_run
    g = AdaptiveLearnedController(model_dir=tmp_path)  # empty directory: no model for any fixture
    res_g = task.run(g, sc)
    row_c, row_g = res_c.to_row(), res_g.to_row()
    for k in row_c:
        if k not in ("controller", "wall_time_s"):
            assert row_c[k] == row_g[k], k
    ev_g = [e for e in res_g.events if e[1] != "learned_prior"]
    assert ev_g == res_c.events
    assert any(e[1] == "learned_prior" and "behaving as C" in e[2] for e in res_g.events)
    assert g.contact_records == ctl_c.contact_records


def test_g_uses_a_matching_model(tmp_path, c_run, task):
    sc, _, _ = c_run
    recs = [r for r in c_run[1].contact_records if "analytic_mean_mm" in r]
    _synthetic_model(tmp_path, recs, task.backend.fixture_dynamics, weight=1.0)
    g = AdaptiveLearnedController(model_dir=tmp_path)
    task.run(g, sc)
    assert g.prior is not None and g.prior_weight == 1.0
    used = [r for r in g.contact_records if "learned_mean_mm" in r]
    assert used and all(r["kind"] == "surface_block" for r in used)
    # Weight 0 switches the term off.
    g0 = AdaptiveLearnedController(prior_cfg=LearnedPriorConfig(weight=0.0), model_dir=tmp_path)
    task.run(g0, sc)
    assert not any("learned_mean_mm" in r for r in g0.contact_records)


def test_update_gaussian_pulls_the_posterior_and_weight_zero_is_a_no_op():
    spec = ConnectorSpec.load("rect_12x8")
    loc = HoleLocalizer(spec, prior_sigma=2 * MM, extent=7 * MM, resolution=0.25 * MM, cop_sigma=0.5 * MM)
    before = loc.posterior.copy()
    loc.update_gaussian(np.array([2.0, -1.0]) * MM, np.eye(2) / (0.5 * MM) ** 2, 0.0)
    assert np.allclose(loc.posterior, before)
    loc.update_gaussian(np.array([2.0, -1.0]) * MM, np.eye(2) / (0.5 * MM) ** 2, 1.0)
    m = loc.mean() / MM
    assert 1.5 < m[0] < 2.0 and -1.0 < m[1] < -0.6  # prior N(0, 2 mm) x N(mu, 0.5 mm)
    assert np.allclose(loc.covariance(), loc.covariance().T)
    # With the outlier floor a confident, wrong prediction cannot erase the rest of the posterior.
    hard = HoleLocalizer(spec, prior_sigma=2 * MM, extent=7 * MM, resolution=0.25 * MM, cop_sigma=0.5 * MM)
    robust = HoleLocalizer(spec, prior_sigma=2 * MM, extent=7 * MM, resolution=0.25 * MM, cop_sigma=0.5 * MM)
    far = np.array([5.0, 5.0]) * MM
    hard.update_gaussian(far, np.eye(2) / (0.1 * MM) ** 2, 1.0)
    robust.update_gaussian(far, np.eye(2) / (0.1 * MM) ** 2, 1.0, outlier_weight=0.1)
    centre = (hard.grid.size // 2, hard.grid.size // 2)
    assert hard.posterior[centre] < 1e-12 < robust.posterior[centre]


def test_nll_gradients_match_finite_differences():
    rng = np.random.default_rng(0)
    x, t = rng.normal(size=(11, 4)), rng.normal(size=(11, 3))
    layers = [(W * (5 if k == 2 else 1), b + 0.3 * rng.normal(size=b.shape))
              for k, (W, b) in enumerate(init_layers(rng, 4, (5, 3)))]
    _, grads = loss_and_grads(layers, x, t, 1e-3)
    h = 1e-6
    for k, (W, _) in enumerate(layers):
        for idx in list(np.ndindex(W.shape))[:12]:
            old = W[idx]
            W[idx] = old + h
            lp, _ = loss_and_grads(layers, x, t, 1e-3)
            W[idx] = old - h
            lm, _ = loss_and_grads(layers, x, t, 1e-3)
            W[idx] = old
            assert abs((lp - lm) / (2 * h) - grads[k][0][idx]) < 1e-5 * max(1.0, abs(grads[k][0][idx]))


def test_g_is_registered():
    assert "adaptive_learned" in CONTROLLERS
    assert LABELS["adaptive_learned"] == "G: Defex adaptive + learned contact prior"
    assert isinstance(make_controller("adaptive_learned"), AdaptiveLearnedController)
