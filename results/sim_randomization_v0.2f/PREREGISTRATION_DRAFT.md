# sim_randomization_v0.2f pre-registration (DRAFT)

DRAFT for the lead agent's review. Not final. Seed 20261205 has not been run. When final,
this file is renamed PREREGISTRATION.md and committed before the first trial. Nothing
below changes after that. If the run exposes a bug, the bug gets a fix, a new
pre-registration and a fresh seed. No result is read until both runs have finished. A
run that stops early is repeated with the same command, and RUN_LOG.md says so.

## Question

`results/sim_randomization_v0.2` (seed 20261108) used v0.2a code, the gantry only,
controllers A-F, untuned-since baselines and standard conditions only. It found C ahead of
the best of D, E, F by 8.3-12.5 points in all 13 simulators. Since then H and I (a pull
test) were added and the baselines changed. In benchmark_v0.2e (seed 20261130), C is
ahead of every fair baseline only on the standard suite. Its remaining edge there is
bad units: mis-seated good parts that the controller passed as good, in the
high-camera-error conditions. Over all good-part trials: C 0, H 101, I 138
(`results/benchmark_v0.2e/REPORT.md`).

This run asks two questions:

1. Do the current comparisons hold when the contact and servo parameters vary within
   plausible bands? The comparisons are success and bad units for C against F, H and I,
   and for J and G against C, on both machines.
2. Is the gap of 0 bad units for C against about 30 for H and I an artifact of one
   contact model?

It does not ask whether any rate stays the same, and it says nothing about real parts.

## Frozen code

- Controllers, simulator and conditions: unchanged since **ddd0d34** (the benchmark_v0.2e
  code). `git diff --stat ddd0d34 HEAD -- . ':(exclude)results' ':(exclude)README.md'
  ':(exclude)docs'` was empty on 4df8cae. The only code added since is this run's own:
  `experiments/sim_randomization_v02f.py`, `experiments/sim_randomization_v02f_tables.py`
  and `tests/test_sim_randomization_v02f.py`.
- Frozen commit: **[the commit that adds the final PREREGISTRATION.md; hash filled in at
  finalisation]**. The run may start from a later commit that changes only `results/`.
  Both `config.json` files must show `git_dirty: false`. RUN_LOG.md records
  `git status --porcelain --untracked-files=all` outside `results/` at the start, the
  environment and the load average.
- G's model files are unchanged: `assets/models/contact_prior_{gantry,arm}.json`, with
  sha256 as in `results/benchmark_v0.2d/PREREGISTRATION.md`.

## Simulator variants

- Base seed **20261205**. No file under `results/`, `experiments/`, `defex/`, `tests/`,
  README.md or docs/ mentions it (grep on 2026-11-02).
- 12 randomized variants per machine, plus variant 0, the nominal simulator. Variant k
  is drawn from `numpy.random.default_rng([20261205, k])`, exactly as
  `experiments/sim_randomization.py` draws it. A test checks that the new script
  reproduces `results/sim_randomization_v0.2/variants.json` for seed 20261108. Variant k
  has the same contact draw on both machines.
- Contact bands, uniform, unchanged from v0.2a (`experiments/sim_randomization.py`
  BANDS):
  - normal-contact time constant 1.5-4 ms;
  - damping ratio 0.7-1.3;
  - friction time constant 10-40 ms;
  - solimp dmin 0.90-0.97, dmax 0.98-0.995, width 0.1-0.5 mm;
  - impratio 3-20;
  - cone elliptic or pyramidal (50/50).
- Gantry servo bands, unchanged: linear stiffness 5-20 N/mm and wrist stiffness 10-25 N m/rad,
  both uniform. The damping ratio stays 1.0, as on the nominal gantry.
