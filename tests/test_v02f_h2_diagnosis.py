"""v0.2f h2 diagnosis scripts: seed guard of the trace replay, and the drift axes (no simulation)."""

from __future__ import annotations

import numpy as np
import pytest

from experiments.v02f_h2_drift_axes import drift_rates
from experiments.v02f_h2_trace import H2_SEED, check_seed, named_failures


def test_named_failures_are_c_failures_of_the_reported_run():
    assert named_failures("arm", "h2_ft_drift_0.3") >= {4, 12, 18, 19, 21, 28, 29, 30}
    assert 0 not in named_failures("arm", "h2_ft_drift_0.3")  # C seated arm drift trial 0


def test_seed_guard():
    check_seed("arm", "h2_ft_drift_0.3", 12, 2026)
    check_seed("arm", "h2_ft_drift_0.3", 12, H2_SEED)
    with pytest.raises(SystemExit):
        check_seed("arm", "h2_ft_drift_0.3", 0, H2_SEED)  # not a named failure
    with pytest.raises(SystemExit):
        check_seed("arm", "h2_tilt_unseen_2deg", 0, H2_SEED)  # family not under diagnosis
    with pytest.raises(SystemExit):
        check_seed("arm", "h2_ft_drift_0.3", 12, 20261123)


def test_drift_rates_have_the_condition_magnitude():
    r = drift_rates("h2_ft_drift_0.3", H2_SEED, [4, 12])
    for v in r.values():
        assert np.linalg.norm(v) == pytest.approx(0.3)
    # Arm trial 12, a false accept in the reported run: drift reads as the socket pushing the plug out.
    assert r[12][2] == pytest.approx(0.298, abs=1e-3)
