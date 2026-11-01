# v0.2c: arm tuning of the conventional cells D, E and F (development)

Development measurements in simulation on dev seeds 2026 (diagnosis and tuning) and
2027 (confirmation) only. Every number below comes from `tables.md` in this folder
(`python -m experiments.v02c_arm_tables`), which recomputes it from the committed
`trials.csv`, `events.json.gz`, tuning CSVs and diagnosis JSON files named there.
Branch `v0.2c/arm-baselines`. Before runs: commit 54f3097 (the frozen Checkpoint 2
code). After runs: commit e054ff0. All `config.json` files show `git_dirty: false`.

## Result

After arm tuning, F still seats about as many good parts on the UR5e as C, and no
more. D closes most of its gap to C. E's seating does not change. All three are now
about 1.7-2.3 s faster per cycle. C's arm advantage remains bad parts passed as good.

Seed 2027 (not used for any choice), standard 5-condition set plus the three
Micro-Fit good-part conditions, 160 paired trials per controller:

| | Before | After | After vs before (p) | After: C-only / other-only (p) | Median cycle before -> after (s) | Good units/h (60 s per stop) before -> after |
|---|---|---|---|---|---|---|
| D spiral | 113 | 132 | 20 / 1 (2e-05) | 9 / 2 (0.065) | 6.52 -> 4.77 | 198 -> 398 |
| E correction_rcc | 110 | 110 | 0 / 0 | 32 / 3 (<1e-6) | 6.32 -> 4.07 | 109 -> 118 |
| F spiral_rcc | 140 | 138 | 2 / 4 (0.69) | 8 / 7 (1) | 6.49 -> 4.78 | 364 -> 403 |
| C adaptive | 139 | 139 | identical | - | 8.39 | 229 |
| G adaptive_learned | 144 | 144 | identical | G-only / C-only 5 / 0 (0.062) | 8.42 | 247 |

- **Tuned F does not beat C on the arm.** It ties: 138 against 139 of 160 (C-only 8,
  F-only 7, p = 1). It also tied before tuning (140 against 139). The tuning made F
  faster, not better at seating.
- **D improved.** 113 to 132 of 160 (p = 2e-05), almost all on Micro-Fit parts
  (latching good parts 34 to 50 of 60). C is still ahead of D, 9 against 2, but not
  significantly (p = 0.065).
- **Ranking by seating on the arm, seed 2027:** before G 144, F 140, C 139, D 113,
  E 110; after G 144, C 139, F 138, D 132, E 110. G against F: 12 / 6 (p = 0.24);
  G against D: 12 / 0 (p = 0.0005).
- **Cycle time.** D and F median 4.8 s, E 4.1 s, against 8.4 s for both C and G.
  At 60 s per protective stop, F makes 403 good units per hour and D 398, against
  C's 229 and G's 247.
- **Bad parts passed as good** (four deliberately bad Micro-Fit parts, 80 trials per
  seed): C 0 and G 0 of 80 on both seeds (Wilson 95% upper bound 5%), unchanged.
  After tuning D passes 42 (seed 2026) and 39 (2027), F 44 and 45, E 31 and 37.

## What got worse

- **D passes more bad parts.** 23 to 42 of 80 on seed 2026, 25 to 39 on seed 2027.
  The tuned search now finds the hole on half-latched and broken-latch parts and
  pushes them to depth, which D's depth check cannot tell from a good seat
  (broken latch: 20 of 20 on both seeds). The wider seat margin (0.5 to 1.0 mm)
  also passes stubbed terminals, which stop 1.5 mm short (1 to 7 and 0 to 6 of 20).
- **D protective stops** rose on the standard set: 2 to 5 (seed 2026) and 1 to 2 (2027).
  D's seed-2026 standard-set success went 82 to 80 (within noise).
