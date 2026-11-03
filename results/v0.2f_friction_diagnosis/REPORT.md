v0.2f friction diagnosis: why C loses arm friction_1 under the pyramidal cone

POST HOC throughout. Every analysis here was chosen after the sim_randomization_v0.2f and
benchmark results were seen. Nothing here was pre-registered. No controller was changed, nothing
was tuned or selected. Simulation only.

Code: experiments/friction_diagnosis_v02f.py (replay, trace, development counts) and
experiments/friction_diagnosis_v02f_classify.py (event-log classes), on branch
v0.2f/friction-diagnosis from v0.2f/integration (d29d43f). MuJoCo 3.17.0.

RESULT IN ONE PARAGRAPH

C's loss is a false reject in VERIFY's wall probe on the stiff arm. C seats the part correctly
(14.6 mm deep, true yaw about 1 deg, tilt under 0.02 deg). VERIFY then probes the two y walls with
a 1 N axial preload and stops each probe when the lateral F/T reaction reaches 2 N. At mu = 1 the
floor friction under the preload reaches 2 N before the plug meets a wall, so the probe stops after
0.03-0.1 mm of real plug travel. The wall-yaw check reads this as "too little free travel"
(about 0.03-0.07 mm half travel against 0.293 mm needed) and rejects the part. Recovery re-aims
by 0.3 deg and repeats the same probe, which fails the same way, until the 26 s time limit. The
pyramidal cone makes this happen on nearly every trial because MuJoCo ignores the model's
softer friction reference time (solreffriction, 20 ms) under pyramidal cones. The same failure
appears on the nominal elliptic simulator when only that one parameter is set to the normal
contact time (2 ms). F, H and I do not run a wall probe. J runs the same VERIFY code, but on F's
RCC stage. There the probe force builds through a 5.78 N/mm spring and the plug slides to the
wall. On the nominal arm (elliptic), C's friction_1 losses are a weaker form of the same
wall-probe stall (6 of 18) and torque protective stops just over the 0.6 N m limit (11 of 18),
mostly at wall or floor impacts.

1. REPLAYS AND TRACES OF NAMED FAILURES

Method. "trace" rebuilds the workcell the way the reported run did. --source simrand --variant k
calls draw_variant(k, 20261205, "arm") and make_task from experiments/sim_randomization_v02f.py.
--source nominal is variant 0, which is what experiments.runner builds. Every replay reproduced
the reported row: the same failure reason, the same event times and the same final depth. The
trace records each control tick. It records the tared F/T wrench, the true plug pose relative to
the true socket, and the contact forces on the held parts. Those forces are split by socket
feature (floor, x walls, y walls, lead-in) into a normal part and a friction part
(mj_contactForce). Outputs are in traces/ (*.events.txt, and *.probes.csv with one row per VERIFY
wall probe).

Randomized run, pyramidal variants, friction_1 (seed 20261205)
- v4 #0 (time_limit, 3 retries):
  - Seated at 14.59 mm, true yaw -1.04 deg, tilt <= 0.01 deg.
  - Wall probes: setpoint 0.24-0.48 mm, plug 0.035-0.12 mm. At the stop, the only contact is the
    floor: normal 2.2-2.7 N, friction 2.25-2.65 N.
  - Wall-yaw half travel 0.035, 0.048, 0.031, 0.032 mm, need 0.293 mm.
  - One "turn +4.43 deg" correction was blocked at once (the plug was not yawed).
  - FAIL three times, then time limit.
- v6 #1 (protective_stop): the same probe stall (half travel 0.022, 0.054 mm, true yaw
  +0.54 deg). Then stuck_during_retract and |F| = 30.1 N at the retract.
- v12 #0 (stuck_during_retract): the same probe stall (half travel 0.041, 0.077 mm, true yaw
  -1.03 deg). The retract after the failed check got stuck.
- v8 #4 (retry_limit): a second, minor mode, the mouth stall. Eight surface_block diagnoses at
  depth 0.00 mm with lateral force near 0 and CoP (0, 0). The localizer moves the probe up to 5 mm
  away from the hole and never enters.
