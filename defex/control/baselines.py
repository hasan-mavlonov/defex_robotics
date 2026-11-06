"""Baseline controllers.

* **Controller A, fixed trajectory**: a taught, open-loop program. It moves to a
  point above the *nominal* socket pose and inserts straight down to the nominal
  seat depth plus a small programmed overtravel. No sensing is used. This is how
  conventional fixed automation is programmed.
* **Controller B, position correction**: vision-guided automation. It reads the
  socket pose estimate (and the in-hand connector estimate) once, corrects the
  approach pose and insertion axis accordingly, then executes the same
  position-controlled insertion. It has no force feedback and no recovery.

Both rely on the cell-level protective stop (in the task harness) for safety,
exactly like a conventional robot program relying on the robot's collision stop.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from defex.config import (
    DEG,
    MM,
    FixedTrajectoryConfig,
    PassiveComplianceConfig,
    PassiveComplianceStiffFixtureConfig,
    PositionCorrectionConfig,
)
from defex.control.base import Command, ControllerContext, InsertionController, outside_reference_family
from defex.perception.state_estimator import Observation
from defex.utils.transforms import Pose


@dataclass(frozen=True)
class _Waypoint:
    name: str
    target: Pose  # fixture TCP target (world)
    speed: float  # m/s


class _WaypointProgram(InsertionController):
    """Executes a list of fixture waypoints followed by a dwell."""

    dwell_s: float = 0.3

    def __init__(self) -> None:
        super().__init__()
        self._waypoints: list[_Waypoint] = []
        self._idx = 0
        self._dwell_start: float | None = None

    def reset(self, ctx: ControllerContext) -> None:
        super().reset(ctx)
        self._waypoints = []
        self._idx = 0
        self._dwell_start = None

    def _plan(self, obs: Observation) -> list[_Waypoint]:
        raise NotImplementedError

    def step(self, obs: Observation) -> Command:
        if not self._waypoints:
            self._waypoints = self._plan(obs)
            self.set_state(obs.t, self._waypoints[0].name.upper())
        ang_speed = self.ctx.fixture.max_angular_speed_deg_s * DEG
        if self._idx < len(self._waypoints):
            wp = self._waypoints[self._idx]
            reached = np.linalg.norm(obs.setpoint.p - wp.target.p) < 1e-6 and np.allclose(
                obs.setpoint.R, wp.target.R, atol=1e-6
            )
            if reached:
                self._idx += 1
                if self._idx < len(self._waypoints):
                    wp = self._waypoints[self._idx]
                    self.set_state(obs.t, wp.name.upper())
                else:
                    self._dwell_start = obs.t
                    self.set_state(obs.t, "DWELL")
            return Command(wp.target, wp.speed, ang_speed)
        last = self._waypoints[-1]
        if not self.done and obs.t - self._dwell_start >= self.dwell_s:
            self.set_state(obs.t, "DONE")
            self.finish(obs.t, success=None)
        return Command(last.target, last.speed, ang_speed)


def taught_overtravel(ctx: ControllerContext, programmed_mm: float) -> float:
    """Overtravel (mm) a position program needs to reach the connector's insertion force (W3).

    An integrator teaches the program to push hard enough to seat the part: with a
    force budget, the servo deflection that produces the insertion target force.
    """
    budget = ctx.connector.force_budget
    if budget is None:
        return programmed_mm
    k = ctx.fixture_dynamics.translational_stiffness_n_per_mm if ctx.fixture_dynamics else 10.0
    if ctx.insertion_stiffness_n_per_mm is not None:  # v0.2d: the axis the program pushes along
        k = ctx.insertion_stiffness_n_per_mm
    return max(programmed_mm, budget.insert_target_n / k)


class FixedTrajectoryController(_WaypointProgram):
    name = "fixed"
    label = "A: Fixed trajectory"

    def __init__(self, cfg: FixedTrajectoryConfig | None = None) -> None:
        super().__init__()
        self.cfg = cfg or FixedTrajectoryConfig()
        self.dwell_s = self.cfg.dwell_s

    def _plan(self, obs: Observation) -> list[_Waypoint]:
        c = self.cfg
        S = self.ctx.nominal_socket_pose  # taught pose, never re-measured
        depth = self.ctx.connector.depth
        above = self.socket_frame_pose(S, [0.0, 0.0, c.approach_height_mm * MM])
        seat = self.socket_frame_pose(S, [0.0, 0.0, -(depth + taught_overtravel(self.ctx, c.overtravel_mm) * MM)])
        self.markers = {"target": S}
        # Nominal grasp assumed: connector tip == fixture TCP.
        return [
            _Waypoint("approach", above, c.transit_speed_mm_s * MM),
            _Waypoint("insert", seat, c.insert_speed_mm_s * MM),
        ]


class PositionCorrectionController(_WaypointProgram):
    name = "correction"
    label = "B: Vision position correction"

    def __init__(self, cfg: PositionCorrectionConfig | None = None) -> None:
        super().__init__()
        self.cfg = cfg or PositionCorrectionConfig()
        self.dwell_s = self.cfg.dwell_s

    def _plan(self, obs: Observation) -> list[_Waypoint]:
        c = self.cfg
        S = obs.socket_pose  # vision estimate
        G = obs.grasp_offset  # in-hand estimate
        depth = self.ctx.connector.depth
        above = self.socket_frame_pose(S, [0.0, 0.0, c.approach_height_mm * MM])
        seat = self.socket_frame_pose(S, [0.0, 0.0, -(depth + taught_overtravel(self.ctx, c.overtravel_mm) * MM)])
        self.markers = {"target": S}
        return [
            _Waypoint("approach", self.fixture_target_for_connector(above, G), c.transit_speed_mm_s * MM),
            _Waypoint("insert", self.fixture_target_for_connector(seat, G), c.insert_speed_mm_s * MM),
        ]


class PassiveComplianceController(PositionCorrectionController):
    """Controller E: B's vision-corrected program on a passive RCC stage, no force feedback.

    The stage (``defex.config.CompliantStageConfig``) lets the chamfer steer the plug
    laterally and in torsion with less force, as a remote center compliance device
    does on a conventional cell.
    """

    name = "correction_rcc"
    label = "E: Vision correction + passive compliance"
    compliant_wrist = True

    def __init__(
        self, cfg: PassiveComplianceConfig | None = None, stiff_fixture_cfg: PassiveComplianceConfig | None = None
    ) -> None:
        super().__init__(cfg or PassiveComplianceConfig())
        # v0.2c: settings for fixtures outside the gantry family (the UR5e), tuned there.
        self.stiff_fixture_cfg = stiff_fixture_cfg or PassiveComplianceStiffFixtureConfig()

    def reset(self, ctx: ControllerContext) -> None:
        super().reset(ctx)
        # Per-machine program (v0.2c): the config set by the user or a script on every gantry,
        # stiff_fixture_cfg on fixtures outside the gantry family. Never compounds across resets.
        if getattr(self, "_machine_cfg", None) is not self.cfg:
            self._user_cfg = self.cfg
        c = self._user_cfg
        if outside_reference_family(ctx, c.stiff_wrist_min_ratio, c.lagging_servo_min_ratio):
            c = self.stiff_fixture_cfg
        self.cfg = self._machine_cfg = c
        self.dwell_s = c.dwell_s
