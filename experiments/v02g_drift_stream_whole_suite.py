"""heldout2 whole-suite rule outcomes with the drift rows replaced by the drift-stream-fix rerun.

    PYTHONPATH=. python -m experiments.v02g_drift_stream_whole_suite > results/v0.2g_drift_stream_fix/WHOLE_SUITE.md
"""

from __future__ import annotations

import csv
import io
import contextlib
import sys
import tempfile
from pathlib import Path

from experiments import heldout2_tables


def main() -> None:
    with tempfile.TemporaryDirectory() as t:
        out = ["# heldout2 whole suite, original rows vs drift rows replaced", ""]
        for label in ("original", "drift replaced"):
            run = Path(t) / label.replace(" ", "_")
            for m in ("gantry", "arm"):
                with open(f"results/heldout2_v0.2f/{m}_heldout2/trials.csv", newline="") as f:
                    rows = list(csv.DictReader(f))
                if label != "original":
                    with open(f"results/v0.2g_drift_stream_fix/{m}_drift/trials.csv", newline="") as f:
                        new = list(csv.DictReader(f))
                    rows = [r for r in rows if not r["condition"].startswith("h2_ft_drift")] + new
                d = run / f"{m}_heldout2"
                d.mkdir(parents=True)
                with open(d / "trials.csv", "w", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=list(rows[0]), extrasaction="ignore")
                    w.writeheader()
                    w.writerows(rows)
            buf = io.StringIO()
            argv, sys.argv = sys.argv, ["x", str(run)]
            try:
                with contextlib.redirect_stdout(buf):
                    heldout2_tables.main()
            finally:
                sys.argv = argv
            out += [f"## {label}", ""] + [ln for ln in buf.getvalue().splitlines()
                                          if "all families" in ln and "| C vs best" in ln or "all families | J vs" in ln
                                          or "all families | C vs H" in ln or "all families | C vs I" in ln] + [""]
    print("\n".join(out))


if __name__ == "__main__":
    main()
