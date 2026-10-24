"""Simulator-agnostic backend interface.

A backend owns the physics of the workcell: the receptacle, the held connector and
the 6-DOF insertion fixture with its servo drives, encoders and wrist F/T sensor.
Everything a controller may see flows through :class:`RawSensorData`; everything
used only for scoring flows through :class:`GroundTruth`. The two are never mixed.

The MuJoCo implementation lives in :mod:`defex.sim.mujoco_backend`. An Isaac Sim
backend would implement the same protocol (load a USD workcell, map
``set_tcp_setpoint`` onto its articulation controller, and read its contact
sensors for ground truth).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import numpy as np

from defex.config import ConnectorSpec
from defex.utils.transforms import Pose


@dataclass(frozen=True)
class SceneParams:
    """Per-trial physical configuration of the workcell."""

    connector: ConnectorSpec
    friction: float
    socket_pose: Pose  # true world pose of the socket mouth frame
    grasp_offset: Pose = field(default_factory=Pose.identity)  # connector tip relative to the fixture TCP


@dataclass(frozen=True)
class PayloadModel:
    """Mass properties below the F/T sensor, as identified after grasping."""

    mass_kg: float
    com_in_sensor: np.ndarray  # (3,) center of mass in the sensor frame (m)
    sensor_in_tcp: Pose  # F/T sensor frame relative to the fixture TCP frame


@dataclass(slots=True)
class RawSensorData:
    """Noise-free hardware signals. Noise is added by :mod:`defex.perception.sensors`."""

    t: float
    joint_pos: np.ndarray  # (6,) fixture joint positions [x, y, z, yaw, pitch, roll]
    tcp_pose: Pose  # fixture TCP from forward kinematics of joint_pos
    ft_force: np.ndarray  # (3,) force exerted by the wrist on the tool, sensor frame
    ft_torque: np.ndarray  # (3,) torque about the sensor origin, sensor frame


@dataclass(slots=True)
class GroundTruth:
    """Simulator truth used for scoring only. Never passed to controllers."""

    t: float
    socket_pose: Pose
    connector_pose: Pose
    contact_force: np.ndarray  # (3,) net contact force on the held parts, world frame
    contact_force_norm: float
    max_penetration: float  # m, deepest current contact
    n_contacts: int
    tcp_speed: float  # m/s
    joint_limit_hit: bool
    actuator_saturated: bool


class SimBackend(Protocol):
    """Minimal interface the task harness needs from a physics backend."""

    @property
    def time(self) -> float: ...

    @property
    def home_tcp_pose(self) -> Pose: ...

    @property
    def nominal_socket_pose(self) -> Pose: ...

    @property
    def payload(self) -> PayloadModel: ...

    def load(self, params: SceneParams) -> None: ...

    def reset(self) -> None: ...

    def set_tcp_setpoint(self, pose: Pose) -> None: ...

    def step(self, duration: float) -> None: ...

    def read_sensors(self) -> RawSensorData: ...

    def ground_truth(self) -> GroundTruth: ...

    def joint_positions(self) -> np.ndarray:
        """True fixture joint positions, for trajectory logging and replay (not for control)."""
        ...

    def set_marker_pose(self, which: str, pose: Pose) -> None:
        """Move a visual-only marker (``"estimate"`` or ``"setpoint"``). May be a no-op."""
        ...
