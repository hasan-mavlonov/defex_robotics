# v0.2f: real-time fit of the controller step, and pull-test force overshoot


Development measurements only, on development seeds 2026 and 2027, at commit 4df8cae (the
v0.2e code). No controller behaviour was changed. Every timing number comes from an Apple M5
laptop (4 performance and 6 efficiency cores) shared with other agents' simulations. It is
not the rig PC.

Scripts: `experiments/v02f_tick_timing.py` (Part 1), `experiments/v02f_pull_overshoot.py`
(Part 2), tests in `tests/test_v02f_measurement_tools.py`. Tables: `timing/TABLES.md`,
`pull/TABLES.md`, `pull_counterfactual/TABLES.md`, each rebuilt by the script's `--tables`
mode from the committed per-run files.

## Summary

**Part 1.** The controller's own work fits a 2 ms (500 Hz) tick on this laptop. The work that
would run on the rig PC each tick (state estimator + controller step + motion generator)
takes about 43-50 us at the median for C and G and 30-43 us for F, I and J (wall clock, in
the trial loop). The intrinsic cost of `controller.step` (the fastest of the in-loop call and
three exact replays of the same observations) never exceeded 2 ms in any of about 12.6
million ticks measured. Its p99.9 is 30-70 us. Its maximum is 0.62-0.64 ms for C and
0.81-0.89 ms for G at load below about 10, and 1.2-1.5 ms under heavy load. J's maximum is
0.25 ms, F's and I's below 0.08 ms. All of the slowest ticks are one event: the RECOVER tick
that ends a retract and plans the next attempt (`_plan_correction`: hole-localizer
posterior update, G's learned prior, probe selection). It runs once per blocked attempt,
with the tool at rest above the socket.

The wall-clock budget was broken by two things outside the controller logic: preemption
by other load, and Python garbage collection. At load below about 10, 66 of 1.0 million
gantry ticks and 46 of 1.6 million arm ticks took longer than 2 ms. 59 and 24 of them had a
GC collection in them; full collections took up to 9-11 ms. Under heavy load (1-minute
load average 30-180), 0.04-0.3% of ticks were over 2 ms, almost all of them preempted
(thread CPU time low). A rig needs a quiet core, GC control and its own per-tick log.

**Part 2.** The guarded pull of C, G, H, I and J at 35.2 N barely overshoots in the model.
There were 7,779 pulls over the latching and latch_spread suites, both machines, both seeds,
20 trials per cell. 2 exceeded the commanded force by more than 10% (measured, tared,
filtered F/T), and none by more than 25%. The largest measured pull force was 42.4 N. The
latch-hook force in the simulator peaked at 41.9 N inside a pull window, below the 58 N
retention (which is also the damage force). No latch broke in any pull window. No good
part failed because of a pull. The overshoot that exists is on the gantry, almost only with
high terminal friction (`mf_terminal_max`, `mf_spread`): there the plug rings on the latch
hook at about 105-120 Hz. In a counterfactual run with 300 N s/m of damping on the hook, the
ringing disappeared: peak/target maximum 1.001, against 1.096 on the same 253 pulls, with
the same outcomes. So the ringing comes from the simulator's undamped hook, not from the
controllers. Separately, H's retry retract (not its pull) broke the latch of two good gantry
parts. H has no gentle-retract cap, and the 48 N measured-force protective stop fired only
after the hook had passed 58 N.

## Part 1: does the controller fit the real-time loop?

### Control rates in the code

- Both simulated machines use `SimConfig.control_period_s = 0.002` (500 Hz, `defex/config.py`)
  with 2 kHz physics (`timestep_s = 0.0005`); the loop is `InsertionTask.run`
  (`defex/tasks/insertion.py`).
- Arm: `defex/sim/arm_backend.py` takes Cartesian setpoints "at the 500 Hz control rate (UR
  RTDE servoL class)", delayed by `latency_s = 0.006` (3 periods). The real driver
  `URRTDEMotionDriver` (`defex/hardware/drivers.py`) calls `servoL(..., 0.002, ...)`: 500 Hz.
