"""Tables for the Checkpoint 2 review fixes, from committed files only.

    python -m experiments.cp2_review_tables > results/checkpoint2_prep/review_fixes/tables.md

Development measurements in simulation (seeds 2026, 3031, 4001 and the training seeds
3001-3030 for the data counts), not reported results. Every table names its files.
"""

from __future__ import annotations

import csv
import gzip
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from defex.config import REPO_ROOT, ConnectorSpec, SafetyConfig
from defex.control.base import REFERENCE_FOLLOWING_LAG_S, REFERENCE_ROTATIONAL_STIFFNESS_NM_PER_RAD
from experiments.cp2_tables import LETTER, overlap_check, rel, snapshot_tables, text_file
from experiments.eval_learned_prior import _boot_ci

ROOT = REPO_ROOT / "results" / "checkpoint2_prep"
RF = ROOT / "review_fixes"
VARIANTS = (2, 4, 6, 11, 12)
KEY = ("controller", "condition", "trial_index", "seed")


def _rows(path: Path) -> dict[tuple, dict]:
    with path.open() as fh:
        return {tuple(r[k] for k in KEY): r for r in csv.DictReader(fh)}


def _differs(a: dict, b: dict) -> bool:
    return any(a[k] != b.get(k) for k in a if k != "wall_time_s")


def _ok(r: dict) -> bool:
    return r["success"] == "True"


# ------------------------------------------------------------------ randomized slice
def rand_slice_table() -> str:
    meta = json.loads((RF / "rand_slice" / "cp2_after" / "variants.json").read_text())
    out = ["| Variant | Wrist servo (x 15 N m/rad) | Translational / rotational lag (s) | C rows differing from w3: "
           "before fix / after | F rows differing: before / after | C successes w3 / before / after | "
           "C cycle, before minus w3, both succeeded (s, 95% CI) |", "|---|---|---|---|---|---|---|"]
    pooled = {"w3": 0, "before": 0, "after": 0, "n": 0, "dcyc": []}
    for k in VARIANTS:
        fd = meta["variants"][str(k)]["fixture_dynamics"]
        w3, bf, af = (_rows(RF / "rand_slice" / n / f"variant_{k}" / "trials.csv") for n in ("w3", "cp2_before", "cp2_after"))
        cnt = {c: [sum(_differs(w3[key], run[key]) for key in w3 if key[0] == c) for run in (bf, af)]
               for c in ("adaptive", "spiral_rcc")}
        nc = sum(key[0] == "adaptive" for key in w3)
        succ = [sum(_ok(run[key]) for key in w3 if key[0] == "adaptive") for run in (w3, bf, af)]
        dcyc = np.array([float(bf[key]["cycle_time_s"]) - float(w3[key]["cycle_time_s"]) for key in w3
                         if key[0] == "adaptive" and _ok(w3[key]) and _ok(bf[key])])
        ci = _boot_ci(dcyc)
        ratio = fd["yaw_stiffness_nm_per_rad"] / REFERENCE_ROTATIONAL_STIFFNESS_NM_PER_RAD
        out.append(f"| {k} | {ratio:.3f} | {fd['following_lag_s']:.4f} / {fd['rotational_following_lag_s']:.4f} | "
                   f"{cnt['adaptive'][0]} / {cnt['adaptive'][1]} of {nc} | {cnt['spiral_rcc'][0]} / "
                   f"{cnt['spiral_rcc'][1]} of {nc} | {succ[0]} / {succ[1]} / {succ[2]} of {nc} | "
                   f"{dcyc.mean():+.2f} ({ci[0]:+.2f} to {ci[1]:+.2f}), n = {dcyc.size} |")
        if ratio > 1.0:
            for i, n in enumerate(("w3", "before", "after")):
                pooled[n] += succ[i]
            pooled["n"] += nc
            pooled["dcyc"] += dcyc.tolist()
    d = np.array(pooled["dcyc"])
    ci = _boot_ci(d)
    out += ["", f"Pooled over the variants with a wrist servo above 15 N m/rad (rate-mode conform before the fix): "
                f"C successes w3 / before / after {pooled['w3']} / {pooled['before']} / {pooled['after']} of {pooled['n']}; "
                f"cycle before minus w3, both succeeded, {d.mean():+.2f} s (95% CI {ci[0]:+.2f} to {ci[1]:+.2f}, n = {d.size}).",
            "", f"Before-fix failures of C not in w3: " + (", ".join(_new_failures()) or "none") + ".",
            "", f"Files: `{rel(RF / 'rand_slice')}/{{w3,cp2_before,cp2_after}}/variant_*/trials.csv`, "
                f"`{rel(RF / 'rand_slice' / 'cp2_after' / 'variants.json')}` (fixture dynamics as reported after the fix)."]
    return "\n".join(out)


