import mujoco
import numpy as np

from defex.utils.transforms import (
    Pose,
    cross3,
    euler_zyx_to_matrix,
    matrix_to_euler_zyx,
    matrix_to_quat,
    matrix_to_rotvec,
    norm3,
    quat_to_matrix,
    rotvec_to_matrix,
    transform_wrench,
    twist_about_axis,
)


def test_rotvec_matches_mujoco(rng):
    for _ in range(300):
        rv = rng.normal(size=3) * rng.uniform(0.0, 3.0)
        q = np.zeros(4)
        angle = np.linalg.norm(rv)
        mujoco.mju_axisAngle2Quat(q, rv / angle, angle)
        R_mj = np.zeros(9)
        mujoco.mju_quat2Mat(R_mj, q)
        np.testing.assert_allclose(rotvec_to_matrix(rv), R_mj.reshape(3, 3), atol=1e-12)
        np.testing.assert_allclose(rotvec_to_matrix(matrix_to_rotvec(rotvec_to_matrix(rv))), rotvec_to_matrix(rv), atol=1e-9)


def test_quaternion_round_trip(rng):
    for _ in range(300):
        q = rng.normal(size=4)
        q /= np.linalg.norm(q)
        R = quat_to_matrix(q)
        np.testing.assert_allclose(quat_to_matrix(matrix_to_quat(R)), R, atol=1e-12)
        R_mj = np.zeros(9)
        mujoco.mju_quat2Mat(R_mj, q)
        np.testing.assert_allclose(R, R_mj.reshape(3, 3), atol=1e-12)


def test_euler_zyx_round_trip(rng):
    for _ in range(300):
        y, p, r = rng.uniform(-1.2, 1.2, 3)
        assert np.allclose(matrix_to_euler_zyx(euler_zyx_to_matrix(y, p, r)), (y, p, r))


def test_pose_algebra(rng):
    for _ in range(100):
        a = Pose.from_rotvec(rng.normal(size=3), rng.normal(size=3))
        b = Pose.from_rotvec(rng.normal(size=3), rng.normal(size=3))
        x = rng.normal(size=3)
        np.testing.assert_allclose((a @ b).apply(x), a.apply(b.apply(x)), atol=1e-12)
        np.testing.assert_allclose((a @ a.inv()).p, np.zeros(3), atol=1e-12)
        np.testing.assert_allclose((a @ a.inv()).R, np.eye(3), atol=1e-12)
        np.testing.assert_allclose(Pose.from_array(a.as_array()).R, a.R, atol=1e-12)


def test_fast_vector_helpers(rng):
    for _ in range(100):
        a, b = rng.normal(size=3), rng.normal(size=3)
        np.testing.assert_allclose(cross3(a, b), np.cross(a, b))
        assert abs(norm3(a) - np.linalg.norm(a)) < 1e-12


def test_wrench_reference_shift():
    # 1 N along x applied at A=(0,0,1); torque about the origin is r x F = (0, 1, 0).
    f, t = transform_wrench(np.array([1.0, 0, 0]), np.zeros(3), np.array([0, 0, 1.0]))
    np.testing.assert_allclose(t, [0.0, 1.0, 0.0])


def test_twist_extraction():
    for ang in (-0.3, 0.05, 0.4):
        R = rotvec_to_matrix(np.array([0.02, -0.01, 0.0])) @ euler_zyx_to_matrix(ang, 0, 0)
        assert abs(twist_about_axis(R) - ang) < 2e-3
