from dataclasses import replace

import numpy as np

from defex.config import FixtureConfig, SensorNoiseConfig
from defex.sim.backend import SceneParams
from defex.tasks.calibration import calibration_seed, identification_error, identify_payload


def _identify(backend, spec, noise, seed):
    backend.load(SceneParams(spec, spec.friction, backend.nominal_socket_pose))
    return identify_payload(backend, FixtureConfig(), noise, 0.002, seed)


def test_identification_is_exact_without_sensor_noise(backend, spec):
    quiet = replace(
        SensorNoiseConfig(), ft_force_sigma_n=0.0, ft_torque_sigma_nm=0.0, encoder_pos_sigma_mm=0.0,
        encoder_rot_sigma_deg=0.0,
    )
    err = identification_error(_identify(backend, spec, quiet, 1), backend.true_payload)
    assert abs(err["mass_error_g"]) < 1e-3
    assert err["com_error_mm"] < 1e-3


def test_identification_with_nominal_noise_and_bias(backend, spec):
    # Development measurement over 20 seeds: mass RMS error 0.15 g (max 0.27 g),
    # CoM error median 0.17 mm (max 0.32 mm), sensor bias fitted as a nuisance.
    for seed in (calibration_seed(spec.name), 3, 11):
        fit = _identify(backend, spec, SensorNoiseConfig(), seed)
        err = identification_error(fit, backend.true_payload)
        assert abs(err["mass_error_g"]) < 0.5, err
        assert err["com_error_mm"] < 0.6, err
        assert np.linalg.norm(fit.force_bias) > 0.0


def test_harness_uses_the_identified_payload(task, spec):
    from defex.tasks.conditions import conditions_by_name
    from defex.tasks.scenarios import sample_scenario

    sc = sample_scenario(conditions_by_name()["nominal"], 0, 2026, task.backend.nominal_socket_pose)
    fit = task.payload_fit(sc)
    assert fit.payload.mass_kg != task.backend.true_payload.mass_kg
    assert task.payload_fit(sc) is fit  # identified once per connector