def _new_failures() -> list[str]:
    out = []
    for k in VARIANTS:
        w3 = _rows(RF / "rand_slice" / "w3" / f"variant_{k}" / "trials.csv")
        bf = _rows(RF / "rand_slice" / "cp2_before" / f"variant_{k}" / "trials.csv")
        for key in sorted(w3):
            if key[0] == "adaptive" and _ok(w3[key]) != _ok(bf[key]):
                who = "before-only failure" if _ok(w3[key]) else "before-only success"
                out.append(f"variant {k} {key[1]} #{key[2]} ({who}: {bf[key]['failure_reason'] if not _ok(bf[key]) else 'seated'})")
    return out


# ------------------------------------------------------------------ out-of-sample snapshot
def failure_reasons(run: Path, controllers=("spiral", "spiral_rcc", "adaptive", "adaptive_learned"),
                    condition: str = "noise_2mm") -> str:
    rows = list(_rows(run / "trials.csv").values())
    out = []
    for c in controllers:
        rr = [r for r in rows if r["controller"] == c and r["condition"] == condition]
        if not rr:
            continue
        fr = Counter(r["failure_reason"] for r in rr if not _ok(r))
        out.append(f"{LETTER[c]} {sum(_ok(r) for r in rr)}/{len(rr)} ("
                   + (", ".join(f"{k} {v}" for k, v in sorted(fr.items())) or "no failures") + ")")
    return f"{condition} in `{rel(run / 'trials.csv')}`: " + "; ".join(out) + "."


# ------------------------------------------------------------------ wrong-polarization stops
_STOP = re.compile(r"\|F\|=([\d.]+) N \|T\|=([\d.]+) N m")


def stop_mechanisms(runs: list[tuple[str, Path]]) -> str:
    safety = SafetyConfig()
    stop_n = ConnectorSpec.load("microfit3_4ckt").force_budget.protective_stop_n
    out = [f"Protective stops on mf_wrong_polarization (limits: measured force {stop_n:g} N for the Micro-Fit, "
           f"measured torque {safety.protective_stop_torque_nm:g} N m). Values at the stop event.", "",
           "| Run | Controller | Stops | Force trips | Torque trips | |F| at stop (N) | |T| at stop (N m) | "
           "State before the stop | Yaw correction of the last attempt (deg) |", "|---|---|---|---|---|---|---|---|---|"]
    for name, run in runs:
        ev = json.loads(gzip.open(run / "events.json.gz", "rt").read())
        for c in ("adaptive", "adaptive_learned"):
            fs, ts, states, yaws, nf, nt = [], [], Counter(), [], 0, 0
            for key, events in ev.items():
                cond, ctl, _ = key.split("|")
                if cond != "mf_wrong_polarization" or ctl != c:
                    continue
                stops = [e for e in events if e[1] == "protective_stop"]
                if not stops:
                    continue
                m = _STOP.search(stops[0][2])
                f, t = float(m.group(1)), float(m.group(2))
                fs.append(f)
                ts.append(t)
                nf += f > stop_n
                nt += t > safety.protective_stop_torque_nm
                before = [e for e in events if e[0] <= stops[0][0] and e[1] == "state"]
                states[before[-1][2].split(":")[0] if before else "?"] += 1
                att = [e for e in events if e[0] <= stops[0][0] and e[1] == "attempt"]
                ym = re.search(r"yaw_corr=([+-][\d.]+) deg", att[-1][2]) if att else None
                yaws.append(float(ym.group(1)) if ym else float("nan"))
            if not fs:
                out.append(f"| {name} | {LETTER[c]} | 0 | - | - | - | - | - | - |")
                continue
            out.append(f"| {name} | {LETTER[c]} | {len(fs)} | {nf} | {nt} | {min(fs):.1f}-{max(fs):.1f} | "
                       f"{min(ts):.2f}-{max(ts):.2f} | {', '.join(f'{k} {v}' for k, v in states.items())} | "
                       f"{', '.join(f'{y:+.1f}' for y in sorted(yaws))} |")
    out += ["", "Files: " + ", ".join(f"`{rel(run / 'events.json.gz')}`" for _, run in runs) + "."]
    return "\n".join(out)


