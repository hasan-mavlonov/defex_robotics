# v0.2c: a better learned contact prior for G (development, both backends)

These are development measurements in simulation on branch `v0.2c/learned-prior`, which starts from 54f3097. All paths are relative to `results/v0.2c_learned_prior/`. Commands, in order, are in `commands.sh`.

Seeds:
- Run: 2026 (dev), 3033-3040 (new training data), 4002 (selection).
- Read from existing data files: 3001-3030 (training data) and 2026.
- Not run and not read: 4001, 3031, 3032, and every reserved seed.
- No file under `results/benchmark_v0.2b` was read. I only listed which summary files existed, to see when the benchmark had finished.

## Result

The pre-registered rule (`SELECTION_RULE.md`) installed a new model on both backends:
- On the gantry, the gain over the current G is small and not significant.
- On the arm, the gain is inside noise on the selection seed and reverses on the dev seed.
- The new models are better calibrated offline, but that did not give a clear closed-loop gain.

| Backend | Seed | C | current G (v1) | chosen v2 | v2 vs v1: v1-only / v2-only (McNemar p) | Stops C / v1 / v2 |
|---|---|---|---|---|---|---|
| gantry | 4002, 400 trials (selection) | 374 | 382 | **389** (residual K=2) | 4 / 11 (0.12) | 4 / 5 / 1 |
| gantry | 2026, 600 trials (check) | 349 | 355 | 355 | 3 / 3 (1) | 21 / 35 / 26 |
| arm | 4002, 500 trials (selection) | 391 | 413 | **417** (residual K=3) | 13 / 17 (0.58) | 18 / 23 / 24 |
| arm | 2026, 660 trials (check) | 357 | 375 | 372 | 7 / 4 (0.55) | 12 / 16 / 19 |

Sources: `validation/gantry/tables.md`, `validation/arm/tables.md`, `dev2026/gantry/tables.md`, `dev2026/arm/tables.md`.

Only one variant passed a bad unit, and the safety gate excluded it (below). Against C, the chosen models are ahead on both seeds:
- gantry: 7 / 22 (p 0.008) on 4002;
- arm: 6 / 32 (p 2e-5) on 4002, and 4 / 19 (p 0.003) on 2026.

The v1 models are ahead of C as well.

**Gantry: residual K=2 is installed.**
- It seated 7 more units than v1 on the selection seed (not significant) and the same number on the dev seed.
- It had fewer protective stops on both seeds: 1 against 5, and 26 against 35.
- p95 cycle time is higher on 4002 (13.51 against 12.03 s) and lower on 2026 (10.71 against 11.36 s).
- Median cycle time is 0.13 s longer on 4002 (7.51 against 7.38 s).

**Arm: residual K=3 is installed because the rule picked it (417 against 413).**
- The gain is not established.
- On the dev seed it seated 3 fewer units than v1 and had 3 more protective stops (19 against 16; 5 against 3 of them on wrong-polarization parts).
- I followed the pre-registered rule rather than overriding it after the fact on the dev seed.
- My recommendation: treat the arm change as no improvement. Restoring the v1 arm model is one copy: `models/v1_contact_prior_arm.json` to `assets/models/contact_prior_arm.json`.

**Best arm variant by seating rate, excluded.** Posterior K=3 seated 425 of 500 on 4002 (v1-only / K=3-only 5 / 17, p 0.017). It passed one bad unit: noise_2mm trial 80, seated 3.14 deg off in tilt at 14.67 mm depth and declared good. The gate excluded it.

