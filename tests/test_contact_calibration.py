"""W7 calibration: recover known contact parameters from a synthetic 'real' curve."""

import numpy as np
import pytest

from defex.calibration.contact_fit import Curve, fit_contact, simulate_move


@pytest.mark.slow
def test_fit_recovers_friction_from_a_noisy_logged_curve(spec, tmp_path):
    truth = simulate_move(spec, friction=0.47, contact_timeconst_s=0.002)  # off the coarse grid
    rng = np.random.default_rng(0)
    noisy = Curve(truth.depth_mm, truth.fz_n + rng.normal(0.0, 0.05, truth.fz_n.size))
    noisy.write_csv(tmp_path / "real.csv")
    real = Curve.read_csv(tmp_path / "real.csv")
    fit = fit_contact(spec, real, frictions=np.round(np.arange(0.2, 0.81, 0.1), 2), timeconsts=(0.002, 0.004))
    assert abs(fit.friction - 0.47) <= 0.02, fit.friction
    assert fit.median_abs_error_n < 0.1
