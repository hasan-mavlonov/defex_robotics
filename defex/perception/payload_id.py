"""Payload identification from static wrist F/T readings.

A real cell does not know the mass properties below its F/T sensor exactly. It
holds the tool at several orientations in free space, averages the sensor at each
one, and fits the payload by least squares. At rest the sensor reads

    f = -m u + b_f
    t = u x (m c) + b_t        with u = R_sensor^T g (gravity in the sensor frame)

which is linear in (m, b_f) and in (m c, b_t). The sensor biases are nuisance
parameters fitted alongside, because taring only removes them at one orientation.
Orientations must span more than one gravity direction in the sensor frame: pure
yaw about the vertical leaves ``u`` unchanged and adds no information.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from defex.sim.backend import PayloadModel
from defex.utils.transforms import Pose

GRAVITY = np.array([0.0, 0.0, -9.81])


@dataclass(frozen=True)
class StaticSample:
    sensor_R_world: np.ndarray  # (3, 3) sensor orientation from the encoders
    force: np.ndarray  # (3,) mean raw F/T force at rest, sensor frame (N)
    torque: np.ndarray  # (3,) mean raw F/T torque at rest, sensor frame (N m)


@dataclass(frozen=True)
class PayloadFit:
    payload: PayloadModel
    force_bias: np.ndarray
    torque_bias: np.ndarray
    force_rms_residual_n: float
    torque_rms_residual_nm: float
    n_poses: int


def _skew(v: np.ndarray) -> np.ndarray:
    return np.array([[0.0, -v[2], v[1]], [v[2], 0.0, -v[0]], [-v[1], v[0], 0.0]])


def fit_payload(samples: list[StaticSample], sensor_in_tcp: Pose) -> PayloadFit:
    if len(samples) < 3:
        raise ValueError("payload identification needs at least three orientations")
    us = [s.sensor_R_world.T @ GRAVITY for s in samples]
    if np.linalg.matrix_rank(np.array(us), tol=1e-3) < 2:
        raise ValueError("orientations do not span enough gravity directions")

    eye = np.eye(3)
    A_f = np.vstack([np.column_stack([-u, eye]) for u in us])
    y_f = np.concatenate([s.force for s in samples])
    x_f, *_ = np.linalg.lstsq(A_f, y_f, rcond=None)
    mass = float(x_f[0])

    A_t = np.vstack([np.hstack([_skew(u), eye]) for u in us])
    y_t = np.concatenate([s.torque for s in samples])
    x_t, *_ = np.linalg.lstsq(A_t, y_t, rcond=None)
    com = x_t[:3] / mass

    res_f = A_f @ x_f - y_f
    res_t = A_t @ x_t - y_t
    return PayloadFit(
        payload=PayloadModel(mass_kg=mass, com_in_sensor=com, sensor_in_tcp=sensor_in_tcp),
        force_bias=x_f[1:].copy(),
        torque_bias=x_t[3:].copy(),
        force_rms_residual_n=float(np.sqrt(np.mean(res_f**2))),
        torque_rms_residual_nm=float(np.sqrt(np.mean(res_t**2))),
        n_poses=len(samples),
    )