**The tempered model** (it learns a temperature on C's posterior) was by far the best calibrated offline. It did not help in closed loop: gantry 379 against 382 for v1, arm 415 against 413.

## What was built

**1. v2 model format** (`defex/recovery/contact_likelihood.py`, numpy and JSON only).
- Same network body as v1: a tanh MLP on 38 translation-invariant contact features.
- The head is a mixture of K Gaussians over the plug-to-mouth offset (x, y), plus a uniform floor `e` that is fitted with the network. v1 copied C's 0.1 instead.
- G evaluates the term on the localizer's own grid and adds it (`HoleLocalizer.update_log_term`).
- Modes:
  - `posterior`: trained alone, like v1.
  - `ratio`: a posterior model with the training offset marginal (a 2-component Gaussian mixture) divided out.
  - `residual`: trained against C's own posterior. C's analytic localizer posterior is rebuilt from the trial's records; the replay matches C's recorded posterior mean to within 4e-15 mm on every C contact. The loss is the grid NLL of the true mouth cell under `normalize(C posterior + g)`, including the model's own terms for the trial's earlier contacts, as at run time.
  - `residual --temper`: also fits a temperature tau on C's posterior, and G applies `log_post <- tau * log_post + g` at each contact. Fitted tau: gantry 0.68, arm 0.50.

**2. DAgger-style re-collection.** The current G (v1 models) ran on training seeds 3033-3040 with the W9 families and trial counts, labelled offline:
- gantry: 1,040 trials, 2,236 records;
- arm: 1,360 trials, 3,088 records.

These were added to C's 3001-3030 data.

**3. One model per fixture.** `find_model` now refuses more than one matching `contact_prior_*.json`. The installed files replace the v1 files in place. The v1 models stay reproducible as byte copies in `models/v1_contact_prior_{gantry,arm}.json`, together with their W9 and Checkpoint 2 recipes.

**4. Seed guards.**
- `collect_contacts` (also used by `eval_learned_prior`) now runs only 2026, 2027, 3001-3030, 3033-3040 and 4002.
- 4001, 3031 and 3032 are refused, and 20261116 was added to the reserved list.
- The training script refuses to read 4001, 3031, 3032 or any reserved seed.

**5. Scripts.**
- `experiments/train_contact_likelihood.py`: fit, evaluate, to-ratio, install.
- `experiments/v02c_tables.py`: Wilson intervals; McNemar against C and the current G; pooled run parts, with a check that trials repeated across parts are identical.

**6. Tests** (`tests/test_contact_likelihood.py`, 11 tests).
- Finite-difference gradients of the grid loss for K=1 and K=3, the floor and the temperature.
- Density normalization, and the ratio-model marginal requirement.
- G with a v2 model, and weight 0 equals C.
- Two matching models are refused.
- The floor keeps a confident wrong term from erasing the truth.
- Tempered training is reproducible.
- The import-boundary test now also covers the new module, and the installed-model tests accept v2 files.

Full suite: 110 passed.

## Offline: G's combined posterior (`offline/tables.md`)

How to read the table:
- Every row uses integration weight 1.
- C's row is its analytic posterior alone. Every other row is C's posterior plus that model's terms along the recorded probes.
- "Next probe in capture": the fraction of contacts where C's own `best_probe`, run on that posterior, lands inside the lead-in capture region of the true mouth.
- Dev 2026 holds C's contacts only and was not used for any choice.

| Backend, dev 2026 | Grid NLL (nats) | Mean error (mm) | Outside 50% HPD (exp. 0.50) | Outside 95% HPD (exp. 0.05) | Next probe in capture |
|---|---|---|---|---|---|
| gantry C | 4.263 | 1.75 | 0.49 | 0.237 | 0.471 |
| gantry v1 (current G) | 3.278 | 1.20 | 0.73 | 0.380 | 0.693 |
| gantry residual K=2 (installed) | 2.750 | 1.26 | 0.67 | 0.277 | 0.734 |
| gantry residual K=2 tempered | 1.879 | 1.37 | 0.55 | 0.113 | 0.723 |
| gantry posterior K=3 | 2.344 | 1.07 | 0.69 | 0.299 | 0.752 |
| arm C | 6.982 | 1.83 | 0.67 | 0.504 | 0.432 |
| arm v1 (current G) | 4.637 | 1.11 | 0.75 | 0.496 | 0.699 |
| arm residual K=3 (installed) | 3.275 | 0.92 | 0.75 | 0.368 | 0.794 |
| arm residual K=2 tempered | 2.094 | 1.20 | 0.57 | 0.107 | 0.716 |
| arm posterior K=3 | 2.946 | 0.74 | 0.75 | 0.414 | 0.809 |

What this shows:
- Every v2 model has a lower combined NLL than v1 on dev.
- v1's combined posterior is the most overconfident: 38% (gantry) and 50% (arm) of true mouths fall outside its 95% region.
- Only the tempered models come near calibration (0.11 outside 95%).
- C's own posterior is badly overconfident on later contacts, especially on the arm (0.50 outside 95%). A term that can only multiply C's posterior cannot fix that; tempering it can.
- Calibration did not buy better probes: the tempered models' next-probe rates are no better than v1's.
- More mixture components helped the residual mode. On the gantry stopping split: K=1 2.865, K=2 2.547, K=3 2.626 nats.
- The DAgger data helped a little: residual K=2 on C data only scored 2.619 (stopping split) and 2.951 (dev), against 2.547 and 2.750 with the DAgger data.
- The ratio model scored worse than the posterior model it was built from on every split.

Caveat: the stopping split includes C's seeds 3026-3030, on which v1 was trained, so v1's stopping-split numbers are in-sample. Dev 2026 is out of sample for every model.

## Selection, seed 4002 (`validation/`)

Order of the rules:
- `OFFLINE_RULE.md` was committed before any posterior, ratio, tempered or K=3 model was scored, but after the gantry residual K=1 and K=2 scores were known.
- It carried the three v2 models with the lowest stopping-split NLL to closed loop: gantry tempered K=2, residual K=2 and residual K=3; arm tempered K=2, posterior K=3 and residual K=3.
- `SELECTION_RULE.md` was committed before any 4002 run.

Runs: the ranking families at 100 trials each, and the latching safety suite (without mf_noise_1mm) at 30 trials each.

**Gantry** (400 ranking trials and 180 safety trials per variant):

| Variant | Successes (95% CI) | Bad units | Stops | Median / p95 cycle (s) | vs C (p) | vs v1 (p) |
|---|---|---|---|---|---|---|
| C | 374 (90.6-95.5%) | 0 | 4 | 7.04 / 15.08 | - | 17 / 9 (0.17) |
| v1 | 382 (93.0-97.1%) | 0 | 5 | 7.38 / 12.03 | 9 / 17 (0.17) | - |
| residual K=2 tempered | 379 (92.1-96.5%) | 0 | 3 | 7.20 / 11.53 | 11 / 16 (0.44) | 10 / 7 (0.63) |
| **residual K=2** | **389 (95.1-98.5%)** | 0 | 1 | 7.51 / 13.51 | 7 / 22 (0.008) | 4 / 11 (0.12) |
| residual K=3 | 388 (94.8-98.3%) | 0 | 3 | 7.51 / 13.26 | 6 / 20 (0.009) | 7 / 13 (0.26) |

Gantry safety suite:
- Every variant seated 60 of 180 and passed 0 bad units.
- Stops (half-latched and wrong-polarization parts): C 13, v1 17, tempered 15, residual K=2 13, residual K=3 13.

**Arm** (500 ranking trials and 180 safety trials per variant):

| Variant | Successes (95% CI) | Bad units | Stops | Median / p95 cycle (s) | vs C (p) | vs v1 (p) |
|---|---|---|---|---|---|---|
| C | 391 (74.4-81.6%) | 0 | 18 | 9.30 / 19.79 | - | 28 / 6 (0.0002) |
| v1 | 413 (79.0-85.7%) | 0 | 23 | 9.54 / 19.73 | 6 / 28 (0.0002) | - |
| residual K=2 tempered | 415 (79.5-86.0%) | 0 | 22 | 9.55 / 21.15 | 8 / 32 (0.0002) | 12 / 14 (0.85) |
| posterior K=3 (excluded) | 425 (81.6-87.9%) | **1** | 19 | 9.73 / 19.69 | 3 / 37 (2e-8) | 5 / 17 (0.017) |
| **residual K=3** | **417 (79.9-86.4%)** | 0 | 24 | 9.55 / 20.21 | 6 / 32 (2e-5) | 13 / 17 (0.58) |

Arm safety suite:
- Every variant seated 59 of 180 and passed 0 bad units.
- Wrong-polarization stops: C 0, v1 0, tempered 1, posterior K=3 1, residual K=3 4.

Applying the rule:
- The gate excludes posterior K=3.
- Arm: residual K=3 (417) ranks above tempered (415), which ranks above v1 (413). Residual K=3 replaces v1.
- Gantry: residual K=2 (389) ranks above residual K=3 (388), which ranks above v1 (382). Residual K=2 replaces v1.

## Equivalence (`equivalence/`)

**Rule-5 set.** Seed 2026, all seven controllers: noise_1mm, noise_2mm and friction_1 at 10 trials, plus the latching suite at 5 trials, i.e. 455 trials per backend. It ran on the untouched 54f3097 (`before_*`) and again after installing the new models (`after_install_*`, commit 10e8dd7). Results are in `comparison_install.txt`:
- A-F and C: 0 differences on both backends.
- G: differs on 18 of 65 gantry trials and 21 of 65 arm trials. This change is intended.

**G with the v1 model is unchanged by the v2 code.**
- On dev 2026, this branch's C and v1-G against the Checkpoint 2 prep runs: 0 differences on 240 gantry and 660 arm trials per controller (`dev2026_vs_cp2_{gantry,arm}.txt`).
- In the 4002 runs, C was re-run in every part and checked identical: 1,580 trials.

**Reproducibility.** Retraining the installed gantry model from scratch with the logged command gives bit-identical weights (`repro_check.txt`).

## What got worse or is open

- **Arm stops.** More protective stops with the installed model: 24 against 23 on 4002, 19 against 16 on dev 2026, mostly on wrong-polarization parts. The success gain is not established.
- **Gantry cycle time.** Median cycle time is up 0.13 s on 4002. The p95 is up on 4002 and down on 2026.
- **Calibration did not pay off in closed loop.** The tempered models fixed the overconfidence of the combined posterior offline, yet they only drew level with v1 in closed loop.
- **The best-seating arm model passed a bad unit**, a tilted seat that VERIFY did not catch.
- **One DAgger round only.** The re-collection used v1-G, not the models now installed.
- **Process deviations.**
  - The tempered and K=3 candidates were added after the first gantry K=1/K=2 stopping scores were seen, though before `OFFLINE_RULE.md` and before any closed-loop run.
  - Three trainings were killed (no traceback, memory pressure) and re-run with identical commands (`train_rest.sh`, `gantry_rest.sh`).
  - For about 10 minutes I ran 4 heavy processes while the benchmark was still running, and for about 20 minutes after it finished.

## Recipe (re-collect and retrain on the integrated C without new choices)

1. **C data**, per backend, as in W9 / Checkpoint 2 (`collect_contacts --controller adaptive`):
   - train_main: seeds 3001-3030, 40 trials each, on noise_1mm, noise_2mm and mf_noise_1mm, plus friction_1 on the arm;
   - train_noise05: noise_0.5mm, 10 trials each;
   - dev_seed2026: the families at 60 trials, for reporting only.
2. **DAgger data**: `collect_dagger.sh`. G with the then-installed models, seeds 3033-3040, same families and trial counts.
3. **Train**: `python -m experiments.train_contact_likelihood fit --backend <b> --mode residual --components <2 gantry | 3 arm> --weight-decay 1e-3 --sources "<C data root>:train_main,train_noise05;<v0.2c data root>:dagger_g_main,dagger_g_noise05" --name <name>`. Fixed settings:
   - inputs: the 38 `contact` features;
   - network: tanh 32x32;
   - optimizer: Adam, lr 3e-3, batch 128, numpy seed 11;
   - early stopping: patience 30 epochs, at most 300;
   - splits: fit 3001-3025 + 3033-3038, stop 3026-3030 + 3039-3040;
   - floor: fitted, initial value 0.1, never below 1e-3;
   - grid: the localizer's (0.25 mm, +/-7 mm).
4. **Install**: `python -m experiments.train_contact_likelihood install --model <file> --result <table>`. A changed integrated C changes the posterior the residual model is trained against, so retrain before installing.
5. **Compare**: to compare with this report, run `validate.sh` on a fresh seed (not 4001 or 4002).
