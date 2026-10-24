"""Standard experiment conditions for the DAIE V0.1 benchmark."""

from __future__ import annotations

from dataclasses import replace

from defex.config import Condition, DisturbanceSpec, SensorNoiseConfig

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
