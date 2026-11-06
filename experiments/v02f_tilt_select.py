"""v0.2f tilt diagnosis: trials for the P re-run shortcut (results/v0.2f_tilt_diagnosis/RULE.md).

    python experiments/v02f_tilt_select.py runs/arm_latch_cg.jsonl.gz --controls 40 > runs/P_arm_trials.json

Every trial with a latch check whose window is under the force floor or empty, plus a fixed control set of
trials without one (the first ``--controls`` in key order after a seeded shuffle, numpy seed 0).
"""

from __future__ import annotations

import argparse
import gzip
import json

import numpy as np


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths")
    ap.add_argument("--controls", type=int, default=40)
    args = ap.parse_args()
    act, rest = [], []
    for p in args.paths.split(","):
        with gzip.open(p, "rt") as fh:
            for line in fh:
                r = json.loads(line)
                k = [r["suite"], r["condition"], r["controller"], r["base_seed"], r["trial_index"]]
                low = any(c["f_ax"] is None or c["f_ax"] < c["floor"] for c in r["checks"])
                (act if low else rest).append(k)
    rest.sort()
    idx = np.random.default_rng(0).permutation(len(rest))[:args.controls]
    print(json.dumps(act + [rest[i] for i in sorted(idx)]))


if __name__ == "__main__":
    main()
