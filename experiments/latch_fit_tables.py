"""Markdown tables from results/v0.2f_latch_fit/recovery.csv and summary.json."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from experiments.latch_fit_recovery import JUDGED


def main(folder: str = "results/v0.2f_latch_fit") -> None:
    out = Path(folder)
    rows = list(csv.DictReader((out / "recovery.csv").open()))
    s = json.loads((out / "summary.json").read_text())
    designs = list(s["verdict"])
    print("## main design: recovery per parameter\n")
    print("| parameter | truth (nominal) | nominal error | tolerance (nominal) | off-nominal within | "
          "worst abs error, all 11 | pass |")
    print("|---|---|---|---|---|---|---|")
    for name in JUDGED:
        rs = [r for r in rows if r["design"] == "main" and r["parameter"] == name]
        nom = [r for r in rs if r["set"] == "nominal"][0]
        v = s["verdict"]["main"]["params"][name]
        print(f"| {name} | {float(nom['truth']):.4g} | {float(nom['error']):+.4f} | {float(nom['tolerance']):.4f} | "
              f"{v['off_nominal_within']}/{v['off_nominal_n']} | {v['max_abs_error']:.4f} | "
              f"{'PASS' if v['pass'] else 'FAIL'} |")
    print(f"\nmain overall: {'PASS' if s['verdict']['main']['pass'] else 'FAIL'}\n")
    print("## all designs: sets within tolerance (nominal + 10 off-nominal = 11)\n")
    print("| parameter | " + " | ".join(designs) + " |")
    print("|---|" + "---|" * len(designs))
    for name in JUDGED:
        cells = []
        for d in designs:
            rs = [r for r in rows if r["design"] == d and r["parameter"] == name]
            if rs[0]["fitted"] != "True":
                cells.append("fixed")
            else:
                cells.append(f"{sum(r['within'] == 'True' for r in rs)}")
        print(f"| {name} | " + " | ".join(cells) + " |")
    print("| median abs error N (median over sets) | " + " | ".join(
        f"{sorted(float(r['median_abs_error_n']) for r in rows if r['design'] == d and r['parameter'] == JUDGED[0])[5]:.3f}"
        for d in designs) + " |")
    print("\n## main design: errors per set\n")
    sets = [x["name"] for x in s["sets"]]
    print("| parameter | " + " | ".join(sets) + " |")
    print("|---|" + "---|" * len(sets))
    for name in JUDGED:
        cells = []
        for st in sets:
            r = [r for r in rows if r["design"] == "main" and r["parameter"] == name and r["set"] == st][0]
            cells.append(f"{float(r['error']):+.3g}" + ("" if r["within"] == "True" else " x"))
        print(f"| {name} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main(*sys.argv[1:])
