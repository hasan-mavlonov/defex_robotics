# Tuning of the conventional baselines D, E and F

All tuning used development seed 2026. Benchmark seed 20261031 was not run
before the controllers were frozen. Every number here is a development
measurement; the per-setting results are the CSV files in [`tuning/`](tuning).
Script: [`experiments/tune_baselines.py`](../../experiments/tune_baselines.py).

## Effort compared with C

C was tuned by hand on seed 2026 over the same 18 condition families (V0.1
README, "Experiment protocol"). D, E and F got a systematic search over the
same families and seed:

| Controller | Settings evaluated | Development trials |
|---|---|---|
| E: vision + RCC | 18 (coarse) + 5 (confirm) | 1,080 + 1,800 |
| D: spiral search | 324 (coarse) + 90 (fine) + 16 (edge) + 5 (confirm) | 19,440 + 5,400 + 5,760 + 1,800 |
| F: spiral + RCC | 324 (coarse) + 90 (fine) + 16 (edge) + 5 (confirm) | 19,440 + 5,400 + 5,760 + 1,800 |

That is about 68,000 development trials for the three baselines.

## Procedure

1. **Coarse.** Full grid on the six hardest development conditions
   (`lateral_3mm`, `yaw_5deg`, `tilt_5deg`, `noise_1mm`, `noise_2mm`,
   `friction_1`), 10 trials each.
2. **Fine** (D, F). The top 5 coarse settings crossed with insertion force,
   number of attempts and seat margin, same conditions.
3. **Edge** (D, F). The coarse winners sat on the grid edges (lowest force,
   pitch, speed and push distance), so the grid was extended past them, down to
   Flexiv's minimum contact force of 2 N, on all 18 development conditions x 20
   trials. For F nothing beyond the edges did better. For D one edge setting
   tied the selected one (search 2 N, 2.5 mm/s: 349/360, median 3.532 s
   against 3.540 s, 4 false accepts against 7) and by the ranking rule below
   should have been selected; it was not carried to the confirm stage. This
   deviation was found in review after benchmark_v0.2a and is disclosed rather
   than corrected: success on the development set is identical, the cycle-time
   difference is 0.008 s, and changing D now would mean a new pre-registered run.
4. **Confirm.** The top 5 settings on all 18 development conditions (the two
   generalization conditions stay held out), 20 trials each.

Ranking rule, fixed before tuning: success rate, then median cycle time, then
95th-percentile cycle time.

## Search spaces

D and F (`SpiralSearchConfig`), with the vendor reference for each range:

| Parameter | Values | Reference |
|---|---|---|
| search force | 2, 3, 5, 8 N | Flexiv SearchHole contactForce: default 5 N, range 2-20 N |
| spiral pitch (radius increment per turn) | 0.5, 1.0, 1.5, 2.0, 2.5 mm | Robotiq FT 300 Insertion node input; no published default. Upper bound: twice the 1.3 mm lead-in capture |
| tangential speed | 2.5, 5, 10, 20 mm/s | no vendor default found for spiral speed |
| lateral stiffness during the spiral | stiff, 2, 0.5 N/mm | Flexiv SearchHole searchStiffRatio (0.1-1) |
| hole-found push distance | 0.3, 0.5, 1.0, 2.0 mm | Flexiv SearchHole pushDistance > 5 mm, scaled to this 15 mm socket |
| insertion force | 3, 5, 8 N | Flexiv InsertComp maxContactForce: default 5 N |
| attempts | 1, 2, 3 | |
| seat margin | 0.5, 1.0 mm | |

E (`PassiveComplianceConfig`): insertion speed 2, 4, 8 mm/s; overtravel 0.25,
0.5, 1.0 mm; approach height 2, 5 mm. The RCC stage itself is not tuned: its
stiffness comes from datasheets (`CompliantStageConfig`).

Sources: Flexiv Adaptive Assembly primitives,
https://www.flexiv.com/software/primitives/en/3.9/rizon4/Adaptive%20Assembly.html;
Robotiq FT 300 Insertion node, https://dof.robotiq.com/discussion/1278; ATI 9115
compensator datasheet, https://www.ati-ia.com/products/compliance/compensator_9115DataSheet.aspx;
PFA compliance devices, https://www.pfa-inc.com/?p=7093. Doosan's Insert manual
page (404) and TM Robot's Smart Insert page (expired certificate) could not be
read.

## Selected settings

| Controller | Selected | Confirm stage, 18 conditions x 20 trials |
|---|---|---|
| D | search 3 N, pitch 1.0 mm, 5 mm/s, stiff, push 0.5 mm, insert 8 N, 2 attempts, margin 1.0 mm | 349 / 360 (96.9%), 0 stops, 7 false accepts, cycle p50 3.54 s |
| E | insert 4 mm/s, overtravel 1.0 mm, approach 2 mm | 335 / 360 (93.1%), 22 stops, cycle p50 6.32 s |
| F | search 3 N, pitch 1.0 mm, 5 mm/s, stiff, push 0.5 mm, insert 3 N, 3 attempts, margin 1.0 mm | 349 / 360 (96.9%), 0 stops, 8 false accepts, cycle p50 3.54 s |

For reference, on exactly the same 360 development trials: C 360 / 360, B
(V0.1 settings, untuned here) 327 / 360. C was developed on these trials, so
this comparison favours C; the reported benchmark uses a fresh seed.

Re-running the frozen defaults through the normal runner reproduced the confirm
numbers exactly (`results/dev_frozen_check`, not committed).

## Observations from tuning

- D and F plateau at about 97% on the development set. Many settings tie: the
  spiral finds the hole in nearly every trial where the plug lands on the face.
  The remaining failures are cases a spiral cannot fix (yaw beyond the cavity's
  4.9 degree limit, tilt), plus false accepts where the plug reached full depth
  with yaw or tilt over the 3 degree tolerance, or where the vision depth window
  (3 sigma of the camera's height error) accepted a shallow jam.
- D and F have a shorter median cycle than C (3.5 s against about 5.4 s): they
  do no verification probing.
- A slower, softer search wins: 3 N and 5 mm/s beat the vendor's 5 N default.
- Flexiv also ships CheckPiH, a lateral-probe "peg in hole" check (searchForce
  3 N, searchRange 10 mm). Wall-probe verification as such is therefore not
  unique to C; D and F here do not use it.
