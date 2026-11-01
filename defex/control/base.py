"""Controller interface shared by all insertion strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from defex.config import ConnectorSpec, FixtureConfig, SensorNoiseConfig
from defex.perception.state_estimator import Observation
from defex.sim.backend import FixtureDynamics
from defex.utils.transforms import Pose


@dataclass(frozen=True)
class Command:
    """Desired fixture TCP pose plus the speed caps for reaching it."""

    target: Pose
    max_linear_speed: float  # m/s
    max_angular_speed: float  # rad/s


@dataclass(frozen=True)
class ControllerContext:
    """A-priori knowledge available to a controller (no ground truth)."""

    connector: ConnectorSpec  # nominal product geometry (from the drawing)
    nominal_socket_pose: Pose  # taught / programmed socket pose
    home_pose: Pose  # fixture TCP pose at cycle start
    control_period_s: float
    fixture: FixtureConfig
    vision_accuracy: SensorNoiseConfig  # characterized accuracy of the vision system
    fixture_dynamics: "FixtureDynamics | None" = None  # the machine actually pushing (W5)


@dataclass
class ControllerEvent:
    t: float
    kind: str
    detail: str = ""


class InsertionController(ABC):
    """Base class: produces one :class:`Command` per control tick."""

    name: str = "base"
    label: str = "Base controller"
    compliant_wrist: bool = False  # runs on the passive RCC stage (hardware choice, baselines E and F)

    def __init__(self) -> None:
        self.ctx: ControllerContext | None = None
        self.done = False
        self.declared_success: bool | None = None  # None: controller does not self-verify
        self.failure_reason: str | None = None
        self.state = "IDLE"
        self.retries = 0
        self.events: list[ControllerEvent] = []
        self.done_time: float | None = None
        self.markers: dict[str, Pose] = {}  # optional visualization targets

    def reset(self, ctx: ControllerContext) -> None:
        self.ctx = ctx
        self.done = False
        self.declared_success = None
        self.failure_reason = None
        self.state = "IDLE"
        self.retries = 0
        self.events = []
        self.done_time = None
        self.markers = {}

    @abstractmethod
    def step(self, obs: Observation) -> Command: ...

    # ------------------------------------------------------------------ helpers
    def log(self, t: float, kind: str, detail: str = "") -> None:
        self.events.append(ControllerEvent(t, kind, detail))

    def set_state(self, t: float, state: str, detail: str = "") -> None:
        if state != self.state:
            self.state = state
            self.log(t, "state", f"{state}{(': ' + detail) if detail else ''}")

    def finish(self, t: float, success: bool | None, reason: str | None = None) -> None:
        self.done = True
        self.done_time = t
        self.declared_success = success
        self.failure_reason = reason
        self.log(t, "finish", f"success={success} reason={reason}")

    @staticmethod
    def fixture_target_for_connector(connector_target: Pose, grasp_offset: Pose) -> Pose:
        """Fixture TCP pose that places the connector tip at ``connector_target``."""
        return connector_target @ grasp_offset.inv()

    @staticmethod
    def socket_frame_pose(socket_pose: Pose, xyz: np.ndarray, R_local: np.ndarray | None = None) -> Pose:
        """World pose of a connector-tip target expressed in a socket frame."""
        R = socket_pose.R if R_local is None else socket_pose.R @ R_local
        return Pose(socket_pose.apply(np.asarray(xyz, dtype=float)), R)


# Guarded-motion speed limits from the fixture's dynamics (W5). The reference values are
# those of the gantry the controllers were tuned on, so both rules are inactive there.
REFERENCE_EFFECTIVE_MASS_KG = 1.0  # gantry: 0.88 kg along z
FT_FILTER_DELAY_S = 1.0 / (2.0 * 3.141592653589793 * 40.0)  # 40 Hz first-order filter


def contact_speed_scale(ctx: ControllerContext) -> float:
    """Scale for speeds at which contact can occur: impact force ~ v sqrt(k m), so keep v sqrt(m)."""
    fd = ctx.fixture_dynamics
    if fd is None:
        return 1.0
    return min(1.0, (REFERENCE_EFFECTIVE_MASS_KG / fd.effective_mass_kg) ** 0.5)


def max_rotation_speed(ctx: ControllerContext, torque_budget_nm: float) -> float:
    """rad/s such that stiffness x speed x reaction time stays within the torque budget."""
    fd = ctx.fixture_dynamics
    if fd is None:
        return float("inf")
    reaction = fd.command_latency_s + FT_FILTER_DELAY_S + ctx.control_period_s
    return torque_budget_nm / (fd.yaw_stiffness_nm_per_rad * reaction)
