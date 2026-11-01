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
class MatingSpec:
    """Terminal and latch behaviour along the insertion axis (W3).

    Depths are measured from the socket mouth (0) to the seat (socket depth). Values
    come from the connector's JSON ("mating" -> "model"); its "basis" field says which
    are datasheet values and which are assumptions.
    """

    circuits: int
    terminal_wipe_mm: float
    terminal_peak_per_circuit_n: float
    terminal_slide_per_circuit_n: float
    terminal_lead_mm: float
    latch_onset_depth_mm: float
    latch_peak_depth_mm: float
    latch_peak_force_n: float
    latch_snap_depth_mm: float
    latch_post_snap_stroke_mm: float
    latch_retention_force_n: float
    mating_force_max_n: float  # datasheet maximum, total (per circuit x circuits)
    unmating_force_min_n: float  # datasheet minimum without the latch, total


@dataclass(frozen=True)
class ForceBudget:
    """Per-connector force thresholds, replacing the fixed 6/20/30/45 N of V0.1 (W3)."""

    insert_target_n: float
    abort_n: float
    protective_stop_n: float
    damage_n: float


@dataclass(frozen=True)
class ConnectorSpec:
    name: str = "rect_12x8"
    description: str = "Generic rectangular wire-to-board connector, 12 x 8 mm"
    plug: PlugGeometry = field(default_factory=PlugGeometry)
    socket: SocketGeometry = field(default_factory=SocketGeometry)
    friction: float = 0.3  # PBT-GF on PBT, dry (typ. 0.25-0.35)
    mating: MatingSpec | None = None  # None: housing only (V0.1 behaviour)
    force_budget: ForceBudget | None = None  # None: the V0.1 thresholds

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
        mating = None
        m = raw.get("mating", {})
        if "model" in m:
            mod = m["model"]
            mating = MatingSpec(
                circuits=int(m["circuits"]),
                terminal_wipe_mm=float(m["terminal_wipe_mm"]),
                terminal_peak_per_circuit_n=float(mod["terminal_peak_per_circuit_n"]),
                terminal_slide_per_circuit_n=float(mod["terminal_slide_per_circuit_n"]),
                terminal_lead_mm=float(mod["terminal_lead_mm"]),
                latch_onset_depth_mm=float(mod["latch_onset_depth_mm"]),
                latch_peak_depth_mm=float(mod["latch_peak_depth_mm"]),
                latch_peak_force_n=float(mod["latch_peak_force_n"]),
                latch_snap_depth_mm=float(mod["latch_snap_depth_mm"]),
                latch_post_snap_stroke_mm=float(mod["latch_post_snap_stroke_mm"]),
                latch_retention_force_n=float(m["latch_retention_force_min_n"]),
                mating_force_max_n=float(m["terminal_mating_force_max_per_circuit_n"]) * int(m["circuits"]),
                unmating_force_min_n=float(m["terminal_unmating_force_min_per_circuit_n"]) * int(m["circuits"]),
            )
        budget = ForceBudget(**raw["force_budget"]) if "force_budget" in raw else None
        return ConnectorSpec(
            name=raw["name"],
            description=raw.get("description", ""),
            plug=PlugGeometry(**raw["plug"]),
            socket=SocketGeometry(**raw["socket"]),
            friction=float(raw.get("friction", 0.3)),
            mating=mating,
            force_budget=budget,
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
    # Gross vision errors (W2 held-out families): with this probability a shot is off by a
    # uniform 3-6 mm in a random horizontal direction (wrong feature, glare, occlusion).
    vision_outlier_probability: float = 0.0
    vision_outlier_min_mm: float = 3.0
    vision_outlier_max_mm: float = 6.0
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
class CompliantStageConfig:
    """Passive remote-center compliance (RCC) stage between the F/T sensor and the gripper.

    Used only by the passive-compliance baselines (E, F). The center of compliance
    sits at the nominal plug tip. Values from public datasheets:

    * Lateral: ATI 9115-001-A (smallest 9115 model), 33 lb/in = 5.78 N/mm; allowable
      lateral misalignment for size 000: 0.065 in = 1.65 mm.
      https://www.ati-ia.com/products/compliance/compensator_9115DataSheet.aspx
    * Torsion (about the insertion axis): ATI lists no torsional stiffness, only an
      allowable torsion of 4.5 deg (size 000). Stiffness from PFA AST-75 with MO-30
      pads: 4.5 N mm/mrad = 4.5 N m/rad. https://www.pfa-inc.com/?p=7093
    * Cocking (tilt): ATI 9115-001-A 1600 in-lb/rad = 181 N m/rad. At the cell's
      0.6 N m torque stop that is under 0.2 deg of deflection, so cocking is
      modeled as rigid (it would also need a far smaller physics step).
    """

    lateral_stiffness_n_per_mm: float = 5.78
    lateral_travel_mm: float = 1.65
    torsional_stiffness_nm_per_rad: float = 4.5
    torsional_travel_deg: float = 4.5
    moving_mass_kg: float = 0.010  # gripper share of the 30 g tool, carried by the stage (assumed)
    lateral_armature_kg: float = 0.02  # moving plate of the compliance device (assumed)
    torsional_armature_kgm2: float = 6e-6  # assumed: 30 g plate, 20 mm radius
    damping_ratio: float = 0.3  # elastomer shear pads (assumed)


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
    defect: str | None = None  # deliberately bad part (W3), see defex.sim.mating.DEFECTS
    # What the cell integrator believes the vision accuracy is (handed to controllers).
    # None: the true noise above (correctly characterized, as in V0.1).
    characterized_noise: SensorNoiseConfig | None = None


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
class PassiveComplianceConfig(PositionCorrectionConfig):
    """Controller E: B's program on the passive RCC stage (tuned separately, see BASELINE_TUNING.md)."""

    approach_height_mm: float = 2.0
    insert_speed_mm_s: float = 4.0
    overtravel_mm: float = 1.0


@dataclass(frozen=True)
class SpiralSearchConfig:
    """Controllers D and F: force-controlled spiral search, as shipped in cobot insertion packages.

    Defaults follow Flexiv's Adaptive Assembly primitives (SearchHole, InsertComp),
    the only vendor page found that publishes numeric defaults:
    https://www.flexiv.com/software/primitives/en/3.9/rizon4/Adaptive%20Assembly.html
    SearchHole: contactForce 5 N (range 2-20), spiralRadius up to 0.015 m, hole found
    when pushDistance > 0.005 m. InsertComp: insertVel 0.01 m/s, maxContactForce 5 N.
    Robotiq's FT 300 Insertion node exposes the same spiral inputs (speed, force,
    radius increment per turn, maximum radius) without published defaults:
    https://dof.robotiq.com/discussion/1278. Pitch, speed, force and push distance are
    tuned on the development seed (results/benchmark_v0.2a/BASELINE_TUNING.md).
    Cell force limits are the same as controller C's.
    """

    approach_height_mm: float = 2.5  # above the estimated mouth, plus 3 sigma of vision z (as C)
    transit_speed_mm_s: float = 40.0
    retract_clearance_mm: float = 3.0
    retract_speed_mm_s: float = 15.0
    descent_speed_mm_s: float = 10.0  # Flexiv insertVel default
    force_gain_mm_s_per_n: float = 1.0
    contact_force_n: float = 1.0
    search_force_n: float = 3.0  # tuned; Flexiv SearchHole contactForce default 5 N, range 2-20
    spiral_pitch_mm: float = 1.0  # tuned; radius increment per turn (Robotiq term)
    spiral_speed_mm_s: float = 5.0  # tuned; tangential speed along the spiral
    spiral_max_radius_mm: float = 6.5  # same lateral bound as C's recovery
    hole_push_mm: float = 0.5  # tuned; depth gained below the face that counts as "hole found"
    # Lateral stiffness during the spiral (software spring on the stiff servo); 0 = stiff.
    # Flexiv SearchHole exposes the same choice as searchStiffRatio (0.1-1, default 1).
    search_lateral_stiffness_n_per_mm: float = 0.0
    insert_force_n: float = 8.0  # tuned; Flexiv InsertComp maxContactForce default 5 N
    insert_speed_mm_s: float = 10.0  # Flexiv InsertComp insertVel default
    lateral_compliance_damping_n_s_per_mm: float = 1.0  # force-mode compliant x/y during insertion
    max_lateral_compliance_mm: float = 2.0
    seat_margin_mm: float = 1.0  # declared seated when this close to full depth
    stall_window_s: float = 0.4
    stall_progress_mm: float = 0.15
    max_force_n: float = 20.0
    max_torque_nm: float = 0.35
    max_lateral_force_n: float = 10.0
    max_attempts: int = 2  # tuned; re-descend at the found position after a jam
    time_limit_s: float = 26.0
    tare_settle_s: float = 0.06
    tare_average_s: float = 0.06


@dataclass(frozen=True)
class CompliantSpiralSearchConfig(SpiralSearchConfig):
    """Controller F: D's routine on the RCC stage, tuned separately (BASELINE_TUNING.md)."""

    insert_force_n: float = 3.0
    max_attempts: int = 3


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
    max_insert_speed_mm_s: float = 10.0  # W6 (V0.1: 6.0); see results/w6_development
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
    # Light axial preload held during probing. Floor friction (mu x preload) must stay
    # below verify_force_n, or the floor rather than a wall could stop a probe.
    verify_preload_n: float = 1.0
    verify_probe_speed_mm_s: float = 5.0  # W6 (V0.1: 2.5)
    # Yaw centering inside the cavity (runs when the vision yaw sigma exceeds the gate)
    yaw_center_gate_deg: float = 1.0
    yaw_probe_speed_deg_s: float = 25.0  # W6 (V0.1: 10.0)
    yaw_probe_torque_nm: float = 0.02
    yaw_probe_max_deg: float = 7.0
    # ---- Constants moved out of the controller code in W2. Values are unchanged from
    # V0.1; the basis says where each came from. "dev-tuned" means chosen by hand on
    # development seed 2026 (see the W2 sensitivity sweep for how much each matters).
    # Motion and command limits
    max_back_off_speed_mm_s: float = 4.0  # force loop's maximum retreat speed (dev-tuned)
    free_insert_speed_mm_s: float = 15.0  # descent inside the cavity before contact (dev-tuned)
    near_bottom_speed_mm_s: float = 10.0  # W6 (V0.1: 5.0): slower descent near the floor
    near_bottom_margin_mm: float = 2.0  # "near the floor" starts this far above it, plus 3 sigma
    force_phase_speed_cap_mm_s: float = 30.0  # motion-generator cap while the force loop moves the setpoint
    slow_phase_speed_cap_mm_s: float = 10.0  # cap for yaw probing and terminal holds
    verify_return_speed_factor: float = 2.0  # probe return speed relative to the probe speed
    # Reached-target tolerances (setpoint vs commanded target)
    reach_tol_mm: float = 0.002
    reach_tol_rad: float = 1e-4
    retract_reach_tol_mm: float = 0.005
    retract_reach_tol_rad: float = 2e-3
    probe_reach_tol_mm: float = 0.02
    yaw_reach_tol_rad: float = 2e-4
    # Depth uncertainty bookkeeping (multiples of the depth sigma)
    touch_depth_sigma_mm: float = 0.1  # depth uncertainty after touching the top face (encoder + CoP model)
    approach_sigma_k: float = 3.0
    engage_sigma_k: float = 3.0
    near_bottom_sigma_k: float = 3.0
    mouth_sigma_k: float = 3.0
    seat_sigma_k: float = 2.5  # looser than 3: the bottoming force confirms the seat (dev-tuned)
    # Vision prior for the hole localizer
    min_prior_sigma_mm: float = 0.15  # floor so a perfect camera still leaves a usable prior
    prior_sigma_scale: float = 1.3  # widen the characterized sigma (dev-tuned)
    # Free-space tare before each attempt
    tare_settle_s: float = 0.06
    tare_end_s: float = 0.12
    # Contact detection hysteresis (multiples of contact_force_n)
    contact_on_norm_factor: float = 1.5
    contact_off_axial_factor: float = 0.5
    contact_off_norm_factor: float = 0.75
    # Bottoming detection during INSERT
    bottom_force_fraction: float = 0.8  # of insert_force_n
    bottom_hold_s: float = 0.08
    # DETECT
    excess_diagnosis_samples: int = 10  # samples used when an excess-force stop skips the hold
    recent_samples: int = 25
    surface_conform_delay_s: float = 0.04
    bottomed_hold_s: float = 0.05
    detect_discard_divisor: int = 3  # discard the first third of a window (transient)
    slide_in_depth_mm: float = 0.8  # depth gained during conform that means "slid into the lead-in"
    conform_window_s: float = 0.06
    conform_min_s: float = 0.1
    conform_rate_deg: float = 0.03  # settled when the tilt moved less than this over the window
    conform_saturation_fraction: float = 0.97
    measure_s: float = 0.1
    surface_cop_margin_mm: float = 0.3  # CoP may sit this far outside the plug face (noise)
    surface_lateral_ratio: float = 0.35  # lateral/axial force ratio of a flat face contact
    surface_lateral_offset_n: float = 0.5
    touch_higher_support_mm: float = 0.15  # a support this much higher re-calibrates the mouth
    tilt_fold_cop_mm: float = 0.4  # CoP this close to centre means the plug sat flat
    seat_lateral_ratio: float = 0.6  # deep stall with more side load than this is a jam
    seat_lateral_offset_n: float = 1.0
    # RECOVER
    retract_stuck_force_factor: float = 1.2  # of max_force_n
    retract_stuck_delay_s: float = 0.3
    yaw_search_entry_probability: float = 0.6  # a block where entry was this likely counts toward yaw search
    clean_cop_mm: float = 0.4
    unclean_cop_sigma_mm: float = 1.2  # CoP noise assumed for mixed face/lead-in support
    yaw_search_step_deg: float = 3.0  # yaw search tries +/-step, +/-2 step, ...
    yaw_search_steps: int = 4
    # Hole localizer model
    localizer_outlier_weight: float = 0.1
    localizer_entry_likelihood: float = 0.05
    localizer_band_stick_probability: float = 0.35
    localizer_prior_uniform_weight: float = 0.1  # heavy tail on the vision prior
    localizer_exclude_fraction: float = 0.75  # of the strict clearance, around blocked probes
    localizer_exclude_min_cells: float = 0.6
    localizer_min_support_mm: float = 0.02  # support strips narrower than this do not carry load
    # W4: joint (x, y, yaw) localizer. "xy" is V0.1's 2D filter plus the fixed yaw sequence.
    localizer_mode: str = "xy"  # "xyyaw" available; no measured gain in development (W4 report)
    yaw_localizer_extent_deg: float = 12.0  # hypotheses of true yaw relative to the vision estimate
    yaw_localizer_resolution_deg: float = 1.5
    yaw_prior_scale: float = 1.3  # widen the characterized yaw sigma, as prior_sigma_scale does for x/y
    min_yaw_prior_sigma_deg: float = 0.5
    probe_xy_step_mm: float = 0.5  # coarse probe search grid, refined to half the step
    probe_yaw_step_deg: float = 1.5
    exclude_yaw_deg: float = 1.0  # a blocked pose excludes probes within this yaw (and the x/y radius)
    # Re-centre yaw in VERIFY whenever the controller itself changed the yaw by more than this
    # (the replication-seed escape: a yaw search left the plug 3.4 deg off and centring was skipped).
    yaw_center_if_corrected_deg: float = 0.5
    # When VERIFY re-centres yaw between the rotational limits:
    # "sigma_gate" (V0.1): only if the characterized vision yaw sigma exceeds yaw_center_gate_deg;
    # "gate_or_corrected": also if C changed the yaw itself; "always": every cycle.
    yaw_center_policy: str = "always"  # W4 default; V0.1 used "sigma_gate" (see results/w4_development)
    rotation_budget_fraction: float = 0.8  # of max_torque_nm, for torque overshoot while probing yaw (W5)
    # W3 push-click-pull verification for latching connectors
    click_drop_fraction: float = 0.4  # force drop at the snap, as a fraction of the latch peak force
    click_window_after_snap_mm: float = 0.2  # search the trace this far past the expected snap
    pull_test_fraction: float = 0.5  # guarded pull at this fraction of the rated retention force
    pull_test_margin_mm: float = 0.3  # allowed movement beyond the post-snap stroke
    pull_test_max_s: float = 3.0
    reseat_tolerance_mm: float = 0.05  # after the pull, back within this of the depth it bottomed at
    # VERIFY
    verify_probe_margin_mm: float = 0.35  # probe travel beyond 2 x clearance
    seat_conform_min_s: float = 0.08
    seat_conform_max_s: float = 0.8
    preload_tolerance_n: float = 0.2
    preload_min_s: float = 0.1
    preload_settle_s: float = 0.05
    preload_max_s: float = 0.8


@dataclass(frozen=True)
class LearnedPriorConfig:
    """W9 controller G: C plus a learned contact prior in the hole localizer."""

    # Weight of the learned log-likelihood term. None: the weight stored with the model,
    # chosen on validation seed 4001 (results/w9_development); 0 switches the term off.
    weight: float | None = None
    # A model applies only when each stored fixture-dynamics value matches the running
    # fixture within this relative tolerance (gantry and UR5e differ by 2x to 30x).
    fixture_match_rel_tol: float = 0.01
    # Uniform floor mixed into the learned Gaussian term, as C's CoP likelihood does
    # (AdaptiveConfig.localizer_outlier_weight, same value, not tuned). Added because the
    # model's errors are heavy-tailed on validation: 5-6% of contacts beyond 3 sigma (2D
    # Gaussian: 1.1%), from mirror-ambiguous contacts a single Gaussian cannot represent.
    outlier_weight: float = 0.1


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
    "CompliantSpiralSearchConfig",
    "CompliantStageConfig",
    "Condition",
    "ConnectorSpec",
    "DEG",
    "DisturbanceSpec",
    "FixedTrajectoryConfig",
    "FixtureConfig",
    "LearnedPriorConfig",
    "MM",
    "PlugGeometry",
    "PassiveComplianceConfig",
    "PositionCorrectionConfig",
    "SpiralSearchConfig",
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
