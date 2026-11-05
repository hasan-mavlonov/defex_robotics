"""heldout2 F/T-drift family before and after the drift-stream fix, with heldout2_tables' rules.

    PYTHONPATH=. python -m experiments.v02g_drift_stream_compare > results/v0.2g_drift_stream_fix/TABLES.md

Before: the h2_ft_drift rows of results/heldout2_v0.2f (commit 6ea164e). After: results/v0.2g_drift_stream_fix
(the same command restricted to the drift conditions, with the drift drawn from its own stream).
"""

from __future__ import annotations

import contextlib
import csv
import io
import tempfile
from pathlib import Path

from experiments import heldout2_tables

BEFORE = Path("results/heldout2_v0.2f")
AFTER = Path("results/v0.2g_drift_stream_fix")


def stage(tmp: Path, label: str) -> Path:
    for machine in ("gantry", "arm"):
        src = (BEFORE / f"{machine}_heldout2" if label == "before" else AFTER / f"{machine}_drift") / "trials.csv"
        with open(src, newline="") as f:
            rows = [r for r in csv.DictReader(f) if r["condition"].startswith("h2_ft_drift")]
        dst = tmp / label / f"{machine}_heldout2"
        dst.mkdir(parents=True)
        with open(dst / "trials.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    return tmp / label


def tables(run: Path) -> list[str]:
    import sys

    buf = io.StringIO()
    argv, sys.argv = sys.argv, ["heldout2_tables", str(run)]
    try:
        with contextlib.redirect_stdout(buf):
            heldout2_tables.main()
    finally:
        sys.argv = argv
    return [ln for ln in buf.getvalue().splitlines() if "h2_ft_drift" in ln and "all families" not in ln
            or ln.startswith("## (") or ln.startswith("| Machine")]


def main() -> None:
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        out = ["# heldout2 F/T drift family: before and after the drift-stream fix", "",
               "Rules and columns are heldout2_tables'. Each machine: 2 conditions x 40 trials x 10 controllers, "
               "seed 20261207. Before = heldout2_v0.2f (6ea164e); after = this folder (c3f967a).", ""]
        for label in ("before", "after"):
            out += [f"# {label}", ""] + tables(stage(tmp, label)) + [""]
    print("\n".join(out))


if __name__ == "__main__":
    main()
