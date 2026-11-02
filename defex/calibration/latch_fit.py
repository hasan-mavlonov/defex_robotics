"""Fit the terminal and latch model (defex/sim/mating.py) to logged force-depth curves (W7, v0.2f).

Input: one or more logged moves of the same part, each a CSV ``t_s,depth_mm,fz_n``
(hardware/TEST_PROTOCOL.md section 4: depth positive into the socket, fz the axial
force pushing the plug out of the socket). A move is a slow guarded push on the
socket axis to the floor (push-click), optionally followed by a guarded pull. The
fitter splits a move at its deepest point: before it is the push, after it the pull.
A move can be flagged ``latch=False``: a push with the latch disabled (held open, or
a receptacle with the latch arm removed), which shows the terminals alone.

Model (quasi-static, the same piecewise-linear shapes as mating.py; depths measured
back from the seat, so the unknown zero of the logged depth drops out):

* terminals: engage ``terminal_wipe_mm`` before the seat, rise over ``terminal_lead_mm``
  to ``terminal_peak_n`` (all circuits), fall over the next lead to ``terminal_slide_n``;
  the sign follows the motion through the same position bristle as mating.py;
* latch ramp: zero up to the onset, rises over ``latch_rise_mm`` to ``latch_peak_n``,
  falls over ``latch_fall_mm`` to ``(1 - snap_drop) * latch_peak_n`` at the snap, which
  is ``post_snap_stroke_mm`` before the seat. mating.py has snap_drop = 1 (the force
  falls to zero); the fit leaves it free so a real latch that keeps some ramp force
  past the click shows up as snap_drop < 1;
* engaged latch on the pull: free play ``latch_play_mm``, then a spring of
  ``latch_stiffness_n_per_mm`` (mating.py: 0.1 mm and 200 N/mm, module constants);
* floor: a linear stop at the seat (nuisance stiffness, a property of the rig and
  the floor contact, not of the part);
* per move: the seat depth in the logged frame (the depth offset) and a force offset
  (imperfect tare).

Not fitted: the latch retention (a guarded pull at 50% of it never breaks the latch)
and the defect end stops.

Objective: soft-L1 (smooth Huber) of the residual between the model and the logged
force, binned on the logged depth (0.01 mm bins, median force per bin, so every
depth counts once whatever the speed and dwell). The loss scale is three times the
free-space noise of the bins. Like the median objective of contact_fit.py it is
robust to spikes and to unmodelled dynamics; unlike the plain median, it does not
ignore features that cover less than half the samples (the click is 0.1 mm of a 9 mm
move). Minimizer: projected Levenberg-Marquardt with iteratively reweighted residuals,
from several starts. Numpy only; no MuJoCo.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from defex.config import ConnectorSpec

BIN_MM = 0.01
REBOUND_MM = 0.01  # depth regained after the lowest pull point that ends the pull segment
PART_PARAMS = ("terminal_wipe_mm", "terminal_lead_mm", "terminal_peak_n", "terminal_slide_n",
               "latch_rise_mm", "latch_peak_n", "latch_fall_mm", "snap_drop", "post_snap_stroke_mm",
               "latch_play_mm", "latch_stiffness_n_per_mm", "bristle_mm")
TERMINAL_PARAMS = PART_PARAMS[:4]
LATCH_PUSH_PARAMS = ("latch_rise_mm", "latch_peak_n", "latch_fall_mm", "snap_drop", "post_snap_stroke_mm")
PULL_PARAMS = ("latch_play_mm", "latch_stiffness_n_per_mm", "bristle_mm")
LOG_PARAMS = ("latch_stiffness_n_per_mm", "floor_stiffness_n_per_mm")
BOUNDS = {
    "terminal_wipe_mm": (0.3, 4.0), "terminal_lead_mm": (0.02, 1.0),
    "terminal_peak_n": (0.0, 120.0), "terminal_slide_n": (0.0, 100.0),
    "latch_rise_mm": (0.05, 2.5), "latch_peak_n": (0.0, 40.0), "latch_fall_mm": (0.01, 0.6),
    "snap_drop": (0.0, 1.0), "post_snap_stroke_mm": (0.02, 2.0),
    "latch_play_mm": (0.0, 0.6), "latch_stiffness_n_per_mm": (10.0, 5000.0), "bristle_mm": (0.005, 0.3),
    "floor_stiffness_n_per_mm": (20.0, 1e5),
}
# mating.py's module constants (_LATCH_PLAY, _LATCH_STIFFNESS, _BRISTLE): defaults when a pull is not logged.
MATING_CONSTANTS = {"latch_play_mm": 0.1, "latch_stiffness_n_per_mm": 200.0, "bristle_mm": 0.05}


@dataclass(frozen=True)
class LoggedMove:
    t_s: np.ndarray
    depth_mm: np.ndarray
    fz_n: np.ndarray
    latch: bool = True  # False: the latch was disabled for this push (terminals only)
    speed_mm_s: float | None = None

    @staticmethod
    def read_csv(path: Path, latch: bool = True, speed_mm_s: float | None = None) -> "LoggedMove":
        rows = list(csv.DictReader(Path(path).open()))
        col = lambda k: np.array([float(r[k]) for r in rows])  # noqa: E731
        return LoggedMove(col("t_s"), col("depth_mm"), col("fz_n"), latch, speed_mm_s)

    def write_csv(self, path: Path) -> None:
        with Path(path).open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["t_s", "depth_mm", "fz_n"])
            for t, d, f in zip(self.t_s, self.depth_mm, self.fz_n):
                w.writerow([f"{t:.4f}", f"{d:.5f}", f"{f:.5f}"])

    def turnaround(self) -> int:
        k = min(25, max(1, self.depth_mm.size // 20))
        smooth = np.convolve(self.depth_mm, np.ones(k) / k, mode="same")
        return int(np.argmax(smooth[k:-k]) + k) if self.depth_mm.size > 3 * k else int(np.argmax(self.depth_mm))

    def pull_end(self) -> int:
        """Last sample of the monotone pull: the first rebound after the turnaround ends it.

        A stiff latch hook caught by a compliant servo rings, and the terminal contacts
        re-stick on every reversal; the quasi-static model describes only the first,
        monotone stretch of the pull.
        """
        i = self.turnaround()
        d = self.depth_mm[i:]
        if d.size < 10:
            return self.depth_mm.size - 1
        k = 3
        s = np.median(np.lib.stride_tricks.sliding_window_view(d, k), axis=1)
        low = np.minimum.accumulate(s)
        moved = s[0] - low > 0.05
        back = np.nonzero(moved & (s > low + REBOUND_MM))[0]
        j = int(back[0]) if back.size else s.size - 1
        j = int(np.argmin(s[: j + 1]))
        return i + j + k // 2

    @property
    def has_pull(self) -> bool:
        i, j = self.turnaround(), self.pull_end()
        return j - i > 20 and self.depth_mm[i] - self.depth_mm[i:j + 1].min() > 0.2


@dataclass
class _Binned:
    d: np.ndarray  # logged depth per bin
    f: np.ndarray  # median force per bin
    pull: np.ndarray  # bool
    d_turn: float
    latch: bool


def _bin(move: LoggedMove) -> _Binned:
    i, j = move.turnaround(), move.pull_end()
    ds, fs, ps = [], [], []
    for seg, sl in ((False, slice(0, i + 1)), (True, slice(i + 1, j + 1))):
        d, f = move.depth_mm[sl], move.fz_n[sl]
        if d.size == 0:
            continue
        key = np.floor(d / BIN_MM).astype(int)
        for k in np.unique(key):
            m = key == k
            ds.append(float(np.median(d[m])))
            fs.append(float(np.median(f[m])))
            ps.append(seg)
    d_turn = float(np.median(move.depth_mm[max(0, i - 5):i + 6]))
    return _Binned(np.array(ds), np.array(fs), np.array(ps), d_turn, move.latch)


def terminal_force(x: np.ndarray, p: dict, seat: float) -> np.ndarray:
    t0 = seat - p["terminal_wipe_mm"]
    lead = p["terminal_lead_mm"]
    u = x - t0
    rise = p["terminal_peak_n"] * np.clip(u / lead, 0.0, 1.0)
    fall = (p["terminal_slide_n"] - p["terminal_peak_n"]) * np.clip((u - lead) / lead, 0.0, 1.0)
    return np.where(u > 0.0, rise + fall, 0.0)


def latch_depths(p: dict, seat: float) -> tuple[float, float, float]:
    snap = seat - p["post_snap_stroke_mm"]
    lpeak = snap - p["latch_fall_mm"]
    return lpeak - p["latch_rise_mm"], lpeak, snap


def latch_push_force(x: np.ndarray, p: dict, seat: float) -> np.ndarray:
    onset, lpeak, snap = latch_depths(p, seat)
    peak, rest = p["latch_peak_n"], (1.0 - p["snap_drop"]) * p["latch_peak_n"]
    up = peak * np.clip((x - onset) / (lpeak - onset), 0.0, 1.0)
    down = (rest - peak) * np.clip((x - lpeak) / (snap - lpeak), 0.0, 1.0)
    return np.where(x > onset, up + down, 0.0)


def model_force(x: np.ndarray, pull: np.ndarray, x_turn: float, p: dict, seat: float, latch: bool,
                floor_k: float) -> np.ndarray:
    """Force pushing the plug out, at model depth x (same frame as seat), push or pull samples."""
    bristle = np.where(pull, np.clip(1.0 - (x_turn - x) / p["bristle_mm"], -1.0, 1.0), 1.0)
    f = terminal_force(x, p, seat) * bristle + floor_k * np.maximum(x - seat, 0.0)
    if latch:
        f = f + np.where(pull, 0.0, latch_push_force(x, p, seat))
        _, _, snap = latch_depths(p, seat)
        if x_turn >= snap:
            catch = snap - p["latch_play_mm"]
            f = f - np.where(pull, p["latch_stiffness_n_per_mm"] * np.maximum(catch - x, 0.0), 0.0)
    return f


@dataclass(frozen=True)
class LatchFit:
    params: dict  # every part parameter (fitted or fixed), seat-referenced
    free: tuple  # names fitted
    seat_mm: tuple  # per move, in the logged depth frame
    force_offset_n: tuple  # per move
    floor_stiffness_n_per_mm: float
    cost: float
    median_abs_error_n: float  # over the engagement window, all moves
    rms_error_n: float
    noise_n: float  # per-bin noise estimate used for the loss scale
    starts: int

    def mating_depths_mm(self, socket_depth_mm: float) -> dict:
        """Absolute depths in the simulator's frame (seat at the socket depth)."""
        onset, lpeak, snap = latch_depths(self.params, socket_depth_mm)
        return {"terminal_start_depth_mm": socket_depth_mm - self.params["terminal_wipe_mm"],
                "latch_onset_depth_mm": onset, "latch_peak_depth_mm": lpeak, "latch_snap_depth_mm": snap}

    def predict(self, move: LoggedMove, k: int) -> np.ndarray:
        """Model force at the logged samples of move k (for overlays)."""
        i = move.turnaround()
        pull = np.arange(move.depth_mm.size) > i
        d_turn = float(np.median(move.depth_mm[max(0, i - 5):i + 6]))
        return model_force(move.depth_mm, pull, d_turn, self.params, self.seat_mm[k], move.latch,
                           self.floor_stiffness_n_per_mm) + self.force_offset_n[k]


