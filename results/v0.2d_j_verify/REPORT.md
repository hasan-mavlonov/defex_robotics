# v0.2d: controller J, F's insertion then C's VERIFY

Development work, not a pre-registered benchmark. The question: does C's VERIFY on
top of the fast spiral cell F give F's throughput with C's zero escapes? Short
answer, from dev seeds 2026 and 2027 (both machines, all four suites, 20 trials per
condition): C's escapes, close to C's throughput, not F's. J passed 1 bad unit in
2,720 good-part trials (C 0, I 80, F 146) and 0 of 560 deliberately bad parts. It
made 420 good units per hour against C's 400, I's 560 and F's 645. VERIFY adds about
2.4 s per cycle on the gantry and 3.2 s on the arm, most of the gap between C and F.
J seats fewer good parts than C (93.2% against 96.1%, p = 0.00043) and more than I
(90.3%, p < 1e-6). Every number is in [`TABLES.md`](TABLES.md)
(`python -m experiments.v02d_j_tables results/v0.2d_j_verify --pick spiral_rcc_verify_research`).
Commands: [`run.sh`](run.sh).

These runs use the benchmark_v0.2c code base (insert target 30 N); the force-budget
change (35.2 N, `v0.2d/force-budget`) is not in them.

## What J is

`defex/control/spiral_verify.py`, registered as `spiral_rcc_verify`, letter J. J is
a subclass of F with F's per-machine settings and code; it overrides `__init__`,
`reset`, `step` and `_succeed`. From the tick at which F would declare seated, J runs
C's own class with C's settings, with only `_plan_correction` (called after the
retract that follows a failed check) replaced by J's policy. The only change to
`adaptive_fsm.py` is the structural `_begin_attempt` (ca19980). C and G before and
after: 1,080 trials, 0 differences except wall time, identical event logs
(`equivalence/COMPARE.txt`).

## J before the hand-over is F

On all 11,913 trials where F declared seated (dev2026, dev2027, val4003), J's events
equal F's up to F's "seated", and J logs `verify_handover` at F's exact finish time.
On all 1,207 trials where F never declared seated, J's row and events equal F's.
Tick-by-tick tests on the gantry (floor contact, face contact then spiral, latching
part) and the arm compare observed pose, force, torque and command up to the
hand-over.

## What VERIFY reads, and where J gets it

- Socket and grasp estimates, cycle start: F's.
- Wrench tare: F's free-space tare.
- Setpoint `xy`/`z`: F's commanded tip (spiral point + search spring offset + F's
  lateral compliance; F's depth setpoint).
- C's admittance offsets and `yaw_adj`: zero. `R_corr`: identity (F aims along the
  vision estimate).
- Mouth plane: F's face-contact depth (`face_depth`, no tilt correction) as C's touch
  calibration; uncalibrated with the vision sigma when F went straight in.
- Latching insertion trace: F's DESCEND and INSERT samples (the click is logged only).
- Bottom diagnosis: none at first, so `no_retention` cannot fire on the first
  slide-out.
- Per-attempt state: reset at each hand-over. Per-cycle evidence: kept across a
  re-search.
- Fixture rates and gates: the same `ControllerContext`, whose fixture dynamics leave
  out the RCC stage.
- Probe allowance: C's plus 2 N / 5.78 N/mm = 0.346 mm (RCC term). Plug lateral
  position: encoders + F/k (RCC term).
- Not given to J: C's localizer, yaw estimates or yaw search, blocked probes, or C's
  DETECT depth gate.

## The RCC terms

On F's RCC stage the plug trails the tool by F/k. Smoke trials on seed 2026 (indices
0-2 of five conditions) showed C's wall probe ending at 1.35 mm with 1.4-1.6 N of
reaction. The two terms come from the F/T reading and the datasheet stiffness
(`CompliantStageConfig`, 5.78 N/mm), have no free parameter, and were added before
the selection rule was committed. Ablation (dev, pooled): J(a) seats 2485/2720 with
1 bad unit and 421 units/h; without the terms 1784/2720 (65.6%), 22 bad units (15 on
yaw, arm), 298 units/h. Median half free travel on wall-yaw passes: 0.805 mm without
the terms, 0.471 mm with them, C 0.454 mm; the aligned true value is 0.5 mm.

## Choosing the response to a failed check

[`SELECTION_RULE.md`](SELECTION_RULE.md), committed at 9e7d012 before the runs.
(a) rejects; (b) hands back to F's jam retry within F's 2 attempts. Rule: fewer bad
units passed, then more seated, then lower median good cycle. On seed 2026, (a) 0 bad
units and 1242/1360 seated (7.494 s), (b) 0 and 1269/1360 (7.568 s): pick (b). On
validation seed 4003 (run once, at 7fc078e), (a) 2 and 1241, (b) 2 and 1273: pick
confirmed. `spiral_rcc_verify` equals (b) on all 1,640 dev2027 trials.

