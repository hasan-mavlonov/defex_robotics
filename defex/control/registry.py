"""Controller registry: build controllers by short name."""

from __future__ import annotations

from typing import Callable

from defex.control.adaptive_fsm import AdaptiveInsertionController
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
}

LABELS = {
    "fixed": "A: Fixed trajectory",
    "correction": "B: Vision position correction",
    "adaptive": "C: Defex adaptive (DAIE)",
    "spiral": "D: Spiral search",
    "correction_rcc": "E: Vision correction + passive compliance",
    "spiral_rcc": "F: Spiral search + passive compliance",
}

COLORS = {
    "fixed": "#9aa0a6",
    "correction": "#4a7fd4",
    "adaptive": "#f2761d",
    "spiral": "#2e9e6b",
    "correction_rcc": "#8a63c9",
    "spiral_rcc": "#c94f6d",
}


def make_controller(name: str) -> InsertionController:
    try:
        return CONTROLLERS[name]()
    except KeyError as exc:
        raise ValueError(f"unknown controller '{name}', choose from {sorted(CONTROLLERS)}") from exc