- Arm servo bands (new, `ARM_BANDS`). The arm has no gantry servos, so the gantry band
  cannot apply. The arm's FixtureConfig stays nominal. Three parameters are drawn from a
  separate stream, `default_rng([20261205, k, 1])`:
  - **Shoulder and elbow joint stiffness: a factor of 0.5-2** on Menagerie's
    2000 N m/rad, log-uniform.
  - **Wrist joint stiffness: a factor of 0.5-2** on Menagerie's 500 N m/rad,
    log-uniform, drawn separately.
  - **Command latency: 4-8 ms**, uniform. Nominal is 6 ms.

  Why these choices:
  - The factor 0.5-2 spans the same range around nominal as the gantry's 5-20 N/mm
    around 10 N/mm.
  - Log-uniform puts the median at Menagerie's model. Universal Robots publishes no
    joint stiffness, so Menagerie's values are a modelling choice, not a measurement.
  - Each joint's damping is scaled by the square root of the factor, so its damping
    ratio stays Menagerie's. This matches the gantry, which keeps its dampratio fixed
    when its stiffness is drawn.
  - The latency band is the brief's W5 band.
  - At every corner of these bands, the controllers' arm switches (W5b
    `outside_reference_family`) stay on. A test checks this. So no controller changes
    to its gantry settings on any arm variant.
- What the controllers are told. On the nominal machines, the controllers receive the
  drawn servo stiffness and latency through the fixture dynamics the backend reports. In
  the variants they receive them the same way, as a cell integrator would know its own
  servo gains. They are not told the contact parameters.
- No variant is excluded, for any reason.

## G in the variants

G looks up its learned model by the fixture dynamics, within 1%. In every randomized
variant the servo draw changes those dynamics, so the lookup as built finds no model and
G runs exactly as C. A test checks this on a development draw. So this run pins G to its
machine's one nominal model whatever the fixture reports (`--g-model pinned`,
`fixture_match_rel_tol = inf`). This tests G's model trained on the nominal simulator
when it runs on other simulators. On variant 0 the pinned G gives the same rows as G in
experiments.robustness (equivalence check below).

## Conditions

These are exact names from `python -m experiments.robustness --suite S --list`. The
groups were fixed before any run on seed 20261205, from where C stood in benchmark_v0.2e.

| Group | Suite | Conditions | Trials per condition per variant |
|---|---|---|---|
| c_favourable | standard | `noise_1mm`, `noise_2mm`, `generalization_combined` | 15 |
| neutral | standard | `nominal`, `lateral_3mm`, `friction_1` | 15 |
| c_unfavourable | heldout | `heldout_worst_case`, `heldout_handeye_bias_1.5mm` | 15 |
| latching_good | latching | `mf_noise_1mm` | 20 |
| bad_parts | latching | `mf_half_latched`, `mf_broken_latch`, `mf_stubbed_terminal` | 4 each |

Notes on the conditions:

- `mf_nominal` and `mf_moderate` are left out. In benchmark_v0.2e, C, F, H, I, J and G
  seated 200 of 200 of each on both machines, except H at 199 on `mf_moderate`. They
  have almost no discordant pairs, so they could not change any comparison.
- `mf_wrong_polarization` is left out. No controller passed it in benchmark_v0.2e.
- `mf_broken_latch` is included because a pull test is what rejects it. Housing
  friction is the contact-model term most likely to let a part without a latch hold
  under the pull.
- The terminal and latch forces come from `defex/sim/mating.py`. They are not
  MuJoCo contact, so this run does not vary them. Mating-value spread is
  `latch_spread`'s question, not this run's.

## Controllers

C `adaptive`, F `spiral_rcc`, H `spiral_pull`, I `spiral_rcc_pull`, J
`spiral_rcc_verify`, G `adaptive_learned` (pinned). D and E are not run. The rules below
compare C with each of F, H and I separately, so no "best fair baseline" has to be chosen
after the run.

## Trials and compute

