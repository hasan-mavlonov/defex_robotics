"""MuJoCo implementation of :class:`~defex.sim.backend.SimBackend`."""

from __future__ import annotations

from dataclasses import dataclass

import mujoco
import numpy as np

from defex.config import MM, ConnectorSpec, FixtureConfig, SimConfig
from defex.sim.backend import GroundTruth, PayloadModel, RawSensorData, SceneParams
from defex.sim.scene_builder import (
    FIXTURE_JOINTS,
    FT_SITE_Z,
    GRIPPER_GEOM_NAMES,
    PLUG_GEOM_NAMES,
    SOCKET_GEOM_PREFIX,
    WorkcellLayout,
    build_workcell_xml,
)
from defex.utils.transforms import Pose, euler_zyx_to_matrix, matrix_to_euler_zyx, norm3


@dataclass
class _CompiledModel:
    model: mujoco.MjModel
    layout: WorkcellLayout


class MuJoCoBackend:
    """Physics backend for the DAIE workcell.

    The fixture is commanded with Cartesian TCP setpoints. Because the three wrist
    hinges intersect at the TCP, inverse kinematics is exact and closed-form:
    slide positions equal the TCP displacement from home and the hinge angles are
    the Z-Y'-X'' Euler angles of the TCP orientation.
    """

    def __init__(self, sim: SimConfig | None = None, fixture: FixtureConfig | None = None) -> None:
        self.sim_cfg = sim or SimConfig()
        self.fixture_cfg = fixture or FixtureConfig()
        self._cache: dict[str, _CompiledModel] = {}
        self.model: mujoco.MjModel | None = None
        self.data: mujoco.MjData | None = None
        self.params: SceneParams | None = None
        self._layout: WorkcellLayout | None = None

    # ------------------------------------------------------------------ setup
    @staticmethod
    def _spec_key(spec: ConnectorSpec) -> str:
        return repr((spec.name, spec.plug, spec.socket))

    def load(self, params: SceneParams) -> None:
        key = self._spec_key(params.connector)
        if key not in self._cache:
            xml = build_workcell_xml(params.connector, self.fixture_cfg, self.sim_cfg, params.connector.friction)
            model = mujoco.MjModel.from_xml_string(xml)
            self._cache[key] = _CompiledModel(model, WorkcellLayout.from_spec(params.connector, self.fixture_cfg))
        compiled = self._cache[key]
        if self.model is not compiled.model:
            self.model = compiled.model
            self.data = mujoco.MjData(self.model)
            self._layout = compiled.layout
            self._index_model()
        self.params = params
        m = self.model
        # Friction coefficient of every connector/socket contact pair.
        m.pair_friction[:, 0] = params.friction
        m.pair_friction[:, 1] = params.friction
        # In-hand grasp offset of the connector relative to the fixture TCP.
        m.body_pos[self._connector_body] = params.grasp_offset.p
        m.body_quat[self._connector_body] = params.grasp_offset.quat()
        self.reset()

    def _index_model(self) -> None:
        m = self.model
        self._connector_body = m.body("connector").id
        self._tool_body = m.body("tool").id
        self._socket_mocap = m.body("socket").mocapid[0]
        self._marker_est_mocap = m.body("marker_estimate").mocapid[0]
        self._marker_sp_mocap = m.body("marker_setpoint").mocapid[0]
        self._tcp_site = m.site("tcp").id
        self._ft_site = m.site("ft_site").id
        self._qadr = np.array([m.joint(j).qposadr[0] for j in FIXTURE_JOINTS])
        self._vadr = np.array([m.joint(j).dofadr[0] for j in FIXTURE_JOINTS])
        self._jrange = np.array([m.joint(j).range for j in FIXTURE_JOINTS])
        self._ctrlrange = m.actuator_ctrlrange.copy()
        self._forcerange = m.actuator_forcerange.copy()
        s_f = m.sensor("ft_force")
        s_t = m.sensor("ft_torque")
        self._ft_force_adr = slice(s_f.adr[0], s_f.adr[0] + 3)
        self._ft_torque_adr = slice(s_t.adr[0], s_t.adr[0] + 3)
        held = {m.geom(n).id for n in (*PLUG_GEOM_NAMES, *GRIPPER_GEOM_NAMES)}
        socket = {i for i in range(m.ngeom) if m.geom(i).name.startswith(SOCKET_GEOM_PREFIX)}
        self._held_mask = np.zeros(m.ngeom, dtype=bool)
        self._held_mask[list(held)] = True
        self._socket_mask = np.zeros(m.ngeom, dtype=bool)
        self._socket_mask[list(socket)] = True
        self._elliptic = m.opt.cone == mujoco.mjtCone.mjCONE_ELLIPTIC
        self._payload = self._identify_payload()

    def _identify_payload(self) -> PayloadModel:
        """Mass properties below the F/T sensor with a nominal grasp (identified once)."""
        m = self.model
        d = mujoco.MjData(m)
        saved_pos = m.body_pos[self._connector_body].copy()
        saved_quat = m.body_quat[self._connector_body].copy()
        m.body_pos[self._connector_body] = 0.0
        m.body_quat[self._connector_body] = (1.0, 0.0, 0.0, 0.0)
        mujoco.mj_forward(m, d)
        mass = float(m.body_subtreemass[self._tool_body])
        com_w = d.subtree_com[self._tool_body].copy()
        p_s = d.site_xpos[self._ft_site].copy()
        R_s = d.site_xmat[self._ft_site].reshape(3, 3).copy()
        m.body_pos[self._connector_body] = saved_pos
        m.body_quat[self._connector_body] = saved_quat
        return PayloadModel(
            mass_kg=mass,
            com_in_sensor=R_s.T @ (com_w - p_s),
            sensor_in_tcp=Pose(np.array([0.0, 0.0, FT_SITE_Z]), np.eye(3)),
        )

    def reset(self) -> None:
        m, d = self.model, self.data
        mujoco.mj_resetData(m, d)
        sp = self.params.socket_pose
        d.mocap_pos[self._socket_mocap] = sp.p
        d.mocap_quat[self._socket_mocap] = sp.quat()
        d.qpos[self._qadr] = 0.0
        d.ctrl[:] = 0.0
        self._ctrl_clipped = False
        self._socket_pose_true = Pose(sp.p.copy(), sp.R.copy())
        mujoco.mj_forward(m, d)

    # ------------------------------------------------------------------ properties
    @property
    def time(self) -> float:
        return float(self.data.time)

    @property
    def home_tcp_pose(self) -> Pose:
        return Pose(self._layout.home_tcp.copy(), np.eye(3))

    @property
    def nominal_socket_pose(self) -> Pose:
        return Pose(self._layout.socket_mouth.copy(), np.eye(3))

    @property
    def payload(self) -> PayloadModel:
        return self._payload

    @property
    def timestep(self) -> float:
        return float(self.model.opt.timestep)

    # ------------------------------------------------------------------ kinematics
    def inverse_kinematics(self, pose: Pose) -> np.ndarray:
        yaw, pitch, roll = matrix_to_euler_zyx(pose.R)
        q = np.empty(6)
        q[:3] = pose.p - self._layout.home_tcp
        q[3:] = (yaw, pitch, roll)
        return q

    def forward_kinematics(self, q: np.ndarray) -> Pose:
        return Pose(self._layout.home_tcp + q[:3], euler_zyx_to_matrix(q[3], q[4], q[5]))

    # ------------------------------------------------------------------ control
    def set_tcp_setpoint(self, pose: Pose) -> None:
        q = self.inverse_kinematics(pose)
        q_clipped = np.clip(q, self._ctrlrange[:, 0], self._ctrlrange[:, 1])
        self._ctrl_clipped = bool(np.any(np.abs(q_clipped - q) > 1e-9))
        self.data.ctrl[:] = q_clipped

    def step(self, duration: float) -> None:
        n = max(1, int(round(duration / self.model.opt.timestep)))
        mujoco.mj_step(self.model, self.data, nstep=n)

    # ------------------------------------------------------------------ sensing
    def read_sensors(self) -> RawSensorData:
        d = self.data
        q = d.qpos[self._qadr].copy()
        return RawSensorData(
            t=float(d.time),
            joint_pos=q,
            tcp_pose=self.forward_kinematics(q),
            ft_force=d.sensordata[self._ft_force_adr].copy(),
            ft_torque=d.sensordata[self._ft_torque_adr].copy(),
        )

    def contact_wrench(self) -> tuple[np.ndarray, float, int]:
        """Net contact force on the held parts (world), deepest penetration, count."""
        m, d = self.model, self.data
        ncon = d.ncon
        if ncon == 0:
            return np.zeros(3), 0.0, 0
        con = d.contact
        g1 = con.geom1
        g2 = con.geom2
        relevant = (self._held_mask[g1] & self._socket_mask[g2]) | (self._held_mask[g2] & self._socket_mask[g1])
        if not np.any(relevant):
            return np.zeros(3), 0.0, 0
        idx = np.nonzero(relevant)[0]
        max_pen = float(np.max(np.maximum(-con.dist[idx], 0.0)))
        frames = con.frame[idx].reshape(-1, 3, 3)
        if self._elliptic:
            adr = con.efc_address[idx]
            valid = adr >= 0
            f = np.zeros((idx.size, 3))
            a = adr[valid]
            f[valid, 0] = d.efc_force[a]
            f[valid, 1] = d.efc_force[a + 1]
            f[valid, 2] = d.efc_force[a + 2]
        else:
            f = np.zeros((idx.size, 3))
            buf = np.zeros(6)
            for k, ci in enumerate(idx):
                mujoco.mj_contactForce(m, d, int(ci), buf)
                f[k] = buf[:3]
        world = np.einsum("ni,nij->nj", f, frames)  # force on geom2
        sign = np.where(self._held_mask[g2[idx]], 1.0, -1.0)
        net = (world * sign[:, None]).sum(axis=0)
        return net, max_pen, int(idx.size)

    def ground_truth(self) -> GroundTruth:
        m, d = self.model, self.data
        net, max_pen, n = self.contact_wrench()
        q = d.qpos[self._qadr]
        near_limit = bool(((q <= self._jrange[:, 0] + 1e-5) | (q >= self._jrange[:, 1] - 1e-5)).any())
        saturated = bool((np.abs(d.actuator_force) >= self._forcerange[:, 1] - 1e-6).any())
        return GroundTruth(
            t=float(d.time),
            socket_pose=self._socket_pose_true,
            connector_pose=Pose(d.site_xpos[self._tcp_site].copy(), d.site_xmat[self._tcp_site].reshape(3, 3).copy()),
            contact_force=net,
            contact_force_norm=norm3(net),
            max_penetration=max_pen,
            n_contacts=n,
            tcp_speed=norm3(d.qvel[self._vadr[:3]]),
            joint_limit_hit=near_limit or self._ctrl_clipped,
            actuator_saturated=saturated,
        )

    # ------------------------------------------------------------------ visualization helpers
    def set_marker_pose(self, which: str, pose: Pose) -> None:
        """Move a visual-only marker (``"estimate"`` or ``"setpoint"``)."""
        mocap = self._marker_est_mocap if which == "estimate" else self._marker_sp_mocap
        self.data.mocap_pos[mocap] = pose.p
        self.data.mocap_quat[mocap] = pose.quat()

    def joint_positions(self) -> np.ndarray:
        return self.data.qpos[self._qadr].copy()

    def set_joint_positions_kinematic(self, q: np.ndarray) -> None:
        """Kinematic state overwrite for *replay/visualization only* (never used in trials)."""
        self.data.qpos[self._qadr] = q
        self.data.qvel[:] = 0.0
        mujoco.mj_forward(self.model, self.data)


__all__ = ["MM", "MuJoCoBackend"]
