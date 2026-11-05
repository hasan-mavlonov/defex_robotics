# C design round on the four diagnosed failures: draft pre-registration

**DRAFT, not frozen. Hasan decides whether to run this. Nothing has been run.**

No code for any change below exists. No development, validation or benchmark seed has
been spent for it. Every number here comes from committed results and is quoted with its
file. Power numbers come from `POWER.md` in this folder (made by `power_v02g.py`, which
reads committed trials.csv only). Seeds are proposals: each reads "seed to be assigned
when frozen".

## 0. What freezing this file would take

This draft becomes a pre-registration only when every placeholder below is filled, the
changes are built and kept by their rules, validation has passed, and the file is
committed before the first benchmark trial. The list is in section 13.

## 1. Question

`results/v0.2f_checkpoint/CHECKPOINT_REPORT.md` ("Open questions" 3) names four C
failures, each traced POST HOC to one mechanism:

1. VERIFY's 1 N force-target preload lifts a seated plug when the F/T zero drifts, and
   nothing re-checks the depth (arm, heldout2 F/T drift);
2. VERIFY's wall probe stops on a 2 N reaction that floor friction can reach before the
   plug meets a wall (arm friction 1.0, and the pyramidal cone);
3. RECOVER's jam branch retries from the same probe after a CoP relabel (heldout2
   plug offset in the fingers, and the old `heldout_mischar_2mm`);
4. the latching tilt check measures the plug against the axis C aimed it along, so it
   cannot see an error in C's socket-axis estimate.

The questions:

- Does each change remove the failure it targets, on seeds nobody has seen?
- Does the changed controller (here **C2**) lose anything elsewhere?
- After the changes, how does C2 compare with the best fair baseline in every cell, and
  with J2 (F's insertion plus C2's VERIFY)?

The pitch is Hasan's decision. This round does not pick it.

## 2. Seeds

| Use | Seed |
|---|---|
| Development | 2026 and 2027 only |
| Validation (once) | seed V, to be assigned when frozen |
| Benchmark | seed B, to be assigned when frozen |

Spent, do not use: 2026 and 2027 (development only), 3001-3040 (learned-prior training),
3031, 3032, 4001-4006, 4007, 20261025, 20261031, 20261102, 20261107, 20261108, 20261109,
20261116, 20261123, 20261124, 20261130, 20261201, 20261205, 20261207.

Unspent but reserved: 4008 and 20261210. This draft does not assign them. Hasan may pick
them or any other fresh number. Before use, check that no file under `results/` contains
the number (`grep -rl <seed> results`).

## 3. The four changes

Each change is built behind a default-off flag in `AdaptiveConfig` (and the verifier
config J uses), so C with every flag off gives the v0.2e rows. C2 is C with the kept flags
on, run under its own name through `DEFEX_CONTROLLER_VARIANTS` (as
`results/v0.2f_baseline_retract_cap/variants.json` did). G is not changed (section 6).

Every change uses only what C sees today: encoder, tared F/T, camera, drawing. Nothing
under `defex/control`, `defex/recovery` or `defex/perception` may import MuJoCo, the
backend or GroundTruth.

### 3.1 VERIFY depth hold and re-check

**Diagnosis** (`results/v0.2f_h2_diagnosis/REPORT.md`, mode 2).
- In all 6 traced arm bad units under `h2_ft_drift_0.3` the plug was at the floor
  (14.86-15.00 mm true) when C saw the bottoming force. VERIFY's preload then drove the
  read force to 1 N while the true force was about 0 N or a pull. The plug rose 0.6-1.8 mm
  during the wall probes (trial 12: 15.00 to 13.23 mm). The probes still passed, and no
  step compared the encoder depth with the bottoming depth before SUCCESS.
- All 8 reported bad units have axial drift +0.19 to +0.30 N/s in the push-out direction.
- A second route from the same drift: lateral drift makes the lateral admittance press
  the plug on a wall, the probes measure no free travel, and the wall-yaw check fails a
  seated plug until the time limit (11 trials on seed 20261207).
- Development seeds: 6 C bad units, all arm, all at 0.3 N/s, all push-out drift; the 8
  other arm C failures there all end with a wall-yaw FAIL. Gantry: 0 C failures in 160
  drift trials. C seated 11 and 15 of 20 (seeds 2026, 2027); D seated 40 of 40.

**Candidate change, in plain words.**
- (1a) Re-check: just before SUCCESS, compare the encoder depth with the depth at
  bottoming. If the plug rose more than d_rise (proposed 0.2 mm, under the score's 0.5 mm
  depth tolerance), push it back to the bottoming signature once and repeat the check; if
  it rises again, fail the part.
