"""Controller interface shared by all insertion strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from defex.config import ConnectorSpec, FixtureConfig, SensorNoiseConfig
from defex.perception.state_estimator import Observation
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


@dataclass
class ControllerEvent:
    t: float
    kind: str
    detail: str = ""


class InsertionController(ABC):
    """Base class: produces one :class:`Command` per control tick."""

    name: str = "base"
    label: str = "Base controller"

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
