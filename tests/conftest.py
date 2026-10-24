from __future__ import annotations

import numpy as np
import pytest

from defex.config import ConnectorSpec
from defex.sim.backend import SceneParams
from defex.sim.mujoco_backend import MuJoCoBackend
from defex.tasks.insertion import InsertionTask
from defex.utils.transforms import Pose


@pytest.fixture(scope="session")
def spec() -> ConnectorSpec:
    return ConnectorSpec.load("rect_12x8")


@pytest.fixture()
def backend(spec) -> MuJoCoBackend:
    be = MuJoCoBackend()
    be.load(SceneParams(spec, spec.friction, Pose.identity()))
    be.load(SceneParams(spec, spec.friction, be.nominal_socket_pose))
    return be


@pytest.fixture(scope="session")
def task() -> InsertionTask:
    t = InsertionTask()
    spec = ConnectorSpec.load("rect_12x8")
    t.backend.load(SceneParams(spec, spec.friction, Pose.identity()))
    return t


@pytest.fixture(scope="session")
def rng() -> np.random.Generator:
    return np.random.default_rng(1234)