- (1b) Depth hold: during the wall probes and the centring, hold the encoder depth found
  at bottoming (a position hold with a force ceiling) instead of a 1 N force target, or
  cap upward travel at 0.1 mm.
- (1c) Drift estimate: C tares before every attempt, so two tares give a drift rate.
  Subtract the predicted drift during VERIFY. This is the only candidate aimed at the
  lateral wall-yaw route.
- Candidates for the RULE.md: 1a alone; 1a + 1b; 1a + 1b + 1c. Values are set from the
  geometry and the score, not searched.

**Development-seed protocol.**
- Target cells: `--suite heldout2 --conditions h2_ft_drift_0.1,h2_ft_drift_0.3`, both
  machines, seeds 2026 and 2027, 40 trials per condition (160 pairs per machine), C
  against each candidate, D and J as references.
- The no-harm check in section 4.

**Keep rule (committed in RULE.md before any candidate run).**
- Arm target cell, both seeds pooled: the candidate passes at most 1 bad unit, and its net
  gain in seated parts (candidate-only minus C-only) is at least half of the trials where
  C fails and D seats.
- Gantry target cell: no net loss.
- Plus every no-harm bound in section 4.

**Risk of tuning to the test.**
- The diagnosis replayed the reported heldout2 seed 20261207 (C trials 3, 4, 12, 19, 20,
  25, 28; D trial 12; F trial 29) and used development seeds 2026 and 2027.
- So `h2_ft_drift` is now a development family. A gain there at seed B shows the fix
  holds on fresh draws of a known family. It does not show that C copes with an unseen
  disturbance.
- The fix must be judged only on seeds V and B. Seed 20261207's heldout2 result stands as
  it was reported.
- The drift is linear and its rates are assumed (`results/heldout2_v0.2f/PREREGISTRATION.md`).
  A fix that fits linear drift may not fit a real sensor.

**Equal effort.**
- J runs C's VERIFY, so J2 gets this change with no extra work.
- D, E, F, H and I have no low-force phase after the seat. They declare on the encoder
  depth and stop, so a depth re-check gives them nothing.
- Open item: C re-tares before every attempt; the baselines tare once. F's one drift bad
  unit (trial 29) came from a false contact reading during descent. A re-tare before each
  baseline search attempt is cheap and should be offered to D-I if 1c is kept.
- A lower-drift sensor is an integrator setting for every controller, not a C change.

### 3.2 Wall-probe stop on a wall signature, not force alone

**Diagnosis** (`results/v0.2f_friction_diagnosis/REPORT.md`).
- At mu = 1 on the stiff arm, floor friction under the 1 N preload reaches the 2 N probe
  stop before the plug meets a wall. The plug moves 0.03-0.1 mm; the wall-yaw check reads
  too little free travel (about 0.03-0.07 mm half travel against 0.293 mm) and rejects a
  seated plug. Recovery re-aims by 0.3 deg and repeats the same probe until the 26 s limit.
- Nominal (elliptic) benchmarks, three seeds: 18 C friction_1 losses, of which 11 torque
  protective stops at 0.61-0.71 N m, 6 wall-probe stalls, 1 mouth stall. J seated 300 of 300.
- Pyramidal cone (randomized run, seed 20261205): C seated 1 of 90, F, H and I 89-90.
- Development seeds, arm, 20 trials per cell per seed: friction_1 C seated 39 of 40
  nominal, 0 of 40 pyramidal, 0 of 40 elliptic with 2 ms friction time; friction_0.6 C
  40, 29 and 33 of 40. F and J 40 of 40 in every friction cell except J pyramidal
  friction_0.6 at 39 (`dev_counts/summary.csv`).
- From the same report: C's median peak torque at friction_1 is 0.32-0.34 N m against
  0.06-0.07 for F, I and J. On dev seed 2026 C's peak torque fell in a VERIFY wall-probe
  stop in every friction_1 trial (0.34-0.55 N m).

**Candidate change, in plain words.**
- (2a) Count a probe stop as a wall only if the lateral reaction rises while the encoder
  position stops advancing, at a stiffness consistent with a wall. A stop at 2 N where
  the plug moved much less than the setpoint (minus the servo lead) is inconclusive: repeat
  that probe once at a lower preload (proposed 0.5 N). If it is still inconclusive, fail
  as today. So 2a can only turn a false reject into a pass when the second probe reaches
  the wall.
