"""v0.2c: v2 learned contact terms (mixture head, ratio and residual modes) and their training."""

import json
from dataclasses import asdict

import numpy as np
import pytest

from defex.config import MM, AdaptiveConfig, LearnedPriorConfig
from defex.control.adaptive_fsm import AdaptiveInsertionController
from defex.control.adaptive_learned import AdaptiveLearnedController
from defex.recovery.contact_likelihood import (
    FORMAT_V2,
    ContactLikelihood,
    gaussian_mixture_log_density,
    n_outputs,
)
from defex.recovery.learned_prior import FEATURE_SETS, find_model, load_model, raw_features
from defex.recovery.search_policy import HoleLocalizer
from defex.config import ConnectorSpec
from defex.tasks.conditions import conditions_by_name
from defex.tasks.scenarios import sample_scenario
from experiments.runner import nominal_socket_pose
from experiments.train_contact_likelihood import (
    batch_loss_grads,
    fit_marginal,
    grid_mm,
    init_net,
)
from experiments.train_contact_prior import standardize

BLOCKING_TRIAL = ("noise_2mm", 4, 2026)  # development seed; C blocks twice on this trial (test_learned_prior)


@pytest.fixture(scope="module")
def c_run(task):
    cond = conditions_by_name()[BLOCKING_TRIAL[0]]
    sc = sample_scenario(cond, BLOCKING_TRIAL[1], BLOCKING_TRIAL[2], nominal_socket_pose(cond, task.fixture))
    ctl = AdaptiveInsertionController()
    return sc, ctl, task.run(ctl, sc)


def _v2_model(records, fixture_dynamics, mode="residual", components=2, weight=1.0, outlier=0.1, seed=0):
    names = FEATURE_SETS["contact"]
    x = np.array([[raw_features(r)[n] for n in names] for r in records])
    x_mean, x_std = standardize(x)
    net = init_net(np.random.default_rng(seed), len(names), (8, 8), components)
    data = {
        "format": FORMAT_V2, "backend": "gantry", "mode": mode, "components": components, "feature_set": "contact",
        "feature_names": list(names), "x_mean": x_mean.tolist(), "x_std": x_std.tolist(),
        "o_mean_mm": [0.0, 0.0], "o_std_mm": [1.5, 1.2], "outlier_weight": outlier,
        "layers": [{"W": W.tolist(), "b": b.tolist()} for W, b in net.layers],
        "applies_to_kinds": ["surface_block"], "integration_weight": weight,
        "fixture_dynamics": asdict(fixture_dynamics), "metadata": {"description": "test"},
    }
    if mode == "ratio":
        data["offset_marginal"] = {"weights": [1.0], "means_mm": [[0.0, 0.0]], "covs_mm2": [[[4.0, 0.0], [0.0, 4.0]]]}
    return data


def _write(tmp_path, data, name="contact_prior_test.json"):
    path = tmp_path / name
    path.write_text(json.dumps(data))
    return path


@pytest.mark.parametrize("components", [1, 3])
def test_grid_loss_gradients_match_finite_differences(components):
    rng = np.random.default_rng(components)
    n, c = 7, 40
    x, t = rng.normal(size=(n, 5)), 1.5 * rng.normal(size=(n, c, 2))
    base, cell = rng.normal(size=(n, c)), rng.integers(0, c, n)
    net = init_net(rng, 5, (6, 4), components)
    net.layers = [(W * (4 if k == 2 else 1), b + 0.3 * rng.normal(size=b.shape)) for k, (W, b) in enumerate(net.layers)]
    net.eta = 0.3
    args = (components, 0.05, 1.0, 1e-3, 0.0)
    _, grads, d_eta = batch_loss_grads(net, x, t, base, cell, *args)
    h = 1e-6
    for k, (W, b) in enumerate(net.layers):
        for arr, which in ((W, 0), (b, 1)):
            for idx in list(np.ndindex(arr.shape))[:20]:
                old = arr[idx]
                arr[idx] = old + h
                lp = batch_loss_grads(net, x, t, base, cell, *args)[0]
                arr[idx] = old - h
                lm = batch_loss_grads(net, x, t, base, cell, *args)[0]
                arr[idx] = old
                an = grads[k][which][idx]
                assert abs((lp - lm) / (2 * h) - an) < 1e-5 * max(1.0, abs(an))
    e0 = net.eta
    net.eta = e0 + h
    lp = batch_loss_grads(net, x, t, base, cell, *args)[0]
    net.eta = e0 - h
    lm = batch_loss_grads(net, x, t, base, cell, *args)[0]
    net.eta = e0
    assert abs((lp - lm) / (2 * h) - d_eta) < 1e-6