- Gantry: simulated at the same 500 Hz. The real gantry's command rate is not known:
  `hardware/BOM.md` says no 500 Hz external command rate is published for the Zaber stages,
  and it must be measured on the bench. A Franka FCI loop would be 1 kHz (BOM.md), a 1 ms
  budget; the slowest planning ticks under load (1.2-1.5 ms) would not fit it.

### What was timed and how

`experiments/v02f_tick_timing.py` runs normal trials single-process (no worker pool) and
times, every control tick, the code a rig PC would run:

- `est`: `StateEstimator.update` (payload compensation, tare, F/T filter, frames);
- `ctrl`: `controller.step` (FSM, contact diagnosis, hole localizer, learned prior, VERIFY,
  recovery planning);
- `motion`: `CartesianMotionGenerator.update`.

`total` is their sum (wall clock). `cpu` is the thread CPU time over the same span: wall
minus CPU is time the process was not running. After each trial, the observation stream
the controller saw is replayed into fresh controllers three times without physics. The first
replay must reproduce every command bit for bit, and it did in every trial (checked by the
script; a mismatch aborts). `best` is the minimum of the in-loop `ctrl` time and the three
replays: the intrinsic cost with most scheduling noise removed. GC collections inside a tick
are counted. Inclusive sub-timers wrap the localizer, learned-prior, diagnosis and VERIFY
helpers. A test (`test_tick_replay_reproduces_the_trial_commands`) checks the replay.

Not timed: MuJoCo physics; the arm backend's IK (on a UR the robot controller does it
behind servoL; the gantry's is trivial); the simulator's synthetic sensor noise; the rig's
I/O (F/T UDP read, servoL send). I did not use the mock `HardwareBackend` in
`defex/hardware/`. Its stage is a quasi-static spring floor with no hole, so the controllers
would never reach RECOVER, the localizer or the latching VERIFY, which are the paths that
matter here. Timing inside the simulated loop covers every state.

Coverage per run: the standard, latching and latch_spread suites (36 conditions), for C, G,
J, F and I. Loaded runs: 2 trials per cell, both seeds (720 trials). Low-load runs: 1 trial
per cell, one seed each (180 trials).

### Runs and load (uptime 1-minute load average per trial, from each config.json)

