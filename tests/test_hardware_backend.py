"""W7: the unchanged harness runs on HardwareBackend (mocks in CI), and the Net F/T driver speaks RDT."""

import socket
import threading
from dataclasses import replace

import numpy as np
import pytest

from defex.config import MM, SensorNoiseConfig
from defex.control.registry import make_controller
from defex.hardware.backend import HardwareBackend, hardware_noise
from defex.hardware.drivers import RDT_RECORD, RDT_REQUEST, FTSensorFault, MockFTSensor, MockMotionStage, NetFTDriver
from defex.sim.backend import FixtureDynamics
from defex.tasks.conditions import conditions_by_name
from defex.tasks.insertion import InsertionTask
from defex.tasks.scenarios import sample_scenario
from defex.utils.transforms import Pose

SENSOR = Pose(np.array([0.0, 0.0, 0.037]), np.eye(3))
MOUTH = Pose(np.array([0.0, 0.0, 0.04]), np.eye(3))
HOME = Pose(MOUTH.p + np.array([0.0, 0.0, 0.06]), np.eye(3))
# The mock stage stands in for the gantry: every value stated, as the backend requires.
MOCK_DYNAMICS = FixtureDynamics(10.0, 15.0, 0.9, 0.0, tilt_stiffness_nm_per_rad=15.0, following_lag_s=0.037,
                                rotational_following_lag_s=0.024)


def _mock_task(floor_depth_mm: float) -> tuple[InsertionTask, HardwareBackend]:
    stage = MockMotionStage(HOME, floor_z=MOUTH.p[2] - floor_depth_mm * MM)
    ft = MockFTSensor(stage, payload_mass_kg=0.034, payload_com_in_sensor=np.array([0.0, 0.0, -0.009]),
                      sensor_in_tcp=SENSOR)
    be = HardwareBackend(stage, ft, SENSOR, MOUTH, MOCK_DYNAMICS)
    task = InsertionTask(backend=be)
    task.identification_noise = hardware_noise(SensorNoiseConfig())
    return task, be


def _scenario(task):
    sc = sample_scenario(conditions_by_name()["nominal"], 0, 2026, task.backend.nominal_socket_pose)
    return replace(sc, noise=hardware_noise(sc.noise))


def test_harness_runs_unchanged_on_the_hardware_backend():
    task, be = _mock_task(floor_depth_mm=15.0)
    res = task.run(make_controller("fixed"), _scenario(task))
    assert res.success, res.failure_reason
    assert abs(res.final_depth_mm - 15.0) < 0.2
    assert be.ground_truth().source == "measured"
    fit = task.payload_fit(_scenario(task))
    assert abs(fit.payload.mass_kg - 0.034) < 1e-6  # identified on the mock, no noise


def test_adaptive_never_accepts_a_socket_without_walls():
    """A floor at full depth but no cavity walls: the wall probes must fail, so C may not declare success."""
    task, _ = _mock_task(floor_depth_mm=15.0)
    res = task.run(make_controller("adaptive"), _scenario(task))
    assert res.declared_success is not True, [e for e in res.events if e[1] in ("verify", "finish")]
    verdicts = [d for _, k, d in res.events if k == "verify"]
    assert verdicts and all(v.endswith("FAIL") for v in verdicts), verdicts  # rejected by the wall probes


def _fake_netft(records):
    srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    srv.bind(("127.0.0.1", 0))

    def serve():
        for rec in records:
            data, addr = srv.recvfrom(64)
            assert RDT_REQUEST.unpack(data) == (0x1234, 2, 1)
            srv.sendto(RDT_RECORD.pack(*rec), addr)

    th = threading.Thread(target=serve, daemon=True)
    th.start()
    return srv, srv.getsockname()[1], th


def test_netft_driver_decodes_rdt_records_and_applies_the_sign_convention():
    cpf = cpt = 1_000_000
    ft = [int(v * cpf) for v in (1.5, -2.0, 10.25)] + [int(v * cpt) for v in (0.01, -0.02, 0.003)]
    srv, port, th = _fake_netft([(7, 9, 0, *ft), (8, 10, 0, *ft)])
    wrist = NetFTDriver("127.0.0.1", cpf, cpt, "wrist_on_tool", port=port, timeout_s=2.0)
    s = wrist.read()
    assert np.allclose(s.force, [1.5, -2.0, 10.25]) and np.allclose(s.torque, [0.01, -0.02, 0.003])
    load = NetFTDriver("127.0.0.1", cpf, cpt, "load_on_sensor", port=port, timeout_s=2.0)
    s2 = load.read()
    assert np.allclose(s2.force, [-1.5, 2.0, -10.25])
    th.join(2.0)
    srv.close()
    with pytest.raises(ValueError):
        NetFTDriver("127.0.0.1", cpf, cpt, "unknown")


def test_netft_driver_rejects_fault_records():
    srv, port, th = _fake_netft([(1, 1, 0x80000000, 0, 0, 0, 0, 0, 0)])
    drv = NetFTDriver("127.0.0.1", 1e6, 1e6, "wrist_on_tool", port=port, timeout_s=2.0)
    with pytest.raises(FTSensorFault):
        drv.read()
    th.join(2.0)
    srv.close()


def test_hardware_backend_stops_motion_on_a_sensor_fault():
    class Faulty:
        def read(self):
            raise FTSensorFault("saturated")

    stage = MockMotionStage(HOME, floor_z=0.0)
    be = HardwareBackend(stage, Faulty(), SENSOR, MOUTH, MOCK_DYNAMICS)
    with pytest.raises(FTSensorFault):
        be.read_sensors()
    assert getattr(stage, "stopped", False)


def test_hardware_backend_refuses_uncharacterized_fixture_dynamics():
    """Checkpoint 2 review: a fixture without its W5b values ran C in a mixed configuration."""
    stage = MockMotionStage(HOME, floor_z=0.0)
    ft = MockFTSensor(stage, payload_mass_kg=0.034, payload_com_in_sensor=np.zeros(3), sensor_in_tcp=SENSOR)
    for field in ("tilt_stiffness_nm_per_rad", "following_lag_s", "rotational_following_lag_s"):
        with pytest.raises(ValueError, match=field):
            HardwareBackend(stage, ft, SENSOR, MOUTH, replace(MOCK_DYNAMICS, **{field: None}))
    with pytest.raises(ValueError):
        HardwareBackend(stage, ft, SENSOR, MOUTH, FixtureDynamics(8.0, 400.0, 6.3, 0.006))


def test_hardware_ground_truth_uses_the_nominal_grasp_not_the_scenario_draw():
    task, be = _mock_task(floor_depth_mm=15.0)
    sc = sample_scenario(conditions_by_name()["generalization_combined"], 0, 2026, be.nominal_socket_pose)
    sc = replace(sc, noise=hardware_noise(sc.noise))
    assert not np.allclose(sc.grasp_offset.p, 0.0)
    task.run(make_controller("fixed"), sc)
    gt = be.ground_truth()
    assert np.allclose(gt.connector_pose.p, be.motion.read_tcp_pose().p)
