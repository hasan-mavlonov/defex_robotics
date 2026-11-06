"""Checkpoint 2 review scripts: the randomized-slice seed guard and the posterior calibration measure."""

import numpy as np

from experiments.collect_contacts import RESERVED_SEEDS
from experiments.cp2_posterior_calibration import hpd_mass_above_truth
from experiments.rand_equivalence import DEV_SEEDS


def test_rand_equivalence_runs_only_development_seeds():
    assert not (DEV_SEEDS & RESERVED_SEEDS)
    assert {2026, 2027, 4001, 3031} <= DEV_SEEDS


def test_hpd_mass_above_the_truth_cell():
    g = np.linspace(-5.0, 5.0, 101)
    hx, hy = np.meshgrid(g, g, indexing="ij")
    p = np.exp(-0.5 * (hx**2 + hy**2))
    p /= p.sum()
    assert hpd_mass_above_truth(p, hx, hy, np.zeros(2)) == 0.0  # truth at the mode: inside every region
    assert hpd_mass_above_truth(p, hx, hy, np.array([4.9, 4.9])) > 0.99
    # 2D standard normal: the region of mass 0.5 has radius sqrt(2 ln 2) = 1.18
    assert abs(hpd_mass_above_truth(p, hx, hy, np.array([np.sqrt(2.0 * np.log(2.0)), 0.0])) - 0.5) < 0.03