def nominal_params(spec: ConnectorSpec) -> dict:
    m = spec.mating
    seat = spec.socket.depth_mm
    return {
        "terminal_wipe_mm": m.terminal_wipe_mm, "terminal_lead_mm": m.terminal_lead_mm,
        "terminal_peak_n": m.circuits * m.terminal_peak_per_circuit_n,
        "terminal_slide_n": m.circuits * m.terminal_slide_per_circuit_n,
        "latch_rise_mm": m.latch_peak_depth_mm - m.latch_onset_depth_mm, "latch_peak_n": m.latch_peak_force_n,
        "latch_fall_mm": m.latch_snap_depth_mm - m.latch_peak_depth_mm, "snap_drop": 1.0,
        "post_snap_stroke_mm": seat - m.latch_snap_depth_mm, **MATING_CONSTANTS,
    }


def identifiable(moves: list[LoggedMove], fit_snap_drop: bool | None = None) -> tuple:
    """Part parameters the data can fix (see results/v0.2f_latch_fit/REPORT.md, identifiability).

    Terminals: any move. Latch push shape: a latched push. Snap drop: only with a
    second look at the terminal slide force (a latched pull or a latch-disabled
    push); from a push alone the post-snap force is slide + (1 - drop) x peak and
    the two trade. Play, latch stiffness and bristle: a latched pull.
    """
    latched = [m for m in moves if m.latch]
    has_pull = any(m.has_pull for m in latched)
    free = list(TERMINAL_PARAMS)
    if latched:
        free += [n for n in LATCH_PUSH_PARAMS if n != "snap_drop"]
        drop_ok = has_pull or any(not m.latch for m in moves)
        if fit_snap_drop if fit_snap_drop is not None else drop_ok:
            free.append("snap_drop")
    if has_pull:
        free += list(PULL_PARAMS)
    return tuple(free)


