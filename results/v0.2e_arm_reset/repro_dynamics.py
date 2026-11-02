"""Minimal reproduction: the arm's FixtureDynamics for one scene, computed in a fresh backend
versus after another trial with a large grasp offset left the cached model's connector body moved.

Run from the repository root:  python results/v0.2e_arm_reset/repro_dynamics.py [gantry|arm]
"""

from __future__ import annotations

import sys
from dataclasses import asdict

import numpy as np

from defex.config import CompliantStageConfig, FixtureConfig
from defex.sim.backend import SceneParams
from defex.tasks.conditions import conditions_by_name
from defex.tasks.scenarios import resolve_connector
from defex.utils.transforms import Pose, rotvec_to_matrix


def make(which: str):
    if which == "arm":
        from defex.sim.arm_backend import MuJoCoArmBackend

        return MuJoCoArmBackend()
    from defex.sim.mujoco_backend import MuJoCoBackend

    return MuJoCoBackend()


def main() -> None:
    which = sys.argv[1] if len(sys.argv) > 1 else "arm"
    spec = resolve_connector(conditions_by_name()["generalization_combined"])
    from defex.sim.scene_builder import WorkcellLayout

    socket = Pose(WorkcellLayout.from_spec(spec, FixtureConfig()).socket_mouth.copy(), np.eye(3))
    grasp = Pose(np.array([0.001, -0.0007, 0.001]), rotvec_to_matrix(np.array([0.04, -0.03, 0.0])))
    rigid = SceneParams(spec, 0.5, socket)  # what the rigid (non-RCC) controllers load
    rcc = SceneParams(spec, 0.5, socket, compliance=CompliantStageConfig())  # F and I load this model
    rcc_grasp = SceneParams(spec, 0.5, socket, grasp, CompliantStageConfig())

    fresh = make(which)
    fresh.load(rcc)
    a = fresh.fixture_dynamics

    used = make(which)
    used.load(rcc_grasp)  # a trial with a grasp error on the RCC model
    used.load(rigid)  # next job in the worker is a rigid controller: model switch
    used.load(rcc)  # back to the RCC model: _index_model recomputes the dynamics
    b = used.fixture_dynamics

    print(f"backend: {which}")
    for k, va in asdict(a).items():
        vb = asdict(b)[k]
        flag = "" if va == vb else "   <-- differs"
        print(f"  {k:36s} fresh {va!r:24}  after other trial {vb!r:24}{flag}")
    print("identical" if a == b else "DIFFERENT")


if __name__ == "__main__":
    main()