| run | machine | trials | ticks | load min / mean / max | label |
|---|---|---|---|---|---|
| run1_gantry | gantry | 720 | 1,996,009 | 31.4 / 48.4 / 74.0 | loaded; superseded (see below) |
| run2_gantry | gantry | 720 | 1,996,009 | 39.3 / 62.3 / 101.3 | loaded |
| run2_arm | arm | 720 | 3,186,355 | 30.8 / 78.1 / 183.6 | loaded |
| run4_gantry_quiet | gantry | 180 (seed 2026) | 500,233 | 7.2 / 7.9 / 9.2 | below 8 on average |
| run5_gantry_quiet | gantry | 180 (seed 2027) | 500,282 | 7.3 / 8.0 / 8.6 | at 8 ("loaded" by the script's > 8 rule) |
| run4_arm_quiet | arm | 180 (seed 2026) | 787,178 | 6.8 / 7.6 / 8.6 | below 8 on average |
| run5_arm_quiet | arm | 180 (seed 2027) | 800,460 | 8.4 / 9.8 / 10.7 | loaded (just above 8) |

The low-load runs were taken when the machine's load fell to about 7-10. To keep to one
process at a time, my Part 2 run was paused (SIGSTOP) while they ran. Other agents' jobs
were still running, so "quiet" means lower load, not an idle machine.

### Results at lower load (run4 + run5)

Microseconds per tick. Two values separated by "/" are run4/run5. Source:
`timing/run4_*_quiet/summary.csv`, `timing/run5_*_quiet/summary.csv`.

| machine | ctrl | ticks | total p50 | total p99.9 | total max | total > 2 ms (with GC) | total max, no GC | cpu max, no GC | best p99.9 | best max | best > 0.5 ms | best > 1 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gantry | C | 236,105 | 43.0/43.2 | 205/228 | 8,993 | 16 (14) | 4,675 | 1,207 | 36.2/38.2 | 621 | 20 | 0 |
| gantry | G | 239,431 | 43.6/43.7 | 218/239 | 9,097 | 17 (16) | 9,097 | 1,044 | 35.8/36.6 | 891 | 23 | 0 |
| gantry | J | 220,733 | 35.3/37.6 | 166/199 | 8,859 | 12 (12) | 1,500 | 288 | 32.5/30.7 | 176 | 0 | 0 |
| gantry | F | 121,110 | 30.2/30.5 | 118/274 | 9,546 | 10 (7) | 3,934 | 259 | 13.0/20.9 | 45 | 0 | 0 |
| gantry | I | 183,136 | 31.2/31.5 | 122/136 | 7,685 | 11 (10) | 3,393 | 178 | 18.8/23.8 | 45 | 0 | 0 |
| arm | C | 386,065 | 43.5/46.5 | 232/307 | 11,225 | 13 (4) | 7,461 | 1,307 | 35.2/51.7 | 642 | 32 | 0 |
| arm | G | 378,206 | 44.7/46.5 | 253/284 | 9,850 | 13 (7) | 5,382 | 1,533 | 37.4/52.1 | 812 | 23 | 0 |
| arm | J | 349,327 | 34.9/42.8 | 174/263 | 7,708 | 12 (6) | 7,165 | 523 | 30.5/44.5 | 246 | 0 | 0 |
| arm | F | 200,819 | 30.7/32.5 | 118/182 | 7,338 | 2 (1) | 2,092 | 197 | 13.6/21.1 | 36 | 0 | 0 |
| arm | I | 273,221 | 32.3/34.0 | 124/165 | 7,324 | 6 (6) | 1,419 | 209 | 13.5/21.5 | 40 | 0 | 0 |

Over-budget ticks without a GC collection had low thread CPU time (cpu max without GC is
at most 1.53 ms, on a planning tick): they were preempted, even at this load. Components
at the median: `est` about 11 us, `motion` about 10 us, `ctrl` 16-25 us for C and G.

### Results under heavy load (run2)

Source: `timing/run2_gantry/summary.csv`, `timing/run2_arm/summary.csv`.

| machine | ctrl | ticks | total p50 | total p99 | total p99.9 | total max | total > 2 ms (with GC) | cpu > 2 ms | best p99.9 | best max | best > 1 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gantry | C | 469,173 | 47 | 234 | 1,827 | 64,288 | 437 (33) | 27 | 60.9 | 1,277 | 1 |
| gantry | G | 471,297 | 47 | 208 | 1,173 | 124,799 | 200 (37) | 30 | 59.2 | 945 | 0 |
| gantry | J | 441,168 | 41 | 199 | 1,166 | 79,204 | 231 (30) | 25 | 67.3 | 126 | 0 |
| gantry | F | 246,429 | 33 | 179 | 1,484 | 114,435 | 170 (19) | 16 | 27.0 | 76 | 0 |
| gantry | I | 367,942 | 34 | 183 | 1,445 | 48,088 | 264 (24) | 22 | 26.8 | 75 | 0 |
| arm | C | 751,134 | 49 | 231 | 2,323 | 45,504 | 904 (20) | 7 | 58.4 | 1,212 | 2 |
| arm | G | 739,691 | 50 | 408 | 4,176 | 121,284 | 2,005 (32) | 8 | 61.6 | 1,498 | 3 |
| arm | J | 709,025 | 49 | 190 | 2,765 | 27,054 | 1,118 (34) | 16 | 65.9 | 478 | 0 |
| arm | F | 418,352 | 35 | 108 | 537 | 15,507 | 92 (3) | 3 | 29.2 | 66 | 0 |
| arm | I | 568,153 | 35 | 106 | 536 | 66,699 | 129 (7) | 6 | 29.3 | 69 | 0 |

Every tick over 2 ms of CPU had a GC collection in it, with one exception: one G gantry
planning tick at 2.00 ms of CPU. Under this load even the replays land on efficiency cores,
so the planning tick's `best` grew from 0.6-0.9 ms (low load) to 0.9-1.5 ms.

run1_gantry stored its per-tick records in Python lists of millions of floats. That made
the collector's full passes much slower (CPU maxima up to 270 ms) and the wall-clock tail
worse (2,248 C ticks over 2 ms, against 437 in run2). It is kept as the first loaded
measurement and is superseded by run2. Its intrinsic numbers agree with run2 (C `best`
max 1.13 ms, G 1.59 ms). The script now stores per-trial numpy arrays.

### By FSM state, and the worst ticks

Per-state rows are in `timing/TABLES.md`. For C and G, the `best` maximum in APPROACH,
ALIGN, INSERT, VERIFY and FAILURE stays below 0.25 ms. DETECT reaches 0.34-0.72 ms (p99.9
0.23-0.27 ms: `_diagnose`, the contact diagnosis over the stored window). RECOVER has p99
about 58 us but p99.9 0.6-0.9 ms: the planning tick. The start of the latching VERIFY
(`_begin_latch_verify`: tilt verdict and click detection over the descent trace) is
0.05-0.29 ms at the median.

Every one of the slowest C and G ticks by intrinsic cost is `RECOVER -> ALIGN`. On that
tick the retract reaches its height, and `_recover_step` calls `_plan_correction`
(`defex/control/adaptive_fsm.py`). In one tick that function runs:

- `entry_probability_at` (the posterior and two box filters);
- `update_blocked` (the contact likelihood over the 57 x 57 grid: 0.25 mm cells over
  +/-7 mm);
- for G only, the learned term (`ContactLikelihood.localizer_log_term` for the gantry
  model, `ContactPrior.localizer_term` for the arm model);
- `best_probe` (the posterior and box filters again, with masks for excluded probes).

Medians in run2 (`timing/run2_*/subtimers.csv`, in-loop, inclusive): `_plan_correction`
0.65 ms (C gantry), 0.91 ms (G gantry), 0.66 ms (C arm), 0.77 ms (G arm). Inside it,
`update_blocked` takes 0.33-0.41 ms, `best_probe` 0.15-0.23 ms and the learned term
0.09-0.27 ms. These are numpy calls on small arrays, so per-call overhead dominates.

How often: once per blocked attempt. In run2, C called `_plan_correction` 60 times in 144
gantry trials and 75 times in 144 arm trials. `best` > 0.5 ms occurred on 20-46 ticks per
controller and machine, all planning ticks. `best` > 1 ms occurred on 0-3 ticks per cell
under heavy load and 0 at low load. `best` > 2 ms never occurred.

On the planning tick the tool has finished its retract and is at rest in free space above
the socket. A late command there delays the start of the next move by one tick; it does not
touch a force-controlled contact. Whether servoL (or the gantry's interface) tolerates one
late packet must be checked on the rig. `update_entered` is small (about 40 us). The xy-yaw
localizer is off by default (`localizer_mode = "xy"`), so its 3-D grid was not exercised.

### What would make the rig loop safe (text only; nothing changed)

- Run the 500 Hz loop on an isolated performance core of a quiet PC. Keep GC out of the
  cycle (`gc.disable()` during the cycle and `gc.collect()` between cycles, or
  `gc.freeze()` after `reset`). Log per-tick wall time on the rig from the first run.
- Measure the planning tick on the rig PC. If it is close to the budget, there are two
  behaviour-preserving options: hold the retract pose one extra tick while the plan is
  computed (the tool is at rest there), or compute the plan in a worker during the last
  ticks of the retract. Each shifts timing by at most one tick and needs its own
  equivalence test.
- No optional faster implementation was added. `update_blocked` and `best_probe` are
  already vectorized, and the remaining cost is numpy call overhead on a 57 x 57 grid. The
  two posterior evaluations in `_plan_correction` happen before and after the update, so
  they cannot share a cache without changing the code path.

## Part 2: pull-test force overshoot

### What the controllers command

C's VERIFY pull target is `max(pull_test_fraction x retention, pull_test_mating_factor x
mating max)` = max(0.5 x 58, 1.1 x 32) = 35.2 N (`AdaptiveConfig`, `_begin_latch_verify`). H
and I use the same rule and values (`spiral_search._with_retention_pull`), and J runs C's
VERIFY code. The script reads each controller's own `_pull_target`, and it was 35.2 N in
every pull. 29 N is the 0.5 x 58 N term alone, which is not what C, G, H, I or J pull at.

The pull is a force loop on the setpoint (`ForceGuidedAxis`). It ends on the first tick
whose tared, filtered axial force is at or below -35.2 N, or at the movement limit, or after
3 s.

Model values (`assets/connectors/microfit3_4ckt.json`, `defex/sim/mating.py`):

- The latch retention minimum is 58 N. The engaged hook is a 2e5 N/m spring after 0.1 mm
  of free play, with no damping, and it breaks when its force exceeds 58 N.
- The connector's `damage_n` is also 58 N. But the damage check uses the 10 ms average of
  the housing contact force, and that average does not include the mating force (the
  mating force is applied through `xfrc_applied`). So in the model the latch is protected
  only by its own 58 N break, and by the 48 N protective stop on measured force.

### Method

`experiments/v02f_pull_overshoot.py` runs the normal harness single-process with a
read-only per-tick callback. I checked that its trials.csv rows equal a normal
`experiments.robustness` run on a 10-trial subset, except for wall time. For every pull it
records:

- the commanded force;
- the measured axial force on the tick the guard ends the pull, and its most negative value
  from the pull start to 0.1 s after that tick;
- the simulator's hook force at physics rate (2 kHz), over the same window and over the
  whole trial.

Coverage: the latching suite (7 conditions) and latch_spread (9 conditions), both machines,
seeds 2026 and 2027, 20 trials per cell, controllers C, G, H, I and J: 6,400 trials.

### Counts (development measurement)

Source: `pull/TABLES.md` (from `pull/*/episodes.csv`). "Held" means the guard ended the pull
on force. Peak/target compares the peak measured pull force with the 35.2 N command.

| machine | ctrl | trials | pulls | held | peak/target p99 | max | > 1.10 | > 1.25 | max peak N | max hook N in window | hook > 58 N | max measured abs(F) N |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gantry | C | 640 | 799 | 357 | 1.051 | 1.063 | 0 | 0 | 37.4 | 40.9 | 0 | 37.5 |
| gantry | G | 640 | 801 | 360 | 1.051 | 1.070 | 0 | 0 | 37.7 | 40.8 | 0 | 37.7 |
| gantry | H | 640 | 690 | 345 | 1.056 | 1.070 | 0 | 0 | 37.7 | 41.0 | 0 | 37.7 |
| gantry | I | 640 | 758 | 358 | 1.056 | 1.085 | 0 | 0 | 38.2 | 41.3 | 0 | 39.6 |
| gantry | J | 640 | 740 | 358 | 1.064 | 1.109 | 1 | 0 | 39.1 | 41.9 | 0 | 39.1 |
| arm | C | 640 | 860 | 349 | 1.001 | 1.001 | 0 | 0 | 35.2 | 25.6 | 0 | 35.2 |
| arm | G | 640 | 867 | 356 | 1.001 | 1.001 | 0 | 0 | 35.2 | 25.6 | 0 | 35.2 |
| arm | H | 640 | 731 | 340 | 1.001 | 1.204 | 1 | 0 | 42.4 | 25.6 | 0 | 42.4 |
| arm | I | 640 | 780 | 354 | 1.001 | 1.001 | 0 | 0 | 35.2 | 25.6 | 0 | 35.2 |
| arm | J | 640 | 753 | 354 | 1.001 | 1.001 | 0 | 0 | 35.2 | 25.6 | 0 | 35.2 |

- Pulls more than 10% over the command: 2 of 7,779. Pulls more than 25% over: 0. Pulls more
  than 5% over: 91, of which 90 were held pulls on the gantry.
  - Gantry J, latch_spread seed 2027, `mf_spread` trial 6: peak 39.1 N (1.109 x) with a hook
    peak of 41.0 N. The pull was held and the part passed, seated. This is the ringing
    described below.
  - Arm H, latching seed 2026, `mf_noise_1mm` trial 7: 42.4 N (1.204 x), but this is not
    pull overshoot. The plug stopped 7.29 mm in, not latched (hook force 0). The pull
    reached 35.1 N and timed out (FAIL). The re-push tripped `excess_torque` on its first
    tick, and the 42.4 N came from the FAILURE retract dragging the wedged plug within the
    0.1 s window.
- Arm held pulls: the maximum is 1.018 x. Only 1 of 1,753 is over 1.01 x.
- Retention and damage: the largest hook force in any pull window was 41.9 N, 72% of the
  58 N retention. No latch broke in a pull window. The largest measured abs(F) in a window
  was 42.4 N (the arm H retract above), below the 48 N protective stop, and no pull caused
  a protective stop.
- Good parts: every held pull on a good part that ended unseated had an intact latch and
  another cause: 2 time limits (arm C `mf_latch_weak`, arm G `mf_noise_1mm`) and 1 false
  accept (arm H `mf_latch_early`, seed 2027 trial 14). None was caused by the pull force.
- Most pulls end below the target because the part slides out (bad parts, and good parts
  whose first pull fails before a re-push), so the median peak/target is about 0.84.

### Where the overshoot comes from

Post-hoc breakdown (gantry, held pulls, both seeds): pulls more than 2% over the command by
condition were `mf_terminal_max` 184 of 200, `mf_spread` 57 of 200, `mf_noise_1mm` 4 of
179, `mf_latch_early` 1 of 200, and 0 in every other condition. With terminal forces at
1.6 x, the terminals carry about 19 N of the 35.2 N pull and the hook only about 16 N. That
is about 0.08 mm of hook stretch, the same order as the terminals' 0.05 mm elastic bristle.

The kept traces of the largest overshoots (`pull/gantry_*/trace_*.csv`, six traces,
post-hoc analysis) show a sustained hook-force oscillation at 104-121 Hz, 4.6-6.6 N rms
(high-passed). The hook peaks at 40-42 N against about 16-23 N quasi-static, and the
filtered measured force swings 1-5 N rms. That frequency is about what the 2e5 N/m hook
gives against roughly 0.5 kg of moving gantry mass. On the arm, with stiff joints, there is
no ringing: every held pull ended within 2% of the target.

The controllers' pull itself is slow: about 1.7 s from +35 N to -35 N on the gantry. When
the hook does not ring, the guard trips within 0.1 N of the target.

Counterfactual (`pull_counterfactual/`, simulator only, never the model). I reran the same
gantry trials (seed 2026, `mf_terminal_max` and `mf_spread`, 20 trials, all five
controllers: 253 pulls, 200 held):

- With 300 N s/m of viscous damping on the engaged hook: peak/target maximum 1.001 (model:
  1.096); no pull over 1.02 x (model: 122); median hook force in held pulls 16.2 N (model:
  39.4 N); all 200 trials succeed in both.
- With a 4 x softer hook (5e4 N/m), the latch check itself changes. Only 161 of the 200
  good parts pass: C, G and J fail 7-9 parts each as `stuck_during_retract`, and H and I
  fail 7 and 9 as protective stops. The plug backs out past the movement limit before
  35.2 N, and the second pulls reach 43-45 N measured. So the pass/fail of the latch check
  depends on the assumed hook stiffness, which is one of the unknowns in the latch-fit work.

### Is it a simulator artifact or real dynamics?

As modelled, the overshoot is a simulator artifact of the undamped, stiff hook; the
controllers are not the cause. Real dynamics could still ring. A real plastic latch has
some damping and an unknown stiffness, and the gantry is compliant (10 N/mm servo). The
latch-fit agent's report (results/v0.2f_latch_fit/REPORT.txt in its worktree) makes the
same point: the simulator's undamped hook "rings on a compliant servo; a real one may not".
Only a rig pull logged with a fast F/T can settle it.

### Could it unlatch a good part, or tear a weak latch, where a real part would not?

- In the model, no pull came near the break: 41.9 N maximum against 58 N, and only the
  ringing takes the hook above its quasi-static 16-23 N. A real Micro-Fit at its 58 N
  datasheet minimum would have the same margin.
- latch_spread varies latch position, latch ramp peak and terminal forces, but not
  retention: every latch that is not broken holds 58 N, so a weak-retention latch is not
  modelled. A latch that held less than about 42 N could be torn by the ringing in
  simulation, where a damped hook (about 25 N peak) would survive. That would be a failure
  in simulation only. No such part exists in the current suites.
- Separate from the pull, H's retry retract broke the latch of two good gantry parts
  (`mf_noise_1mm`, seed 2027, trials 17 and 19; hook 58.5 and 59.1 N). It loaded a third to
  54.1 N (seed 2026 trial 7). In all three, INSERT ended on `excess_torque` with the plug
  already latched, and the "re-descend" retract pulled on it. Trials 17 and 7 ended in a
  48 N protective stop. In trial 17 the hook was already past 58 N when it fired, because
  the 40 Hz filter and the retract speed keep the measured force behind the hook force.
  Trial 19 later failed its pulls as `retention_failed`, a good part rejected.
- C does not do this. It caps any retract pull on a latching part at 36 N
  (`retract_pull_cap_fraction`, the "gentle retract"). This is an equal-effort item, not
  overshoot.

### Proposals (text only; nothing changed)

- Give the hook model damping (for example a fraction of critical damping against the
  fixture's moving mass), or state that pull-force peaks on the gantry with high terminal
  friction are partly a ringing artifact. Choose this together with the latch-fit work,
  where the hook's stiffness and damping are the unknowns.
- Add weak-retention latches (for example 0.5 x and 0.75 x of 58 N) to latch_spread, so the
  margin between the pull and the break is tested.
- Count the hook force against retention in the trial result. Today
  `excessive_contact_force` only sees housing contacts.

## Open fairness items

- D, F, H and I have no gentle-retract cap on their retry retract (`spiral_search.py` has none; J has C's only inside its VERIFY);
  C has one. The cap is cheap to give the baselines. Until they have it, H's retry can tear
  a latch where C's would not (2 good gantry parts here, development seeds).
- The timing comparison is not a fairness issue for the benchmark: F and I are cheaper per
  tick than C and G because they do less (no localizer).

## How the runs were made

- All runs were single-process. At the start, three of my processes overlapped: two
  Part 2 chains and the first timing run. After the lead's note I ran one process at a
  time, in queued sequence. Two low-load timing runs were taken by pausing (SIGSTOP) the
  running Part 2 process and resuming it afterwards.
- Commands: `pull/run.sh <machine>` (Part 2, model runs); `timing/run.sh <label>` (the
  loaded timing runs). The low-load runs used the same timing command with `--trials 1`
  and `--seeds 2026` or `--seeds 2027`. The counterfactual runs used
  `--conditions mf_terminal_max,mf_spread` with `--hook-damping 300` or
  `--hook-stiffness 5e4`. Each run's exact arguments are in its `config.json`.
- Committed: the two scripts and the test file. For timing, `summary.csv`,
  `subtimers.csv`, `worst_ticks.json` and `config.json` per run. For Part 2, per folder:
  `trials.csv`, `summary.json`, `summary.csv`, `config.json`, `episodes.csv` and the three
  `trace_*.csv`. Not committed: `events.json.gz` (no table needs it; the event lines quoted
  for the H trials can be regenerated by rerunning those trials) and the raw per-tick `.npz`
  files.

## Uncertain or not done

- Nothing was measured on the rig PC, or on an idle machine (the lowest load average was
  about 7).
- The replay minimum is not a clean idle number. Under heavy load the replays also ran on
  efficiency cores, and in some ticks a replay was slower than the in-loop call.
- GC pause sizes depend on the measuring process's heap. It is larger than the
  controller's alone, because it keeps the observation stream for the replay.
- The ringing explanation rests on one counterfactual (one seed, two conditions) and six
  traces. The match between the 105-120 Hz ringing and the gantry's moving mass is
  approximate.
- I did not reproduce the "about -50 N" development case. No pull of C, G, H, I or J here
  measured more than 42.4 N. The latch-fit agent's pull is its own logging move stopping at
  29 N, not the controllers' VERIFY. I could not see that case's setup.
