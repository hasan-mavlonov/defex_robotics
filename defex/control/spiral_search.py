"""Controllers D and F: force-controlled spiral search, the conventional cobot cell.

This is the insertion routine that cobot vendors ship (Flexiv Adaptive Assembly
SearchHole + InsertComp, Robotiq FT 300 Insertion node, UR force mode with a
spiral). It is the fair comparison for controller C, not a strawman:

    APPROACH -> TARE -> DESCEND -> {SPIRAL -> INSERT | INSERT} -> SUCCESS / FAILURE

* APPROACH: move above the vision-estimated socket, aligned with its estimated
  axis and yaw (as B).
* TARE: settle and zero the F/T sensor in free space (as vendor force modes do).
* DESCEND: guarded descent under force control until the axial force settles at
  the search force. A contact deeper than half the socket depth is the floor:
  the plug went straight in. Otherwise the plug is on the socket face.
* SPIRAL: Archimedean spiral in the socket plane at constant tangential speed,
  with the axial force held at the search force. The hole is found when the plug
  has pushed a set distance below the face height ("pushDistance" in Flexiv's
  SearchHole).
* INSERT: force-controlled insertion with compliant x/y (zero-force admittance,
  like the compliant axes of a force mode). Declares success when the depth below
  the face reaches the socket depth (less a margin) at the insertion force; a
  stall before that is a jam, which gets one more descent at the found position.

What it does not have, compared with C: no contact-based hole localization, no
yaw or tilt search, no tilt conform, and no verification beyond the depth window.
D runs on the stiff wrist; F is the same routine on the passive RCC stage.
"""

from __future__ import annotations

from collections import deque
from dataclasses import replace

import numpy as np

from defex.config import (
    AdaptiveConfig,
    DEG,
    MM,
    CompliantSpiralSearchConfig,
    CompliantSpiralSearchStiffFixtureConfig,
    SpiralSearchConfig,
    SpiralSearchStiffFixtureConfig,
)
from defex.control.base import (
    Command,
    ControllerContext,
    InsertionController,
    budgeted,
    contact_speed_scale,
    outside_reference_family,
)
from defex.control.compliance import Admittance, ForceGuidedAxis
from defex.perception.state_estimator import Observation
from defex.utils.transforms import Pose, norm3

APPROACH, TARE, DESCEND, SPIRAL, INSERT, SUCCESS, FAILURE = (
    "APPROACH",
    "TARE",
    "DESCEND",
    "SPIRAL",
    "INSERT",
    "SUCCESS",
    "FAILURE",
)
VERIFY = "VERIFY"  # only with SpiralSearchConfig.retention_pull (v0.2c review)