# ------------------------------------------------------------------ offline model quality and data
def model_quality() -> str:
    out = ["| Model | Split | n | NLL (nats) | Radial error, all contacts: learned / C's analytic posterior (mm) | "
           "First contacts: learned / analytic (mm) | Inside 1 / 2 sigma (expected 0.39 / 0.86) |",
           "|---|---|---|---|---|---|---|"]
    paths = [ROOT / "arm_prior" / "models" / f"arm_{s}_metrics.json" for s in ("contact", "all")]
    names = {"train": "train 3001-3030", "validation": "validation 4001 (selection split)",
             "dev_seed2026": "dev 2026 (held out)"}
    for p in paths:
        m = json.loads(p.read_text())
        for split in ("dev_seed2026", "validation", "train"):
            s = m[split]
            a, f, c = s["mae_mm"], s["mae_mm_first_contact"], s["calibration_xy"]["learned"]
            out.append(f"| {m['feature_set']}{' (installed)' if m['feature_set'] == 'contact' else ''} | {names[split]} | "
                       f"{s['n']} | {s['nll_nats']:.2f} | {a['learned']['radial_mean']:.3f} / "
                       f"{a['analytic_posterior_mean']['radial_mean']:.3f} | {f['learned']['radial_mean']:.3f} / "
                       f"{f['analytic_posterior_mean']['radial_mean']:.3f} | {c['inside_1sigma']:.3f} / {c['inside_2sigma']:.3f} |")
    return "\n".join(out + ["", "The validation split chose early stopping, the grid point, the input set and the "
                                "integration weight; dev 2026 was used for none of them. Files: "
                            + ", ".join(f"`{rel(p)}`" for p in paths) + "."])


def data_counts() -> str:
    out = ["| Dataset | Base seeds | Trials | Surface-block records |", "|---|---|---|---|"]
    total = 0
    for p in sorted((ROOT / "arm_prior" / "data" / "arm").glob("*/summary.json")):
        d = json.loads(p.read_text())
        seeds = d.get("base_seeds") or []
        kinds = d.get("records_by_condition_and_kind") or {}
        sb = sum(v.get("surface_block", 0) for v in kinds.values()) if isinstance(kinds, dict) else "-"
        out.append(f"| {p.parent.name} | {min(seeds)}-{max(seeds)} | {d['n_trials']} | {sb} |")
        total += d["n_trials"] if p.parent.name != "family_probe_seed3001" else 0
    return "\n".join(out + ["", f"Without the family probe: {total} trials. Files: "
                            f"`{rel(ROOT / 'arm_prior' / 'data' / 'arm')}/*/summary.json`."])