- (2b) After a failed VERIFY, change the probe (lower preload, slower) instead of only the
  aim.
- (2c) For the torque stops: approach walls and floor more slowly on the stiff wrist, or
  add a soft lateral admittance during the probe (a software RCC).
- Candidates for the RULE.md: 2a; 2a + 2b; 2a + 2b + 2c.

**Development-seed protocol.**
- Arm, `--suite standard --conditions friction_0.6,friction_1`, seeds 2026 and 2027,
  100 trials per condition on the nominal simulator (400 pairs). The dev seeds show only
  1 nominal friction_1 loss in 40, so 20 trials are too few.
- The same conditions at 40 trials per seed on the cone-only pyramidal simulator and the
  2 ms friction simulator, built by `experiments/friction_diagnosis_v02f.py counts`.
- Standard `yaw_5deg` and `yaw_10deg` on both machines, 40 trials per seed: the check
  must still fail truly yawed plugs.
- The no-harm check in section 4.

**Keep rule.**
- Pyramidal friction_1, both seeds: net gain of at least 40 of 80.
- Nominal friction_1 and friction_0.6: no net loss, and no rise in protective stops.
- No candidate-only bad unit in any yaw or friction cell.
- Plus every no-harm bound in section 4.
- 2c is kept only if it also lowers nominal friction_1 protective stops (net, both seeds).

**Risk of tuning to the test.**
- The diagnosis replayed benchmark seed 20261130 (friction_1 trials 8, 21, 51) and the
  randomized seed 20261205 (variants 4, 6, 8, 11, 12), and counted every friction_1
  failure in all three benchmark seeds (20261123, 20261124, 20261130).
- The fix must be judged only on seeds V and B. The friction_1 loss on the three benchmark
  seeds and on seed 20261205 must not be quoted as evidence that the fix works.
- The pyramidal cone undoes a deliberate contact setting (`solreffriction` 20 ms). MuJoCo's
  documentation calls the elliptic cone the closer model. A fix judged mainly on the
  pyramidal cone could be fitting a solver property, so the keep rule also needs the
  nominal cells to hold.

**Equal effort.**
- J runs C's VERIFY, so J2 gets 2a and 2b. 2c is a C-wrist change; J's probe already runs
  on F's RCC spring.
- F, H and I run no wall probe, so there is nothing to give them.

### 3.3 Jam-branch progress after repeated same-probe attempts

**Diagnosis** (`results/v0.2f_h2_diagnosis/REPORT.md`, mode 1).
- With an unseen in-hand slip and rotation of the same sign, the true tip sits 0.82 mm
  from C's estimate. C computes the CoP about the estimated tip, so a plug on one edge reads
  a CoP 3.75-4.16 mm off centre, outside the 3.73 mm face bound. DETECT relabels the
  top-face block as an in-cavity jam at 0.35-0.37 mm depth. RECOVER's jam branch tells the
  localizer the plug entered at that probe and retries from the same place until the
  retry or time limit. F's spiral passes over the offset (F on gantry trial 2 seated at
  6.07 s, 0 retries).
- Development seeds: all 24 C failures are same-sign trials, all show the CoP relabel and
  three or more same-probe jam retries; with opposite signs C seated 80 of 80. F failed 1
  trial in the 160 shown.
- The same jam loop ends 17 of 93 gantry and 18 of 116 arm C failures in the old
  `heldout` suite, 31 of them in `heldout_mischar_2mm`, by another route (camera depth
  error).

**Candidate change, in plain words.**
- (3a) A stop short of the engage depth that is relabelled only by its CoP updates the
  localizer as a block (with the unclean-CoP sigma, or no CoP), not as an entry.
- (3b) After two attempts from the same probe (within a set distance, proposed 0.1 mm)
  with no depth progress, fall back to a bounded spiral around the current estimate, as F
  does. Spiral radius and pitch: F's own values, not new ones.
- (3c) Widen the CoP face bound and the localizer prior by a told in-hand uncertainty.
  This needs C to be told an in-hand sigma, which C is not told today (no code in
  `defex/control` or `defex/recovery` reads `grasp_xy_sigma_mm`). It is a change to what
  C is told, so it needs Hasan's decision first, and every baseline must be told the same.
- Candidates for the RULE.md: 3a; 3b; 3a + 3b. 3c only if Hasan accepts it.

**Development-seed protocol.**
- `--suite heldout2 --conditions h2_mf_grasp_unseen_1deg,h2_mf_grasp_unseen_2deg`, both
  machines, seeds 2026 and 2027, 40 trials per condition (160 pairs per machine).
