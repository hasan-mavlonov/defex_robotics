"""Post-hoc (v0.2f retract cap): per-tick trace of one trial, uncapped then capped: state, tared axial F, setpoint
and TCP z, true and estimated depth, latch-hook force, latch broken. Development seeds only.

    PYTHONPATH=. python results/v0.2f_baseline_retract_cap/trace_trip.py gantry mf_noise_1mm spiral 7 2026 5.09 5.17
"""
import os, sys
from dataclasses import replace
assert int(sys.argv[5]) in (2026, 2027), "development seeds only"
os.environ["DEFEX_BACKEND"] = sys.argv[1]
from experiments.v02f_pull_overshoot import _install_hook_probe
probe = _install_hook_probe(0.0, None)
import defex.sim.mating as mating
from defex.config import MM
from defex.control.registry import make_controller
from defex.tasks.conditions import latching_conditions
from defex.tasks.insertion import InsertionTask
from defex.tasks.scenarios import sample_scenario
from experiments.runner import make_backend, nominal_socket_pose
cond = {c.name: c for c in latching_conditions()}[sys.argv[2]]
task = InsertionTask(backend=make_backend())
for cap in (False, True):
    ctrl = make_controller(sys.argv[3])
    ctrl.cfg = replace(ctrl.cfg, retract_pull_cap=cap)
    sc = sample_scenario(cond, int(sys.argv[4]), int(sys.argv[5]), nominal_socket_pose(cond, task.fixture))
    rows = []
    def on_step(info):
        h = probe["tick_max"]; probe["tick_max"] = 0.0
        o = info.obs; c = info.controller
        rel = info.gt.socket_pose.inv() @ info.gt.connector_pose
        rows.append((info.t, c.state, float(o.force[2] - c.bias_f[2]), float(o.setpoint.p[2]), float(o.fixture_tcp.p[2]), -rel.p[2] / MM, o.depth / MM, h, info.gt.latch_broken))
    probe.update(trial_max=0.0)
    res = task.run(ctrl, sc, on_step=on_step)
    print("cap", cap, res.success, res.failure_reason, "hookmax", round(probe["trial_max"], 1), "intact", res.final_latch_intact)
    t0 = float(sys.argv[6]); t1 = float(sys.argv[7])
    for r in rows:
        if t0 <= r[0] <= t1:
            print(f"{r[0]:.3f} {r[1]:9s} Fz={r[2]:+6.1f} sp_z={r[3]*1e3:8.3f} tcp_z={r[4]*1e3:8.3f} true_d={r[5]:6.2f} est_d={r[6]:6.2f} hook={r[7]:5.1f} broken={r[8]}")
