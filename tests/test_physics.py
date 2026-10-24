"""Physics validation of the workcell against hand calculations."""

import numpy as np

from defex.config import MM, SensorNoiseConfig
from defex.perception.sensors import SensorSuite
from defex.perception.state_estimator import StateEstimator
from defex.recovery.search_policy import predicted_cop
from defex.utils.transforms import Pose


def _descend(backend, dx=0.0, dy=0.0, depth_target=15.5 * MM, speed=6 * MM, start_above=1 * MM):
    S = backend.nominal_socket_pose
    backend.reset()
    peak, pen = 0.0, 0.0
    z = start_above
    p0 = Pose(S.p + np.array([dx, dy, z]), S.R)
    backend.set_joint_positions_kinematic(backend.inverse_kinematics(p0))
    backend.set_tcp_setpoint(p0)
    while z > -depth_target:
        z = max(-depth_target, z - speed * 0.002)
        backend.set_tcp_setpoint(Pose(S.p + np.array([dx, dy, z]), S.R))
        backend.step(0.002)
        gt = backend.ground_truth()
        peak, pen = max(peak, gt.contact_force_norm), max(pen, gt.max_penetration)
    for _ in range(200):
        backend.step(0.002)
        gt = backend.ground_truth()
        peak, pen = max(peak, gt.contact_force_norm), max(pen, gt.max_penetration)
    rel = S.inv() @ gt.connector_pose
    return -rel.p[2], peak, pen, gt


def test_nominal_insertion_is_seated_without_interpenetration(backend):
    depth, peak, pen, gt = _descend(backend)
    assert abs(depth - 15 * MM) < 0.02 * MM
    # 0.5 mm programmed overtravel on a 10 N/mm servo -> 5 N preload, plus the weight of
    # the tool and connector (fixture links are gravity-compensated, the payload is not).
    expected = 5.0 + backend.payload.mass_kg * 9.81
    assert abs(gt.contact_force_norm - expected) < 0.05
    assert pen < 0.01 * MM


def test_lead_in_guides_and_rim_blocks(backend):
    depth, peak, _, _ = _descend(backend, dx=1.0 * MM)
    assert depth > 14.9 * MM  # captured by the 0.8 mm lead-in
    # Coulomb estimate on a 45 deg chamfer with mu=0.3: about 12 N. Guards against the
    # soft-friction normal-force inflation that solreffriction removes (was ~42 N).
    assert peak < 18.0
    depth, _, _, _ = _descend(backend, dx=1.5 * MM, depth_target=2 * MM)
    assert depth < 0.3 * MM  # outside the lead-in: blocked on the rim


def test_ft_sensor_convention_and_compensation(backend):
    backend.reset()
    backend.set_tcp_setpoint(backend.home_tcp_pose)
    backend.step(0.3)
    raw = backend.read_sensors()
    # The force sensor reports the wrist's force on the tool: +m g in free space.
    np.testing.assert_allclose(raw.ft_force, [0, 0, backend.payload.mass_kg * 9.81], atol=2e-3)
    # Estimated external wrench equals the ground-truth contact force when pressing.
    noise = SensorNoiseConfig(ft_force_sigma_n=0.0, ft_torque_sigma_nm=0.0, ft_force_bias_n=0.0, ft_torque_bias_nm=0.0,
                              encoder_pos_sigma_mm=0.0, encoder_rot_sigma_deg=0.0)
    sensors = SensorSuite(noise, 0)
    est = StateEstimator(backend.payload, 0.002, 40.0)
    est.reset(backend.nominal_socket_pose, Pose.identity())
    _, _, _, gt = _descend(backend, depth_target=15.8 * MM)
    for _ in range(50):
        backend.step(0.002)
        obs = est.update(sensors.measure(backend.read_sensors()), backend.home_tcp_pose)
    np.testing.assert_allclose(obs.force_world, backend.ground_truth().contact_force, atol=0.05)


def test_measured_center_of_pressure_matches_forward_model(backend, spec):
    S = backend.nominal_socket_pose
    noise = SensorNoiseConfig()
    for k, (ox, oy) in enumerate([(2.0, 0.0), (4.0, 0.0), (0.0, 3.0), (2.5, 2.5), (-2.5, 1.0)]):
        backend.reset()
        sensors = SensorSuite(noise, 100 + k)
        est = StateEstimator(backend.payload, 0.002, noise.ft_filter_cutoff_hz)
        est.reset(S, Pose.identity())
        backend.set_tcp_setpoint(backend.home_tcp_pose)
        for i in range(100):
            if i == 50:
                est.begin_tare()
            backend.step(0.002)
            est.update(sensors.measure(backend.read_sensors()), backend.home_tcp_pose)
        est.end_tare()
        p_above = Pose(S.p + np.array([ox, oy, 1.0]) * MM, S.R)
        backend.set_joint_positions_kinematic(backend.inverse_kinematics(p_above))
        for i in range(400):
            z = 1.0 - min(i / 200, 1.0) * 1.6
            backend.set_tcp_setpoint(Pose(S.p + np.array([ox, oy, z]) * MM, S.R))
            backend.step(0.002)
        obs = [est.update(sensors.measure(backend.read_sensors()), backend.home_tcp_pose) for _ in range(60)
               if backend.step(0.002) is None]
        F = np.mean([o.force for o in obs], axis=0)
        T = np.mean([o.torque for o in obs], axis=0)
        cop = np.array([-T[1] / F[2], T[0] / F[2]])
        lat = np.mean([o.lateral for o in obs], axis=0)
        pred = predicted_cop(spec, lat)
        assert pred is not None
        assert np.linalg.norm(cop - pred) < 0.3 * MM, (ox, oy, cop / MM, pred / MM)
