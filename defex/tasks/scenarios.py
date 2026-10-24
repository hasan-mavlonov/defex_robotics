"""Scenario sampling with paired, reproducible seeds.

A *condition* describes a family of disturbances (e.g. "lateral error 3 mm"). A
*scenario* is one concrete draw from it. The draw depends only on
``(base_seed, condition name, trial index)``, so every controller sees exactly the
same socket pose, grasp offset and vision measurement for a given trial index
(paired comparison).
"""

from __future__ import annotations

import zlib
from dataclasses import dataclass, field

import numpy as np

from defex.config import DEG, MM, Condition, ConnectorSpec, SensorNoiseConfig
from defex.utils.transforms import Pose, rot_z, rotvec_to_matrix, tilt_matrix


@dataclass(frozen=True)
class Scenario:
    condition: str
    group: str
    trial_index: int
    seed: int
    connector: ConnectorSpec
    friction: float
    socket_pose: Pose  # true socket mouth pose (world)
    grasp_offset: Pose  # true connector tip pose relative to the fixture TCP
    noise: SensorNoiseConfig
    disturbance: dict[str, float] = field(default_factory=dict)


def trial_seed(base_seed: int, condition_name: str, trial_index: int) -> int:
    ss = np.random.SeedSequence([int(base_seed), zlib.crc32(condition_name.encode()), int(trial_index)])
    return int(ss.generate_state(1, dtype=np.uint64)[0] & np.uint64(0x7FFFFFFFFFFFFFFF))


def _signed(rng: np.random.Generator, magnitude: float, mode: str) -> float:
    if magnitude == 0.0:
        return 0.0
    if mode == "fixed":
        return float(magnitude * rng.choice([-1.0, 1.0]))
    return float(rng.uniform(-magnitude, magnitude))


def resolve_connector(condition: Condition) -> ConnectorSpec:
    spec = ConnectorSpec.load(condition.connector)
    if condition.clearance_mm is not None or condition.chamfer_mm is not None:
        spec = spec.with_overrides(condition.clearance_mm, condition.chamfer_mm)
    return spec


def sample_scenario(condition: Condition, trial_index: int, base_seed: int, nominal_socket: Pose) -> Scenario:
    seed = trial_seed(base_seed, condition.name, trial_index)
    # Dedicated stream for the disturbance (sensor streams are derived separately).
    rng = np.random.default_rng(np.random.SeedSequence(seed).spawn(5)[4])
    dist = condition.disturbance
    spec = resolve_connector(condition)

    phi = rng.uniform(0.0, 2.0 * np.pi)
    if dist.lateral_mode == "fixed":
        r = dist.lateral_mm
    else:
        r = dist.lateral_mm * np.sqrt(rng.uniform())
    dx, dy = r * np.cos(phi), r * np.sin(phi)
    yaw = _signed(rng, dist.yaw_deg, dist.yaw_mode)
    tilt_az = rng.uniform(0.0, 2.0 * np.pi)
    tilt = dist.tilt_deg if dist.tilt_mode == "fixed" else dist.tilt_deg * rng.uniform()
    dz = rng.uniform(-dist.height_mm, dist.height_mm) if dist.height_mm > 0 else 0.0

    R = tilt_matrix(tilt * DEG, tilt_az) @ rot_z(yaw * DEG) @ nominal_socket.R
    socket_pose = Pose(nominal_socket.p + np.array([dx, dy, dz]) * MM, R)

    g_lat = rng.uniform(-dist.grasp_lateral_mm, dist.grasp_lateral_mm) if dist.grasp_lateral_mm > 0 else 0.0
    g_ax = -rng.uniform(0.0, dist.grasp_axial_mm) if dist.grasp_axial_mm > 0 else 0.0
    g_tilt = rng.uniform(-dist.grasp_tilt_deg, dist.grasp_tilt_deg) if dist.grasp_tilt_deg > 0 else 0.0
    grip_center = np.array([0.0, 0.0, (spec.plug.length_mm - spec.plug.grip_length_mm * 0.5) * MM])
    Rg = rotvec_to_matrix(np.array([g_tilt * DEG, 0.0, 0.0]))
    grasp = Pose(grip_center + Rg @ (np.array([0.0, g_lat * MM, g_ax * MM]) - grip_center), Rg)

    friction = spec.friction if condition.friction is None else condition.friction
    return Scenario(
        condition=condition.name,
        group=condition.group,
        trial_index=trial_index,
        seed=seed,
        connector=spec,
        friction=float(friction),
        socket_pose=socket_pose,
        grasp_offset=grasp,
        noise=condition.noise,
        disturbance={
            "dx_mm": float(dx),
            "dy_mm": float(dy),
            "dz_mm": float(dz),
            "lateral_mm": float(np.hypot(dx, dy)),
            "yaw_deg": float(yaw),
            "tilt_deg": float(tilt),
            "tilt_azimuth_deg": float(np.rad2deg(tilt_az)),
            "grasp_lateral_mm": float(g_lat),
            "grasp_axial_mm": float(g_ax),
            "grasp_tilt_deg": float(g_tilt),
        },
    )
