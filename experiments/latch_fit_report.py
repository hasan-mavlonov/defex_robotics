"""Overlay report for the latch-model fit: logged curves against the fitted model (v0.2f).

On the rig day:

    PYTHONPATH=. python -m experiments.latch_fit_report --csv push_pull_1.csv --csv push_pull_2.csv \
        [--disabled latch_disabled.csv] --out results/<session>/latch_fit

writes ``latch_fit.png`` (force against seat-referenced depth, logged and fitted, and the residual
against a +/-15% band) and ``latch_fit.json`` (parameters, per-move seat and force offset,
errors, the values to put in the connector JSON). Numpy and matplotlib only; no MuJoCo.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from defex.calibration.latch_fit import LatchFit, LoggedMove, fit_latch, latch_depths
from defex.config import ConnectorSpec

BAND_REL, BAND_FLOOR_N = 0.15, 0.5


def _engaged(move: LoggedMove, fit: LatchFit, k: int) -> np.ndarray:
    """Samples from 0.2 mm before the terminals engage to the end of the monotone pull."""
    lo = fit.seat_mm[k] - fit.params["terminal_wipe_mm"] - 0.2
    idx = np.arange(move.depth_mm.size)
    return (move.depth_mm >= lo) & (idx <= move.pull_end())


def band_stats(move: LoggedMove, fit: LatchFit, k: int) -> dict:
    sel = _engaged(move, fit, k)
    f, pred = move.fz_n[sel], fit.predict(move, k)[sel]
    band = np.maximum(BAND_REL * np.abs(f), BAND_FLOOR_N)
    inside = np.abs(pred - f) <= band
    i = move.turnaround()
    push = sel & (np.arange(sel.size) <= i) & (move.depth_mm < fit.seat_mm[k] - 0.02)
    peak_log = float(move.fz_n[push].max()) if push.any() else float("nan")
    peak_fit = float(fit.predict(move, k)[push].max()) if push.any() else float("nan")
    return {"within_band_fraction": float(inside.mean()), "samples": int(sel.sum()),
            "peak_logged_n": peak_log, "peak_fitted_n": peak_fit, "peak_rel_error": (peak_fit - peak_log) / peak_log}


def overlay(spec: ConnectorSpec, moves: list[LoggedMove], fit: LatchFit, path: Path, title: str = "",
            truth: list[np.ndarray] | None = None) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    seat = spec.socket.depth_mm
    fig, (ax, rx) = plt.subplots(2, 1, figsize=(7.0, 5.6), dpi=130, sharex=True,
                                 gridspec_kw={"height_ratios": [2.2, 1.0]})
    for k, m in enumerate(moves):
        sel = _engaged(m, fit, k)
        x = m.depth_mm - fit.seat_mm[k] + seat
        pred = fit.predict(m, k)
        tag = "" if len(moves) == 1 else f" {k + 1}" + ("" if m.latch else " (latch disabled)")
        ax.plot(x[sel], m.fz_n[sel], ".", ms=1.6, color="#2a78d6", alpha=0.55, label=f"logged{tag}" if k < 2 else None)
        ax.plot(x[sel], pred[sel], "-", lw=1.1, color="#eb6834", label="fitted model" if k == 0 else None)
        if truth is not None:
            ax.plot(x[sel], truth[k][sel], "--", lw=0.9, color="#444444", label="true model" if k == 0 else None)
        if k == 0:
            i = m.turnaround()
            idx = np.arange(m.depth_mm.size)
            for j, seg in enumerate((sel & (idx <= i), sel & (idx > i))):
                if not seg.any():
                    continue
                order = np.argsort(x[seg])
                band = np.maximum(BAND_REL * np.abs(m.fz_n[seg]), BAND_FLOOR_N)[order]
                rx.fill_between(x[seg][order], -band, band, color="#d0d0d0" if j == 0 else "#e6e6e6", lw=0,
                                alpha=0.8, label="+/-15% of logged (0.5 N floor): push, pull" if j == 0 else None)
        rx.plot(x[sel], pred[sel] - m.fz_n[sel], ".", ms=1.6, color="#eb6834", alpha=0.6,
                label="fit - logged" if k == 0 else None)
    onset, lpeak, snap = latch_depths(fit.params, seat)
    for d, lab in ((seat - fit.params["terminal_wipe_mm"], "terminals"), (onset, "latch onset"), (snap, "snap"),
                   (seat, "seat")):
        ax.axvline(d, color="#999999", lw=0.6, ls=":")
        ax.text(d, ax.get_ylim()[1] * 0.97, lab, fontsize=6, rotation=90, va="top", ha="right", color="#555555")
    if spec.mating is not None:
        ax.axhline(spec.mating.mating_force_max_n, color="#999999", lw=0.6, ls="--")
        ax.text(ax.get_xlim()[0], spec.mating.mating_force_max_n, " datasheet max mating force", fontsize=6,
                va="bottom", color="#555555")
    ax.set_ylabel("axial force, out of socket (N)")
    ax.set_title(title or f"Latch fit, {spec.name}: median |error| {fit.median_abs_error_n:.2f} N", fontsize=9)
    ax.legend(fontsize=7, loc="lower left")
    ax.grid(alpha=0.25)
    rx.set_xlabel("depth below mouth, seat-referenced (mm)")
    rx.set_ylabel("residual (N)")
    rx.set_ylim(-6, 6)
    rx.legend(fontsize=7, loc="lower left")
    rx.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def recovery_plot(spec: ConnectorSpec, part_set, path: Path) -> None:
    """Synthetic case: simulate the nominal part's push and pull, fit, overlay with the true model."""
    from defex.calibration.latch_fit import model_force
    from experiments.latch_fit_recovery import truth_params
    from experiments.latch_fit_sim import PushPull, simulate_logged_move

    m, _ = simulate_logged_move(spec, PushPull(), part_set.variation, depth_offset_mm=part_set.depth_offset_mm,
                                seed=part_set.sensor_seed)
    fit = fit_latch(spec, [m], seed=2026)
    i = m.turnaround()
    pull = np.arange(m.depth_mm.size) > i
    d_turn = float(np.median(m.depth_mm[max(0, i - 5):i + 6]))
    true = model_force(m.depth_mm, pull, d_turn, truth_params(spec, part_set.variation),
                       spec.socket.depth_mm + part_set.depth_offset_mm, True, fit.floor_stiffness_n_per_mm)
    true = true + fit.force_offset_n[0]
    overlay(spec, [m], fit, path, truth=[true],
            title=f"Synthetic recovery, {part_set.name} part (MuJoCo gantry, 1 mm/s push + guarded pull)")