- Per machine and variant: 8 x 15 + 20 + 3 x 4 = 152 trials per controller.
- Per machine: 152 x 6 controllers x 13 variants = 11,856 trials. Both machines: 23,712.
- Timing on development seed 2026: variants 0-3, all 13 conditions above plus
  `mf_moderate`, 3 trials each, 6 controllers, `--workers 4`, 936 trials per machine.
  - Gantry: 160 s.
  - Arm: 357 s, 2.24 times the gantry's summed trial time.
  - On the arm, the randomized variants took 1.26-1.48 times variant 0's time.
  - Other agents were running at the same time: load average 22-37 on 10 cores. A
    quieter machine may be faster.
  - Files: `dev_timing/{gantry,arm}/run_time.json` and the `wall_time_s` column of
    `trials.csv`.
- Estimate, from the randomized variants' mean time per trial per condition:
  - gantry 30 min;
  - arm 72 min;
  - **about 102 min** at `--workers 4` under the same load.
- More trials per condition or more variants? We chose the trials per condition first,
  then the number of variants:
  - **The decision rule is per variant.** It asks whether each simulator keeps the
    comparison's direction, so each variant needs enough trials for its direction to
    be reliable. The power table below shows 15 trials per housing condition is the
    smallest count at which every C comparison with a clear benchmark effect has under
    5% chance of failing from trial noise alone. At 10 trials, four of them reach
    10-16%.
  - **Variants are not the limiting factor for the pooled test.** Every variant reuses
    the same scenarios, so the pooled test's unit is the scenario. More variants do not
    add scenarios.
  - **12 variants keeps v0.2a's threshold** (more than 2 of 12 failing) and covers the
    10-parameter band at the density v0.2a used. 10 variants would take about 94 min.

## Commands

```
PY=python   # ~/projects/defex_robotics/.venv/bin/python, from the repository root
CELLS=standard:noise_1mm:15,standard:noise_2mm:15,standard:generalization_combined:15,\
standard:nominal:15,standard:lateral_3mm:15,standard:friction_1:15,\
heldout:heldout_worst_case:15,heldout:heldout_handeye_bias_1.5mm:15,\
latching:mf_noise_1mm:20,latching:mf_half_latched:4,latching:mf_broken_latch:4,latching:mf_stubbed_terminal:4
for B in gantry arm; do
  $PY -m experiments.sim_randomization_v02f --backend $B --variants 12 --seed 20261205 --workers 4 \
    --g-model pinned --cells $CELLS \
    --controllers adaptive,spiral_rcc,spiral_pull,spiral_rcc_pull,spiral_rcc_verify,adaptive_learned \
    --name sim_randomization_v0.2f/$B
done
$PY -m experiments.sim_randomization_v02f_tables results/sim_randomization_v0.2f \
  > results/sim_randomization_v0.2f/TABLES.md
```

Committed after the run: `{gantry,arm}/trials.csv`, `summary.csv`, `config.json`,
`variants.json`, `run_time.json`, TABLES.md, RUN_LOG.md and REPORT.md.
`events.json.gz` is kept locally and committed only if a reported number needs it.

## Equivalence check (done, development seed 2026)

Variant 0 must give rows identical to experiments.robustness for the same seed,
conditions and trials. The check used:

- conditions `noise_2mm`, `generalization_combined` (standard), `heldout_worst_case`
  (heldout), `mf_noise_1mm` and `mf_half_latched` (latching);
- the six controllers, G pinned;
- 5 trials each, both machines.

Result: 150 of 150 rows identical on each machine. Every robustness field was compared
as text, except wall time (`dev_equivalence/EQUIVALENCE.txt`). Commands:

