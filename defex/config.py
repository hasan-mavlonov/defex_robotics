"""Configuration objects for the Defex Adaptive Insertion Engine (DAIE).

All user-facing quantities carry an explicit unit suffix (``_mm``, ``_deg``, ``_n``,
``_nm``, ``_s``). Code that talks to the simulator converts to SI internally.

The default values document the physical assumptions of V0.1. See README section
"Physical assumptions" for the rationale behind each number.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields, is_dataclass, replace
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CONNECTOR_ASSET_DIR = REPO_ROOT / "assets" / "connectors"

MM = 1e-3
DEG = 3.141592653589793 / 180.0


# --------------------------------------------------------------------------------------
# Connector geometry
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class PlugGeometry:
    """Male connector housing that the fixture holds and inserts."""

    size_x_mm: float = 12.0  # long side of the rectangular cross-section
    size_y_mm: float = 8.0  # short side of the rectangular cross-section
    length_mm: float = 25.0  # total housing length along the insertion axis
    mass_g: float = 4.0  # PBT housing + crimped terminals
    grip_length_mm: float = 7.0  # length held by the gripper fingers (at the top)


@dataclass(frozen=True)
class SocketGeometry:
    """Female receptacle: a real cavity built from collision boxes."""

    clearance_mm: float = 0.5  # radial clearance per side
    depth_mm: float = 15.0  # cavity depth == full insertion depth
    chamfer_mm: float = 0.8  # 45 degree lead-in on the cavity opening (0 disables)
    wall_mm: float = 2.5  # housing wall thickness around the cavity
    floor_mm: float = 2.0  # cavity floor thickness
    pcb_thickness_mm: float = 1.6  # FR4 board the receptacle is mounted on


@dataclass(frozen=True)
class ConnectorSpec:
    name: str = "rect_12x8"
    description: str = "Generic rectangular wire-to-board connector, 12 x 8 mm"
    plug: PlugGeometry = field(default_factory=PlugGeometry)
    socket: SocketGeometry = field(default_factory=SocketGeometry)
    friction: float = 0.3  # PBT-GF on PBT, dry (typ. 0.25-0.35)

    # Derived quantities (SI) -------------------------------------------------------
    @property
    def plug_half(self) -> tuple[float, float, float]:
        p = self.plug
        return (p.size_x_mm * 0.5 * MM, p.size_y_mm * 0.5 * MM, p.length_mm * 0.5 * MM)

    @property
    def cavity_half(self) -> tuple[float, float]:
        c = self.socket.clearance_mm
        return ((self.plug.size_x_mm * 0.5 + c) * MM, (self.plug.size_y_mm * 0.5 + c) * MM)

    @property
    def depth(self) -> float:
        return self.socket.depth_mm * MM

    @property
    def chamfer(self) -> float:
        return self.socket.chamfer_mm * MM

    @property
    def outer_half(self) -> tuple[float, float]:
        hx, hy = self.cavity_half
        w = self.socket.wall_mm * MM
        return (hx + w, hy + w)

    @staticmethod
    def load(name_or_path: str | Path) -> "ConnectorSpec":
        path = Path(name_or_path)
        if not path.suffix:
            path = CONNECTOR_ASSET_DIR / f"{name_or_path}.json"
        raw = json.loads(path.read_text())
        return ConnectorSpec(
            name=raw["name"],
            description=raw.get("description", ""),
            plug=PlugGeometry(**raw["plug"]),
            socket=SocketGeometry(**raw["socket"]),
            friction=float(raw.get("friction", 0.3)),
        )

    def with_overrides(self, clearance_mm: float | None = None, chamfer_mm: float | None = None) -> "ConnectorSpec":
        socket = self.socket
        if clearance_mm is not None:
            socket = replace(socket, clearance_mm=clearance_mm)
        if chamfer_mm is not None:
            socket = replace(socket, chamfer_mm=chamfer_mm)
        return replace(self, socket=socket)


# --------------------------------------------------------------------------------------
# Simulation, fixture, sensors, safety
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class SimConfig:
    timestep_s: float = 0.0005  # 2 kHz physics
    control_period_s: float = 0.002  # 500 Hz control loop (UR RTDE class)
    contact_timeconst_s: float = 0.002  # stiff normal contacts (>= 2 x timestep for stability)
    contact_dampratio: float = 1.0
    # Softer reference dynamics for the friction dimensions only. MuJoCo's convex
    # soft-contact model otherwise inflates the normal force during fast sliding
    # (measured 42 N vs ~12 N Coulomb estimate when a plug snaps off the lead-in).
    # 20 ms keeps static creep below ~0.03 mm/s at half the friction limit.
    contact_friction_timeconst_s: float = 0.02
    contact_solimp: tuple[float, float, float, float, float] = (0.95, 0.99, 0.0002, 0.5, 2.0)
    integrator: str = "implicitfast"
    cone: str = "elliptic"
    impratio: float = 10.0
    max_trial_time_s: float = 30.0
    settle_time_s: float = 0.25  # hold after the controller finishes before scoring


@dataclass(frozen=True)
class FixtureConfig:
    """Directly controlled 6-DOF insertion fixture (Cartesian gantry + wrist).

    The three wrist hinges intersect at the connector tip (remote-center
    kinematics, equivalent to a hexapod with its pivot at the TCP). Each joint is
    driven by a position servo with explicit force/torque saturation.
    """

    linear_kp_n_per_m: float = 10000.0  # 10 N/mm servo stiffness
    linear_dampratio: float = 1.0
    linear_force_limit_n: float = 60.0
    angular_kp_nm_per_rad: float = 15.0
    angular_dampratio: float = 1.0
    angular_torque_limit_nm: float = 2.0
    carriage_x_mass_kg: float = 1.5
    carriage_y_mass_kg: float = 1.0
    ram_z_mass_kg: float = 0.5
    wrist_link_mass_kg: float = 0.05
    tool_mass_kg: float = 0.03  # gripper + F/T tool side, excluding the connector
    linear_armature_kg: float = 0.2  # reflected rotor inertia of the ball-screw drives
    angular_armature_kgm2: float = 0.002
    linear_viscous_n_s_per_m: float = 2.0
    angular_viscous_nm_s_per_rad: float = 0.002
    # Motion limits enforced by the motion generator (bounded velocities).
    max_linear_speed_mm_s: float = 50.0
    max_angular_speed_deg_s: float = 45.0
    max_linear_accel_mm_s2: float = 500.0
    max_angular_accel_deg_s2: float = 600.0
    home_height_mm: float = 60.0  # TCP height above the nominal socket mouth at start
    travel_xy_mm: float = 80.0
    travel_z_down_mm: float = 90.0
    travel_z_up_mm: float = 60.0
    yaw_range_deg: float = 35.0
    tilt_range_deg: float = 25.0


@dataclass(frozen=True)
class SensorNoiseConfig:
    """Observation noise. Ground truth never reaches the controller directly."""

    # One-shot vision estimate of the socket mouth pose (camera + calibration).
    vision_xy_sigma_mm: float = 0.3
    vision_z_sigma_mm: float = 0.3
    vision_yaw_sigma_deg: float = 0.5
    vision_tilt_sigma_deg: float = 0.3
    vision_bias_mm: float = 0.0  # systematic hand-eye calibration error (random direction)
    # In-hand estimate of the connector pose relative to the gripper.
    grasp_xy_sigma_mm: float = 0.1
    grasp_rot_sigma_deg: float = 0.3
    # 6-axis wrist force/torque sensor (ATI Mini40 class).
    ft_force_sigma_n: float = 0.03
    ft_torque_sigma_nm: float = 0.0005
    ft_force_bias_n: float = 0.3  # per-trial bias; removed by taring
    ft_torque_bias_nm: float = 0.003
    ft_filter_cutoff_hz: float = 40.0
    # Joint encoders, expressed at the TCP.
    encoder_pos_sigma_mm: float = 0.002
    encoder_rot_sigma_deg: float = 0.002

    def scaled_vision(self, xy_sigma_mm: float) -> "SensorNoiseConfig":
        """Scale all vision noise terms with the lateral sigma (for noise sweeps)."""
        base = SensorNoiseConfig()
        k = xy_sigma_mm / base.vision_xy_sigma_mm if base.vision_xy_sigma_mm > 0 else 0.0
        return replace(
            self,
            vision_xy_sigma_mm=xy_sigma_mm,
            vision_z_sigma_mm=base.vision_z_sigma_mm * k,
            vision_yaw_sigma_deg=base.vision_yaw_sigma_deg * k,
            vision_tilt_sigma_deg=base.vision_tilt_sigma_deg * k,
        )


@dataclass(frozen=True)
class SafetyConfig:
    protective_stop_force_n: float = 30.0  # online, on the measured F/T (all controllers)
    protective_stop_torque_nm: float = 0.6
    damage_contact_force_n: float = 45.0  # ground-truth contact force that counts as damage
    max_penetration_mm: float = 0.2  # ground-truth interpenetration validity bound


@dataclass(frozen=True)
class SuccessCriteria:
    depth_tolerance_mm: float = 0.5  # seated if depth >= socket depth - tolerance
    lateral_margin_mm: float = 0.15  # lateral offset <= clearance + margin
    max_tilt_deg: float = 3.0
    max_yaw_deg: float = 3.0
    max_final_speed_mm_s: float = 2.0


# --------------------------------------------------------------------------------------
# Disturbances and experiment conditions
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class DisturbanceSpec:
    """How the true socket/grasp pose deviates from nominal for one condition.

    ``*_mode`` is ``"fixed"`` (exact magnitude, random direction/sign) or
    ``"uniform"`` (uniform within the magnitude).
    """

    lateral_mm: float = 0.0
    lateral_mode: str = "fixed"
    yaw_deg: float = 0.0
    yaw_mode: str = "fixed"
    tilt_deg: float = 0.0
    tilt_mode: str = "fixed"
    height_mm: float = 0.0  # uniform in [-h, h]
    # In-hand (grasp) errors. Flat fingers clamp the plug's +/-x faces, so the plug
    # can only slip along y, slide down from the palm stop (z <= 0), or rotate
    # about the finger normal (x). Each is uniform in [-a, a] ([-a, 0] for axial).
    grasp_lateral_mm: float = 0.0
    grasp_axial_mm: float = 0.0
    grasp_tilt_deg: float = 0.0


@dataclass(frozen=True)
class Condition:
    name: str
    group: str
    disturbance: DisturbanceSpec = field(default_factory=DisturbanceSpec)
    noise: SensorNoiseConfig = field(default_factory=SensorNoiseConfig)
    friction: float | None = None  # None -> connector default
    connector: str = "rect_12x8"
    clearance_mm: float | None = None
    chamfer_mm: float | None = None
    description: str = ""


# --------------------------------------------------------------------------------------
# Controllers
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class FixedTrajectoryConfig:
    approach_height_mm: float = 5.0
    transit_speed_mm_s: float = 40.0
    insert_speed_mm_s: float = 8.0
    overtravel_mm: float = 0.5  # programmed past the nominal seat to guarantee preload
    dwell_s: float = 0.3


@dataclass(frozen=True)
class PositionCorrectionConfig:
    approach_height_mm: float = 5.0
    transit_speed_mm_s: float = 40.0
    insert_speed_mm_s: float = 8.0
    overtravel_mm: float = 0.5
    dwell_s: float = 0.3


@dataclass(frozen=True)
class AdaptiveConfig:
    # Motion
    approach_height_mm: float = 2.5  # above the estimated mouth, plus 3 sigma of vision z
    retract_clearance_mm: float = 3.0  # height above the estimated mouth for re-positioning
    transit_speed_mm_s: float = 40.0
    reposition_speed_mm_s: float = 15.0
    retract_speed_mm_s: float = 15.0
    # Force-guided insertion (velocity = gain * (target - axial force))
    contact_force_n: float = 1.0
    insert_force_n: float = 6.0
    force_gain_mm_s_per_n: float = 1.0
    max_insert_speed_mm_s: float = 6.0
    # Active compliance (admittance about the TCP)
    lateral_stiffness_n_per_mm: float = 0.3
    lateral_damping_n_s_per_mm: float = 1.0  # 1 mm/s per N of lateral force
    max_lateral_compliance_mm: float = 1.6
    rot_stiffness_nm_per_rad: float = 0.15
    rot_damping_nm_s_per_rad: float = 0.6  # loop gain 15/0.6 = 25 rad/s, well below the ~84 rad/s wrist servo
    max_rot_compliance_deg: float = 6.0
    # Surface conformity probe (zero-spring tilt admittance) before measuring the CoP
    conform_damping_nm_s_per_rad: float = 0.5
    conform_limit_deg: float = 4.0
    conform_max_s: float = 1.2
    conform_force_n: float = 8.0
    # Failure detection
    stall_window_s: float = 0.4
    stall_progress_mm: float = 0.15
    stall_force_fraction: float = 0.7
    max_force_n: float = 20.0  # controller-level abort/retract threshold
    max_torque_nm: float = 0.35
    max_lateral_force_n: float = 10.0
    insert_timeout_s: float = 6.0
    detect_hold_s: float = 0.12
    engage_depth_mm: float = 1.5  # depth beyond which the plug has entered the cavity
    seat_depth_margin_mm: float = 1.0
    # Recovery bounds
    max_attempts: int = 8
    max_lateral_correction_mm: float = 6.5
    max_yaw_correction_deg: float = 12.0
    max_tilt_correction_deg: float = 6.0
    time_limit_s: float = 26.0
    # Search policy (contact-based hole localization)
    search_resolution_mm: float = 0.25
    search_extent_mm: float = 7.0
    cop_sigma_mm: float = 0.5
    min_cop_force_n: float = 2.0
    # Verification (lateral constraint probe)
    verify_probe_mm: float = 1.2  # max guarded travel per direction (>= 2 x clearance + margin)
    verify_force_n: float = 2.0  # wall reaction required in every direction
    verify_preload_n: float = 1.0  # light axial preload during probing (keeps floor friction low)
    verify_probe_speed_mm_s: float = 2.5
    # Yaw centering inside the cavity (runs when the vision yaw sigma exceeds the gate)
    yaw_center_gate_deg: float = 1.0
    yaw_probe_speed_deg_s: float = 10.0
    yaw_probe_torque_nm: float = 0.02
    yaw_probe_max_deg: float = 7.0


# --------------------------------------------------------------------------------------
# Serialization helpers
# --------------------------------------------------------------------------------------


def to_dict(obj: Any) -> Any:
    """Recursively convert dataclasses (and tuples) into JSON-friendly structures."""
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: to_dict(getattr(obj, f.name)) for f in fields(obj)}
    if isinstance(obj, (list, tuple)):
        return [to_dict(v) for v in obj]
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    return obj


def dataclass_from_dict(cls: type, data: dict[str, Any]) -> Any:
    """Construct a (flat) dataclass from a dict, ignoring unknown keys."""
    names = {f.name for f in fields(cls)}
    kwargs = {k: (tuple(v) if isinstance(v, list) else v) for k, v in data.items() if k in names}
    return cls(**kwargs)


__all__ = [
    "AdaptiveConfig",
    "Condition",
    "ConnectorSpec",
    "DEG",
    "DisturbanceSpec",
    "FixedTrajectoryConfig",
    "FixtureConfig",
    "MM",
    "PlugGeometry",
    "PositionCorrectionConfig",
    "REPO_ROOT",
    "SafetyConfig",
    "SensorNoiseConfig",
    "SimConfig",
    "SocketGeometry",
    "SuccessCriteria",
    "asdict",
    "dataclass_from_dict",
    "to_dict",
]
