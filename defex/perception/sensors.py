"""Sensor noise models.

These models turn noise-free backend signals into what real hardware would report:

* **Vision**: a one-shot estimate of the socket mouth pose per cycle (camera +
  hand-eye calibration), with Gaussian position/orientation noise and an optional
  systematic calibration bias.
* **In-hand estimate**: the connector pose in the gripper (e.g. an up-looking
  camera), with Gaussian noise.
* **Wrist F/T sensor**: white noise plus a per-trial bias (removed by taring).
* **Encoders**: tiny white noise on the forward-kinematics TCP pose.

Each trial owns independent random streams derived from its seed, so the vision
and in-hand measurements are identical for every controller evaluated on the same
paired scenario.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from defex.config import DEG, MM, SensorNoiseConfig
from defex.sim.backend import RawSensorData
from defex.utils.transforms import Pose, rotvec_to_matrix


@dataclass(slots=True)
class SensorReadings:
    t: float
    tcp_pose: Pose  # encoder-based fixture TCP pose
    ft_force: np.ndarray  # sensor frame, parent-on-child convention (N)
    ft_torque: np.ndarray  # sensor frame (N m)


class SensorSuite:
    def __init__(self, noise: SensorNoiseConfig, seed: int) -> None:
        self.noise = noise
        ss = np.random.SeedSequence(seed)
        vision_ss, grasp_ss, ft_ss, enc_ss = ss.spawn(4)
        self._rng_vision = np.random.default_rng(vision_ss)
        self._rng_grasp = np.random.default_rng(grasp_ss)
        self._rng_ft = np.random.default_rng(ft_ss)
        self._rng_enc = np.random.default_rng(enc_ss)
        self.ft_force_bias = self._rng_ft.normal(0.0, noise.ft_force_bias_n, 3)
        self.ft_torque_bias = self._rng_ft.normal(0.0, noise.ft_torque_bias_nm, 3)
        self._enc_pos_sigma = noise.encoder_pos_sigma_mm * MM
        self._enc_rot_sigma = noise.encoder_rot_sigma_deg * DEG
        bias_dir = self._rng_vision.uniform(0.0, 2.0 * np.pi)
        self.vision_bias = noise.vision_bias_mm * MM * np.array([np.cos(bias_dir), np.sin(bias_dir), 0.0])

    # -------------------------------------------------------------- one-shot estimates
    def vision_measurement(self, true_socket_pose: Pose) -> Pose:
        n = self.noise
        r = self._rng_vision
        dp = np.array(
            [r.normal(0.0, n.vision_xy_sigma_mm), r.normal(0.0, n.vision_xy_sigma_mm), r.normal(0.0, n.vision_z_sigma_mm)]
        ) * MM
        tilt = np.array([r.normal(0.0, n.vision_tilt_sigma_deg), r.normal(0.0, n.vision_tilt_sigma_deg), 0.0]) * DEG
        yaw = r.normal(0.0, n.vision_yaw_sigma_deg) * DEG
        # Orientation error expressed in the socket frame: yaw about the socket axis, tilt about its x/y.
        R_err = rotvec_to_matrix(tilt) @ rotvec_to_matrix(np.array([0.0, 0.0, yaw]))
        return Pose(true_socket_pose.p + dp + self.vision_bias, true_socket_pose.R @ R_err)

    def grasp_measurement(self, true_grasp: Pose) -> Pose:
        n = self.noise
        r = self._rng_grasp
        dp = np.array([r.normal(0.0, n.grasp_xy_sigma_mm), r.normal(0.0, n.grasp_xy_sigma_mm), 0.0]) * MM
        rv = r.normal(0.0, n.grasp_rot_sigma_deg, 3) * DEG
        return Pose(true_grasp.p + dp, true_grasp.R @ rotvec_to_matrix(rv))

    # -------------------------------------------------------------- streaming sensors
    def measure(self, raw: RawSensorData) -> SensorReadings:
        e = self._rng_enc.standard_normal(6)
        w = self._rng_ft.standard_normal(6)
        dp = e[:3] * self._enc_pos_sigma
        drv = e[3:] * self._enc_rot_sigma
        # Encoder noise is micro-radian scale: first-order rotation update is exact to 1e-10.
        dR = np.array([[1.0, -drv[2], drv[1]], [drv[2], 1.0, -drv[0]], [-drv[1], drv[0], 1.0]])
        tcp = Pose(raw.tcp_pose.p + dp, raw.tcp_pose.R @ dR)
        f = raw.ft_force + self.ft_force_bias + w[:3] * self.noise.ft_force_sigma_n
        t = raw.ft_torque + self.ft_torque_bias + w[3:] * self.noise.ft_torque_sigma_nm
        return SensorReadings(t=raw.t, tcp_pose=tcp, ft_force=f, ft_torque=t)
