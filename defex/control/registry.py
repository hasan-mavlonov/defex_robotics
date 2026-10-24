"""Controller registry: build controllers by short name."""

from __future__ import annotations

from typing import Callable

from defex.control.adaptive_fsm import AdaptiveInsertionController
from defex.control.base import InsertionController
from defex.control.baselines import FixedTrajectoryController, PositionCorrectionController

CONTROLLERS: dict[str, Callable[[], InsertionController]] = {
    "fixed": FixedTrajectoryController,
    "correction": PositionCorrectionController,
    "adaptive": AdaptiveInsertionController,
}

LABELS = {
    "fixed": "A: Fixed trajectory",
    "correction": "B: Vision position correction",
    "adaptive": "C: Defex adaptive (DAIE)",
}

COLORS = {"fixed": "#9aa0a6", "correction": "#4a7fd4", "adaptive": "#f2761d"}


def make_controller(name: str) -> InsertionController:
    try:
        return CONTROLLERS[name]()
    except KeyError as exc:
        raise ValueError(f"unknown controller '{name}', choose from {sorted(CONTROLLERS)}") from exc
