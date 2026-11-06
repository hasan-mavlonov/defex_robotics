"""Apply results/v0.2c_integration/review_fixes/verify_selection/SELECTION_RULE.md to a validation folder.

    python -m experiments.v02c_verify_select results/v0.2c_integration/review_fixes/verify_selection/validation4002

Expects <folder>/<backend>_<suite>/trials.csv with controllers ``adaptive@<variant>``. Prints the
markdown table, the ranking and the decision. Pure function of the per-trial rows.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from experiments.checkpoint_report import escape, false_reject, fmt_p, load, mcnemar, ok, paired, stop, wilson

CANDIDATES = ("w3", "noclick", "w60", "w80", "w60f", "w80f")  # rule order; w3 is the current code
REFERENCE = "w3"


def gather(folder: Path) -> dict[str, list[dict]]:
    rows: list[dict] = []
    for sub in sorted(p for p in folder.iterdir() if (p / "trials.csv").exists()):
        backend = sub.name.partition("_")[0]
        rows += [dict(r, backend=backend) for r in load(sub)]
    return {v: [r for r in rows if r["controller"] == f"adaptive@{v}"] for v in CANDIDATES}


def stats(rs: list[dict]) -> dict:
    good = [r for r in rs if r["group"] != "bad_part"]
    ct = [float(r["cycle_time_s"]) for r in good if ok(r)]
    return {"k": sum(ok(r) for r in good), "n": len(good), "bad": sum(escape(r) for r in rs),
            "bad_n": sum(r["group"] == "bad_part" for r in rs), "fr": sum(false_reject(r) for r in good),
            "stops": sum(stop(r) for r in rs),
            "p50": float(np.percentile(ct, 50)) if ct else float("inf"),
            "p95": float(np.percentile(ct, 95)) if ct else float("inf")}


def _keyed(rs: list[dict]) -> list[dict]:
    # paired() keys on (controller, condition, trial); make the backend part of the condition
    return [dict(r, condition=f"{r['backend']}|{r['condition']}") for r in rs if r["group"] != "bad_part"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", type=Path)
    args = ap.parse_args()
    by = gather(args.folder)
    st = {v: stats(rs) for v, rs in by.items() if rs}
    lines = [f"Rule applied to `{args.folder}` (C only, latching + latch_spread suites, both backends).", "",
             "| Variant | Good parts seated (95% CI) | Bad units passed (bad-part trials) | False rejects | "
             "Protective stops | Median / p95 cycle (s) | vs w3: w3-only / variant-only (McNemar p) | Eligible |",
             "|---|---|---|---|---|---|---|---|"]
    for v, s in st.items():
        lo, hi = wilson(s["k"], s["n"])
        if v == REFERENCE:
            pair = "reference"
        else:
            rows = _keyed(by[REFERENCE]) + _keyed(by[v])
            a, b, _ = paired(rows, f"adaptive@{REFERENCE}", f"adaptive@{v}")
            pair = f"{a} / {b} ({fmt_p(mcnemar(a, b))})"
        lines.append(f"| {v} | {s['k']}/{s['n']} = {100 * s['k'] / s['n']:.1f}% ({100 * lo:.1f}-{100 * hi:.1f}) | "
                     f"{s['bad']} ({s['bad_n']}) | {s['fr']} | {s['stops']} | {s['p50']:.2f} / {s['p95']:.2f} | "
                     f"{pair} | {'yes' if s['bad'] == 0 else 'no'} |")
    for backend in ("gantry", "arm"):
        lines += ["", f"{backend}:", "", "| Variant | Good parts seated | Bad units passed | False rejects | Stops |",
                  "|---|---|---|---|---|"]
        for v in st:
            s = stats([r for r in by[v] if r["backend"] == backend])
            lines.append(f"| {v} | {s['k']}/{s['n']} | {s['bad']} | {s['fr']} | {s['stops']} |")
    eligible = [v for v in st if st[v]["bad"] == 0]
    ranked = sorted(eligible, key=lambda v: (-st[v]["k"], st[v]["p50"], st[v]["p95"], CANDIDATES.index(v)))
    lines += ["", "Ranking (good parts seated, then median, then p95, then rule order): " + " > ".join(ranked)]
    lines.append(f"\nDecision: install {ranked[0]}." if ranked else f"\nDecision: no eligible candidate; keep {REFERENCE}.")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
