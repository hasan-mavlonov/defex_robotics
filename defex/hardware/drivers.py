"""Hardware driver interfaces for hardware-in-the-loop runs (W7), with CI mocks.

Two devices are needed:

* a 6-axis wrist F/T sensor (:class:`FTSensorDriver`), and
* a motion system that takes Cartesian TCP setpoints at the control rate and
  reports the encoder-based TCP pose (:class:`MotionDriver`): a cobot over its
  real-time interface, or a desktop Cartesian gantry with a remote-centre wrist
  (the simulated fixture is the latter).

Real drivers here:

* :class:`NetFTDriver`: ATI Net F/T / Axia over UDP RDT (Raw Data Transfer):
  request ``>HHI`` (header 0x1234, command, sample count) to port 49152; each
  record is ``>IIIiiiiii`` (RDT sequence, F/T sequence, status, Fx..Tz in counts).
  Counts per force/torque unit come from the sensor's calibration page.
* :class:`URRTDEMotionDriver`: Universal Robots e-Series through the optional
  ``ur_rtde`` package (servoL at 500 Hz). Not exercised in CI.

Mocks (:class:`MockFTSensor`, :class:`MockMotionStage`) give CI a closed loop
without hardware: a quasi-static stiff stage pressing on a spring floor.
"""

from __future__ import annotations

import socket
import struct
import time
from dataclasses import dataclass, field
from typing import Protocol

import numpy as np

from defex.utils.transforms import Pose, cross3

GRAVITY = np.array([0.0, 0.0, -9.81])


@dataclass(slots=True)
class FTSample:
    t: float
    force: np.ndarray  # (3,) N, force exerted by the wrist on the tool, sensor frame
    torque: np.ndarray  # (3,) N m about the sensor origin, sensor frame


class FTSensorDriver(Protocol):
    def read(self) -> FTSample: ...


class MotionDriver(Protocol):
    @property
    def home_tcp_pose(self) -> Pose: ...

    @property
    def time(self) -> float: ...

    def set_tcp_setpoint(self, pose: Pose) -> None: ...

    def wait_period(self, duration: float) -> None:
        """Block until the next control period (real time on hardware)."""
        ...

    def read_tcp_pose(self) -> Pose:
        """Encoder-based TCP pose (forward kinematics)."""
        ...

    def joint_positions(self) -> np.ndarray: ...


# ----------------------------------------------------------------------------- ATI Net F/T
RDT_PORT = 49152
RDT_HEADER = 0x1234
RDT_CMD_STOP = 0x0000
RDT_CMD_START_REALTIME = 0x0002
RDT_REQUEST = struct.Struct(">HHI")
RDT_RECORD = struct.Struct(">IIIiiiiii")


@dataclass
class NetFTDriver:
    """ATI Net F/T over UDP RDT. Polls one record per read (command 2, count 1)."""

    host: str
    counts_per_force: float  # from the sensor's calibration (e.g. 1,000,000 counts per N)
    counts_per_torque: float  # counts per N m
    port: int = RDT_PORT
    timeout_s: float = 0.05
    _sock: socket.socket | None = field(default=None, init=False, repr=False)
    last_status: int = field(default=0, init=False)
    last_sequence: int = field(default=0, init=False)

    def _socket(self) -> socket.socket:
        if self._sock is None:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sock.settimeout(self.timeout_s)
        return self._sock

    def read(self) -> FTSample:
        s = self._socket()
        s.sendto(RDT_REQUEST.pack(RDT_HEADER, RDT_CMD_START_REALTIME, 1), (self.host, self.port))
        data, _ = s.recvfrom(RDT_RECORD.size)
        rdt_seq, ft_seq, status, *ft = RDT_RECORD.unpack(data[: RDT_RECORD.size])
        self.last_status, self.last_sequence = status, rdt_seq
        f = np.array(ft[:3], dtype=float) / self.counts_per_force
        t = np.array(ft[3:], dtype=float) / self.counts_per_torque
        return FTSample(time.monotonic(), f, t)

    def close(self) -> None:
        if self._sock is not None:
            self._sock.sendto(RDT_REQUEST.pack(RDT_HEADER, RDT_CMD_STOP, 0), (self.host, self.port))
            self._sock.close()
            self._sock = None