- v11 #4 (time_limit): the same mouth stall six times. The plug enters on the seventh attempt and
  is seated at 26.1 s, just before the limit.

The mouth stall is not traced further. It is consistent with a self-locking lead-in. The chamfer
is 45 deg and tan 45 deg = 1 = mu, so the chamfer reaction can come out almost purely axial. The
localizer then reads it as the top face. Treat this as a hypothesis.

Counts for every trial, from the run's own event log. That file (events.json.gz) is not committed
with the run; it was read from the sim_randomization worktree. The classes are in
simrand_friction_1_classes.txt.
- Pyramidal variants, C: 89 failures of 90. In 85 of them C reached the floor (seated_candidate)
  and then failed VERIFY: 74 time_limit, 7 protective_stop, 4 stuck_during_retract. 1 is a mouth
  stall and 3 are other (2 time_limit with late mouth stalls, 1 protective stop).
- G: 89 failures of 90, all verify_reject.
- J: 89 of 90 seated (1 jam).
- Wall-yaw checks on friction_1 (each line is one check):
  - pyramidal C: 308 checks, median half travel 0.053 mm, 100% below 0.293 mm;
  - elliptic C: 98 checks, median 0.431 mm, 17% below;
  - J: 0% below on both cones (medians 0.456 and 0.465 mm).
- On the nominal condition (mu = 0.3), pyramidal C has 90 checks, median 0.448 mm, 0% below. The
  effect needs high friction.
- Per variant, the stall happens in all six pyramidal variants, with medians 0.027-0.104 mm. It
  does not depend on the drawn impratio (3.4-18.9), wrist stiffness factor (0.50-1.60), latency or
  solreffriction (11-40 ms, which pyramidal ignores). The six elliptic variants have medians
  0.401-0.440 mm, with solreffriction 12.4-33.7 ms.

Counterfactual replays of the same scenario (seed 20261205, friction_1 #0, C):
- nominal (elliptic, solreffriction 20 ms): seated in 7.87 s. Half travel 0.390 mm, PASS; the
  plug travels 0.64 mm per probe.
- nominal with only cone = pyramidal: time_limit. Half travel 0.048, 0.027, 0.033, 0.067 mm.
- pyramidal with impratio 1: time_limit. Half travel 0.083, 0.017, 0.038 mm.
- elliptic with solreffriction = 2 ms (the normal solref): time_limit. Half travel 0.030, 0.053,
  -0.006, 0.050 mm.
- v4 as drawn, J: seated in 7.52 s. Half travel 0.410 mm, PASS; the plug travels 0.66 and
  0.80 mm.
So the cone alone reproduces the loss, impratio does not matter, and an elliptic cone with stiff
friction dynamics reproduces it too. The common factor is friction dynamics as stiff as the
normal contact.

What the contact does during C's probe (v4 #0, probes.csv):
- The floor contact is on in only 59-77% of ticks.
- The floor normal force averages 1.0 N, which is the regulated preload, but peaks at 2.2-6 N.
- Friction is at the cone limit at those peaks.
- Under the nominal elliptic cone the floor normal force averages 1.0-1.2 N and peaks at 1.4 N,
  apart from the single wall-impact tick.
- In J's probe the floor normal force peaks at 1.9 N, the contact is on in 98% of ticks, and
  friction/normal is 0.50-0.78 (sliding).

The encoder reading is correct. C's measured half travel (0.035 mm) matches the true plug
positions (-0.227 and -0.289 mm, half difference 0.031 mm). The plug really did not move. What is
wrong is the stop rule: it treats a 2 N reaction as a wall.

Nominal benchmark, elliptic, friction_1 (benchmark_v0.2e, seed 20261130)
- #8 (protective_stop at 5.80 s): the plug descends pressed against the -y wall
  (y = -0.482 mm). On the tick it reaches the floor (5.798 s), one physics tick shows 100.8 N
  floor normal, 85.4 N wall normal and 90 N floor friction. The F/T torque reads 0.65 N m, over
  the 0.6 N m limit.
- #51 (protective_stop at 8.08 s): seated, and the first wall probe passed. The second (-y) probe
  hits the wall: one tick with 74.6 N wall normal and 65.9 N floor friction. |T| = 0.62 N m.
- #21 (time_limit): a different case.
  - After a surface_block, C's recovery runs a "yaw search +3 deg", and the plug enters with a
    true yaw of +3.95 deg.
  - VERIFY's wall-yaw rejection was correct (half travel 0.016-0.026 mm; even without sticking a
    3.95 deg plug has only 0.096 mm).
  - The re-aim kept +2.8 deg of yaw, and time ran out.

