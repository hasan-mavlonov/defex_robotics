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
from defex.control.spiral_search import CompliantSpiralSearchController, SpiralSearchController

CONTROLLERS: dict[str, Callable[[], InsertionController]] = {
    "fixed": FixedTrajectoryController,
    "correction": PositionCorrectionController,
    "adaptive": AdaptiveInsertionController,
    "spiral": SpiralSearchController,
    "correction_rcc": PassiveComplianceController,
    "spiral_rcc": CompliantSpiralSearchController,
    "adaptive_learned": AdaptiveLearnedController,  # W9: C + learned contact prior (opt-in)
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
}

COLORS = {
    "fixed": "#9aa0a6",
    "correction": "#4a7fd4",
    "adaptive": "#f2761d",
    "spiral": "#2e9e6b",
    "correction_rcc": "#8a63c9",
    "spiral_rcc": "#c94f6d",
    "adaptive_learned": "#705010",
}


def make_controller(name: str) -> InsertionController:
    """``name`` or, for development comparisons, ``name@variant``: config overrides for ``variant`` come
    from the JSON file named by the environment variable DEFEX_CONTROLLER_VARIANTS ({variant: {field: value}})."""
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
        ctrl.name = name
    return ctrl
