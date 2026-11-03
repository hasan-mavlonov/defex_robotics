sim_randomization_v0.2f report

Run details
- Seed 20261205. Code frozen at c87f942. Run from 69cbaa4, which adds only results/.
- 12 randomized MuJoCo simulators plus the nominal one (variant 0), on each machine.
- Controllers C, F, H, I, J and G. G is pinned (configuration of this run): it runs its
  machine's nominal learned model whatever servo values the variant reports.
- 26,052 paired trials.

Every number below comes from TABLES.md, made by the pre-registered command, unless a
line says it comes from trials.csv and is post hoc. References are benchmark_v0.2e's
classes on the same conditions (REFERENCES.md). Simulation only.

RESULT IN ONE PARAGRAPH

Gantry
- Every primary comparison holds across simulators: 29 of 29.
  - C against F, H and I, for success and for bad units, in every group.
  - The zero bad units and the zero bad parts.
- Of the 20 secondary comparisons, 18 hold and 2 do not:
  - G (pinned, configuration of this run) against C on c_favourable. Variant 0 does
    not reproduce the benchmark's gain there either: 44 of 45 each.
  - J against C on neutral. J false-rejected 10 parts in variant 10.

Arm
- 24 of 29 primary comparisons hold. Four do not hold and one is not resolved:
  - NEUTRAL SUCCESS, C AGAINST F, H AND I: DOES NOT HOLD. The reference is no
    difference. In the 6 variants with the pyramidal friction cone, C seats 30-31 of 45
    against 44-45 for F, H and I. Pooled: C worse on 15 scenarios, better on 0,
    p = 6.1e-05.
  - LATCHING GOOD PARTS, C AGAINST F: DOES NOT HOLD. The reference is C below F.
    C is below F in 9 of 12 variants; 10 are needed. Pooled, C is still below F (13 / 27
    scenarios, p = 0.038 *), and variant 0 has C below F too (1 / 9, p = 0.021 *). So
    the C-below-F result is not confirmed on every simulator. It is not reversed either:
    C is ahead of F in only one variant.
  - LATCHING GOOD PARTS, C AGAINST I: NOT RESOLVED (LOW POWER). C is below I in 9 of
    12 variants. Variant 1 reverses (I seats 18 of 50).
- Of the 20 secondary comparisons, 14 hold and 6 do not:
  - J against C, on bad units (c_favourable, neutral, all good parts) and on neutral
    success;
  - G (pinned, configuration of this run) against C, on c_unfavourable and on latching
    success.

Bad units and bad parts
- C'S BAD-UNIT LEAD OVER F, H AND I HOLDS ON BOTH MACHINES, IN ALL 12 VARIANTS
  (all_good_parts).
- C passed 1 bad unit on each machine, both in variant 10. So by rule 6, "C's zero bad
  units does not hold on every simulator". Over all variants:
    gantry, 1,820 good-part trials: C 1 (Wilson upper 0.31%), H 73, I 75, F 75.
    arm, 2,210 good-part trials:    C 1 (0.26%), H 30, I 56, F 59.
  G passed 0 on both.
- C, G, H, I and J passed 0 of 156 deliberately bad parts each on each machine
  (Wilson upper 2.40%).

VERDICTS, PRIMARY (C against F, H, I)
"Holds" is the number of variants keeping the reference, of 12. "Pooled" is the
scenario sign test over the 12 randomized variants. The full table is in TABLES.md,
"Verdicts". Columns: C vs F / C vs H / C vs I.

gantry
- c_favourable, success, ref C better: holds 12/12 / holds 12/12 / holds 12/12.
- c_favourable, bad units, ref C better: holds 12/12 for all three.
- neutral, success and bad units, ref n.s.: holds for all three.
- c_unfavourable, success, ref C worse (F, I) and C better (H): holds 12/12 for all
  three.
- c_unfavourable, bad units, ref n.s.: holds for all three.
- latching_good, success, ref n.s. (F, I) and C better (H): holds 12/12 / 12/12 / 10/12.
- latching_good, bad units, ref n.s.: holds for all three.
- all_good_parts, bad units, ref C better: holds 12/12 for all three.

