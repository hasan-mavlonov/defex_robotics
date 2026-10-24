"""Procedural MJCF generation for the DAIE insertion workcell.

The workcell is generated from :class:`~defex.config.ConnectorSpec` and
:class:`~defex.config.FixtureConfig` so that connector dimensions, clearances and
servo parameters are single-sourced from configuration.

Socket construction
-------------------
The receptacle cavity is a genuine opening assembled from convex collision boxes
(no solid placeholder, no collision bypass):

* one floor box at the bottom of the cavity,
* per side, an *outer block* (full height) and an *inner strip* (below the lead-in),
* per side, a 45 degree *chamfer box* whose face lies exactly on the lead-in plane.

Adjacent chamfer boxes overlap at the corners; because the solid is the union of
the boxes, the corner surface is ``max`` of the two chamfer planes, which is the
exact geometry of a chamfered rectangular opening. All boxes stay inside the wall
profile (verified in ``tests/test_scene_geometry.py``).

Frames
------
* World: z up, table top at z = 0.
* Socket frame (mocap body ``socket``): origin at the center of the cavity mouth,
  +z pointing out of the socket. A seated plug tip sits at z = -depth.
* Connector frame (body ``connector``): origin at the plug tip center (TCP), +z
  along the plug towards the gripper.
* Fixture TCP: the six fixture joints are arranged so that joint zero places the
  TCP at ``home``; the three wrist hinges intersect at the TCP.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from defex.config import MM, REPO_ROOT, ConnectorSpec, FixtureConfig, SimConfig

# Nominal layout (metres)
JIG_BOTTOM_Z = 0.008
JIG_THICKNESS = 0.010

SOCKET_GEOM_PREFIX = "socket_"
PLUG_GEOM_NAMES = ("plug",)
GRIPPER_GEOM_NAMES = ("palm", "finger_pos", "finger_neg")
FIXTURE_JOINTS = ("fx", "fy", "fz", "rz", "ry", "rx")

# Gripper/F-T layout in the connector/tool frame (metres above the TCP)
FT_SITE_Z = 0.037
PALM_Z = (0.025, 0.031)
FINGER_HALF_THICKNESS = 0.00125


@dataclass(frozen=True)
class WorkcellLayout:
    """Derived nominal poses of the workcell (world frame, metres)."""

    socket_mouth: np.ndarray
    home_tcp: np.ndarray

    @staticmethod
    def from_spec(spec: ConnectorSpec, fixture: FixtureConfig) -> "WorkcellLayout":
        s = spec.socket
        mouth_z = JIG_BOTTOM_Z + JIG_THICKNESS + (s.pcb_thickness_mm + s.floor_mm + s.depth_mm) * MM
        mouth = np.array([0.0, 0.0, mouth_z])
        home = mouth + np.array([0.0, 0.0, fixture.home_height_mm * MM])
        return WorkcellLayout(socket_mouth=mouth, home_tcp=home)


def _look_at(pos: np.ndarray, target: np.ndarray) -> str:
    """MJCF ``xyaxes`` for a camera at ``pos`` looking at ``target`` (world z up)."""
    f = target - pos
    f = f / np.linalg.norm(f)
    x = np.cross(f, np.array([0.0, 0.0, 1.0]))
    x /= np.linalg.norm(x)
    y = np.cross(x, f)
    return " ".join(f"{v:.6g}" for v in (*x, *y))


def _fmt(v: float | np.ndarray | tuple | list) -> str:
    if isinstance(v, (float, int, np.floating)):
        return f"{float(v):.6g}"
    return " ".join(f"{float(x):.6g}" for x in v)


def _box(name: str, pos, size, cls: str, quat=None, material: str | None = None, extra: str = "") -> str:
    q = f' quat="{_fmt(quat)}"' if quat is not None else ""
    m = f' material="{material}"' if material else ""
    return f'<geom name="{name}" type="box" class="{cls}" pos="{_fmt(pos)}" size="{_fmt(size)}"{q}{m}{extra}/>'


def socket_collision_shapes(spec: ConnectorSpec) -> list[dict]:
    """Return the socket's collision solids in the socket frame.

    Each entry is either a box (``kind="box"``, with ``pos`` and ``half``) or a
    convex prism (``kind="prism"``, with ``vertices`` (N, 3)). Exposed separately
    so tests can verify the cavity geometry analytically.

    Each wall side is a single convex prism: the wall profile
    ``(h,-D) -> (h+w,-D) -> (h+w,0) -> (h+ch,0) -> (h,-ch)`` extruded along the
    wall. Using one convex solid per side (instead of a box stack) avoids
    internal edges at the bottom of the lead-in, where a hidden face of a
    neighbouring box would otherwise produce non-physical "ghost" contact normals.
    """
    hx, hy = spec.cavity_half
    ox, oy = spec.outer_half
    depth = spec.depth
    ch = spec.chamfer
    wall = spec.socket.wall_mm * MM
    floor = spec.socket.floor_mm * MM
    shapes: list[dict] = [
        dict(
            kind="box",
            name="floor",
            pos=np.array([0.0, 0.0, -depth - floor * 0.5]),
            half=np.array([ox, oy, floor * 0.5]),
        )
    ]
    sides = [
        ("xpos", np.array([1.0, 0.0, 0.0]), hx, oy),
        ("xneg", np.array([-1.0, 0.0, 0.0]), hx, oy),
        ("ypos", np.array([0.0, 1.0, 0.0]), hy, ox),
        ("yneg", np.array([0.0, -1.0, 0.0]), hy, ox),
    ]
    z_hat = np.array([0.0, 0.0, 1.0])
    for tag, d, h, half_len in sides:
        e = np.cross(z_hat, d)
        if ch > 0.0:
            profile = [(h, -depth), (h + wall, -depth), (h + wall, 0.0), (h + ch, 0.0), (h, -ch)]
        else:
            profile = [(h, -depth), (h + wall, -depth), (h + wall, 0.0), (h, 0.0)]
        verts = [d * u + z_hat * z + e * s for s in (-half_len, half_len) for (u, z) in profile]
        shapes.append(dict(kind="prism", name=f"wall_{tag}", vertices=np.array(verts)))
    return shapes


def build_workcell_xml(
    spec: ConnectorSpec | None = None,
    fixture: FixtureConfig | None = None,
    sim: SimConfig | None = None,
    friction: float | None = None,
) -> str:
    """Generate the complete MJCF string for the insertion workcell."""
    spec = spec or ConnectorSpec.load("rect_12x8")
    fixture = fixture or FixtureConfig()
    sim = sim or SimConfig()
    mu = spec.friction if friction is None else friction
    layout = WorkcellLayout.from_spec(spec, fixture)
    px, py, pz = spec.plug_half
    hx, hy = spec.cavity_half
    ox, oy = spec.outer_half
    depth = spec.depth
    floor = spec.socket.floor_mm * MM
    pcb = spec.socket.pcb_thickness_mm * MM
    plug_len = spec.plug.length_mm * MM
    grip_len = spec.plug.grip_length_mm * MM
    solimp = _fmt(sim.contact_solimp)
    solref = f"{sim.contact_timeconst_s:.6g} {sim.contact_dampratio:.6g}"

    # ---------------------------------------------------------------- socket body
    socket_geoms = []
    socket_meshes = []
    for shp in socket_collision_shapes(spec):
        name = SOCKET_GEOM_PREFIX + shp["name"]
        if shp["kind"] == "box":
            socket_geoms.append(_box(name, shp["pos"], shp["half"], "socket_col", None, "mat_socket"))
        else:
            socket_meshes.append(f'<mesh name="mesh_{shp["name"]}" vertex="{_fmt(shp["vertices"].ravel())}"/>')
            material = "mat_socket_front" if shp["name"].endswith("yneg") else "mat_socket"
            socket_geoms.append(
                f'<geom name="{name}" type="mesh" mesh="mesh_{shp["name"]}" class="socket_col" material="{material}"/>'
            )
    pcb_half = np.array([max(0.02, ox + 0.011), max(0.015, oy + 0.008), pcb * 0.5])
    pcb_z = -depth - floor - pcb * 0.5
    socket_geoms.append(_box(SOCKET_GEOM_PREFIX + "pcb", [0, 0, pcb_z], pcb_half, "socket_col", None, "mat_pcb"))
    jig_half = np.array([pcb_half[0] + 0.003, pcb_half[1] + 0.003, JIG_THICKNESS * 0.5])
    jig_z = pcb_z - pcb * 0.5 - JIG_THICKNESS * 0.5
    socket_geoms.append(_box("jig_plate", [0, 0, jig_z], jig_half, "visual", None, "mat_alu_dark"))
    # SMD pads and solder tails (visual only) for a recognizable board context.
    pad_z = pcb_z + pcb * 0.5 + 0.00005
    for i, xoff in enumerate(np.linspace(-hx + 0.0015, hx - 0.0015, 5)):
        for sgn in (-1, 1):
            socket_geoms.append(
                _box(f"pad_{i}_{sgn > 0}", [xoff, sgn * (oy + 0.0022), pad_z], [0.0007, 0.0012, 0.00005], "visual", None, "mat_gold")
            )
    socket_geoms.append(f'<site name="socket_mouth" pos="0 0 0" size="0.0006" rgba="0.1 1 0.3 1"/>')

    # ---------------------------------------------------------------- contact model
    # Every physical contact between the held parts and the receptacle is an
    # explicit pair, so the friction model (solreffriction) is controlled and the
    # complete contact set is auditable.
    socket_collider_names = [SOCKET_GEOM_PREFIX + s["name"] for s in socket_collision_shapes(spec)]
    socket_collider_names.append(SOCKET_GEOM_PREFIX + "pcb")
    solreffriction = f"{sim.contact_friction_timeconst_s:.6g} 1"
    contact_pairs = [
        f'<pair name="c_{a}__{b}" geom1="{a}" geom2="{b}" condim="3" '
        f'friction="{mu:.6g} {mu:.6g} 0.005 0.0001 0.0001" solref="{solref}" '
        f'solreffriction="{solreffriction}" solimp="{solimp}" margin="0" gap="0"/>'
        for a in (*PLUG_GEOM_NAMES, *GRIPPER_GEOM_NAMES)
        for b in socket_collider_names
    ]

    # ---------------------------------------------------------------- outline markers
    def outline(prefix: str, material: str) -> list[str]:
        t = 0.00025
        lines = [
            _box(f"{prefix}_ox", [0, hy + t, 0], [hx + 2 * t, t, t], "visual", None, material),
            _box(f"{prefix}_oxn", [0, -hy - t, 0], [hx + 2 * t, t, t], "visual", None, material),
            _box(f"{prefix}_oy", [hx + t, 0, 0], [t, hy, t], "visual", None, material),
            _box(f"{prefix}_oyn", [-hx - t, 0, 0], [t, hy, t], "visual", None, material),
            f'<geom name="{prefix}_axis" type="cylinder" class="visual" fromto="0 0 0 0 0 0.03" size="0.00018" material="{material}"/>',
        ]
        return lines

    # ---------------------------------------------------------------- fixture visuals
    finger_z0 = plug_len - grip_len
    finger_hz = grip_len * 0.5
    finger_x = px + FINGER_HALF_THICKNESS
    palm_hz = (PALM_Z[1] - PALM_Z[0]) * 0.5
    palm_z = (PALM_Z[0] + PALM_Z[1]) * 0.5
    tool_mass = fixture.tool_mass_kg
    wrist_m = fixture.wrist_link_mass_kg
    lin_arm = fixture.linear_armature_kg
    ang_arm = fixture.angular_armature_kgm2
    lin_d = fixture.linear_viscous_n_s_per_m
    ang_d = fixture.angular_viscous_nm_s_per_rad
    txy = fixture.travel_xy_mm * MM
    zdn = fixture.travel_z_down_mm * MM
    zup = fixture.travel_z_up_mm * MM
    yaw_r = np.deg2rad(fixture.yaw_range_deg)
    tilt_r = np.deg2rad(fixture.tilt_range_deg)
    home = layout.home_tcp
    beam_z = 0.235
    cam_close = layout.socket_mouth + np.array([0.060, -0.075, 0.028])
    cam_side = layout.socket_mouth + np.array([0.0, -0.078, 0.003])

    xml = f"""<mujoco model="defex_daie_workcell">
  <!-- Generated by defex.sim.scene_builder. Do not edit by hand; regenerate with
       `python -m defex.sim.scene_builder`. Connector: {spec.name}
       cavity {2 * hx / MM:.2f} x {2 * hy / MM:.2f} mm, depth {depth / MM:.1f} mm,
       clearance {spec.socket.clearance_mm:.2f} mm/side, chamfer {spec.socket.chamfer_mm:.2f} mm, friction {mu:.3g} -->
  <compiler angle="radian" autolimits="true"/>
  <option timestep="{sim.timestep_s:.6g}" integrator="{sim.integrator}" cone="{sim.cone}" impratio="{sim.impratio:.6g}"
          gravity="0 0 -9.81" tolerance="1e-9" iterations="80" ls_iterations="20"/>
  <statistic center="0 0 0.05" extent="0.25" meansize="0.006"/>
  <visual>
    <global offwidth="1920" offheight="1080" fovy="35" azimuth="135" elevation="-22"/>
    <quality shadowsize="4096" offsamples="8"/>
    <map znear="0.004" zfar="10" force="0.02"/>
    <headlight ambient="0.32 0.32 0.34" diffuse="0.45 0.45 0.45" specular="0.1 0.1 0.1"/>
    <scale contactwidth="0.15" contactheight="0.05" forcewidth="0.06" framelength="1.5" framewidth="0.08"/>
    <rgba contactpoint="0.9 0.1 0.1 1" contactforce="1 0.3 0.1 1"/>
  </visual>

  <asset>
    <texture name="tex_sky" type="skybox" builtin="gradient" rgb1="0.16 0.18 0.22" rgb2="0.03 0.035 0.045" width="512" height="512"/>
    <texture name="tex_grid" type="2d" builtin="checker" rgb1="0.80 0.81 0.83" rgb2="0.74 0.75 0.78" width="512" height="512" mark="edge" markrgb="0.66 0.67 0.70"/>
    <material name="mat_table" texture="tex_grid" texrepeat="50 50" texuniform="true"/>
    <material name="mat_alu" rgba="0.74 0.76 0.80 1" specular="0.6" shininess="0.7"/>
    <material name="mat_alu_dark" rgba="0.36 0.38 0.42 1" specular="0.4" shininess="0.5"/>
    <material name="mat_dark" rgba="0.12 0.12 0.14 1" specular="0.3" shininess="0.4"/>
    <material name="mat_sensor" rgba="0.16 0.22 0.36 1" specular="0.5" shininess="0.6"/>
    <material name="mat_plug" rgba="0.96 0.46 0.08 1" specular="0.35" shininess="0.4"/>
    <material name="mat_cable" rgba="0.08 0.08 0.09 1" specular="0.2"/>
    <material name="mat_socket" rgba="0.93 0.91 0.85 0.75" specular="0.25" shininess="0.3"/>
    <material name="mat_socket_front" rgba="0.93 0.91 0.85 0.28" specular="0.25" shininess="0.3"/>
    {chr(10).join('    ' + mm for mm in socket_meshes).strip()}
    <material name="mat_pcb" rgba="0.05 0.34 0.17 1" specular="0.3"/>
    <material name="mat_gold" rgba="0.86 0.68 0.22 1" specular="0.9" shininess="0.9"/>
    <material name="mat_marker_est" rgba="0.15 0.95 0.35 0.75" emission="0.4"/>
    <material name="mat_marker_nom" rgba="0.95 0.2 0.2 0.6" emission="0.3"/>
    <material name="mat_marker_sp" rgba="0.1 0.8 1.0 0.85" emission="0.5"/>
  </asset>

  <default>
    <default class="visual">
      <geom contype="0" conaffinity="0" group="1" density="0"/>
    </default>
    <default class="socket_col">
      <geom contype="0" conaffinity="0" group="0" condim="3" friction="{mu:.6g} 0.005 0.0001"
            solref="{solref}" solimp="{solimp}" margin="0" gap="0" density="0"/>
    </default>
    <default class="plug_col">
      <geom contype="0" conaffinity="0" group="0" condim="3" friction="{mu:.6g} 0.005 0.0001"
            solref="{solref}" solimp="{solimp}" margin="0" gap="0" density="0"/>
    </default>
  </default>

  <worldbody>
    <light name="key" directional="true" pos="0.3 -0.4 0.8" dir="-0.35 0.45 -0.8" diffuse="0.55 0.55 0.55" specular="0.2 0.2 0.2" castshadow="true"/>
    <light name="fill" pos="-0.3 0.3 0.5" dir="0.4 -0.4 -0.6" diffuse="0.25 0.25 0.28" specular="0 0 0" castshadow="false"/>
    <geom name="table" type="box" class="visual" pos="0 0 -0.01" size="0.45 0.45 0.01" material="mat_table"/>
    <!-- Static gantry frame (visual only) -->
    <geom name="gantry_post_l" type="box" class="visual" pos="0 0.17 {beam_z * 0.5:.6g}" size="0.015 0.015 {beam_z * 0.5 + 0.02:.6g}" material="mat_alu_dark"/>
    <geom name="gantry_post_r" type="box" class="visual" pos="0 -0.17 {beam_z * 0.5:.6g}" size="0.015 0.015 {beam_z * 0.5 + 0.02:.6g}" material="mat_alu_dark"/>
    <geom name="gantry_beam" type="box" class="visual" pos="0 0 {beam_z + 0.035:.6g}" size="0.02 0.19 0.015" material="mat_alu"/>
    <geom name="gantry_rail" type="box" class="visual" pos="0 0 {beam_z + 0.0185:.6g}" size="0.006 0.18 0.0015" material="mat_dark"/>

    <camera name="closeup" pos="{_fmt(cam_close)}" xyaxes="{_look_at(cam_close, layout.socket_mouth + np.array([0, 0, 0.007]))}" fovy="34"/>
    <camera name="side" pos="{_fmt(cam_side)}" xyaxes="{_look_at(cam_side, layout.socket_mouth + np.array([0, 0, -0.004]))}" fovy="24"/>
    <camera name="overview" mode="targetbody" target="socket" pos="0.32 -0.36 0.26"/>
    <camera name="top" pos="0 0 {layout.socket_mouth[2] + 0.12:.6g}" xyaxes="1 0 0 0 1 0"/>

    <!-- Nominal socket pose (what the fixed-trajectory program assumes) -->
    <body name="marker_nominal" pos="{_fmt(layout.socket_mouth)}">
      {''.join(outline('nominal', 'mat_marker_nom'))}
    </body>
    <!-- Vision estimate of the socket mouth (updated by the demo) -->
    <body name="marker_estimate" mocap="true" pos="{_fmt(layout.socket_mouth)}">
      {''.join(outline('estimate', 'mat_marker_est'))}
    </body>
    <!-- Commanded TCP setpoint (updated by the demo) -->
    <body name="marker_setpoint" mocap="true" pos="{_fmt(home)}">
      <geom name="setpoint_dot" type="sphere" class="visual" size="0.0007" material="mat_marker_sp"/>
    </body>

    <!-- Receptacle: pose randomized per trial through the mocap pose -->
    <body name="socket" mocap="true" pos="{_fmt(layout.socket_mouth)}">
      {chr(10).join('      ' + g for g in socket_geoms).strip()}
    </body>

    <!-- 6-DOF insertion fixture: X-Y-Z gantry + yaw/pitch/roll wrist pivoting at the TCP -->
    <body name="fixture_x" pos="{_fmt(home)}" gravcomp="1">
      <joint name="fx" type="slide" axis="1 0 0" range="{-txy:.6g} {txy:.6g}" armature="{lin_arm:.6g}" damping="{lin_d:.6g}"/>
      <inertial pos="0 0 0.2" mass="{fixture.carriage_x_mass_kg:.6g}" diaginertia="0.004 0.004 0.004"/>
      <geom name="carriage_x" type="box" class="visual" pos="0 0 {beam_z + 0.035 - home[2]:.6g}" size="0.03 0.03 0.022" material="mat_alu"/>
      <body name="fixture_y" gravcomp="1">
        <joint name="fy" type="slide" axis="0 1 0" range="{-txy:.6g} {txy:.6g}" armature="{lin_arm:.6g}" damping="{lin_d:.6g}"/>
        <inertial pos="0 0 0.18" mass="{fixture.carriage_y_mass_kg:.6g}" diaginertia="0.003 0.003 0.003"/>
        <geom name="carriage_y" type="box" class="visual" pos="0 -0.035 {beam_z + 0.03 - home[2]:.6g}" size="0.022 0.008 0.03" material="mat_alu_dark"/>
        <body name="fixture_z" gravcomp="1">
          <joint name="fz" type="slide" axis="0 0 1" range="{-zdn:.6g} {zup:.6g}" armature="{lin_arm:.6g}" damping="{lin_d:.6g}"/>
          <inertial pos="0 0 0.12" mass="{fixture.ram_z_mass_kg:.6g}" diaginertia="0.002 0.002 0.0005"/>
          <geom name="ram_z" type="box" class="visual" pos="0 -0.035 0.135" size="0.01 0.006 0.09" material="mat_alu"/>
          <geom name="ram_arm" type="box" class="visual" pos="0 -0.0175 0.062" size="0.008 0.0175 0.006" material="mat_alu"/>
          <body name="wrist_yaw" gravcomp="1">
            <joint name="rz" type="hinge" axis="0 0 1" range="{-yaw_r:.6g} {yaw_r:.6g}" armature="{ang_arm:.6g}" damping="{ang_d:.6g}"/>
            <inertial pos="0 0 0.053" mass="{wrist_m:.6g}" diaginertia="1e-5 1e-5 1e-5"/>
            <geom name="wrist_yaw_vis" type="cylinder" class="visual" pos="0 0 0.053" size="0.012 0.004" material="mat_dark"/>
            <body name="wrist_pitch" gravcomp="1">
              <joint name="ry" type="hinge" axis="0 1 0" range="{-tilt_r:.6g} {tilt_r:.6g}" armature="{ang_arm:.6g}" damping="{ang_d:.6g}"/>
              <inertial pos="0 0 0.046" mass="{wrist_m:.6g}" diaginertia="1e-5 1e-5 1e-5"/>
              <geom name="wrist_pitch_vis" type="box" class="visual" pos="0 0 0.046" size="0.011 0.009 0.003" material="mat_alu"/>
              <body name="wrist_roll" gravcomp="1">
                <joint name="rx" type="hinge" axis="1 0 0" range="{-tilt_r:.6g} {tilt_r:.6g}" armature="{ang_arm:.6g}" damping="{ang_d:.6g}"/>
                <inertial pos="0 0 0.040" mass="{wrist_m:.6g}" diaginertia="1e-5 1e-5 1e-5"/>
                <geom name="flange" type="cylinder" class="visual" pos="0 0 0.0400" size="0.010 0.003" material="mat_alu"/>
                <body name="tool">
                  <inertial pos="0 0 0.030" mass="{tool_mass:.6g}" diaginertia="4e-6 4e-6 3e-6"/>
                  <site name="ft_site" pos="0 0 {FT_SITE_Z:.6g}" size="0.001" rgba="0.2 0.4 1 1"/>
                  <geom name="ft_sensor" type="cylinder" class="visual" pos="0 0 0.034" size="0.0095 0.003" material="mat_sensor"/>
                  <geom name="palm" type="box" class="plug_col" pos="0 0 {palm_z:.6g}" size="{px + 2 * FINGER_HALF_THICKNESS + 0.0005:.6g} {py + 0.001:.6g} {palm_hz:.6g}" material="mat_alu"/>
                  <geom name="finger_pos" type="box" class="plug_col" pos="{finger_x:.6g} 0 {finger_z0 + finger_hz:.6g}" size="{FINGER_HALF_THICKNESS:.6g} {py:.6g} {finger_hz:.6g}" material="mat_alu_dark"/>
                  <geom name="finger_neg" type="box" class="plug_col" pos="{-finger_x:.6g} 0 {finger_z0 + finger_hz:.6g}" size="{FINGER_HALF_THICKNESS:.6g} {py:.6g} {finger_hz:.6g}" material="mat_alu_dark"/>
                  <body name="connector">
                    <geom name="plug" type="box" class="plug_col" pos="0 0 {pz:.6g}" size="{px:.6g} {py:.6g} {pz:.6g}" mass="{spec.plug.mass_g * 1e-3:.6g}" material="mat_plug"/>
                    <geom name="plug_key" type="box" class="visual" pos="0 {py + 0.00015:.6g} {pz * 1.4:.6g}" size="{px * 0.35:.6g} 0.00015 {pz * 0.45:.6g}" material="mat_dark"/>
                    <geom name="cable" type="cylinder" class="visual" fromto="0 0 {PALM_Z[1]:.6g} 0 0 {PALM_Z[1] + 0.003:.6g}" size="0.0025" material="mat_cable"/>
                    <site name="tcp" pos="0 0 0" size="0.0006" rgba="1 1 0 1"/>
                  </body>
                </body>
              </body>
            </body>
          </body>
        </body>
      </body>
    </body>
  </worldbody>

  <actuator>
    <position name="act_fx" joint="fx" kp="{fixture.linear_kp_n_per_m:.6g}" dampratio="{fixture.linear_dampratio:.6g}" ctrlrange="{-txy:.6g} {txy:.6g}" forcerange="{-fixture.linear_force_limit_n:.6g} {fixture.linear_force_limit_n:.6g}"/>
    <position name="act_fy" joint="fy" kp="{fixture.linear_kp_n_per_m:.6g}" dampratio="{fixture.linear_dampratio:.6g}" ctrlrange="{-txy:.6g} {txy:.6g}" forcerange="{-fixture.linear_force_limit_n:.6g} {fixture.linear_force_limit_n:.6g}"/>
    <position name="act_fz" joint="fz" kp="{fixture.linear_kp_n_per_m:.6g}" dampratio="{fixture.linear_dampratio:.6g}" ctrlrange="{-zdn:.6g} {zup:.6g}" forcerange="{-fixture.linear_force_limit_n:.6g} {fixture.linear_force_limit_n:.6g}"/>
    <position name="act_rz" joint="rz" kp="{fixture.angular_kp_nm_per_rad:.6g}" dampratio="{fixture.angular_dampratio:.6g}" ctrlrange="{-yaw_r:.6g} {yaw_r:.6g}" forcerange="{-fixture.angular_torque_limit_nm:.6g} {fixture.angular_torque_limit_nm:.6g}"/>
    <position name="act_ry" joint="ry" kp="{fixture.angular_kp_nm_per_rad:.6g}" dampratio="{fixture.angular_dampratio:.6g}" ctrlrange="{-tilt_r:.6g} {tilt_r:.6g}" forcerange="{-fixture.angular_torque_limit_nm:.6g} {fixture.angular_torque_limit_nm:.6g}"/>
    <position name="act_rx" joint="rx" kp="{fixture.angular_kp_nm_per_rad:.6g}" dampratio="{fixture.angular_dampratio:.6g}" ctrlrange="{-tilt_r:.6g} {tilt_r:.6g}" forcerange="{-fixture.angular_torque_limit_nm:.6g} {fixture.angular_torque_limit_nm:.6g}"/>
  </actuator>

  <contact>
    {chr(10).join('    ' + c for c in contact_pairs).strip()}
  </contact>

  <sensor>
    <force name="ft_force" site="ft_site"/>
    <torque name="ft_torque" site="ft_site"/>
    <jointpos name="enc_fx" joint="fx"/>
    <jointpos name="enc_fy" joint="fy"/>
    <jointpos name="enc_fz" joint="fz"/>
    <jointpos name="enc_rz" joint="rz"/>
    <jointpos name="enc_ry" joint="ry"/>
    <jointpos name="enc_rx" joint="rx"/>
  </sensor>
</mujoco>
"""
    return xml


DEFAULT_SCENE_PATH = REPO_ROOT / "simulations" / "scenes" / "daie_workcell.xml"


def write_scene(path: Path = DEFAULT_SCENE_PATH, connector: str = "rect_12x8") -> Path:
    spec = ConnectorSpec.load(connector)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_workcell_xml(spec))
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate the DAIE workcell MJCF scene.")
    parser.add_argument("--connector", default="rect_12x8", help="connector spec in assets/connectors")
    parser.add_argument("--out", type=Path, default=DEFAULT_SCENE_PATH)
    args = parser.parse_args()
    out = write_scene(args.out, args.connector)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
