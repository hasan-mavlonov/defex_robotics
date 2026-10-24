"""Connector-insertion task harness.

The harness wires the pieces together for one trial and is the only place where
ground truth and observations coexist; it keeps them strictly apart:

    backend --raw--> SensorSuite --readings--> StateEstimator --Observation--> controller
       ^                                                                          |
       +----------- IK <-- CartesianMotionGenerator (bounded v, a) <-- Command ---+

Ground truth (true poses, contact forces, penetration) is only used by the safety
bookkeeping and the final scoring. The online protective stop uses the *measured*
F/T signal, as a real cell would.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from defex.config import DEG, MM, FixtureConfig, SafetyConfig, SimConfig, SuccessCriteria
from defex.control.base import Command, ControllerContext, InsertionController
from defex.control.motion import CartesianMotionGenerator
from defex.logging.metrics import TrialResult
from defex.perception.sensors import SensorSuite
from defex.perception.state_estimator import Observation, StateEstimator
from defex.sim.backend import GroundTruth, SceneParams, SimBackend
from defex.sim.mujoco_backend import MuJoCoBackend
from defex.tasks.scenarios import Scenario
from defex.utils.transforms import Pose, axis_angle_between, twist_about_axis

StepCallback = Callable[["StepInfo"], None]


@dataclass
class StepInfo:
    """Snapshot handed to visualizers after every control tick."""

    t: float
    obs: Observation
    gt: GroundTruth
    controller: InsertionController
    setpoint: Pose
    backend: SimBackend
    scenario: Scenario
    protective_stop: bool = False


@dataclass
class TrajectoryRecorder:
    """Decimated time series of one trial (for replay and plots)."""

    every_n: int = 10  # 500 Hz control -> 50 Hz log
    t: list[float] = field(default_factory=list)
    joints: list[np.ndarray] = field(default_factory=list)
    setpoint: list[np.ndarray] = field(default_factory=list)
    connector_true: list[np.ndarray] = field(default_factory=list)
    force_meas: list[np.ndarray] = field(default_factory=list)
    torque_meas: list[np.ndarray] = field(default_factory=list)
    contact_force: list[float] = field(default_factory=list)
    depth_est: list[float] = field(default_factory=list)
    depth_true: list[float] = field(default_factory=list)
    state: list[str] = field(default_factory=list)
    _k: int = 0

    def record(self, info: StepInfo) -> None:
        self._k += 1
        if self._k % self.every_n:
            return
        rel = info.gt.socket_pose.inv() @ info.gt.connector_pose
        self.t.append(info.t)
        self.joints.append(info.backend.joint_positions())
        self.setpoint.append(info.setpoint.as_array())
        self.connector_true.append(info.gt.connector_pose.as_array())
        self.force_meas.append(info.obs.force.copy())
        self.torque_meas.append(info.obs.torque.copy())
        self.contact_force.append(info.gt.contact_force_norm)
        self.depth_est.append(info.obs.depth)
        self.depth_true.append(float(-rel.p[2]))
        self.state.append(info.controller.state)

    def to_arrays(self) -> dict[str, np.ndarray]:
        return {
            "t": np.asarray(self.t),
            "joints": np.asarray(self.joints),
            "setpoint": np.asarray(self.setpoint),
            "connector_true": np.asarray(self.connector_true),
            "force_meas": np.asarray(self.force_meas),
            "torque_meas": np.asarray(self.torque_meas),
            "contact_force": np.asarray(self.contact_force),
            "depth_est": np.asarray(self.depth_est),
            "depth_true": np.asarray(self.depth_true),
            "state": np.asarray(self.state),
        }


def evaluate_final_state(gt: GroundTruth, scenario: Scenario, crit: SuccessCriteria) -> dict:
    """Score the final connector pose against the true socket frame."""
    spec = scenario.connector
    rel = gt.socket_pose.inv() @ gt.connector_pose
    depth = float(-rel.p[2])
    lateral = float(np.linalg.norm(rel.p[:2]))
    tilt = axis_angle_between(rel.R[:, 2], np.array([0.0, 0.0, 1.0]))
    yaw = twist_about_axis(rel.R)
    # The cavity is rectangular: a plug resting in a corner sits at (c, c), so the
    # lateral bound is checked per axis of the socket frame, not as a radius.
    lat_limit = (spec.socket.clearance_mm + crit.lateral_margin_mm) * MM
    checks = {
        "depth": depth >= spec.depth - crit.depth_tolerance_mm * MM,
        "lateral": bool(abs(rel.p[0]) <= lat_limit and abs(rel.p[1]) <= lat_limit),
        "tilt": tilt <= crit.max_tilt_deg * DEG,
        "yaw": abs(yaw) <= crit.max_yaw_deg * DEG,
        "settled": gt.tcp_speed <= crit.max_final_speed_mm_s * MM,
    }
    return {
        "depth_mm": depth / MM,
        "lateral_mm": lateral / MM,
        "tilt_deg": tilt / DEG,
        "yaw_deg": yaw / DEG,
        "seated": bool(all(checks.values())),
        "failed_checks": [k for k, ok in checks.items() if not ok],
    }


class InsertionTask:
    def __init__(
        self,
        sim: SimConfig | None = None,
        fixture: FixtureConfig | None = None,
        safety: SafetyConfig | None = None,
        success: SuccessCriteria | None = None,
        backend: SimBackend | None = None,
    ) -> None:
        self.sim = sim or SimConfig()
        self.fixture = fixture or FixtureConfig()
        self.safety = safety or SafetyConfig()
        self.criteria = success or SuccessCriteria()
        self.backend = backend or MuJoCoBackend(self.sim, self.fixture)

    def run(
        self,
        controller: InsertionController,
        scenario: Scenario,
        recorder: TrajectoryRecorder | None = None,
        on_step: StepCallback | None = None,
        tare_time_s: float = 0.2,
    ) -> TrialResult:
        wall0 = time.perf_counter()
        dt = self.sim.control_period_s
        be = self.backend
        be.load(SceneParams(scenario.connector, scenario.friction, scenario.socket_pose, scenario.grasp_offset))

        sensors = SensorSuite(scenario.noise, scenario.seed)
        vision = sensors.vision_measurement(scenario.socket_pose)
        grasp_est = sensors.grasp_measurement(scenario.grasp_offset)
        estimator = StateEstimator(be.payload, dt, scenario.noise.ft_filter_cutoff_hz)
        estimator.reset(vision, grasp_est)
        motion = CartesianMotionGenerator(self.fixture, dt)
        home = be.home_tcp_pose
        motion.reset(home)
        be.set_tcp_setpoint(home)
        be.set_marker_pose("estimate", vision)
        be.set_marker_pose("setpoint", home)

        # Settle the servos at home and tare the F/T sensor in free space.
        n_tare = int(round(tare_time_s / dt))
        obs: Observation | None = None
        for k in range(n_tare):
            if k == n_tare // 2:
                estimator.begin_tare()
            be.step(dt)
            obs = estimator.update(sensors.measure(be.read_sensors()), motion.pose)
        estimator.end_tare()

        ctx = ControllerContext(
            connector=scenario.connector,
            nominal_socket_pose=be.nominal_socket_pose,
            home_pose=home,
            control_period_s=dt,
            fixture=self.fixture,
            vision_accuracy=scenario.noise,
        )
        controller.reset(ctx)

        t0 = be.time
        peak_contact = 0.0
        peak_sustained = 0.0
        window: deque[float] = deque(maxlen=max(1, int(round(0.010 / dt))))
        peak_measured = 0.0
        peak_torque = 0.0
        max_pen = 0.0
        joint_limit = False
        protective_stop = False
        timeout = False
        setpoint = motion.pose
        gt = be.ground_truth()

        visualize = on_step is not None

        def tick(command_setpoint: Pose | None) -> None:
            nonlocal setpoint, gt, peak_contact, peak_sustained, max_pen, joint_limit
            if command_setpoint is not None:
                setpoint = command_setpoint
                be.set_tcp_setpoint(setpoint)
                if visualize:
                    be.set_marker_pose("setpoint", setpoint)
            be.step(dt)
            gt = be.ground_truth()
            peak_contact = max(peak_contact, gt.contact_force_norm)
            window.append(gt.contact_force_norm)
            peak_sustained = max(peak_sustained, sum(window) / len(window))
            max_pen = max(max_pen, gt.max_penetration)
            joint_limit = joint_limit or gt.joint_limit_hit

        while True:
            obs = estimator.update(sensors.measure(be.read_sensors()), motion.pose)
            f_meas = obs.force_norm
            peak_measured = max(peak_measured, f_meas)
            peak_torque = max(peak_torque, obs.torque_norm)
            if f_meas > self.safety.protective_stop_force_n or obs.torque_norm > self.safety.protective_stop_torque_nm:
                protective_stop = True
                controller.log(obs.t, "protective_stop", f"|F|={f_meas:.1f} N |T|={obs.torque_norm:.2f} N m")
                break
            cmd: Command = controller.step(obs)
            sp = motion.update(cmd)
            tick(sp)
            if on_step or recorder:
                info = StepInfo(obs.t, obs, gt, controller, setpoint, be, scenario)
                if recorder:
                    recorder.record(info)
                if on_step:
                    on_step(info)
            if controller.done:
                break
            if be.time - t0 > self.sim.max_trial_time_s:
                timeout = True
                controller.log(obs.t, "timeout")
                break

        end_t = be.time
        # Hold the final setpoint (or the frozen setpoint after a protective stop) and let it settle.
        n_settle = int(round(self.sim.settle_time_s / dt))
        for _ in range(n_settle):
            tick(None)
            if on_step or recorder:
                obs = estimator.update(sensors.measure(be.read_sensors()), motion.pose)
                info = StepInfo(obs.t, obs, gt, controller, setpoint, be, scenario, protective_stop)
                if recorder:
                    recorder.record(info)
                if on_step:
                    on_step(info)

        final = evaluate_final_state(gt, scenario, self.criteria)
        penetration_violation = max_pen > self.safety.max_penetration_mm * MM
        # Damage is judged on the 10 ms average: single-sample transients from MuJoCo's
        # velocity-proportional contact damping (impacts, stick-slip) are reported in
        # peak_contact_force_n but are not a meaningful damage criterion on their own.
        damage = peak_sustained > self.safety.damage_contact_force_n
        declared = controller.declared_success
        success = bool(
            final["seated"]
            and not protective_stop
            and not penetration_violation
            and not damage
            and not joint_limit
            and not timeout
            and declared is not False
        )
        reason = "none"
        if not success:
            if protective_stop:
                reason = "protective_stop"
            elif penetration_violation:
                reason = "penetration_violation"
            elif damage:
                reason = "excessive_contact_force"
            elif joint_limit:
                reason = "workspace_limit"
            elif timeout:
                reason = "timeout"
            elif declared is False and final["seated"]:
                reason = "false_reject"
            elif declared is True and not final["seated"]:
                reason = "false_accept"
            elif declared is False:
                reason = f"aborted:{controller.failure_reason}"
            elif final["depth_mm"] < 1.5:
                reason = "blocked_at_entry"
            elif final["depth_mm"] < scenario.connector.socket.depth_mm - self.criteria.depth_tolerance_mm:
                reason = "jammed_partial_insertion"
            else:
                reason = "seated_out_of_tolerance:" + "+".join(final["failed_checks"])

        cycle_end = controller.done_time if controller.done_time is not None else end_t
        return TrialResult(
            controller=controller.name,
            condition=scenario.condition,
            group=scenario.group,
            trial_index=scenario.trial_index,
            seed=scenario.seed,
            success=success,
            failure_reason=reason,
            gt_seated=bool(final["seated"]),
            declared_success=declared,
            cycle_time_s=float(cycle_end - t0),
            peak_contact_force_n=float(peak_contact),
            peak_contact_force_10ms_n=float(peak_sustained),
            peak_measured_force_n=float(peak_measured),
            peak_measured_torque_nm=float(peak_torque),
            retries=int(controller.retries),
            recovered=bool(success and controller.retries > 0),
            final_depth_mm=float(final["depth_mm"]),
            final_lateral_mm=float(final["lateral_mm"]),
            final_tilt_deg=float(final["tilt_deg"]),
            final_yaw_deg=float(final["yaw_deg"]),
            max_penetration_mm=float(max_pen / MM),
            protective_stop=protective_stop,
            timeout=timeout,
            friction=scenario.friction,
            vision_sigma_mm=scenario.noise.vision_xy_sigma_mm,
            disturbance=dict(scenario.disturbance),
            events=[(e.t, e.kind, e.detail) for e in controller.events],
            sim_time_s=float(be.time),
            wall_time_s=float(time.perf_counter() - wall0),
        )
