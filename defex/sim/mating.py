"""Terminal and latch forces along the insertion axis (W3). Simulator side only.

MuJoCo models the housing as rigid boxes; the terminals and the latch are
compliant parts far smaller than the housing, so they are modelled as a force on
the plug along the socket axis, as a function of insertion depth and velocity:

* Terminal friction: from (seat - wipe) the contacts engage over ``terminal_lead``
  to a peak (entry), then settle to a sliding force. Stick-slip is modelled with a
  bristle (Dahl-type, position based): the contacts deflect elastically up to
  0.05 mm, then slide at the friction force. It resists insertion and withdrawal
  alike and, unlike a velocity-based law, cannot chatter against a stiff servo.
* Latch: an elastic ramp from onset to peak depth (force rises to the peak), then
  falls to zero by the snap depth: the click. Past the snap the latch is engaged;
  pulling back more than its free play stretches a stiff spring that holds up to
  the rated retention force, beyond which the latch breaks.
* Defects (deliberately bad parts): ``half_latched`` (an obstruction stops the plug
  0.3 mm short of the snap), ``broken_latch`` (no ramp, no retention),
  ``stubbed_terminal`` (a bent pin butts the header 0.2 mm after the terminals
  start), ``wrong_polarization`` (the key stops the plug 1 mm into the cavity).
  Obstructions are stiff, damped end stops.

All forces act only while the plug is laterally inside the cavity (terminals and
latch cannot engage while it rests on the face).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from defex.config import MM, ConnectorSpec

DEFECTS = ("half_latched", "broken_latch", "stubbed_terminal", "wrong_polarization")
_BRISTLE = 0.05 * MM  # m, elastic pre-sliding deflection of the terminal contacts
_STOP_STIFFNESS = 5e5  # N/m, obstruction end stop (0.06 mm under a 30 N push)
_STOP_DAMPING = 1500.0  # N s/m
_LATCH_STIFFNESS = 2e5  # N/m, engaged latch hook against withdrawal (assumed)
_LATCH_PLAY = 0.1 * MM  # free axial play of an engaged latch


@dataclass
class MatingState:
    latched: bool = False
    broken: bool = False
    max_depth: float = 0.0
    bristle: float = 0.0  # -1..1, terminal contact deflection (fraction of _BRISTLE)
    last_depth: float | None = None


class MatingForce:
    def __init__(self, spec: ConnectorSpec, defect: str | None = None) -> None:
        if defect is not None and defect not in DEFECTS:
            raise ValueError(f"unknown defect {defect!r}; choose from {DEFECTS}")
        self.spec = spec
        self.m = spec.mating
        self.defect = defect
        self.depth = spec.depth
        hx, hy = spec.cavity_half
        px, py = spec.plug_half[:2]
        self.lateral_gate = (hx - px + 0.1 * MM, hy - py + 0.1 * MM)
        m = self.m
        self.t0 = self.depth - m.terminal_wipe_mm * MM
        self.lead = m.terminal_lead_mm * MM
        self.peak_t = m.circuits * m.terminal_peak_per_circuit_n
        self.slide_t = m.circuits * m.terminal_slide_per_circuit_n
        self.onset = m.latch_onset_depth_mm * MM
        self.lpeak = m.latch_peak_depth_mm * MM
        self.snap = m.latch_snap_depth_mm * MM
        self.latch_peak = 0.0 if defect == "broken_latch" else m.latch_peak_force_n
        self.retention = 0.0 if defect == "broken_latch" else m.latch_retention_force_n
        self.stop = {
            "half_latched": self.snap - 0.3 * MM,
            "stubbed_terminal": self.t0 + 0.2 * MM,
            "wrong_polarization": 1.0 * MM,
        }.get(defect)
        self.state = MatingState()

    def reset(self) -> None:
        self.state = MatingState()

    def terminal_force(self, d: float) -> float:
        """Magnitude of the terminal friction at depth d (before the velocity sign)."""
        if d <= self.t0:
            return 0.0
        x = d - self.t0
        if x < self.lead:
            return self.peak_t * x / self.lead
        if x < 2 * self.lead:
            return self.peak_t + (self.slide_t - self.peak_t) * (x - self.lead) / self.lead
        return self.slide_t

    def latch_ramp_force(self, d: float) -> float:
        if self.state.latched or self.state.broken or d <= self.onset or d >= self.snap:
            return 0.0
        if d < self.lpeak:
            return self.latch_peak * (d - self.onset) / (self.lpeak - self.onset)
        return self.latch_peak * (self.snap - d) / (self.snap - self.lpeak)

    def axial_force(self, d: float, v_in: float, lateral: np.ndarray) -> float:
        """Force on the plug along the socket axis, positive pushing it out of the socket.

        ``d``: tip depth below the mouth (m); ``v_in``: velocity into the socket (m/s);
        ``lateral``: tip offset from the cavity axis in the socket frame (m).
        """
        st = self.state
        if abs(lateral[0]) > self.lateral_gate[0] or abs(lateral[1]) > self.lateral_gate[1]:
            st.last_depth = None
            return 0.0
        st.max_depth = max(st.max_depth, d)
        step = 0.0 if st.last_depth is None else d - st.last_depth
        st.last_depth = d
        st.bristle = float(np.clip(st.bristle + step / _BRISTLE, -1.0, 1.0))
        f = 0.0
        if self.stop is not None and d > self.stop:
            f += _STOP_STIFFNESS * (d - self.stop) + _STOP_DAMPING * max(v_in, 0.0)
        f += self.terminal_force(d) * st.bristle
        f += self.latch_ramp_force(d)
        if not st.latched and not st.broken and d >= self.snap and self.latch_peak > 0.0:
            st.latched = True
        if st.latched:
            pull = self.snap - _LATCH_PLAY - d
            if pull > 0.0:
                hold = _LATCH_STIFFNESS * pull
                if hold > self.retention:
                    st.latched = False
                    st.broken = True
                else:
                    f -= hold  # pulls the plug back in
        return float(f)