All C friction_1 failures in the three nominal benchmarks (benchmark_friction_1_failures.txt,
from the committed events; v0.2d and its replication ran the v0.2d code):
- 18 failures (7 + 6 + 5, the 0/7, 0/6, 0/5 of CONCENTRATION.md).
- 6 end in time_limit after repeated wall-yaw rejects with half travel 0.014-0.22 mm (one of
  them is #21, a true yaw).
- 11 are torque protective stops at 0.61-0.71 N m: 5 during VERIFY wall probes, 3 at floor
  arrival, 3 during a re-insert. Two of the 11 came after a wall-yaw reject.
- 1 is a mouth stall (retry_limit).
- J seated 300 of 300.
- C's wall-yaw checks below 0.293 mm on friction_1: 17/110, 6/100 and 5/100. J's: 0 on every seed.

The torque budget at mu = 1 (from the committed trials.csv, peak_measured_torque_nm, friction_1):
- C has a median peak of 0.32-0.34 N m on all three seeds; F, I and J have 0.06-0.07, and H
  0.08-0.09.
- At friction_0.6, C has 0.08-0.09.
- On dev seed 2026 (6 friction_1 trials, all seated), C's peak torque falls in VERIFY, at the tick
  a wall probe stops, in every trial: 0.34-0.55 N m.
- So at mu = 1 the wall-probe impact on the stiff arm uses most of the 0.6 N m protective-stop
  margin, and the stops are its tail. H (stiff arm, no RCC) also has stops (2, 5 and 0 trials
  over 0.6 N m). Its stops do not come from a wall probe; their source was not traced.

2. WHY F, H, I AND J DO NOT FAIL

- F, H and I have no wall-probe VERIFY on housing-only parts. H runs on the same stiff arm and
  seats 89-90 of 90 pyramidal friction_1 trials. So the stiff arm and the pyramidal contact do not
  prevent insertion.
- J runs C's VERIFY code with C's settings, so J passing does show that the check's logic is
  sound when the probe can reach the wall. It does not show that the failure is in C's insertion
  or recovery. The failure is in VERIFY as it runs on C's stiff wrist, not in insertion. Recovery
  only adds to it.
  - Insertion is correct. In every traced pyramidal VERIFY failure, the part was seated with true
    yaw at most 1.04 deg and tilt under 0.02 deg.
  - The failing element is the wall probe's stop rule. It ends the probe at a 2.0 N F/T reaction
    and assumes the floor contributes at most mu x preload. That assumption breaks when the
    instantaneous floor normal force peaks at 2-6 N under a regulated 1 N mean, and mu = 1.
  - On J's RCC stage the same rule works. J adds the RCC deflection (verify_force_n / k) to C's
    setpoint-lead allowance, the lateral force builds slowly through the spring, and the floor
    contact stays on (98% of ticks, peak 1.9 N). For comparison, C's floor contact is on in 72-77%
    of ticks under the nominal elliptic cone too, and C passes there; what differs under the
    pyramidal cone is the normal-force peaks (2.2-6 N against 1.4 N).
  - Recovery adds to the loss. After a failed check it changes only the aim (0.3 deg tilt), not
    the probe. Each repeat costs about 6.5 s, so 3-4 attempts reach the 26 s limit. Some retracts
    then get stuck or trip a protective stop.
- G shares C's VERIFY and fails the same way (89 of 89 failures are verify rejects).

3. DEVELOPMENT SEEDS 2026 AND 2027 (dev_counts/)

The arm, 20 trials per cell, --workers 2, 1,080 trials, 405 s. The three simulators are built by
the same script:
- (a) elliptic_nominal: variant 0, the nominal arm.
- (b) pyramidal_cone_only: the nominal arm with only SimConfig.cone = "pyramidal" (built through
  make_task with servo factors 1.0 and nominal latency).
- (c) elliptic_fric_2ms: elliptic with contact_friction_timeconst_s = 0.002. This is a mechanism
  check, not one of the requested arms.

Seated, seed 2026 / seed 2027 (dev_counts/summary.csv). Columns: (a) / (b) / (c).
- friction_1:
  - C: 20/19, 0/0, 0/0
  - F: 20/20, 20/20, 20/20
  - J: 20/20, 20/20, 20/20
- friction_0.6:
  - C: 20/20, 14/15, 16/17
  - F: 20/20, 20/20, 20/20
  - J: 20/20, 20/19, 20/20
- nominal:
  - C: 20/20, 20/20, 20/20
  - F: 20/20, 20/20, 20/20
  - J: 20/20, 18/19, 20/20

- The mechanism reproduces off the reported seed.
  - friction_1, C: 39/40 seated nominal, 0/40 pyramidal, 0/40 with 2 ms friction.
  - Under the pyramidal cone, VERIFY failed in 37 of C's 40 friction_1 trials, and the median of
    each trial's smallest wall-yaw half travel is 0.005 / 0.007 mm.
  - friction_0.6, C: 40/40, 29/40 and 33/40. Under the pyramidal cone VERIFY failed in 20 of 40
    trials (median smallest half travel 0.289 / 0.175 mm). Failures are 11 time_limit. With
    mu = 0.6 the floor friction peak sits near the 2 N stop.
  - nominal (mu = 0.3), C: 40/40 on all three simulators.
- F and J: every friction cell 40/40 on all three, except J pyramidal friction_0.6 at 39/40. The
  one J miss there, and all three J misses on nominal under the pyramidal cone (2 + 1), are
  false_accept.

Side observation, not investigated: J passed 4 bad units in 120 pyramidal trials (3 on nominal,
1 on friction_0.6) and 0 in 240 elliptic trials. This matches the randomized run's report (J: 30
bad units of 1,020 pyramidal good-part trials against 1 of 1,020 elliptic). It is a VERIFY false
accept on the RCC stage and needs its own trace.