```
for B in gantry arm; do
  for S in standard:noise_2mm,generalization_combined heldout:heldout_worst_case latching:mf_noise_1mm,mf_half_latched; do
    $PY -m experiments.robustness --suite ${S%%:*} --backend $B --trials 5 --seed 2026 --workers 4 --no-plots \
      --controllers adaptive,spiral_rcc,spiral_pull,spiral_rcc_pull,spiral_rcc_verify,adaptive_learned \
      --conditions ${S##*:} --name sim_randomization_v0.2f/dev_equivalence/robustness_${B}_${S%%:*}
  done
  $PY -m experiments.sim_randomization_v02f --backend $B --seed 2026 --only-variants 0 --workers 4 \
    --controllers adaptive,spiral_rcc,spiral_pull,spiral_rcc_pull,spiral_rcc_verify,adaptive_learned \
    --cells standard:noise_2mm:5,standard:generalization_combined:5,heldout:heldout_worst_case:5,latching:mf_noise_1mm:5,latching:mf_half_latched:5 \
    --name sim_randomization_v0.2f/dev_equivalence/v02f_$B
  $PY -m experiments.sim_randomization_v02f --equivalence results/sim_randomization_v0.2f/dev_equivalence/v02f_$B \
    results/sim_randomization_v0.2f/dev_equivalence/robustness_${B}_{standard,heldout,latching}
done
```

A slow test (`tests/test_sim_randomization_v02f.py::test_variant_zero_rows_equal_robustness_rows`)
repeats the check on a smaller slice.

## Metrics

All are paired: the same (condition, trial index) in the same variant. Trial rows record
`success`, `declared_success`, `gt_seated`, final depth, lateral offset, tilt and yaw, and
the variant's drawn parameters as `sim_*` columns.

- **Success**: on good-part conditions. "X better on a trial" means X seated the part
  and Y did not.
- **Bad units**: a bad unit is a trial that failed, was not stopped by the protective
  stop, and was not declared failed. This is `is_escape`, as in benchmark_v0.2e
  metric 5. On good-part conditions it is a mis-seated good part passed as good. On
  `bad_parts` it is a bad part passed. "X better on a trial" means Y passed a bad unit
  there and X did not.
- **Variant test**: for X against Y in one group and variant, exact two-sided McNemar on
  (X-better, Y-better). The class is:
  - "better": p < 0.05 and X-better > Y-better;
  - "worse": p < 0.05 and X-better < Y-better;
  - "n.s." otherwise.

  There is no 1-point margin in either direction.
- **Pooled test** over the 12 randomized variants. The unit is the scenario,
  (condition, trial index), because every variant reuses the same scenarios. For each
  scenario, take the number of variants where X did better minus the number where Y did
  better. Then run an exact sign test (McNemar on the counts) over the scenarios where
  that is not zero. The class is the same as for the variant test.
- **Groups**: c_favourable, neutral, c_unfavourable and latching_good for success and
  bad units. For bad units only, also `all_good_parts`, the union of the four, and
  `bad_parts`.
- **Comparisons**:
  - primary: C against F, C against H, C against I;
  - secondary: J against C, G against C;
  - on `bad_parts`: C against H and against I (primary), J against C and G against C
    (secondary).
- **Reference class**: the class of the same comparison on the same conditions in
  benchmark_v0.2e. That run used seed 20261130 and 100 trials per standard or heldout
  condition, 200 per latching condition. The references are computed by
  `python -m experiments.sim_randomization_v02f_tables --references results/benchmark_v0.2e`
  and committed in `REFERENCES.md`. The directional ones:

| Machine | Group | Metric | Comparison | Reference (X-better / Y-better in v0.2e) |
|---|---|---|---|---|
| gantry | c_favourable | success | C vs F, H, I | C better (53/8, 54/6, 53/8) |
| gantry | c_favourable | success | J vs C; G vs C | J worse (10/26 *); G better (17/0) |
| gantry | c_favourable | bad units | C vs F, H, I | C better (32/0, 29/0, 32/0) |
| gantry | c_unfavourable | success | C vs F, I; C vs H | C worse (5/44); C better than H (35/17 *) |
| gantry | c_unfavourable | success | J vs C; G vs C | J better (45/8); G better (35/2) |
| gantry | latching_good | success | C vs H; G vs C | C better (70/6); G better (13/3 *) |
| gantry | all_good_parts | bad units | C vs F, H, I | C better (33/0, 31/0, 33/0) |
| arm | c_favourable | success | C vs F, H, I | C better (53/10, 69/11, 53/10) |
| arm | c_favourable | success | J vs C; G vs C | J worse (11/39); G better (16/0) |
| arm | c_favourable | bad units | C vs F, H, I | C better (32/0, 22/0, 32/0) |
| arm | c_unfavourable | success | C vs F, I; G vs C | C worse (13/45); G better (23/5) |
| arm | latching_good | success | C vs F, I | C worse (18/37 *, 19/37 *) |
| arm | latching_good | success | C vs H; J vs C; G vs C | C better (83/6); J better (38/18 *); G better (26/1) |
| arm | all_good_parts | bad units | C vs F, H, I | C better (37/0, 23/0, 37/0) |

