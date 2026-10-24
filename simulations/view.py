"""Open a Defex scene in the interactive MuJoCo viewer.

    python simulations/view.py                 # DAIE V0.1 insertion workcell (default)
    python simulations/view.py --scene legacy  # original connector prototype scene
    python simulations/view.py --scene path/to/scene.xml

This uses MuJoCo's managed viewer (``mujoco.viewer.launch``), which works with the
regular ``python`` interpreter on macOS. The closed-loop demos in ``demos/`` use
the passive viewer and must be started with ``mjpython`` on macOS.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import mujoco
import mujoco.viewer

BASE_DIR = Path(__file__).resolve().parent
SCENES = {
    "workcell": BASE_DIR / "scenes" / "daie_workcell.xml",
    "legacy": BASE_DIR / "models" / "connector_prototype_v0.xml",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scene", default="workcell", help="workcell | legacy | path to an MJCF file")
    args = parser.parse_args()
    path = SCENES.get(args.scene, Path(args.scene))
    if args.scene == "workcell" and not path.exists():
        from defex.sim.scene_builder import write_scene

        write_scene(path)
    model = mujoco.MjModel.from_xml_path(str(path))
    data = mujoco.MjData(model)
    print(f"Defex Robotics | MuJoCo {mujoco.__version__} | scene: {path.relative_to(BASE_DIR.parent) if path.is_relative_to(BASE_DIR.parent) else path}")
    print("Close the viewer window to exit.")
    mujoco.viewer.launch(model, data)


if __name__ == "__main__":
    main()
