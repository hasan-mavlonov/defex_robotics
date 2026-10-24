"""Shared helpers for the live viewer, video recorder and trajectory replay."""

from __future__ import annotations

import argparse
import threading
from collections import deque
from dataclasses import replace
from pathlib import Path

import mujoco
import numpy as np

from defex.config import DEG, MM, Condition, DisturbanceSpec, FixtureConfig, SensorNoiseConfig
from defex.control.registry import LABELS
from defex.tasks.conditions import conditions_by_name
from defex.tasks.insertion import StepInfo
from defex.tasks.scenarios import Scenario, sample_scenario
from defex.utils.transforms import Pose

REPO = Path(__file__).resolve().parents[1]
MEDIA_DIR = REPO / "demos" / "media"
FSM_FLOW = ("APPROACH", "ALIGN", "INSERT", "DETECT", "RECOVER", "VERIFY")
SERIES_RGB = {"fixed": (57, 135, 229), "correction": (25, 158, 112), "adaptive": (217, 89, 38)}


def nominal_socket_pose(condition: Condition) -> Pose:
    from experiments.runner import nominal_socket_pose as _nom

    return _nom(condition, FixtureConfig())


def add_scenario_args(ap: argparse.ArgumentParser) -> None:
    g = ap.add_argument_group("scenario (either a benchmark condition or explicit disturbances)")
    g.add_argument("--condition", default=None, help="benchmark condition name, e.g. lateral_3mm, noise_2mm")
    g.add_argument("--trial", type=int, default=0, help="trial index within the condition (paired seed)")
    g.add_argument("--seed", type=int, default=2026, help="base seed")
    g.add_argument("--lateral", type=float, default=None, help="socket lateral error (mm)")
    g.add_argument("--direction", type=float, default=30.0, help="direction of the lateral error (deg)")
    g.add_argument("--yaw", type=float, default=0.0, help="socket yaw error (deg)")
    g.add_argument("--tilt", type=float, default=0.0, help="socket tilt error (deg)")
    g.add_argument("--vision-sigma", type=float, default=0.3, help="vision lateral noise sigma (mm)")
    g.add_argument("--friction", type=float, default=None)


def scenario_from_args(args: argparse.Namespace, default_condition: str = "nominal") -> Scenario:
    if args.lateral is None and args.condition is None:
        args.condition = default_condition
    if args.condition is not None:
        cond = conditions_by_name()[args.condition]
        return sample_scenario(cond, args.trial, args.seed, nominal_socket_pose(cond))
    noise = SensorNoiseConfig().scaled_vision(args.vision_sigma)
    cond = Condition(
        name="custom",
        group="custom",
        disturbance=DisturbanceSpec(lateral_mm=args.lateral, yaw_deg=abs(args.yaw), tilt_deg=args.tilt),
        noise=noise,
        friction=args.friction,
    )
    sc = sample_scenario(cond, args.trial, args.seed, nominal_socket_pose(cond))
    # Apply the requested direction and yaw sign exactly (sampling only fixes the magnitudes).
    nom = nominal_socket_pose(cond)
    d = np.deg2rad(args.direction)
    p = nom.p + np.array([np.cos(d), np.sin(d), 0.0]) * args.lateral * MM
    from defex.utils.transforms import rot_z, tilt_matrix

    R = tilt_matrix(args.tilt * DEG, d + np.pi / 2) @ rot_z(args.yaw * DEG) @ nom.R
    dist = dict(sc.disturbance)
    dist.update(dx_mm=float(np.cos(d) * args.lateral), dy_mm=float(np.sin(d) * args.lateral), yaw_deg=args.yaw)
    return replace(sc, socket_pose=Pose(p, R), disturbance=dist)


def describe_scenario(sc: Scenario) -> str:
    d = sc.disturbance
    return (
        f"{sc.condition} #{sc.trial_index}: socket offset ({d['dx_mm']:+.2f}, {d['dy_mm']:+.2f}) mm, "
        f"yaw {d['yaw_deg']:+.1f} deg, tilt {d['tilt_deg']:.1f} deg, friction {sc.friction:.2f}, "
        f"vision sigma {sc.noise.vision_xy_sigma_mm:.2f} mm"
    )


