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

from defex.config import CompliantStageConfig, ConnectorSpec, PartVariation
from defex.utils.transforms import Pose


@dataclass(frozen=True)
class SceneParams:
    """Per-trial physical configuration of the workcell."""

    connector: ConnectorSpec
    friction: float
    socket_pose: Pose  # true world pose of the socket mouth frame
    grasp_offset: Pose = field(default_factory=Pose.identity)  # connector tip relative to the fixture TCP
    compliance: CompliantStageConfig | None = None  # passive RCC stage (baselines E, F); None = rigid
    defect: str | None = None  # deliberately bad part (defex.sim.mating.DEFECTS); None = good part
    part_variation: PartVariation | None = None  # mating values off nominal (v0.2c review); None = nominal


@dataclass(frozen=True)
class FixtureDynamics:
    """What a controller needs to know about the machine it pushes with (W5).

    Without this, controllers were told the gantry's servo values even on the arm.
    """

    translational_stiffness_n_per_mm: float  # weakest Cartesian direction at the tool
    yaw_stiffness_nm_per_rad: float  # about the insertion axis
    effective_mass_kg: float  # apparent mass at the tool along the insertion axis
    command_latency_s: float  # setpoint to actuator
    # W5b. Stiffer of the two tilt axes, tool tip held in place (as it is by a face or floor
    # contact). None: not characterized, taken equal to the yaw stiffness.
    tilt_stiffness_nm_per_rad: float | None = None
    # W5b. Following error per unit of commanded speed in steady motion (servo damping over
    # stiffness), slowest translational axis. A guarded move that stops on a wall stores speed x lag
    # of setpoint lead, which the servo then pushes into the wall. On hardware: identify from a
    # logged ramp. None: not characterized (no lag correction).
    following_lag_s: float | None = None
    # The same for the rotational axes (slowest of yaw and tilt), for guarded rotations.
    # None: taken equal to following_lag_s.
    rotational_following_lag_s: float | None = None

    @property
    def tilt_stiffness(self) -> float:
        return self.yaw_stiffness_nm_per_rad if self.tilt_stiffness_nm_per_rad is None else self.tilt_stiffness_nm_per_rad

    @property
    def rotational_following_lag(self) -> float | None:
        return self.following_lag_s if self.rotational_following_lag_s is None else self.rotational_following_lag_s


@dataclass(frozen=True)
class PayloadModel:
    """Mass properties below the F/T sensor (identified, or the simulator's truth)."""

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
    # "simulator": exact. "measured": a hardware run, where pose comes from encoders and
    # force from the wrist sensor; seating is confirmed by the post-trial inspection.
    source: str = "simulator"
    latched: bool | None = None  # latching connectors: is the latch engaged (None: no latch modelled)
    latch_broken: bool = False


class SimBackend(Protocol):
    """Minimal interface the task harness needs from a physics backend."""

    @property
    def time(self) -> float: ...

    @property
    def home_tcp_pose(self) -> Pose: ...

    @property
    def nominal_socket_pose(self) -> Pose: ...

    @property
    def fixture_dynamics(self) -> FixtureDynamics: ...

    @property
    def ft_sensor_in_tcp(self) -> Pose:
        """F/T sensor frame relative to the fixture TCP (a drawing dimension)."""
        ...

    @property
    def true_payload(self) -> PayloadModel:
        """Simulator mass properties below the F/T sensor. For tests and reports only:
        the harness identifies the payload from F/T readings (defex.tasks.calibration)."""
        ...

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