def _to_internal(name: str, v: float) -> float:
    return float(np.log10(v)) if name in LOG_PARAMS else float(v)


def _to_external(name: str, u: float) -> float:
    return float(10.0 ** u) if name in LOG_PARAMS else float(u)


def _bounds(name: str) -> tuple[float, float]:
    lo, hi = BOUNDS[name]
    return _to_internal(name, lo), _to_internal(name, hi)


def _lm(fun, x0, lo, hi, delta, iters=150):
    def cost_of(r):
        return float(np.sum(2.0 * delta**2 * (np.sqrt(1.0 + (r / delta) ** 2) - 1.0)))

    x = np.clip(x0, lo, hi)
    r = fun(x)
    cost = cost_of(r)
    lam, stall = 1e-3, 0
    h = 1e-5 * (hi - lo)
    for _ in range(iters):
        w = 1.0 / np.sqrt(1.0 + (r / delta) ** 2)
        J = np.empty((r.size, x.size))
        for j in range(x.size):
            xp = x.copy()
            xp[j] = xp[j] + h[j] if xp[j] + h[j] <= hi[j] else xp[j] - h[j]
            J[:, j] = (fun(xp) - r) / (xp[j] - x[j])
        sw = np.sqrt(w)
        A = J * sw[:, None]
        g = A.T @ (sw * r)
        H = A.T @ A
        improved = False
        while lam < 1e10:
            step = np.linalg.solve(H + lam * (np.diag(np.diag(H)) + 1e-12 * np.eye(x.size)), -g)
            xn = np.clip(x + step, lo, hi)
            rn = fun(xn)
            cn = cost_of(rn)
            if cn < cost:
                rel = (cost - cn) / max(cost, 1e-12)
                x, r, cost = xn, rn, cn
                lam = max(lam / 3.0, 1e-9)
                improved = True
                stall = stall + 1 if rel < 1e-8 else 0
                break
            lam *= 4.0
        if not improved or stall >= 3:
            break
    return x, cost


