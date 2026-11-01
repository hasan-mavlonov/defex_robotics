"""Fetch the UR5e model from MuJoCo Menagerie at a pinned commit (W5 serial-arm backend).

Not stored in git (31 MB of meshes). BSD-3-Clause, ROS Industrial Consortium.
    python scripts/fetch_menagerie.py
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from defex.sim.arm_backend import MENAGERIE_COMMIT, MENAGERIE_DIR  # noqa: E402

root = MENAGERIE_DIR.parent
if not (root / ".git").exists():
    root.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(["git", "clone", "--filter=blob:none", "--sparse",
                           "https://github.com/google-deepmind/mujoco_menagerie.git", str(root)])
subprocess.check_call(["git", "-C", str(root), "sparse-checkout", "set", "universal_robots_ur5e"])
subprocess.check_call(["git", "-C", str(root), "fetch", "--depth", "1", "origin", MENAGERIE_COMMIT])
subprocess.check_call(["git", "-C", str(root), "checkout", "-q", MENAGERIE_COMMIT])
print(f"UR5e model at {MENAGERIE_DIR} (commit {MENAGERIE_COMMIT})")