class SpiralSearchController(InsertionController):
    name = "spiral"
    label = "D: Spiral search"

    def __init__(self, cfg: SpiralSearchConfig | None = None, stiff_fixture_cfg: SpiralSearchConfig | None = None) -> None:
        super().__init__()
        self.cfg = cfg or SpiralSearchConfig()
        # v0.2c: settings for fixtures outside the gantry family (the UR5e), tuned there.
        self.stiff_fixture_cfg = stiff_fixture_cfg or SpiralSearchStiffFixtureConfig()

    def _machine_cfg(self, ctx: ControllerContext, cfg: SpiralSearchConfig) -> SpiralSearchConfig:
        """The config for this fixture: ``cfg`` on every gantry, ``stiff_fixture_cfg`` on the arm (v0.2c)."""
        if outside_reference_family(ctx, cfg.stiff_wrist_min_ratio, cfg.lagging_servo_min_ratio):
            return self.stiff_fixture_cfg
        return cfg

    def reset(self, ctx: ControllerContext) -> None:
        super().reset(ctx)
        # W3: same per-connector force budget as C (insertion force and abort threshold).
        self.cfg = budgeted(self, ctx, select=lambda cfg: self._machine_cfg(ctx, cfg),
                            insert_force_n="insert_target_n", max_force_n="abort_n")
        c = self.cfg
        self.S: Pose | None = None
        self.G: Pose | None = None
        self.depth = ctx.connector.depth
        self.sigma_z = ctx.vision_accuracy.vision_z_sigma_mm * MM
        self.xy = np.zeros(2)
        self.center = np.zeros(2)
        self.z = 0.0
        self.theta = 0.0
        self.face_depth: float | None = None
        self.attempts = 0
        self.bias_f = np.zeros(3)
        self.bias_t = np.zeros(3)
        self._tare: list[tuple[np.ndarray, np.ndarray]] = []
        self._phase_t = 0.0
        self._settled_since: float | None = None
        self._hist: deque[tuple[float, float]] = deque()
        self._fail_reason = ""
        self._pulled = False
        self._pull_retries_left = c.pull_retries
        s = contact_speed_scale(ctx)  # W5: same fixture-aware limit as C
        self._v_descent = c.descent_speed_mm_s * MM * s
        self._v_insert = c.insert_speed_mm_s * MM * s
        self._v_spiral = c.spiral_speed_mm_s * MM * s
        self._v_free = c.free_speed_mm_s * MM * s  # v0.2c two-speed guarded moves; 0 = off
        self._chamfer = ctx.connector.socket.chamfer_mm * MM
        self.force_axis = ForceGuidedAxis(c.force_gain_mm_s_per_n * MM, self._v_descent, 4.0 * MM)
        self.insert_axis = ForceGuidedAxis(c.force_gain_mm_s_per_n * MM, self._v_insert, 4.0 * MM)
        self.adm = Admittance(0.0, c.lateral_compliance_damping_n_s_per_mm / MM, c.max_lateral_compliance_mm * MM, 2)
        self.adm_search = Admittance(
            c.search_lateral_stiffness_n_per_mm / MM, c.lateral_compliance_damping_n_s_per_mm / MM,
            c.max_lateral_compliance_mm * MM, 2,
        )

    # ------------------------------------------------------------------ helpers
    def _wrench(self, obs: Observation) -> tuple[np.ndarray, np.ndarray]:
        return obs.force - self.bias_f, obs.torque - self.bias_t

    def _mouth_z(self) -> float:
        return 3.0 * self.sigma_z

    def _target(self) -> Pose:
        xy = self.xy + self.adm.x + self.adm_search.x
        conn = Pose(self.S.apply(np.array([xy[0], xy[1], self.z])), self.S.R)
        return self.fixture_target_for_connector(conn, self.G)

    def _cmd(self, speed_mm_s: float) -> Command:
        target = self._target()
        self.markers["target"] = target @ self.G
        return Command(target, speed_mm_s * MM, self.ctx.fixture.max_angular_speed_deg_s * DEG)

    def _free_or(self, v: float, depth: float, lo: float, hi: float) -> float:
        """Two-speed guarded move (v0.2c): the free speed while the depth is between lo and hi, else v."""
        return self._v_free if self._v_free > 0.0 and lo < depth < hi else v

    def _reached(self, obs: Observation, tol: float = 2e-6) -> bool:
        return norm3(obs.setpoint.p - self._target().p) < tol

    def _enter(self, t: float, state: str, detail: str = "") -> None:
        self.set_state(t, state, detail)
        self._phase_t = t
        self._settled_since = None
        self._hist.clear()

    def _fail(self, obs: Observation, reason: str) -> Command:
        self.log(obs.t, "abort", reason)
        self._fail_reason = reason
        self._enter(obs.t, FAILURE, reason)
        return self._failure_step(obs)

    def _limits(self, F: np.ndarray, T: np.ndarray) -> str | None:
        c = self.cfg
        if norm3(F) > c.max_force_n:
            return "excess_force"
        if norm3(T) > c.max_torque_nm:
            return "excess_torque"
        if float(np.hypot(F[0], F[1])) > c.max_lateral_force_n:
            return "excess_lateral_force"
        return None

    def _stalled(self, t: float, depth: float) -> bool:
        c = self.cfg
        self._hist.append((t, depth))
        while self._hist and t - self._hist[0][0] > c.stall_window_s:
            self._hist.popleft()
        if t - self._hist[0][0] < 0.98 * c.stall_window_s:
            return False
        return self._hist[-1][1] - self._hist[0][1] < c.stall_progress_mm * MM

    # ------------------------------------------------------------------ main step
    def step(self, obs: Observation) -> Command:
        c = self.cfg
        if self.S is None:
            self.S = obs.socket_pose
            self.G = obs.grasp_offset
            self.t_start = obs.t
            self.z = c.approach_height_mm * MM + self._mouth_z()
            self._enter(obs.t, APPROACH)
        if self.state not in (SUCCESS, FAILURE) and obs.t - self.t_start > c.time_limit_s:
            return self._fail(obs, "time_limit")
        handler = {
            APPROACH: self._approach_step,
            TARE: self._tare_step,
            DESCEND: self._descend_step,
            SPIRAL: self._spiral_step,
            INSERT: self._insert_step,
            VERIFY: self._pull_step,
            SUCCESS: self._success_step,
            FAILURE: self._failure_step,
        }[self.state]
        return handler(obs)

    def _approach_step(self, obs: Observation) -> Command:
        if self._reached(obs):
            self._tare = []
            self._enter(obs.t, TARE)
        return self._cmd(self.cfg.transit_speed_mm_s)

    def _tare_step(self, obs: Observation) -> Command:
        c = self.cfg
        el = obs.t - self._phase_t
        if el > c.tare_settle_s:
            self._tare.append((obs.force.copy(), obs.torque.copy()))
        if el > c.tare_settle_s + c.tare_average_s:
            self.bias_f = np.mean([f for f, _ in self._tare], axis=0)
            self.bias_t = np.mean([t for _, t in self._tare], axis=0)
            self.attempts += 1
            self.log(obs.t, "attempt", f"#{self.attempts} at ({self.xy[0] / MM:+.2f},{self.xy[1] / MM:+.2f}) mm")
            self._enter(obs.t, DESCEND)
        return self._cmd(self.cfg.transit_speed_mm_s)

    def _descend_step(self, obs: Observation) -> Command:
        c = self.cfg
        dt = self.ctx.control_period_s
        F, T = self._wrench(obs)
        reason = self._limits(F, T)
        if reason:
            return self._fail(obs, reason)
        f_ax = float(F[2])
        if f_ax < c.contact_force_n:
            v = self._v_descent  # guarded move until contact
            if self._v_free > 0.0:  # below the mouth band without contact: inside the cavity
                v = self._free_or(v, obs.depth, self._mouth_z() + self._chamfer,
                                  self.depth - c.near_floor_margin_mm * MM - 3.0 * self.sigma_z)
        else:
            v = self.force_axis.velocity(c.search_force_n, f_ax)
        self.z -= v * dt
        if obs.depth > self.depth + 2.0 * MM + 3.0 * self.sigma_z:
            return self._fail(obs, "no_contact")
        if f_ax >= 0.8 * c.search_force_n:
            if self._settled_since is None:
                self._settled_since = obs.t
            elif obs.t - self._settled_since > 0.05:
                if obs.depth > 0.5 * self.depth:
                    self.face_depth = None
                    if self.ctx.connector.mating is not None:
                        # Terminals, not the floor: keep inserting under force control (vendor
                        # linear insertion to a force or distance limit).
                        self.log(obs.t, "contact", f"deep contact at {obs.depth / MM:.2f} mm: inserting")
                        self.adm.reset()
                        self._enter(obs.t, INSERT)
                        return self._cmd(30.0)
                    self.log(obs.t, "contact", f"floor contact at depth {obs.depth / MM:.2f} mm: went straight in")
                    return self._check_seat(obs, obs.depth)
                if self.face_depth is None:
                    self.face_depth = obs.depth
                self.center = self.xy.copy()
                self.theta = 0.0
                self.log(obs.t, "contact", f"face at depth {obs.depth / MM:.2f} mm: spiral search")
                self._enter(obs.t, SPIRAL)
        else:
            self._settled_since = None
        return self._cmd(30.0)

    def _spiral_step(self, obs: Observation) -> Command:
        c = self.cfg
        dt = self.ctx.control_period_s
        F, T = self._wrench(obs)
        reason = self._limits(F, T)
        if reason:
            return self._fail(obs, reason)
        self.z -= self.force_axis.velocity(c.search_force_n, float(F[2])) * dt
        if c.search_lateral_stiffness_n_per_mm > 0.0:
            self.adm_search.update(F[:2], dt)
        if obs.depth - self.face_depth > c.hole_push_mm * MM:
            self.log(obs.t, "hole_found", f"pushed {(obs.depth - self.face_depth) / MM:.2f} mm at "
                                          f"({self.xy[0] / MM:+.2f},{self.xy[1] / MM:+.2f}) mm")
            if c.hole_at_measured_position:
                self.xy = np.asarray(obs.lateral, dtype=float).copy()
            else:
                self.xy = self.xy + self.adm_search.x
            self.adm_search.reset()
            self.adm.reset()
            self._enter(obs.t, INSERT)
            return self._cmd(30.0)
        b = c.spiral_pitch_mm * MM / (2.0 * np.pi)
        r = b * self.theta
        if r > c.spiral_max_radius_mm * MM:
            return self._fail(obs, "search_exhausted")
        self.theta += self._v_spiral * dt / max(np.hypot(r, b), 1e-9)
        r = b * self.theta
        self.xy = self.center + r * np.array([np.cos(self.theta), np.sin(self.theta)])
        return self._cmd(30.0)

    def _insert_step(self, obs: Observation) -> Command:
        c = self.cfg
        dt = self.ctx.control_period_s
        F, T = self._wrench(obs)
        reason = self._limits(F, T)
        if reason:
            return self._jam_or_fail(obs, reason)
        f_ax = float(F[2])
        if f_ax < c.contact_force_n:
            v = self._v_insert
            if self._v_free > 0.0 and self.face_depth is not None:  # floor = face + socket depth (measured)
                v = self._free_or(v, obs.depth, self.face_depth + self._chamfer,
                                  self.face_depth + self.depth - c.near_floor_margin_mm * MM)
        else:
            v = self.insert_axis.velocity(c.insert_force_n, f_ax)
        self.z -= v * dt
        self.adm.update(F[:2], dt)
        gain, need = self._seat_window(obs)
        if gain >= need and f_ax >= 0.8 * c.insert_force_n:
            if self._settled_since is None:
                self._settled_since = obs.t
            elif obs.t - self._settled_since > 0.08:
                self.log(obs.t, "seated", f"{gain / MM:.2f} mm below the face")
                return self._succeed(obs)
        else:
            self._settled_since = None
        if f_ax > 0.7 * c.insert_force_n and self._stalled(obs.t, obs.depth):
            return self._jam_or_fail(obs, "jam")
        return self._cmd(30.0)

    def _seat_window(self, obs: Observation) -> tuple[float, float]:
        """(Depth gained, depth needed) for INSERT's seat rule, from the encoders (and F/k on the RCC stage)."""
        c = self.cfg
        if self.face_depth is not None:
            return obs.depth - self.face_depth, self.depth - c.seat_margin_mm * MM
        # went straight in: depth from the vision estimate, window widened by its accuracy
        return obs.depth, self.depth - c.seat_margin_mm * MM - 3.0 * self.sigma_z

    def _check_seat(self, obs: Observation, depth: float) -> Command:
        c = self.cfg
        if depth >= self.depth - c.seat_margin_mm * MM - 3.0 * self.sigma_z:
            self.log(obs.t, "seated", f"floor at {depth / MM:.2f} mm (vision depth window)")
            return self._succeed(obs)
        return self._jam_or_fail(obs, "jam")

    def _jam_or_fail(self, obs: Observation, reason: str) -> Command:
        if self.attempts >= self.cfg.max_attempts:
            return self._fail(obs, reason)
        self.log(obs.t, "retry", f"{reason}: re-descend at ({self.xy[0] / MM:+.2f},{self.xy[1] / MM:+.2f}) mm")
        self.retries += 1
        self.xy = self.xy + self.adm.x
        self.adm.reset()
        self.z = self._mouth_z() + self.cfg.retract_clearance_mm * MM
        self._enter(obs.t, APPROACH, "retry")
        return self._cmd(self.cfg.retract_speed_mm_s)

    def _succeed(self, obs: Observation) -> Command:
        m = self.ctx.connector.mating
        if self.cfg.retention_pull and m is not None and not self._pulled:
            self._pulled = True
            self._pull_start = float(obs.depth)
            self._pull_target = max(self.cfg.pull_test_fraction * m.latch_retention_force_n,
                                    self.cfg.pull_test_mating_factor * m.mating_force_max_n)
            self._pull_limit = self.cfg.pull_limit_wipe_fraction * m.terminal_wipe_mm * MM
            self._pull_phase = "pull"
            self._enter(obs.t, VERIFY, "pull")
            return self._cmd(10.0)
        self._enter(obs.t, SUCCESS)
        self.finish(obs.t, True)
        return self._cmd(10.0)

    def _pull_step(self, obs: Observation) -> Command:
        """v0.2c review: guarded retention pull after the depth check, then re-seat (as C's latch check)."""
        c = self.cfg
        dt = self.ctx.control_period_s
        F, T = self._wrench(obs)
        f_ax = float(F[2])
        moved = self._pull_start - float(obs.depth)
        timed_out = obs.t - self._phase_t > c.pull_test_max_s
        if self._pull_phase == "pull":
            if c.verify_lateral_compliance:
                self.adm.update(F[:2], dt)
            self.z -= self.insert_axis.velocity(-self._pull_target, f_ax) * dt
            held = f_ax <= -self._pull_target
            if held or moved > self._pull_limit or timed_out:
                passed = held and moved <= self._pull_limit
                self.log(obs.t, "verify", f"pull {-f_ax:.1f} N at {moved / MM:.2f} mm -> {'PASS' if passed else 'FAIL'}")
                if not passed:
                    if self._pull_retries_left <= 0:
                        return self._fail(obs, "retention_failed")
                    self._pull_retries_left -= 1
                    self.retries += 1  # v0.2e: counted, as C's slide-out retry is
                    self._repush_t_force, self._repush_peak, self._repush_depth0 = None, 0.0, 0.0
                    self.log(obs.t, "retry", f"pull failed: push again at {c.insert_force_n:.1f} N and pull once more")
                    self._pull_phase, self._phase_t = "repush", obs.t
                    return self._cmd(10.0)
                self._pull_phase, self._phase_t = "reseat", obs.t
            return self._cmd(10.0)
        if self._pull_phase == "repush":  # as C's bottom proof push: capped speed, hold at the target, no stall exit
            reason = self._limits(F, T)
            if reason:
                return self._fail(obs, reason)
            self.z -= min(self.insert_axis.velocity(c.insert_force_n, f_ax), c.repush_speed_mm_s * MM) * dt
            if c.verify_lateral_compliance:
                self.adm.update(F[:2], dt)
            self._repush_peak = max(self._repush_peak, f_ax)
            if self._repush_t_force is not None and obs.depth - self._repush_depth0 > c.repush_advance_mm * MM:
                self._repush_t_force = None  # the plug is still going in (C: "not a hard stop"): keep pushing
            if f_ax >= 0.8 * c.insert_force_n and self._repush_t_force is None:
                self._repush_t_force, self._repush_depth0 = obs.t, float(obs.depth)
            held = self._repush_t_force is not None and obs.t - self._repush_t_force >= c.repush_hold_s
            if held or obs.t - self._phase_t > 2.0 * c.pull_test_max_s:
                head = (f"re-push {'held' if held else 'timed out'}, peak {self._repush_peak:.1f} N, "
                        f"now {f_ax:.1f} N at {obs.depth / MM:.2f} mm")
                if c.repush_seat_gate:
                    # As C after a held re-seat: the latch is checked only on a plug held at the push force at the
                    # seat depth (C: its seated_candidate gate; here INSERT's seat window). Otherwise rejected.
                    gain, need = self._seat_window(obs)
                    if not held:
                        self.log(obs.t, "verify", f"{head}: not held at the target, not checked")
                        return self._fail(obs, "repush_not_held")
                    if gain < need:
                        self.log(obs.t, "verify", f"{head}: {gain / MM:.2f} mm, short of the seat depth "
                                                  f"{need / MM:.2f} mm, not checked")
                        return self._fail(obs, "repush_short_of_seat")
                self.log(obs.t, "verify", f"{head}: pull again")
                self._pull_start = float(obs.depth)
                self._pull_phase, self._phase_t = "pull", obs.t
            return self._cmd(10.0)
        if c.verify_lateral_compliance:
            self.adm.update(F[:2], dt)
        self.z -= self.insert_axis.velocity(c.insert_force_n, f_ax) * dt
        back = float(obs.depth) >= self._pull_start - c.reseat_tolerance_mm * MM
        if (back and f_ax >= 0.8 * c.insert_force_n) or timed_out:
            return self._succeed(obs)
        return self._cmd(10.0)

    def _success_step(self, obs: Observation) -> Command:
        return self._cmd(10.0)

    def _failure_step(self, obs: Observation) -> Command:
        self.z = self._mouth_z() + self.cfg.retract_clearance_mm * MM
        if not self.done and self._reached(obs, tol=5e-6):
            self.finish(obs.t, False, self._fail_reason or "unknown")
        return self._cmd(self.cfg.retract_speed_mm_s)


