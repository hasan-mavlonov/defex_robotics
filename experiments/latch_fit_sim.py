"""Synthetic 'logged' latch curves from the MuJoCo simulator (v0.2f latch fit).

One guarded push-click move on the gantry, as the rig would log it: the plug starts
0.5 mm above the mouth on the socket axis, the setpoint descends at a constant speed
until the tared axial force passes the guard (the connector's insert target, 35.2 N
for the Micro-Fit), holds, then (optionally) climbs at the same speed until the pull
reaches the guard pull force (50% of the rated retention, as in C's VERIFY) or has
the setpoint has travelled ``pull_travel_mm``. The gantry servo is compliant
(about 10 N/mm), so the setpoint runs well past the plug: the guard is on force. The log is what a rig has: encoder depth and wrist F/T,
both through ``SensorSuite`` (bias, white noise, encoder noise), plus a depth offset
for the unknown mouth-plane zero. Simulator side: imports MuJoCo.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from defex.calibration.latch_fit import LoggedMove
from defex.config import MM, ConnectorSpec, FixtureConfig, PartVariation, SensorNoiseConfig
from defex.perception.sensors import SensorSuite
from defex.sim.backend import SceneParams
from defex.sim.mujoco_backend import MuJoCoBackend
from defex.utils.transforms import Pose


@dataclass(frozen=True)
class PushPull:
    speed_mm_s: float = 1.0
    start_height_mm: float = 0.5
    guard_push_n: float | None = None  # None: the connector's insert target
    guard_pull_n: float | None = None  # None: 50% of the rated latch retention
    pull: bool = True
    push_overtravel_mm: float = 6.0  # setpoint travel allowed past the seat (the gantry servo is ~10 N/mm)
    pull_travel_mm: float = 8.0  # setpoint travel allowed for the pull
    hold_s: float = 0.1
    dt: float = 0.002


def simulate_logged_move(spec: ConnectorSpec, move: PushPull = PushPull(), variation: PartVariation | None = None,
                         defect: str | None = None, noise: SensorNoiseConfig = SensorNoiseConfig(),
                         depth_offset_mm: float = 0.0, seed: int = 2027, fixture: FixtureConfig | None = None):
    """Return (LoggedMove as the rig logs it, dict of ground-truth extras)."""
    be = MuJoCoBackend(fixture=fixture)
    be.load(SceneParams(spec, spec.friction, Pose.identity()))
    S = be.nominal_socket_pose
    be.load(SceneParams(spec, spec.friction, S, defect=defect, part_variation=variation))
    sensors = SensorSuite(noise, seed)
    guard_push = move.guard_push_n if move.guard_push_n is not None else spec.force_budget.insert_target_n
    guard_pull = move.guard_pull_n if move.guard_pull_n is not None else 0.5 * spec.mating.latch_retention_force_n
    z = move.start_height_mm * MM
    start = Pose(S.p + np.array([0.0, 0.0, z]), S.R)
    be.set_joint_positions_kinematic(be.inverse_kinematics(start))
    be.set_tcp_setpoint(start)
    for _ in range(25):
        be.step(move.dt)

    t, depth, fz, gt_depth = [], [], [], []

    def log():
        raw = be.read_sensors()
        r = sensors.measure(raw)
        rel = S.R.T @ (r.tcp_pose.p - S.p)
        t.append(raw.t)
        depth.append(-rel[2] / MM + depth_offset_mm)
        fz.append(-float(r.ft_force[2]))  # wrist-on-tool force; the socket pushing the plug out reads negative
        gt_depth.append(-(S.R.T @ (be.data.site_xpos[be._tcp_site] - S.p))[2] / MM)

    step = move.speed_mm_s * MM * move.dt
    log()
    f_tare = fz[0]
    limit = -(spec.depth + move.push_overtravel_mm * MM)
    while z > limit:
        z -= step
        be.set_tcp_setpoint(Pose(S.p + np.array([0.0, 0.0, z]), S.R))
        be.step(move.dt)
        log()
        if fz[-1] - f_tare > guard_push:
            break
    for _ in range(int(round(move.hold_s / move.dt))):
        be.step(move.dt)
        log()
    if move.pull:
        z_turn = z
        while z < z_turn + move.pull_travel_mm * MM:
            z += step
            be.set_tcp_setpoint(Pose(S.p + np.array([0.0, 0.0, z]), S.R))
            be.step(move.dt)
            log()
            if fz[-1] - f_tare < -guard_pull:
                break
        for _ in range(int(round(move.hold_s / move.dt))):
            be.step(move.dt)
            log()
    m = LoggedMove(np.array(t) - t[0], np.array(depth), np.array(fz), latch=defect != "broken_latch",
                   speed_mm_s=move.speed_mm_s)
    extras = {"gt_depth_mm": np.array(gt_depth), "latched": bool(be._mating.state.latched),
              "broken": bool(be._mating.state.broken), "max_depth_mm": be._mating.state.max_depth / MM}
    return m, extras


def stress_noise(k: float) -> SensorNoiseConfig:
    base = SensorNoiseConfig()
    return replace(base, ft_force_sigma_n=base.ft_force_sigma_n * k)