class Telemetry:
    """Formats the per-tick status lines shown in the viewer and the video."""

    def __init__(self) -> None:
        self.force_hist: deque[tuple[float, float]] = deque(maxlen=900)
        self.last_event = ""

    def update(self, info: StepInfo) -> None:
        self.force_hist.append((info.t, info.obs.force_norm))
        ev = info.controller.events
        if ev:
            e = ev[-1]
            if e.kind not in ("state",):
                self.last_event = f"{e.kind}: {e.detail}"

    @staticmethod
    def header(info: StepInfo) -> str:
        return LABELS.get(info.controller.name, info.controller.name)

    @staticmethod
    def lines(info: StepInfo) -> list[tuple[str, str]]:
        c = info.controller
        obs = info.obs
        rel = info.gt.socket_pose.inv() @ info.gt.connector_pose
        depth = -rel.p[2] / MM
        # Above the mouth, show the clearance height instead of a negative depth.
        depth_text = f"{depth:5.2f} mm" if depth >= -0.05 else f"{-depth:4.1f} mm above"
        out = [
            ("time", f"{info.t:5.2f} s"),
            ("state", f"{c.state}"),
            ("insertion depth*", depth_text),
            ("measured force", f"{obs.force_norm:5.1f} N"),
            ("recoveries", f"{c.retries}"),
        ]
        if info.protective_stop:
            out.append(("SAFETY", "protective stop"))
        return out


class SceneMarkers:
    """Trail of the connector tip plus the controller's current target, as extra scene geoms."""

    def __init__(self, max_trail: int = 400) -> None:
        self.trail: deque[np.ndarray] = deque(maxlen=max_trail)
        self._last: np.ndarray | None = None

    def update(self, info: StepInfo) -> None:
        p = info.obs.connector_pose.p
        if self._last is None or np.linalg.norm(p - self._last) > 0.25 * MM:
            self.trail.append(p.copy())
            self._last = p.copy()

    def draw(self, scn: mujoco.MjvScene, info: StepInfo | None, color=(1.0, 0.55, 0.15)) -> None:
        pts = list(self.trail)
        n = len(pts)
        for i in range(1, n):
            if scn.ngeom >= scn.maxgeom:
                return
            alpha = 0.15 + 0.75 * i / max(n - 1, 1)
            g = scn.geoms[scn.ngeom]
            mujoco.mjv_initGeom(g, mujoco.mjtGeom.mjGEOM_CAPSULE, np.zeros(3), np.zeros(3), np.zeros(9),
                                np.array([*color, alpha], dtype=np.float32))
            mujoco.mjv_connector(g, mujoco.mjtGeom.mjGEOM_CAPSULE, 0.00018, pts[i - 1], pts[i])
            scn.ngeom += 1
        if info is not None and "target" in info.controller.markers and scn.ngeom < scn.maxgeom:
            tgt = info.controller.markers["target"]
            g = scn.geoms[scn.ngeom]
            mujoco.mjv_initGeom(g, mujoco.mjtGeom.mjGEOM_SPHERE, np.array([0.0006, 0, 0]), tgt.p,
                                np.eye(3).ravel(), np.array([0.1, 0.85, 1.0, 0.9], dtype=np.float32))
            scn.ngeom += 1


def font(size: int):
    from matplotlib import font_manager
    from PIL import ImageFont

    path = font_manager.findfont("DejaVu Sans")
    return ImageFont.truetype(path, size)


def font_bold(size: int):
    from matplotlib import font_manager
    from PIL import ImageFont

    path = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold"))
    return ImageFont.truetype(path, size)


class PassiveViewer:
    """``mujoco.viewer.launch_passive`` with a shutdown that waits for the viewer.

    On Linux the passive viewer renders from its own daemon thread, and MuJoCo
    registers ``glfw.terminate`` to run at interpreter exit. ``Handle.close()`` only
    requests an exit, so a script that ends right after it can tear GLFW down under
    a live render loop (a segfault or an X11 hang). ``close()`` here also joins the
    viewer's threads. On macOS (``mjpython``) the viewer lives on the main thread,
    no extra threads exist, and this reduces to ``Handle.close()``.
    """

    def __init__(self, model: mujoco.MjModel, data: mujoco.MjData, **kwargs) -> None:
        from mujoco import viewer as mj_viewer  # lazy: headless renderers never need GLFW

        before = set(threading.enumerate())
        self.handle = mj_viewer.launch_passive(model, data, **kwargs)
        self._threads = [t for t in threading.enumerate() if t not in before]

    def close(self, timeout_s: float = 10.0) -> None:
        if self.handle is None:
            return
        self.handle.close()
        for t in self._threads:
            t.join(timeout_s)
        self.handle = None

