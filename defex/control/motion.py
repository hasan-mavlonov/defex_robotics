"""Bounded Cartesian motion generation.

Every controller command passes through :class:`CartesianMotionGenerator` before
it reaches the fixture. It moves the setpoint towards the commanded target along a
straight line (and a geodesic in rotation) with explicit limits on linear/angular
velocity and acceleration, using the time-optimal approach law
``v = min(v_max, sqrt(2 a d))``. The connector can therefore never be teleported,
and no controller can exceed the fixture's motion limits.
"""

from __future__ import annotations

import numpy as np

from defex.config import DEG, MM, FixtureConfig
from defex.control.base import Command
from defex.utils.transforms import Pose, matrix_to_rotvec, norm3, rotvec_to_matrix


class _Axis:
    """Vector-valued online trajectory generator (straight-line, trapezoidal)."""

    def __init__(self, v_max: float, a_max: float) -> None:
        self.v_max = v_max
        self.a_max = a_max
        self.v = np.zeros(3)

    def reset(self) -> None:
        self.v = np.zeros(3)

    def step(self, error: np.ndarray, v_cap: float, dt: float) -> np.ndarray:
        """Return the displacement for this tick given the remaining error vector."""
        dist = norm3(error)
        v_lim = min(max(v_cap, 0.0), self.v_max)
        if dist < 1e-12:
            v_des = np.zeros(3)
        else:
            speed = min(v_lim, np.sqrt(2.0 * self.a_max * dist))
            v_des = error / dist * speed
        dv = v_des - self.v
        dv_norm = norm3(dv)
        dv_max = self.a_max * dt
        if dv_norm > dv_max:
            dv *= dv_max / dv_norm
        self.v = self.v + dv
        speed_now = norm3(self.v)
        if speed_now > self.v_max:
            self.v *= self.v_max / speed_now
        step = self.v * dt
        if dist > 0.0 and float(np.dot(step, error)) / dist >= dist:
            # The next step would pass the target: land on it exactly. The implied
            # velocity error/dt is no larger than the current speed, so limits hold.
            self.v = error / dt
            return error.copy()
        return step


class CartesianMotionGenerator:
    def __init__(self, fixture: FixtureConfig, dt: float) -> None:
        self.dt = dt
        self.lin = _Axis(fixture.max_linear_speed_mm_s * MM, fixture.max_linear_accel_mm_s2 * MM)
        self.ang = _Axis(fixture.max_angular_speed_deg_s * DEG, fixture.max_angular_accel_deg_s2 * DEG)
        self.pose = Pose.identity()

    def reset(self, pose: Pose) -> None:
        self.pose = Pose(pose.p.copy(), pose.R.copy())
        self.lin.reset()
        self.ang.reset()

    @property
    def linear_speed(self) -> float:
        return norm3(self.lin.v)

    @property
    def angular_speed(self) -> float:
        return norm3(self.ang.v)

    def update(self, cmd: Command) -> Pose:
        dp = self.lin.step(cmd.target.p - self.pose.p, cmd.max_linear_speed, self.dt)
        rv_err = matrix_to_rotvec(cmd.target.R @ self.pose.R.T)
        drv = self.ang.step(rv_err, cmd.max_angular_speed, self.dt)
        self.pose = Pose(self.pose.p + dp, rotvec_to_matrix(drv) @ self.pose.R)
        return self.pose
