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
# W5b. C's admittance dampings were tuned against the gantry's 15 N m/rad wrist servos, and its
# guarded moves with the gantry's servo lag absorbed in their constants. The corrections scale with
# the excess over these values, and only switch on for fixtures at least a given ratio beyond them
# (AdaptiveConfig.stiff_wrist_min_ratio, lagging_servo_min_ratio), well outside the gantry family:
# no-ops on the nominal gantry and on every gantry of the simulator-randomization bands
# (experiments/sim_randomization.py), active on the UR5e arm.
REFERENCE_ROTATIONAL_STIFFNESS_NM_PER_RAD = 15.0  # gantry wrist servos (FixtureConfig.angular_kp_nm_per_rad)
REFERENCE_FOLLOWING_LAG_S = 0.04  # gantry: 0.037 s on its heaviest axis (x carriage), 0.019-0.024 s elsewhere


def budgeted(controller, ctx: ControllerContext, **fields_from_budget: str):
    """Controller config with force thresholds from the connector's force budget (W3).

    Starts from whatever config the controller holds at reset (scripts may swap it),
    never compounding an earlier override. ``fields_from_budget`` maps a config field
    to a ForceBudget attribute, e.g. insert_force_n="insert_target_n".
    """
    from dataclasses import replace

    if getattr(controller, "_budget_cfg", None) is not controller.cfg:
        controller._user_cfg = controller.cfg
    cfg = controller._user_cfg
    budget = ctx.connector.force_budget
    if budget is not None:
        cfg = replace(cfg, **{f: getattr(budget, b) for f, b in fields_from_budget.items()})
    controller._budget_cfg = cfg
    return cfg


def contact_speed_scale(ctx: ControllerContext) -> float:
    """Scale for speeds at which contact can occur: impact force ~ v sqrt(k m), so keep v sqrt(m)."""
    fd = ctx.fixture_dynamics
    if fd is None:
        return 1.0
    return min(1.0, (REFERENCE_EFFECTIVE_MASS_KG / fd.effective_mass_kg) ** 0.5)


def excess_following_lag(ctx: ControllerContext, min_ratio: float, rotational: bool = False) -> float:
    """Servo following lag beyond the reference fixture's (s), translational axes (rotational with
    ``rotational``). 0 unless the lag is at least ``min_ratio`` x the reference, and 0 when the
    fixture's lag is not characterized."""
    fd = ctx.fixture_dynamics
    if fd is None:
        return 0.0
    lag = fd.rotational_following_lag if rotational else fd.following_lag_s
    if lag is None or lag < min_ratio * REFERENCE_FOLLOWING_LAG_S:
        return 0.0
    return max(0.0, lag - REFERENCE_FOLLOWING_LAG_S)


def max_rotation_speed(ctx: ControllerContext, torque_budget_nm: float, min_lag_ratio: float) -> float:
    """rad/s such that stiffness x speed x (reaction time + excess rotational lag) stays within the torque budget.

    W5b: a guarded rotation that stops on a wall also unloads the setpoint lead it carried,
    speed x following lag, into the wall (the W5 rule had the reaction time only). The lag term
    follows :func:`excess_following_lag` (rotational axes, ``min_lag_ratio``).
    """
    fd = ctx.fixture_dynamics
    if fd is None:
        return float("inf")
    filter_delay = 1.0 / (2.0 * 3.141592653589793 * ctx.vision_accuracy.ft_filter_cutoff_hz)  # first-order F/T filter
    reaction = fd.command_latency_s + filter_delay + ctx.control_period_s
    lag = excess_following_lag(ctx, min_lag_ratio, rotational=True)
    return torque_budget_nm / (fd.yaw_stiffness_nm_per_rad * (reaction + lag))


def rotational_damping_scale(ctx: ControllerContext, min_ratio: float) -> tuple[float, float]:
    """(tilt, yaw) factors for rotational admittance damping that keep the loop gain
    stiffness / damping at its value on the reference wrist (W5b).

    Per axis: the stiffness over the reference wrist's when that ratio is at least ``min_ratio``,
    else 1 (a wrist within the gantry family keeps the dampings C was tuned with)."""
    fd = ctx.fixture_dynamics
    if fd is None:
        return 1.0, 1.0

    def factor(stiffness: float) -> float:
        r = stiffness / REFERENCE_ROTATIONAL_STIFFNESS_NM_PER_RAD
        return max(1.0, r) if r >= min_ratio else 1.0

    return factor(fd.tilt_stiffness), factor(fd.yaw_stiffness_nm_per_rad)
