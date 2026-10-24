"""Controller C: Defex Adaptive Insertion Engine (DAIE) finite-state machine.

    APPROACH -> ALIGN -> INSERT -> DETECT -> {VERIFY | RECOVER}
    RECOVER  -> ALIGN (retry)            VERIFY -> {SUCCESS | RECOVER}
    any      -> FAILURE (force / time / retry limits)

* APPROACH: transit above the vision-estimated socket, aligning the connector
  axis and yaw with the estimate.
* ALIGN: move to the current probe position above the mouth, settle, and tare
  the wrench in free space.
* INSERT: force-guided descent along the estimated socket axis with active
  compliance (lateral + yaw admittance on contact, tilt admittance once the plug
  is confidently inside the cavity). The failure detector watches progress and
  limits.
* DETECT: hold and diagnose the contact state. A plug stopped on the top face is
  first allowed to *conform* (zero-spring tilt admittance) so that the measured
  center of pressure reflects the support geometry rather than the residual tilt
  error; a flat conform also measures that tilt error, which is folded into the
  reference.
* RECOVER: retract along the axis, update the contact-based hole localizer (or
  re-aim using the orientation learned through compliance after a jam), choose a
  bounded correction, and retry.
* VERIFY: bottoming signature, seat conform (tilt aligned to the floor), guarded
  lateral probes along the socket's short axis (both opposing walls must push back
  within the clearance budget, which proves the plug is captured by the cavity;
  their positions also center it) and, when the vision yaw is uncertain, yaw
  centering between the rotational limits.

Depth estimates are only as good as the vision height estimate until the top
face has been touched, so every depth-based decision uses an explicit depth
uncertainty (vision sigma, then 0.1 mm after touch calibration).

Recovery is triggered and steered exclusively by observations (F/T wrench,
encoder-based pose, one-shot vision estimate). The controller never sees the
true disturbance and never re-measures with vision.
"""

from __future__ import annotations

from collections import deque

import numpy as np

from defex.config import DEG, MM, AdaptiveConfig
from defex.control.base import Command, ControllerContext, InsertionController
from defex.control.compliance import Admittance, ForceGuidedAxis
from defex.perception.state_estimator import Observation
from defex.recovery.failure_detector import ContactDiagnoser, ContactDiagnosis, InsertionMonitor
from defex.recovery.search_policy import YAW_SEARCH_SEQUENCE_DEG, HoleLocalizer
from defex.utils.transforms import Pose, matrix_to_rotvec, norm3, rot_z, rotvec_to_matrix

APPROACH, ALIGN, INSERT, DETECT, RECOVER, VERIFY, SUCCESS, FAILURE = (
    "APPROACH",
    "ALIGN",
    "INSERT",
    "DETECT",
    "RECOVER",
    "VERIFY",
    "SUCCESS",
    "FAILURE",
)
FSM_STATES = (APPROACH, ALIGN, INSERT, DETECT, RECOVER, VERIFY, SUCCESS, FAILURE)