# ----------------------------------------------------------------------------- Universal Robots
class URRTDEMotionDriver:
    """UR e-Series via ``ur_rtde`` (pip install ur_rtde). servoL at 500 Hz.

    Untested in CI. The TCP must be configured on the robot to the connector tip.
    """

    def __init__(self, host: str, home: Pose, lookahead_s: float = 0.03, gain: float = 300.0) -> None:
        import rtde_control  # type: ignore[import-not-found]
        import rtde_receive  # type: ignore[import-not-found]

        self._ctrl = rtde_control.RTDEControlInterface(host)
        self._recv = rtde_receive.RTDEReceiveInterface(host)
        self._home = home
        self._lookahead = lookahead_s
        self._gain = gain
        self._t0 = time.monotonic()
        self._next = self._t0

    @property
    def home_tcp_pose(self) -> Pose:
        return self._home

    @property
    def time(self) -> float:
        return time.monotonic() - self._t0

    def set_tcp_setpoint(self, pose: Pose) -> None:
        from defex.utils.transforms import matrix_to_rotvec

        target = [*pose.p.tolist(), *matrix_to_rotvec(pose.R).tolist()]
        self._ctrl.servoL(target, 0.0, 0.0, 0.002, self._lookahead, self._gain)

    def wait_period(self, duration: float) -> None:
        self._next += duration
        delay = self._next - time.monotonic()
        if delay > 0:
            time.sleep(delay)

    def read_tcp_pose(self) -> Pose:
        from defex.utils.transforms import rotvec_to_matrix

        x = self._recv.getActualTCPPose()
        return Pose(np.array(x[:3]), rotvec_to_matrix(np.array(x[3:])))

    def joint_positions(self) -> np.ndarray:
        return np.array(self._recv.getActualQ())


# ----------------------------------------------------------------------------- mocks for CI
@dataclass
class MockMotionStage:
    """Quasi-static stiff stage with a horizontal spring floor (no real time)."""

    home: Pose
    floor_z: float  # world height of the contact surface
    servo_stiffness_n_per_m: float = 1e4
    floor_stiffness_n_per_m: float = 2e5
    t: float = 0.0
    setpoint: Pose | None = None
    pose: Pose | None = None

    def __post_init__(self) -> None:
        self.setpoint = self.home
        self.pose = self.home

    @property
    def home_tcp_pose(self) -> Pose:
        return self.home

    @property
    def time(self) -> float:
        return self.t

    def set_tcp_setpoint(self, pose: Pose) -> None:
        self.setpoint = pose

    def contact_force_world(self) -> np.ndarray:
        pen = self.floor_z - self.pose.p[2]
        return np.array([0.0, 0.0, self.floor_stiffness_n_per_m * pen]) if pen > 0 else np.zeros(3)

    def wait_period(self, duration: float) -> None:
        self.t += duration
        p = self.setpoint.p.copy()
        ks, kf = self.servo_stiffness_n_per_m, self.floor_stiffness_n_per_m
        if p[2] < self.floor_z:
            p[2] = (ks * p[2] + kf * self.floor_z) / (ks + kf)
        self.pose = Pose(p, self.setpoint.R.copy())

    def read_tcp_pose(self) -> Pose:
        return self.pose

    def joint_positions(self) -> np.ndarray:
        return np.concatenate([self.pose.p - self.home.p, np.zeros(3)])


@dataclass
class MockFTSensor:
    """Reads the mock stage's contact force at the TCP, plus the payload's weight."""

    stage: MockMotionStage
    payload_mass_kg: float
    payload_com_in_sensor: np.ndarray
    sensor_in_tcp: Pose

    def read(self) -> FTSample:
        sensor = self.stage.pose @ self.sensor_in_tcp
        f_ext = self.stage.contact_force_world()
        r = self.stage.pose.p - sensor.p  # contact acts at the TCP (plug tip)
        g = self.payload_mass_kg * GRAVITY
        f_wrist = -(f_ext + g)
        t_wrist = -(cross3(r, f_ext) + cross3(sensor.R @ self.payload_com_in_sensor, g))
        return FTSample(self.stage.t, sensor.R.T @ f_wrist, sensor.R.T @ t_wrist)