def test_v2_term_is_a_floored_density_on_the_localizer_grid(c_run, task):
    recs = [r for r in c_run[1].contact_records if "analytic_mean_mm" in r]
    model = ContactLikelihood(_v2_model(recs, task.backend.fixture_dynamics, components=3))
    grid, cell_area, area = grid_mm(AdaptiveConfig())
    g = model.log_term_mm(recs, grid, area)
    assert g.shape == (len(recs), grid.shape[0]) and np.all(np.isfinite(g))
    mass = np.exp(g).sum(axis=1) * cell_area  # mixture mostly on the grid, plus the floor e
    assert np.all(mass > 0.5) and np.all(mass < 1.01)
    assert np.all(g >= np.log(model.outlier / area) - 1e-9)  # never below the floor
    m = model.mixture_mean_mm(recs[0])
    assert m.shape == (2,)


def test_gaussian_mixture_marginal_is_normalized_and_fit_recovers_it():
    g = np.linspace(-12, 12, 241)
    hx, hy = np.meshgrid(g, g, indexing="ij")
    pts = np.stack([hx.ravel(), hy.ravel()], axis=1)
    params = {"weights": [0.3, 0.7], "means_mm": [[-1.0, 0.0], [1.5, 0.5]],
              "covs_mm2": [[[1.0, 0.2], [0.2, 0.5]], [[0.8, 0.0], [0.0, 1.2]]]}
    mass = np.exp(gaussian_mixture_log_density(params, pts)).sum() * 0.1**2
    assert abs(mass - 1.0) < 1e-3
    rng = np.random.default_rng(0)
    o = rng.normal(size=(4000, 2)) * [1.0, 2.0] + [0.5, -0.5]
    fit = fit_marginal(o, components=1)
    assert np.allclose(fit["means_mm"][0], [0.5, -0.5], atol=0.1)
    assert np.allclose(np.diag(fit["covs_mm2"][0]), [1.0, 4.0], rtol=0.1)


def test_ratio_model_needs_its_marginal(c_run, task):
    recs = [r for r in c_run[1].contact_records if "analytic_mean_mm" in r]
    data = _v2_model(recs, task.backend.fixture_dynamics, mode="ratio")
    ContactLikelihood(data)
    del data["offset_marginal"]
    with pytest.raises(ValueError):
        ContactLikelihood(data)
    with pytest.raises(ValueError):
        ContactLikelihood({**data, "mode": "nonsense"})


def test_g_runs_a_v2_model_and_weight_zero_is_c(tmp_path, c_run, task):
    sc, ctl_c, res_c = c_run
    recs = [r for r in ctl_c.contact_records if "analytic_mean_mm" in r]
    _write(tmp_path, _v2_model(recs, task.backend.fixture_dynamics))
    g = AdaptiveLearnedController(model_dir=tmp_path)
    res_g = task.run(g, sc)
    assert isinstance(g.prior, ContactLikelihood) and g.prior_weight == 1.0
    used = [r for r in g.contact_records if "learned_mean_mm" in r]
    assert used and all(r["kind"] == "surface_block" and "combined_mean_mm" in r for r in used)
    assert any(e[1] == "learned_prior" and "contact_prior_test.json" in e[2] for e in res_g.events)
    g0 = AdaptiveLearnedController(prior_cfg=LearnedPriorConfig(weight=0.0), model_dir=tmp_path)
    res_0 = task.run(g0, sc)
    row_c, row_0 = res_c.to_row(), res_0.to_row()
    for k in row_c:
        if k not in ("controller", "wall_time_s"):
            assert row_c[k] == row_0[k], k


def test_two_models_for_one_fixture_are_refused(tmp_path, c_run, task):
    recs = [r for r in c_run[1].contact_records if "analytic_mean_mm" in r]
    fd = task.backend.fixture_dynamics
    _write(tmp_path, _v2_model(recs, fd), "contact_prior_a.json")
    assert isinstance(find_model(fd, tmp_path), ContactLikelihood)
    _write(tmp_path, _v2_model(recs, fd, seed=1), "contact_prior_b.json")
    with pytest.raises(ValueError, match="several"):
        find_model(fd, tmp_path)
    assert isinstance(load_model(tmp_path / "contact_prior_b.json"), ContactLikelihood)


def test_the_fitted_floor_keeps_a_confident_wrong_term_from_erasing_the_truth(c_run, task):
    """A v2 term with a tiny floor still leaves mass far from its mixture (unlike a pure Gaussian)."""
    recs = [r for r in c_run[1].contact_records if "analytic_mean_mm" in r]
    model = ContactLikelihood(_v2_model(recs, task.backend.fixture_dynamics, components=1, outlier=1e-3))
    spec = ConnectorSpec.load("rect_12x8")
    loc = HoleLocalizer(spec, prior_sigma=2 * MM, extent=7 * MM, resolution=0.25 * MM, cop_sigma=0.5 * MM)
    rec = {**recs[0], "probe_xy_mm": [6.0, 6.0]}
    loc.update_log_term(model.localizer_log_term(rec, loc.hx, loc.hy, loc.area))
    centre = (loc.grid.size // 2, loc.grid.size // 2)
    assert loc.posterior[centre] > 1e-8
    assert n_outputs(3) == 18
