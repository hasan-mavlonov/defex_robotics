"""State estimation: noisy sensor readings -> controller observation.

The estimator only consumes sensor readings, the one-shot vision and in-hand
estimates, and calibrated constants (payload mass properties, nominal connector
geometry). It never touches simulator ground truth.

Wrench processing chain (standard industrial F/T practice):

1. Gravity compensation with the identified payload, using the encoder-measured
   sensor orientation.
2. Tare (bias removal) from a free-space average at the start of the cycle.
3. First-order low-pass filter.
4. Reference-point shift from the sensor origin to the estimated connector tip.
5. Expression in the estimated socket frame (axial = along the insertion axis).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from defex.perception.sensors import SensorReadings
from defex.sim.backend import PayloadModel
from defex.utils.transforms import Pose, cross3, norm3

GRAVITY = np.array([0.0, 0.0, -9.81])


@dataclass(slots=True)
class Observation:
    """Everything a controller is allowed to know at one control tick (read-only by convention)."""

    t: float
    setpoint: Pose  # commanded fixture TCP pose (after motion limits)
    fixture_tcp: Pose  # measured fixture TCP pose (encoders)
    connector_pose: Pose  # estimated connector tip pose (world)
    socket_pose: Pose  # vision estimate of the socket mouth pose (world)
    grasp_offset: Pose  # estimated connector tip relative to the fixture TCP
    rel_pose: Pose  # estimated connector tip pose in the estimated socket frame
    depth: float  # m, insertion depth estimate along the socket axis (+ = inside)
    lateral: np.ndarray  # (2,) m, tip offset from the socket axis, socket frame
    force: np.ndarray  # (3,) external force on the connector, socket frame (N)
    torque: np.ndarray  # (3,) external torque about the connector tip, socket frame (N m)
    force_world: np.ndarray
    torque_world: np.ndarray
    tared: bool

    @property
    def axial_force(self) -> float:
        """Insertion resistance (N): positive when the environment pushes the plug out."""
        return float(self.force[2])

    @property
    def lateral_force(self) -> np.ndarray:
        return self.force[:2]

    @property
    def force_norm(self) -> float:
        return norm3(self.force)

    @property
    def torque_norm(self) -> float:
        return norm3(self.torque)


class StateEstimator:
    def __init__(self, payload: PayloadModel, control_period_s: float, ft_cutoff_hz: float) -> None:
        self.payload = payload
        self.dt = control_period_s
        tau = 1.0 / (2.0 * np.pi * ft_cutoff_hz)
        self._alpha = self.dt / (self.dt + tau)
        self.socket_pose = Pose.identity()
        self.grasp_offset = Pose.identity()
        self._bias_f = np.zeros(3)
        self._bias_t = np.zeros(3)
        self._filt_f = np.zeros(3)
        self._filt_t = np.zeros(3)
        self._tare_acc: list[tuple[np.ndarray, np.ndarray]] | None = None
        self.tared = False

    def reset(self, socket_pose_estimate: Pose, grasp_offset_estimate: Pose) -> None:
        self.socket_pose = socket_pose_estimate
        self._socket_inv = socket_pose_estimate.inv()
        self._RsT = socket_pose_estimate.R.T.copy()
        self.grasp_offset = grasp_offset_estimate
        self._bias_f[:] = 0.0
        self._bias_t[:] = 0.0
        self._filt_f[:] = 0.0
        self._filt_t[:] = 0.0
        self._tare_acc = None
        self.tared = False

    # ---------------------------------------------------------------- taring
    def begin_tare(self) -> None:
        self._tare_acc = []

    def end_tare(self) -> None:
        if self._tare_acc:
            f = np.mean([a for a, _ in self._tare_acc], axis=0)
            t = np.mean([b for _, b in self._tare_acc], axis=0)
            self._bias_f = f
            self._bias_t = t
            self._filt_f[:] = 0.0
            self._filt_t[:] = 0.0
            self.tared = True
        self._tare_acc = None

    # ---------------------------------------------------------------- update
    def _compensated_wrench(self, readings: SensorReadings) -> tuple[np.ndarray, np.ndarray, Pose]:
        p = self.payload
        sensor_pose = readings.tcp_pose @ p.sensor_in_tcp
        g_s = sensor_pose.R.T @ (p.mass_kg * GRAVITY)
        # Static balance of the payload: F_wrist + F_ext + m g = 0.
        f_ext = -readings.ft_force - g_s
        t_ext = -readings.ft_torque - cross3(p.com_in_sensor, g_s)
        return f_ext, t_ext, sensor_pose

    def update(self, readings: SensorReadings, setpoint: Pose) -> Observation:
        f_ext, t_ext, sensor_pose = self._compensated_wrench(readings)
        if self._tare_acc is not None:
            self._tare_acc.append((f_ext.copy(), t_ext.copy()))
        f_ext = f_ext - self._bias_f
        t_ext = t_ext - self._bias_t
        a = self._alpha
        self._filt_f += a * (f_ext - self._filt_f)
        self._filt_t += a * (t_ext - self._filt_t)

        connector = readings.tcp_pose @ self.grasp_offset
        f_w = sensor_pose.R @ self._filt_f
        t_w_sensor = sensor_pose.R @ self._filt_t
        t_w_tip = t_w_sensor + cross3(sensor_pose.p - connector.p, f_w)

        S = self.socket_pose
        rel = self._socket_inv @ connector
        return Observation(
            t=readings.t,
            setpoint=setpoint,
            fixture_tcp=readings.tcp_pose,
            connector_pose=connector,
            socket_pose=S,
            grasp_offset=self.grasp_offset,
            rel_pose=rel,
            depth=float(-rel.p[2]),
            lateral=rel.p[:2].copy(),
            force=self._RsT @ f_w,
            torque=self._RsT @ t_w_tip,
            force_world=f_w,
            torque_world=t_w_tip,
            tared=self.tared,
        )
