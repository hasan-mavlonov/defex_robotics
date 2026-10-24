"""Online failure detection and contact-state diagnosis for adaptive insertion.

Two pieces:

* :class:`InsertionMonitor` runs every tick during INSERT and decides *when* to
  stop: insufficient progress while pushing (stall), excessive force or torque,
  excessive lateral force (wedging), or phase timeout.
* :class:`ContactDiagnoser` runs in DETECT on a short window of observations
  held at constant setpoint and decides *what happened*: the plug is seated, it
  is blocked on the top face (and where the contact acts), or it entered the
  cavity but jammed part-way.

Both use only :class:`~defex.perception.state_estimator.Observation` data.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np

from defex.config import MM, AdaptiveConfig
from defex.perception.state_estimator import Observation


class InsertionMonitor:
    def __init__(self, cfg: AdaptiveConfig) -> None:
        self.cfg = cfg
        self._hist: deque[tuple[float, float]] = deque()
        self._t0 = 0.0

    def reset(self, t: float) -> None:
        self._hist.clear()
        self._t0 = t

    def progress(self) -> float | None:
        """Depth gained over the stall window (m), or None until the window is filled."""
        if not self._hist:
            return None
        t_now, d_now = self._hist[-1]
        t_old, d_old = self._hist[0]
        if t_now - t_old < self.cfg.stall_window_s * 0.98:
            return None
        return d_now - d_old

    def update(self, obs: Observation, f_target: float) -> str | None:
        return self.update_values(obs.t, obs.depth, obs.force, obs.torque, f_target)

    def update_values(
        self, t: float, depth: float, force: np.ndarray, torque: np.ndarray, f_target: float
    ) -> str | None:
        """Return a stop reason, or None to keep inserting."""
        c = self.cfg
        self._hist.append((t, depth))
        while self._hist and t - self._hist[0][0] > c.stall_window_s:
            self._hist.popleft()
        if float(np.sqrt(force @ force)) > c.max_force_n:
            return "excess_force"
        if float(np.sqrt(torque @ torque)) > c.max_torque_nm:
            return "excess_torque"
        if float(np.hypot(force[0], force[1])) > c.max_lateral_force_n:
            return "excess_lateral_force"
        prog = self.progress()
        if prog is not None and force[2] > c.stall_force_fraction * f_target and prog < c.stall_progress_mm * MM:
            return "stall"
        if t - self._t0 > c.insert_timeout_s:
            return "insert_timeout"
        return None


@dataclass
class ContactDiagnosis:
    kind: str  # "seated_candidate" | "surface_block" | "partial_jam" | "no_contact"
    depth: float  # m (estimate, touch-corrected if available)
    axial_force: float  # N
    lateral_force: np.ndarray  # (2,) N
    torque: np.ndarray  # (3,) N m about the tip, socket frame
    cop: np.ndarray | None  # (2,) m, center of pressure relative to the tip (socket frame)
    probe_xy: np.ndarray  # (2,) m, tip lateral position in the estimated socket frame
    trigger: str = ""

    def describe(self) -> str:
        cop = "n/a" if self.cop is None else f"({self.cop[0] / MM:+.2f},{self.cop[1] / MM:+.2f}) mm"
        return (
            f"{self.kind} [{self.trigger}] depth={self.depth / MM:.2f} mm Fax={self.axial_force:.1f} N "
            f"Flat=({self.lateral_force[0]:+.1f},{self.lateral_force[1]:+.1f}) N CoP={cop} "
            f"at ({self.probe_xy[0] / MM:+.2f},{self.probe_xy[1] / MM:+.2f}) mm"
        )


class ContactDiagnoser:
    def __init__(self, cfg: AdaptiveConfig) -> None:
        self.cfg = cfg

    def diagnose(
        self, window: list[Observation], depth_offset: float, seat_threshold: float, trigger: str
    ) -> ContactDiagnosis:
        return self.diagnose_values(
            [o.t for o in window],
            [o.depth for o in window],
            [o.lateral for o in window],
            [o.force for o in window],
            [o.torque for o in window],
            depth_offset,
            seat_threshold,
            trigger,
        )

    def diagnose_values(
        self,
        times: list[float],
        depths: list[float],
        laterals: list[np.ndarray],
        forces: list[np.ndarray],
        torques: list[np.ndarray],
        depth_offset: float,
        seat_threshold: float,
        trigger: str,
        engage_threshold: float | None = None,
    ) -> ContactDiagnosis:
        """Classify the contact state from a window of (bias-corrected) samples.

        ``engage_threshold`` is the depth beyond which the plug is *confidently*
        inside the cavity; callers widen it by the current depth uncertainty.
        """
        c = self.cfg
        F = np.mean(forces, axis=0)
        T = np.mean(torques, axis=0)
        depth = float(np.mean(depths)) - depth_offset
        probe = np.mean(laterals, axis=0)
        fz = float(F[2])
        cop = None
        if fz >= c.min_cop_force_n:
            cop = np.array([-T[1] / fz, T[0] / fz])
        if fz < c.contact_force_n * 0.5 and trigger not in ("excess_lateral_force", "excess_torque"):
            kind = "no_contact"
        elif depth >= seat_threshold:
            kind = "seated_candidate"
        elif depth < (c.engage_depth_mm * MM if engage_threshold is None else engage_threshold):
            kind = "surface_block"
        else:
            kind = "partial_jam"
        return ContactDiagnosis(kind, depth, fz, F[:2].copy(), T.copy(), cop, probe, trigger)