\* 0.01 <= p < 0.05 in benchmark_v0.2e. Every other comparison has reference "n.s.".
That includes every bad-units comparison on neutral, c_unfavourable, latching_good and
bad_parts, every J-vs-C and G-vs-C bad-units comparison, and success on neutral.

## Decision rules, fixed in advance

Applied by `experiments/sim_randomization_v02f_tables.py`, per machine, group and
comparison.

1. **The comparison holds in variant k** when:
   - for a "better" reference: X-better > Y-better in that variant (same direction);
   - for a "worse" reference: X-better < Y-better;
   - for an "n.s." reference: the variant's class is "n.s.".

   A tie (X-better = Y-better, including 0 = 0) does not hold a directional reference.
   Per-variant significance is not required: a variant has 20-140 pairs, against
   200-1,200 in the benchmark. Two more counts are reported but do not enter the
   verdict:
   - variants that hold with p < 0.05 ("confirmed");
   - "departing" variants: the opposite significant class for a directional
     reference, or any significant class for an "n.s." reference.
2. **Bad units** are compared with exactly the same rule, on the bad-unit pairs. For
   C 0 against I 3, that is X-better 3 and Y-better 0. That holds a "C better" reference
   whatever the p.
3. **The comparison holds across simulators** when both of these are true:
   - **(a)** it holds in at least **10 of the 12** randomized variants (at most 2
     fail, the v0.2a threshold);
   - **(b)** the pooled test is not the opposite class (directional reference) or is
     "n.s." ("n.s." reference).

   Otherwise it **does not hold**. Variant 0 is not counted. If variant 0 itself does
   not hold, the table marks it "not reproduced". The verdict is applied as written all
   the same, and the report says the departure may come from the seed or from this n
   rather than the physics.
4. **Low power, stated before the run.** For each directional reference, the tables
   compute the chance that trial noise alone fails rule 3(a). That assumes every variant
   had the benchmark's per-trial X-better and Y-better rates at this run's n
   (`POWER.md`). Where that chance is over 0.2, a "does not hold" is reported as **"not
   resolved (low power)"**, never as evidence that the comparison failed or reversed. A
   "holds" is reported as "holds". At the planned trials these are:
   - gantry c_favourable J vs C (0.45);
   - gantry c_unfavourable C vs H (0.48);
   - gantry latching_good G vs C (0.87);
   - arm latching_good C vs F (0.67), C vs I (0.72) and J vs C (0.63).

   So **the arm's latching "C below F" cannot be resolved per variant at this
   budget**: it needs about 100 trials per variant. Every other primary directional
   comparison has under 0.04.
5. **What is reported when a comparison does not hold:**
   - It goes in the report's first paragraph if it is primary.
   - The failing variants are listed with their drawn parameters, and so are departing
     variants with their p.
   - Any statement about what the failing variants have in common (cone, servo
     stiffness, ...) is labelled post hoc every time it is quoted.
   - No variant is excluded, and no band, seed or condition is changed to make it hold.
   - A "C better" reference that does not hold counts against C.
   - A "C worse" reference that does not hold (gantry and arm c_unfavourable against F
     and I; arm latching, if resolved) is reported in C's favour in the same words.
6. **Question 2, the zero bad units.** The answer is the `all_good_parts` bad-unit
   comparisons C against H and against I on each machine, by rules 1-4. In addition,
   C's bad units over all good-part trials of all 13 variants are reported per machine:
   - the count;
   - the Wilson 95% upper bound;
   - the number of variants with any.

   Every bad unit C or G passes is listed with its trial, variant and final pose
   (TABLES.md, "Every bad unit ..."). If C
   passes any bad unit in a randomized variant, the report says "C's zero bad units
   does not hold on every simulator", whatever rule 3 gives.
