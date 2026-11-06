"""v0.2f: flags-off rows against the v0.2e code (4df8cae). python experiments/v02f_identity.py <v0.2e runs> <branch runs>"""
import csv, sys
from pathlib import Path
BASE = Path(sys.argv[1])
BR = Path(sys.argv[2])
tot = fields = diffs = 0
lines = ["| Run | Trials | Fields compared | Differences |", "|---|---|---|---|"]
for b in ("arm", "gantry"):
    for s in ("latching", "standard"):
        a = list(csv.DictReader(open(BASE / f"v02e_{b}_{s}" / "trials.csv")))
        c = list(csv.DictReader(open(BR / f"branch_{b}_{s}" / "trials.csv")))
        key = lambda r: (r["controller"], r["condition"], r["trial_index"])
        A = {key(r): r for r in a}; C = {key(r): r for r in c}
        assert A.keys() == C.keys()
        n = d = 0
        for k in A:
            for f in A[k]:
                if f == "wall_time_s": continue
                n += 1; d += A[k][f] != C[k][f]
        tot += len(A); fields += n; diffs += d
        lines.append(f"| {b} {s} | {len(A)} | {n} | {d} |")
lines.append(f"| all | {tot} | {fields} | {diffs} |")
print("\n".join(lines))
