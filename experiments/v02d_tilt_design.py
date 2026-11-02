"""v0.2d tilt check: design tables from the training-seed feature files (results/v0.2d_tilt_check/design).

    python -m experiments.v02d_tilt_design results/v0.2d_tilt_check/design > results/v0.2d_tilt_check/DESIGN_TABLES.md

Offline, ground truth from the feature files. "Pass" is the VERIFY that ended in a declared success.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from experiments.v02d_tilt_select import MAX_TILT_DEG, load

CANDIDATES = {"tilt_k1": (2.0, 0.875), "tilt_k2": (2.5, 0.875), "tilt_k3": (1.5, 0.75)}


def passes(rows):
    out = []
    for r in rows:
        p = [v for v in r["record"]["verifies"] if "pass" in v]
        if r["declared_success"] and p:
            out.append((r, p[-1]))
    return out


def is_escape(r) -> bool:
    return bool(r["declared_success"] and not r["gt_seated"] and not r["protective_stop"])


def diag_edge(v, half) -> float:
    c = v["begin"].get("diag", {}).get("cop_mm")
    return float("nan") if c is None else max(abs(c[0]) / half[0], abs(c[1]) / half[1])


def latching(name: str, rows) -> list[str]:
    half = (3.425, 3.43)
    ps = passes(rows)
    esc = [(r, v) for r, v in ps if is_escape(r)]
    out = [f"### {name}: latching VERIFY, `mf_noise_1mm`, seeds 3001-3030 x 40 trials\n",
           f"{len(rows)} trials, {len(ps)} declared seated, {len(esc)} of them tilt escapes.\n",
           "Bottoming CoP (DETECT window, largest |CoP| / half-width) and plug axis against C's socket-axis estimate "
           "at the start of the passing VERIFY, by true final tilt:\n",
           "| True tilt (deg) | Passes | CoP fraction median / p90 / max | Axis off estimate median / p90 / max (deg) |",
           "|---|---|---|---|"]
    gt = np.array([r["final_tilt_deg"] for r, _ in ps])
    edge = np.array([diag_edge(v, half) for _, v in ps])
    tilt = np.array([v["begin"]["est_tilt_vs_corr"] for _, v in ps])
    for lo, hi in ((0, 1), (1, 2), (2, 2.5), (2.5, 3.0), (3.0, 90)):
        m = (gt >= lo) & (gt < hi)
        if m.sum():
            e, t = edge[m], tilt[m]
            out.append(f"| {lo}-{hi if hi < 90 else ''} | {int(m.sum())} | {np.nanmedian(e):.2f} / {np.nanpercentile(e, 90):.2f} / "
                       f"{np.nanmax(e):.2f} | {np.median(t):.2f} / {np.percentile(t, 90):.2f} / {t.max():.2f} |")
    out += ["", "Every tilt escape:\n", "| Seed | Trial | True tilt | True depth (mm) | Axis off estimate (deg) | CoP fraction | "
            "Top-face conform that slid into the lead-in (deg) |", "|---|---|---|---|---|---|---|"]
    for r, v in esc:
        slid = [[round(c, 2) for c in s["adm_conf_deg"][:2]] for s in r["record"]["slid_in"]]
        out.append(f"| {r['base_seed']} | {r['trial_index']} | {r['final_tilt_deg']:.2f} | {r['final_depth_mm']:.2f} | "
                   f"{v['begin']['est_tilt_vs_corr']:.2f} | {diag_edge(v, half):.2f} | {slid} |")
    out += ["", "Trials where a candidate would act (any VERIFY start of the trial, DETECT-window CoP):\n",
            "| Candidate | Seated good parts | Tilt escapes | Already failing trials |", "|---|---|---|---|"]
    for k, (deg, frac) in CANDIDATES.items():
        n = {"good": 0, "escape": 0, "other": 0}
        for r in rows:
            hit = any(v["begin"]["est_tilt_vs_corr"] > deg and diag_edge(v, half) > frac for v in r["record"]["verifies"])
            if hit:
                n["good" if r["success"] else "escape" if is_escape(r) else "other"] += 1
        out.append(f"| {k} | {n['good']} | {n['escape']} | {n['other']} |")
    return out + [""]


def housing(name: str, rows) -> list[str]:
    half = (6.0, 4.0)
    ps = passes(rows)
    esc = [(r, v) for r, v in ps if is_escape(r)]
    out = [f"### {name}: housing-only VERIFY, `noise_1mm`, `noise_2mm`, `friction_1`, seeds 3001-3030 x 40 trials\n",
           f"{len(rows)} trials, {len(ps)} declared seated, {len(esc)} of them tilt escapes.\n"]
    for r, v in esc:
        sc = v.get("seat_conform", {})
        out.append(f"Escape: seed {r['base_seed']}, {r['condition']}, trial {r['trial_index']}: {r['final_tilt_deg']:.2f} deg, "
                   f"true tilt vector {np.round(v['pass']['gt']['rv_deg'][:2], 2).tolist()} deg (x, y).\n")
    rows_t = ["| Observable at the passing VERIFY | Escape | Good passes at least as extreme |", "|---|---|---|"]
    goods = [(r, v) for r, v in ps if not is_escape(r)]

    def axis_off(v):
        return v.get("seat_conform", {}).get("est_tilt_vs_corr", np.nan)

    def sc_edge(v):
        c = v.get("seat_conform", {}).get("win", {}).get("cop_mm")
        return np.nan if c is None else max(abs(c[0]) / half[0], abs(c[1]) / half[1])

    def unflat(v):
        f = v.get("seat_conform", {}).get("rc_flat")
        return np.nan if f is None else float(not all(f))

    def neg_free(v):
        c = v.get("lateral", {}).get("contacts") or []
        return -(c[0][0] + c[1][0]) if len(c) >= 2 else np.nan

    obs = [("plug axis off C's socket-axis estimate after the seat conform (deg)", axis_off),
           ("largest CoP / half-width at the end of the seat conform", sc_edge),
           ("minus the free travel between the two y-wall contacts (mm; tilt about x narrows it)", neg_free)]
    if any(any(v.get("seat_conform", {}).get("rc_flat", [])) for _, v in ps[:50]):
        obs.append(("rate-mode seat conform left an axis not flat (1 = yes)", unflat))
    for label, fn in obs:
        for r, v in esc:
            x = fn(v)
            n = sum(1 for _, g in goods if fn(g) >= x - 1e-12)
            rows_t.append(f"| {label} | {x:.2f} | {n} of {len(goods)} |")
    gt = np.array([r["final_tilt_deg"] for r, _ in ps])
    out += rows_t + ["", f"True final tilt of the passes: median {np.median(gt):.2f}, p99 {np.percentile(gt, 99):.2f}, "
                         f"above 2 deg: {int((gt > 2).sum())}, above {MAX_TILT_DEG} deg: {int((gt > MAX_TILT_DEG).sum())}.", ""]
    return out


def gantry_conform_timeout(rows) -> list[str]:
    ps = passes(rows)
    out = []
    data = []
    for r, v in ps:
        fin = [e for e in r["events"] if e[1] == "finish"]
        sc = [e for e in r["events"] if e[1] == "seat_conform"]
        if not fin or not sc:
            continue
        off = fin[-1][0] - r["cycle_time_s"]
        t_b = v["begin"]["t"]
        after = [e for e in sc if e[0] - off >= t_b - 1e-6]
        if not after:
            continue
        el = after[0][0] - off - t_b
        conf = v.get("seat_conform", {}).get("adm_conf_deg", [0, 0])
        data.append((is_escape(r), el, float(np.hypot(*conf[:2])), r["final_tilt_deg"]))
    if not data:
        return out
    to = [d for d in data if d[1] > 0.79]
    out.append(f"Gantry seat conform (admittance, 0.8 s limit): {len(to)} of {len(data)} passes ran out of time, "
               f"{sum(d[0] for d in to)} of them the escape; of those with less than 1.2 deg turned: "
               f"{sum(1 for d in to if d[2] < 1.2)} passes, {sum(1 for d in to if d[2] < 1.2 and d[0])} the escape.\n")
    return out


def main() -> None:
    d = Path(sys.argv[1])
    out = ["# v0.2d tilt check: design tables", "",
           f"Generated by `python -m experiments.v02d_tilt_design {d}` from the feature files there (controller C, "
           "training seeds 3001-3030; collector `experiments/v02d_tilt_features.py`). Ground truth offline only.", ""]
    for m in ("arm", "gantry"):
        out += latching(m, load([str(d / f"{m}_train_mf.jsonl.gz")]))
    for m in ("arm", "gantry"):
        rows = load([str(d / f"{m}_train_std.jsonl.gz")])
        out += housing(m, rows)
        if m == "gantry":
            out += gantry_conform_timeout(rows)
    print("\n".join(out))


if __name__ == "__main__":
    main()
