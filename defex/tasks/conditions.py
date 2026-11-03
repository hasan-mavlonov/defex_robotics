"""Standard experiment conditions for the DAIE V0.1 benchmark."""

from __future__ import annotations

from dataclasses import replace

from defex.config import Condition, DisturbanceSpec, PartSpread, SensorNoiseConfig

NOMINAL_NOISE = SensorNoiseConfig()

# Moderate randomized disturbance used as the backdrop for the noise and friction sweeps.
MODERATE = DisturbanceSpec(
    lateral_mm=3.0, lateral_mode="uniform", yaw_deg=5.0, yaw_mode="uniform", tilt_deg=3.0, tilt_mode="uniform"
)


def standard_conditions() -> list[Condition]:
    conds: list[Condition] = [
        Condition("nominal", "nominal", DisturbanceSpec(), NOMINAL_NOISE, description="Correctly aligned socket"),
    ]
    for mm in (1.0, 3.0, 5.0):
        conds.append(
            Condition(
                f"lateral_{mm:g}mm",
                "lateral",
                DisturbanceSpec(lateral_mm=mm, lateral_mode="fixed"),
                NOMINAL_NOISE,
                description=f"Socket displaced {mm:g} mm in a random horizontal direction",
            )
        )
    for deg in (2.0, 5.0, 10.0):
        conds.append(
            Condition(
                f"yaw_{deg:g}deg",
                "angular_yaw",
                DisturbanceSpec(yaw_deg=deg, yaw_mode="fixed"),
                NOMINAL_NOISE,
                description=f"Socket rotated +/-{deg:g} deg about its insertion axis",
            )
        )
    for deg in (2.0, 5.0, 10.0):
        conds.append(
            Condition(
                f"tilt_{deg:g}deg",
                "angular_tilt",
                DisturbanceSpec(tilt_deg=deg, tilt_mode="fixed"),
                NOMINAL_NOISE,
                description=f"Socket axis tilted {deg:g} deg about a random horizontal axis",
            )
        )
    for sigma in (0.0, 0.5, 1.0, 2.0):
        conds.append(
            Condition(
                f"noise_{sigma:g}mm",
                "pose_uncertainty",
                MODERATE,
                NOMINAL_NOISE.scaled_vision(sigma),
                description=(
                    f"Moderate disturbance, vision sigma {sigma:g} mm "
                    f"(z {0.3 * sigma / 0.3:g} mm, yaw {0.5 * sigma / 0.3:.2g} deg, tilt {0.3 * sigma / 0.3:.2g} deg)"
                ),
            )
        )
    for mu in (0.1, 0.3, 0.6, 1.0):
        conds.append(
            Condition(
                f"friction_{mu:g}",
                "contact_variation",
                MODERATE,
                NOMINAL_NOISE,
                friction=mu,
                description=f"Moderate disturbance, friction coefficient {mu:g}",
            )
        )
    conds.append(
        Condition(
            "generalization_combined",
            "generalization",
            DisturbanceSpec(
                lateral_mm=5.0,
                lateral_mode="uniform",
                yaw_deg=10.0,
                yaw_mode="uniform",
                tilt_deg=8.0,
                tilt_mode="uniform",
                height_mm=1.0,
                grasp_lateral_mm=1.0,
                grasp_axial_mm=1.0,
                grasp_tilt_deg=3.0,
            ),
            replace(NOMINAL_NOISE.scaled_vision(0.8), vision_bias_mm=0.8),
            friction=0.5,
            description=(
                "Unseen combination: socket pose, height, in-hand grasp error, 0.8 mm vision noise, "
                "0.8 mm hand-eye calibration bias, friction 0.5"
            ),
        )
    )
    conds.append(
        Condition(
            "generalization_tight",
            "generalization",
            DisturbanceSpec(
                lateral_mm=3.0, lateral_mode="uniform", yaw_deg=6.0, yaw_mode="uniform", tilt_deg=4.0, tilt_mode="uniform"
            ),
            NOMINAL_NOISE.scaled_vision(0.5),
            clearance_mm=0.2,
            chamfer_mm=0.5,
            description="Unseen geometry: 0.2 mm clearance, 0.5 mm lead-in, 0.5 mm vision noise",
        )
    )
    return conds


def conditions_by_name() -> dict[str, Condition]:
    return {c.name: c for c in standard_conditions()}


# --------------------------------------------------------------------------------------
# W2 held-out families. Defined and pre-registered before any run; never used for
# development or tuning. Not part of standard_conditions(), so no tuning script can
# reach them by accident.
# --------------------------------------------------------------------------------------

TOLD_HALF_MM = NOMINAL_NOISE.scaled_vision(0.5)  # what the integrator believes: 0.5 mm class camera


