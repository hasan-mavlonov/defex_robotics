# W9: learned contact prior, controller G (development, gantry)

Development measurements in simulation. G was trained, selected and checked
only on base seeds 3001-3030 (train), 4001 (validation) and 2026 (dev). No
reserved seed was used; `experiments/collect_contacts.py` refuses any seed
outside {2026, 2027, 3001-3040, 4001}.

## Result

G helped modestly. On dev seed 2026, which no choice was made on, the success
gain is not statistically established.

| Seed | Use | C | G | C-only / G-only | McNemar p | Mean retries C / G |
|---|---|---|---|---|---|---|
| 4001 | model, input set, grid and weight chosen here | 218 / 240 | 235 / 240 | 2 / 19 | 0.0002 | 1.48 / 1.02 |
| 2026 | dev, no choices | 229 / 240 | 235 / 240 | 3 / 9 | 0.15 | 1.14 / 0.90 |

On dev seed 2026 (`dev2026/pooled/paired.md`):

- Bad units passed: 0 for both. Protective stops: C 1, G 0.
- Retries per trial: -0.24 (95% CI -0.41 to -0.09). Cycle time where both
  succeeded: -0.41 s (95% CI -0.68 to -0.17). p95 cycle 15.2 s to 11.8 s.
- Almost all of the gain is on the Micro-Fit (mf_noise_1mm 53 to 58 of 60,
  retries -0.68, cycle -1.22 s). On the generic connector's noise families G
  and C are level (176 against 177 of 180).
- G lost 3 trials C won (noise_2mm 47 and 52, mf_noise_1mm 53), all search
  failures.

The validation gain is optimistic because every choice was made on that seed.
What G mainly fixes is C running out of search attempts: on validation,
retry-limit failures fell from 21 to 4.

## What was built

1. **Contact records in C** (`defex/control/adaptive_fsm.py`). At every DETECT
   diagnosis C stores an observation-only record: probe pose, commanded probe,
   centre of pressure, axial and lateral force, torque, depth, touch
   calibration, conform rotation and saturation, compliance offsets,
   orientation correction, the vision accuracy C is told, attempt, trigger and
   connector geometry. A hook, `_contact_prior_update`, does nothing in C. C's
   trials are field-identical with this change (equivalence below).
2. **Data** (`experiments/collect_contacts.py`). Runs C through the normal
   harness and labels each record offline with the true mouth offset (x, y,
   yaw) in C's estimated socket frame. Families: noise_0.5mm, noise_1mm,
   noise_2mm, mf_noise_1mm; a 9-family probe showed friction_0.6, friction_1,
   lateral_3mm, yaw_5deg and tilt_5deg produce no blocked contacts on the
   gantry, so G cannot differ from C there. Train 3001-3030: 3,900 trials,
   5,878 usable surface contacts. Validation 4001: 400 trials, 543. Dev 2026:
   240 trials, 274 (`data/gantry/`, collected at clean commit 1003b4d).
3. **Model** (`defex/recovery/learned_prior.py`, numpy and JSON only; trained by
   `experiments/train_contact_prior.py`). A tanh MLP with a heteroscedastic
   Gaussian head over the plug-to-mouth offset: mean (x, y, yaw), full x/y
   covariance through the precision's Cholesky factor, yaw sigma. Gaussian NLL,
   Adam, batches of 128, L2, standardized inputs and targets, early stopping on
   validation NLL, fixed seed (retraining reproduces the weights exactly).
   Gradients checked by finite differences in a test. Two input sets:
   `contact` (38 translation-invariant features) and `all` (adds probe
   position, attempt, vision sigmas and yaw correction).
4. **Controller G** (`defex/control/adaptive_learned.py`). After C's analytic
   localizer update at each surface contact, G adds
   `w * log[(1 - e) N(h; mean, cov) + e / area]` to the posterior, then C's own
   probe selection runs. e = 0.1 is C's existing `localizer_outlier_weight`,
   added after validation calibration showed heavy tails. G loads only a model
   whose stored fixture dynamics match the backend's; otherwise it runs exactly
   as C and logs "behaving as C".
5. **Wiring.** G is in the registry and the dashboards. A new
   `registry.BENCHMARK_CONTROLLERS` (A-F) is the default list for
   `robustness.py`, `baseline.py` and `sim_randomization.py`, so unqualified
   runs still contain the same cells; G is opt-in.

## Offline model quality

Mean radial error of the mouth estimate, mm. L = learned, A = C's analytic
posterior after the same contact (includes earlier contacts), V = vision.
Coverage expected 0.39 inside 1 sigma and 0.86 inside 2 sigma.
(`models/gantry_all_metrics.json`, `models/gantry_contact_metrics.json`)

| Model | Split | NLL | L / A / V, all contacts | L / A / V, first contacts | 1 sigma / 2 sigma |
|---|---|---|---|---|---|
| all (chosen) | train | 4.14 | 1.39 / 1.85 / 2.24 | 1.17 / 1.56 / 2.07 | 0.44 / 0.91 |
| all (chosen) | val 4001 | 5.15 | 1.54 / 1.93 / 2.38 | 1.26 / 1.61 / 2.15 | 0.39 / 0.78 |
| all (chosen) | dev 2026 | 8.16 | 1.49 / 1.75 / 2.20 | 1.21 / 1.42 / 1.97 | 0.31 / 0.77 |
| contact | train | 4.68 | 1.98 / 1.85 / 2.24 | 1.24 / 1.56 / 2.07 | 0.47 / 0.90 |
| contact | val 4001 | 5.47 | 2.10 / 1.93 / 2.38 | 1.33 / 1.61 / 2.15 | 0.43 / 0.83 |
| contact | dev 2026 | 7.02 | 1.88 / 1.75 / 2.20 | 1.21 / 1.42 / 1.97 | 0.44 / 0.82 |

