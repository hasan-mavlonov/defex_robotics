# Checkpoint 2 preparation: merge, arm prior, review fixes (development)

Development measurements in simulation, made before the Checkpoint 2 code was
frozen. Seeds used: 2026 (dev), 3001-3030 (training), 4001 (validation), 3031
(one out-of-sample check, now spent). No reserved seed was run. The tables are
generated from committed files: `tables.md` (`experiments/cp2_tables.py`) and
`review_fixes/tables.md` (`experiments/cp2_review_tables.py`). Every command is
in `commands.sh` and `review_fixes/commands.sh`.

The reported Checkpoint 2 run is `results/benchmark_v0.2b/`.

## What happened here

1. **Merge.** `v0.2/checkpoint2` = `v0.2/w3-latch-physics` + `v0.2/w5b-arm-recovery`
   (C on the UR5e) + `v0.2/w9-learned-prior` (controller G). No textual
   conflicts. Gantry equivalence against the untouched w3 branch: 0 differences
   (`equivalence/comparison.txt`); W9's gantry G-vs-C runs reproduce bit for bit
   (`gantry_g_recheck/comparison_vs_w9_dev2026.txt`).
2. **Arm contact prior.** Same pipeline and seed splits as the gantry model
   (`arm_prior/`). Families chosen by W9's rule (where C makes surface-block
   contacts in a seed-3001 probe): noise_0.5mm, noise_1mm, noise_2mm,
   mf_noise_1mm, plus friction_1, which blocks on the arm but not on the gantry.
   5,900 trials of data (5,990 with the probe). Selection rule committed before
   the validation runs (`arm_prior/SELECTION_RULE.txt`). Chosen: contact inputs,
   weight 1, installed as `assets/models/contact_prior_arm.json`.
3. **Two independent reviews**, then fixes (`review_fixes/`).

## Arm prior selection (validation seed 4001, 300 paired trials per variant)

| Variant | Successes | C-only / G-only (p) | Bad units | Stops | Mean retries |
|---|---|---|---|---|---|
| C | 242 | - | 0 | 7 | 1.54 |
| contact w 0.25 | 250 | 4 / 12 (0.077) | 0 | 11 | 1.29 |
| contact w 0.5 | 259 | 4 / 21 (0.0009) | 0 | 10 | 1.18 |
| **contact w 1 (chosen)** | **261** | **5 / 24 (0.0006)** | **0** | **7** | **1.16** |
| all w 0.25 | 249 | 8 / 15 (0.21) | 0 | 11 | 1.29 |
| all w 0.5 | 257 | 4 / 19 (0.003) | 0 | 12 | 1.16 |
| all w 1 | 256 | 6 / 20 (0.009) | 0 | 10 | 1.20 |

The top three are within noise. The gantry chose `all` inputs and the arm chose
`contact`.

## Arm G against C on dev seed 2026 (60 trials per condition)

| Condition | C / G | C-only / G-only (p) | Stops C / G |
|---|---|---|---|
| noise_0.5mm | 60 / 60 | 0 / 0 | 0 / 0 |
| noise_1mm | 52 / 54 | 0 / 2 | 0 / 1 |
| noise_2mm | 32 / 41 | 1 / 10 (0.012) | 5 / 5 |
| friction_1 | 54 / 55 | 0 / 1 | 3 / 3 |
| mf_nominal, mf_moderate | 120 / 120 | 0 / 0 | 0 / 0 |
| mf_noise_1mm | 39 / 45 | 0 / 6 (0.031) | 4 / 4 |
| 4 bad-part conditions | bad units passed 0 / 0 | - | wrong_polarization 0 / 3 |
| **All, 660 pairs** | **357 / 375** | **1 / 19 (4e-5)** | **12 / 16** |

Seed 2026 was used to develop C's arm rules but no choice about G was made on
it.

## Review findings and what was done

| Finding | Severity | Outcome |
|---|---|---|
| W5b rules switched on inside the gantry's sim-randomization bands (any wrist above 15 N m/rad), so "exact no-op on the gantry" held only for the nominal fixture. Measured: C changed on 4 of 5 randomized variants, 240 to 236 successes, +0.37 s per cycle. | high | Fixed: rules only for wrists at least 4x stiffer or servos at least 2x slower than the gantry's. 0 differences on the rule-3 set and on a 600-trial randomized slice afterwards. |
| A model with an unset fixture value could never match, or could raise, so G would silently run as C. | medium | Fixed: a model must state every fixture field; incomplete models are refused when written and loaded. |
| The arm comparison is not like for like: C and G had two arm-specific passes, D, E, F none, and the snapshot is on the seed C's arm rules were set on. | medium | Labelled, and A-G re-run on unused seed 3031 (below). No arm tuning pass for D and F. |
| Offline model quality was quoted on the selection split. | medium | Tables now lead with dev 2026: arm contact model 1.69 mm against 1.83 mm for C's analytic posterior over all contacts, 2-sigma coverage 0.855 (expected 0.865). |
| Servo lag was taken from the slowest axis. | low | Fixed: separate translational and rotational lag. |
| Hardware backend did not require the W5b fixture values. | low | Fixed: it refuses unset values. |
| The installed gantry model stored fewer fixture values than the arm model. | low | Both completed; weights unchanged; 380 snapshot trials reproduce with 0 differences. |
| G's combined posterior calibration was never reported. | low | Reported, not changed: on first contacts G's posterior is closer to the truth (gantry 1.42 to 1.20 mm, arm 1.38 to 1.11 mm) but more overconfident than C's. |
| The explanation for G's extra wrong-polarization stops held on the gantry only. | low | Corrected: force trips above 48 N on the gantry; 0.6 N m torque trips at 7-20 N on the arm, each after a +/-3 deg yaw correction. |

Not done: an arm tuning pass for D and F; redesigning G to use the learned
output as a likelihood instead of a posterior; a guard against G's extra
wrong-polarization stops. All three are listed as open.

## Out-of-sample check, seed 3031 (20 trials per cell)

| Run | A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|---|
| Arm, 5 conditions: success / escapes / stops | 25 / 1 / 74 | 66 / 1 / 33 | 86 / 0 / 3 | 81 / 6 / 0 | 73 / 2 / 25 | 87 / 6 / 0 | 90 / 0 / 3 |
| Gantry, 5 conditions | 26 / 1 / 73 | 69 / 2 / 29 | 100 / 0 / 0 | 85 / 4 / 0 | 74 / 1 / 25 | 88 / 10 / 0 | 99 / 0 / 0 |

On the arm, F seated as many units as C (87 against 86 of 100) and passed 6
failed units as good where C passed none. C's arm advantage on this seed is
bad units passed, not seating rate. C is slower: median cycle 8.44 s against
6.51 s for F on the arm, 5.37 s against 3.54 s on the gantry.

## Open before hardware

- Servo lag and tilt stiffness come from Menagerie's UR5e model; on a real arm
  both must be identified and a new arm prior collected.
- G was trained only on C's contacts (policy shift not addressed) and is
  unvalidated outside its training families (it lost one gantry
  generalization_tight trial in the snapshot).
- C rejects a bad part only after it runs out of retries or time (snapshot,
  dev seed 2026: median 24.6 s per bad part on the gantry, 26.3 s on the arm,
  against 5-8 s for a good cycle). It has no explicit "this part is defective"
  verdict, so each bad part costs several normal cycles.
