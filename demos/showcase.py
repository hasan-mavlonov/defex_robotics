"""Pick a representative benchmark trial for demonstrations.

The showcase is an actual benchmark trial (same condition, index and seed), so the
video reproduces it exactly instead of staging a scene. Selection criteria:
the fixed program fails (protective stop), vision correction alone also fails,
and the adaptive controller succeeds after 1-3 observation-driven recoveries.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from demos.common import REPO

DEFAULT_RESULTS = REPO / "results" / "benchmark_v0.1"
CANDIDATE_CONDITIONS = ("noise_2mm", "generalization_combined", "noise_1mm")


@dataclass(frozen=True)
class Showcase:
    condition: str
    trial_index: int
    base_seed: int
    note: str = ""


FALLBACK = Showcase("noise_2mm", 3, 2026, "fallback (no benchmark results found)")


def _base_seed(results_dir: Path) -> int:
    import json

    return int(json.loads((results_dir / "config.json").read_text())["base_seed"])


def find_showcase(results_dir: Path = DEFAULT_RESULTS) -> Showcase:
    trials = results_dir / "trials.csv"
    if not trials.exists():
        return FALLBACK
    rows: dict[tuple[str, int], dict[str, dict]] = {}
    with trials.open() as fh:
        for r in csv.DictReader(fh):
            rows.setdefault((r["condition"], int(r["trial_index"])), {})[r["controller"]] = r
    best = None
    for cond in CANDIDATE_CONDITIONS:
        for (c, i), by in sorted(rows.items(), key=lambda kv: kv[0][1]):
            if c != cond or len(by) < 3:
                continue
            a, b, ad = by["fixed"], by["correction"], by["adaptive"]
            lateral = abs(float(a.get("dist_lateral_mm", 0.0) or 0.0))
            ok = (
                a["failure_reason"] == "protective_stop"
                and b["success"] == "False"
                and ad["success"] == "True"
                and 1 <= int(ad["retries"]) <= 3
                and float(ad["cycle_time_s"]) < 16.0
                and lateral > 1.5
            )
            if ok:
                score = (int(ad["retries"]) != 2, float(ad["cycle_time_s"]))
                if best is None or score < best[0]:
                    best = (score, Showcase(c, i, _base_seed(results_dir), "selected from benchmark results"))
        if best is not None:
            return best[1]
    return FALLBACK