arm
- c_favourable, success, ref C better: holds 10/12 / 12/12 / 10/12.
- c_favourable, bad units, ref C better: holds 12/12 for all three.
- neutral, success, ref n.s.: DOES NOT HOLD 6/12 for all three.
- neutral, bad units: holds for all three.
- c_unfavourable, success, ref C worse (F, I) and n.s. (H): holds 12/12 / 11/12 / 12/12.
- c_unfavourable, bad units: holds for all three.
- latching_good, success, ref C worse (F, I) and C better (H): DOES NOT HOLD 9/12 /
  holds 12/12 / NOT RESOLVED 9/12.
- latching_good, bad units: holds for all three.
- all_good_parts, bad units, ref C better: holds 12/12 for all three.

Bad parts, C against H and against I: holds on both machines, 0 against 0 in every
variant.

Notes
- Arm c_favourable success holds narrowly. C against F and against I is 10 of 12, the
  minimum. Variants 8 and 12 have C 2 / F 3, and the pooled test is not significant
  (8 / 7 scenarios). C against H holds 12 of 12.
- C's deficit against F and I on c_unfavourable holds in all 12 variants:
  - gantry: 8 with p < 0.05, pooled 2 / 9, p = 0.065;
  - arm: 11 with p < 0.05, pooled 1 / 13, p = 0.0018.
- Every variant 0 reproduced its reference, except gantry c_favourable G vs C.

THE ARM NEUTRAL AND LATCHING RESULTS, BY FRICTION CONE (POST HOC)
This section is post hoc. It was not pre-registered. The numbers are counted from
arm/trials.csv and gantry/trials.csv, randomized variants only.

- The variants where arm neutral fails are exactly the 6 pyramidal-cone variants: 4, 6,
  7, 8, 11 and 12. Every lost trial is on friction_1 (friction coefficient 1).
  - Pyramidal cone: C seats 1 of 90 friction_1 parts and G 1 of 90, against 89-90 of 90
    for F, H, I and J. Almost all of C's failures are aborted:time_limit; variants 6, 8
    and 12 also have protective stops and stuck_during_retract.
  - Elliptic cone: C seats 81 of 90. In variant 0, C seats 43 of 45 over neutral.
  - The gantry, with the same contact draws, has no such loss: C seats 90 of 90
    friction_1 parts under the pyramidal cone.
- Arm latching C against F also loses its direction only in pyramidal variants.
  Variants 6 and 8 are ties (8 / 8, 6 / 6) and variant 12 has C ahead 8 / 5. Arm
  mf_noise_1mm seated, out of 300:
    elliptic:  C 222, F 278, I 250.
    pyramidal: C 202, F 222, I 211.
  F loses more than C under the pyramidal cone, so the gap narrows.
- J's bad units on the arm come almost all from pyramidal variants: 30 of 1,020
  good-part trials there, against 1 of 1,020 in elliptic variants. Several are
  false_accept on nominal and lateral_3mm. On the gantry J passed 2 in all randomized
  variants.
- The pyramidal cone is one of MuJoCo's two friction-cone models, and v0.2a drew it in
  half its variants too. Both approximate Coulomb friction; neither is the more
  realistic one. benchmark_v0.2a's randomization also found D most sensitive to it.

QUESTION 2: IS C'S ZERO BAD UNITS AN ARTIFACT OF ONE CONTACT MODEL?
- By the pre-registered rule, no.
  - C passes fewer bad units than F, H and I on all good parts in all 12 variants, on
    both machines.
  - In the pooled test, C is better on both machines against F (gantry 10 / 1,
    p = 0.012 *; arm 11 / 1, p = 0.0063) and against I (10 / 1, p = 0.012 *; 9 / 1,
    p = 0.021 *).
  - Against H the pooled test is not significant (6 / 1, p = 0.12; 5 / 1, p = 0.22).
    The scenario unit has few scenarios with any bad unit.
