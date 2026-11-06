"""v0.2c review: part-to-part spread of the mating values is simulator-side only and off by default."""

from dataclasses import replace

import numpy as np
import pytest

from defex.config import MM, ConnectorSpec, PartVariation
from defex.sim.mating import MatingForce
from defex.tasks.conditions import LATCH_SPREAD, latch_spread_conditions, latching_conditions_by_name
from defex.tasks.scenarios import sample_scenario
from defex.utils.transforms import Pose

SPEC = ConnectorSpec.load("microfit3_4ckt")


def _profile(mf: MatingForce) -> list[float]:
    return [mf.axial_force(d, 1e-3, np.zeros(2)) for d in np.linspace(0.0, SPEC.depth, 500)]


def test_nominal_variation_is_the_nominal_part():
    assert _profile(MatingForce(SPEC)) == _profile(MatingForce(SPEC, None, PartVariation()))


def test_variation_moves_the_latch_and_scales_the_forces():
    mf = MatingForce(SPEC, None, PartVariation(latch_shift_mm=-0.2, latch_peak_scale=0.5, terminal_scale=1.6))
    m = SPEC.mating
    assert mf.snap == pytest.approx((m.latch_snap_depth_mm - 0.2) * MM)
    assert mf.latch_peak == pytest.approx(0.5 * m.latch_peak_force_n)
    assert mf.peak_t == pytest.approx(1.6 * m.circuits * m.terminal_peak_per_circuit_n)
    assert mf.peak_t <= m.mating_force_max_n + 1e-9  # the top of the range is the datasheet maximum
    lo = MatingForce(SPEC, None, PartVariation(terminal_scale=0.8))
    assert lo.slide_t >= m.unmating_force_min_n - 1e-9  # the bottom is the datasheet unmating minimum
    bad = MatingForce(SPEC, "half_latched", PartVariation(latch_shift_mm=0.2))
    assert bad.stop == pytest.approx(bad.snap - 0.3 * MM)  # the defect follows the moved latch


def test_conditions_without_a_spread_keep_their_exact_draws():
    cond = latching_conditions_by_name()["mf_moderate"]
    a = sample_scenario(cond, 3, 2026, Pose.identity())
    b = sample_scenario(replace(cond, part_spread=LATCH_SPREAD), 3, 2026, Pose.identity())
    assert a.part_variation is None and "latch_shift_mm" not in a.disturbance
    assert np.array_equal(a.socket_pose.p, b.socket_pose.p) and np.array_equal(a.grasp_offset.p, b.grasp_offset.p)
    assert b.part_variation is not None
    assert {k: v for k, v in b.disturbance.items() if k in a.disturbance} == a.disturbance


def test_spread_draws_stay_in_range_and_the_controller_keeps_the_drawing():
    cond = {c.name: c for c in latch_spread_conditions()}["mf_spread"]
    nominal = ConnectorSpec.load("microfit3_4ckt")
    for i in range(30):
        sc = sample_scenario(cond, i, 2026, Pose.identity())
        v = sc.part_variation
        assert -0.2 <= v.latch_shift_mm <= 0.2 and 0.5 <= v.latch_peak_scale <= 1.5 and 0.8 <= v.terminal_scale <= 1.6
        assert sc.connector == nominal  # what ControllerContext.connector is built from
    assert sample_scenario(cond, 4, 2026, Pose.identity()).part_variation == \
        sample_scenario(cond, 4, 2026, Pose.identity()).part_variation
