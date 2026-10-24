"""Record insertion runs to MP4 (or GIF) with telemetry overlays.

    python -m demos.record_video --controller adaptive --condition noise_2mm --trial 3
    python -m demos.record_video --controller fixed --lateral 3 --yaw 5 --out demos/media/fixed.mp4
    python -m demos.record_video --compare --condition lateral_3mm        # A, B, C back to back

Headless Linux: prefix with MUJOCO_GL=egl (or osmesa). macOS renders offscreen
with plain ``python``. MP4 needs ``pip install -e ".[video]"`` (imageio-ffmpeg);
otherwise use ``--out something.gif``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from defex.control.registry import LABELS, make_controller
from defex.sim.backend import SceneParams
from defex.tasks.insertion import InsertionTask, StepInfo
from defex.tasks.scenarios import Scenario
from demos.common import MEDIA_DIR, SceneMarkers, Telemetry, add_scenario_args, describe_scenario, scenario_from_args
from demos.render import FrameRenderer, OverlayState, outcome_text


class VideoSink:
    """Collects frames and encodes MP4 (imageio-ffmpeg) or GIF (Pillow)."""

    def __init__(self, path: Path, fps: int = 30) -> None:
        self.path = Path(path)
        self.fps = fps
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._writer = None
        self._gif_frames: list = []
        self.frames = 0  # frames written so far (duration = frames / fps)
        if self.path.suffix.lower() == ".mp4":
            import imageio.v2 as imageio

            self._writer = imageio.get_writer(
                str(self.path), fps=fps, codec="libx264", quality=7, pixelformat="yuv420p", macro_block_size=8
            )

    def add(self, frame: np.ndarray) -> None:
        self.frames += 1
        if self._writer is not None:
            self._writer.append_data(frame)
        else:
            from PIL import Image

            if len(self._gif_frames) % 2 == 0:  # GIF: half frame rate, half resolution
                im = Image.fromarray(frame)
                self._gif_frames.append(im.resize((im.width // 2, im.height // 2)))
            else:
                self._gif_frames.append(None)

    def hold(self, frame: np.ndarray, seconds: float) -> None:
        for _ in range(int(round(seconds * self.fps))):
            self.add(frame)

    def close(self) -> None:
        if self._writer is not None:
            self._writer.close()
        else:
            frames = [f for f in self._gif_frames if f is not None]
            if frames:
                frames[0].save(self.path, save_all=True, append_images=frames[1:], duration=int(2000 / self.fps), loop=0)


def record_run(
    task: InsertionTask,
    controller_name: str,
    scenario: Scenario,
    sink: VideoSink,
    speed: float = 1.0,
    title: str | None = None,
    subtitle: str | None = None,
    hold_s: float = 3.0,
    width: int = 1280,
    height: int = 720,
    pip: bool = True,
    stills: dict[str, np.ndarray] | None = None,
):
    """Run one trial and append its frames (plus an outcome hold) to ``sink``.

    If ``stills`` is given, it receives the first rendered frame of every FSM state
    the controller enters (keyed by state name) and the final frame (``"final"``).
    """
    be = task.backend
    be.load(SceneParams(scenario.connector, scenario.friction, scenario.socket_pose, scenario.grasp_offset))
    renderer = FrameRenderer(
        be.model,
        width,
        height,
        pip_camera="side" if pip else None,
        title=title or LABELS[controller_name],
        subtitle=subtitle or describe_scenario(scenario),
    )
    tel, markers, state = Telemetry(), SceneMarkers(), OverlayState()
    dt_frame = speed / sink.fps
    next_t = [None]
    last: list[StepInfo | None] = [None]

    def on_step(info: StepInfo) -> None:
        tel.update(info)
        markers.update(info)
        last[0] = info
        if next_t[0] is None:
            next_t[0] = info.t
        if info.t + 1e-9 >= next_t[0]:
            frame = renderer.frame(be.data, info, tel, markers, state, controller_name)
            sink.add(frame)
            if stills is not None and info.controller.state not in stills:
                stills[info.controller.state] = frame.copy()
            next_t[0] += dt_frame

    result = task.run(make_controller(controller_name), scenario, on_step=on_step)
    state.outcome, state.outcome_text, state.extra_lines = outcome_text(result)
    final = renderer.frame(be.data, last[0], tel, markers, state, controller_name)
    sink.hold(final, hold_s)
    if stills is not None:
        stills["final"] = final.copy()
    renderer.close()
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--controller", default="adaptive", choices=["fixed", "correction", "adaptive"])
    ap.add_argument("--compare", action="store_true", help="record A, B and C back to back on the same scenario")
    ap.add_argument("--speed", type=float, default=1.0, help="sim seconds per video second (0.5 = slow motion)")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--no-pip", action="store_true", help="disable the cutaway picture-in-picture")
    ap.add_argument("--out", type=Path, default=None)
    add_scenario_args(ap)
    args = ap.parse_args()
    scenario = scenario_from_args(args, default_condition="lateral_3mm")
    names = ["fixed", "correction", "adaptive"] if args.compare else [args.controller]
    out = args.out or MEDIA_DIR / f"{'compare' if args.compare else args.controller}_{scenario.condition}_{scenario.trial_index}.mp4"
    task = InsertionTask()
    sink = VideoSink(out, args.fps)
    print(describe_scenario(scenario))
    for name in names:
        r = record_run(task, name, scenario, sink, args.speed, width=args.width, height=args.height, pip=not args.no_pip)
        print(f"{LABELS[name]:32s} success={r.success} reason={r.failure_reason} retries={r.retries} "
              f"cycle={r.cycle_time_s:.2f}s peakF={r.peak_contact_force_n:.1f}N")
    sink.close()
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
