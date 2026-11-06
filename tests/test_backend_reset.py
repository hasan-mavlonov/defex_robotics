"""v0.2e: a trial's physics depends only on its own scene, not on what the worker ran before.

The backends cache one compiled model per connector and wrist and write each trial's grasp
offset into it. Up to 966a5f5 the payload and fixture dynamics were derived on a model switch
with the previous trial's grasp offset still in the model, so they depended on worker history.
"""

import numpy as np
import pytest

from defex.config import CompliantStageConfig
from defex.sim.arm_backend import menagerie_available
from defex.sim.backend import SceneParams
from defex.sim.mujoco_backend import MuJoCoBackend
from defex.tasks.conditions import conditions_by_name
from defex.tasks.scenarios import resolve_connector, sample_scenario
from defex.utils.transforms import Pose, rotvec_to_matrix

needs_arm = pytest.mark.skipif(not menagerie_available(), reason="run scripts/fetch_menagerie.py")
GRASP = Pose(np.array([0.001, -0.0007, 0.001]), rotvec_to_matrix(np.array([0.04, -0.03, 0.0])))


def _make(which: str):
    if which == "arm":
        from defex.sim.arm_backend import MuJoCoArmBackend

        return MuJoCoArmBackend()
    return MuJoCoBackend()


def _scenes():
    spec = resolve_connector(conditions_by_name()["generalization_combined"])
    rcc = CompliantStageConfig()
    socket = Pose.identity()
    return (SceneParams(spec, 0.5, socket, compliance=rcc), SceneParams(spec, 0.5, socket, GRASP, rcc),
            SceneParams(spec, 0.5, socket))


@pytest.mark.parametrize("which", ["gantry", pytest.param("arm", marks=needs_arm)])
def test_derived_quantities_ignore_the_previous_trials_grasp(which):
    nominal, gripped, rigid = _scenes()
    fresh = _make(which)
    fresh.load(nominal)
    used = _make(which)
    used.load(gripped)  # leaves the grasp offset in the cached RCC model
    used.load(rigid)  # model switch
    used.load(nominal)  # switch back: payload and dynamics are derived again
    assert used.fixture_dynamics == fresh.fixture_dynamics
    assert used.true_payload.mass_kg == fresh.true_payload.mass_kg
    assert np.array_equal(used.true_payload.com_in_sensor, fresh.true_payload.com_in_sensor)
    # and the trial's own grasp is still applied after the switch
    used.load(gripped)
    assert np.array_equal(used.model.body_pos[used._connector_body], GRASP.p)


@needs_arm
@pytest.mark.slow
def test_arm_trial_row_is_the_same_fresh_or_after_other_trials():
    from defex.control.registry import make_controller
    from defex.sim.arm_backend import MuJoCoArmBackend
    from defex.tasks.insertion import InsertionTask
    from experiments.runner import nominal_socket_pose

    cond = conditions_by_name()["generalization_combined"]

    def run(task, ctrl, i):
        sc = sample_scenario(cond, i, 2027, nominal_socket_pose(cond, task.fixture))
        row = task.run(make_controller(ctrl), sc).to_row()
        row.pop("wall_time_s")
        return row

    fresh = run(InsertionTask(backend=MuJoCoArmBackend()), "spiral_rcc", 0)
    task = InsertionTask(backend=MuJoCoArmBackend())
    run(task, "spiral_rcc", 1)  # grasp error of trial 1 left in the RCC model
    run(task, "spiral_pull", 1)  # rigid wrist: model switch
    assert run(task, "spiral_rcc", 0) == fresh