(b)'s gain is on latch_spread (38 gantry, 13 arm, mostly `mf_terminal_max`). The pull
fails after F stalls at 30 N; on the second hand-over, C's latch check proof-pushes
at 35.2 N, and C's INSERT and DETECT carry the plug to the floor. In this path J runs
more than the VERIFY state.

## Results (dev seeds 2026 and 2027 pooled)

J = (b). Good-part conditions; 60 s per protective stop. Each cell: good parts
seated, bad units passed on good-part trials, median good cycle (s), good units per
hour. Latching suites also give deliberately bad parts passed.

| Machine, suite | C | F | I | J |
|---|---|---|---|---|
| gantry standard (800) | 797, 0, 5.30, 624 | 768, 18, 2.43, 1126 | 768, 18, 2.43, 1126 | 777, 1, 4.77, 650 |
| gantry latching (good 120; bad parts passed of 160) | 115, bad 0, 5.95, 436 | 118, bad 99, 2.43, 872 | 118, bad 0, 5.33, 515 | 118, bad 0, 5.33, 515 |
| gantry heldout (200) | 169, 0, 6.15, 322 | 162, 21, 3.25, 470 | 162, 21, 3.25, 470 | 175, 0, 5.85, 374 |
| gantry latch_spread (240; bad of 120) | 240, bad 0, 5.95, 530 | 189 (47 bad units), bad 98, 2.41, 1053 | 189, bad 0, 5.30, 535 | 227, bad 0, 5.33, 579 |
| arm standard (800) | 780, 0, 8.16, 378 | 764, 22, 4.77, 579 | 764, 22, 4.77, 579 | 771, 0, 8.00, 375 |
| arm latching | 111, bad 0, 8.67, 252 | 114, bad 89, 4.55, 487 | 114, bad 0, 8.23, 326 | 114, bad 0, 8.30, 324 |
| arm heldout | 162, 0, 9.58, 193 | 154, 19, 6.55, 279 | 154, 19, 6.55, 279 | 154, 0, 9.67, 205 |
| arm latch_spread | 240, bad 0, 8.70, 355 | 187 (19 bad units), bad 93, 4.51, 523 | 187, bad 0, 8.17, 335 | 200, bad 0, 8.28, 340 |
| totals: seated / bad units / bad parts / units/h | 96.1%, 0, 0/560, 400 | 90.3%, 146, 379/560, 645 | 90.3%, 80, 0/560, 560 | 93.2%, 1, 0/560, 420 |

- False rejects: 0 for every controller. Protective stops: C 12, F 2, I 2, J 2.
- Paired J vs C: seated J-only / C-only 80 / 132 (p = 0.00043); bad units 1 / 0
  (p = 1). J is significantly below C on gantry standard (p = 0.00022) and on
  latch_spread on both machines.
- Paired J vs I: seated 164 / 60 (p < 1e-6); bad units 1 / 88 (p < 1e-6).

VERIFY's cost (median good cycle, F -> J -> C): gantry standard 2.43 -> 4.77 -> 5.30 s;
gantry heldout 3.25 -> 5.85 -> 6.15; arm standard 4.77 -> 8.00 -> 8.16; arm heldout
6.55 -> 9.67 -> 9.58. On latching parts J costs the same as I.

## J's bad units

Dev: gantry `noise_2mm` trial 11, seed 2027. F declared seated through its
vision-widened window at a reading of 11.0 mm; the plug was 10.6 mm deep and tilted
6.6 degrees. Seat conform left it at 14.49 mm and 4.7 degrees; the walls and the yaw
sweep passed; there is no tilt check and no depth gate. Validation: gantry
`friction_1` trial 18 and `heldout_worst_case` trial 7, at full depth, failing only
"settled" (2.03 and 2.21 mm/s against 2.0) from C's preload hold through the RCC
stage.

## What a skeptic would attack

1. The RCC terms are information F does not use.
2. (b)'s latch_spread gain comes from C's proof push and its INSERT/DETECT
   continuation.
3. No depth gate.
4. VERIFY was not re-tuned for the RCC stage.
5. The re-search is F's retry at the same position, so it cannot fix yaw.
6. J contains Defex's VERIFY, so it is not in `FAIR`.
7. Small development samples; seed 2026 was used for smoke trials and ranking; the
   Wilson upper bounds on J's bad units are 0.42% (gantry dev) and 1.07% (gantry
   4003).
8. Simulation only, with the v0.2c limits (assumed latch model, one latching family,
   30 N target below the datasheet's 32 N maximum in these runs).

## Commits

ca19980 refactor; 9e7d012 J, candidates, ablation, rule (dev2026 run); 7fc078e pick
registered (val4003, dev2027 runs); 87c5f7e results and tables. All `config.json`
files show `git_dirty: false`. Seeds 20261102, 20261116, 20261123 and 4002 were
never run.
