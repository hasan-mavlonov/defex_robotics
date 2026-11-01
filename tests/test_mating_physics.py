"""W3: terminal and latch physics reproduce the connector data, and bad parts behave as bad parts."""

import numpy as np
import pytest

from defex.config import MM, ConnectorSpec
from defex.sim.backend import SceneParams
from defex.sim.mating import MatingForce
from defex.sim.mujoco_backend import MuJoCoBackend
from defex.utils.transforms import Pose

SPEC = ConnectorSpec.load("microfit3_4ckt")


def test_model_latch_holds_to_the_rated_retention_then_breaks():
    mf = MatingForce(SPEC)
    for d in np.linspace(0.0, SPEC.depth, 400):
        mf.axial_force(d, 1e-3, np.zeros(2))
    assert mf.state.latched
    retention = SPEC.mating.latch_retention_force_n  # 58 N, PS-43045
    held = []
    for d in np.linspace(SPEC.depth, SPEC.depth - 2.0 * MM, 4000):
        f = mf.axial_force(d, -1e-3, np.zeros(2))
        if mf.state.broken:
            break
        held.append(-f - mf.terminal_force(d))  # latch share of the pull-in force
    assert mf.state.broken
    assert max(held) == pytest.approx(retention, rel=0.15)


def test_model_forces_respect_the_datasheet_limits():
    mf = MatingForce(SPEC)
    depths = np.linspace(0.0, SPEC.depth, 2000)
    peak = max(mf.terminal_force(d) + mf.latch_ramp_force(d) for d in depths)
    assert peak <= SPEC.mating.mating_force_max_n  # 32 N max for 4 circuits
    assert mf.slide_t >= SPEC.mating.unmating_force_min_n  # 9.6 N min withdrawal


def _press_and_pull(defect=None, pull_n=29.0, overtravel_mm=3.0):
    be = MuJoCoBackend()
    be.load(SceneParams(SPEC, SPEC.friction, Pose.identity()))
    S = be.nominal_socket_pose
    be.load(SceneParams(SPEC, SPEC.friction, S, defect=defect))
    start = Pose(S.p + np.array([0, 0, 0.5]) * MM, S.R)
    be.set_joint_positions_kinematic(be.inverse_kinematics(start))
    be.set_tcp_setpoint(start)
    for _ in range(50):
        be.step(0.002)
    f0 = be.read_sensors().ft_force[2]
    z, depth, force = 0.5 * MM, [], []
    tip = lambda: (S.p[2] - be.data.site_xpos[be._tcp_site][2]) / MM  # noqa: E731
    while z > -(SPEC.depth + overtravel_mm * MM):
        z -= MM * 0.002
        be.set_tcp_setpoint(Pose(S.p + np.array([0, 0, z]), S.R))
        be.step(0.002)
        depth.append(tip())
        force.append(abs(be.read_sensors().ft_force[2] - f0))
    for _ in range(100):
        be.step(0.002)
    seat, latched = tip(), be._mating.state.latched
    while z < -SPEC.depth:  # release the press back to the nominal seat setpoint
        z += MM * 0.002
        be.set_tcp_setpoint(Pose(S.p + np.array([0, 0, z]), S.R))
        be.step(0.002)
    d0, fz0, pulled = tip(), be.read_sensors().ft_force[2], 0.0
    for _ in range(3000):
        z += MM * 0.002
        be.set_tcp_setpoint(Pose(S.p + np.array([0, 0, z]), S.R))
        be.step(0.002)
        pulled = abs(be.read_sensors().ft_force[2] - fz0)
        if pulled >= pull_n:
            break
    return np.array(depth), np.array(force), seat, latched, d0 - tip(), pulled


@pytest.mark.slow
def test_good_part_mating_curve_latch_and_pull():
    depth, force, seat, latched, pull_disp, pulled = _press_and_pull()
    mf = MatingForce(SPEC)
    designed = max(mf.terminal_force(d) + mf.latch_ramp_force(d) for d in np.linspace(0, mf.snap, 2000))
    band = (depth > mf.t0 / MM) & (depth < mf.snap / MM)
    measured = force[band].max()
    assert measured == pytest.approx(designed, rel=0.15), (measured, designed)  # F/T sees the model, +/-15%
    assert measured <= SPEC.mating.mating_force_max_n
    assert abs(seat - SPEC.socket.depth_mm) < 0.05 and latched
    # Half the rated retention holds; the plug may retrace the post-snap stroke before the hook catches.
    assert pulled >= 29.0 and pull_disp < SPEC.mating.latch_post_snap_stroke_mm + 0.3, pull_disp


@pytest.mark.slow
@pytest.mark.parametrize("defect", ["broken_latch", "half_latched", "stubbed_terminal"])
def test_bad_parts_fail_the_pull_test(defect):
    _, force, seat, latched, pull_disp, _ = _press_and_pull(defect)
    assert not latched
    assert pull_disp > 1.0, (defect, pull_disp)  # comes out under a 29 N pull
    if defect == "stubbed_terminal":
        assert seat < SPEC.socket.depth_mm - 1.0 and force.max() > SPEC.force_budget.abort_n


@pytest.mark.slow
def test_wrong_polarization_stops_at_the_key():
    _, _, seat, latched, _, _ = _press_and_pull("wrong_polarization")
    assert seat < 1.5 and not latched