- The old `heldout` suite on both machines, 40 trials per condition per seed.
- The no-harm check in section 4.

**Keep rule.**
- Target cells, each machine, both seeds pooled: net gain of at least half of the trials
  where C fails and F seats.
- Old `heldout`: no net loss on either machine.
- Plus every no-harm bound in section 4.

**Risk of tuning to the test.**
- The diagnosis replayed seed 20261207 (gantry trials 2, 9, 37; arm 2, 4, 37) and ran
  counterfactual replays there with `surface_cop_margin_mm` 1.0 and `min_prior_sigma_mm`
  1.0. Those values were not searched, but they were tried on a reported seed. A candidate
  must not take either value from those replays; any new value needs a basis in the
  geometry, stated in RULE.md.
- `h2_mf_grasp_unseen` is now a development family; the same limit as 3.1 applies.
- The old `heldout` suite was used in W4 development and is not a clean test either.
- The fix must be judged only on seeds V and B.

**Equal effort.**
- 3b gives C what F already does. There is nothing to give the baselines.
- Against C: an in-hand camera or fingers that centre the plug remove this failure for
  every controller (C seated 5 of 5 replays with the true grasp seen). That is an
  integrator setting, not a C change.
- If 3c is accepted, D and F could size their spiral from the same told sigma. That
  would be a baseline change with its own rule. Open item.

### 3.4 A socket-axis reference for the tilt check

**Diagnosis** (`results/v0.2f_tilt_diagnosis/REPORT.md`, items 1 and 3).
- G's 3.01 deg bad unit (benchmark_v0.2e arm `mf_noise_1mm` trial 130): true tilt
  3.09 deg, measured 0.47 deg, because C's socket-axis estimate was 2.87 deg off after a
  wrong flat-face fold.
- Development seeds, C and G, latching and latch_spread: 234 of 8,320 tilt verdicts read
  more than 1 deg under the true tilt. Largest error projection: camera 149, in-hand 82,
  folds 3. All 10 verdicts at a true tilt over 2 deg passed; all those trials ended seated
  at 1.83-2.98 deg.
- C and G passed 0 tilted bad units on the development seeds. 5 declared C/G latching
  trials ended at 2.5-3.0 deg.
- Two simple options were checked and rejected there: a fold cap at 3 sigma (7 folds
  better, 7 worse) and failing a gantry yaw sweep that hits its end (would act on 12% of
  accepted units, all with good yaw).

**Candidate change, in plain words.**
- (4a) Before the latch check, run a low-force conform against the cavity floor or walls
  at the bottom, and use the plug-to-cavity angle it gives as the socket-axis reference for
  the tilt check. Whether the Micro-Fit cavity gives a clean reference (terminals, latch,
  floor area) is unknown. No design exists yet.
- The only candidate for the RULE.md is 4a, with its values stated before any run.
  If 4a cannot be built so that it reads the cavity, not the aim, this fix is dropped
  before any run.

**Development-seed protocol.**
- The tilt collector (`experiments/v02f_tilt_diag.py`, ground truth read between ticks,
  never by the controller), seeds 2026 and 2027, latching and latch_spread, 50 trials per
  condition, both machines, C against the candidate.
- The no-harm check in section 4.

**Keep rule.**
- Verdicts reading more than 1 deg under the true tilt fall by at least half against C
  on the same trials.
- No candidate-only bad unit or bad part passed.
- Mean cycle on latching good parts seated by both rises by at most 1.0 s per machine.
- Plus every no-harm bound in section 4.

**Risk of tuning to the test.**
- The diagnosis used seeds 2026 and 2027, validation seed 4007 (spent), and replays of
  benchmark seed 20261130 (G and C trial 130, J trial 46, arm `mf_noise_1mm`).
- Judge only on seeds V and B.
- The benchmark cannot show a gain in outcomes. C's tilted bad-unit rate is 0 on every
  seed, and G's one case is about 1 in 600 arm `mf_noise_1mm` G trials on one seed. The
  only effect endpoint is the collector's under-read count, which is a measurement in
  simulation, not a test on outcomes.