def fit_latch(spec: ConnectorSpec, moves: list[LoggedMove], free: tuple | None = None, starts: int = 24,
              seed: int = 0, fit_snap_drop: bool | None = None) -> LatchFit:
    """Fit the part parameters shared by ``moves`` (one part) plus per-move seat and force offset."""
    if not moves:
        raise ValueError("need at least one logged move")
    free = tuple(free) if free is not None else identifiable(moves, fit_snap_drop)
    base = nominal_params(spec)
    bins = [_bin(m) for m in moves]
    # Noise per bin from the free-space start of each push (the first 30% of its depth range).
    quiet = []
    for b in bins:
        push = ~b.pull
        cut = b.d[push].min() + 0.3 * (b.d_turn - b.d[push].min())
        q = b.f[push & (b.d < cut)]
        if q.size > 10:
            quiet.append(np.diff(q))
    noise = float(np.median(np.abs(np.concatenate(quiet))) / 0.6745 / np.sqrt(2.0)) if quiet else 0.05
    delta = max(3.0 * noise, 0.05)

    names = list(free) + ["floor_stiffness_n_per_mm"]
    n_shared = len(names)
    lo = np.array([_bounds(n)[0] for n in names] + sum([[b.d_turn - 1.5, -10.0] for b in bins], []))
    hi = np.array([_bounds(n)[1] for n in names] + sum([[b.d_turn + 0.3, 10.0] for b in bins], []))

    def unpack(u):
        p = dict(base)
        for j, n in enumerate(names[:-1]):
            p[n] = _to_external(n, u[j])
        return p, _to_external("floor_stiffness_n_per_mm", u[n_shared - 1]), u[n_shared:]

    def resid(u):
        p, kf, per = unpack(u)
        out = []
        for k, b in enumerate(bins):
            seat, off = per[2 * k], per[2 * k + 1]
            f = model_force(b.d, b.pull, b.d_turn, p, seat, b.latch, kf) + off
            out.append(f - b.f)
        return np.concatenate(out)

    def x_from(p, kf, seats, offs):
        shared = [_to_internal(n, p[n]) for n in names[:-1]] + [_to_internal("floor_stiffness_n_per_mm", kf)]
        return np.array(shared + sum([[s, o] for s, o in zip(seats, offs)], []))

    offs0 = []
    for b in bins:
        push = ~b.pull
        cut = b.d[push].min() + 0.3 * (b.d_turn - b.d[push].min())
        q = b.f[push & (b.d < cut)]
        offs0.append(float(np.median(q)) if q.size else 0.0)
    rng = np.random.default_rng(seed)
    best = None
    for s in range(starts):
        p0 = dict(base)
        if s > 0:
            for n in names[:-1]:
                if n == "snap_drop":
                    p0[n] = float(rng.uniform(0.3, 1.0))
                    continue
                a, c = BOUNDS[n]
                if n in LOG_PARAMS:
                    p0[n] = float(10 ** rng.uniform(np.log10(max(a, base[n] / 3)), np.log10(min(c, base[n] * 3))))
                else:
                    p0[n] = float(np.clip(base[n] * rng.uniform(0.5, 1.6), a, c))
        seats0 = [b.d_turn - (0.02 if s == 0 else rng.uniform(0.0, 0.4)) for b in bins]
        kf0 = 1000.0 if s == 0 else float(10 ** rng.uniform(2.0, 4.0))
        x, cost = _lm(resid, x_from(p0, kf0, seats0, offs0), lo, hi, delta)
        if best is None or cost < best[1]:
            best = (x, cost)
    x, cost = best
    p, kf, per = unpack(x)
    r = resid(x)
    window = []
    for k, b in enumerate(bins):
        window.append(b.d >= per[2 * k] - p["terminal_wipe_mm"] - 0.2)
    window = np.concatenate(window)
    return LatchFit(params=p, free=tuple(free), seat_mm=tuple(float(per[2 * k]) for k in range(len(bins))),
                    force_offset_n=tuple(float(per[2 * k + 1]) for k in range(len(bins))),
                    floor_stiffness_n_per_mm=kf, cost=cost,
                    median_abs_error_n=float(np.median(np.abs(r[window]))),
                    rms_error_n=float(np.sqrt(np.mean(r[window] ** 2))), noise_n=noise, starts=starts)