class AdaptiveInsertionController(InsertionController):
    name = "adaptive"
    label = "C: Defex adaptive (DAIE)"

    def __init__(self, cfg: AdaptiveConfig | None = None) -> None:
        super().__init__()
        self.cfg = cfg or AdaptiveConfig()
        c = self.cfg
        self.monitor = InsertionMonitor(c)
        self.diagnoser = ContactDiagnoser(c)
        self.force_axis = ForceGuidedAxis(c.force_gain_mm_s_per_n * MM, c.max_insert_speed_mm_s * MM, 4.0 * MM)
        self.adm_lat = Admittance(
            c.lateral_stiffness_n_per_mm / MM, c.lateral_damping_n_s_per_mm / MM, c.max_lateral_compliance_mm * MM, 2
        )
        self.adm_rot = Admittance(c.rot_stiffness_nm_per_rad, c.rot_damping_nm_s_per_rad, c.max_rot_compliance_deg * DEG, 3)
        # Zero-spring tilt admittance used to conform the plug face to the top surface.
        self.adm_conf = Admittance(0.0, c.conform_damping_nm_s_per_rad, c.conform_limit_deg * DEG, 3)

    # ------------------------------------------------------------------ lifecycle
    def reset(self, ctx: ControllerContext) -> None:
        super().reset(ctx)
        c = self.cfg
        spec = ctx.connector
        self.S: Pose | None = None
        self.G: Pose | None = None
        self.xy = np.zeros(2)
        self.z = 0.0
        self.R_corr = np.eye(3)
        self.yaw_adj = 0.0
        self.adm_lat.reset()
        self.adm_rot.reset()
        self.adm_conf.reset()
        self.bias_f = np.zeros(3)
        self.bias_t = np.zeros(3)
        self._tare_buf: list[tuple[np.ndarray, np.ndarray]] = []
        self.depth_offset = 0.0  # touch calibration: depth reading at the true mouth plane
        self.touch_calibrated = False
        self.sigma_z = ctx.vision_accuracy.vision_z_sigma_mm * MM
        self.yaw_sigma = ctx.vision_accuracy.vision_yaw_sigma_deg * DEG
        self.depth = spec.depth
        self.plug_half = spec.plug_half[:2]
        self.t_start = 0.0
        self.attempts = 0
        self.yaw_search_idx = 0
        self.yaw_offset = 0.0
        self.blocks_at_best = 0
        self._blocked_probes: list[np.ndarray] = []
        self.diagnosis: ContactDiagnosis | None = None
        self.phase = ""
        self.phase_t = 0.0
        self._trigger = ""
        self._window: list[Observation] = []
        self._recent: deque[Observation] = deque(maxlen=25)
        self._contact = False
        self._conf_hist: deque[tuple[float, np.ndarray]] = deque()
        self._conf_saturated = False
        self._conf_depth0 = 0.0
        self._verify_dirs: list[np.ndarray] = []
        self._verify_base = np.zeros(2)
        self._preload_unsettled_t = 0.0
        self._verify_results: list[tuple[float, float]] = []
        self._yaw_results: list[float] = []
        self._yaw_base = 0.0
        self._bottom_since: float | None = None
        sigma_xy = max(ctx.vision_accuracy.vision_xy_sigma_mm, 0.15) * MM
        bias = ctx.vision_accuracy.vision_bias_mm * MM
        self.localizer = HoleLocalizer(
            spec,
            prior_sigma=float(np.hypot(1.3 * sigma_xy, bias)),
            extent=c.search_extent_mm * MM,
            resolution=c.search_resolution_mm * MM,
            cop_sigma=c.cop_sigma_mm * MM,
        )
        self.verify_probe = max(c.verify_probe_mm, 2.0 * spec.socket.clearance_mm + 0.35) * MM

    # ------------------------------------------------------------------ helpers
    def _wrench(self, obs: Observation) -> tuple[np.ndarray, np.ndarray]:
        return obs.force - self.bias_f, obs.torque - self.bias_t

    def _corrected_depth(self, obs: Observation) -> float:
        return obs.depth - self.depth_offset

    def _sigma_depth(self) -> float:
        return 0.1 * MM if self.touch_calibrated else self.sigma_z

    def _engaged(self, depth: float) -> bool:
        """Confidently inside the cavity (accounting for depth uncertainty)."""
        return depth > self.cfg.engage_depth_mm * MM + 3.0 * self._sigma_depth()

    def _seat_threshold(self) -> float:
        return self.depth - self.cfg.seat_depth_margin_mm * MM - 2.5 * self._sigma_depth()

    def _mouth_z(self) -> float:
        """Height of the true mouth plane in the estimated socket frame (conservative)."""
        return -self.depth_offset if self.touch_calibrated else 3.0 * self.sigma_z

    def _target(self) -> Pose:
        xy = self.xy + self.adm_lat.x
        R_local = (
            rotvec_to_matrix(self.adm_rot.x) @ rotvec_to_matrix(self.adm_conf.x) @ rot_z(self.yaw_adj) @ self.R_corr
        )
        conn = Pose(self.S.apply(np.array([xy[0], xy[1], self.z])), self.S.R @ R_local)
        return self.fixture_target_for_connector(conn, self.G)

    def _cmd(self, speed_mm_s: float) -> Command:
        target = self._target()
        self.markers["target"] = target @ self.G
        return Command(target, speed_mm_s * MM, self.ctx.fixture.max_angular_speed_deg_s * DEG)

    def _reached(self, obs: Observation, tol: float = 2e-6, rot_tol: float = 1e-4) -> bool:
        target = self._target()
        dp = norm3(obs.setpoint.p - target.p)
        dr = norm3(matrix_to_rotvec(target.R @ obs.setpoint.R.T))
        return dp < tol and dr < rot_tol

    def _enter(self, t: float, state: str, phase: str = "", detail: str = "") -> None:
        self.set_state(t, state, detail)
        self.phase = phase
        self.phase_t = t

    def _fail(self, obs: Observation, reason: str) -> Command:
        self.log(obs.t, "abort", reason)
        self._fail_reason = reason
        self._enter(obs.t, FAILURE, "retract", reason)
        return self._failure_step(obs)

    # ------------------------------------------------------------------ main step
    def step(self, obs: Observation) -> Command:
        c = self.cfg
        if self.S is None:
            self.S = obs.socket_pose
            self.G = obs.grasp_offset
            self.t_start = obs.t
            self.z = c.approach_height_mm * MM + 3.0 * self.sigma_z
            self._enter(obs.t, APPROACH)
        self._recent.append(obs)
        if self.state not in (SUCCESS, FAILURE) and obs.t - self.t_start > c.time_limit_s:
            return self._fail(obs, "time_limit")
        handler = {
            APPROACH: self._approach_step,
            ALIGN: self._align_step,
            INSERT: self._insert_step,
            DETECT: self._detect_step,
            RECOVER: self._recover_step,
            VERIFY: self._verify_step,
            SUCCESS: self._success_step,
            FAILURE: self._failure_step,
        }[self.state]
        return handler(obs)

    # ------------------------------------------------------------------ APPROACH / ALIGN
    def _approach_step(self, obs: Observation) -> Command:
        if self._reached(obs):
            self._enter(obs.t, ALIGN, "settle")
            self._tare_buf = []
        return self._cmd(self.cfg.transit_speed_mm_s)

    def _align_step(self, obs: Observation) -> Command:
        c = self.cfg
        if self.phase == "move":
            if self._reached(obs):
                self.phase, self.phase_t = "settle", obs.t
                self._tare_buf = []
            return self._cmd(c.reposition_speed_mm_s)
        # settle + free-space tare of the wrench (removes residual gravity/orientation error)
        if obs.t - self.phase_t > 0.06:
            self._tare_buf.append((obs.force.copy(), obs.torque.copy()))
        if obs.t - self.phase_t > 0.12:
            if self._tare_buf:
                self.bias_f = np.mean([f for f, _ in self._tare_buf], axis=0)
                self.bias_t = np.mean([t for _, t in self._tare_buf], axis=0)
            self.attempts += 1
            self.log(
                obs.t,
                "attempt",
                f"#{self.attempts} probe=({self.xy[0] / MM:+.2f},{self.xy[1] / MM:+.2f}) mm "
                f"yaw_corr={matrix_to_rotvec(self.R_corr)[2] / DEG:+.1f} deg",
            )
            self.monitor.reset(obs.t)
            self._contact = False
            self._bottom_since = None
            self._enter(obs.t, INSERT)
        return self._cmd(c.reposition_speed_mm_s)

    # ------------------------------------------------------------------ INSERT
    def _insert_step(self, obs: Observation) -> Command:
        c = self.cfg
        dt = self.ctx.control_period_s
        F, T = self._wrench(obs)
        f_ax = float(F[2])
        depth = self._corrected_depth(obs)
        # contact state with hysteresis
        if f_ax > c.contact_force_n or norm3(F) > 1.5 * c.contact_force_n:
            self._contact = True
        elif f_ax < 0.5 * c.contact_force_n and norm3(F) < 0.75 * c.contact_force_n:
            self._contact = False
        engaged = self._engaged(depth)
        near_bottom = depth > self.depth - (2.0 * MM + 3.0 * self._sigma_depth())
        if self._contact:
            v = self.force_axis.velocity(c.insert_force_n, f_ax)
            self.adm_lat.update(F[:2], dt)
            self.adm_rot.update(T, dt, active=np.array([engaged, engaged, True], dtype=float))
        elif not engaged and depth < c.engage_depth_mm * MM + 3.0 * self._sigma_depth():
            v = c.max_insert_speed_mm_s * MM
        elif near_bottom:
            v = 5.0 * MM
        else:
            v = 15.0 * MM
        self.z -= v * dt
        # Bottoming: deep enough and pushing at the target force -> diagnose quickly.
        if depth >= self._seat_threshold() and f_ax > 0.8 * c.insert_force_n:
            if self._bottom_since is None:
                self._bottom_since = obs.t
            elif obs.t - self._bottom_since > 0.08:
                return self._to_detect(obs, "bottomed")
        else:
            self._bottom_since = None
        reason = self.monitor.update_values(obs.t, depth, F, T, c.insert_force_n)
        if reason is not None:
            return self._to_detect(obs, reason)
        return self._cmd(30.0)

    # ------------------------------------------------------------------ DETECT
    def _to_detect(self, obs: Observation, trigger: str) -> Command:
        self._window = []
        self._trigger = trigger
        self._enter(obs.t, DETECT, "hold", trigger)
        if trigger.startswith("excess"):
            # Do not keep pressing: diagnose from the most recent samples and back off.
            self.diagnosis = self._diagnose(list(self._recent)[-10:], trigger)
            self.log(obs.t, "detect", self.diagnosis.describe())
            return self._begin_recover(obs)
        return self._cmd(30.0)

    def _diagnose(self, window: list[Observation], trigger: str) -> ContactDiagnosis:
        forces, torques = [], []
        for o in window:
            F, T = self._wrench(o)
            forces.append(F)
            torques.append(T)
        return self.diagnoser.diagnose_values(
            [o.t for o in window],
            [o.depth for o in window],
            [o.lateral for o in window],
            forces,
            torques,
            self.depth_offset,
            self._seat_threshold(),
            trigger,
            engage_threshold=self.cfg.engage_depth_mm * MM + 3.0 * self._sigma_depth(),
        )

    def _detect_step(self, obs: Observation) -> Command:
        c = self.cfg
        dt = self.ctx.control_period_s
        if self.phase == "hold":
            self._window.append(obs)
            depth = self._corrected_depth(obs)
            possibly_surface = not self._engaged(depth) and depth < self._seat_threshold()
            if possibly_surface and obs.t - self.phase_t >= 0.04:
                # Possibly stopped on the top face: let the plug face conform first so the
                # center of pressure reflects the support geometry, not the tilt error.
                self.adm_conf.reset()
                self._conf_hist.clear()
                self._conf_saturated = False
                self._conf_depth0 = depth
                self.phase, self.phase_t = "conform", obs.t
                return self._cmd(30.0)
            hold = 0.05 if self._trigger == "bottomed" else c.detect_hold_s
            if obs.t - self.phase_t < hold:
                return self._cmd(30.0)
            return self._conclude_detect(obs, self._window[len(self._window) // 3 :])
        if self.phase == "conform":
            F, T = self._wrench(obs)
            self.z -= self.force_axis.velocity(c.conform_force_n, float(F[2])) * dt
            self.adm_conf.update(T, dt, active=np.array([1.0, 1.0, 0.0]))
            # Lateral and yaw compliance stay active: if conforming tips the plug onto
            # the lead-in, the chamfer reaction is allowed to guide it into the cavity.
            self.adm_lat.update(F[:2], dt)
            self.adm_rot.update(T, dt, active=np.array([0.0, 0.0, 1.0]))
            if self._corrected_depth(obs) - self._conf_depth0 > 0.8 * MM:
                self.log(obs.t, "conform", "plug slid into the lead-in: resuming insertion")
                self.monitor.reset(obs.t)
                self._enter(obs.t, INSERT)
                return self._cmd(30.0)
            self._conf_hist.append((obs.t, self.adm_conf.x.copy()))
            while self._conf_hist and obs.t - self._conf_hist[0][0] > 0.06:
                self._conf_hist.popleft()
            elapsed = obs.t - self.phase_t
            rate = norm3(self._conf_hist[-1][1] - self._conf_hist[0][1])
            saturated = norm3(self.adm_conf.x) >= 0.97 * c.conform_limit_deg * DEG
            if (elapsed > 0.1 and (rate < 0.03 * DEG or saturated)) or elapsed > c.conform_max_s:
                self._conf_saturated = saturated
                self.phase, self.phase_t = "measure", obs.t
                self._window = []
            return self._cmd(30.0)
        # measure: tilt frozen, keep the conform force, average the wrench
        F, T = self._wrench(obs)
        self.z -= self.force_axis.velocity(c.conform_force_n, float(F[2])) * dt
        self.adm_lat.update(F[:2], dt)
        self.adm_rot.update(T, dt, active=np.array([0.0, 0.0, 1.0]))
        if self._corrected_depth(obs) - self._conf_depth0 > 0.8 * MM:
            self.log(obs.t, "conform", "plug slid into the lead-in: resuming insertion")
            self.monitor.reset(obs.t)
            self._enter(obs.t, INSERT)
            return self._cmd(30.0)
        self._window.append(obs)
        if obs.t - self.phase_t < 0.1:
            return self._cmd(30.0)
        return self._conclude_detect(obs, self._window[len(self._window) // 3 :])

    def _surface_consistent(self, diag: ContactDiagnosis) -> bool:
        """Contact signature of a flat face resting on the top surface."""
        if diag.cop is None:
            return False
        px, py = self.plug_half
        inside_face = abs(diag.cop[0]) <= px + 0.3 * MM and abs(diag.cop[1]) <= py + 0.3 * MM
        lateral_small = float(np.hypot(*diag.lateral_force)) <= 0.35 * max(diag.axial_force, 1e-6) + 0.5
        return bool(inside_face and lateral_small)

    def _touch_calibrate(self, obs: Observation, diag: ContactDiagnosis) -> None:
        """Locate the true mouth plane from the support point on the (tilted) plug face.

        The top face is the highest solid surface near the mouth (lead-in contacts sit
        lower), so the calibration keeps the highest support observed so far.
        """
        rel = obs.rel_pose
        n = rel.R[:, 2]
        h = -(n[0] * diag.cop[0] + n[1] * diag.cop[1]) / max(n[2], 1e-6)
        offset = float(-(rel.p[2] + h))
        if not self.touch_calibrated:
            self.depth_offset = offset
            self.touch_calibrated = True
            self.log(obs.t, "touch_calibration", f"mouth {self.depth_offset / MM:+.2f} mm below vision estimate")
        elif offset < self.depth_offset - 0.15 * MM:
            self.log(obs.t, "touch_calibration", f"higher support found: mouth {offset / MM:+.2f} mm "
                                                 f"(was {self.depth_offset / MM:+.2f})")
            self.depth_offset = offset

    def _conclude_detect(self, obs: Observation, window: list[Observation]) -> Command:
        diag = self._diagnose(window, self._trigger)
        self.diagnosis = diag
        if self.phase in ("conform", "measure"):
            conf = self.adm_conf.x.copy()
            state = "tipped" if self._conf_saturated else "flat"
            self.log(obs.t, "conform", f"{state}, rotation=({conf[0] / DEG:+.2f},{conf[1] / DEG:+.2f}) deg")
            if diag.kind == "surface_block" and not self._surface_consistent(diag):
                diag.kind = "partial_jam"
                self.log(obs.t, "detect", "contact signature inconsistent with the top face: treated as in-cavity jam")
            if diag.kind == "surface_block":
                self._touch_calibrate(obs, diag)
                diag.depth = self._corrected_depth(obs)
                if not self._conf_saturated and norm3(np.append(diag.cop, 0.0)) < 0.4 * MM:
                    # Settled flat on the top face: that rotation measures the residual
                    # socket tilt. Fold it into the reference orientation.
                    self.R_corr = rotvec_to_matrix(conf) @ self.R_corr
                    self.adm_conf.reset()
                    self.log(obs.t, "surface_alignment", f"tilt corrected ({conf[0] / DEG:+.2f},{conf[1] / DEG:+.2f}) deg")
        self.log(obs.t, "detect", diag.describe())
        if diag.kind == "seated_candidate":
            lat = float(np.hypot(*diag.lateral_force))
            if lat <= 0.6 * diag.axial_force + 1.0:
                return self._begin_verify(obs)
            diag.kind = "partial_jam"
            self.log(obs.t, "detect", "deep stall with high lateral load: treated as jam")
        return self._begin_recover(obs)

    # ------------------------------------------------------------------ RECOVER
    def _begin_recover(self, obs: Observation) -> Command:
        self._enter(obs.t, RECOVER, "retract", self.diagnosis.kind)
        return self._recover_step(obs)

    def _retract_height(self) -> float:
        return self._mouth_z() + self.cfg.retract_clearance_mm * MM

    def _recover_step(self, obs: Observation) -> Command:
        c = self.cfg
        F, _ = self._wrench(obs)
        if norm3(F) > c.max_force_n * 1.2 and obs.t - self.phase_t > 0.3:
            return self._fail(obs, "stuck_during_retract")
        self.z = self._retract_height()
        if self._reached(obs, tol=5e-6, rot_tol=2e-3):
            return self._plan_correction(obs)
        return self._cmd(c.retract_speed_mm_s)

    def _plan_correction(self, obs: Observation) -> Command:
        c = self.cfg
        diag = self.diagnosis
        if self.attempts >= c.max_attempts:
            return self._fail(obs, "retry_limit")
        learned_rot = self.adm_rot.x.copy()
        learned_lat = self.adm_lat.x.copy()
        lim_xy = c.max_lateral_correction_mm * MM
        detail = ""
        if diag.kind in ("surface_block", "no_contact"):
            # A block where entry was expected is evidence of a yaw error (corners on the
            # lead-in) or a sticking lead-in; repeated surprises trigger the yaw search.
            if self.localizer.entry_probability_at(diag.probe_xy) > 0.6:
                self.blocks_at_best += 1
            # CoP reliability: a conform that settled flat (CoP ~ 0) or tipped onto a
            # pivot edge matches the contact model; an intermediate stop indicates mixed
            # support (top face + lead-in) whose CoP magnitude is biased.
            clean = self._conf_saturated or (diag.cop is not None and norm3(np.append(diag.cop, 0.0)) < 0.4 * MM)
            sigma = self.cfg.cop_sigma_mm * MM if clean else 1.2 * MM
            self.localizer.update_blocked(
                diag.probe_xy, diag.cop if diag.kind == "surface_block" else None, cop_sigma=sigma
            )
            self._blocked_probes.append(diag.probe_xy.copy())
            new_xy, p_cap = self.localizer.best_probe(lim_xy, exclude=self._blocked_probes)
            if self.blocks_at_best >= 2 and self.yaw_search_idx < len(YAW_SEARCH_SEQUENCE_DEG):
                self.yaw_offset = YAW_SEARCH_SEQUENCE_DEG[self.yaw_search_idx] * DEG
                self.yaw_search_idx += 1
                self.blocks_at_best = 0
                rv = matrix_to_rotvec(self.R_corr)
                rv[2] = float(np.clip(self.yaw_offset, -c.max_yaw_correction_deg * DEG, c.max_yaw_correction_deg * DEG))
                self.R_corr = rotvec_to_matrix(rv)
                detail = f"yaw search {self.yaw_offset / DEG:+.0f} deg; "
            self.xy = new_xy
            detail += f"localizer -> probe ({new_xy[0] / MM:+.2f},{new_xy[1] / MM:+.2f}) mm, P(entry)={p_cap:.2f}"
        elif diag.kind == "partial_jam":
            self.localizer.update_entered(diag.probe_xy)
            self.xy = np.clip(self.xy + learned_lat, -lim_xy, lim_xy)
            # Re-aim with the orientation found through compliance during the attempt.
            rv = matrix_to_rotvec(self.R_corr) + learned_rot
            tilt = float(np.hypot(rv[0], rv[1]))
            if tilt > c.max_tilt_correction_deg * DEG:
                rv[:2] *= c.max_tilt_correction_deg * DEG / tilt
            rv[2] = float(np.clip(rv[2], -c.max_yaw_correction_deg * DEG, c.max_yaw_correction_deg * DEG))
            self.R_corr = rotvec_to_matrix(rv)
            detail = f"jam: re-aim tilt=({rv[0] / DEG:+.1f},{rv[1] / DEG:+.1f}) yaw={rv[2] / DEG:+.1f} deg"
        else:  # verification failed or ambiguous
            detail = "retry at same probe"
        self.retries += 1
        self.log(obs.t, "recover", detail)
        self.adm_lat.reset()
        self.adm_rot.reset()
        self.adm_conf.reset()
        self.yaw_adj = 0.0
        self.z = self._retract_height()
        self._enter(obs.t, ALIGN, "move", f"retry {self.retries}")
        return self._cmd(c.reposition_speed_mm_s)

    # ------------------------------------------------------------------ VERIFY
    def _begin_verify(self, obs: Observation) -> Command:
        # Seat conformity first: zero-spring tilt compliance lets the plug face settle
        # flat on the cavity floor, aligning the connector axis with the true socket axis.
        self.adm_conf.reset()
        self._conf_hist.clear()
        self._enter(obs.t, VERIFY, "seat_conform")
        return self._verify_step(obs)

    def _verify_step(self, obs: Observation) -> Command:
        c = self.cfg
        dt = self.ctx.control_period_s
        F, T = self._wrench(obs)
        if self.phase == "seat_conform":
            self.z -= self.force_axis.velocity(c.insert_force_n, float(F[2])) * dt
            self.adm_conf.update(T, dt, active=np.array([1.0, 1.0, 0.0]))
            self.adm_lat.update(F[:2], dt)
            self._conf_hist.append((obs.t, self.adm_conf.x.copy()))
            while self._conf_hist and obs.t - self._conf_hist[0][0] > 0.06:
                self._conf_hist.popleft()
            elapsed = obs.t - self.phase_t
            rate = norm3(self._conf_hist[-1][1] - self._conf_hist[0][1])
            if (elapsed > 0.08 and rate < 0.03 * DEG) or elapsed > 0.8:
                conf = self.adm_conf.x
                self.log(obs.t, "seat_conform", f"tilt aligned to floor by ({conf[0] / DEG:+.2f},{conf[1] / DEG:+.2f}) deg")
                self.phase, self.phase_t = "preload", obs.t
                self._preload_unsettled_t = obs.t
            return self._cmd(30.0)
        if self.phase == "preload":
            self._hold_preload(F, dt)
            self.adm_lat.update(F[:2], dt)
            # The wall probes only mean something while floor friction (mu x axial
            # force) stays below the wall-reaction threshold, so wait until the axial
            # force has really come down from the seating force to the light preload
            # (the force loop's time constant is about 0.1 s).
            if abs(float(F[2]) - c.verify_preload_n) > 0.2:
                self._preload_unsettled_t = obs.t
            elapsed = obs.t - self.phase_t
            if (elapsed > 0.1 and obs.t - self._preload_unsettled_t >= 0.05) or elapsed > 0.8:
                self._verify_base = self.adm_lat.x.copy()
                # Probe along the socket's short axis (y): it carries the lighter gantry
                # axis (smaller wall-impact transients) and two opposing walls are enough
                # to prove the plug is captured by the cavity and to center it.
                self._verify_dirs = [np.array(d, dtype=float) for d in ((0, 1), (0, -1))]
                self._verify_results = []
                self.phase, self.phase_t = "probe_out", obs.t
            return self._cmd(30.0)
        if self.phase in ("probe_out", "probe_back", "center", "yaw_out", "yaw_back"):
            self._hold_preload(F, dt)
        if self.phase == "probe_out":
            # Guarded lateral probe: advance until the wall pushes back, or give up
            # once the travel exceeds the full clearance budget.
            d = self._verify_dirs[len(self._verify_results)]
            reaction = float(-np.dot(F[:2], d))
            travel = float(np.dot(self.adm_lat.x - self._verify_base, d))
            if reaction >= c.verify_force_n or travel >= self.verify_probe:
                self._verify_results.append((reaction, travel))
                self.phase, self.phase_t = "probe_back", obs.t
            else:
                self.adm_lat.x = self.adm_lat.x + d * c.verify_probe_speed_mm_s * MM * dt
            return self._cmd(c.verify_probe_speed_mm_s * 2.0)
        if self.phase == "probe_back":
            self.adm_lat.x = self._verify_base.copy()
            if self._reached(obs, tol=2e-5):
                if len(self._verify_results) == len(self._verify_dirs):
                    return self._lateral_verdict(obs)
                self.phase, self.phase_t = "probe_out", obs.t
            return self._cmd(c.verify_probe_speed_mm_s * 2.0)
        if self.phase == "center":
            if self._reached(obs, tol=2e-5):
                if self.yaw_sigma > c.yaw_center_gate_deg * DEG:
                    self._yaw_base = self.yaw_adj
                    self._yaw_results = []
                    self.phase, self.phase_t = "yaw_out", obs.t
                else:
                    return self._succeed(obs)
            return self._cmd(c.verify_probe_speed_mm_s * 2.0)
        if self.phase == "yaw_out":
            sgn = 1.0 if not self._yaw_results else -1.0
            reaction = -float(T[2]) * sgn
            swept = (self.yaw_adj - self._yaw_base) * sgn
            if reaction >= c.yaw_probe_torque_nm or swept >= c.yaw_probe_max_deg * DEG:
                self._yaw_results.append(self.yaw_adj - self._yaw_base)
                self.phase, self.phase_t = "yaw_back", obs.t
            else:
                self.yaw_adj += sgn * c.yaw_probe_speed_deg_s * DEG * dt
            return self._cmd(10.0)
        if self.phase == "yaw_back":
            if len(self._yaw_results) == 2:
                lo, hi = sorted(self._yaw_results)
                self.yaw_adj = self._yaw_base + 0.5 * (lo + hi)
                if self._reached(obs, tol=2e-5, rot_tol=2e-4):
                    self.log(
                        obs.t,
                        "yaw_centering",
                        f"limits ({lo / DEG:+.1f},{hi / DEG:+.1f}) deg -> corrected {0.5 * (lo + hi) / DEG:+.2f} deg",
                    )
                    return self._succeed(obs)
            else:
                self.yaw_adj = self._yaw_base
                if self._reached(obs, tol=2e-5, rot_tol=2e-4):
                    self.phase, self.phase_t = "yaw_out", obs.t
            return self._cmd(10.0)
        return self._cmd(30.0)

    def _hold_preload(self, F: np.ndarray, dt: float) -> None:
        """Regulate the light axial preload used during verification probes."""
        self.z -= self.force_axis.velocity(self.cfg.verify_preload_n, float(F[2])) * dt

    def _lateral_verdict(self, obs: Observation) -> Command:
        c = self.cfg
        reactions = [r for r, _ in self._verify_results]
        travels = [tr for _, tr in self._verify_results]
        ok = all(r >= c.verify_force_n for r in reactions)
        self.log(
            obs.t,
            "verify",
            f"wall reactions {[round(r, 1) for r in reactions]} N at travel {[round(t / MM, 2) for t in travels]} mm"
            f" -> {'PASS' if ok else 'FAIL'}",
        )
        if not ok:
            self.diagnosis = ContactDiagnosis(
                "verify_failed", self._corrected_depth(obs), 0.0, np.zeros(2), np.zeros(3), None, obs.lateral.copy(), "verify"
            )
            self._enter(obs.t, RECOVER, "retract", "verify_failed")
            return self._recover_step(obs)
        # Center the plug between the two walls that were just located.
        cy = 0.5 * (travels[0] - travels[1])
        self.adm_lat.x = self._verify_base + np.array([0.0, cy])
        self.phase, self.phase_t = "center", obs.t
        return self._cmd(c.verify_probe_speed_mm_s * 2.0)

    def _succeed(self, obs: Observation) -> Command:
        self._enter(obs.t, SUCCESS)
        self.finish(obs.t, True)
        return self._cmd(10.0)

    # ------------------------------------------------------------------ terminal states
    def _success_step(self, obs: Observation) -> Command:
        F, _ = self._wrench(obs)
        v = self.force_axis.velocity(self.cfg.verify_preload_n, float(F[2]))
        self.z -= v * self.ctx.control_period_s
        return self._cmd(10.0)

    def _failure_step(self, obs: Observation) -> Command:
        # Back out along the current compliant pose, exactly as RECOVER's retract does.
        # The admittance offsets stay frozen: zeroing them while the plug is still in
        # the cavity commands a sudden re-orientation against the walls, and a wedged
        # plug then loads the wrist past the cell's torque stop.
        self.z = self._retract_height()
        if not self.done and self._reached(obs, tol=5e-6, rot_tol=2e-3):
            self.finish(obs.t, False, getattr(self, "_fail_reason", "unknown"))
        return self._cmd(self.cfg.retract_speed_mm_s)
