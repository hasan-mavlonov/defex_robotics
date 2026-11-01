"""W5: a UR5e-class serial arm behind the same SimBackend protocol.

The workcell (socket, contact pairs, tool, F/T sensor, materials) is the gantry
workcell from :mod:`defex.sim.scene_builder`, unchanged; only the fixture is
replaced by a Universal Robots UR5e from MuJoCo Menagerie (BSD-3-Clause, ROS
Industrial Consortium; fetched at a pinned commit by ``scripts/fetch_menagerie.py``,
not stored in git).

Arm modelling choices:

* Joint servos are Menagerie's: PD position actuators (2000 N m/rad shoulder and
  elbow, 500 N m/rad wrist, with damping). With an ideal motor this is exactly a
  series-elastic spring between the commanded and the actual joint angle, i.e. the
  joint flexibility the brief asks for. Joint torque limits 150 / 28 N m.
* Gravity is compensated in the joints (``gravcomp``), as the UR controller does;
  the servos only resist contact loads.
* Cartesian setpoints arrive at the 500 Hz control rate (UR RTDE servoL class) and
  are turned into joint targets by damped least-squares inverse kinematics, then
  delayed by ``latency_s`` (default 6 ms, within the brief's 4-8 ms).
* Encoders read the actual joint angles; the TCP pose reported to the estimator is
  their forward kinematics, so arm deflection under load is visible to C exactly
  as on the real robot (it is not visible on the gantry, whose axes are stiff).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path

import mujoco
import numpy as np

from defex.config import ConnectorSpec, FixtureConfig, SimConfig
from defex.sim.backend import FixtureDynamics, RawSensorData, SceneParams
from defex.sim.mujoco_backend import MuJoCoBackend, _CompiledModel
from defex.sim.scene_builder import WorkcellLayout, build_workcell_xml
from defex.utils.transforms import Pose, matrix_to_rotvec

MENAGERIE_COMMIT = "b0655057a9df2abe39ea7fc989914ba6f248301c"
MENAGERIE_DIR = Path.home() / ".cache" / "defex" / "mujoco_menagerie" / "universal_robots_ur5e"
UR_JOINTS = ("shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint")
_TMP = "toolcopy_"
TOOL_LENGTH = 0.045  # m, plug tip to flange along the tool axis (F/T sensor sits at 0.037)


@dataclass(frozen=True)
class ArmConfig:
    base_pos: tuple[float, float, float] = (-0.40, 0.0, 0.0)  # arm base in the world, socket at the origin
    latency_s: float = 0.006
    ik_damping: float = 1e-4
    ik_iterations: int = 8
    home_q: tuple[float, ...] = (0.0, -1.2, 1.6, -1.97, -1.5708, 0.0)  # IK seed: elbow up, tool down


def menagerie_available() -> bool:
    return (MENAGERIE_DIR / "ur5e.xml").exists()


def build_arm_spec(spec: ConnectorSpec, fixture: FixtureConfig, sim: SimConfig, compliance=None,
                   arm: ArmConfig = ArmConfig()) -> mujoco.MjSpec:
    xml = build_workcell_xml(spec, fixture, sim, spec.friction, compliance)
    cell = mujoco.MjSpec.from_string(xml)
    tool_src = mujoco.MjSpec.from_string(xml)
    ur = mujoco.MjSpec.from_file(str(MENAGERIE_DIR / "ur5e.xml"))
    # Drop the gantry and its actuators; keep everything else (socket, pairs, sensors, assets).
    for act in list(cell.actuators):
        cell.delete(act)
    cell.delete(cell.body("fixture_x"))
    for b in ur.bodies:
        b.gravcomp = 1.0
    for g in ur.geoms:
        g.contype = 0
        g.conaffinity = 0
    base_frame = cell.worldbody.add_frame(pos=list(arm.base_pos))
    base_frame.attach_body(ur.body("base"), "ur_", "")
    site = cell.site("ur_attachment_site")
    # Tool frame: origin at the plug tip, +z back towards the flange (site z points away from it).
    flange = cell.body("ur_wrist_3_link")
    mount = flange.add_frame(pos=list(site.pos), quat=list(site.quat))
    tip = mount.add_frame(pos=[0.0, 0.0, TOOL_LENGTH], quat=[0.0, 1.0, 0.0, 0.0])  # flip about x
    # Attaching copies the source's assets too, so attach under a prefix, then give the
    # tool's own bodies, geoms and sites their original names back (the gantry's copies
    # were deleted with the fixture). Pairs and sensors refer to those names.
    tip.attach_body(tool_src.body("tool"), _TMP, "")
    for group in (cell.pairs, cell.sensors, cell.actuators):
        names = {el.name for el in group}
        for el in list(group):
            if el.name.startswith(_TMP):
                base = el.name[len(_TMP):]
                if base in names:
                    cell.delete(el)  # the original survived the fixture's deletion
                else:
                    el.name = base  # the original went with the fixture: keep the copy
                    for attr in ("geomname1", "geomname2", "objname", "refname", "target"):
                        ref = getattr(el, attr, None)
                        if isinstance(ref, str) and ref.startswith(_TMP):
                            setattr(el, attr, ref[len(_TMP):])
    for group in (cell.bodies, cell.geoms, cell.sites):
        for el in group:
            if el.name.startswith(_TMP):
                el.name = el.name[len(_TMP):]
    return cell


class MuJoCoArmBackend(MuJoCoBackend):
    """UR5e workcell. Same protocol, same contact model, same sensors as the gantry."""

    joint_names = tuple("ur_" + j for j in UR_JOINTS)

    def __init__(self, sim: SimConfig | None = None, fixture: FixtureConfig | None = None,
                 arm: ArmConfig | None = None) -> None:
        if not menagerie_available():
            raise FileNotFoundError(f"UR5e model not found in {MENAGERIE_DIR}; run python scripts/fetch_menagerie.py")
        super().__init__(sim, fixture)
        self.arm = arm or ArmConfig()

    def load(self, params: SceneParams) -> None:
        key = "arm:" + self._spec_key(params.connector, params.compliance)
        if key not in self._cache:
            spec = build_arm_spec(params.connector, self.fixture_cfg, self.sim_cfg, params.compliance, self.arm)
            self._cache[key] = _CompiledModel(spec.compile(), WorkcellLayout.from_spec(params.connector, self.fixture_cfg))
        compiled = self._cache[key]
        if self.model is not compiled.model:
            self.model = compiled.model
            self.data = mujoco.MjData(self.model)
            self._kin = mujoco.MjData(self.model)
            self._layout = compiled.layout
            self._index_model()
        self.params = params
        m = self.model
        m.pair_friction[:, 0] = params.friction
        m.pair_friction[:, 1] = params.friction
        m.body_pos[self._connector_body] = params.grasp_offset.p
        m.body_quat[self._connector_body] = params.grasp_offset.quat()
        self._setup_mating(params)
        self.reset()

    def _index_model(self) -> None:
        m = self.model
        self._act = np.array([m.actuator("ur_" + a).id for a in
                              ("shoulder_pan", "shoulder_lift", "elbow", "wrist_1", "wrist_2", "wrist_3")])
        self._home_q = None
        super()._index_model()  # sensors, geoms, markers, payload, dynamics; joints via joint_names
        self._tcp_site_id = m.site("tcp").id
        self._home_q = self._solve_home()
        self._dynamics = self._fixture_dynamics()

    # ------------------------------------------------------------------ kinematics
    def _fixture_dynamics(self) -> FixtureDynamics:
        if self._home_q is None:  # called by the parent before the home pose exists
            return None
        m, d = self.model, self._kin
        self._fk_tool(self._home_q)
        jp = np.zeros((3, m.nv))
        jr = np.zeros((3, m.nv))
        mujoco.mj_jacBody(m, d, jp, jr, self._tool_body)
        J = np.vstack([jp[:, self._vadr], jr[:, self._vadr]])
        kq = np.array([m.actuator_gainprm[a, 0] for a in self._act])
        C = J @ np.diag(1.0 / kq) @ J.T  # Cartesian compliance of the joint springs
        saved = self.data.qpos[self._qadr].copy()
        self.data.qpos[self._qadr] = self._home_q
        meff = self._tool_effective_mass_z()
        self.data.qpos[self._qadr] = saved
        return FixtureDynamics(
            translational_stiffness_n_per_mm=float(1.0 / C[:3, :3].diagonal().max()) * 1e-3,
            yaw_stiffness_nm_per_rad=float(1.0 / C[5, 5]),
            effective_mass_kg=meff,
            command_latency_s=self.arm.latency_s,
        )

    def _fk_tool(self, q: np.ndarray) -> Pose:
        d = self._kin
        d.qpos[self._qadr] = q
        mujoco.mj_kinematics(self.model, d)
        mujoco.mj_comPos(self.model, d)  # mj_jacBody needs it
        return Pose(d.xpos[self._tool_body].copy(), d.xmat[self._tool_body].reshape(3, 3).copy())

    def _ik(self, target: Pose, q0: np.ndarray) -> np.ndarray:
        m, d = self.model, self._kin
        q = q0.copy()
        jacp = np.zeros((3, m.nv))
        jacr = np.zeros((3, m.nv))
        for _ in range(self.arm.ik_iterations):
            cur = self._fk_tool(q)
            err = np.concatenate([target.p - cur.p, matrix_to_rotvec(target.R @ cur.R.T)])
            if np.linalg.norm(err[:3]) < 1e-8 and np.linalg.norm(err[3:]) < 1e-7:
                break
            mujoco.mj_jacBody(m, d, jacp, jacr, self._tool_body)
            J = np.vstack([jacp[:, self._vadr], jacr[:, self._vadr]])
            q = q + J.T @ np.linalg.solve(J @ J.T + self.arm.ik_damping * np.eye(6), err)
        return q

    def _solve_home(self) -> np.ndarray:
        """Home joint angles: IK from a grid of seeds, keeping solutions inside every joint
        limit and choosing the one with the most margin to its limits (a single seed can
        converge to a branch with the elbow past its +/-pi range)."""
        import itertools

        target = Pose(self._layout.home_tcp.copy(), np.eye(3))
        lo, hi = self._jrange[:, 0], self._jrange[:, 1]
        best, best_margin = None, -np.inf
        for pan, lift, elbow, w1 in itertools.product((0.0, np.pi / 2, np.pi, -np.pi / 2), (-1.2, -2.0),
                                                      (1.6, -1.6), (-1.97, -1.2)):
            q = np.array([pan, lift, elbow, w1, -np.pi / 2, 0.0])
            for _ in range(40):
                q = self._ik(target, q)
            q = (q + np.pi) % (2.0 * np.pi) - np.pi  # same pose, angles in [-pi, pi)
            if np.linalg.norm(self._fk_tool(q).p - target.p) > 1e-6:
                continue
            margin = float(np.min(np.minimum(q - lo, hi - q)))
            if margin > best_margin:
                best, best_margin = q, margin
        if best is None or best_margin <= 0.0:
            raise RuntimeError("UR5e home pose not reachable inside the joint limits")
        return best

    def inverse_kinematics(self, pose: Pose) -> np.ndarray:
        return self._ik(pose, self._q_cmd if hasattr(self, "_q_cmd") else self._home_q)

    def forward_kinematics(self, q: np.ndarray) -> Pose:
        return self._fk_tool(q)

    # ------------------------------------------------------------------ protocol
    def reset(self) -> None:
        m, d = self.model, self.data
        mujoco.mj_resetData(m, d)
        sp = self.params.socket_pose
        d.mocap_pos[self._socket_mocap] = sp.p
        d.mocap_quat[self._socket_mocap] = sp.quat()
        d.qpos[self._qadr] = self._home_q
        self._q_cmd = self._home_q.copy()
        d.ctrl[self._act] = self._home_q
        n = max(1, int(round(self.arm.latency_s / self.sim_cfg.control_period_s)))
        # Append-then-read-oldest: a buffer of n + 1 delays each command by exactly n periods.
        self._delay: deque[np.ndarray] = deque([self._home_q.copy()] * (n + 1), maxlen=n + 1)
        self._ctrl_clipped = False
        self._socket_pose_true = Pose(sp.p.copy(), sp.R.copy())
        if getattr(self, "_mating", None) is not None:
            self._mating.reset()
        mujoco.mj_forward(m, d)

    @property
    def home_tcp_pose(self) -> Pose:
        return self._fk_tool(self._home_q)

    def set_tcp_setpoint(self, pose: Pose) -> None:
        self._q_cmd = self._ik(pose, self._q_cmd)
        q = np.clip(self._q_cmd, self._jrange[:, 0], self._jrange[:, 1])
        self._ctrl_clipped = bool(np.any(np.abs(q - self._q_cmd) > 1e-9))
        self._delay.append(q)
        self.data.ctrl[self._act] = self._delay[0]

    def read_sensors(self) -> RawSensorData:
        d = self.data
        q = d.qpos[self._qadr].copy()
        return RawSensorData(
            t=float(d.time),
            joint_pos=q,
            tcp_pose=self._fk_tool(q),
            ft_force=d.sensordata[self._ft_force_adr].copy(),
            ft_torque=d.sensordata[self._ft_torque_adr].copy(),
        )

    def ground_truth(self):
        gt = super().ground_truth()
        v = np.zeros(6)
        mujoco.mj_objectVelocity(self.model, self.data, mujoco.mjtObj.mjOBJ_SITE, self._tcp_site_id, v, 0)
        gt.tcp_speed = float(np.linalg.norm(v[3:]))  # linear part (world frame)
        return gt

    def set_joint_positions_kinematic(self, q: np.ndarray) -> None:
        self._q_cmd = np.asarray(q, dtype=float).copy()
        self._delay = deque([self._q_cmd.copy()] * self._delay.maxlen, maxlen=self._delay.maxlen)
        self.data.ctrl[self._act] = self._q_cmd
        self.data.qpos[self._qadr] = q
        self.data.qvel[:] = 0.0
        mujoco.mj_forward(self.model, self.data)
