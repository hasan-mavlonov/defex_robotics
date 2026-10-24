"""The receptacle is a real, open cavity with the specified clearance and lead-in."""

import mujoco
import numpy as np
import pytest

from defex.config import MM, ConnectorSpec
from defex.sim.scene_builder import (
    GRIPPER_GEOM_NAMES,
    PLUG_GEOM_NAMES,
    SOCKET_GEOM_PREFIX,
    build_workcell_xml,
    socket_collision_shapes,
)


def _solid(shapes, p):
    """True if point p (socket frame) lies inside any socket collision solid."""
    for s in shapes:
        if s["kind"] == "box":
            if np.all(np.abs(p - s["pos"]) <= s["half"] + 1e-12):
                return True
        else:
            V = s["vertices"]
            # Convex prism: inside iff inside its 2D profile and within its extrusion range.
            n = len(V) // 2
            prof, other = V[:n], V[n:]
            axis = other[0] - prof[0]
            L = np.linalg.norm(axis)
            axis = axis / L
            t = np.dot(p - prof[0], axis)
            if t < -1e-12 or t > L + 1e-12:
                continue
            q = p - t * axis
            # In-plane test using the profile polygon (convex): same side of every edge.
            c = prof.mean(axis=0)
            inside = True
            for i in range(n):
                a, b = prof[i], prof[(i + 1) % n]
                nrm = np.cross(b - a, axis)
                if np.dot(nrm, c - a) < 0:
                    nrm = -nrm
                if np.dot(nrm, q - a) < -1e-12:
                    inside = False
                    break
            if inside:
                return True
    return False


def test_cavity_is_open(spec, rng):
    shapes = socket_collision_shapes(spec)
    hx, hy = spec.cavity_half
    for _ in range(4000):
        p = np.array([rng.uniform(-hx, hx), rng.uniform(-hy, hy), rng.uniform(-spec.depth + 1e-6, 0.002)]) * 0.999
        assert not _solid(shapes, p), f"cavity blocked at {p / MM} mm"


def test_walls_floor_and_chamfer_are_solid(spec):
    shapes = socket_collision_shapes(spec)
    hx, hy = spec.cavity_half
    ox, oy = spec.outer_half
    ch, D = spec.chamfer, spec.depth
    eps = 0.02 * MM
    # Wall material just outside the cavity, below the lead-in
    assert _solid(shapes, np.array([hx + eps, 0.0, -D / 2]))
    assert _solid(shapes, np.array([0.0, -hy - eps, -D / 2]))
    # Floor just below the seat
    assert _solid(shapes, np.array([0.0, 0.0, -D - eps]))
    # Top face beyond the lead-in
    assert _solid(shapes, np.array([hx + ch + 0.5 * (ox - hx - ch), 0.0, -eps]))
    # 45 degree lead-in: free above the chamfer plane, solid below it
    for f in (0.25, 0.5, 0.75):
        x = hx + f * ch
        z_plane = -ch + (x - hx)
        assert not _solid(shapes, np.array([x, 0.0, z_plane + eps]))
        assert _solid(shapes, np.array([x, 0.0, z_plane - eps]))
    # Mitred corner: surface = max of both chamfer planes
    x, y = hx + 0.3 * ch, hy + 0.6 * ch
    z_surface = -ch + max(x - hx, y - hy)
    assert not _solid(shapes, np.array([x, y, z_surface + eps]))
    assert _solid(shapes, np.array([x, y, z_surface - eps]))


def test_contact_model_is_explicit_and_complete(spec):
    m = mujoco.MjModel.from_xml_string(build_workcell_xml(spec))
    held = [m.geom(n).id for n in (*PLUG_GEOM_NAMES, *GRIPPER_GEOM_NAMES)]
    sock = [i for i in range(m.ngeom) if m.geom(i).name.startswith(SOCKET_GEOM_PREFIX)]
    # MuJoCo stores each pair in its own normalized order: compare unordered pairs.
    pairs = {frozenset((int(m.pair_geom1[i]), int(m.pair_geom2[i]))) for i in range(m.npair)}
    for h in held:
        for s in sock:
            assert frozenset((h, s)) in pairs, (m.geom(h).name, m.geom(s).name)
    # No other geom takes part in automatic collision detection: nothing invisible can collide.
    for i in range(m.ngeom):
        assert m.geom_contype[i] == 0 and m.geom_conaffinity[i] == 0, m.geom(i).name


def _place(backend, dx, dy, depth, yaw=0.0):
    """Kinematically place the plug tip relative to the mouth (geometry test only)."""
    m, d = backend.model, backend.data
    q = np.zeros(6)
    home = backend.home_tcp_pose.p
    mouth = backend.nominal_socket_pose.p
    q[:3] = mouth + np.array([dx, dy, -depth]) - home
    q[3] = yaw
    backend.set_joint_positions_kinematic(q)
    return backend.contact_wrench()[2]


@pytest.mark.parametrize("axis", [0, 1])
def test_radial_clearance(backend, spec, axis):
    c = spec.socket.clearance_mm * MM
    for sign in (-1, 1):
        off = np.zeros(2)
        off[axis] = sign * (c - 0.05 * MM)
        assert _place(backend, off[0], off[1], spec.depth - 1 * MM) == 0
        off[axis] = sign * (c + 0.05 * MM)
        assert _place(backend, off[0], off[1], spec.depth - 1 * MM) > 0


def test_yaw_capacity_matches_geometry(backend, spec):
    # A 12 x 8 plug in a 13 x 9 cavity fits up to asin(4.5 / hypot(6, 4)) - atan2(4, 6) = 4.92 deg of yaw.
    assert _place(backend, 0.0, 0.0, spec.depth - 1 * MM, yaw=np.deg2rad(4.3)) == 0
    assert _place(backend, 0.0, 0.0, spec.depth - 1 * MM, yaw=np.deg2rad(5.2)) > 0


def test_seated_plug_bottoms_on_floor(backend, spec):
    assert _place(backend, 0.0, 0.0, spec.depth - 0.01 * MM) == 0
    assert _place(backend, 0.0, 0.0, spec.depth + 0.01 * MM) > 0
