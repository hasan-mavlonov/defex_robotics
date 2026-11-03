import csv, sys
from pathlib import Path
old_root, new_root = Path(sys.argv[1]), Path(sys.argv[2])
tot_rows = tot_fields = tot_diff = 0
for cell in sys.argv[3].split(","):
    key = lambda r: (r["condition"], r["controller"], r["trial_index"])
    old = {key(r): r for r in csv.DictReader(open(old_root / cell / "trials.csv"))}
    new = {key(r): r for r in csv.DictReader(open(new_root / cell / "trials.csv"))}
    first = {k: r for k, r in new.items() if int(k[2]) < 50}
    assert set(first) == set(old), (cell, len(first), len(old))
    diffs = [(k, f, old[k][f], first[k][f]) for k in old for f in old[k] if f != "wall_time_s" and old[k][f] != first[k][f]]
    nf = sum(len(r) - 1 for r in old.values())
    print(f"{cell}: rows {len(old)} (new total {len(new)}), fields compared {nf}, differences {len(diffs)}")
    for d in diffs[:5]: print("  ", d)
    tot_rows += len(old); tot_fields += nf; tot_diff += len(diffs)
print(f"total: {tot_rows} rows, {tot_fields} fields, {tot_diff} differences (wall_time_s excluded)")
