"""Controller registry: build controllers by short name."""

from __future__ import annotations

import json
import os
from dataclasses import replace
from pathlib import Path
from typing import Callable

from defex.control.adaptive_fsm import AdaptiveInsertionController
from defex.control.adaptive_learned import AdaptiveLearnedController
from defex.control.base import InsertionController
from defex.control.baselines import FixedTrajectoryController, PassiveComplianceController, PositionCorrectionController
from defex.control.spiral_search import (
    CompliantSpiralSearchController,
    CompliantSpiralSearchPullController,
    SpiralSearchController,
    SpiralSearchPullController,
)
from defex.control.spiral_verify import (
    CompliantSpiralSearchVerifyController,
    CompliantSpiralSearchVerifyRejectController,
    CompliantSpiralSearchVerifyRejectNoRCCController,
    CompliantSpiralSearchVerifyResearchController,
)

CONTROLLERS: dict[str, Callable[[], InsertionController]] = {
    "fixed": FixedTrajectoryController,
    "correction": PositionCorrectionController,
    "adaptive": AdaptiveInsertionController,
    "spiral": SpiralSearchController,
    "correction_rcc": PassiveComplianceController,
    "spiral_rcc": CompliantSpiralSearchController,
    "adaptive_learned": AdaptiveLearnedController,  # W9: C + learned contact prior (opt-in)
    "spiral_pull": SpiralSearchPullController,  # v0.2c: H = D + C's retention pull
    "spiral_rcc_pull": CompliantSpiralSearchPullController,  # v0.2c: I = F + C's retention pull
    # v0.2d: J = F + C's VERIFY, re-search after a failed check (SELECTION_RULE.md); its candidates (a) and (b),
    # and (a) without the RCC terms
    "spiral_rcc_verify": CompliantSpiralSearchVerifyController,
    "spiral_rcc_verify_reject": CompliantSpiralSearchVerifyRejectController,
    "spiral_rcc_verify_research": CompliantSpiralSearchVerifyResearchController,
    "spiral_rcc_verify_reject_no_rcc": CompliantSpiralSearchVerifyRejectNoRCCController,
}

# The benchmark cells A-F. Scripts that run "every controller" by default use this, so
# registering G (W9) does not change what an unqualified benchmark run contains.
BENCHMARK_CONTROLLERS = ("fixed", "correction", "adaptive", "spiral", "correction_rcc", "spiral_rcc")

LABELS = {
    "fixed": "A: Fixed trajectory",
    "correction": "B: Vision position correction",
    "adaptive": "C: Defex adaptive (DAIE)",
    "spiral": "D: Spiral search",
    "correction_rcc": "E: Vision correction + passive compliance",
    "spiral_rcc": "F: Spiral search + passive compliance",
    "adaptive_learned": "G: Defex adaptive + learned contact prior",
    "spiral_pull": "H: Spiral search + retention pull",
    "spiral_rcc_pull": "I: Spiral search + passive compliance + retention pull",
    "spiral_rcc_verify": CompliantSpiralSearchVerifyController.label,
    "spiral_rcc_verify_reject": CompliantSpiralSearchVerifyRejectController.label,
    "spiral_rcc_verify_research": CompliantSpiralSearchVerifyResearchController.label,
    "spiral_rcc_verify_reject_no_rcc": CompliantSpiralSearchVerifyRejectNoRCCController.label,
}

COLORS = {
    "fixed": "#9aa0a6",
    "correction": "#4a7fd4",
    "adaptive": "#f2761d",
    "spiral": "#2e9e6b",
    "correction_rcc": "#8a63c9",
    "spiral_rcc": "#c94f6d",
    "adaptive_learned": "#705010",
    "spiral_pull": "#1f6b48",
    "spiral_rcc_pull": "#8c2f47",
    "spiral_rcc_verify": "#b5651d",
    "spiral_rcc_verify_reject": "#d98c3a",
    "spiral_rcc_verify_research": "#b5651d",
    "spiral_rcc_verify_reject_no_rcc": "#c9b38f",
}


def make_controller(name: str) -> InsertionController:
    """``name`` or, for development comparisons, ``name@variant``: config overrides for ``variant`` come
    from the JSON file named by the environment variable DEFEX_CONTROLLER_VARIANTS ({variant: {field: value}}).
    For D, E and F the overrides apply to both the gantry config and the arm's stiff_fixture_cfg."""
    base, _, variant = name.partition("@")
    try:
        ctrl = CONTROLLERS[base]()
    except KeyError as exc:
        raise ValueError(f"unknown controller '{name}', choose from {sorted(CONTROLLERS)}") from exc
    if variant:
        path = os.environ.get("DEFEX_CONTROLLER_VARIANTS")
        if not path:
            raise ValueError(f"'{name}': set DEFEX_CONTROLLER_VARIANTS to a variants JSON file")
        overrides = json.loads(Path(path).read_text())[variant]
        ctrl.cfg = replace(ctrl.cfg, **overrides)
        if hasattr(ctrl, "stiff_fixture_cfg"):
            # D, E and F run stiff_fixture_cfg on the arm (v0.2c): the variant applies on every machine.
            ctrl.stiff_fixture_cfg = replace(ctrl.stiff_fixture_cfg, **overrides)
        if hasattr(ctrl, "dwell_s"):
            ctrl.dwell_s = ctrl.cfg.dwell_s  # A and B copy it at construction
        ctrl.name = name
    return ctrl