def heldout_conditions() -> list[Condition]:
    return [
        Condition(
            "heldout_mischar_1mm",
            "heldout_vision",
            MODERATE,
            NOMINAL_NOISE.scaled_vision(1.0),
            characterized_noise=TOLD_HALF_MM,
            description="Controllers told vision sigma 0.5 mm; true sigma 1.0 mm (z, yaw, tilt scaled alike)",
        ),
        Condition(
            "heldout_mischar_2mm",
            "heldout_vision",
            MODERATE,
            NOMINAL_NOISE.scaled_vision(2.0),
            characterized_noise=TOLD_HALF_MM,
            description="Controllers told vision sigma 0.5 mm; true sigma 2.0 mm",
        ),
        Condition(
            "heldout_handeye_bias_1.5mm",
            "heldout_vision",
            MODERATE,
            replace(NOMINAL_NOISE, vision_bias_mm=1.5),
            characterized_noise=NOMINAL_NOISE,
            description="Unknown 1.5 mm hand-eye calibration bias (random direction); controllers told no bias",
        ),
        Condition(
            "heldout_vision_outliers",
            "heldout_vision",
            MODERATE,
            replace(NOMINAL_NOISE, vision_outlier_probability=0.05),
            characterized_noise=NOMINAL_NOISE,
            description="5% of vision shots off by 3-6 mm; controllers told the nominal accuracy",
        ),
        Condition(
            "heldout_worst_case",
            "heldout_combined",
            MODERATE,
            NOMINAL_NOISE.scaled_vision(1.0),
            friction=0.8,
            clearance_mm=0.2,
            characterized_noise=TOLD_HALF_MM,
            description="Friction 0.8, 0.2 mm clearance, told 0.5 mm vision sigma but true 1.0 mm",
        ),
    ]


def heldout_conditions_by_name() -> dict[str, Condition]:
    return {c.name: c for c in heldout_conditions()}


# --------------------------------------------------------------------------------------
# W3 latching connector (Molex Micro-Fit 3.0, 4 circuits): good parts and deliberately
# bad parts. Controllers are never told about a defect.
# --------------------------------------------------------------------------------------

LATCHING_CONNECTOR = "microfit3_4ckt"


def latching_conditions() -> list[Condition]:
    good = [
        Condition("mf_nominal", "latching", DisturbanceSpec(), NOMINAL_NOISE, connector=LATCHING_CONNECTOR,
                  description="Micro-Fit 3.0, aligned socket"),
        Condition("mf_moderate", "latching", MODERATE, NOMINAL_NOISE, connector=LATCHING_CONNECTOR,
                  description="Micro-Fit 3.0, socket up to 3 mm / 5 deg yaw / 3 deg tilt off, nominal vision"),
        Condition("mf_noise_1mm", "latching", MODERATE, NOMINAL_NOISE.scaled_vision(1.0), connector=LATCHING_CONNECTOR,
                  description="Micro-Fit 3.0, moderate disturbance, 1 mm vision sigma"),
    ]
    bad = [
        Condition(f"mf_{d}", "bad_part", MODERATE, NOMINAL_NOISE, connector=LATCHING_CONNECTOR, defect=d,
                  description=f"Micro-Fit 3.0 with a deliberately bad part: {d.replace('_', ' ')}")
        for d in ("half_latched", "broken_latch", "stubbed_terminal", "wrong_polarization")
    ]
    return good + bad


def latching_conditions_by_name() -> dict[str, Condition]:
    return {c.name: c for c in latching_conditions()}


# --------------------------------------------------------------------------------------
# v0.2c review: part-to-part spread of the Micro-Fit mating values (simulator side). The
# model's latch geometry and 6 N latch peak are assumed (no value is published) and its
# terminal forces sit inside the datasheet range, so a controller tuned on the nominal part
# may depend on those exact values. Ranges: latch position +/-0.2 mm, latch peak +/-50%,
# terminal forces from the datasheet unmating minimum (2.4 N / 3 N slide = 0.8 x) to the
# datasheet mating maximum (8 N / 5 N peak = 1.6 x). Controllers are told nothing.
# --------------------------------------------------------------------------------------

LATCH_SPREAD = PartSpread(latch_shift_mm=(-0.2, 0.2), latch_peak_scale=(0.5, 1.5), terminal_scale=(0.8, 1.6))