4. IS THE PYRAMIDAL CONE MORE OR LESS REALISTIC HERE?

MuJoCo's documentation (doc sources read 2026-11-02 from google-deepmind/mujoco main):
- XMLreference, option/cone: "Elliptic cones are a better model of the physical reality, but
  pyramidal cones sometimes make the solver faster and more robust."
- modeling.rst: "Elliptic cones correspond more closely to physical reality. ... While the
  default is pyramidal, we recommend trying the elliptic cones."
- computation: "elliptic and pyramidal friction cones define different soft-contact dynamics
  (although they are usually very close). The elliptic model is more principled and more
  consistent with physical intuition".
- XMLreference, pair/solreffriction: it "only takes effect for elliptic friction cones, since
  pyramidal cones mix normal and frictional forces."
- XMLreference, option/impratio: "it is not recommended to use high impratio values with
  pyramidal cones."

So MuJoCo's own position is that the elliptic cone is the closer model. Two facts bear on this
benchmark:
- The repo's nominal contact uses solreffriction = 20 ms (SimConfig.contact_friction_timeconst_s,
  set to stop normal-force inflation during sliding). Under the pyramidal cone that setting is
  dropped. So a pyramidal variant is not only a different cone; it also undoes a deliberate
  contact setting.
- The randomization drew impratio 3-20 for every variant, including pyramidal ones, which the
  documentation advises against. In the counterfactual replay impratio did not matter (impratio 1
  failed the same way).

