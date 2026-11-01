"""HardwareBackend: the SimBackend protocol on real devices (W7).

The trial harness, controllers, perception and scoring run unchanged. What
differs on hardware:

* ``load`` cannot move the socket. ``SceneParams.socket_pose`` is the pose the
  operator set with the test jig (TEST_PROTOCOL.md); the harness still draws the
  "vision" estimate from it with the condition's noise, so the camera error is a
  deliberate, known injection and trials stay paired with simulation.
* ``ground_truth`` is measured, not true (``source="measured"``): pose from the
  encoders, contact force from the wrist sensor. Seating is confirmed after each
  trial by the inspection and pull test in the protocol, logged separately.
* Run hardware trials with zero synthetic F/T and encoder noise
  (:func:`hardware_noise`): the real sensors already have theirs.
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np

from defex.config import SensorNoiseConfig
from defex.hardware.drivers import FTSensorDriver, MotionDriver
from defex.sim.backend import GroundTruth, PayloadModel, RawSensorData, SceneParams
from defex.utils.transforms import Pose, norm3


def hardware_noise(condition_noise: SensorNoiseConfig) -> SensorNoiseConfig:
    """Keep the condition's (injected) vision error; no synthetic noise on real sensors."""
    return replace(
        condition_noise,
        ft_force_sigma_n=0.0,
        ft_torque_sigma_nm=0.0,
        ft_force_bias_n=0.0,
        ft_torque_bias_nm=0.0,
        encoder_pos_sigma_mm=0.0,
        encoder_rot_sigma_deg=0.0,
    )


class HardwareBackend:
    def __init__(self, motion: MotionDriver, ft: FTSensorDriver, sensor_in_tcp: Pose, nominal_socket_pose: Pose) -> None:
        self.motion = motion
        self.ft = ft
        self._sensor_in_tcp = sensor_in_tcp
        self._nominal_socket = nominal_socket_pose
        self.params: SceneParams | None = None
        self._last: tuple[float, np.ndarray] | None = None
        self.reporting_payload: PayloadModel | None = None  # for the measured contact force only

    # ------------------------------------------------------------------ protocol
    @property
    def time(self) -> float:
        return self.motion.time

    @property
    def home_tcp_pose(self) -> Pose:
        return self.motion.home_tcp_pose

    @property
    def nominal_socket_pose(self) -> Pose:
        return self._nominal_socket

    @property
    def ft_sensor_in_tcp(self) -> Pose:
        return self._sensor_in_tcp

    @property
    def true_payload(self) -> PayloadModel:
        raise NotImplementedError("hardware has no true payload; the harness identifies it from F/T readings")

    def load(self, params: SceneParams) -> None:
        if params.compliance is not None:
            # A physical RCC must actually be mounted; the backend only records the claim.
            pass
        self.params = params
        self.reset()

    def reset(self) -> None:
        self._last = None

    def set_tcp_setpoint(self, pose: Pose) -> None:
        self.motion.set_tcp_setpoint(pose)

    def step(self, duration: float) -> None:
        self.motion.wait_period(duration)

    def read_sensors(self) -> RawSensorData:
        s = self.ft.read()
        return RawSensorData(
            t=self.motion.time,
            joint_pos=self.motion.joint_positions(),
            tcp_pose=self.motion.read_tcp_pose(),
            ft_force=s.force,
            ft_torque=s.torque,
        )

    def ground_truth(self) -> GroundTruth:
        tcp = self.motion.read_tcp_pose()
        s = self.ft.read()
        sensor = tcp @ self._sensor_in_tcp
        f_world = -(sensor.R @ s.force)
        if self.reporting_payload is not None:
            f_world = f_world - self.reporting_payload.mass_kg * np.array([0.0, 0.0, -9.81])
        t = self.motion.time
        speed = 0.0
        if self._last is not None and t > self._last[0]:
            speed = norm3(tcp.p - self._last[1]) / (t - self._last[0])
        self._last = (t, tcp.p.copy())
        grasp = self.params.grasp_offset if self.params is not None else Pose.identity()
        return GroundTruth(
            t=t,
            socket_pose=self.params.socket_pose if self.params is not None else self._nominal_socket,
            connector_pose=tcp @ grasp,
            contact_force=f_world,
            contact_force_norm=norm3(f_world),
            max_penetration=0.0,
            n_contacts=-1,
            tcp_speed=speed,
            joint_limit_hit=False,
            actuator_saturated=False,
            source="measured",
        )

    def joint_positions(self) -> np.ndarray:
        return self.motion.joint_positions()

    def set_marker_pose(self, which: str, pose: Pose) -> None:
        return None
