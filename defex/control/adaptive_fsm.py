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
from defex.control.base import (
    Command,
    ControllerContext,
    InsertionController,
    budgeted,
    contact_speed_scale,
    excess_following_lag,
    max_rotation_speed,
    rotational_damping_scale,
)
from defex.control.compliance import Admittance, ForceGuidedAxis
from defex.perception.state_estimator import Observation
from defex.recovery.failure_detector import ContactDiagnoser, ContactDiagnosis, InsertionMonitor
from defex.recovery.search_policy import HoleLocalizer, yaw_search_sequence_deg
from defex.recovery.yaw_localizer import YawHoleLocalizer
from defex.utils.transforms import Pose, matrix_to_rotvec, norm3, rot_z, rotvec_to_matrix, twist_about_axis

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
_EPS = 1e-6  # guards divisions by a force or a direction component (numerical, not tuned)


class AdaptiveInsertionController(InsertionController):
    name = "adaptive"
    label = "C: Defex adaptive (DAIE)"

    def __init__(self, cfg: AdaptiveConfig | None = None) -> None:
        super().__init__()
        self.cfg = cfg or AdaptiveConfig()
        c = self.cfg
        self.monitor = InsertionMonitor(c)
        self.diagnoser = ContactDiagnoser(c)
        self.force_axis = ForceGuidedAxis(
            c.force_gain_mm_s_per_n * MM, c.max_insert_speed_mm_s * MM, c.max_back_off_speed_mm_s * MM
        )
        self.yaw_sequence = yaw_search_sequence_deg(c.yaw_search_step_deg, c.yaw_search_steps)
        self.adm_lat = Admittance(
            c.lateral_stiffness_n_per_mm / MM, c.lateral_damping_n_s_per_mm / MM, c.max_lateral_compliance_mm * MM, 2
        )
        self.adm_rot = Admittance(c.rot_stiffness_nm_per_rad, c.rot_damping_nm_s_per_rad, c.max_rot_compliance_deg * DEG, 3)
        # Zero-spring tilt admittance used to conform the plug face to the top surface.
        self.adm_conf = Admittance(0.0, c.conform_damping_nm_s_per_rad, c.conform_limit_deg * DEG, 3)
        self._adm_d0 = (self.adm_rot.d, self.adm_conf.d)

    # ------------------------------------------------------------------ lifecycle
    def reset(self, ctx: ControllerContext) -> None:
        super().reset(ctx)
        # W3: force thresholds from the connector's budget when it has one.
        self.cfg = budgeted(self, ctx, insert_force_n="insert_target_n", max_force_n="abort_n")
        c = self.cfg
        self.monitor = InsertionMonitor(c)
        self.diagnoser = ContactDiagnoser(c)
        spec = ctx.connector
        self.latching = spec.mating is not None and spec.mating.latch_retention_force_n > 0.0
        self._trace: list[tuple[float, float]] = []  # (depth, axial force) during INSERT, for the click
        # W5: bound contact speeds and yaw probing by the fixture actually pushing (no-ops on the gantry).
        s = contact_speed_scale(ctx)
        self._v_insert = c.max_insert_speed_mm_s * MM * s
        self._v_free = c.free_insert_speed_mm_s * MM * s
        self._v_near_bottom = c.near_bottom_speed_mm_s * MM * s
        self.force_axis = ForceGuidedAxis(c.force_gain_mm_s_per_n * MM, self._v_insert, c.max_back_off_speed_mm_s * MM)
        # Wall probes are guarded contact moves too. Kept as a separate factor so the
        # gantry (factor 1.0) computes exactly what it did before W5.
        self._probe_speed_mm_s = c.verify_probe_speed_mm_s * s
        self._yaw_probe_rate = min(
            c.yaw_probe_speed_deg_s * DEG,
            max_rotation_speed(ctx, c.rotation_budget_fraction * c.max_torque_nm, c.lagging_servo_min_ratio),
        )
        # W5b: keep the rotational admittance loop gains (stiffness / damping) at their value on the
        # reference wrist, on wrists at least stiff_wrist_min_ratio x as stiff. Both factors are exactly 1
        # on every gantry (nominal and randomized), which keeps its dampings untouched.
        s_tilt, s_yaw = rotational_damping_scale(ctx, c.stiff_wrist_min_ratio)
        if (s_tilt, s_yaw) == (1.0, 1.0):
            self.adm_rot.d, self.adm_conf.d = self._adm_d0
        else:
            self.adm_rot.d = c.rot_damping_nm_s_per_rad * np.array([s_tilt, s_tilt, s_yaw])
            self.adm_conf.d = c.conform_damping_nm_s_per_rad * s_tilt
        # Rate-mode conform on the same stiff tilt axes (see AdaptiveConfig.rate_conform_*).
        self._rate_conform = s_tilt > 1.0
        self._rc_dir: np.ndarray | None = None
        self._rc_flat = np.zeros(2, dtype=bool)
        self._rc_done = np.zeros(2, dtype=bool)
        self._rc_rev_since: list = [None, None]
        # Setpoint lead a wall probe carries beyond the reference fixture's following lag: the
        # probe may travel that much further on the setpoint before giving up (0 on every gantry).
        self._probe_lead = self._probe_speed_mm_s * MM * excess_following_lag(ctx, c.lagging_servo_min_ratio)
        # Sweep yaw between the rotational limits only where the fixture can do it in time.
        self._yaw_sweep = self._yaw_probe_rate >= c.yaw_sweep_min_speed_deg_s * DEG
        self._wall_contacts: list[tuple[float, float, float]] = []  # (measured position along probe, reaction, T_z)
        self._wall_yaw_left = c.wall_yaw_corrections
        self._yaw_target = 0.0
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
        self._recent: deque[Observation] = deque(maxlen=c.recent_samples)
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
        sigma_xy = max(ctx.vision_accuracy.vision_xy_sigma_mm, c.min_prior_sigma_mm) * MM
        bias = ctx.vision_accuracy.vision_bias_mm * MM
        self.localizer = HoleLocalizer(
            spec,
            prior_sigma=float(np.hypot(c.prior_sigma_scale * sigma_xy, bias)),
            extent=c.search_extent_mm * MM,
            resolution=c.search_resolution_mm * MM,
            cop_sigma=c.cop_sigma_mm * MM,
            outlier_weight=c.localizer_outlier_weight,
            entry_likelihood=c.localizer_entry_likelihood,
            band_stick_probability=c.localizer_band_stick_probability,
            prior_uniform_weight=c.localizer_prior_uniform_weight,
            exclude_fraction=c.localizer_exclude_fraction,
            exclude_min_cells=c.localizer_exclude_min_cells,
            min_support=c.localizer_min_support_mm * MM,
        )
        self.ylocalizer = None
        if c.localizer_mode == "xyyaw":
            self.ylocalizer = YawHoleLocalizer(
                spec,
                prior_sigma=float(np.hypot(c.prior_sigma_scale * sigma_xy, bias)),
                yaw_prior_sigma=max(c.yaw_prior_scale * self.yaw_sigma, c.min_yaw_prior_sigma_deg * DEG),
                extent=c.search_extent_mm * MM,
                resolution=c.search_resolution_mm * MM,
                yaw_extent=c.yaw_localizer_extent_deg * DEG,
                yaw_resolution=c.yaw_localizer_resolution_deg * DEG,
                cop_sigma=c.cop_sigma_mm * MM,
                outlier_weight=c.localizer_outlier_weight,
                entry_likelihood=c.localizer_entry_likelihood,
                band_stick_probability=c.localizer_band_stick_probability,
                prior_uniform_weight=c.localizer_prior_uniform_weight,
                min_support=c.localizer_min_support_mm * MM,
            )
        self._blocked_poses: list[tuple[np.ndarray, float]] = []
        # Both walls: the plug crosses the clearance twice.
        self.verify_probe = max(c.verify_probe_mm, 2 * spec.socket.clearance_mm + c.verify_probe_margin_mm) * MM
        # W9: one observation-only feature dict per DETECT diagnosis (training data for a
        # learned contact prior; labels are attached offline, never here).
        self.contact_records: list[dict] = []
        self._record_diag: ContactDiagnosis | None = None

    # ------------------------------------------------------------------ helpers
    def _wrench(self, obs: Observation) -> tuple[np.ndarray, np.ndarray]:
        return obs.force - self.bias_f, obs.torque - self.bias_t

    def _corrected_depth(self, obs: Observation) -> float:
        return obs.depth - self.depth_offset

    def _sigma_depth(self) -> float:
        return self.cfg.touch_depth_sigma_mm * MM if self.touch_calibrated else self.sigma_z

    def _engaged(self, depth: float) -> bool:
        """Confidently inside the cavity (accounting for depth uncertainty)."""
        return depth > self._engage_threshold()

    def _engage_threshold(self) -> float:
        return self.cfg.engage_depth_mm * MM + self.cfg.engage_sigma_k * self._sigma_depth()

    def _seat_threshold(self) -> float:
        return self.depth - self.cfg.seat_depth_margin_mm * MM - self.cfg.seat_sigma_k * self._sigma_depth()

    def _mouth_z(self) -> float:
        """Height of the true mouth plane in the estimated socket frame (conservative)."""
        return -self.depth_offset if self.touch_calibrated else self.cfg.mouth_sigma_k * self.sigma_z

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

    def _reached(self, obs: Observation, tol: float | None = None, rot_tol: float | None = None) -> bool:
        tol = self.cfg.reach_tol_mm * MM if tol is None else tol
        rot_tol = self.cfg.reach_tol_rad if rot_tol is None else rot_tol
        target = self._target()
        dp = norm3(obs.setpoint.p - target.p)
        dr = norm3(matrix_to_rotvec(target.R @ obs.setpoint.R.T))
        return dp < tol and dr < rot_tol

    def _enter(self, t: float, state: str, phase: str = "", detail: str = "") -> None:
        self.set_state(t, state, detail)
        self.phase = phase
        self.phase_t = t

    def _record_contact(self, obs: Observation, diag: ContactDiagnosis, conf: np.ndarray, conform_ran: bool) -> None:
        """W9: observation-only features of one DETECT diagnosis (no ground truth, no labels).

        Pure bookkeeping: nothing here feeds back into C's decisions.
        """
        spec = self.ctx.connector
        va = self.ctx.vision_accuracy
        self.contact_records.append({
            "t_s": float(obs.t - self.t_start),
            "attempt": int(self.attempts),
            "kind": diag.kind,
            "trigger": diag.trigger,
            "probe_xy_mm": (diag.probe_xy / MM).tolist(),
            "probe_yaw_deg": float(diag.probe_yaw / DEG),
            "commanded_xy_mm": (self.xy / MM).tolist(),
            "cop_mm": None if diag.cop is None else (diag.cop / MM).tolist(),
            "axial_force_n": float(diag.axial_force),
            "lateral_force_n": np.asarray(diag.lateral_force, dtype=float).tolist(),
            "torque_nm": np.asarray(diag.torque, dtype=float).tolist(),
            "depth_mm": float(diag.depth / MM),
            "touch_calibrated": bool(self.touch_calibrated),
            "depth_offset_mm": float(self.depth_offset / MM),
            "conform_ran": bool(conform_ran),
            "conform_saturated": bool(conform_ran and self._conf_saturated),
            "conform_rot_deg": (np.asarray(conf, dtype=float) / DEG).tolist(),
            "lateral_compliance_mm": (self.adm_lat.x / MM).tolist(),
            "rot_compliance_deg": (self.adm_rot.x / DEG).tolist(),
            "orientation_correction_deg": (matrix_to_rotvec(self.R_corr) / DEG).tolist(),
            "vision_xy_sigma_mm": float(va.vision_xy_sigma_mm),
            "vision_z_sigma_mm": float(va.vision_z_sigma_mm),
            "vision_yaw_sigma_deg": float(va.vision_yaw_sigma_deg),
            "vision_bias_mm": float(va.vision_bias_mm),
            "plug_half_mm": [float(spec.plug_half[0] / MM), float(spec.plug_half[1] / MM)],
            "cavity_half_mm": [float(spec.cavity_half[0] / MM), float(spec.cavity_half[1] / MM)],
            "chamfer_mm": float(spec.chamfer / MM),
            "latching": bool(self.latching),
        })
        self._record_diag = diag

    def _record_for(self, diag: ContactDiagnosis) -> dict | None:
        return self.contact_records[-1] if self._record_diag is diag and self.contact_records else None

    def _contact_prior_update(self, diag: ContactDiagnosis, record: dict | None) -> None:
        """Hook after the analytic localizer update of a blocked attempt; C adds nothing (G: W9)."""

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
            self.z = c.approach_height_mm * MM + c.approach_sigma_k * self.sigma_z
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
        if obs.t - self.phase_t > c.tare_settle_s:
            self._tare_buf.append((obs.force.copy(), obs.torque.copy()))
        if obs.t - self.phase_t > c.tare_end_s:
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
            self._trace = []
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
        if f_ax > c.contact_force_n or norm3(F) > c.contact_on_norm_factor * c.contact_force_n:
            self._contact = True
        elif (
            f_ax < c.contact_off_axial_factor * c.contact_force_n
            and norm3(F) < c.contact_off_norm_factor * c.contact_force_n
        ):
            self._contact = False
        engaged = self._engaged(depth)
        near_bottom = depth > self.depth - (c.near_bottom_margin_mm * MM + c.near_bottom_sigma_k * self._sigma_depth())
        if self._contact:
            v = self.force_axis.velocity(c.insert_force_n, f_ax)
            self.adm_lat.update(F[:2], dt)
            self.adm_rot.update(T, dt, active=np.array([engaged, engaged, True], dtype=float))
        elif not engaged and depth < self._engage_threshold():
            v = self._v_insert
        elif near_bottom:
            v = self._v_near_bottom
        else:
            v = self._v_free
        self.z -= v * dt
        if self.latching:
            self._trace.append((depth, f_ax))
        # Bottoming: deep enough and pushing at the target force -> diagnose quickly.
        if depth >= self._seat_threshold() and f_ax > c.bottom_force_fraction * c.insert_force_n:
            if self._bottom_since is None:
                self._bottom_since = obs.t
            elif obs.t - self._bottom_since > c.bottom_hold_s:
                return self._to_detect(obs, "bottomed")
        else:
            self._bottom_since = None
        reason = self.monitor.update_values(obs.t, depth, F, T, c.insert_force_n)
        if reason is not None:
            return self._to_detect(obs, reason)
        return self._cmd(c.force_phase_speed_cap_mm_s)

    # ------------------------------------------------------------------ DETECT
    def _to_detect(self, obs: Observation, trigger: str) -> Command:
        self._window = []
        self._trigger = trigger
        self._enter(obs.t, DETECT, "hold", trigger)
        if trigger.startswith("excess"):
            # Do not keep pressing: diagnose from the most recent samples and back off.
            self.diagnosis = self._diagnose(list(self._recent)[-self.cfg.excess_diagnosis_samples :], trigger)
            self._record_contact(obs, self.diagnosis, self.adm_conf.x.copy(), conform_ran=False)
            self.log(obs.t, "detect", self.diagnosis.describe())
            return self._begin_recover(obs)
        return self._cmd(self.cfg.force_phase_speed_cap_mm_s)

    def _diagnose(self, window: list[Observation], trigger: str) -> ContactDiagnosis:
        forces, torques = [], []
        yaw = float(np.mean([twist_about_axis(o.rel_pose.R) for o in window])) if window else 0.0
        for o in window:
            F, T = self._wrench(o)
            forces.append(F)
            torques.append(T)
        diag = self.diagnoser.diagnose_values(
            [o.t for o in window],
            [o.depth for o in window],
            [o.lateral for o in window],
            forces,
            torques,
            self.depth_offset,
            self._seat_threshold(),
            trigger,
            engage_threshold=self._engage_threshold(),
        )
        diag.probe_yaw = yaw
        return diag

    def _detect_step(self, obs: Observation) -> Command:
        c = self.cfg
        dt = self.ctx.control_period_s
        if self.phase == "hold":
            self._window.append(obs)
            depth = self._corrected_depth(obs)
            possibly_surface = not self._engaged(depth) and depth < self._seat_threshold()
            if possibly_surface and obs.t - self.phase_t >= c.surface_conform_delay_s:
                # Possibly stopped on the top face: let the plug face conform first so the
                # center of pressure reflects the support geometry, not the tilt error.
                self.adm_conf.reset()
                self._conf_hist.clear()
                self._conf_saturated = False
                self._conf_depth0 = depth
                self._rc_dir = None
                self.phase, self.phase_t = "conform", obs.t
                return self._cmd(c.force_phase_speed_cap_mm_s)
            hold = c.bottomed_hold_s if self._trigger == "bottomed" else c.detect_hold_s
            if obs.t - self.phase_t < hold:
                return self._cmd(c.force_phase_speed_cap_mm_s)
            return self._conclude_detect(obs, self._window[len(self._window) // c.detect_discard_divisor :])
        if self.phase == "conform":
            F, T = self._wrench(obs)
            self.z -= self.force_axis.velocity(c.conform_force_n, float(F[2])) * dt
            if self._rate_conform:
                settled = self._rate_conform_step(obs, F, T, dt, c.rate_conform_speed_deg_s * DEG)
            else:
                self.adm_conf.update(T, dt, active=np.array([1.0, 1.0, 0.0]))
            # Lateral and yaw compliance stay active: if conforming tips the plug onto
            # the lead-in, the chamfer reaction is allowed to guide it into the cavity.
            self.adm_lat.update(F[:2], dt)
            self.adm_rot.update(T, dt, active=np.array([0.0, 0.0, 1.0]))
            if self._corrected_depth(obs) - self._conf_depth0 > c.slide_in_depth_mm * MM:
                self.log(obs.t, "conform", "plug slid into the lead-in: resuming insertion")
                self.monitor.reset(obs.t)
                self._enter(obs.t, INSERT)
                return self._cmd(c.force_phase_speed_cap_mm_s)
            self._conf_hist.append((obs.t, self.adm_conf.x.copy()))
            while self._conf_hist and obs.t - self._conf_hist[0][0] > c.conform_window_s:
                self._conf_hist.popleft()
            elapsed = obs.t - self.phase_t
            rate = norm3(self._conf_hist[-1][1] - self._conf_hist[0][1])
            saturated = norm3(self.adm_conf.x) >= c.conform_saturation_fraction * c.conform_limit_deg * DEG
            if self._rate_conform:
                saturated = not self._rc_flat.all()
                rate = 0.0 if settled else np.inf
            max_s = c.conform_max_s
            if self._rate_conform:  # plus the time to turn through the whole tilt range
                max_s += c.conform_limit_deg / c.rate_conform_speed_deg_s
            if (elapsed > c.conform_min_s and (rate < c.conform_rate_deg * DEG or saturated and not self._rate_conform)) \
                    or elapsed > max_s:
                self._conf_saturated = saturated
                self.phase, self.phase_t = "measure", obs.t
                self._window = []
            return self._cmd(c.force_phase_speed_cap_mm_s)
        # measure: tilt frozen, keep the conform force, average the wrench
        F, T = self._wrench(obs)
        self.z -= self.force_axis.velocity(c.conform_force_n, float(F[2])) * dt
        self.adm_lat.update(F[:2], dt)
        self.adm_rot.update(T, dt, active=np.array([0.0, 0.0, 1.0]))
        if self._corrected_depth(obs) - self._conf_depth0 > c.slide_in_depth_mm * MM:
            self.log(obs.t, "conform", "plug slid into the lead-in: resuming insertion")
            self.monitor.reset(obs.t)
            self._enter(obs.t, INSERT)
            return self._cmd(c.force_phase_speed_cap_mm_s)
        self._window.append(obs)
        if obs.t - self.phase_t < c.measure_s:
            return self._cmd(c.force_phase_speed_cap_mm_s)
        return self._conclude_detect(obs, self._window[len(self._window) // c.detect_discard_divisor :])

    def _surface_consistent(self, diag: ContactDiagnosis) -> bool:
        """Contact signature of a flat face resting on the top surface."""
        if diag.cop is None:
            return False
        c = self.cfg
        px, py = self.plug_half
        m = c.surface_cop_margin_mm * MM
        inside_face = abs(diag.cop[0]) <= px + m and abs(diag.cop[1]) <= py + m
        lateral_small = (
            float(np.hypot(*diag.lateral_force))
            <= c.surface_lateral_ratio * max(diag.axial_force, _EPS) + c.surface_lateral_offset_n
        )
        return bool(inside_face and lateral_small)

    def _touch_calibrate(self, obs: Observation, diag: ContactDiagnosis) -> None:
        """Locate the true mouth plane from the support point on the (tilted) plug face.

        The top face is the highest solid surface near the mouth (lead-in contacts sit
        lower), so the calibration keeps the highest support observed so far.
        """
        rel = obs.rel_pose
        n = rel.R[:, 2]
        h = -(n[0] * diag.cop[0] + n[1] * diag.cop[1]) / max(n[2], _EPS)
        offset = float(-(rel.p[2] + h))
        if not self.touch_calibrated:
            self.depth_offset = offset
            self.touch_calibrated = True
            self.log(obs.t, "touch_calibration", f"mouth {self.depth_offset / MM:+.2f} mm below vision estimate")
        elif offset < self.depth_offset - self.cfg.touch_higher_support_mm * MM:
            self.log(obs.t, "touch_calibration", f"higher support found: mouth {offset / MM:+.2f} mm "
                                                 f"(was {self.depth_offset / MM:+.2f})")
            self.depth_offset = offset

    def _conclude_detect(self, obs: Observation, window: list[Observation]) -> Command:
        diag = self._diagnose(window, self._trigger)
        self.diagnosis = diag
        conform_ran = self.phase in ("conform", "measure")
        conf_at_detect = self.adm_conf.x.copy()
        if self.phase in ("conform", "measure"):
            conf = self.adm_conf.x.copy()
            if self._rate_conform and diag.cop is not None:
                # Rocked across the tip about an axis: the plug is supported on both sides of its centre
                # along the other axis, where a soft wrist settles with the CoP at the centre. A stiff
                # wrist cannot rest there (any residual tilt picks an edge), so report the centre.
                diag.cop = np.where(self._rc_flat[::-1], 0.0, diag.cop)
            state = "tipped" if self._conf_saturated else "flat"
            self.log(obs.t, "conform", f"{state}, rotation=({conf[0] / DEG:+.2f},{conf[1] / DEG:+.2f}) deg")
            if diag.kind == "surface_block" and not self._surface_consistent(diag):
                diag.kind = "partial_jam"
                self.log(obs.t, "detect", "contact signature inconsistent with the top face: treated as in-cavity jam")
            if diag.kind == "surface_block":
                self._touch_calibrate(obs, diag)
                diag.depth = self._corrected_depth(obs)
                if not self._conf_saturated and norm3(np.append(diag.cop, 0.0)) < self.cfg.tilt_fold_cop_mm * MM:
                    # Settled flat on the top face: that rotation measures the residual
                    # socket tilt. Fold it into the reference orientation.
                    self.R_corr = rotvec_to_matrix(conf) @ self.R_corr
                    self.adm_conf.reset()
                    self.log(obs.t, "surface_alignment", f"tilt corrected ({conf[0] / DEG:+.2f},{conf[1] / DEG:+.2f}) deg")
        self._record_contact(obs, diag, conf_at_detect, conform_ran)
        self.log(obs.t, "detect", diag.describe())
        if diag.kind == "seated_candidate":
            lat = float(np.hypot(*diag.lateral_force))
            if lat <= self.cfg.seat_lateral_ratio * diag.axial_force + self.cfg.seat_lateral_offset_n:
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
        if norm3(F) > c.max_force_n * c.retract_stuck_force_factor and obs.t - self.phase_t > c.retract_stuck_delay_s:
            return self._fail(obs, "stuck_during_retract")
        self.z = self._retract_height()
        if self._reached(obs, tol=c.retract_reach_tol_mm * MM, rot_tol=c.retract_reach_tol_rad):
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
            if self.localizer.entry_probability_at(diag.probe_xy) > c.yaw_search_entry_probability:
                self.blocks_at_best += 1
            # CoP reliability: a conform that settled flat (CoP ~ 0) or tipped onto a
            # pivot edge matches the contact model; an intermediate stop indicates mixed
            # support (top face + lead-in) whose CoP magnitude is biased.
            clean = self._conf_saturated or (
                diag.cop is not None and norm3(np.append(diag.cop, 0.0)) < c.clean_cop_mm * MM
            )
            sigma = c.cop_sigma_mm * MM if clean else c.unclean_cop_sigma_mm * MM
            cop = diag.cop if diag.kind == "surface_block" else None
            if self.ylocalizer is not None:
                return self._plan_xyyaw(obs, diag, cop, sigma, lim_xy)
            self.localizer.update_blocked(diag.probe_xy, cop, cop_sigma=sigma)
            record = self._record_for(diag)
            if record is not None:
                record["cop_clean"] = bool(clean)
                record["analytic_mean_mm"] = (self.localizer.mean() / MM).tolist()
                record["analytic_cov_mm2"] = (self.localizer.covariance() / MM**2).tolist()
            self._contact_prior_update(diag, record)
            self._blocked_probes.append(diag.probe_xy.copy())
            new_xy, p_cap = self.localizer.best_probe(lim_xy, exclude=self._blocked_probes)
            if record is not None:
                record["next_probe_mm"] = (new_xy / MM).tolist()
            if self.blocks_at_best >= 2 and self.yaw_search_idx < len(self.yaw_sequence):
                self.yaw_offset = self.yaw_sequence[self.yaw_search_idx] * DEG
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
            if self.ylocalizer is not None:
                self.ylocalizer.update_entered(diag.probe_xy, diag.probe_yaw)
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
        return self._retry(obs, detail)

    def _plan_xyyaw(self, obs: Observation, diag: ContactDiagnosis, cop, sigma: float, lim_xy: float) -> Command:
        """W4: update the joint (x, y, yaw) posterior and pick the next probe pose."""
        c = self.cfg
        self.ylocalizer.update_blocked(diag.probe_xy, diag.probe_yaw, cop, cop_sigma=sigma)
        self._blocked_poses.append((diag.probe_xy.copy(), diag.probe_yaw))
        max_yaw = c.max_yaw_correction_deg * DEG
        xy, yaw, p = self.ylocalizer.best_probe(
            lim_xy,
            max_yaw,
            self._blocked_poses,
            exclude_radius=max(
                min(self.localizer.table.strict_half) * c.localizer_exclude_fraction,
                c.localizer_exclude_min_cells * c.search_resolution_mm * MM,
            ),
            exclude_yaw=c.exclude_yaw_deg * DEG,
            xy_step=c.probe_xy_step_mm * MM,
            yaw_step=c.probe_yaw_step_deg * DEG,
        )
        self.xy = xy
        rv = matrix_to_rotvec(self.R_corr)
        rv[2] = float(np.clip(yaw, -max_yaw, max_yaw))
        self.R_corr = rotvec_to_matrix(rv)
        detail = (f"xy-yaw localizer -> probe ({xy[0] / MM:+.2f},{xy[1] / MM:+.2f}) mm, yaw {yaw / DEG:+.1f} deg, "
                  f"P(entry)={p:.2f}")
        return self._retry(obs, detail)

    def _retry(self, obs: Observation, detail: str) -> Command:
        c = self.cfg
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
        if self.latching:
            return self._begin_latch_verify(obs)
        # Seat conformity first: zero-spring tilt compliance lets the plug face settle
        # flat on the cavity floor, aligning the connector axis with the true socket axis.
        self.adm_conf.reset()
        self._conf_hist.clear()
        self._rc_dir = None
        self._enter(obs.t, VERIFY, "seat_conform")
        return self._verify_step(obs)

    # ------------------------------------------------------------------ VERIFY, latching parts (W3)
    def _click_in_trace(self, bottom: float) -> tuple[bool, float]:
        """Latch signature: the force drops while the plug advances, where the snap should be.

        The snap sits ``post_snap_stroke`` above the floor the plug just bottomed on, so the
        window is relative to the encoder depth and does not depend on the camera.
        """
        m = self.ctx.connector.mating
        snap = bottom - m.latch_post_snap_stroke_mm * MM
        lo = snap - (m.latch_snap_depth_mm - m.latch_onset_depth_mm) * MM
        hi = snap + self.cfg.click_window_after_snap_mm * MM
        pts = [(d, f) for d, f in self._trace if lo <= d <= hi]
        best = 0.0
        run_max = -np.inf
        for d, f in pts:
            run_max = max(run_max, f)
            best = max(best, run_max - f)
        return best >= self.cfg.click_drop_fraction * m.latch_peak_force_n, best

    def _begin_latch_verify(self, obs: Observation) -> Command:
        m = self.ctx.connector.mating
        bottom = self._corrected_depth(obs)
        clicked, drop = self._click_in_trace(bottom)
        self.log(obs.t, "latch", f"click {'seen' if clicked else 'not seen'}: drop {drop:.1f} N near the snap")
        self._pull_target = self.cfg.pull_test_fraction * m.latch_retention_force_n
        self._pull_limit = (m.latch_post_snap_stroke_mm + self.cfg.pull_test_margin_mm) * MM
        self._pull_start = bottom
        self._clicked = clicked
        self._enter(obs.t, VERIFY, "pull")
        return self._verify_step(obs)

    def _latch_verify_step(self, obs: Observation) -> Command:
        c = self.cfg
        dt = self.ctx.control_period_s
        F, T = self._wrench(obs)
        f_ax = float(F[2])
        moved = self._pull_start - self._corrected_depth(obs)
        if self._rate_conform:
            # A soft wrist lets the latched plug find its own axis under the pull and the re-seat; a stiff
            # one pulls along the camera's axis and loads the plug sideways (6 N, 0.6 N m in development).
            # Give back that compliance in software (dampings scaled for a stable loop on this wrist).
            self.adm_lat.update(F[:2], dt)
            self.adm_rot.update(T, dt)
        if self.phase == "pull":
            # Guarded pull: back the setpoint out until the latch pulls back with the test force
            # (axial force negative: the environment holds the plug in), or the plug moves too far.
            self.z -= self.force_axis.velocity(-self._pull_target, f_ax) * dt
            held = f_ax <= -self._pull_target
            if held or moved > self._pull_limit or obs.t - self.phase_t > c.pull_test_max_s:
                ok = held and moved <= self._pull_limit and self._clicked
                self.log(obs.t, "verify", f"pull {-f_ax:.1f} N at {moved / MM:.2f} mm, click "
                                          f"{'seen' if self._clicked else 'not seen'} -> {'PASS' if ok else 'FAIL'}")
                if not ok:
                    self.diagnosis = ContactDiagnosis("verify_failed", self._corrected_depth(obs), 0.0, np.zeros(2),
                                                      np.zeros(3), None, obs.lateral.copy(), "verify")
                    self._enter(obs.t, RECOVER, "retract", "verify_failed")
                    return self._recover_step(obs)
                self.phase, self.phase_t = "release", obs.t
            return self._cmd(c.force_phase_speed_cap_mm_s)
        # re-seat: the pull leaves the plug on the latch hook; push it back to the floor
        self.z -= self.force_axis.velocity(c.insert_force_n, f_ax) * dt
        back = self._corrected_depth(obs) >= self._pull_start - c.reseat_tolerance_mm * MM
        if (back and f_ax >= c.bottom_force_fraction * c.insert_force_n) or obs.t - self.phase_t > c.pull_test_max_s:
            self.log(obs.t, "reseat", f"{'back on the floor' if back else 'not back on the floor'}")
            return self._succeed(obs)
        return self._cmd(c.force_phase_speed_cap_mm_s)

    def _verify_step(self, obs: Observation) -> Command:
        if self.latching:
            return self._latch_verify_step(obs)
        c = self.cfg
        dt = self.ctx.control_period_s
        F, T = self._wrench(obs)
        if self.phase == "seat_conform":
            self.z -= self.force_axis.velocity(c.insert_force_n, float(F[2])) * dt
            if self._rate_conform:
                settled = self._rate_conform_step(obs, F, T, dt, c.rate_seat_conform_speed_deg_s * DEG)
            else:
                self.adm_conf.update(T, dt, active=np.array([1.0, 1.0, 0.0]))
            self.adm_lat.update(F[:2], dt)
            self._conf_hist.append((obs.t, self.adm_conf.x.copy()))
            while self._conf_hist and obs.t - self._conf_hist[0][0] > c.conform_window_s:
                self._conf_hist.popleft()
            elapsed = obs.t - self.phase_t
            rate = norm3(self._conf_hist[-1][1] - self._conf_hist[0][1])
            max_s = c.seat_conform_max_s
            if self._rate_conform:
                rate = 0.0 if settled else np.inf
                max_s += c.conform_limit_deg / c.rate_seat_conform_speed_deg_s
            if (elapsed > c.seat_conform_min_s and rate < c.conform_rate_deg * DEG) or elapsed > max_s:
                conf = self.adm_conf.x
                self.log(obs.t, "seat_conform", f"tilt aligned to floor by ({conf[0] / DEG:+.2f},{conf[1] / DEG:+.2f}) deg")
                self.phase, self.phase_t = "preload", obs.t
                self._preload_unsettled_t = obs.t
            return self._cmd(c.force_phase_speed_cap_mm_s)
        if self.phase == "preload":
            self._hold_preload(F, dt)
            self.adm_lat.update(F[:2], dt)
            # The wall probes only mean something while floor friction (mu x axial
            # force) stays below the wall-reaction threshold, so wait until the axial
            # force has really come down from the seating force to the light preload
            # (the force loop's time constant is about 0.1 s).
            if abs(float(F[2]) - c.verify_preload_n) > c.preload_tolerance_n:
                self._preload_unsettled_t = obs.t
            elapsed = obs.t - self.phase_t
            if (
                elapsed > c.preload_min_s and obs.t - self._preload_unsettled_t >= c.preload_settle_s
            ) or elapsed > c.preload_max_s:
                self._verify_base = self.adm_lat.x.copy()
                # Probe along the socket's short axis (y): it carries the lighter gantry
                # axis (smaller wall-impact transients) and two opposing walls are enough
                # to prove the plug is captured by the cavity and to center it.
                self._verify_dirs = [np.array(d, dtype=float) for d in ((0, 1), (0, -1))]
                self._verify_results = []
                self.phase, self.phase_t = "probe_out", obs.t
            return self._cmd(c.force_phase_speed_cap_mm_s)
        if self.phase in ("probe_out", "probe_back", "center", "yaw_out", "yaw_back", "wall_yaw_turn"):
            self._hold_preload(F, dt)
        if self.phase == "probe_out":
            # Guarded lateral probe: advance until the wall pushes back, or give up
            # once the travel exceeds the full clearance budget.
            d = self._verify_dirs[len(self._verify_results)]
            reaction = float(-np.dot(F[:2], d))
            travel = float(np.dot(self.adm_lat.x - self._verify_base, d))
            if reaction >= c.verify_force_n or travel >= self.verify_probe + self._probe_lead:
                self._verify_results.append((reaction, travel))
                self._wall_contacts.append((float(np.dot(obs.lateral, d)), reaction, float(T[2])))
                self.phase, self.phase_t = "probe_back", obs.t
            else:
                self.adm_lat.x = self.adm_lat.x + d * self._probe_speed_mm_s * MM * dt
            return self._cmd(self._probe_speed_mm_s * c.verify_return_speed_factor)
        if self.phase == "probe_back":
            self.adm_lat.x = self._verify_base.copy()
            if self._reached(obs, tol=c.probe_reach_tol_mm * MM):
                if len(self._verify_results) == len(self._verify_dirs):
                    return self._lateral_verdict(obs)
                self.phase, self.phase_t = "probe_out", obs.t
            return self._cmd(self._probe_speed_mm_s * c.verify_return_speed_factor)
        if self.phase == "center":
            if self._reached(obs, tol=c.probe_reach_tol_mm * MM):
                if self._yaw_centering_needed() and not self._yaw_sweep:
                    return self._wall_yaw_verdict(obs)
                if self._yaw_centering_needed():
                    self._yaw_base = self.yaw_adj
                    self._yaw_results = []
                    self.phase, self.phase_t = "yaw_out", obs.t
                else:
                    return self._succeed(obs)
            return self._cmd(self._probe_speed_mm_s * c.verify_return_speed_factor)
        if self.phase == "wall_yaw_turn":
            return self._wall_yaw_turn_step(obs, T, dt)
        if self.phase == "yaw_out":
            sgn = 1.0 if not self._yaw_results else -1.0
            reaction = -float(T[2]) * sgn
            swept = (self.yaw_adj - self._yaw_base) * sgn
            if reaction >= c.yaw_probe_torque_nm or swept >= c.yaw_probe_max_deg * DEG:
                self._yaw_results.append(self.yaw_adj - self._yaw_base)
                self.phase, self.phase_t = "yaw_back", obs.t
            else:
                self.yaw_adj += sgn * self._yaw_probe_rate * dt
            return self._cmd(c.slow_phase_speed_cap_mm_s)
        if self.phase == "yaw_back":
            if len(self._yaw_results) == 2:
                lo, hi = sorted(self._yaw_results)
                self.yaw_adj = self._yaw_base + 0.5 * (lo + hi)
                if self._reached(obs, tol=c.probe_reach_tol_mm * MM, rot_tol=c.yaw_reach_tol_rad):
                    self.log(
                        obs.t,
                        "yaw_centering",
                        f"limits ({lo / DEG:+.1f},{hi / DEG:+.1f}) deg -> corrected {0.5 * (lo + hi) / DEG:+.2f} deg",
                    )
                    return self._succeed(obs)
            else:
                self.yaw_adj = self._yaw_base
                if self._reached(obs, tol=c.probe_reach_tol_mm * MM, rot_tol=c.yaw_reach_tol_rad):
                    self.phase, self.phase_t = "yaw_out", obs.t
            return self._cmd(c.slow_phase_speed_cap_mm_s)
        return self._cmd(c.force_phase_speed_cap_mm_s)

    # ------------------------------------------------------------------ rate-mode conform (W5b)
    def _orientation_lag(self, obs: Observation) -> np.ndarray:
        """Measured minus commanded orientation (rotation vector, estimated socket axes): the servo lag."""
        return self.S.R.T @ matrix_to_rotvec(obs.fixture_tcp.R @ obs.setpoint.R.T)

    def _rate_conform_step(self, obs: Observation, F: np.ndarray, T: np.ndarray, dt: float, rate: float) -> bool:
        """Tilt at ``rate`` towards the measured torque, per axis, until it reverses (the face passed flat:
        command the measured orientation) or the tilt limit is reached (tipped onto an edge). Returns True
        once both axes are resolved and the fixture has caught up with the setpoint."""
        c = self.cfg
        f_ax = max(float(F[2]), _EPS)
        lag = self._orientation_lag(obs)
        if self._rc_dir is None:
            self._rc_dir = np.sign(T[:2])  # the zero-spring admittance's direction (x' = T / d)
            self._rc_flat[:] = False
            self._rc_done[:] = self._rc_dir == 0
            self._rc_rev_since = [None, None]
        wall = c.rate_conform_wall_factor * f_ax * float(np.hypot(*self.plug_half))
        limit = c.conform_limit_deg * DEG
        loaded = f_ax >= 0.5 * c.conform_force_n
        for k in (0, 1):
            if self._rc_done[k]:
                continue
            reversed_ = loaded and self._rc_dir[k] * T[k] < -c.rate_conform_flip_lever_mm * MM * f_ax
            if not reversed_:
                self._rc_rev_since[k] = None
            elif self._rc_rev_since[k] is None:
                self._rc_rev_since[k] = (obs.t, lag[k])
            if reversed_ and obs.t - self._rc_rev_since[k][0] >= c.rate_conform_flip_hold_s:
                # Command the orientation at which the torque first reversed (measured, so the servo
                # lag does not enter), less the turn made since.
                self.adm_conf.x[k] += self._rc_rev_since[k][1] - self._rc_dir[k] * rate * (obs.t - self._rc_rev_since[k][0])
                self._rc_done[k] = self._rc_flat[k] = True
            elif abs(T[k]) > wall:
                self.adm_conf.x[k] += lag[k]  # held by a wall: stop where the plug is, not where the setpoint led
                self._rc_done[k] = True
            elif abs(self.adm_conf.x[k]) >= c.conform_saturation_fraction * limit:
                self._rc_done[k] = True  # tipped onto an edge: stop turning
            else:
                self.adm_conf.x[k] = float(np.clip(self.adm_conf.x[k] + self._rc_dir[k] * rate * dt, -limit, limit))
        return bool(self._rc_done.all() and norm3(np.append(lag[:2], 0.0)) < c.conform_rate_deg * DEG)

    # ------------------------------------------------------------------ VERIFY, yaw from the walls (W5b)
    def _wall_half_travel(self, yaw: float) -> float:
        """Half the free travel between the two y walls for a plug yawed by ``yaw`` (no tilt), from the drawing."""
        px, py = self.plug_half
        return self.ctx.connector.cavity_half[1] - px * np.sin(abs(yaw)) - py * np.cos(yaw)

    def _yaw_from_free_travel(self, free: float) -> float:
        """Inverse of :meth:`_wall_half_travel` for the full free travel (>= 0); tilt also narrows the travel, so an upper bound."""
        px, py = self.plug_half
        h = self.ctx.connector.cavity_half[1] - 0.5 * free
        return max(0.0, float(np.arcsin(min(1.0, h / np.hypot(px, py))) - np.arctan2(py, px)))

    def _wall_yaw_verdict(self, obs: Observation) -> Command:
        """Yaw check from the two wall contacts just made, for fixtures too stiff to sweep yaw in time.

        The plug's diagonal narrows the free travel between the walls as it yaws, and tilt narrows it
        further, so a free travel at least that of a plug yawed by the tolerance proves the yaw is
        within it. Otherwise each wall touched a corner near one end of the plug: the lever arm of the
        reaction (-T_z / reaction, same sign at both walls) gives the direction of the yaw and the free
        travel its size. The plug is centred, so turning it back towards the cavity axis is free.
        """
        c = self.cfg
        (pos_a, r_a, tz_a), (pos_b, r_b, tz_b) = self._wall_contacts[-2:]
        free = pos_a + pos_b  # measured (encoders), not setpoint: the setpoint lead does not enter
        tol = c.wall_yaw_tolerance_deg * DEG
        need = self._wall_half_travel(tol)
        levers = (-tz_a / max(r_a, _EPS), -tz_b / max(r_b, _EPS))
        detail = (f"half free travel {0.5 * free / MM:.3f} mm (>= {need / MM:.3f} for {c.wall_yaw_tolerance_deg:.1f} "
                  f"deg), levers ({levers[0] / MM:+.1f},{levers[1] / MM:+.1f}) mm")
        if 0.5 * free >= need:
            self.log(obs.t, "wall_yaw", detail + " -> PASS")
            return self._succeed(obs)
        px = self.plug_half[0]
        corner = (min(abs(levers[0]), abs(levers[1])) >= c.wall_yaw_lever_fraction * px
                  and max(abs(levers[0]), abs(levers[1])) <= c.wall_yaw_lever_max_fraction * px and free > 0.0)
        if self._wall_yaw_left > 0 and levers[0] * levers[1] > 0 and corner:
            yaw = float(np.sign(levers[0])) * self._yaw_from_free_travel(free)
            self._wall_yaw_left -= 1
            self._yaw_target = self.yaw_adj - yaw
            self.log(obs.t, "wall_yaw", detail + f" -> turn {-yaw / DEG:+.2f} deg, probe again")
            self.phase, self.phase_t = "wall_yaw_turn", obs.t
            return self._cmd(c.slow_phase_speed_cap_mm_s)
        self.log(obs.t, "wall_yaw", detail + " -> FAIL")
        return self._verify_failed(obs)

    def _wall_yaw_turn_step(self, obs: Observation, T: np.ndarray, dt: float) -> Command:
        c = self.cfg
        err = self._yaw_target - self.yaw_adj
        if -float(T[2]) * np.sign(err) >= c.yaw_probe_torque_nm:  # a wall resists the turn: wrong estimate
            self.log(obs.t, "wall_yaw", f"turn blocked at {-float(T[2]):+.3f} N m -> FAIL")
            self.yaw_adj += float(self._orientation_lag(obs)[2])  # drop the setpoint lead the servo carries
            return self._verify_failed(obs)
        step = c.wall_yaw_correct_speed_deg_s * DEG * dt
        self.yaw_adj += float(np.clip(err, -step, step))
        if abs(err) <= step and self._reached(obs, tol=c.probe_reach_tol_mm * MM, rot_tol=c.yaw_reach_tol_rad):
            self._verify_base = self.adm_lat.x.copy()
            self._verify_results = []
            self.phase, self.phase_t = "probe_out", obs.t
        return self._cmd(c.slow_phase_speed_cap_mm_s)

    def _verify_failed(self, obs: Observation) -> Command:
        self.diagnosis = ContactDiagnosis(
            "verify_failed", self._corrected_depth(obs), 0.0, np.zeros(2), np.zeros(3), None, obs.lateral.copy(), "verify"
        )
        self._enter(obs.t, RECOVER, "retract", "verify_failed")
        return self._recover_step(obs)

    def _yaw_centering_needed(self) -> bool:
        c = self.cfg
        gate = self.yaw_sigma > c.yaw_center_gate_deg * DEG
        if c.yaw_center_policy == "always":
            return True
        if c.yaw_center_policy == "gate_or_corrected":
            return gate or abs(matrix_to_rotvec(self.R_corr)[2]) > c.yaw_center_if_corrected_deg * DEG
        return gate

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
        return self._cmd(self._probe_speed_mm_s * c.verify_return_speed_factor)

    def _succeed(self, obs: Observation) -> Command:
        self._enter(obs.t, SUCCESS)
        self.finish(obs.t, True)
        return self._cmd(self.cfg.slow_phase_speed_cap_mm_s)

    # ------------------------------------------------------------------ terminal states
    def _success_step(self, obs: Observation) -> Command:
        F, _ = self._wrench(obs)
        v = self.force_axis.velocity(self.cfg.verify_preload_n, float(F[2]))
        self.z -= v * self.ctx.control_period_s
        return self._cmd(self.cfg.slow_phase_speed_cap_mm_s)

    def _failure_step(self, obs: Observation) -> Command:
        # Back out along the current compliant pose, exactly as RECOVER's retract does.
        # The admittance offsets stay frozen: zeroing them while the plug is still in
        # the cavity commands a sudden re-orientation against the walls, and a wedged
        # plug then loads the wrist past the cell's torque stop.
        self.z = self._retract_height()
        c = self.cfg
        if not self.done and self._reached(obs, tol=c.retract_reach_tol_mm * MM, rot_tol=c.retract_reach_tol_rad):
            self.finish(obs.t, False, getattr(self, "_fail_reason", "unknown"))
        return self._cmd(self.cfg.retract_speed_mm_s)
