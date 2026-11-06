v0.2f rig predictions: report

These are the simulation's predictions for the conditions of hardware/TEST_PROTOCOL.md,
frozen before any rig exists.
- Seed 20261201; code ddd0d34 (benchmark_v0.2e's frozen code), run from dc938d1, which
  adds only this folder's pre-registration and tables.py.
- 6,600 trials: controllers A, C, F, H, I and J, on the gantry and UR5e arm models.
- Every number below is from TABLES.md in this folder, made from trials.csv with the
  pre-registered command.
- Rates are k/n with Wilson 95% intervals. Simulation only.

RESULT

Housing-only part:
- C seats more than F, I and J on both machines (gantry 194/200 = 97.0% against
  175/200 = 87.5% for F and I).
- C passes no bad unit in 200. F and I pass 13/200 (gantry) and 18/200 (arm).
- 27 of F and I's 31 bad units are at full depth, and all 27 are 3.00-4.65 deg off in
  tilt or yaw.

Micro-Fit:
- Good parts: F, I and J seat as many as C or more. No difference reaches p < 0.05.
- Deliberately bad parts: C, H, I and J pass none (0/200 each). F passes 130/200
  (gantry) and 116/200 (arm).

Cycle time: C's median is 2.3 times F's on the gantry and 1.8 times on the arm.

Everything matches PREREGISTRATION.md's expectations from benchmark_v0.2e, except one:
on the housing-only part, the differences already reach p < 0.005 at 50 trials per
condition.

RUN
- RUN_LOG.md: 1 h 02 min at --workers 2, against the about 45 min it was sized for. The
  shared machine was loaded by other agents.
- All four config.json files: git_dirty false, commit dc938d1.
- Frozen-code check: git diff --stat ddd0d34 HEAD, excluding results/, README.md and
  docs/, was empty at 4df8cae and at dc938d1.

PREDICTIONS, POOLED (success | bad units passed | protective stops | cycle p50/p95 s)

Housing-only part (nominal, lateral_3mm, noise_1mm, noise_2mm; 200 per controller):
  gantry A  61/200 (24.5-37.2%) | 2/200 (0.3-3.6%)   | 137/200 | 4.32/4.32
  gantry C 194/200 (93.6-98.6%) | 0/200 (0.0-1.9%)   | 0/200   | 5.51/12.26
  gantry F 175/200 (82.2-91.4%) | 13/200 (3.8-10.8%) | 0/200   | 2.44/10.46
  gantry H 172/200 (80.5-90.1%) | 12/200 (3.5-10.2%) | 0/200   | 2.96/7.82
  gantry I 175/200 (82.2-91.4%) | 13/200 (3.8-10.8%) | 0/200   | 2.44/10.46
  gantry J 182/200 (86.2-94.2%) | 0/200 (0.0-1.9%)   | 0/200   | 4.85/16.61
  arm    A  56/200 (22.2-34.6%) | 0/200              | 144/200 | 4.32/4.32
  arm    C 190/200 (91.0-97.3%) | 0/200 (0.0-1.9%)   | 2/200   | 8.51/20.20
  arm    F 168/200 (78.3-88.4%) | 18/200 (5.8-13.8%) | 0/200   | 4.82/13.22
  arm    H 162/200 (75.0-85.8%) | 11/200 (3.1-9.6%)  | 4/200   | 4.82/10.50
  arm    I 168/200 (78.3-88.4%) | 18/200 (5.8-13.8%) | 0/200   | 4.82/13.22
  arm    J 177/200 (83.3-92.2%) | 0/200 (0.0-1.9%)   | 0/200   | 8.33/17.77
  F and I give identical rows on this part: I's pull test runs only after a latching
  insertion (defex/control/spiral_search.py, controller I).

Micro-Fit good parts (mf_nominal, mf_moderate, mf_noise_1mm; 150 per controller):
  gantry A  50/150 (26.3-41.2%) | 0/150 | 100/150 | 3.82/3.82
  gantry C 143/150 (90.7-97.7%) | 0/150 | 0/150   | 6.18/11.65
  gantry F 148/150 (95.3-99.6%) | 0/150 | 0/150   | 2.41/13.39
  gantry H 130/150 (80.3-91.2%) | 0/150 | 3/150   | 6.16/10.75
  gantry I 148/150 (95.3-99.6%) | 0/150 | 0/150   | 5.47/16.38
  gantry J 148/150 (95.3-99.6%) | 0/150 | 0/150   | 5.47/16.38
  arm    A  50/150 (26.3-41.2%) | 0/150 | 100/150 | 3.79/3.79
  arm    C 137/150 (85.7-94.9%) | 0/150 | 3/150   | 9.02/18.95
  arm    F 141/150 (89.0-96.8%) | 1/150 | 0/150   | 4.69/15.67
  arm    H 118/150 (71.4-84.5%) | 0/150 | 6/150   | 8.50/12.18
  arm    I 140/150 (88.2-96.3%) | 1/150 | 1/150   | 8.63/17.98
  arm    J 141/150 (89.0-96.8%) | 0/150 | 0/150   | 8.63/17.84

Micro-Fit bad parts (4 defects; 200 per controller; bad parts passed | stops | time to
reject p50/p95 s):
  gantry A 2/200 (0.3-3.6%)      | 198 | 2.67/2.69
  gantry C 0/200 (0.0-1.9%)      | 10  | 8.56/11.64
  gantry F 130/200 (58.2-71.3%)  | 15  | 19.13/22.38
  gantry H 0/200                 | 11  | 9.32/12.87
  gantry I 0/200                 | 15  | 8.92/21.30
  gantry J 0/200                 | 25  | 7.86/21.30
  arm    A 2/200                 | 198 | 2.63/2.64
  arm    C 0/200                 | 0   | 13.00/16.32
  arm    F 116/200 (51.1-64.6%)  | 0   | 8.90/26.38
  arm    H 0/200                 | 0   | 10.24/12.50
  arm    I 0/200                 | 0   | 11.55/26.37
  arm    J 0/200                 | 0   | 12.11/26.37

Per-condition rows are in TABLES.md ("Per condition"). They are what a rig compares with
condition by condition.

PREDICTED DIFFERENCES (paired; C-only / other-only, exact McNemar p, C - other in points
with Newcombe 95% CI)

Housing-only part:
  gantry vs I (= F): success 21/2, p = 6.6e-5, +9.5 (+5.1 to +14.6);
    bad units 0/13, p = 0.00024
  gantry vs J: success 14/2, p = 0.0042, +6.0 (+2.2 to +10.5); bad units 0/0
  arm vs I (= F): success 25/3, p = 2.7e-5, +11.0 (+6.2 to +16.4);
    bad units 0/18, p = 7.6e-6
  arm vs J: success 16/3, p = 0.0044, +6.5 (+2.4 to +11.2); bad units 0/0

Micro-Fit good parts:
  gantry vs I, J, F: success 0/5, p = 0.062, -3.3 (-7.6 to -0.4)
  arm vs I: 6/9, p = 0.61; vs J: 6/10, p = 0.45; vs F: 5/9, p = 0.42

Micro-Fit bad parts:
  vs F: gantry 0/130, p = 1.5e-39; arm 0/116, p = 2.4e-35

On gantry Micro-Fit good parts, the Newcombe interval excludes 0 while McNemar p =
0.062. The pre-registered test between controllers is McNemar. The interval is the one
the sim-against-rig rule uses.

WHERE THE BAD UNITS ARE
- This run: 27 of F/I's 31 housing-only bad units are at full depth, all over 3 deg in
  tilt or yaw (3.00-4.65 deg). The one Micro-Fit bad unit (arm F/I) is at full depth with
  3.22 deg tilt.
- Over the three benchmark seeds (hardware/RIG_POWER.md): 392 of I's 433 housing-only
  bad units are at full depth and over 3 deg (median 3.45, max 5.02).
- This is why the protocol now measures final plug pose.

AGAINST THE PRE-REGISTERED EXPECTATIONS
- Housing-only, C ahead of F and I, 0 bad units for C, about 7% for F and I: yes. C 97.0
  / 95.0% against 87.5 / 84.0%; F/I 6.5 / 9.0%.
- Micro-Fit good parts, F, I and J as many as C or more: yes. Gantry 98.7% against
  95.3%; arm 93.3-94.0% against 91.3%.
- Micro-Fit bad parts, C/H/I/J 0, F most: yes.
- C's median cycle about twice F's on the housing-only part: 5.51 against 2.44 s
  (gantry), 8.51 against 4.82 s (arm).
- "Most differences will not reach p < 0.05": true on the Micro-Fit only.
  - On the housing-only part, all four C-against-I/J success comparisons and both
    C-against-I bad-unit comparisons reach p < 0.005.
  - The protocol's conditions include noise_2mm, so they are harder than the full
    standard suite.
- benchmark_v0.2e on the same conditions (CONTEXT_v0.2e.md, seed 20261130, unpaired)
  gives similar rates: gantry housing-only C 95.5%, F 85.0%, F's bad units 7.2%.

HOW A RIG RESULT WILL BE JUDGED
The rule is fixed in PREREGISTRATION.md, "Comparison with a rig result", and is run with
tables.py --rig.
- Pairing: by trial.
- Rates: rig minus sim, with a Newcombe interval. "agrees" if the interval is inside
  +/-5 points; "disagrees" if it excludes 0 and is not inside the band; else
  "inconclusive".
- Cycle times: the ratio rig / sim, with a bootstrap interval and a 0.8-1.25 band.
- Between controllers: the rig's paired difference against the simulated one.

With 50 paired trials and two zero counts, the interval is about +/-7 points, so
"agrees" cannot be reached for zeros. The protocol plans 100 per condition, which first
needs these predictions extended to trial indices 50-99 on the same commit (item 7).

WHAT THIS DOES NOT SHOW
- It does not test the simulator. It freezes what the simulator says.
- It is uncalibrated: asset friction 0.3, modelled contact stiffness.
- 50 trials per condition: 0/50 has an upper bound of 7.1%.
- The physical bad parts only approximate the simulated defects.
- gantry and arm are the simulator's gantry with its RCC and the UR5e model. No BOM.md
  arm is modelled.
- There is no rig counterpart to the damage measure.
- One cosmetic post-run edit to tables.py: the "|tilt|" labels became "abs(tilt)",
  because the pipes broke the markdown table. See RUN_LOG.md.
