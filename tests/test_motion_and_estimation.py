import ast
from pathlib import Path

import numpy as np

from defex.config import DEG, MM, FixtureConfig, SensorNoiseConfig
from defex.control.base import Command
from defex.control.motion import CartesianMotionGenerator
from defex.perception.sensors import SensorSuite
from defex.perception.state_estimator import Observation, StateEstimator
from defex.utils.transforms import Pose, matrix_to_rotvec, rotvec_to_matrix

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER_SIDE = ("control", "recovery", "perception")
SIM_TRUTH_ATTRS = {"ground_truth", "true_payload", "joint_positions", "contact_wrench", "GroundTruth"}
FORBIDDEN_MODULES = ("mujoco", "defex.sim.mujoco_backend", "defex.sim.arm_backend", "defex.hardware")


def test_motion_generator_respects_limits(rng):
    fx = FixtureConfig()
    dt = 0.002
    gen = CartesianMotionGenerator(fx, dt)
    gen.reset(Pose.identity())
    v_max = fx.max_linear_speed_mm_s * MM
    a_max = fx.max_linear_accel_mm_s2 * MM
    w_max = fx.max_angular_speed_deg_s * DEG
    prev_p, prev_v = gen.pose.p.copy(), np.zeros(3)
    prev_R, prev_w = gen.pose.R.copy(), np.zeros(3)
    for _ in range(20):
        target = Pose(rng.uniform(-0.03, 0.03, 3), rotvec_to_matrix(rng.normal(size=3) * 0.2))
        cap = rng.uniform(0.002, 0.08)
        dist = np.linalg.norm(target.p - gen.pose.p)
        n_steps = int((dist / min(cap, v_max) + 2.0 * v_max / a_max + 1.5) / dt)
        for _ in range(n_steps):
            pose = gen.update(Command(target, cap, w_max))
            v = (pose.p - prev_p) / dt
            w = matrix_to_rotvec(pose.R @ prev_R.T) / dt
            assert np.linalg.norm(v) <= min(cap, v_max) * 1.0001 + 1e-9 or np.linalg.norm(v) <= np.linalg.norm(prev_v) + 1e-9
            assert np.linalg.norm(v - prev_v) <= a_max * dt * 1.0001 + 1e-9 or np.linalg.norm(pose.p - target.p) < 1e-9
            assert np.linalg.norm(w) <= w_max * 1.0001 + 1e-9
            prev_p, prev_v, prev_R, prev_w = pose.p.copy(), v, pose.R.copy(), w
        np.testing.assert_allclose(gen.pose.p, target.p, atol=1e-6)


def test_gravity_compensation_and_tare_in_free_space(backend):
    noise = SensorNoiseConfig()
    sensors = SensorSuite(noise, 7)
    est = StateEstimator(backend.true_payload, 0.002, noise.ft_filter_cutoff_hz)
    est.reset(backend.nominal_socket_pose, Pose.identity())
    home = backend.home_tcp_pose
    backend.set_tcp_setpoint(home)
    for i in range(150):
        if i == 50:
            est.begin_tare()
        backend.step(0.002)
        est.update(sensors.measure(backend.read_sensors()), home)
    est.end_tare()
    # Re-orient the tool by 8 degrees: compensation must track the gravity direction.
    tilted = Pose(home.p, rotvec_to_matrix(np.array([0.1, -0.08, 0.3])))
    backend.set_tcp_setpoint(tilted)
    for _ in range(400):
        backend.step(0.002)
        obs = est.update(sensors.measure(backend.read_sensors()), tilted)
    assert obs.force_norm < 0.08
    assert obs.torque_norm < 0.003


def test_observation_has_no_ground_truth_fields():
    names = set(Observation.__dataclass_fields__)
    forbidden = {"contact_force", "max_penetration", "true", "ground_truth", "gt"}
    assert not any(any(f in n for f in forbidden) for n in names)


def test_controller_code_cannot_reach_the_simulator():
    """Controllers, recovery and estimation must not import MuJoCo or ground truth."""
    paths = [p for sub in CONTROLLER_SIDE for p in (ROOT / "defex" / sub).rglob("*.py")]
    assert len(paths) >= 10
    # W9: the learned prior and controller G are controller-side code too.
    names = {p.relative_to(ROOT).as_posix() for p in paths}
    assert {"defex/recovery/learned_prior.py", "defex/control/adaptive_learned.py"} <= names
    for path in paths:
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                assert node.attr not in SIM_TRUTH_ATTRS, (path, node.attr)
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                mods = [node.module or ""]
                names = [a.name for a in node.names]
                assert "GroundTruth" not in names, path
            for mod in mods:
                assert not mod.startswith(FORBIDDEN_MODULES), (path, mod)
                assert "mujoco_backend" not in mod and "arm_backend" not in mod, (path, mod)


def test_learned_prior_is_numpy_and_json_only():
    """W9: the learned contact prior runs on observations and its model file, nothing else."""
    tree = ast.parse((ROOT / "defex" / "recovery" / "learned_prior.py").read_text())
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            mods.add(node.module or "")
    assert mods <= {"__future__", "json", "functools", "pathlib", "numpy", "defex.config"}, mods


def test_harness_identifies_the_payload_instead_of_reading_the_simulator():
    src = (ROOT / "defex" / "tasks" / "insertion.py").read_text()
    assert "true_payload" not in src
    assert "StateEstimator(payload" in src


def test_adaptive_controller_has_no_bare_tuning_constants():
    """W2: every tuned number in C's state machine lives in AdaptiveConfig."""
    tree = ast.parse((ROOT / "defex" / "control" / "adaptive_fsm.py").read_text())
    found = [
        (n.lineno, n.value)
        for fn in ast.walk(tree)
        if isinstance(fn, ast.FunctionDef)
        for n in ast.walk(fn)
        if isinstance(n, ast.Constant) and type(n.value) is float and n.value not in (0.0, 1.0, 0.5)
    ]
    assert not found, found