- **F's 95th-percentile cycle** rose on three of five arm sets (for example seed 2027
  latching good parts 10.81 to 11.90 s; all 20 standard conditions 7.92 to 9.54 s),
  while its median fell 1.7 s.
- **F escapes on good-part conditions**, seed 2027 standard set: 9 to 11 (noise_2mm).
- In the same place, something improved: F's bad-part escapes fell from 56 to 44
  (2026) and 59 to 45 (2027), all on stubbed terminals (16 to 4, 19 to 5), because its
  seat margin went from 1.0 to 0.5 mm. The seat margin trades false jams on good
  parts against passing short bad parts, in both directions.

## Diagnosis (dev seed 2026, before any arm work)

Standard 5-condition set and latching suite, 20 trials, at 54f3097
(`before/arm_dev2026_*`).

1. **Speed against the force budget.** The W5 contact-speed rule scales D's and F's
   guarded speeds by 0.40 on the UR5e (6.3 kg at the tool), to 4 mm/s for descent and
   insertion. The median cycle is 6.5 s on the arm against 3.5 s on the gantry. A
   faster single speed does not work:
   - At 25 mm/s nominal (10 mm/s on the arm), D seated 3-4 of 63 in the tuning's
     speed stage, against 59-60 at 10 mm/s.
   - In three diagnostic trials, every one aborted on D's 20 N force limit at the
     floor contact (21.7-23.4 N, `diagnosis/single_speed_25.json`).
   - With 0.2 s of following lag, 10 mm/s puts about 2 mm of setpoint lead into the floor.
   - F's fast settings seated 10 of 63.
2. **Micro-Fit search.** D's stiff spiral times out on Micro-Fit parts. The capture
   range is 0.15 mm clearance plus a 0.4 mm lead-in. D scored mf_nominal 10 of 20,
   mf_moderate 14, mf_noise_1mm 2, nearly all time limits in the spiral.
   **Not arm-specific**: on the gantry D scores 6, 6 and 1 of 10 on the same
   conditions (`before/gantry_rule3_latching`). W1 tuned D before the Micro-Fit
   connector existed. F, on the RCC stage, seated 20, 20 and 17 of 20.
3. **False jams.** With D's 0.5 mm seat margin, a contact on the chamfer 0.7-1.5 mm
   down is taken for the face, and a full seat then looks short. In four traced D
   retries the plug was 14.78-14.99 mm deep (full depth 15 mm) when D declared a jam
   (`diagnosis/false_jams.json`). Each costs a retry of about 5 s; most then succeed.
   **Not arm-specific**: a jam retry followed 13 of 34 found holes on the arm and 12
   of 37 on the gantry.
4. **Servo lag at hole found** (W5b's open note). When the spiral finds the hole, the
   command leads the plug by speed x 0.2 s. This was offered as an option (continue
   from the measured position). It made no measurable difference (D 60 against 60 of
   63, F 61 against 61) and the rule did not pick it. It stays off.
5. **Not addressed.**
   - D's excess-torque aborts and protective stops on noise_2mm (3 and 2 of 20;
     gantry 0 and 0), caused by the stiff UR5e wrist (400 N m/rad in yaw against 15
     on the gantry).
   - The vision-orientation false accepts of D and F, which a spiral cannot correct.
     They are the same on both machines.
6. **E** has no arm-specific failure. Its protective stops on noisy vision are the
   same on the arm as on the gantry (noise_2mm: 17 of 20 on both).

## What was done

**Per-machine settings.** D, E and F each hold a stiff-fixture config in
`defex/config.py`: `SpiralSearchStiffFixtureConfig`,
`CompliantSpiralSearchStiffFixtureConfig` and `PassiveComplianceStiffFixtureConfig`.
They run it only where `outside_reference_family` (`defex/control/base.py`) is true:
a wrist at least 4x the gantry's stiffness, or a servo lag at least 2x the gantry's.
These are the same thresholds as C's W5b rules. Every gantry, including the
sim-randomization bands, runs the gantry config (`tests/test_arm_baselines.py`).
Nothing under `defex/control` reads the simulator; the import test passes.