class CompliantSpiralSearchController(SpiralSearchController):
    """Controller F: the spiral search routine on the passive RCC stage."""

    name = "spiral_rcc"
    label = "F: Spiral search + passive compliance"
    compliant_wrist = True

    def __init__(
        self, cfg: CompliantSpiralSearchConfig | None = None, stiff_fixture_cfg: CompliantSpiralSearchConfig | None = None
    ) -> None:
        super().__init__(cfg or CompliantSpiralSearchConfig(), stiff_fixture_cfg or CompliantSpiralSearchStiffFixtureConfig())


def _with_retention_pull(cfg: SpiralSearchConfig, retries: int = 0) -> SpiralSearchConfig:
    """C's installed latch check on a spiral cell: the same pull force and movement limit (datasheet-based).

    v0.2d: ``retries`` re-pushes after a failed pull, picked per controller and machine by
    results/v0.2d_pull_retry/SELECTION_RULE.md (version 4): on for H and I on both machines.
    v0.2e (rule version 5, results/v0.2e_pull_retry): the second pull only from the seat depth, and
    INSERT's lateral compliance through the pull, re-push and re-seat."""
    a = AdaptiveConfig()
    return replace(cfg, retention_pull=True, pull_test_mating_factor=a.pull_test_mating_factor,
                   pull_limit_wipe_fraction=a.pull_limit_wipe_fraction, pull_retries=retries,
                   repush_hold_s=a.proof_push_s, repush_speed_mm_s=a.proof_push_speed_mm_s,
                   repush_advance_mm=a.proof_advance_mm, repush_seat_gate=True, verify_lateral_compliance=True)


class SpiralSearchPullController(SpiralSearchController):
    """Controller H (v0.2c): D plus a retention pull after a latching insertion, as C does."""

    name = "spiral_pull"
    label = "H: Spiral search + retention pull"

    def __init__(self) -> None:
        super().__init__()
        self.cfg = _with_retention_pull(self.cfg, retries=1)
        self.stiff_fixture_cfg = _with_retention_pull(self.stiff_fixture_cfg, retries=1)


class CompliantSpiralSearchPullController(CompliantSpiralSearchController):
    """Controller I (v0.2c): F plus a retention pull after a latching insertion, as C does."""

    name = "spiral_rcc_pull"
    label = "I: Spiral search + passive compliance + retention pull"

    def __init__(self) -> None:
        super().__init__()
        self.cfg = _with_retention_pull(self.cfg, retries=1)  # gantry
        self.stiff_fixture_cfg = _with_retention_pull(self.stiff_fixture_cfg, retries=1)  # arm
