"""Turn a benchmark run into plots, a dashboard and a Markdown report.

Usage:
    python -m experiments.evaluate results/robustness
    python -m experiments.evaluate results/robustness --theme dark

Reads ``trials.csv`` only, so it can be re-run on any saved run. Every number
plotted is computed from the logged trials (nothing is hard-coded).

Colour use follows a validated categorical palette (first three slots, checked
all-pairs for colour-vision deficiency in light and dark mode). Colour follows
the controller, never its rank.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

from defex.config import ConnectorSpec, SafetyConfig  # noqa: E402
from defex.logging.metrics import TrialResult, read_trials_csv, summarize, wilson_interval  # noqa: E402
from defex.tasks.conditions import MODERATE  # noqa: E402

CONTROLLER_ORDER = ["fixed", "correction", "adaptive"]
LABELS = {"fixed": "A: Fixed trajectory", "correction": "B: Vision correction", "adaptive": "C: Defex adaptive"}
SHORT = {"fixed": "A Fixed", "correction": "B Vision", "adaptive": "C Defex"}

THEMES = {
    "light": {
        "surface": "#fcfcfb",
        "page": "#f9f9f7",
        "ink": "#0b0b0b",
        "ink2": "#52514e",
        "muted": "#898781",
        "grid": "#e1e0d9",
        "axis": "#c3c2b7",
        "series": {"fixed": "#2a78d6", "correction": "#1baf7a", "adaptive": "#eb6834"},
        "critical": "#d03b3b",
        "warning": "#fab219",
    },
    "dark": {
        "surface": "#1a1a19",
        "page": "#0d0d0d",
        "ink": "#f0efec",
        "ink2": "#c3c2b7",
        "muted": "#898781",
        "grid": "#2c2c2a",
        "axis": "#383835",
        "series": {"fixed": "#3987e5", "correction": "#199e70", "adaptive": "#d95926"},
        "critical": "#d03b3b",
        "warning": "#fab219",
    },
}

GROUPS = [
    ("lateral", "Lateral socket error", "error (mm)"),
    ("angular_yaw", "Yaw error (about insertion axis)", "error (deg)"),
    ("angular_tilt", "Tilt error (axis misalignment)", "error (deg)"),
    ("pose_uncertainty", "Vision pose uncertainty", "lateral sigma (mm)"),
    ("contact_variation", "Contact friction", "friction coefficient"),
]


def _level(cond: str) -> float:
    tail = cond.split("_")[-1]
    num = "".join(ch for ch in tail if ch.isdigit() or ch == ".")
    return float(num) if num else float("nan")


def style_axes(ax, th: dict, ygrid: bool = True, xgrid: bool = False) -> None:
    ax.set_facecolor(th["surface"])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(th["axis"])
        ax.spines[side].set_linewidth(0.8)
    ax.tick_params(colors=th["muted"], labelcolor=th["ink2"], labelsize=8, length=0, pad=4)
    ax.xaxis.label.set_color(th["ink2"])
    ax.yaxis.label.set_color(th["ink2"])
    ax.xaxis.label.set_size(8.5)
    ax.yaxis.label.set_size(8.5)
    if ygrid:
        ax.yaxis.grid(True, color=th["grid"], linewidth=0.6, linestyle="-")
    if xgrid:
        ax.xaxis.grid(True, color=th["grid"], linewidth=0.6, linestyle="-")
    ax.set_axisbelow(True)


class BarLayer:
    """Bars with a rounded data-end (radius in pixels) and a square baseline end.

    Rounding must be specified in pixels: on axes whose x and y data scales differ,
    a data-unit radius would distort. Bars are therefore collected first and drawn
    once the figure layout and axis limits are final (``draw``).
    """

    def __init__(self, radius_px: float = 6.0) -> None:
        self.radius_px = radius_px
        self.items: list[tuple] = []

    def vbar(self, ax, x: float, height: float, width: float, color: str, y0: float = 0.0) -> None:
        if height > 0:
            self.items.append((ax, "v", x - width / 2, y0, width, height, color))

    def hbar(self, ax, y: float, width: float, height: float, color: str, x0: float = 0.0) -> None:
        if width > 0:
            self.items.append((ax, "h", x0, y - height / 2, width, height, color))

    def draw(self, fig) -> None:
        fig.canvas.draw()
        for ax, kind, x, y, w, h, color in self.items:
            bb = ax.get_window_extent()
            x0, x1 = ax.get_xlim()
            y0, y1 = ax.get_ylim()
            xr = abs(x1 - x0) / max(bb.width, 1.0)  # data units per pixel
            yr = abs(y1 - y0) / max(bb.height, 1.0)
            r_x = self.radius_px * xr
            r_y = self.radius_px * yr
            if kind == "v":
                r_x = min(r_x, w / 2)
                r_y = min(r_y, h / 2)
                patch = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r_x}",
                                       mutation_aspect=r_y / max(r_x, 1e-12), linewidth=0, facecolor=color)
                base = Rectangle((x, y), w, min(h, 2 * r_y), linewidth=0, facecolor=color)
            else:
                r_y = min(r_y, h / 2)
                r_x = min(r_x, w / 2)
                patch = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r_x}",
                                       mutation_aspect=r_y / max(r_x, 1e-12), linewidth=0, facecolor=color)
                base = Rectangle((x, y), min(w, 2 * r_x), h, linewidth=0, facecolor=color)
            ax.add_patch(patch)
            ax.add_patch(base)


def _cell(summary: list[dict], cond: str, ctrl: str) -> dict | None:
    for s in summary:
        if s["condition"] == cond and s["controller"] == ctrl:
            return s
    return None


def _controllers(results: list[TrialResult]) -> list[str]:
    present = {r.controller for r in results}
    return [c for c in CONTROLLER_ORDER if c in present]


# ----------------------------------------------------------------------------- plots


def plot_success(summary: list[dict], results: list[TrialResult], path: Path, th: dict) -> None:
    ctrls = _controllers(results)
    conds_by_group = defaultdict(list)
    for s in summary:
        if s["condition"] not in conds_by_group[s["group"]]:
            conds_by_group[s["group"]].append(s["condition"])
    fig, axes = plt.subplots(2, 4, figsize=(15, 7.2), dpi=150, facecolor=th["page"])
    axes = axes.ravel()
    bars = BarLayer()
    panels = [("nominal", "Nominal", None)] + GROUPS + [("generalization", "Generalization (unseen)", None)]
    n_per = max((s["n"] for s in summary), default=0)
    for ax, (group, title, xlabel) in zip(axes, panels):
        style_axes(ax, th)
        conds = conds_by_group.get(group, [])
        ax.set_title(title, color=th["ink"], fontsize=10, loc="left", pad=8)
        if not conds:
            ax.set_visible(False)
            continue
        if xlabel is not None:
            conds = sorted(conds, key=_level)
            if group in ("lateral", "angular_yaw", "angular_tilt") and conds_by_group.get("nominal"):
                conds = ["nominal", *conds]  # the aligned socket is the zero-error point
            xs = np.array([0.0 if c == "nominal" else _level(c) for c in conds])
            span = (xs.max() - xs.min()) or 1.0
            for k, ctrl in enumerate(ctrls):
                dx = (k - (len(ctrls) - 1) / 2) * 0.018 * span
                ys, lo, hi = [], [], []
                for c in conds:
                    cell = _cell(summary, c, ctrl)
                    ys.append(cell["success_rate"] * 100)
                    lo.append(cell["success_ci_low"] * 100)
                    hi.append(cell["success_ci_high"] * 100)
                col = th["series"][ctrl]
                for xx, l_, h_ in zip(xs + dx, lo, hi):
                    ax.plot([xx, xx], [l_, h_], color=col, lw=0.9, alpha=0.75, solid_capstyle="butt")
                ax.plot(xs + dx, ys, color=col, linewidth=1.3, solid_capstyle="round", solid_joinstyle="round")
                ax.plot(xs + dx, ys, "o", color=col, markersize=5, markeredgecolor=th["surface"], markeredgewidth=1.0)
            ax.set_xticks(xs)
            ax.set_xticklabels([f"{x:g}" for x in xs])
            ax.set_xlabel(xlabel)
            ax.set_xlim(xs.min() - 0.08 * span, xs.max() + 0.08 * span)
        else:
            width = 0.22
            for k, ctrl in enumerate(ctrls):
                for j, c in enumerate(conds):
                    cell = _cell(summary, c, ctrl)
                    x = j + (k - (len(ctrls) - 1) / 2) * (width + 0.04)
                    bars.vbar(ax, x, cell["success_rate"] * 100, width, th["series"][ctrl])
                    ax.plot([x, x], [cell["success_ci_low"] * 100, cell["success_ci_high"] * 100], color=th["ink2"], lw=0.8)
                    if cell["success_rate"] == 0:
                        # A zero-height bar is invisible: say so, or the controller looks absent.
                        ax.text(x, 6, "0%", color=th["ink2"], fontsize=7.5, ha="center", va="bottom")
            ax.set_xticks(range(len(conds)))
            ax.set_xticklabels([c.replace("generalization_", "") for c in conds])
            ax.set_xlim(-0.6, len(conds) - 0.4)
        ax.set_ylim(0, 103)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_yticklabels(["0", "25", "50", "75", "100%"])
    axes[-1].set_visible(False)
    handles = [plt.Line2D([], [], color=th["series"][c], marker="o", lw=1.5, markersize=6) for c in ctrls]
    fig.legend(handles, [LABELS[c] for c in ctrls], loc="upper right", ncol=len(ctrls), frameon=False, fontsize=9,
               labelcolor=th["ink"], bbox_to_anchor=(0.985, 0.975))
    fig.suptitle(
        f"Insertion success rate by condition  (n = {n_per} paired trials per point; whiskers: 95% Wilson CI)",
        x=0.012, y=0.97, ha="left", color=th["ink"], fontsize=11.5,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    bars.draw(fig)
    fig.savefig(path, facecolor=th["page"])
    plt.close(fig)


def plot_cycle_and_force(results: list[TrialResult], path: Path, th: dict) -> None:
    ctrls = _controllers(results)
    safety = SafetyConfig()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8), dpi=150, facecolor=th["page"])
    # Cycle time of successful trials, pooled over conditions
    style_axes(ax1, th)
    data = [[r.cycle_time_s for r in results if r.controller == c and r.success] for c in ctrls]
    _strip_box(ax1, data, ctrls, th)
    ax1.set_ylabel("cycle time of successful insertions (s)")
    ax1.set_title("Cycle time (successful trials, all conditions)", color=th["ink"], fontsize=10, loc="left")
    # Peak contact force, all trials
    style_axes(ax2, th)
    data = [[r.peak_contact_force_n for r in results if r.controller == c] for c in ctrls]
    _strip_box(ax2, data, ctrls, th)
    for val, label in (
        (safety.protective_stop_force_n, "protective stop (measured F/T)"),
        (safety.damage_contact_force_n, "damage threshold (judged on the 10 ms average; dots are single-sample peaks)"),
    ):
        ax2.axhline(val, color=th["critical"], lw=0.9)
        ax2.text(len(ctrls) - 0.45, val + 0.6, label, color=th["ink2"], fontsize=7.5, ha="right", va="bottom")
    ax2.set_ylabel("peak contact force on connector (N, ground truth)")
    ax2.set_title("Peak contact force (all trials, all conditions)", color=th["ink"], fontsize=10, loc="left")
    fig.tight_layout()
    fig.savefig(path, facecolor=th["page"])
    plt.close(fig)


def _strip_box(ax, data: list[list[float]], ctrls: list[str], th: dict) -> None:
    rng = np.random.default_rng(0)
    for k, (vals, ctrl) in enumerate(zip(data, ctrls)):
        if not vals:
            continue
        v = np.asarray(vals)
        jitter = rng.uniform(-0.18, 0.18, v.size)
        ax.scatter(np.full(v.size, k) + jitter, v, s=6, color=th["series"][ctrl], alpha=0.35, linewidths=0)
        q1, med, q3 = np.percentile(v, [25, 50, 75])
        ax.plot([k - 0.28, k + 0.28], [med, med], color=th["ink"], lw=1.6, solid_capstyle="round")
        ax.plot([k, k], [q1, q3], color=th["ink"], lw=0.9)
        ax.text(k + 0.31, med, f"{med:.1f}", color=th["ink"], fontsize=8, va="center")
    ax.set_xticks(range(len(ctrls)))
    ax.set_xticklabels([LABELS[c] for c in ctrls])
    ax.set_xlim(-0.6, len(ctrls) - 0.3)


def plot_recovery(results: list[TrialResult], path: Path, th: dict) -> None:
    ad = [r for r in results if r.controller == "adaptive"]
    if not ad:
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.6), dpi=150, facecolor=th["page"],
                                   gridspec_kw={"width_ratios": [1, 1.6]})
    bars = BarLayer()
    style_axes(ax1, th)
    max_r = max(r.retries for r in ad)
    xs = np.arange(0, max_r + 1)
    succ = np.array([sum(1 for r in ad if r.retries == x and r.success) for x in xs])
    fail = np.array([sum(1 for r in ad if r.retries == x and not r.success) for x in xs])
    col = th["series"]["adaptive"]
    top = max(int((succ + fail).max()), 1)
    gap = top * 0.012
    for x, s_, f_ in zip(xs, succ, fail):
        if s_:
            bars.vbar(ax1, x, s_, 0.6, col)
        if f_:
            bars.vbar(ax1, x, f_, 0.6, th["muted"], y0=s_ + (gap if s_ else 0.0))
        if s_ + f_:
            ax1.text(x, s_ + f_ + gap * 2.5, f"{s_ + f_}", ha="center", va="bottom", color=th["ink2"], fontsize=7.5)
    ax1.set_xticks(xs)
    ax1.set_xlabel("recovery cycles used (retract, correct, retry)")
    ax1.set_ylabel("trials")
    ax1.set_title("Controller C: recoveries per trial", color=th["ink"], fontsize=10, loc="left")
    ax1.legend([Rectangle((0, 0), 1, 1, color=col), Rectangle((0, 0), 1, 1, color=th["muted"])],
               ["succeeded", "failed"], frameon=False, fontsize=8, labelcolor=th["ink2"])
    ax1.set_xlim(-0.6, max_r + 0.6)
    ax1.set_ylim(0, top * 1.12)
    style_axes(ax2, th, ygrid=False, xgrid=True)
    by_cond = defaultdict(list)
    for r in ad:
        if r.retries > 0:
            by_cond[r.condition].append(r.success)
    conds = [c for c in dict.fromkeys(r.condition for r in ad) if by_cond.get(c)]
    for j, c in enumerate(conds):
        k = sum(by_cond[c])
        n = len(by_cond[c])
        lo, hi = wilson_interval(k, n)
        bars.hbar(ax2, j, 100 * k / n, 0.62, col)
        ax2.plot([lo * 100, hi * 100], [j, j], color=th["ink2"], lw=0.8)
        ax2.text(101.5, j, f"{k}/{n}", color=th["ink2"], fontsize=7.5, va="center")
    ax2.set_yticks(range(len(conds)))
    ax2.set_yticklabels(conds, fontsize=7.5)
    ax2.set_ylim(len(conds) - 0.5, -0.5)
    ax2.set_xlim(0, 112)
    ax2.set_xticks([0, 25, 50, 75, 100])
    ax2.set_xticklabels(["0", "25", "50", "75", "100%"])
    ax2.set_title("Controller C: success rate of trials that needed recovery (95% CI)", color=th["ink"], fontsize=10,
                  loc="left")
    fig.tight_layout()
    bars.draw(fig)
    fig.savefig(path, facecolor=th["page"])
    plt.close(fig)


def plot_failures(results: list[TrialResult], path: Path, th: dict) -> None:
    ctrls = _controllers(results)
    counts = {c: Counter(r.failure_reason for r in results if r.controller == c and not r.success) for c in ctrls}
    reasons = Counter()
    for c in ctrls:
        reasons.update(counts[c])
    if not reasons:
        return
    reasons_sorted = [r for r, _ in reasons.most_common()]
    fig, ax = plt.subplots(figsize=(11, 0.55 * len(reasons_sorted) + 1.6), dpi=150, facecolor=th["page"])
    bars = BarLayer(radius_px=4.0)
    style_axes(ax, th, ygrid=False, xgrid=True)
    h = 0.24
    n_total = {c: sum(1 for r in results if r.controller == c) for c in ctrls}
    for j, reason in enumerate(reasons_sorted):
        for k, c in enumerate(ctrls):
            y = j + (k - (len(ctrls) - 1) / 2) * (h + 0.03)
            v = 100.0 * counts[c][reason] / max(n_total[c], 1)
            bars.hbar(ax, y, v, h, th["series"][c])
            if counts[c][reason]:
                ax.text(v + 0.3, y, f"{counts[c][reason]}", color=th["ink2"], fontsize=7, va="center")
    ax.set_yticks(range(len(reasons_sorted)))
    ax.set_yticklabels([r.replace("_", " ") for r in reasons_sorted], fontsize=8)
    ax.set_ylim(len(reasons_sorted) - 0.5, -0.5)
    ax.set_xlabel("share of all trials of that controller (%)")
    ax.set_title("Failure reasons (all conditions pooled; labels are trial counts)", color=th["ink"], fontsize=10, loc="left")
    handles = [Rectangle((0, 0), 1, 1, color=th["series"][c]) for c in ctrls]
    ax.legend(handles, [LABELS[c] for c in ctrls], frameon=False, fontsize=8, labelcolor=th["ink"], loc="lower right")
    xmax = max(100.0 * counts[c][r] / max(n_total[c], 1) for c in ctrls for r in reasons_sorted)
    ax.set_xlim(0, xmax * 1.15 + 1)
    fig.tight_layout()
    bars.draw(fig)
    fig.savefig(path, facecolor=th["page"])
    plt.close(fig)


def plot_dashboard(summary: list[dict], results: list[TrialResult], path: Path, th: dict) -> None:
    """Investor dashboard (16:9, 1920x1080)."""
    ctrls = _controllers(results)
    fig = plt.figure(figsize=(12.8, 7.2), dpi=150, facecolor=th["page"])
    bars = BarLayer()
    n_trials = len(results)
    n_conds = len({r.condition for r in results})
    n_per = max((s["n"] for s in summary), default=0)
    fig.text(0.035, 0.935, "Defex Adaptive Insertion Engine  ·  V0.1 simulation benchmark", color=th["ink"], fontsize=17)
    fig.text(0.035, 0.893,
             f"{n_trials:,} simulated insertions  ·  {n_conds} test conditions x {n_per} paired randomized trials  ·  "
             "MuJoCo physics, ground-truth scoring", color=th["ink2"], fontsize=9.5)
    # Hero tiles: overall success per controller (the tile swatch doubles as the legend)
    tile_w, tile_h, top = 0.297, 0.175, 0.665
    for k, c in enumerate(ctrls):
        rs = [r for r in results if r.controller == c]
        k_s = sum(r.success for r in rs)
        rate = k_s / max(len(rs), 1)
        lo, hi = wilson_interval(k_s, len(rs))
        stops = sum(r.protective_stop for r in rs)
        x0 = 0.035 + k * (tile_w + 0.0165)
        ax = fig.add_axes((x0, top, tile_w, tile_h))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.05",
                                    mutation_aspect=tile_w / tile_h * 12.8 / 7.2, facecolor=th["surface"],
                                    edgecolor=th["grid"], lw=0.8))
        ax.add_patch(Rectangle((0.045, 0.71), 0.018, 0.15, color=th["series"][c], lw=0))
        ax.text(0.085, 0.785, LABELS[c], color=th["ink2"], fontsize=10, va="center")
        ax.text(0.045, 0.40, f"{rate * 100:.1f}%", color=th["ink"], fontsize=30, va="center", fontweight="bold")
        ax.text(0.045, 0.12, f"{k_s:,} of {len(rs):,} trials  ·  95% CI {lo * 100:.1f}-{hi * 100:.1f}%  ·  "
                f"{stops:,} safety stop{'' if stops == 1 else 's'}", color=th["muted"], fontsize=7.3)
    # Charts row: success curves + gentleness
    def panel_title(ax, title: str, note: str) -> None:
        ax.set_title(title, color=th["ink"], fontsize=10, loc="left", pad=19)
        ax.text(0.0, 1.02, note, transform=ax.transAxes, color=th["muted"], fontsize=7.3, va="bottom")

    spec = ConnectorSpec.load("rect_12x8")
    capture_mm = spec.socket.clearance_mm + spec.socket.chamfer_mm
    notes = {
        "lateral": ("Success vs socket offset", "exact offset, random direction; nominal vision", "socket offset (mm)"),
        "pose_uncertainty": (
            "Success vs vision error",
            f"socket also randomly off by up to {MODERATE.lateral_mm:g} mm, {MODERATE.yaw_deg:g} deg yaw, "
            f"{MODERATE.tilt_deg:g} deg tilt",
            "vision sigma (mm)",
        ),
    }
    for j, (group, _, _) in enumerate([GROUPS[0], GROUPS[3]]):
        ax = fig.add_axes((0.055 + j * 0.315, 0.10, 0.255, 0.43))
        style_axes(ax, th)
        conds = sorted({s["condition"] for s in summary if s["group"] == group}, key=_level)
        if not conds:
            ax.set_visible(False)
            continue
        if group == "lateral" and any(s["condition"] == "nominal" for s in summary):
            conds = ["nominal", *conds]  # the aligned socket is the 0 mm point
        xs = np.array([0.0 if c == "nominal" else _level(c) for c in conds])
        span = (xs.max() - xs.min()) or 1.0
        if group == "lateral":
            # The fixed program only works inside the chamfer's capture range: mark the cliff.
            ax.axvline(capture_mm, color=th["muted"], lw=0.9, ls=(0, (3, 3)), zorder=1)
            ax.text(capture_mm - 0.12, 50, f"lead-in capture\nlimit {capture_mm:g} mm", color=th["ink2"],
                    fontsize=7.3, va="center", ha="right")
        for k, c in enumerate(ctrls):
            dx = (k - (len(ctrls) - 1) / 2) * 0.012 * span
            ys = [(_cell(summary, cond, c) or {"success_rate": np.nan})["success_rate"] * 100 for cond in conds]
            ax.plot(xs + dx, ys, color=th["series"][c], lw=1.4, solid_capstyle="round", zorder=3)
            ax.plot(xs + dx, ys, "o", color=th["series"][c], markersize=5.5, markeredgecolor=th["surface"],
                    markeredgewidth=1.0, zorder=4)
        title, note, xlabel = notes[group]
        ax.set_xticks(xs)
        ax.set_xticklabels([f"{x:g}" for x in xs])
        ax.set_xlabel(xlabel)
        ax.set_xlim(xs.min() - 0.08 * span, xs.max() + 0.08 * span)
        ax.set_ylim(0, 104)
        ax.set_yticks([0, 50, 100])
        ax.set_yticklabels(["0", "50", "100%"])
        panel_title(ax, title, note)
    ax = fig.add_axes((0.70, 0.10, 0.265, 0.43))
    style_axes(ax, th, ygrid=False, xgrid=True)
    rows = []
    for c in ctrls:
        rs = [r for r in results if r.controller == c]
        rows.append((c, float(np.percentile([r.peak_contact_force_n for r in rs], 95))))
    stop_n = SafetyConfig().protective_stop_force_n
    ax.axvline(stop_n, color=th["critical"], lw=0.9, ls=(0, (3, 3)), zorder=1)
    ax.text(stop_n - 0.6, -0.5, f"safety stop {stop_n:g} N", color=th["critical"], fontsize=7.3, ha="right", va="center")
    for k, (c, v) in enumerate(rows):
        bars.hbar(ax, k, v, 0.46, th["series"][c])
        ax.text(v + 0.6, k, f"{v:.1f} N", color=th["ink"], fontsize=9, va="center")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([SHORT[c] for c, _ in rows], fontsize=9)
    ax.set_ylim(len(rows) - 0.4, -0.75)
    ax.set_xlim(0, max(max(v for _, v in rows), stop_n) * 1.32 + 1)
    ax.set_xlabel("contact force (N)")
    panel_title(ax, "Peak contact force (lower is gentler)", "95th percentile of each trial's peak, all conditions")
    bars.draw(fig)
    fig.savefig(path, facecolor=th["page"])
    plt.close(fig)


# ----------------------------------------------------------------------------- report


def write_report(summary: list[dict], results: list[TrialResult], path: Path) -> str:
    ctrls = _controllers(results)
    lines = [
        "| Condition | " + " | ".join(f"{LABELS[c]} success" for c in ctrls) + " | C median cycle (s) | C median peak force (N) | C recovery success |",
        "|---|" + "---|" * len(ctrls) + "---|---|---|",
    ]
    for cond in dict.fromkeys(r.condition for r in results):
        cells = []
        for c in ctrls:
            s = _cell(summary, cond, c)
            cells.append(f"{s['success_rate'] * 100:.0f}% ({s['success_ci_low'] * 100:.0f}-{s['success_ci_high'] * 100:.0f})")
        sc = _cell(summary, cond, "adaptive")
        if sc:
            ct = sc["cycle_time_s_success"]["median"]
            pf = sc["peak_contact_force_n"]["median"]
            rec = sc["recovery_success_rate"]
            nrec = sc["trials_with_recovery"]
            rec_s = "n/a" if nrec == 0 else f"{rec * 100:.0f}% of {nrec}"
            lines.append(f"| {cond} | " + " | ".join(cells) + f" | {ct:.2f} | {pf:.1f} | {rec_s} |")
        else:
            lines.append(f"| {cond} | " + " | ".join(cells) + " | | | |")
    overall = ["", "| Overall | " + " | ".join(LABELS[c] for c in ctrls) + " |", "|---|" + "---|" * len(ctrls)]
    rows = {
        "success rate": lambda rs: f"{100 * np.mean([r.success for r in rs]):.1f}%",
        "median cycle time, successes (s)": lambda rs: (
            f"{np.median([r.cycle_time_s for r in rs if r.success]):.2f}" if any(r.success for r in rs) else "n/a"
        ),
        "median peak contact force (N)": lambda rs: f"{np.median([r.peak_contact_force_n for r in rs]):.1f}",
        "95th pct peak contact force (N)": lambda rs: f"{np.percentile([r.peak_contact_force_n for r in rs], 95):.1f}",
        "protective stops": lambda rs: f"{sum(r.protective_stop for r in rs)}",
        "max measured wrist torque (N m; stop at 0.6)": lambda rs: f"{max(r.peak_measured_torque_nm for r in rs):.3f}",
        "mean retries": lambda rs: f"{np.mean([r.retries for r in rs]):.2f}",
        "max penetration (mm)": lambda rs: f"{max(r.max_penetration_mm for r in rs):.4f}",
        "false accepts (declared success, not seated)": lambda rs: (
            f"{sum(1 for r in rs if r.declared_success and not r.gt_seated)}"
            if any(r.declared_success is not None for r in rs)
            else "n/a (no self-verification)"
        ),
    }
    for label, fn in rows.items():
        overall.append(f"| {label} | " + " | ".join(fn([r for r in results if r.controller == c]) for c in ctrls) + " |")
    text = "\n".join(lines + overall) + "\n"
    path.write_text(text)
    return text


def evaluate(run_dir: Path, theme: str = "light") -> None:
    run_dir = Path(run_dir)
    results = read_trials_csv(run_dir / "trials.csv")
    summary = summarize(results)
    plots = run_dir / "plots"
    plots.mkdir(parents=True, exist_ok=True)
    th = THEMES[theme]
    plot_success(summary, results, plots / "success_rate.png", th)
    plot_cycle_and_force(results, plots / "cycle_time_and_force.png", th)
    plot_recovery(results, plots / "recovery.png", th)
    plot_failures(results, plots / "failure_reasons.png", th)
    plot_dashboard(summary, results, plots / "dashboard_dark.png", THEMES["dark"])
    plot_dashboard(summary, results, plots / "dashboard_light.png", THEMES["light"])
    write_report(summary, results, run_dir / "report.md")
    print(f"wrote plots to {plots} and {run_dir / 'report.md'}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Plot and summarize a DAIE benchmark run.")
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--theme", choices=sorted(THEMES), default="light")
    args = ap.parse_args()
    evaluate(args.run_dir, args.theme)


if __name__ == "__main__":
    main()
