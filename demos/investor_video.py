"""Render the 60-90 s investor demonstration video.

    python -m demos.investor_video                      # uses results/benchmark_v0.1 if present
    python -m demos.investor_video --results results/robustness --out demos/media/defex_daie_v01.mp4

Sequence:
  0. Title card, short orbit of the workcell.
  1. Scene 1: conventional fixed-trajectory automation meets a misaligned socket and
     fails (protective stop at the force limit).
  2. Scene 2: the Defex adaptive controller meets the *same* socket, detects the
     failure from contact forces, retracts, corrects, inserts and verifies.
  3. Scene 3: dashboard of the benchmark across randomized trials.

The two runs are an actual benchmark trial (same condition, index and seed), chosen
by ``demos.showcase``; nothing is staged. All dashboard numbers come from the
benchmark results on disk.

Headless Linux: ``MUJOCO_GL=egl`` (or ``osmesa``). Requires ``.[video]`` extras.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import mujoco
import numpy as np
from PIL import Image, ImageDraw

from defex.config import MM
from defex.control.registry import LABELS
from defex.sim.backend import SceneParams
from defex.tasks.conditions import conditions_by_name
from defex.tasks.insertion import InsertionTask
from defex.tasks.scenarios import sample_scenario
from defex.perception.sensors import SensorSuite
from demos.common import MEDIA_DIR, font, font_bold, nominal_socket_pose
from demos.record_video import VideoSink, record_run
from demos.showcase import DEFAULT_RESULTS, find_showcase

W, H = 1280, 720
BG = (13, 13, 13)
INK = (240, 239, 236)
INK2 = (195, 194, 183)
ACCENT = (217, 89, 38)


def card(title: str, lines: list[str], kicker: str = "") -> np.ndarray:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle((96, 250, 104, 250 + 64 + 34 * len(lines)), fill=ACCENT)
    y = 236
    if kicker:
        d.text((128, y - 34), kicker.upper(), font=font_bold(18), fill=INK2)
    d.text((128, y), title, font=font_bold(46), fill=INK)
    y += 76
    for line in lines:
        d.text((128, y), line, font=font(24), fill=INK2)
        y += 34
    return np.asarray(img)


def fade(sink: VideoSink, a: np.ndarray, b: np.ndarray, seconds: float = 0.5) -> None:
    n = max(1, int(seconds * sink.fps))
    for i in range(n):
        w = (i + 1) / n
        sink.add((a.astype(np.float32) * (1 - w) + b.astype(np.float32) * w).astype(np.uint8))


def orbit(task: InsertionTask, scenario, sink: VideoSink, seconds: float = 4.0) -> np.ndarray:
    be = task.backend
    be.load(SceneParams(scenario.connector, scenario.friction, scenario.socket_pose, scenario.grasp_offset))
    m, d = be.model, be.data
    r = mujoco.Renderer(m, H, W)
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat[:] = be.nominal_socket_pose.p + np.array([0.0, 0.0, 0.03])
    n = int(seconds * sink.fps)
    last = None
    for i in range(n):
        s = i / max(n - 1, 1)
        cam.azimuth = 100 + 60 * s
        cam.elevation = -28 + 8 * s
        cam.distance = 0.42 - 0.18 * s
        r.update_scene(d, camera=cam)
        last = r.render()
        sink.add(last)
    r.close()
    return last


def dashboard_frames(path: Path, sink: VideoSink, seconds: float = 10.0) -> np.ndarray:
    img = Image.open(path).convert("RGB")
    n = int(seconds * sink.fps)
    last = None
    for i in range(n):
        s = i / max(n - 1, 1)
        z = 1.0 + 0.06 * s  # slow push-in
        cw, ch = img.width / z, img.height / z
        x0 = (img.width - cw) / 2
        y0 = (img.height - ch) / 2
        frame = img.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)
        last = np.asarray(frame)
        sink.add(last)
    return last


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", type=Path, default=DEFAULT_RESULTS, help="benchmark run folder (for showcase + dashboard)")
    ap.add_argument("--out", type=Path, default=MEDIA_DIR / "defex_daie_v01_investor_demo.mp4")
    ap.add_argument("--fps", type=int, default=30)
    args = ap.parse_args()

    show = find_showcase(args.results)
    cond = conditions_by_name()[show.condition]
    scenario = sample_scenario(cond, show.trial_index, show.base_seed, nominal_socket_pose(cond))
    d = scenario.disturbance
    vis = SensorSuite(scenario.noise, scenario.seed).vision_measurement(scenario.socket_pose)
    vis_err = float(np.linalg.norm((vis.inv() @ scenario.socket_pose).p[:2]) / MM)
    print(f"showcase: {show.condition} trial {show.trial_index} (seed {show.base_seed}, {show.note})")

    task = InsertionTask()
    sink = VideoSink(args.out, args.fps)
    title = card(
        "Defex Adaptive Insertion Engine",
        ["Force-adaptive connector insertion, V0.1 simulation", "MuJoCo physics  ·  real 0.5 mm clearance socket  ·  no learning"],
        kicker="Defex Robotics",
    )
    sink.hold(title, 3.0)
    o = orbit(task, scenario, sink, 4.0)
    fade(sink, o, o, 0.1)

    s1 = card(
        "Scene 1: fixed-trajectory automation",
        [
            f"The socket sits {d['lateral_mm']:.1f} mm off its taught position, rotated {d['yaw_deg']:+.1f} deg.",
            "The program replays the taught motion. It cannot see the error.",
        ],
        kicker="Conventional automation",
    )
    fade(sink, o, s1, 0.5)
    sink.hold(s1, 3.0)
    ra = record_run(task, "fixed", scenario, sink, speed=0.5, title=LABELS["fixed"],
                    subtitle="Taught program, no sensing  ·  socket misaligned", hold_s=3.0)

    s2 = card(
        "Scene 2: Defex adaptive insertion",
        [
            "Same socket, same misalignment.",
            f"Its camera estimate is off by {vis_err:.1f} mm: vision alone is not enough here.",
            "Defex feels the contact, retracts, corrects and verifies.",
        ],
        kicker="Defex Adaptive Insertion Engine",
    )
    sink.hold(s2, 3.5)
    rc = record_run(task, "adaptive", scenario, sink, speed=0.8, title=LABELS["adaptive"],
                    subtitle="Vision + force feedback  ·  same socket as Scene 1", hold_s=3.5)

    dash = args.results / "plots" / "dashboard_dark.png"
    if dash.exists():
        s3 = card("Scene 3: measured across randomized trials",
                  ["Paired disturbances, identical for every controller.", "Ground-truth scoring in simulation."],
                  kicker="Benchmark")
        sink.hold(s3, 2.5)
        last = dashboard_frames(dash, sink, 10.0)
        end = card("defexrobotics.com", ["Adaptive assembly for real-world variation."], kicker="Defex Robotics")
        fade(sink, last, end, 0.6)
        sink.hold(end, 3.0)
    sink.close()
    print(f"Scene 1 (A): success={ra.success} reason={ra.failure_reason} peak={ra.peak_contact_force_n:.1f} N")
    print(f"Scene 2 (C): success={rc.success} retries={rc.retries} cycle={rc.cycle_time_s:.1f} s "
          f"peak={rc.peak_contact_force_n:.1f} N")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