**Tuning, the W1 protocol on the arm, scaled down** (`SELECTION_RULE.md`, committed
before the first arm tuning run; amendment 1 committed before the runs that use it).
It keeps W1's parameter ranges, vendor references and ranking rule (success, then
median cycle, then p95). Differences, stated exactly:

- **Conditions.**
  - Coarse and fine: W1's six hardest conditions plus mf_nominal and mf_noise_1mm.
  - Later stages: W1's 18 development families plus the three Micro-Fit good-part conditions.
  - Bad parts and the generalization conditions were never tuned on.
- **Cut for compute** (the machine was shared with the Checkpoint 2 run and other agents):
  - Coarse: 81 settings instead of 324. Dropped 8 N force, 2.0 and 2.5 mm pitch and
    20 mm/s, which never made the gantry top five. Added the edge values 2 N, 0.5 mm
    and 2.5 mm/s. Push fixed at 0.5 mm here and varied later.
  - 3 trials per condition in the coarse, fine and speed stages (W1: 10, 10, 20);
    10 in confirm (W1: 20).
  - Fine starts from the top 3 coarse settings (W1: 5) and drops the one-attempt value.
  - Confirm takes the top 3 (W1: 5). No separate edge stage.
- **Added for the arm:**
  - A speed stage: push distance, a faster guarded speed, and the lag option.
  - By amendment 1, a speed2 stage for two-speed guarded moves.
- **Trials:** D 4,446, F 4,446, E 1,062; 9,954 in all. W1 used about 34,000 for D
  and F each.

**Two-speed guarded moves (amendment 1).** The speed stage showed that a faster
single speed trips the force limit. D and F then got the fix C already has
(`free_insert_speed_mm_s`, `near_bottom_*`): a free speed inside the cavity, outside
the mouth band, and the tuned speed within a margin of the floor. It is off on every
gantry (`free_speed_mm_s = 0`). The amendment was written after D's coarse, fine and
speed stages. D's confirm stage, which had started, was stopped with no output and
re-run after the amendment.

**Selected settings (confirm rank 1).** For D and F, ranks 1-3 tied on success and
differ only in the two-speed values, so cycle time chose.

| | Changed from the gantry setting | Confirm, 21 conditions x 10 trials |
|---|---|---|
| D | search force 2 -> 5 N, spiral speed 2.5 -> 10 mm/s, lateral search stiffness stiff -> 0.5 N/mm, insert force 8 -> 5 N, seat margin 0.5 -> 1.0 mm, free speed 25 mm/s | 198/210, median 4.76 s |
| F | search force 3 -> 2 N, pitch 1.0 -> 1.5 mm, lateral search stiffness stiff -> 0.5 N/mm, insert force 3 -> 8 N, attempts 3 -> 2, seat margin 1.0 -> 0.5 mm, push 0.5 -> 0.3 mm, free speed 25 mm/s | 202/210, median 4.75 s |
| E | insert speed 4 -> 8 mm/s | 189/210, 21 stops, 4.08 s |

On Micro-Fit good parts, every controller's insertion force is the connector's force
budget (30 N). The insert-force values above therefore apply only to the
housing-only connector.

The tuning landscapes were flat. D's coarse settings scored 16-21 of 24 and every
fine setting 21 of 24; F's coarse settings scored 20-22 and every fine setting 22.
The one clear signal was lateral compliance during D's search (Flexiv's
searchStiffRatio, already in W1's grid). The top 14 coarse settings all used it. The
mean over the 27 settings per value was 18.4 of 24 for the stiff search against 20.1
at 0.5 or 2 N/mm.

## Effort compared with C

- **C on the arm:** W5b (diagnosis on seed 2026 and the rule changes listed in its
  report, set by hand), plus G's learned prior (5,900 trials of arm contact data,
  selected on validation seed 4001).
