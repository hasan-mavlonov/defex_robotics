"""Fit MuJoCo contact parameters to force-depth curves logged on a real rig (W7).

Calibration move (same on the rig and in simulation, TEST_PROTOCOL.md section 4):
the plug starts 1 mm above the socket mouth, laterally offset onto the lead-in,
and the fixture descends at constant speed while the wrist sensor logs the axial
force. The chamfer slide, wall friction and bottoming shape that curve.

Fitted parameters: friction coefficient and normal-contact time constant (the
contact stiffness). Method: grid search, then a 0.01 friction grid around the
best cell, minimizing the median absolute force difference on a common depth
grid. RMS is the wrong objective here: a small friction change shifts the
moment the plug slips off the chamfer, and the resulting force spikes make the
RMS landscape flat and noisy; the median is smooth with a single minimum.

Log format (CSV, one per move): ``t_s,depth_mm,fz_n`` with depth measured from
the mouth plane (positive into the socket) and fz the tared axial force pushing
the plug out of the socket.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

from defex.config import MM, ConnectorSpec, SimConfig
from defex.sim.backend import SceneParams
from defex.sim.mujoco_backend import MuJoCoBackend
from defex.utils.transforms import Pose


@dataclass(frozen=True)
class CalibrationMove:
    lateral_offset_mm: float = 1.0
    start_height_mm: float = 1.0
    end_depth_mm: float = 15.5  # 0.5 mm past the seat: includes the bottoming rise
    speed_mm_s: float = 2.0


@dataclass(frozen=True)
class Curve:
    depth_mm: np.ndarray
    fz_n: np.ndarray

    @staticmethod
    def read_csv(path: Path) -> "Curve":
        rows = list(csv.DictReader(Path(path).open()))
        return Curve(np.array([float(r["depth_mm"]) for r in rows]), np.array([float(r["fz_n"]) for r in rows]))

    def write_csv(self, path: Path) -> None:
        with Path(path).open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["t_s", "depth_mm", "fz_n"])
            for i, (d, f) in enumerate(zip(self.depth_mm, self.fz_n)):
                w.writerow([i * 0.002, f"{d:.5f}", f"{f:.5f}"])


def simulate_move(spec: ConnectorSpec, friction: float, contact_timeconst_s: float,
                  move: CalibrationMove = CalibrationMove(), dt: float = 0.002) -> Curve:
    be = MuJoCoBackend(replace(SimConfig(), contact_timeconst_s=contact_timeconst_s))
    be.load(SceneParams(spec, friction, Pose.identity()))
    S = be.nominal_socket_pose
    be.load(SceneParams(spec, friction, S))
    x = move.lateral_offset_mm * MM
    z0 = move.start_height_mm * MM
    start = Pose(S.p + np.array([x, 0.0, z0]), S.R)
    be.set_joint_positions_kinematic(be.inverse_kinematics(start))
    be.set_tcp_setpoint(start)
    n = int(round((z0 + move.end_depth_mm * MM) / (move.speed_mm_s * MM) / dt))
    depth, fz = [], []
    for k in range(n):
        z = z0 - (k + 1) * move.speed_mm_s * MM * dt
        be.set_tcp_setpoint(Pose(S.p + np.array([x, 0.0, z]), S.R))
        be.step(dt)
        gt = be.ground_truth()
        depth.append(-(gt.connector_pose.p[2] - S.p[2]) / MM)
        fz.append(float(gt.contact_force[2]))
    return Curve(np.array(depth), np.array(fz))


def curve_error(a: Curve, b: Curve, grid: np.ndarray) -> float:
    def resample(c: Curve) -> np.ndarray:
        order = np.argsort(c.depth_mm)
        d, f = c.depth_mm[order], c.fz_n[order]
        d, idx = np.unique(d, return_index=True)
        return np.interp(grid, d, f[idx])

    return float(np.median(np.abs(resample(a) - resample(b))))


@dataclass(frozen=True)
class Fit:
    friction: float
    contact_timeconst_s: float
    median_abs_error_n: float
    table: list[tuple[float, float, float]]  # (friction, timeconst, median abs error)


def fit_contact(spec: ConnectorSpec, real: Curve, move: CalibrationMove = CalibrationMove(),
                frictions=np.arange(0.1, 1.01, 0.1), timeconsts=(0.0015, 0.002, 0.003, 0.004)) -> Fit:
    lo, hi = max(real.depth_mm.min(), 0.0), min(real.depth_mm.max(), move.end_depth_mm)
    grid = np.linspace(lo, hi, 200)
    table = [(float(mu), float(tc), curve_error(simulate_move(spec, mu, tc, move), real, grid))
             for mu in frictions for tc in timeconsts]
    mu0, tc0, _ = min(table, key=lambda r: r[2])
    fine = np.clip(np.round(mu0 + np.arange(-0.1, 0.1001, 0.01), 3), 0.05, 1.5)
    table += [(float(mu), tc0, curve_error(simulate_move(spec, mu, tc0, move), real, grid)) for mu in fine]
    mu, tc, err = min(table, key=lambda r: r[2])
    return Fit(mu, tc, err, table)


def overlay_report(spec: ConnectorSpec, real: Curve, fit: Fit, path: Path, move: CalibrationMove = CalibrationMove()):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sim = simulate_move(spec, fit.friction, fit.contact_timeconst_s, move)
    fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=150)
    ax.plot(real.depth_mm, real.fz_n, lw=1.0, color="#2a78d6", label="real (logged)")
    ax.plot(sim.depth_mm, sim.fz_n, lw=1.4, color="#eb6834",
            label=f"sim fit: mu {fit.friction:.2f}, timeconst {fit.contact_timeconst_s * 1e3:.1f} ms")
    ax.set_xlabel("depth below mouth (mm)")
    ax.set_ylabel("axial force (N)")
    ax.set_title(f"Calibration move, {move.lateral_offset_mm:g} mm offset; median |error| {fit.median_abs_error_n:.2f} N",
                 fontsize=9)
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
