"""Rigid-body transform utilities (pure NumPy, backend independent).

Conventions
-----------
* Quaternions are scalar-first ``(w, x, y, z)``, matching MuJoCo.
* Rotation matrices map body-frame vectors into the parent frame.
* ``Pose(p, R)`` maps a point ``x_b`` in the child frame to ``p + R @ x_b`` in the
  parent frame.
* Euler angles use the intrinsic Z-Y'-X'' (yaw, pitch, roll) sequence, which is
  exactly the joint order of the insertion fixture's wrist.

These helpers are deliberately free of MuJoCo imports so that controllers and
estimators stay simulator-agnostic.
"""

from __future__ import annotations

import math

import numpy as np

_EPS = 1e-12


def cross3(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cross product of two 3-vectors (~20x faster than ``np.cross`` for single vectors)."""
    a0, a1, a2 = a.tolist() if isinstance(a, np.ndarray) else a
    b0, b1, b2 = b.tolist() if isinstance(b, np.ndarray) else b
    return np.array([a1 * b2 - a2 * b1, a2 * b0 - a0 * b2, a0 * b1 - a1 * b0])


def norm3(v: np.ndarray) -> float:
    """Euclidean norm of a 3-vector (or any short vector)."""
    return math.sqrt(float(np.dot(v, v)))


def skew(v: np.ndarray) -> np.ndarray:
    """Return the 3x3 cross-product matrix of ``v``."""
    x, y, z = v
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])


def rotvec_to_matrix(rv: np.ndarray) -> np.ndarray:
    """Exponential map from a rotation vector (axis * angle) to a rotation matrix."""
    x, y, z = rv.tolist() if isinstance(rv, np.ndarray) else rv
    theta = math.sqrt(x * x + y * y + z * z)
    if theta < 1e-9:
        return np.array([[1.0, -z, y], [z, 1.0, -x], [-y, x, 1.0]])
    kx, ky, kz = x / theta, y / theta, z / theta
    c = math.cos(theta)
    s_ = math.sin(theta)
    v = 1.0 - c
    return np.array(
        [
            [c + kx * kx * v, kx * ky * v - kz * s_, kx * kz * v + ky * s_],
            [ky * kx * v + kz * s_, c + ky * ky * v, ky * kz * v - kx * s_],
            [kz * kx * v - ky * s_, kz * ky * v + kx * s_, c + kz * kz * v],
        ]
    )


def matrix_to_rotvec(R: np.ndarray) -> np.ndarray:
    """Logarithmic map from a rotation matrix to a rotation vector."""
    (r00, r01, r02), (r10, r11, r12), (r20, r21, r22) = R.tolist()
    cos_theta = min(1.0, max(-1.0, (r00 + r11 + r22 - 1.0) * 0.5))
    theta = math.acos(cos_theta)
    w = np.array([r21 - r12, r02 - r20, r10 - r01])
    if theta < 1e-6:
        return 0.5 * w
    if np.pi - theta < 1e-4:
        # Near 180 degrees: recover the axis from the symmetric part.
        axis = np.sqrt(np.maximum((np.diag(R) + 1.0) * 0.5, 0.0))
        # Fix signs using the largest component.
        i = int(np.argmax(axis))
        if i == 0:
            axis[1] = np.copysign(axis[1], R[0, 1] + R[1, 0])
            axis[2] = np.copysign(axis[2], R[0, 2] + R[2, 0])
        elif i == 1:
            axis[0] = np.copysign(axis[0], R[0, 1] + R[1, 0])
            axis[2] = np.copysign(axis[2], R[1, 2] + R[2, 1])
        else:
            axis[0] = np.copysign(axis[0], R[0, 2] + R[2, 0])
            axis[1] = np.copysign(axis[1], R[1, 2] + R[2, 1])
        return axis / max(np.linalg.norm(axis), _EPS) * theta
    return w * (theta / (2.0 * math.sin(theta)))


def quat_to_matrix(q: np.ndarray) -> np.ndarray:
    """Convert a unit quaternion ``(w, x, y, z)`` to a rotation matrix."""
    w, x, y, z = np.asarray(q, dtype=float) / max(np.linalg.norm(q), _EPS)
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
            [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
            [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
        ]
    )


def matrix_to_quat(R: np.ndarray) -> np.ndarray:
    """Convert a rotation matrix to a unit quaternion ``(w, x, y, z)`` with ``w >= 0``."""
    m = np.asarray(R, dtype=float)
    tr = m[0, 0] + m[1, 1] + m[2, 2]
    if tr > 0.0:
        s = np.sqrt(tr + 1.0) * 2.0
        q = np.array([0.25 * s, (m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s])
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2.0
        q = np.array([(m[2, 1] - m[1, 2]) / s, 0.25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s])
    elif m[1, 1] > m[2, 2]:
        s = np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2.0
        q = np.array([(m[0, 2] - m[2, 0]) / s, (m[0, 1] + m[1, 0]) / s, 0.25 * s, (m[1, 2] + m[2, 1]) / s])
    else:
        s = np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2.0
        q = np.array([(m[1, 0] - m[0, 1]) / s, (m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, 0.25 * s])
    q /= np.linalg.norm(q)
    return q if q[0] >= 0.0 else -q


def euler_zyx_to_matrix(yaw: float, pitch: float, roll: float) -> np.ndarray:
    """Intrinsic Z-Y'-X'' rotation: ``Rz(yaw) @ Ry(pitch) @ Rx(roll)``."""
    cz, sz = np.cos(yaw), np.sin(yaw)
    cy, sy = np.cos(pitch), np.sin(pitch)
    cx, sx = np.cos(roll), np.sin(roll)
    rz = np.array([[cz, -sz, 0.0], [sz, cz, 0.0], [0.0, 0.0, 1.0]])
    ry = np.array([[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]])
    rx = np.array([[1.0, 0.0, 0.0], [0.0, cx, -sx], [0.0, sx, cx]])
    return rz @ ry @ rx


def matrix_to_euler_zyx(R: np.ndarray) -> tuple[float, float, float]:
    """Inverse of :func:`euler_zyx_to_matrix`; returns ``(yaw, pitch, roll)``."""
    pitch = float(-np.arcsin(np.clip(R[2, 0], -1.0, 1.0)))
    yaw = float(np.arctan2(R[1, 0], R[0, 0]))
    roll = float(np.arctan2(R[2, 1], R[2, 2]))
    return yaw, pitch, roll


def rot_z(angle: float) -> np.ndarray:
    return euler_zyx_to_matrix(angle, 0.0, 0.0)


def tilt_matrix(magnitude: float, azimuth: float) -> np.ndarray:
    """Rotation by ``magnitude`` about the horizontal axis at angle ``azimuth`` from +x."""
    axis = np.array([np.cos(azimuth), np.sin(azimuth), 0.0])
    return rotvec_to_matrix(axis * magnitude)


def axis_angle_between(z_a: np.ndarray, z_b: np.ndarray) -> float:
    """Angle (rad) between two direction vectors."""
    c = float(np.dot(z_a, z_b) / max(np.linalg.norm(z_a) * np.linalg.norm(z_b), _EPS))
    return float(np.arccos(np.clip(c, -1.0, 1.0)))


def twist_about_axis(R_rel: np.ndarray, axis: np.ndarray = np.array([0.0, 0.0, 1.0])) -> float:
    """Swing-twist decomposition: signed twist angle of ``R_rel`` about ``axis``."""
    q = matrix_to_quat(R_rel)
    proj = float(np.dot(q[1:], axis))
    return float(2.0 * np.arctan2(proj, q[0]))


class Pose:
    """Rigid transform with translation ``p`` (m) and rotation matrix ``R``.

    Treated as immutable by convention (methods return new poses). Implemented as a
    slotted class rather than a frozen dataclass because poses are created many
    times per control tick.
    """

    __slots__ = ("p", "R")

    def __init__(self, p: np.ndarray, R: np.ndarray) -> None:
        self.p = p
        self.R = R

    def __repr__(self) -> str:
        return f"Pose(p={np.round(self.p, 6).tolist()}, rotvec={np.round(matrix_to_rotvec(self.R), 6).tolist()})"

    @staticmethod
    def identity() -> "Pose":
        return Pose(np.zeros(3), np.eye(3))

    @staticmethod
    def from_quat(p: np.ndarray, q: np.ndarray) -> "Pose":
        return Pose(np.asarray(p, dtype=float).copy(), quat_to_matrix(q))

    @staticmethod
    def from_rotvec(p: np.ndarray, rv: np.ndarray) -> "Pose":
        return Pose(np.asarray(p, dtype=float).copy(), rotvec_to_matrix(np.asarray(rv, dtype=float)))

    def quat(self) -> np.ndarray:
        return matrix_to_quat(self.R)

    def inv(self) -> "Pose":
        Rt = self.R.T
        return Pose(-(Rt @ self.p), Rt)

    def __matmul__(self, other: "Pose") -> "Pose":
        return Pose(self.p + self.R @ other.p, self.R @ other.R)

    def apply(self, x: np.ndarray) -> np.ndarray:
        """Transform a point from the child frame into the parent frame."""
        return self.p + self.R @ np.asarray(x)

    def rotate(self, v: np.ndarray) -> np.ndarray:
        return self.R @ np.asarray(v)

    def translated(self, dp_world: np.ndarray) -> "Pose":
        return Pose(self.p + np.asarray(dp_world), self.R)

    def as_array(self) -> np.ndarray:
        """Return ``[x, y, z, qw, qx, qy, qz]``."""
        return np.concatenate([self.p, self.quat()])

    @staticmethod
    def from_array(a: np.ndarray) -> "Pose":
        a = np.asarray(a, dtype=float)
        return Pose.from_quat(a[:3], a[3:7])


def pose_error(target: Pose, current: Pose) -> tuple[np.ndarray, np.ndarray]:
    """Position error and world-frame rotation-vector error (target relative to current)."""
    dp = target.p - current.p
    dr = matrix_to_rotvec(target.R @ current.R.T)
    return dp, dr


def transform_wrench(force: np.ndarray, torque: np.ndarray, r_from_to: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Shift a wrench's reference point.

    ``force`` and ``torque`` are referenced at point A. ``r_from_to`` is the vector
    from the new reference point B to A (``A - B``), in the same frame. Returns the
    equivalent wrench referenced at B.
    """
    return force, torque + cross3(r_from_to, force)