Neither cone is claimed here to be right for the real part. MuJoCo's soft contact is a
regularized model under either cone. The failure depends on two things that are properties of
the real cell, not of the solver:
- the instantaneous floor normal force during a 1 N preload, and how far it peaks above the mean;
- the floor friction while the plug slides sideways at 5 mm/s.

Also, friction_1 (mu = 1.0) is well above the connector default (0.3, "PBT-GF on PBT, dry, typ.
0.25-0.35" in defex/config.py).

What a rig measurement would settle:
- On the real cobot with the real housing and receptacle, seat the plug, hold C's 1 N axial
  preload, and run C's lateral wall probe at 5 mm/s. Log the F/T at the full rate and the
  encoder position.
- From that log:
  - the lateral force while the plug slides on the floor, as mean, peak and its ratio to the
    axial force;
  - the peak-to-mean ratio of the axial force under force control;
  - whether the plug moves with the setpoint before it meets a wall (stick-slip or smooth
    sliding).
- Measure the static and kinetic friction coefficient of the housing pair, which bounds whether
  mu = 1 is reachable at all.
- Log the F/T torque at the wall impact, filtered the way the cell's protective stop filters it.
  That settles the torque-stop mode.
- If the measured floor friction peak stays under the 2 N stop with margin, the pyramidal result
  does not transfer. If it does not, the rig shows the same false reject.

5. WHAT A FIX WOULD LOOK LIKE (TEXT ONLY; NOTHING WAS CHANGED OR RUN)

C design changes. These apply to J too, which uses C's VERIFY, so equal effort is automatic for
J; F, H and I have no wall probe.
1. Stop a wall probe on a wall signature, not a force level alone: the reaction rises while the
   encoder position stops advancing, at a stiffness consistent with a wall. A probe that reaches
   2 N while the plug has moved much less than the setpoint, minus the servo lead, has been
   stopped by friction. It should be treated as inconclusive, and the probe repeated at a lower
   preload. It should not be counted as a wall contact.
2. Tie the preload to the friction bound: verify_preload_n x mu_max x (peak / mean axial force)
   below verify_force_n. Or probe with the axial force loop relieved (near zero preload) once
   the seat depth is confirmed. The config comment at verify_preload_n already states the
   mean-force form of this assumption; it is the peaks that break it.
3. After a verify failure, change the probe rather than only the aim. Repeating the identical
   probe cannot pass if friction stopped it.
4. For the torque stops: approach walls and the floor more slowly on a stiff wrist, or add a
   soft lateral admittance during the wall probe (a software RCC). At mu = 1, C's wall-probe
   impact uses 0.34-0.55 N m of the 0.6 N m protective stop on the nominal simulator.

Any of these is a C design change. It would need the usual equal-effort accounting and a new
pre-registered run on a fresh seed. The reported pyramidal and benchmark results stay as they are.

Settings that are fair to all controllers (simulator or benchmark design, not controller):
- Randomize friction dynamics explicitly: draw contact_friction_timeconst_s down to the normal
  solref (2 ms) under the elliptic cone. Or record that a pyramidal draw drops solreffriction,
  and stop drawing high impratio with it. This applies to every controller equally.
- Tie friction_1's mu to a measured value for the target housing once the rig gives one.
- Any such change to a randomization or condition design is itself post hoc relative to this
  result and must be pre-registered before it is run.

FILES

- traces/: events and per-probe tables. The named runs are simrand v4 #0 (C and J), v6 #1,
  v8 #4, v11 #4, v12 #0; v0.2e (20261130) #8, #21, #51; the counterfactual replays of seed
  20261205 #0; and dev seed 2026 #0 nominal and pyramidal.
- simrand_friction_1_classes.txt: event classes of every friction_1 C, G and J trial in the
  randomized arm run. It needs that run's uncommitted events.json.gz.
- benchmark_friction_1_failures.txt: every C and J friction_1 failure in the three nominal
  benchmarks.
- dev_counts/: trials.csv, summary.csv, config.json, run_time.json (no events file).