**Equal effort.**
- J2 gets it (C's VERIFY).
- No fair baseline has a tilt check. The fair counterpart is a conventional seat-and-align
  step (`BASELINE_FAIRNESS_RUN.md`).

## 4. Development rules common to every change

- Development seeds 2026 and 2027 only. No validation or benchmark seed is touched until a
  change is kept.
- Before the first candidate run of a change, commit `results/<round>/fix<N>/RULE.md`
  with: the listed candidates and every value they use, the target cells, the metrics, the
  keep rule from section 3, the no-harm bounds below, and the tie-break. Nothing in it
  changes after the first candidate run. If the rule picks something the developer
  dislikes, that is reported, not changed.
- At most 3 candidates per change. No value is searched; each value has a stated basis.
- **No-harm check** (every candidate, both seeds, both machines, 20 trials per
  condition): `standard`, `latching`, `heldout`, `latch_spread`, and heldout2 only
  `h2_ft_drift_*` and `h2_mf_grasp_unseen_*`. Controllers: C, the candidate, J, and J with
  the candidate's VERIFY where it applies. Drop the candidate if any of these holds:
  - any candidate-only bad unit on a good part, in any cell;
  - any candidate-only bad part passed, in any cell;
  - net added good-part rejections outside the target cells over
    max(1, floor(0.001 x the good-part trials of those cells));
  - net added protective stops over the same bound;
  - mean cycle on trials seated by both rises more than 0.25 s in any machine and suite
    outside the target cells (1.0 s on latching suites for change 4);
  - any row differs from C's where the candidate's code path was not entered (a logged
    event). That is a bug: fix it and rerun; no decision on the buggy run.
- Tie-break among kept candidates of one change: larger net target gain, then fewer net
  added rejections, then lower cycle cost, then the one listed first.
- The no-harm bounds are proposals. Hasan may change them before a RULE.md is committed,
  not after.
- **Hands off the clean heldout2 families.** `h2_tilt_unseen`, `h2_yaw_unseen` and
  `h2_mf_tolerance` were never run on a development seed except a 3-trial C-only smoke
  test and an unread 2-trial timing slice, both on seed 2026
  (`results/heldout2_v0.2f/PREREGISTRATION.md`). Nothing in this round
  may run them on any seed before the benchmark, so they stay held-out families.

## 5. Combining the kept changes, and validation

- **C2** = C with every kept flag on.
- Combined development check on seeds 2026 and 2027: the section 4 no-harm check, and each
  kept change's net target gain must be at least 80% of its gain alone. If it fails, drop
  the kept change with the smallest target gain and check once more. If that fails, stop
  and report; no benchmark.
- **Validation, once, on seed V** (to be assigned when frozen): the no-harm suites at 20
  trials per condition, the target cells at 40 (arm friction at 100), controllers C, C2,
  J, J2. Pass: the no-harm bounds hold (bounds computed from seed V's counts) and each kept
  change has net target gain above 0. A change that fails is NO-GO and leaves C2. No
  second try on seed V.
- If a change leaves C2 at validation, the remaining combination was not validated as a
  whole. Either validate it again on another fresh seed, or say so in the benchmark
  pre-registration. Hasan decides.

## 6. Benchmark design

**Frozen code.** Commit to be filled. The run starts from a commit that changes only
`results/`. Every `config.json` must show `git_dirty: false`. `RUN_LOG.md` records an
empty `git status --porcelain --untracked-files=all` outside `results/`, the environment,
start and end times, and workers. The variants file's sha256 is recorded here. G's model
files are unchanged (sha256 in `results/heldout2_v0.2f/PREREGISTRATION.md`).

**Controllers.**

| Name | What | Role |
|---|---|---|
| C | `adaptive`, v0.2e code, flags off | reference: the v0.2e product |
| C2 | C with the kept flags on | the changed product |
| D, E, F, H, I | v0.2e fair baselines | fair baselines |
| J | `spiral_rcc_verify`, v0.2e | F plus C's VERIFY; not a fair baseline |
| J2 | J with C2's VERIFY flags on | F plus C2's VERIFY; not a fair baseline |
| fairness baselines | from `BASELINE_FAIRNESS_RUN.md`, only if kept and validated there | fair baselines |
| G (optional) | `adaptive_learned`, v0.2e | Hasan decides; G is not changed |
| A, B (optional) | v0.2e | reported in five runs already; drop to save CPU unless Hasan wants them |

The fairness baselines (K = I plus seat-and-align, K2 = F plus seat-and-align, and D, F,
H, I with a gentle retract) join only
if they pass their own rules and validation. When they do, "best fair baseline" is taken
over D, E, F, H, I plus those, and the v0.2e set (D, E, F, H, I) is also reported for
continuity.

**Suites and trials, base seed B, both machines.**

| Suite | Trials per condition | Pairs per controller per machine | Note |
|---|---|---|---|
| standard | 100 | 2,000 | as v0.2e |
| arm extension: standard `friction_0.6,friction_1` | 400 | 800 | trials 0-99 repeat the main run; the primary test for change 2 uses this run |
| latching | 200 | 1,400 (600 good) | as v0.2e |
| heldout (old) | 100 | 500 | not clean (W4 development) |
| latch_spread | 100 | 900 (600 good) | as v0.2e |
| heldout2 | 100 | 1,000 | fresh draw; 2 of its 5 families are development families now |
| heldout3 (optional) | to be set | to be set | new families, see below |

**The fresh held-out question.** heldout2 at seed B is a fresh draw. For `h2_ft_drift`
and `h2_mf_grasp_unseen` it is a test on fresh seeds of known families, not an unseen
test. The other three heldout2 families stay held out if section 4's hands-off rule is
kept. An out-of-family test needs new families (a heldout3), written and committed before
any C2 development starts and never run before the benchmark. None is designed. Hasan
decides whether to add one.

**Commands** (to be fixed when frozen; `<ctrls>` is the list above):

```
for M in gantry arm; do
  for S in standard:100 latching:200 heldout:100 latch_spread:100 heldout2:100; do
    DEFEX_CONTROLLER_VARIANTS=<variants file> python -m experiments.robustness \
      --suite ${S%%:*} --backend $M --trials ${S##*:} --seed <seed B> --workers 9 --no-plots \
      --name <round>/${M}_${S%%:*} --controllers <ctrls>
  done
done
DEFEX_CONTROLLER_VARIANTS=<variants file> python -m experiments.robustness --suite standard \
  --backend arm --trials 400 --conditions friction_0.6,friction_1 --seed <seed B> --workers 9 \
  --no-plots --name <round>/arm_standard_friction_ext --controllers <ctrls>
```

Then the table scripts used for v0.2e and heldout2 (`checkpoint_report`, `cp2_audit`,
`v02c_paired`, `v02d_headline`, `heldout2_tables`). They must be checked to accept the new
controller names before freezing.

**Optional, not proposed by default:** an arm pyramidal-cone friction check (C, C2, F, J,
J2) at seed B. `experiments/friction_diagnosis_v02f.py` refuses any seed but 2026, 2027
and two named replay seeds, so this needs a runner change before freezing.

## 7. Endpoints

**Primary** (one test per kept change; changes that were dropped have no primary test):

| Id | Change | Cell at seed B | Comparison | Metric |
|---|---|---|---|---|
| P1 | 3.1 | arm heldout2 `h2_ft_drift`, both levels, 200 pairs | C2 vs C | bad units on good parts |
| P2 | 3.2 | arm standard extension `friction_1`, 400 pairs | C2 vs C | seated |
| P3g | 3.3 | gantry heldout2 `h2_mf_grasp_unseen`, both levels, 200 pairs | C2 vs C | seated |
| P3a | 3.3 | arm heldout2 `h2_mf_grasp_unseen`, both levels, 200 pairs | C2 vs C | seated |

Change 3.4 has no primary test (section 3.4). Its endpoint is descriptive: the collector's
under-read count on seed V, and on seed B only if Hasan wants the collector run there.

**Secondary.**
1. Every cell, every suite, both machines: C2 vs the best fair baseline, by the v0.2e
   decision rules (`results/benchmark_v0.2e/PREREGISTRATION.md`).
2. Harm check, every cell: C2 vs C, seated and bad units. Any cell with C2 below C at
   p < 0.05, and every C2-only bad unit, goes in the report headline, whatever its p.
3. Bad units on good parts: C2 vs H and vs I; bad parts passed: C2 vs the fair baseline
   with the fewest.
4. J2 vs J, J2 vs C2, J2 vs I: seated and bad units.
5. C2 and J2 cycle p50 and p95, good units per hour (0 s and 60 s per stop), protective
   stops, torn good latches (`final_latch_intact`, logged since v0.2f), next to their
   success, including where they are worse.
6. P1's companion: C2 vs C seated in the same cell; C2 vs D in the same cell.
7. Old `heldout_mischar_2mm`: C2 vs C and vs J (change 3.3's second route).

## 8. Multiplicity

- Primary: Holm over the primary tests that exist (at most 4), family-wise 0.05. With 4
  tests the smallest p must be under 0.0125.
- Secondary: no correction, as in every earlier run. Outcomes at 0.01 <= p < 0.05 are
  marked. About 10 cells x 8 tests.
- Harm checks are read at an uncorrected 0.05, because a missed harm costs more than a
  false alarm, and every C2-only bad unit is reported by count.
- Totals pooled over machines or suites are descriptive and get no test.
- "Matches" means no significant difference, not equal.

## 9. Power

Exact McNemar, from the committed discordance rates (`POWER.md`, tables 1-3).

Observed in the target cells:

| Cell | Source | C-only / other-only | Fixable (C fails, reference seats) |
|---|---|---|---|
| arm heldout2 `h2_ft_drift` vs D | seed 20261207, 80 pairs | 0 / 19 | 23.75%; C bad units 8 (10.0%) |
| gantry heldout2 `h2_mf_grasp_unseen` vs F | seed 20261207, 80 pairs | 0 / 19 | 23.75% |
| arm heldout2 `h2_mf_grasp_unseen` vs F | seed 20261207, 80 pairs | 2 / 17 | 21.25% |
| arm standard `friction_1` vs I | three seeds, 300 pairs | 0 / 18 | 6.00% |

Power at the planned n. f = share of the fixable trials the change fixes (an assumption);
h = harm rate, trials C2 newly loses.

| Test | n | f = 1.0, h = 0 | f = 0.5, h = 0 | f = 0.5, h = 0.5% | the last at alpha 0.0125 |
|---|---|---|---|---|---|
| P1 (bad units) | 200 | 1.00 | 0.94 | 0.75 | 0.53 |
| P2 | 400 | 1.00 | 0.98 | 0.73 | 0.50 |
| P3g | 200 | 1.00 | 1.00 | 1.00 | 1.00 |
| P3a | 200 | 1.00 | 1.00 | 1.00 | 0.99 |

- P1 and P2 are the weak ones: if a change fixes only half its cases and costs 0.5% in the
  same cell, power under Holm is about one half. 80 pairs (heldout2's old size) or 100
  (standard's) would not be enough for P2: n for 80% at f = 0.5, h = 0 is 270, which is why
  the arm friction extension is 400.
- The heldout2 rates come from one seed and 80 pairs per family. The friction rate pools
  three seeds.
- Harm detection is weak in small cells (`POWER.md` table 3): with 600 good-part latching
  pairs, a 1% loss with no gains elsewhere is found with power 0.56; with 2,000 standard
  pairs, a 0.5% loss with power 0.93. That is why development uses count bounds, and why
  the report gives counts for every harm, not only p-values.
- Zero bad units has a Wilson 95% upper bound of 1.9% at 200 trials, 0.64% at 600, 0.19%
  at 2,000.

## 10. Stop conditions

Before the benchmark:
- No change kept on development: no validation, no benchmark. Report.
- Every change NO-GO on seed V: no benchmark. Report.
- A change would need to break the ground-truth separation: stop and ask Hasan (brief,
  section 7).
- A candidate needs a value searched on a reported seed: drop it.
- The frozen benchmark estimate is over 4 hours of compute: stop and ask Hasan (brief,
  section 7). The core plan is under (section 12); adding the fairness baselines crosses it.

During the run:
- A run that stops early is repeated with the same command, and `RUN_LOG.md` says so.
- If the run exposes a bug: fix it, write a new pre-registration, use a fresh seed, keep
  the superseded report in `earlier_runs/`. No result is read until all runs finish.

## 11. What each outcome would mean for the claims

| Outcome | Meaning |
|---|---|
| P1 significant, C2 bad units near 0 in `h2_ft_drift` | The diagnosed drift route to a bad unit is closed in simulation, for linear drift at the assumed rates, on fresh draws of a known family. "0 bad units" then rests less on the constant-bias sensor model. It says nothing about a real sensor's drift. |
| P1 not significant | VERIFY under drift stays an open weakness. Any "0 bad units" claim keeps the drift caveat from the checkpoint report (item 3). |
| P2 significant | The arm friction_1 false reject on the nominal simulator narrows or closes. Whether C2 still loses friction_1 to I is secondary 1. mu = 1.0 is above the connector default (0.3), so this matters less than its p suggests. |
| P2 not significant | "C loses arm friction 1.0" stays in the scorecard. |
| P3 significant | The plug-offset loss to F narrows. If C2 is still below F with p < 0.05 there (secondary 1), "C below F under a grasp offset" stays. |
| P3 not significant | The scorecard row "heldout2 plug offset: C below F" stands. |
| Change 3.4 kept, under-reads fall | The tilt check sees part of the socket-axis error in simulation. No outcome claim follows; tilted bad units were already near 0. |
| Any harm check fails | It goes in the headline. A change that fixes one cell and costs another is reported as such. |
| J2 close to C2 | Changes 3.1, 3.2 and 3.4 are VERIFY changes, so they reach J2 too and do not separate C from J. Only change 3.3 (insertion and recovery) is C2's alone. The "C or J" question stays open. |
| C2 vs the best fair baseline on standard | Read by the v0.2e rules. The changes target arm and heldout2 cells; the standard lead is not expected to move, and a fall there would be a harm. |
| Wins in `h2_ft_drift` and `h2_mf_grasp_unseen` | Shown on fresh seeds of development families. Not a held-out result. The held-out reading comes from `h2_tilt_unseen`, `h2_yaw_unseen`, `h2_mf_tolerance` and heldout3 if it exists. |

Whether any of this changes the pitch is Hasan's decision.

## 12. Rough time and CPU

Per-trial CPU from the committed rows (`POWER.md` table 6). Sum of `wall_time_s` divided
by workers matched past wall times: benchmark_v0.2e ran 96,000 trials, about 17.4 CPU
hours, in 1 h 56 min at `--workers 9` (`results/benchmark_v0.2e/RUN_LOG.md`); heldout2 ran
8,000 trials, about 2.1 CPU hours, in 63 min at `--workers 2` with the machine at load
40-50 (`results/heldout2_v0.2f/RUN_LOG.md`). C2 and J2 are assumed 15% slower than C and J
(an assumption: extra probes and retries).

| Step | CPU hours | Wall at 9 workers, quiet machine | Wall at 2 workers |
|---|---|---|---|
| Target-cell development, per change | about 1 | under 10 min | about 30 min |
| No-harm development check, per candidate (2 seeds, C, candidate, J, J-candidate) | about 4.5 | about 30 min | about 2.3 h |
| Validation on seed V (no-harm suites about 2.3, plus the target cells) | about 4 | about 30 min | about 2 h |
| Benchmark, core (C, C2, D, E, F, H, I, J, J2) | about 29 | about 3.3 h | about 15 h |
| Benchmark, core plus K and K2 | about 37 | about 4.1 h | about 19 h |
| Benchmark, core plus K, K2 and four gentle-retract variants | about 47 | about 5.2 h | about 24 h |

- The heldout2 per-trial figures were measured under heavy load, so they overstate.
- The 4-hour line in the brief: the core plan is under it on a quiet machine; the larger
  plans cross it and need Hasan's approval, or a cut (for example old `heldout` at 50
  trials, or no A, B, G).
- Engineering, rough: change 3.1 and 3.3 are small (a check and a fallback, about half a
  day to a day each with tests); 3.2 is medium (a stop rule plus a probe change, about a
  day); 3.4 has no design and may take two days or be dropped. Development runs, review
  and validation add about a day. Total about 3-5 working days before the benchmark, with
  the machine shared.

## 13. Before this can be frozen

- [ ] Hasan says go, and which of the four changes are in scope.
- [ ] Hasan decides on 3c (telling C an in-hand sigma) and on heldout3.
- [ ] Seeds V and B assigned and checked unused.
- [ ] Each change: RULE.md committed before its first candidate run; dev decision; tests;
      architecture test green; flags-off identity against v0.2e rows.
- [ ] C2 combination check and validation on seed V passed.
- [ ] Controller list fixed: G, A, B in or out; fairness baselines in only if kept and
      validated under `BASELINE_FAIRNESS_RUN.md`.
- [ ] Frozen commit, variants file sha256, model sha256 filled in; table scripts accept
      the new names.
- [ ] Section 12 estimate redone for the final list; Hasan approves if over 4 hours.
- [ ] "Expected from development" section written from the dev and validation results,
      before the run, as in every earlier pre-registration.

## 14. Disclosed before the run (to keep in the frozen version)

- Every diagnosis above is POST HOC. Each was chosen after the reported results were seen.
- Seeds 2026 and 2027 have been used for every controller decision since W1, and now for
  the heldout2 `h2_ft_drift` and `h2_mf_grasp_unseen` families.
- The diagnoses replayed reported seeds 20261123, 20261124, 20261130, 20261205 and
  20261207 on named failures. None of them may be used to judge a change.
- All four changes were designed knowing where C loses to F, D and I. The fair baselines
  get their own items in `BASELINE_FAIRNESS_RUN.md` under the same dev budget.
- Change 3.4's effect cannot be shown on outcomes in this benchmark.
- The F/T drift is linear and its rates are assumed. mu = 1.0 is an extreme condition.
