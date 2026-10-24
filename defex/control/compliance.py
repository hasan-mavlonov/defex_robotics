"""Active compliance primitives (admittance control on top of position servos).

The fixture's joint servos are stiff (10 N/mm); compliance is produced in software
by moving the setpoint in response to the measured contact wrench, which is how
force-controlled assembly is done on industrial position-controlled robots
(ABB Integrated Force Control, FANUC Force Sensor, UR force mode).

Loop-stability note: the admittance loop gain is ``k_servo / damping``. With
10 N/mm servo stiffness and 1 N.s/mm damping that is 10 rad/s, an order of
magnitude below the servo bandwidth (~90 rad/s) and the 500 Hz control rate.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


class Admittance:
    """First-order admittance ``x' = (f - k x) / d`` with a norm bound on ``x``."""

    def __init__(self, stiffness: float, damping: float, limit: float, dim: int) -> None:
        self.k = stiffness
        self.d = damping
        self.limit = limit
        self.x = np.zeros(dim)

    def reset(self, x0: np.ndarray | None = None) -> None:
        self.x = np.zeros_like(self.x) if x0 is None else np.asarray(x0, dtype=float).copy()

    def update(self, f: np.ndarray, dt: float, active: np.ndarray | None = None) -> np.ndarray:
        xdot = (np.asarray(f) - self.k * self.x) / self.d
        if active is not None:
            xdot = xdot * active
        self.x = self.x + xdot * dt
        n = float(np.linalg.norm(self.x))
        if n > self.limit:
            self.x *= self.limit / n
        return self.x


@dataclass
class ForceGuidedAxis:
    """Indirect force control along the insertion axis.

    The insertion setpoint advances at ``v = gain * (F_target - F_axial)``,
    saturated to ``[-v_back, v_max]``. In free space the axis advances at the
    capped speed; on contact it settles where the measured resistance equals the
    target force.
    """

    gain: float  # m/s per N
    v_max: float  # m/s
    v_back: float  # m/s (maximum back-off speed)

    def velocity(self, f_target: float, f_axial: float) -> float:
        return float(np.clip(self.gain * (f_target - f_axial), -self.v_back, self.v_max))
