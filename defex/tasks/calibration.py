"""Cell calibration routines that run through the backend like real hardware.

``identify_payload`` holds the tool at a set of wrist orientations in free space
above the socket, averages the noisy F/T and encoder readings at each one, and
fits the payload with :func:`defex.perception.payload_id.fit_payload`. It uses its
own noise stream, so it does not shift any trial's sensor noise.
"""

from __future__ import annotations

import zlib

import numpy as np

from defex.config import DEG, FixtureConfig, SensorNoiseConfig
from defex.control.base import Command
from defex.control.motion import CartesianMotionGenerator
from defex.perception.payload_id import PayloadFit, StaticSample, fit_payload
from defex.perception.sensors import SensorSuite
from defex.sim.backend import PayloadModel, SimBackend
from defex.utils.transforms import Pose, rotvec_to_matrix

IDENTIFICATION_TILT_DEG = 20.0  # inside the 25 deg wrist range
SETTLE_S = 0.3
SAMPLE_S = 0.5  # averaging per pose; error is F/T-noise limited (exact without noise)


def identification_orientations(tilt_deg: float = IDENTIFICATION_TILT_DEG) -> list[np.ndarray]:
    a = tilt_deg * DEG
    d = a / np.sqrt(2.0)
    rvs = [(0, 0, 0), (a, 0, 0), (-a, 0, 0), (0, a, 0), (0, -a, 0), (d, d, 0), (d, -d, 0), (-d, d, 0), (-d, -d, 0)]
    return [np.array(rv, dtype=float) for rv in rvs]


def calibration_seed(connector_name: str) -> int:
    return zlib.crc32(f"payload-identification:{connector_name}".encode())


def identify_payload(
    backend: SimBackend,
    fixture: FixtureConfig,
    noise: SensorNoiseConfig,
    control_period_s: float,
    seed: int,
    orientations: list[np.ndarray] | None = None,
) -> PayloadFit:
    """Run the identification motion on an already loaded scene (nominal grasp)."""
    dt = control_period_s
    sensors = SensorSuite(noise, seed)
    sensor_in_tcp = backend.ft_sensor_in_tcp
    home = backend.home_tcp_pose
    motion = CartesianMotionGenerator(fixture, dt)
    motion.reset(home)
    backend.set_tcp_setpoint(home)
    ang = fixture.max_angular_speed_deg_s * DEG
    lin = fixture.max_linear_speed_mm_s * 1e-3
    samples = []
    for rv in orientations or identification_orientations():
        target = Pose(home.p.copy(), rotvec_to_matrix(rv))
        cmd = Command(target, lin, ang)
        for _ in range(int(round(10.0 / dt))):
            sp = motion.update(cmd)
            backend.set_tcp_setpoint(sp)
            backend.step(dt)
            if np.allclose(sp.p, target.p, atol=1e-9) and np.allclose(sp.R, target.R, atol=1e-9):
                break
        for _ in range(int(round(SETTLE_S / dt))):
            backend.step(dt)
        fs, ts, Rs = [], [], []
        for _ in range(int(round(SAMPLE_S / dt))):
            backend.step(dt)
            r = sensors.measure(backend.read_sensors())
            fs.append(r.ft_force)
            ts.append(r.ft_torque)
            Rs.append((r.tcp_pose @ sensor_in_tcp).R)
        samples.append(StaticSample(np.mean(Rs, axis=0), np.mean(fs, axis=0), np.mean(ts, axis=0)))
    return fit_payload(samples, sensor_in_tcp)


def identification_error(fit: PayloadFit, truth: PayloadModel) -> dict[str, float]:
    """Compare a fit with the simulator's mass properties (reporting only)."""
    return {
        "mass_true_g": truth.mass_kg * 1e3,
        "mass_identified_g": fit.payload.mass_kg * 1e3,
        "mass_error_g": (fit.payload.mass_kg - truth.mass_kg) * 1e3,
        "com_error_mm": float(np.linalg.norm(fit.payload.com_in_sensor - truth.com_in_sensor)) * 1e3,
        "force_rms_residual_n": fit.force_rms_residual_n,
        "torque_rms_residual_nmm": fit.torque_rms_residual_nm * 1e3,
        "n_poses": fit.n_poses,
    }