- But C's zero is not exact on every simulator. C passed 1 bad unit on each machine,
  both in variant 10, which has the same contact draw on both machines. The TABLES.md
  table "Every bad unit C or G passed" lists both:
  - Gantry, noise_2mm trial 6: depth 14.81 mm, lateral 0.22 mm, tilt 1.48 deg,
    penetration_violation, gt_seated True, declared success. The part is seated but
    over-penetrated, which is_escape counts as a bad unit. Variant 10 has the softest
    linear servo of the draws (5.3 N/mm) and a 3.8 ms contact time constant.
  - Arm, mf_noise_1mm trial 15: depth 7.74 mm, tilt 3.11 deg against the 3.0 deg limit,
    false_accept. This is the same failure kind as G's one bad unit in benchmark_v0.2e.
- G passed 0 bad units on both machines.

SECONDARY: J AND G AGAINST C
J against C
- Gantry:
  - c_favourable success, J worse: holds 12 of 12.
  - c_unfavourable, J better: holds 11 of 12; pooled 9 / 9, not significant.
  - Neutral success does not hold: in variant 10, J false-rejected 10 of 45
    (aborted:verify_failed).
- Arm:
  - Four J comparisons do not hold: neutral success, and bad units on c_favourable,
    neutral and all good parts. J passes more bad units than C in the pyramidal
    variants (all good parts: C better on 26 scenarios, J better on 1, p = 4.2e-07).
  - Latching, J better: holds 10 of 12.

G (pinned, configuration of this run) against C
- Gantry:
  - Holds on c_unfavourable (12 of 12, pooled 8 / 0, p = 0.0078) and on latching
    (10 of 12).
  - Does not hold on c_favourable, where C is near its ceiling (42-45 of 45 in every
    variant).
- Arm:
  - Holds on c_favourable (12 of 12).
  - Does not hold on c_unfavourable (8 of 12) or on latching (8 of 12, pooled G better
    18 / 7, p = 0.043 *).
- G is pinned to a model trained on the nominal simulator. This tests that model off its
  training simulator, not G retrained per simulator.

CONTROLS (FLAGS ONLY, NOTHING EXCLUDED)
- F passed no mf_half_latched in gantry variants 3 and 10.
- F passed no mf_stubbed_terminal in arm variants 1, 2, 6, 10 and 12. The chance stated
  in advance was 0.17 per variant, about 2 of 12 expected, so 5 is more than expected.
  Contact parameters seem to change how the stubbed terminal behaves for F on the arm
  (post hoc). C, G, H, I and J passed none of these parts in any variant.
- A controller under 90% on nominal: gantry variant 10 (J, 3 verify_failed) and arm
  variant 12 (J, 3 false_accept).

WHAT THIS CHANGES, AND WHAT IT DOES NOT
- Standard suite. The v0.2a statement "C leads in all 13 simulators" is not repeated in
  this form.
  - On the high-camera-error conditions, C's success lead over F, H and I holds on both
    machines. On the arm it holds against F and I in only the minimum 10 of 12.
  - On neutral conditions on the arm, C loses a whole condition (friction_1) under the
    pyramidal cone, while F, H and I do not.
- Bad units. C's lead over F, H and I holds in every simulator on both machines. It is
  not exactly zero: 1 bad unit per machine, in one variant.
- The arm's latching "C below F". It is not confirmed per simulator: 9 of 12, one short.
  It is not reversed, and the pooled test agrees with it.
- This does not decide the pitch. Hasan decides that.

LIMITS
- Simulation only. Every limit in benchmark_v0.2e's and v0.2d's pre-registrations
  applies.
- Latch and terminal forces are not varied (defex/sim/mating.py, not MuJoCo contact).
- The controllers are told the servo draw through the fixture dynamics.
- 15-50 trials per condition per variant. The verdict count rests on 12 variants that
  share the same scenarios.
- The references come from another seed (20261130). Variant 0 reproduced each reference
  except gantry c_favourable G vs C.
- No correction for multiple comparisons. There are 98 verdicts.
- The cone split above is post hoc.