- Yaw is barely predictable (2.20 deg error against 2.41 deg for vision on
  validation); G does not use the yaw output.
- The tails are overconfident: 5-6% of validation contacts fall beyond 3 sigma
  where a Gaussian predicts 1.1%. This is why the outlier floor is needed.

## Selection (validation seed 4001)

The rule was committed before the runs (`validation/SELECTION_RULE.md`). 240
paired trials per variant, 60 each of the four families
(`validation/weights/paired.md`):

| Variant | Successes | C-only / G-only (p) | Bad units | Stops | Mean retries |
|---|---|---|---|---|---|
| C | 218 | - | 0 | 1 | 1.48 |
| contact, w 0.25 | 234 | 0 / 16 (3e-5) | 0 | 1 | 1.19 |
| contact, w 0.5 | 231 | 2 / 15 (0.002) | 0 | 2 | 1.11 |
| contact, w 1 | 227 | 5 / 14 (0.06) | 0 | 2 | 1.11 |
| all, w 0.25 | 233 | 0 / 15 (6e-5) | 0 | 1 | 1.14 |
| all, w 0.5 | 233 | 2 / 17 (7e-4) | 1 | 2 | 1.03 |
| **all, w 1 (chosen)** | **235** | **2 / 19 (2e-4)** | **0** | **1** | **1.02** |

The top variants are within noise of each other. The chosen model is installed
as `assets/models/contact_prior_gantry.json`.

## Checks

- **Gantry equivalence** (C and F before and after all changes; fe80689 against
  5490cfb; `equivalence/comparison.txt`): seed 2026, noise_1mm / noise_2mm /
  friction_1 x 20 trials, 120 trials, 4,320 fields; latching suite x 10 trials,
  140 trials, 5,040 fields. 0 differences. All runs `git_dirty: false`.
- **Arm fallback** (`arm_fallback/`): UR5e, seed 2026, noise_1mm and noise_2mm,
  8 trials each. G against C: 16 pairs, 560 fields, 0 differences; every G
  trial logs "no model for this fixture: behaving as C". (An arm model was
  trained later, in `results/checkpoint2_prep/`.)
- **Tests**: `tests/test_learned_prior.py` (records are observation-only and
  JSON-serializable; model shapes and positive-definite precision; fixture
  matching; G equals C without a model; weight 0 is a no-op; the outlier floor
  stops a confident wrong prediction from erasing the posterior; NLL gradients
  match finite differences). The architecture test scans the new files for
  simulator imports, and a further test checks `learned_prior.py` imports only
  numpy, json and the standard library.

## Caveats

- The `all` inputs partly double-count what the localizer already holds:
  probe position and attempt reflect where C's posterior sent the probe, and
  the vision sigmas carry the camera prior. The weight and the outlier floor
  temper this. The `contact` model is the cleaner likelihood and scored 234
  against 235 on validation.
- The outlier floor e = 0.1 was added after seeing the heavy validation tails
  (dev tails show the same). It was copied from C, not tuned.
- Policy shift: the model was trained only on C's contacts, while G probes
  elsewhere after its first correction. No re-collection with G was done.
- Seed 4001 has now been used for early stopping, the grid, the input set and
  the weight, and is no longer held out. Seeds 3031-3040 were not used here.
- Labels come from the simulator. On hardware, a possible label source is the
  seated pose of a successful cycle, which locates the mouth within the
  clearance for that cycle's earlier contacts.

## Reproduce

Gantry data, training, selection and dev check (defaults write under
`results/w9_development/`; the arm equivalents are in
`results/checkpoint2_prep/commands.sh`):

```
python -m experiments.collect_contacts --backend gantry --seeds 3001 --trials 10 --name family_probe_seed3001
python -m experiments.collect_contacts --backend gantry --seeds 3001-3030 --conditions noise_1mm,noise_2mm,mf_noise_1mm \
    --trials 40 --name train_main
python -m experiments.collect_contacts --backend gantry --seeds 3001-3030 --conditions noise_0.5mm --trials 10 --name train_noise05
python -m experiments.collect_contacts --backend gantry --seeds 4001 --conditions noise_0.5mm,noise_1mm,noise_2mm,mf_noise_1mm \
    --trials 100 --name validation
python -m experiments.collect_contacts --backend gantry --seeds 2026 --conditions noise_0.5mm,noise_1mm,noise_2mm,mf_noise_1mm \
    --trials 60 --name dev_seed2026
python -m experiments.train_contact_prior --backend gantry --feature-set contact
python -m experiments.train_contact_prior --backend gantry --feature-set all
python -m experiments.eval_learned_prior results/w9_development/validation/variants.json --backend gantry --seed 4001 \
    --trials 60 --conditions noise_0.5mm,noise_1mm,noise_2mm,mf_noise_1mm --name validation/weights
python -m experiments.robustness --seed 2026 --trials 60 --conditions noise_0.5mm,noise_1mm,noise_2mm \
    --controllers adaptive,adaptive_learned --name w9_development/dev2026/standard
python -m experiments.robustness --suite latching --seed 2026 --trials 60 --conditions mf_noise_1mm \
    --controllers adaptive,adaptive_learned --name w9_development/dev2026/latching
python -m experiments.eval_learned_prior --analyze results/w9_development/dev2026/standard \
    results/w9_development/dev2026/latching --out results/w9_development/dev2026/pooled
```

The trial counts above match the committed `summary.json` of each data folder
(90, 3,600, 300, 400 and 240 trials). The flags follow the arm commands that
were logged; the gantry runs were not logged as a script.
