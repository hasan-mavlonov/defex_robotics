"""W7: the unchanged harness runs on HardwareBackend (mocks in CI), and the Net F/T driver speaks RDT."""

import socket
import struct
import threading
from dataclasses import replace

import numpy as np

from defex.config import MM, ConnectorSpec, SensorNoiseConfig
from defex.control.registry import make_controller
from defex.hardware.backend import HardwareBackend, hardware_noise
from defex.hardware.drivers import RDT_RECORD, RDT_REQUEST, MockFTSensor, MockMotionStage, NetFTDriver
from defex.tasks.calibration import identification_error
from defex.tasks.conditions import conditions_by_name
from defex.tasks.insertion import InsertionTask
from defex.tasks.scenarios import sample_scenario
from defex.utils.transforms import Pose

SENSOR = Pose(np.array([0.0, 0.0, 0.037]), np.eye(3))
MOUTH = Pose(np.array([0.0, 0.0, 0.04]), np.eye(3))
HOME = Pose(MOUTH.p + np.array([0.0, 0.0, 0.06]), np.eye(3))


def _mock_task(floor_depth_mm: float) -> tuple[InsertionTask, HardwareBackend]:
    stage = MockMotionStage(HOME, floor_z=MOUTH.p[2] - floor_depth_mm * MM)
    ft = MockFTSensor(stage, payload_mass_kg=0.034, payload_com_in_sensor=np.array([0.0, 0.0, -0.009]),
                      sensor_in_tcp=SENSOR)
    be = HardwareBackend(stage, ft, SENSOR, MOUTH)
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


def test_netft_driver_decodes_rdt_records():
    srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    srv.bind(("127.0.0.1", 0))
    port = srv.getsockname()[1]
    counts = (1_000_000, 1_000_000)

    def serve():
        data, addr = srv.recvfrom(64)
        header, cmd, n = RDT_REQUEST.unpack(data)
        assert (header, cmd, n) == (0x1234, 2, 1)
        ft = [int(v * counts[0]) for v in (1.5, -2.0, 10.25)] + [int(v * counts[1]) for v in (0.01, -0.02, 0.003)]
        srv.sendto(RDT_RECORD.pack(7, 9, 0, *ft), addr)

    th = threading.Thread(target=serve, daemon=True)
    th.start()
    drv = NetFTDriver("127.0.0.1", counts_per_force=counts[0], counts_per_torque=counts[1], port=port, timeout_s=2.0)
    s = drv.read()
    th.join(2.0)
    srv.close()
    assert np.allclose(s.force, [1.5, -2.0, 10.25]) and np.allclose(s.torque, [0.01, -0.02, 0.003])
    assert drv.last_sequence == 7 and drv.last_status == 0