def measured_click(move: LoggedMove, fit: LatchFit, k: int = 0) -> dict:
    """Model-free click numbers from the push: the force drop from the last peak before the snap."""
    i = move.turnaround()
    d, f = move.depth_mm[: i + 1], move.fz_n[: i + 1] - fit.force_offset_n[k]
    onset, lpeak, snap = latch_depths(fit.params, fit.seat_mm[k])
    before = (d > onset) & (d <= snap)
    after = (d > snap) & (d < fit.seat_mm[k] - 0.02)
    if not before.any() or not after.any():
        return {"peak_n": float("nan"), "after_min_n": float("nan"), "drop_n": float("nan")}
    peak, low = float(np.max(f[before])), float(np.min(f[after]))
    return {"peak_n": peak, "after_min_n": low, "drop_n": peak - low}


@dataclass(frozen=True)
class Tolerance:
    rel: float = 0.15
    floors: dict = field(default_factory=lambda: {"mm": 0.05, "n": 0.5, "snap_drop": 0.15})

    def allowed(self, name: str, truth: float) -> float:
        if name == "snap_drop":
            return max(self.rel * abs(truth), self.floors["snap_drop"])
        floor = self.floors["n"] if name.endswith("_n") else self.floors["mm"] if name.endswith("_mm") else 0.0
        return max(self.rel * abs(truth), floor)
