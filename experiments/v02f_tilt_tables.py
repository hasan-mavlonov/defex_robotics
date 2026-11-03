"""v0.2f tilt diagnosis: tables from the collector's rows (experiments/v02f_tilt_diag.py run).

    python experiments/v02f_tilt_tables.py results/v0.2f_tilt_diagnosis/runs > results/v0.2f_tilt_diagnosis/TABLES.md

Reads every ``*.jsonl.gz`` in the folder whose name does not start with ``fix_`` or ``val_`` (the frozen code).
Ground truth is used for scoring only.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

LABEL = {"adaptive": "C", "adaptive_learned": "G", "spiral_rcc_verify": "J"}


def load(folder: Path, prefix: str = "") -> list[dict]:
    rows = []
    for p in sorted(folder.glob("*.jsonl.gz")):
        if prefix and not p.name.startswith(prefix):
            continue
        if not prefix and (p.name.startswith("fix_") or p.name.startswith("val_")):
            continue
        with gzip.open(p, "rt") as fh:
            rows.extend(json.loads(line) for line in fh)
    return rows


def good(r: dict) -> bool:
    return r["group"] != "bad_part"


def bad_unit(r: dict) -> bool:
    return bool(r["declared_success"]) and not r["success"] and not r["protective_stop"]


def cause(c: dict) -> str:
    """Which error makes the measured tilt smaller than the true one (projections on the true tilt direction)."""
    vt = np.array(c["v_true"])
    n = np.linalg.norm(vt)
    if n < 1e-9:
        return "-"
    u = vt / n
    sock = float(np.dot(np.array(c["v_sock"]), u))  # the estimate turned with the plug: hides tilt
    cam = float(np.dot(np.array(c["v_cam"]), u))
    fold = sock - cam
    plug = -float(np.dot(np.array(c["v_plug"]) - vt, u))  # the in-hand estimate short of the true axis
    parts = {"camera": cam, "folds": fold, "in-hand": plug}
    return max(parts, key=parts.get)


def pct(x, q):
    return f"{np.percentile(x, q):.2f}" if len(x) else "-"


def item1(rows: list[dict]) -> list[str]:
    out = ["## Item 1: tilt evidence against true tilt, C and G, latching and latch_spread", "",
           "Latch checks with a tilt verdict (PASS or FAIL). 'Under by > 1 deg': true tilt minus measured tilt over "
           "1 deg. Cause: the largest of the three projections on the true tilt direction (camera axis error, "
           "R_corr folds, in-hand estimate error).", "",
           "| Machine | Ctrl | Trials | Verdicts | Under by > 1 deg | of which true tilt > 2 deg | Cause camera / folds / in-hand (all under > 1) | max underestimate (deg) |",
           "|---|---|---|---|---|---|---|---|"]
    lists = []
    for (m, ctrl), rs in sorted(group(rows, ("backend", "controller")).items()):
        if ctrl == "spiral_rcc_verify" or not any(r["suite"] in ("latching", "latch_spread") for r in rs):
            continue
        rs = [r for r in rs if r["suite"] in ("latching", "latch_spread")]
        checks = [(r, c) for r in rs for c in r["checks"] if c["verdict"] in ("PASS", "FAIL")]
        under = [(r, c) for r, c in checks if c["true_tilt"] - c["meas_tilt"] > 1.0]
        hi = [(r, c) for r, c in under if c["true_tilt"] > 2.0]
        cc = Counter(cause(c) for _, c in under)
        mx = max((c["true_tilt"] - c["meas_tilt"] for _, c in checks), default=0.0)
        out.append(f"| {m} | {LABEL[ctrl]} | {len(rs)} | {len(checks)} | {len(under)} | {len(hi)} | "
                   f"{cc['camera']} / {cc['folds']} / {cc['in-hand']} | {mx:.2f} |")
        lists += [(m, ctrl, r, c) for r, c in hi]
    out += ["", "Verdicts under by > 1 deg at a true tilt over 2 deg (each listed):", "",
            "| Machine | Ctrl | Seed | Condition | Trial | Path | F (N) | Measured | True | CoP edge | Camera err | Folds (R_corr tilt) | In-hand err | Cause | Verdict | Outcome | Final tilt |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m, ctrl, r, c in lists:
        rc = np.hypot(*c["rcorr_deg"][:2])
        out.append(f"| {m} | {LABEL[ctrl]} | {r['base_seed']} | {r['condition']} | {r['trial_index']} | {c['path']} | "
                   f"{c['f_ax']:.1f} | {c['meas_tilt']:.2f} | {c['true_tilt']:.2f} | {c['edge']:.2f} | {c['cam_err']:.2f} | "
                   f"{rc:.2f} | {c['plug_err']:.2f} | {cause(c)} | {c['verdict']} | {outcome(r)} | {r['final_tilt_deg']:.2f} |")
    if not lists:
        out.append("| none | | | | | | | | | | | | | | | | |")
    out += ["", "Final true tilt of trials C or G declared seated (latching, latch_spread; good and bad parts):", "",
            "| Machine | Ctrl | Declared | tilt < 2 | 2-2.5 | 2.5-3 | > 3 (bad units) | max |", "|---|---|---|---|---|---|---|---|"]
    for (m, ctrl), rs in sorted(group(rows, ("backend", "controller")).items()):
        rs = [r for r in rs if r["suite"] in ("latching", "latch_spread") and r["declared_success"]]
        if not rs:
            continue
        t = np.array([r["final_tilt_deg"] for r in rs])
        out.append(f"| {m} | {LABEL[ctrl]} | {len(rs)} | {(t < 2).sum()} | {((t >= 2) & (t < 2.5)).sum()} | "
                   f"{((t >= 2.5) & (t <= 3)).sum()} | {(t > 3).sum()} | {t.max():.2f} |")
    near = [r for r in rows if r["suite"] in ("latching", "latch_spread") and r["declared_success"]
            and 2.0 <= r["final_tilt_deg"] and r["controller"] != "spiral_rcc_verify"]
    out += ["", "Each declared trial at 2 deg or more (C, G):", "",
            "| Machine | Ctrl | Seed | Condition | Trial | Final tilt | Outcome | Last verdict: measured / true / edge / F |",
            "|---|---|---|---|---|---|---|---|"]
    for r in sorted(near, key=lambda r: -r["final_tilt_deg"]):
        v = [c for c in r["checks"] if c["verdict"] in ("PASS", "FAIL", "no verdict")]
        last = v[-1] if v else None
        lv = (f"{last['verdict']}: {last['meas_tilt']:.2f} / {last['true_tilt']:.2f} / {last['edge']:.2f} / "
              f"{last['f_ax'] if last['f_ax'] is None else round(last['f_ax'], 1)}") if last else "-"
        out.append(f"| {r['backend']} | {LABEL[r['controller']]} | {r['base_seed']} | {r['condition']} | "
                   f"{r['trial_index']} | {r['final_tilt_deg']:.2f} | {outcome(r)} | {lv} |")
    return out


def item2(rows: list[dict]) -> list[str]:
    out = ["## Item 2: J's first latch check", "",
           "| Machine | J trials (latching, latch_spread) | Latch checks | of which hand-over | hand-over with samples | no verdict (all) | Verdicts | Hand-over: measured tilt p50 / p95 / max | Hand-over: true tilt p50 / max |",
           "|---|---|---|---|---|---|---|---|---|"]
    for m, rs in sorted(group([r for r in rows if r["controller"] == "spiral_rcc_verify"], ("backend",)).items()):
        cs = [c for r in rs for c in r["checks"]]
        ho = [c for c in cs if c["path"] == "handover"]
        nv = [c for c in cs if c["verdict"] == "no verdict"]
        vd = [c for c in cs if c["verdict"] in ("PASS", "FAIL")]
        mt = [c["meas_tilt"] for c in ho]
        tt = [c["true_tilt"] for c in ho]
        out.append(f"| {m[0] if isinstance(m, tuple) else m} | {len(rs)} | {len(cs)} | {len(ho)} | "
                   f"{sum(c['n'] > 0 for c in ho)} | {len(nv)} | {len(vd)} | {pct(mt, 50)} / {pct(mt, 95)} / "
                   f"{max(mt) if mt else 0:.2f} | {pct(tt, 50)} / {max(tt) if tt else 0:.2f} |")
    return out


def item3(rows: list[dict]) -> list[str]:
    out = ["## Item 3: housing-only VERIFY (standard suite), C and G, accepted units", "",
           "Final true tilt and |yaw| of every trial declared seated (trials.csv fields final_tilt_deg, "
           "final_yaw_deg). Limits 3.0 deg each.", "",
           "| Machine | Ctrl | Declared | tilt p50 / p95 / p99 / max | tilt 2-2.5 / 2.5-3 / > 3 | |yaw| p50 / p95 / p99 / max | |yaw| 2-2.5 / 2.5-3 / > 3 | bad units |",
           "|---|---|---|---|---|---|---|---|"]
    for (m, ctrl), rs in sorted(group([r for r in rows if r["suite"] == "standard"], ("backend", "controller")).items()):
        d = [r for r in rs if r["declared_success"]]
        t = np.array([r["final_tilt_deg"] for r in d])
        y = np.abs([r["final_yaw_deg"] for r in d])
        b = lambda x: f"{((x >= 2) & (x < 2.5)).sum()} / {((x >= 2.5) & (x <= 3)).sum()} / {(x > 3).sum()}"  # noqa
        out.append(f"| {m} | {LABEL[ctrl]} | {len(d)} | {pct(t, 50)} / {pct(t, 95)} / {pct(t, 99)} / {t.max():.2f} | "
                   f"{b(t)} | {pct(y, 50)} / {pct(y, 95)} / {pct(y, 99)} / {y.max():.2f} | {b(y)} | "
                   f"{sum(bad_unit(r) for r in rs)} |")
    out += ["", "By condition, declared trials with tilt or |yaw| at 2 deg or more (C and G pooled):", "",
            "| Machine | Condition | Declared | tilt >= 2 | tilt >= 2.5 | |yaw| >= 2 | |yaw| >= 2.5 |", "|---|---|---|---|---|---|---|"]
    for (m, cond), rs in sorted(group([r for r in rows if r["suite"] == "standard" and r["declared_success"]],
                                      ("backend", "condition")).items()):
        t = np.array([r["final_tilt_deg"] for r in rs])
        y = np.abs([r["final_yaw_deg"] for r in rs])
        if (t >= 2).sum() + (y >= 2).sum() == 0:
            continue
        out.append(f"| {m} | {cond} | {len(rs)} | {(t >= 2).sum()} | {(t >= 2.5).sum()} | {(y >= 2).sum()} | "
                   f"{(y >= 2.5).sum()} |")
    out += ["", "Yaw verdict path of each declared trial, and its true |yaw| (deg):", "",
            "| Machine | Path | Declared | |yaw| p50 / p95 / max | |yaw| > 2 (the wall-yaw tolerance) |", "|---|---|---|---|---|"]
    paths = defaultdict(list)
    for r in rows:
        if r["suite"] != "standard" or not r["declared_success"]:
            continue
        wy = [d for _, k, d in r["ev"] if k == "wall_yaw"]
        yc = [d for _, k, d in r["ev"] if k == "yaw"]
        if wy:
            p = "wall_yaw PASS after a turn" if any("turn" in d for d in wy) else "wall_yaw PASS"
            need = re.search(r">= (-?[\d.]+)", wy[-1])
            if need and float(need.group(1)) < 0:
                p += " (need < 0)"
        elif r["backend"] == "gantry":
            p = "yaw sweep"
        else:
            p = "no yaw check"
        paths[(r["backend"], p)].append(abs(r["final_yaw_deg"]))
    for (m, p), y in sorted(paths.items()):
        y = np.array(y)
        out.append(f"| {m} | {p} | {len(y)} | {pct(y, 50)} / {pct(y, 95)} / {y.max():.2f} | {(y > 2).sum()} |")
    sweeps = defaultdict(list)
    for r in rows:
        if r["suite"] != "standard" or not r["declared_success"] or r["backend"] != "gantry":
            continue
        for _, k, d in r["ev"]:
            m = re.search(r"limits \(([-+\d.]+),([-+\d.]+)\)", d) if k == "yaw_centering" else None
            if m:
                lim = max(abs(float(m.group(1))), abs(float(m.group(2))))
                sweeps["one limit at the 7.0 deg sweep end" if lim >= 6.99 else "both limits found"].append(
                    abs(r["final_yaw_deg"]))
    if sweeps:
        out += ["", "Gantry yaw sweeps of declared trials (events `yaw_centering`; the sweep always ends in SUCCESS):", "",
                "| Sweep | Declared | final |yaw| p95 / max |", "|---|---|---|"]
        for p, y in sorted(sweeps.items()):
            out.append(f"| {p} | {len(y)} | {pct(y, 95)} / {max(y):.2f} |")
    out += ["", "Tilt evidence at the declared seat (housing only; no check uses it): plug axis against R_corr, "
            "against true tilt:", "", "| Machine | Ctrl | Seats | measured p50 / p95 | true p50 / p95 | true >= 2.5 | of which measured >= 2.5 |",
            "|---|---|---|---|---|---|---|"]
    for (m, ctrl), rs in sorted(group([r for r in rows if r["suite"] == "standard"], ("backend", "controller")).items()):
        s = [x for r in rs for x in r["seats"][-1:]]
        mt = [x["meas_tilt"] for x in s]
        tt = [x["true_tilt"] for x in s]
        hi = [x for x in s if x["true_tilt"] >= 2.5]
        out.append(f"| {m} | {LABEL[ctrl]} | {len(s)} | {pct(mt, 50)} / {pct(mt, 95)} | {pct(tt, 50)} / {pct(tt, 95)} | "
                   f"{len(hi)} | {sum(x['meas_tilt'] >= 2.5 for x in hi)} |")
    return out


def item4(rows: list[dict]) -> list[str]:
    out = ["## Item 4: latch checks under the force floor (C and G)", "",
           "'Would fail': the unguarded evidence fails the bounds (axis > 2.5 deg and CoP > 0.875 or a failed check in "
           "the attempt). 'Correct catch': would fail and the true tilt is over 3.0 deg.", "",
           "| Machine | Ctrl | Path | Checks under the floor | F (N) min / max | Would fail | Correct catches dropped | True tilt > 3 (any) | Outcome of those trials |",
           "|---|---|---|---|---|---|---|---|---|"]
    for (m, ctrl), rs in sorted(group([r for r in rows if r["controller"] != "spiral_rcc_verify"
                                       and r["suite"] != "standard"], ("backend", "controller")).items()):
        by = defaultdict(list)
        for r in rs:
            for c in r["checks"]:
                if c["f_ax"] is None or c["f_ax"] < c["floor"]:
                    by[c["path"]].append((r, c))
        for p, lst in sorted(by.items()):
            f = [c["f_ax"] or 0.0 for _, c in lst]
            wf = [(r, c) for r, c in lst if c["would_fail"]]
            cc = [(r, c) for r, c in wf if c["true_tilt"] > 3.0]
            t3 = [(r, c) for r, c in lst if c["true_tilt"] > 3.0]
            oc = Counter(outcome(r) for r, _ in lst)
            out.append(f"| {m} | {LABEL[ctrl]} | {p} | {len(lst)} | {min(f):.1f} / {max(f):.1f} | {len(wf)} | {len(cc)} | "
                       f"{len(t3)} | {', '.join(f'{k} {v}' for k, v in oc.items())} |")
    out += ["", "Each check under the floor:", "",
            "| Machine | Ctrl | Seed | Condition | Trial | Path | F (N) | Measured | True | CoP edge | Would fail | Outcome | Final tilt |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["controller"] == "spiral_rcc_verify":
            continue
        for c in r["checks"]:
            if c["f_ax"] is None or c["f_ax"] < c["floor"]:
                out.append(f"| {r['backend']} | {LABEL[r['controller']]} | {r['base_seed']} | {r['condition']} | "
                           f"{r['trial_index']} | {c['path']} | {c['f_ax'] or 0.0:.1f} | {c['meas_tilt']:.2f} | "
                           f"{c['true_tilt']:.2f} | {c['edge']:.2f} | {c['would_fail']} | {outcome(r)} | "
                           f"{r['final_tilt_deg']:.2f} |")
    return out


def outcome(r: dict) -> str:
    if r["success"]:
        return "seated"
    if bad_unit(r):
        return "BAD UNIT"
    return r["failure_reason"] or "failed"


def group(rows, keys):
    out = defaultdict(list)
    for r in rows:
        out[tuple(r[k] for k in keys) if len(keys) > 1 else r[keys[0]]].append(r)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    args = ap.parse_args()
    rows = load(Path(args.folder))
    seeds = sorted({r["base_seed"] for r in rows})
    head = [f"# v0.2f tilt diagnosis: tables (frozen code, flags off; seeds {seeds}; {len(rows)} trials)", "",
            "Made by `experiments/v02f_tilt_tables.py` from `runs/*.jsonl.gz`. Development seeds only.", ""]
    print("\n".join(head + item1(rows) + [""] + item2(rows) + [""] + item3(rows) + [""] + item4(rows)))


if __name__ == "__main__":
    main()