def calibration_table() -> str:
    res = json.loads((RF / "posterior_calibration.json").read_text())
    out = ["| Backend | Split | First contacts | Outside 50% region: C / G / learned alone (expected 0.50) | "
           "Outside 95% region: C / G / learned alone (expected 0.05) | Mean radial error C / G / learned (mm) |",
           "|---|---|---|---|---|---|"]
    for r in res:
        o, e = r["outside_hpd"], r["mean_radial_error_mm"]
        name = "dev 2026 (held out)" if r["base_seed"] == 2026 else "validation 4001 (selection split)"
        out.append(f"| {r['backend']} | {name} | {r['n_first_contacts']} | {o['C']['0.5']:.2f} / {o['G']['0.5']:.2f} / "
                   f"{o['learned']['0.5']:.2f} | {o['C']['0.95']:.3f} / {o['G']['0.95']:.3f} / {o['learned']['0.95']:.3f} | "
                   f"{e['C']:.2f} / {e['G']:.2f} / {e['learned']:.2f} |")
    return "\n".join(out + ["", "C = C's analytic posterior after the contact; G = that posterior with the installed "
                                "model's term at its weight (what G's probe selection uses); learned alone = the "
                                "model's Gaussian. Highest-density regions. File: "
                            f"`{rel(RF / 'posterior_calibration.json')}` (experiments/cp2_posterior_calibration.py)."])


def main() -> None:
    parts = ["# Checkpoint 2 preparation: review fixes, development tables", "",
             "Generated by `python -m experiments.cp2_review_tables` from committed files. Development "
             "measurements in simulation; not reported results.", ""]
    parts += ["## Rule-3 equivalence against v0.2/w3-latch-physics", "", text_file(RF / "comparison.txt"), ""]
    parts += ["## Randomized gantry slice (dev seed 2026, C and F, 6 conditions x 10 trials per variant)", "",
              rand_slice_table(), ""]
    snap = ROOT / "snapshot"
    mc = RF / "model_check"
    rows = [overlap_check(mc / a / "trials.csv", snap / b / "trials.csv") for a, b in
            (("gantry_standard", "gantry_standard"), ("gantry_latching", "gantry_latching"),
             ("arm_standard", "arm_standard5"), ("arm_latching", "arm_latching"))]
    parts += ["## Installed models with completed fixture dynamics: the same trials as the snapshot", "",
              "| Run | Snapshot run | Shared trials | Controllers | Rows that differ | Differing rows by controller |",
              "|---|---|---|---|---|---|", *rows, ""]
    s31 = RF / "seed3031"
    for name, title in (("arm_standard5", "UR5e arm, five-condition set"), ("gantry_standard5", "Gantry, five-condition set"),
                        ("arm_latching", "UR5e arm, latching suite"), ("gantry_latching", "Gantry, latching suite")):
        if (s31 / name / "summary.json").exists():
            note = ("A, B, D, E, F: no arm-specific tuning. C: W5b arm rules (developed on dev seeds 2026 and 2027). "
                    "G: C plus the arm contact prior (trained on seeds 3001-3030, chosen on 4001)."
                    if name.startswith("arm") else
                    "All controllers as tuned on the gantry (dev seed 2026). G: C plus the gantry contact prior "
                    "(trained on seeds 3001-3030, chosen on 4001).")
            parts += [f"## Seed 3031 (no controller was developed or trained on it): {title}", "", note, "",
                      snapshot_tables(s31 / name), ""]
    for name in ("arm_standard5", "gantry_standard5"):
        if (s31 / name / "trials.csv").exists():
            parts += [failure_reasons(s31 / name), ""]
    parts += [failure_reasons(snap / "arm_standard5"), "", failure_reasons(snap / "gantry_standard"), ""]
    runs = [("gantry snapshot, seed 2026", snap / "gantry_latching"), ("arm snapshot, seed 2026", snap / "arm_latching"),
            ("arm G vs C, seed 2026, 60 trials", ROOT / "arm_prior" / "dev2026" / "latching")]
    runs += [(f"{b} seed 3031", s31 / f"{b}_latching") for b in ("gantry", "arm") if (s31 / f"{b}_latching" / "events.json.gz").exists()]
    parts += ["## Wrong-polarization stops: which limit trips", "", stop_mechanisms(runs), ""]
    parts += ["## Arm contact prior: offline quality, held-out dev split first", "", model_quality(), ""]
    parts += ["## Posterior calibration on first contacts (offline replay)", "", calibration_table(), ""]
    parts += ["## Arm contact data", "", data_counts(), ""]
    print("\n".join(parts).rstrip() + "\n")


if __name__ == "__main__":
    main()
