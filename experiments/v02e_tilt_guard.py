"""v0.2e tilt guard: every tilt verdict C, G and J take at a latch check, with the axial force of its window.

    python experiments/v02e_tilt_guard.py run --backend arm --suite latching,latch_spread --seeds 2026,2027 \\
        --trials 20 --controllers adaptive,adaptive_learned,spiral_rcc_verify --workers 1 --out arm_after.jsonl.gz
    python experiments/v02e_tilt_guard.py table --before arm_before.jsonl.gz,... --after arm_after.jsonl.gz,...

Run by path, the script tests the code on PYTHONPATH (the tree it is run from, or another checkout such as the
code before the guard): the collector stays the same, the controller code changes. Dev seeds 2026 and 2027 only.

One JSON object per trial: the trials.csv fields, and per latch check (``_begin_latch_verify``) the path into it,
the mean bias-corrected axial force of the window the tilt check reads (the recent samples less their first third,
as ``_tilt_evidence``), the evidence, the force floor of results/v0.2e_tilt_guard (computed from the controller's
config, also for code without the guard) and the logged verdict (PASS, FAIL, no verdict, or none). Wrappers read
controller state only; ground truth is not read.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

SEEDS = frozenset((2026, 2027))
IGNORE = {"wall_time_s"}
_TASK = None


def force_floor(v) -> float:
    c = v.cfg
    return float(c.cavity_tilt_lever_mm * c.insert_force_n / (c.tilt_check_edge_fraction * min(v.plug_half) * 1e3))


def instrument(ctrl) -> list[dict]:
    """Wrap the latch-check entry of C's code in ``ctrl`` (C, G, or J's verifier); returns the list it fills."""
    v = getattr(ctrl, "verifier", ctrl)
    checks: list[dict] = []
    orig = v._begin_latch_verify

    def begin_latch_verify(obs):
        recent = list(v._recent)[len(v._recent) // v.cfg.detect_discard_divisor:]
        f_ax = float(np.mean([o.force[2] for o in recent]) - v.bias_f[2]) if recent else None
        if v.phase == "held_reseat":
            path = "held_reseat"
        elif v.phase == "bottom_proof":
            held = v._proof_t_force is not None and obs.t - v._proof_t_force >= v.cfg.proof_push_s
            path = "proof" if held else "proof_timeout"
        elif v is not ctrl and not v._recent:
            path = "handover"
        else:
            path = f"detect:{v._trigger}"
        tilt, edge = v._tilt_evidence(obs)
        n_ev = len(v.events)
        cmd = orig(obs)
        logged = [e.detail for e in v.events[n_ev:] if e.kind == "tilt"]
        verdict = "none"
        if logged:
            d = logged[0]
            verdict = "PASS" if d.endswith("PASS") else "FAIL" if d.endswith("FAIL") else "no verdict"
        checks.append({"t": float(obs.t - v.t_start), "attempt": int(v.attempts), "path": path, "f_ax": f_ax,
                       "n": len(recent), "tilt_deg": float(np.degrees(tilt)), "edge": edge,
                       "floor": force_floor(v), "verdict": verdict, "tilt_check": bool(v.cfg.tilt_check)})
        return cmd

    v._begin_latch_verify = begin_latch_verify
    return checks


def _init() -> None:
    global _TASK
    from defex.tasks.insertion import InsertionTask
    from experiments.runner import make_backend

    os.environ.setdefault("OMP_NUM_THREADS", "1")
    _TASK = InsertionTask(backend=make_backend())


def all_conditions(suite: str):
    from defex.tasks.conditions import latch_spread_conditions, latching_conditions

    return {"latching": latching_conditions, "latch_spread": latch_spread_conditions}[suite]()


def run_job(job: tuple) -> list[dict]:
    from defex.control.registry import make_controller
    from defex.tasks.scenarios import sample_scenario
    from experiments.runner import nominal_socket_pose

    suite, cond_name, controller, seed, indices = job
    if _TASK is None:
        _init()
    cond = {c.name: c for c in all_conditions(suite)}[cond_name]
    nominal = nominal_socket_pose(cond, _TASK.fixture)
    out = []
    for i in indices:
        ctrl = make_controller(controller)
        checks = instrument(ctrl) if controller in C_FAMILY else []
        res = _TASK.run(ctrl, sample_scenario(cond, i, seed, nominal))
        row = res.to_row()
        row.update(base_seed=seed, suite=suite, backend=os.environ.get("DEFEX_BACKEND", "gantry"), checks=checks,
                   tilt_events=[[t, d] for t, k, d in res.events if k == "tilt"])
        out.append(row)
    return out


C_FAMILY = ("adaptive", "adaptive_learned", "spiral_rcc_verify")


def cmd_run(args) -> None:
    os.environ["DEFEX_BACKEND"] = args.backend
    seeds = [int(s) for s in args.seeds.split(",")]
    if not set(seeds) <= SEEDS:
        raise SystemExit(f"dev seeds 2026 and 2027 only, not {sorted(set(seeds) - SEEDS)}")
    conds = [(su, c.name) for su in args.suite.split(",") for c in all_conditions(su)]
    if args.conditions:
        conds = [(su, c) for su, c in conds if c in args.conditions.split(",")]
    idx = list(range(args.trials))
    jobs = [(su, c, ctrl, s, tuple(idx[k:k + args.chunk])) for s in seeds for su, c in conds
            for ctrl in args.controllers.split(",") for k in range(0, len(idx), args.chunk)]
    total = sum(len(j[4]) for j in jobs)
    import defex

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    meta = {"args": vars(args), "defex": str(Path(defex.__file__).parent), "trials": total}
    out.with_suffix("").with_suffix(".meta.json").write_text(json.dumps(meta, indent=1))
    t0, rows = time.time(), []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=_init) as pool:
        for fut in as_completed([pool.submit(run_job, j) for j in jobs]):
            rows.extend(fut.result())
            el = time.time() - t0
            print(f"\r  {len(rows)}/{total} trials, elapsed {el:.0f} s", end="", flush=True)
    print()
    rows.sort(key=lambda r: (r["base_seed"], r["suite"], r["condition"], r["controller"], r["trial_index"]))
    with gzip.open(out, "wt") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(f"wrote {out} ({defex.__file__})")


def load(paths: str) -> dict:
    rows = {}
    for p in paths.split(","):
        with gzip.open(p, "rt") as fh:
            for line in fh:
                r = json.loads(line)
                rows[(r["backend"], r["suite"], r["condition"], r["controller"], r["base_seed"], r["trial_index"])] = r
    return rows


def outcome(r: dict) -> str:
    if r["success"]:
        return "seated"
    return r["failure_reason"] or "failed"


def cmd_table(args) -> None:
    before, after = load(args.before), load(args.after)
    if before.keys() != after.keys():
        raise SystemExit(f"trial sets differ: {len(before.keys() ^ after.keys())} keys")
    cells: dict = defaultdict(Counter)
    paths_low: dict = defaultdict(Counter)
    changed, unexplained = [], []
    for k in sorted(before):
        b, a = before[k], after[k]
        cell = (k[0], k[1], k[3])
        n = cells[cell]
        n["trials"] += 1
        low_fail_before = False
        for c in b["checks"]:
            n["checks_before"] += 1
            if c["verdict"] in ("PASS", "FAIL"):
                n["verdicts_before"] += 1
            low = c["f_ax"] is None or c["f_ax"] < c["floor"]
            if low and c["verdict"] in ("PASS", "FAIL"):
                n["low_verdicts_before"] += 1
                n[f"low_{c['verdict']}_before"] += 1
                paths_low[(k[0], k[3])][c["path"]] += 1
                if c["verdict"] == "FAIL":
                    low_fail_before = True
            if c["verdict"] == "FAIL":
                n["fail_before"] += 1
        for c in a["checks"]:
            n["checks_after"] += 1
            n[{"PASS": "pass_after", "FAIL": "fail_after", "no verdict": "blocked_after"}.get(c["verdict"], "none")] += 1
        diff = [f for f in b if f not in IGNORE and f not in ("checks", "tilt_events") and b[f] != a[f]]
        if diff:
            n["changed"] += 1
            changed.append((k, outcome(b), outcome(a), low_fail_before, diff))
            if not low_fail_before:
                unexplained.append(k)
    out = ["| Machine | Suite | Controller | Trials | Latch checks before / after | Verdicts before | "
           "Verdicts under the floor before (PASS / FAIL) | Fails before / after | Blocked after | Trials changed |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    tot = Counter()
    for cell in sorted(cells):
        n = cells[cell]
        tot.update(n)
        out.append(f"| {cell[0]} | {cell[1]} | {cell[2]} | {n['trials']} | {n['checks_before']} / {n['checks_after']} | "
                   f"{n['verdicts_before']} | {n['low_verdicts_before']} ({n['low_PASS_before']} / {n['low_FAIL_before']}) "
                   f"| {n['fail_before']} / {n['fail_after']} | {n['blocked_after']} | {n['changed']} |")
    out.append(f"| all | | | {tot['trials']} | {tot['checks_before']} / {tot['checks_after']} | {tot['verdicts_before']} | "
               f"{tot['low_verdicts_before']} ({tot['low_PASS_before']} / {tot['low_FAIL_before']}) | "
               f"{tot['fail_before']} / {tot['fail_after']} | {tot['blocked_after']} | {tot['changed']} |")
    out += ["", "Verdicts under the floor before, by path into the latch check:", ""]
    for (m, ctrl), cnt in sorted(paths_low.items()):
        out.append(f"- {m} {ctrl}: " + ", ".join(f"{p} {x}" for p, x in sorted(cnt.items())))
    forces = [(k, c) for k, r in before.items() for c in r["checks"] if c["verdict"] in ("PASS", "FAIL")]
    out += ["", "Window axial force at every verdict before (N), by machine and path: n, min, p5, median", ""]
    by = defaultdict(list)
    for k, c in forces:
        by[(k[0], c["path"])].append(np.nan if c["f_ax"] is None else c["f_ax"])
    for (m, p), fs in sorted(by.items()):
        f = np.array(fs)
        ok = f[~np.isnan(f)]
        desc = f"{ok.min():.1f}, {np.percentile(ok, 5):.1f}, {np.median(ok):.1f}" if len(ok) else "-"
        out.append(f"- {m} {p}: {len(f)} ({int(np.isnan(f).sum())} with no samples); {desc}")
    out += ["", "Trials whose row changed (before -> after outcome; under-floor FAIL before?):", ""]
    for k, ob, oa, lf, diff in changed:
        out.append(f"- {k[0]} {k[1]} {k[2]} {k[3]} seed {k[4]} trial {k[5]}: {ob} -> {oa}; "
                   f"{'yes' if lf else 'NO'}; fields {','.join(diff)}")
    if not changed:
        out.append("- none")
    out += ["", f"Changed trials without an under-floor FAIL before: {len(unexplained)}"]
    print("\n".join(out))
    if unexplained:
        raise SystemExit(1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--backend", choices=["gantry", "arm"], default="arm")
    r.add_argument("--suite", default="latching,latch_spread")
    r.add_argument("--conditions", default="")
    r.add_argument("--controllers", default=",".join(C_FAMILY))
    r.add_argument("--seeds", default="2026,2027")
    r.add_argument("--trials", type=int, default=20)
    r.add_argument("--workers", type=int, default=1)
    r.add_argument("--chunk", type=int, default=5)
    r.add_argument("--out", required=True)
    t = sub.add_parser("table")
    t.add_argument("--before", required=True)
    t.add_argument("--after", required=True)
    args = ap.parse_args()
    cmd_run(args) if args.cmd == "run" else cmd_table(args)


if __name__ == "__main__":
    main()
