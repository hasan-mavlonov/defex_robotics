"""C and the current G (v1) on dev seed 2026 in this branch against the committed Checkpoint 2 runs.

    python results/v0.2c_learned_prior/compare_dev_vs_cp2.py gantry|arm
Rows matched on (condition, trial_index, seed); every field except controller and wall_time_s compared.
"""
import csv
import sys
from pathlib import Path

B = sys.argv[1]
mine = Path(f"results/v0.2c_learned_prior/dev2026/{B}/trials.csv")
ref = ([Path("results/checkpoint2_prep/gantry_g_recheck/standard/trials.csv"),
        Path("results/checkpoint2_prep/gantry_g_recheck/latching/trials.csv")] if B == "gantry" else
       [Path("results/checkpoint2_prep/arm_prior/dev2026/standard/trials.csv"),
        Path("results/checkpoint2_prep/arm_prior/dev2026/latching/trials.csv")])


def load(paths, ctl):
    out = {}
    for p in paths:
        for r in csv.DictReader(p.open()):
            if r["controller"] == ctl:
                out[(r["condition"], r["trial_index"], r["seed"])] = r
    return out


for a, b in (("adaptive", "adaptive"), ("adaptive_learned", "g_v1")):
    R, M = load(ref, a), load([mine], b)
    keys = sorted(R.keys() & M.keys())
    fields = [f for f in next(iter(R.values())) if f not in ("controller", "wall_time_s")]
    diff = [k for k in keys if any(R[k][f] != M[k][f] for f in fields)]
    print(f"{B} {a} (Checkpoint 2) vs {b} (v0.2c): {len(keys)} trials, {len(keys) * len(fields)} fields, "
          f"{len(diff)} trials differ")