7. **Bad parts.** C, G, H, I and J are expected to pass 0. Any pass by any of them is
   listed with its trial and variant. C against H and I uses rules 1-3 (reference
   "n.s.", 0 against 0).

   F's bad parts passed, per variant and type, is a positive control. Without a pull
   test F passes most bad parts, so it shows that each defect still produces a part
   that looks seated. A variant and type where F passed none of its 4 is flagged "F
   passed no <type>". This is descriptive, not an exclusion. At F's benchmark_v0.2e
   rates this happens by chance:
   - arm `mf_stubbed_terminal` (72 of 200): 0.17 per variant;
   - gantry `mf_half_latched` (131 of 200): 0.015.
8. **Sanity flag (no exclusion).** A variant where some controller seats under 90% on
   `nominal` is flagged in the controls table.
9. **No multiple-comparison correction.** There are 98 verdicts: per machine,
   4 groups x 2 metrics x 5 comparisons + 5 + 4. Pooled p-values at
   0.01 <= p < 0.05 are marked. Totals pooled over machines are descriptive.
10. **Symmetry.** Every rule is the same whether C is X or Y and whether the reference
    favours C or not. The rules can come out against C in three ways:
    - C's success lead (c_favourable) or bad-unit lead (all_good_parts) fails in more
      than 2 variants;
    - the pooled test reverses;
    - C passes a bad unit.

    They can come out for C in two ways:
    - C's deficit against F and I on c_unfavourable fails;
    - G's or J's gains over C fail.

## Expected from development, stated so they are not found later

- Development (seed 2026, variants 0-3, 3 trials per condition, `dev_timing/`) is too
  small to predict verdicts. It is used for timing only. Three things were seen there
  (`python -m experiments.sim_randomization_v02f_tables results/sim_randomization_v0.2f/dev_timing`):
  - **Bad units.** C and G passed no bad unit on either machine (108 good-part trials
    each). F passed 4 and 5, I 4 and 5, H 1 on the gantry, and J 1 on the arm.
  - **Bad parts.** Only F passed any.
  - **Gantry variants 2 and 3.** F passed 0 of 3 `mf_half_latched` there, against 3 of
    3 on variants 0 and 1. On variant 2 (pyramidal cone, 5.1 N/mm linear servo), J
    false-rejected one `nominal` part (`aborted:verify_failed`). These were not used to
    change any band or condition.
- benchmark_v0.2a's randomization found D the most simulator-sensitive, mostly under
  the pyramidal cone. D is not in this run.

## Disclosed before the run

- **Simulator only.** Everything disclosed under "Disclosed before the run" and "Known
  limits" in benchmark_v0.2e's and benchmark_v0.2d's pre-registrations applies.
- **G is pinned to its nominal model.** As built, G would run as C on every randomized
  variant. The pinned G is a configuration choice of this run, not of the frozen code.
  On variant 0 it is identical to G.
- **The controllers know the servo draw** through the fixture dynamics, as on the
  nominal machines. A result under "controllers told the nominal servo values" would
  need a code change and is not run.
- **The arm servo band is new.** It was chosen before any run on 20261205, for the
  reasons above, without looking at any outcome.
- **Latch and terminal forces are not varied** (`defex/sim/mating.py`, not MuJoCo
  contact).
- **The groups and their names come from benchmark_v0.2e's outcomes.** The lead agent
  specified them: C-favourable, neutral, C-unfavourable. Each group is tested alone. No
  verdict pools across groups except `all_good_parts` for bad units, which is fixed
  above.
- **The references are on the same conditions but a different seed.** The scenarios
  differ. Variant 0 shows whether this seed reproduces each reference.
- **Seed reuse**: development seed 2026 has been used for every v0.2 decision.