def fit_to_json(spec: ConnectorSpec, fit: LatchFit) -> dict:
    p = fit.params
    depths = fit.mating_depths_mm(spec.socket.depth_mm)
    n = spec.mating.circuits
    return {
        "fitted": list(fit.free), "params": p, "seat_mm": fit.seat_mm, "force_offset_n": fit.force_offset_n,
        "floor_stiffness_n_per_mm": fit.floor_stiffness_n_per_mm, "median_abs_error_n": fit.median_abs_error_n,
        "rms_error_n": fit.rms_error_n, "noise_n": fit.noise_n,
        "connector_json_model": {
            "terminal_peak_per_circuit_n": p["terminal_peak_n"] / n, "terminal_slide_per_circuit_n": p["terminal_slide_n"] / n,
            "terminal_lead_mm": p["terminal_lead_mm"], "latch_onset_depth_mm": depths["latch_onset_depth_mm"],
            "latch_peak_depth_mm": depths["latch_peak_depth_mm"], "latch_peak_force_n": p["latch_peak_n"],
            "latch_snap_depth_mm": depths["latch_snap_depth_mm"], "latch_post_snap_stroke_mm": p["post_snap_stroke_mm"],
        },
        "connector_json_mating": {"terminal_wipe_mm": p["terminal_wipe_mm"]},
        "not_in_connector_json": {k: p[k] for k in ("snap_drop", "latch_play_mm", "latch_stiffness_n_per_mm", "bristle_mm")},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default="microfit3_4ckt")
    ap.add_argument("--csv", action="append", default=[], help="push-click (+ pull) log, t_s,depth_mm,fz_n")
    ap.add_argument("--disabled", action="append", default=[], help="log of a push with the latch disabled")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    spec = ConnectorSpec.load(a.spec)
    moves = [LoggedMove.read_csv(Path(p)) for p in a.csv] + [LoggedMove.read_csv(Path(p), latch=False) for p in a.disabled]
    fit = fit_latch(spec, moves)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    overlay(spec, moves, fit, out / "latch_fit.png")
    rep = fit_to_json(spec, fit)
    rep["band"] = [band_stats(m, fit, k) for k, m in enumerate(moves)]
    (out / "latch_fit.json").write_text(json.dumps(rep, indent=1, default=float))
    print(json.dumps(rep["connector_json_model"], indent=1))


if __name__ == "__main__":
    main()