def latch_spread_conditions() -> list[Condition]:
    def one(name, spread, description, defect=None):
        return Condition(name, "bad_part" if defect else "latch_spread", MODERATE, NOMINAL_NOISE,
                         connector=LATCHING_CONNECTOR, defect=defect, part_spread=spread, description=description)

    return [
        one("mf_spread", LATCH_SPREAD, "Micro-Fit 3.0, moderate disturbance, every mating value drawn from its range"),
        one("mf_latch_early", PartSpread(latch_shift_mm=(-0.2, -0.2)), "latch 0.2 mm shallower than the model"),
        one("mf_latch_late", PartSpread(latch_shift_mm=(0.2, 0.2)), "latch 0.2 mm deeper than the model"),
        one("mf_latch_weak", PartSpread(latch_peak_scale=(0.5, 0.5)), "latch peak force 0.5 x the model's"),
        one("mf_terminal_max", PartSpread(terminal_scale=(1.6, 1.6)), "terminal forces at the datasheet maximum"),
        one("mf_terminal_min", PartSpread(terminal_scale=(0.8, 0.8)), "terminal slide at the datasheet minimum"),
        one("mf_spread_half_latched", LATCH_SPREAD, "bad part, half latched, mating values drawn", "half_latched"),
        one("mf_spread_broken_latch", LATCH_SPREAD, "bad part, broken latch, mating values drawn", "broken_latch"),
        one("mf_terminal_max_broken_latch", PartSpread(terminal_scale=(1.6, 1.6)),
            "bad part, broken latch, terminal forces at the datasheet maximum", "broken_latch"),
    ]


# --------------------------------------------------------------------------------------
# v0.2f held-out families (heldout2). Defined before any run of them, for a clean
# out-of-sample test of the frozen v0.2e code (the W2 `heldout` families were used in W4
# development). Each family is an error a real cell sees that no sensor reports and no
# controller is told; all are new to every earlier suite. Bases and levels:
# results/heldout2_v0.2f/PREREGISTRATION.md. Never used for development or tuning.
# --------------------------------------------------------------------------------------

HELDOUT2_FAMILIES = ("h2_tilt_unseen", "h2_yaw_unseen", "h2_ft_drift", "h2_mf_tolerance", "h2_mf_grasp_unseen")


def heldout2_conditions() -> list[Condition]:
    conds: list[Condition] = []
    for deg in (2.0, 3.0):
        conds.append(Condition(
            f"h2_tilt_unseen_{deg:g}deg", "h2_tilt_unseen", replace(MODERATE, unseen_tilt_deg=deg), NOMINAL_NOISE,
            characterized_noise=NOMINAL_NOISE,
            description=f"Receptacle tilted {deg:g} deg on its board (random axis); the camera does not see it"))
    for deg in (2.5, 4.0):
        conds.append(Condition(
            f"h2_yaw_unseen_{deg:g}deg", "h2_yaw_unseen", replace(MODERATE, unseen_yaw_deg=deg), NOMINAL_NOISE,
            characterized_noise=NOMINAL_NOISE,
            description=f"Receptacle rotated {deg:g} deg about its axis (random sign); the camera does not see it"))
    for rate in (0.1, 0.3):
        conds.append(Condition(
            f"h2_ft_drift_{rate:g}", "h2_ft_drift", MODERATE,
            replace(NOMINAL_NOISE, ft_drift_force_n_per_s=rate, ft_drift_torque_nm_per_s=rate * 0.01),
            characterized_noise=NOMINAL_NOISE,
            description=f"F/T zero drifts {rate:g} N/s and {rate * 0.01:g} N m/s after the tare (random directions)"))
    for clearance, chamfer in ((0.10, 0.3), (0.05, 0.2)):
        conds.append(Condition(
            f"h2_mf_tol_{clearance:.2f}mm", "h2_mf_tolerance", MODERATE, NOMINAL_NOISE, connector=LATCHING_CONNECTOR,
            actual_clearance_mm=clearance, actual_chamfer_mm=chamfer,
            description=(f"Micro-Fit 3.0 at a tight tolerance stack: clearance {clearance:.2f} mm, lead-in "
                         f"{chamfer:g} mm (controllers told the drawing, 0.15 mm and 0.4 mm)")))
    for lat, tilt in ((0.2, 1.0), (0.4, 2.0)):
        conds.append(Condition(
            f"h2_mf_grasp_unseen_{tilt:g}deg", "h2_mf_grasp_unseen",
            replace(MODERATE, grasp_unseen_lateral_mm=lat, grasp_unseen_tilt_deg=tilt), NOMINAL_NOISE,
            connector=LATCHING_CONNECTOR, characterized_noise=NOMINAL_NOISE,
            description=(f"Micro-Fit 3.0 sits {lat:g} mm off along y and {tilt:g} deg about x in the fingers; "
                         f"the in-hand estimate does not see it")))
    return conds


def heldout2_conditions_by_name() -> dict[str, Condition]:
    return {c.name: c for c in heldout2_conditions()}
