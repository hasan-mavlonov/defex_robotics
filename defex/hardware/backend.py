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
* Any exception inside the control loop stops the motion system before it
  propagates (sensor fault, timeout, driver error).
* ``fixture_dynamics`` must be given in full (measured or from the robot's data):
  stiffnesses, mass and latency (W5), and the tilt stiffness and the translational
  and rotational servo following lags (W5b; identify the lags from a logged ramp).
  Without the W5 values the controllers' contact-speed and yaw-rate limits would
  switch off; without the W5b values C would run a mix (stiff-wrist rules from the
  yaw stiffness, no lag compensation). The backend refuses a value left at None.
* The measured "ground truth" force is not tared and the connector pose uses the
  nominal grasp; only the post-trial inspection decides seating on hardware.
"""

from __future__ import annotations

from dataclasses import fields, replace

import numpy as np

from defex.config import SensorNoiseConfig
from defex.hardware.drivers import FTSensorDriver, MotionDriver
from defex.sim.backend import FixtureDynamics, GroundTruth, PayloadModel, RawSensorData, SceneParams
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
    def __init__(self, motion: MotionDriver, ft: FTSensorDriver, sensor_in_tcp: Pose, nominal_socket_pose: Pose,
                 fixture_dynamics: FixtureDynamics) -> None:
        missing = [f.name for f in fields(fixture_dynamics) if getattr(fixture_dynamics, f.name) is None]
        if missing:
            raise ValueError(f"fixture_dynamics must state every value for hardware; not identified: {missing}")
        self.motion = motion
        self._dynamics = fixture_dynamics
        self._last_sample = None
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
    def fixture_dynamics(self) -> FixtureDynamics:
        return self._dynamics

    def _guarded(self, fn, *args):
        try:
            return fn(*args)
        except BaseException:
            self.motion.stop()
            raise

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
        self._guarded(self.motion.set_tcp_setpoint, pose)

    def step(self, duration: float) -> None:
        self._guarded(self.motion.wait_period, duration)

    def read_sensors(self) -> RawSensorData:
        s = self._guarded(self.ft.read)
        self._last_sample = s
        return RawSensorData(
            t=self.motion.time,
            joint_pos=self.motion.joint_positions(),
            tcp_pose=self.motion.read_tcp_pose(),
            ft_force=s.force,
            ft_torque=s.torque,
        )

    def ground_truth(self) -> GroundTruth:
        tcp = self.motion.read_tcp_pose()
        # Reuse the controller's sample: one sensor round trip per tick, and scoring sees
        # the same reading the controller acted on.
        s = self._last_sample if self._last_sample is not None else self._guarded(self.ft.read)
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
