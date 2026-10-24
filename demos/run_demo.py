"""Live 3D demos in the MuJoCo viewer.

    python -m demos.run_demo nominal                          # one nominal insertion (controller C)
    python -m demos.run_demo nominal --controller fixed
    python -m demos.run_demo disturbed --controller fixed --lateral 3 --yaw 5
    python -m demos.run_demo adaptive                         # C on a benchmark trial that needs recovery
    python -m demos.run_demo compare --condition noise_2mm --trial 3   # A, B, C back to back

macOS: the passive viewer must own the main thread, so start these with
``mjpython`` (installed with MuJoCo) instead of ``python``:

    mjpython -m demos.run_demo adaptive

Options: ``--speed 0.5`` for slow motion, ``--headless`` to run without a window.
Markers: red outline = programmed (nominal) socket pose, green outline = vision
estimate, cyan dot = controller target, orange trail = connector tip path.
"""

from __future__ import annotations

import argparse
import sys
import time

import mujoco
import mujoco.viewer
import numpy as np

from defex.control.registry import LABELS, make_controller
from defex.sim.backend import SceneParams
from defex.tasks.insertion import InsertionTask, StepInfo
from defex.tasks.scenarios import Scenario
from demos.common import SceneMarkers, Telemetry, add_scenario_args, describe_scenario, scenario_from_args
from demos.render import friendly, outcome_text


class ViewerClosed(Exception):
    pass


class LiveViewer:
    def __init__(self, task: InsertionTask, speed: float = 1.0, fps: float = 60.0) -> None:
        self.task = task
        self.speed = speed
        self.fps = fps
        self.handle = None
        self._texts: list = []
        self._last_text = 0.0

    def open(self, scenario: Scenario) -> None:
        be = self.task.backend
        be.load(SceneParams(scenario.connector, scenario.friction, scenario.socket_pose, scenario.grasp_offset))
        if self.handle is not None and self.handle.m is be.model:
            return
        if self.handle is not None:
            self.handle.close()
        try:
            self.handle = mujoco.viewer.launch_passive(be.model, be.data, show_left_ui=False, show_right_ui=False)
        except RuntimeError as exc:
            if sys.platform == "darwin":
                raise SystemExit(
                    "On macOS the live viewer needs MuJoCo's launcher. Run:\n"
                    "    mjpython -m demos.run_demo ...\n"
                    "(mjpython is installed next to python in your virtual environment)"
                ) from exc
            raise
        cam = self.handle.cam
        cam.type = mujoco.mjtCamera.mjCAMERA_FREE
        cam.lookat[:] = be.nominal_socket_pose.p + np.array([0.0, 0.0, 0.006])
        cam.distance = 0.11
        cam.azimuth = 128.0
        cam.elevation = -17.0

    def run(self, controller_name: str, scenario: Scenario):
        self.open(scenario)
        h = self.handle
        tel, markers = Telemetry(), SceneMarkers()
        caption = {"text": "", "n": 0}
        clock = {"wall0": None, "sim0": None, "last_sync": 0.0}

        def on_step(info: StepInfo) -> None:
            if not h.is_running():
                raise ViewerClosed
            tel.update(info)
            markers.update(info)
            ev = info.controller.events
            while caption["n"] < len(ev):
                e = ev[caption["n"]]
                caption["n"] += 1
                text = friendly(e.kind, e.detail)
                if text:
                    caption["text"] = text
            now = time.perf_counter()
            if clock["wall0"] is None:
                clock["wall0"], clock["sim0"] = now, info.t
            target = clock["wall0"] + (info.t - clock["sim0"]) / self.speed
            if target > now:
                time.sleep(target - now)
            if time.perf_counter() - clock["last_sync"] >= 1.0 / self.fps:
                clock["last_sync"] = time.perf_counter()
                self._draw(info, tel, markers, caption["text"], controller_name)

        try:
            result = self.task.run(make_controller(controller_name), scenario, on_step=on_step)
        except ViewerClosed:
            return None
        kind, head, lines = outcome_text(result)
        self._texts = [
            (mujoco.mjtFontScale.mjFONTSCALE_200, mujoco.mjtGridPos.mjGRID_TOP, head, " "),
            (mujoco.mjtFontScale.mjFONTSCALE_150, mujoco.mjtGridPos.mjGRID_BOTTOM, " ".join(lines), " "),
        ]
        h.set_texts(self._texts)
        h.sync()
        return result

    def _draw(self, info: StepInfo, tel: Telemetry, markers: SceneMarkers, caption: str, name: str) -> None:
        h = self.handle
        with h.lock():
            scn = h.user_scn
            scn.ngeom = 0
            markers.draw(scn, info)
        # set_texts is synchronous (it waits for the render thread), so only send
        # overlays when they change and at most ~10 Hz; geometry syncs run at full rate.
        now = time.perf_counter()
        if now - self._last_text >= 0.1:
            rows = Telemetry.lines(info)
            texts = [
                (mujoco.mjtFontScale.mjFONTSCALE_150, mujoco.mjtGridPos.mjGRID_TOPLEFT, LABELS[name], info.controller.state),
                (mujoco.mjtFontScale.mjFONTSCALE_150, mujoco.mjtGridPos.mjGRID_BOTTOMLEFT,
                 "\n".join(k for k, _ in rows), "\n".join(v for _, v in rows)),
                (mujoco.mjtFontScale.mjFONTSCALE_150, mujoco.mjtGridPos.mjGRID_BOTTOM, caption or " ", " "),
            ]
            if texts != self._texts:
                h.set_texts(texts)
                self._texts = texts
            self._last_text = now
        h.sync()

    def wait_close(self, seconds: float | None = None) -> None:
        """Keep the window alive (and its render loop fed) until closed or timed out."""
        t0 = time.time()
        while self.handle is not None and self.handle.is_running():
            if seconds is not None and time.time() - t0 > seconds:
                break
            self.handle.sync()
            time.sleep(0.03)


