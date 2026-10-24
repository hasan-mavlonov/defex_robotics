"""Replay a saved trial trajectory (kinematic playback, no physics).

Trajectories are written by ``python -m experiments.robustness --record N`` into
``results/<run>/trajectories/*.npz`` (joint positions, setpoints, measured wrench
and controller state at 50 Hz).

    python -m demos.replay results/benchmark_v0.1/trajectories/noise_2mm__adaptive__000.npz
    python -m demos.replay <file.npz> --render demos/media/replay.mp4     # offscreen video
    python -m demos.replay --list results/benchmark_v0.1

Markers: red outline = programmed socket pose, green outline = the controller's
vision estimate (re-derived from the trial seed, exactly as the trial drew it),
cyan dot = commanded fixture setpoint. On macOS use ``mjpython`` for the
interactive replay.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import mujoco
import numpy as np

from defex.config import ConnectorSpec, PlugGeometry, SocketGeometry
from defex.perception.sensors import SensorSuite
from defex.sim.backend import SceneParams
from defex.sim.mujoco_backend import MuJoCoBackend
from defex.tasks.conditions import conditions_by_name
from defex.utils.transforms import Pose


def load(path: Path) -> tuple[dict, dict]:
    z = np.load(path, allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    arrays = {k: z[k] for k in z.files if k != "meta"}
    return meta, arrays


def backend_for(meta: dict) -> MuJoCoBackend:
    c = meta["connector"]
    spec = ConnectorSpec(
        name=c["name"],
        description=c.get("description", ""),
        plug=PlugGeometry(**c["plug"]),
        socket=SocketGeometry(**c["socket"]),
        friction=c.get("friction", 0.3),
    )
    be = MuJoCoBackend()
    be.load(
        SceneParams(
            spec, meta["friction"], Pose.from_array(np.array(meta["socket_pose"])), Pose.from_array(np.array(meta["grasp_offset"]))
        )
    )
    return be


def vision_estimate(meta: dict) -> Pose | None:
    """The socket pose the controller was given, re-drawn from the trial's sensor seed.

    The trial draws its single vision measurement first on the vision stream of
    ``SensorSuite(condition.noise, trial_seed)``, so a fresh suite reproduces it
    exactly. Returns None for trajectories from conditions this build does not know.
    """
    cond = conditions_by_name().get(meta["condition"])
    if cond is None:
        return None
    return SensorSuite(cond.noise, int(meta["seed"])).vision_measurement(Pose.from_array(np.array(meta["socket_pose"])))


def place_markers(be: MuJoCoBackend, meta: dict) -> None:
    est = vision_estimate(meta)
    # Unknown provenance: park the estimate marker out of view rather than show a wrong pose.
    be.set_marker_pose("estimate", est if est is not None else Pose(np.array([0.0, 0.0, -1.0]), np.eye(3)))


def label_frame(img: np.ndarray, text: str) -> np.ndarray:
    from PIL import Image, ImageDraw

    from demos.common import font_bold

    im = Image.fromarray(img)
    d = ImageDraw.Draw(im, "RGBA")
    f = font_bold(22)
    w = int(d.textlength(text, font=f))
    d.rectangle((16, 16, 16 + w + 24, 16 + 40), fill=(13, 13, 13, 200))
    d.text((28, 24), text, font=f, fill=(240, 239, 236))
    return np.asarray(im)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", type=Path, nargs="?")
    ap.add_argument("--list", type=Path, default=None, help="list trajectories in a results folder")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--render", type=Path, default=None, help="write an MP4/GIF instead of opening the viewer")
    args = ap.parse_args()
    if args.list:
        for p in sorted((args.list / "trajectories").glob("*.npz")):
            meta, _ = load(p)
            print(f"{p.name:48s} success={meta['success']} reason={meta['failure_reason']}")
        return
    if args.path is None:
        ap.error("give a trajectory .npz (or --list <results folder>)")
    meta, a = load(args.path)
    be = backend_for(meta)
    place_markers(be, meta)
    t, joints, states, setpoints = a["t"], a["joints"], a["state"], a["setpoint"]
    outcome = "success" if meta["success"] else f"failed: {meta['failure_reason']}"
    head = f"REPLAY  {meta['controller']} on {meta['condition']} #{meta['trial_index']}"
    print(f"{head}: {outcome}, {len(t)} samples over {t[-1] - t[0]:.2f} s")

    def show(k: int) -> None:
        be.set_marker_pose("setpoint", Pose.from_array(setpoints[k]))
        be.set_joint_positions_kinematic(joints[k])

    if args.render:
        from demos.record_video import VideoSink

        r = mujoco.Renderer(be.model, 720, 1280)
        sink = VideoSink(args.render, 30)
        frame_t = t[0]
        for k in range(len(t)):
            if t[k] + 1e-9 < frame_t:
                continue
            show(k)
            r.update_scene(be.data, camera="closeup")
            text = f"{head}   t={t[k]:5.2f} s   {states[k]}" + (f"   ({outcome})" if k == len(t) - 1 else "")
            sink.add(label_frame(r.render(), text))
            frame_t += args.speed / 30.0
        sink.close()
        r.close()
        print(f"wrote {args.render}")
        return

    from mujoco import viewer as mj_viewer  # local alias: a bare `import mujoco.viewer` would shadow `mujoco`

    h = mj_viewer.launch_passive(be.model, be.data, show_left_ui=False, show_right_ui=False)
    h.cam.lookat[:] = be.nominal_socket_pose.p + np.array([0.0, 0.0, 0.006])
    h.cam.distance, h.cam.azimuth, h.cam.elevation = 0.11, 128.0, -17.0
    wall0 = time.perf_counter()
    last_text = -1.0
    for k in range(len(t)):
        if not h.is_running():
            return
        with h.lock():
            show(k)
        # set_texts blocks on the render thread: refresh the label at ~10 Hz only.
        now = time.perf_counter()
        if now - last_text > 0.1 or k == len(t) - 1:
            sub = f"{states[k]}  t={t[k]:.2f}s" + (f"  {outcome}" if k == len(t) - 1 else "")
            h.set_texts((mujoco.mjtFontScale.mjFONTSCALE_150, mujoco.mjtGridPos.mjGRID_TOPLEFT, head, sub))
            last_text = now
        h.sync()
        target = wall0 + (t[k] - t[0]) / args.speed
        time.sleep(max(0.0, target - time.perf_counter()))
    while h.is_running():
        h.sync()
        time.sleep(0.05)


if __name__ == "__main__":
    main()