- **D, E and F on the arm, here:** diagnosis on seed 2026, 9,954 tuning trials on
  seed 2026, and two offered mechanical options. Two-speed moves were adopted by the
  rule; the lag option was not.

Both C's arm rules and this tuning were set on seed 2026, so seed 2026 favours both.
Seed 2027 is the cleaner comparison, and it is what the result above uses. In trial
count this tuning is smaller than W1's gantry tuning. The flat landscapes suggest
more trials would mostly reorder ties.

## Field identity

`equivalence/*.txt` (`scripts/compare_trials.py`, wall_time_s ignored):

- Gantry, all seven controllers A-G, on the rule-3 set (seed 2026; noise_1mm,
  noise_2mm, friction_1 at 20 trials) and the latching suite (10 trials):
  910 trials, 32,760 fields, **0 differences**.
- Arm, A, B, C and G on all five arm sets (seed 2026 standard 5 and latching; seed
  2027 standard 5, latching and all 20 standard conditions): 2,320 trials,
  **0 differences**.
- D, E and F on the arm differ, as intended.
- Full test suite: 110 passed at ffdc670 (10 new tests in `tests/test_arm_baselines.py`).

## Limits and open issues

- **Small samples.** Development seeds only. Seed 2027 has 20 trials per condition
  (5 for the full 20-condition set), so differences of a few trials are within noise.
  Only D's improvement is significant.
- **Gantry baselines untuned on Micro-Fit.** Gantry D and F were never tuned on
  Micro-Fit parts either (W1 predates W3). They stay untuned here because the gantry
  had to stay field-identical. D on the gantry Micro-Fit set is as weak as D on the
  arm was (mf_noise_1mm 1 of 10). Tuning the gantry baselines on latching parts would
  change gantry D and F and needs a new pre-registered run.
- **Checkpoint 2 arm rows.** The Checkpoint 2 benchmark (`benchmark_v0.2b`) ran D, E
  and F on the arm at their gantry settings, so its arm rows for them are the
  "before" state here. Its trials were not read for this work.
- **Speeds.** The speed stage coupled descent and insertion speed; a faster insertion
  with a slow descent was not tried on its own. E runs without the W5 speed scaling
  (as before), so its 8 mm/s is unscaled on the arm.
- **Escapes.** Escapes are now the main difference between C and the tuned
  conventional cells on the arm. D's and F's depth-only checks cannot see a
  half-latched or broken-latch part. Flexiv's CheckPiH lateral probe or a pull test
  are the conventional additions that would; none was added here.
- **Arm model.** Servo lag and wrist stiffness are Menagerie's UR5e values; a real arm
  must be identified first.

## Seeds

- Run: 2026 (diagnosis, tuning, before/after, gantry identity) and 2027 (before/after).
- Not run: 4002, 3001-3040, 3032, and every reserved seed.
- No file under `results/benchmark_v0.2b/` was read.

## Reproduce

```
results/v0.2c_arm_baselines/run_set.sh before 2      # at 54f3097 (a detached worktree)
results/v0.2c_arm_baselines/tune_chain.sh 2          # arm tuning, SELECTION_RULE.md
results/v0.2c_arm_baselines/run_set.sh after 2       # at e054ff0
results/v0.2c_arm_baselines/equivalence.sh
python -m experiments.v02c_diagnose jams --out results/v0.2c_arm_baselines/diagnosis/false_jams.json
python -m experiments.v02c_diagnose speed --out results/v0.2c_arm_baselines/diagnosis/single_speed_25.json
python -m experiments.v02c_arm_tables > results/v0.2c_arm_baselines/tables.md
```

D's tuning ran its coarse, fine and speed stages at efcc75c, then
`FROM=speed2 tune_chain.sh 2 spiral` at 9f84602 (amendment 1). F and E ran at
9f84602. The `tuning/*.json` files record each commit.