def run_headless(task: InsertionTask, names: list[str], scenario: Scenario) -> None:
    for name in names:
        r = task.run(make_controller(name), scenario)
        print_result(name, r)


def print_result(name: str, r) -> None:
    if r is None:
        print(f"{LABELS[name]}: viewer closed")
        return
    print(
        f"{LABELS[name]:32s} success={r.success} reason={r.failure_reason} retries={r.retries} "
        f"cycle={r.cycle_time_s:.2f}s depth={r.final_depth_mm:.2f}mm peakF={r.peak_contact_force_n:.1f}N"
    )
    for t, kind, detail in r.events:
        if kind not in ("state",):
            print(f"    t={t:6.2f}  {kind:18s} {detail}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["nominal", "disturbed", "adaptive", "compare"])
    ap.add_argument("--controller", choices=["fixed", "correction", "adaptive"], default=None)
    ap.add_argument("--speed", type=float, default=1.0, help="playback speed (0.5 = slow motion)")
    ap.add_argument("--headless", action="store_true", help="run without the viewer and print results")
    ap.add_argument("--hold", type=float, default=None, help="seconds to keep the window open after the run")
    add_scenario_args(ap)
    args = ap.parse_args()

    if args.mode == "nominal":
        if args.lateral is None and args.condition is None:
            args.condition = "nominal"
        names = [args.controller or "adaptive"]
    elif args.mode == "disturbed":
        if args.lateral is None and args.condition is None:
            args.lateral, args.yaw = 3.0, 5.0
        names = [args.controller or "fixed"]
    elif args.mode == "adaptive":
        if args.lateral is None and args.condition is None:
            from demos.showcase import find_showcase

            show = find_showcase()
            args.condition, args.trial, args.seed = show.condition, show.trial_index, show.base_seed
        names = ["adaptive"]
    else:
        if args.lateral is None and args.condition is None:
            args.lateral, args.yaw = 3.0, 5.0
        names = [args.controller] if args.controller else ["fixed", "correction", "adaptive"]

    scenario = scenario_from_args(args)
    print(describe_scenario(scenario))
    task = InsertionTask()
    if args.headless:
        run_headless(task, names, scenario)
        return
    viewer = LiveViewer(task, speed=args.speed)
    for k, name in enumerate(names):
        r = viewer.run(name, scenario)
        print_result(name, r)
        if r is None:
            return
        if k < len(names) - 1:
            viewer.wait_close(2.5)
    viewer.wait_close(args.hold)


if __name__ == "__main__":
    main()
