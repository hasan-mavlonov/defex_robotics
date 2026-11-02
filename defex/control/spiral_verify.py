"""Controller J (v0.2d): F's insertion, then C's VERIFY.

F (spiral search on the passive RCC stage, with F's per-machine settings) runs unchanged up to the
tick at which it would declare the connector seated. From that observation on, C's own VERIFY code
runs, with C's settings: on a housing-only connector seat conform, preload, wall probes, centring,
then the yaw sweep (gantry) or the wall-yaw check (arm); on a latching connector C's latch check
(retention pull, re-seat, defect verdict, gentle retract).

C's VERIFY reads state that C builds before it. J fills it only from what F measured:

* socket and grasp estimates, the free-space tare: F's;
* setpoint: F's commanded tip position (spiral point plus F's compliance offsets) and depth, with no
  rotation (F aims along the vision estimate); C's admittances start at zero;
* mouth plane: the depth of F's face contact as C's touch calibration; none when F went straight in
  (C then uses the vision depth sigma, as before a touch);
* latching parts: depth and axial force from F's last descent as C's insertion trace (the click it
  shows is logged, not required).

Nothing else: no centre-of-pressure diagnosis at the bottom (C's DETECT), no hole localizer, no yaw
estimate.

C's VERIFY assumes a stiff wrist: the encoders give the plug's position, and a wall pushes back as
soon as the plug meets it. On F's RCC stage the plug trails the tool by F / k (k the stage's datasheet
lateral stiffness), so with ``rcc_terms`` J gives C's code two things from the F/T reading and the
datasheet, nothing measured by anything else: the plug position as encoders plus F / k, and C's
setpoint-lead allowance on a wall probe (``_probe_lead``) plus the stage's deflection at C's wall force.

A check that fails ends in C's retract before a retry (compliance frozen, gentle retract on latching
parts); then, in place of C's recovery planning, ``on_verify_fail``: "reject" declares the part
failed; "research" hands back to F, whose jam retry descends again at the found position and
searches, within F's attempt budget.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Callable

from defex.config import MM, CompliantStageConfig
from defex.control.adaptive_fsm import AdaptiveInsertionController
from defex.control.base import Command, ControllerContext
from defex.control.spiral_search import DESCEND, INSERT, TARE, CompliantSpiralSearchController
from defex.perception.state_estimator import Observation

VERIFY_FAIL_POLICIES = ("reject", "research")


class _Verifier(AdaptiveInsertionController):
    """C, entered at VERIFY by J. After a failed check and C's retract, J decides instead of C's planner."""

    def __init__(self, after_failed_check: Callable[[Observation], Command]) -> None:
        super().__init__()
        self._after_failed_check = after_failed_check

    def _plan_correction(self, obs: Observation) -> Command:
        return self._after_failed_check(obs)


class CompliantSpiralSearchVerifyController(CompliantSpiralSearchController):
    name = "spiral_rcc_verify"
    label = "J: F + C's verify"
    # Picked by results/v0.2d_j_verify/SELECTION_RULE.md on dev seed 2026 (more good parts seated, no bad unit
    # passed by either candidate).
    on_verify_fail: str | None = "research"
    rcc_terms = True

    def __init__(self, on_verify_fail: str | None = None) -> None:
        super().__init__()
        if on_verify_fail is not None:
            self.on_verify_fail = on_verify_fail
        if self.on_verify_fail not in VERIFY_FAIL_POLICIES:
            raise ValueError(f"on_verify_fail must be one of {VERIFY_FAIL_POLICIES}")
        self.verifier = _Verifier(self._after_failed_check)
        self.stage = CompliantStageConfig()  # the stage the cell mounts for a compliant wrist (datasheet values)

    def reset(self, ctx: ControllerContext) -> None:
        super().reset(ctx)
        v = self.verifier
        v.reset(ctx)
        v.events = self.events
        v.markers = self.markers
        self._k_lat = self.stage.lateral_stiffness_n_per_mm / MM
        if self.rcc_terms:
            v._probe_lead += v.cfg.verify_force_n / self._k_lat
        self._verifying = False
        self._descent: list[tuple[float, float]] = []  # (depth reading, axial force) of F's current attempt

    def step(self, obs: Observation) -> Command:
        if self._verifying:
            return self._mirror(self.verifier.step(self._plug_obs(obs)))
        if self.state == TARE:
            self._descent = []
        elif self.state in (DESCEND, INSERT) and self.verifier.latching:
            self._descent.append((float(obs.depth), float(obs.force[2] - self.bias_f[2])))
        return super().step(obs)

    def _plug_obs(self, obs: Observation) -> Observation:
        if not self.rcc_terms:
            return obs
        return replace(obs, lateral=obs.lateral + (obs.force[:2] - self.verifier.bias_f[:2]) / self._k_lat)

    def _succeed(self, obs: Observation) -> Command:
        """Where F declares the plug seated: hand over to C's VERIFY with what F measured."""
        v = self.verifier
        v.S, v.G, v.t_start, v.attempts = self.S, self.G, self.t_start, self.attempts
        v.bias_f, v.bias_t = self.bias_f.copy(), self.bias_t.copy()
        v.xy = self.xy + self.adm_search.x + self.adm.x
        v.z = self.z
        v.adm_lat.reset()
        v.adm_rot.reset()
        v.adm_conf.reset()
        v.yaw_adj = 0.0
        v.touch_calibrated = self.face_depth is not None
        v.depth_offset = float(self.face_depth) if v.touch_calibrated else 0.0
        v._begin_attempt(obs.t)
        v._trace = [(d - v.depth_offset, f) for d, f in self._descent]
        face = f"face at {v.depth_offset / MM:.2f} mm" if v.touch_calibrated else "face not touched"
        self.log(obs.t, "verify_handover", f"F seated at {obs.depth / MM:.2f} mm ({face}): C's VERIFY")
        self._verifying = True
        return self._mirror(v._begin_verify(self._plug_obs(obs)))

    def _after_failed_check(self, obs: Observation) -> Command:
        if self.on_verify_fail == "research" and self.attempts < self.cfg.max_attempts:
            self._verifying = False
            return self._jam_or_fail(obs, "verify_failed")
        return self.verifier._fail(obs, "verify_failed")

    def _mirror(self, cmd: Command) -> Command:
        v = self.verifier
        if self._verifying:
            self.state = v.state
            if v.done and not self.done:
                self.done, self.done_time = True, v.done_time
                self.declared_success, self.failure_reason = v.declared_success, v.failure_reason
        return cmd


class CompliantSpiralSearchVerifyRejectController(CompliantSpiralSearchVerifyController):
    """J's candidate (a): a failed check rejects the part."""

    name = "spiral_rcc_verify_reject"
    label = "J(a): F + C's verify, reject on a failed check"
    on_verify_fail = "reject"


class CompliantSpiralSearchVerifyResearchController(CompliantSpiralSearchVerifyController):
    """J's candidate (b): a failed check hands back to F to search again, within F's attempts."""

    name = "spiral_rcc_verify_research"
    label = "J(b): F + C's verify, F searches again on a failed check"
    on_verify_fail = "research"


class CompliantSpiralSearchVerifyRejectNoRCCController(CompliantSpiralSearchVerifyRejectController):
    """Ablation of J(a): C's VERIFY with its stiff-wrist plug position and probe allowance on the RCC stage."""

    name = "spiral_rcc_verify_reject_no_rcc"
    label = "J(a) without the RCC terms"
    rcc_terms = False
