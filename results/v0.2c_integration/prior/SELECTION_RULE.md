# v0.2c integration: retraining G's contact model on the integrated C (rule written before any run)

Written 2026-11-01, before any contact data was collected with the integrated C, before any
model was trained on it, and before any seed-4002 run with such a model. Nothing here is new:
it is the learned-prior workstream's recipe and rules (`results/v0.2c_learned_prior/REPORT.md`,
"Recipe"; `OFFLINE_RULE.md`; `SELECTION_RULE.md`), applied to the integrated C. Where those files
leave something open, the choice is stated here, in advance.

## Data (outputs under `results/v0.2c_integration/prior/data/<backend>/`)

- C (integrated, `--controller adaptive`), as W9 / Checkpoint 2:
  - `train_main`: seeds 3001-3030, 40 trials each; gantry noise_1mm, noise_2mm, mf_noise_1mm; arm the
    same plus friction_1.
  - `train_noise05`: seeds 3001-3030, noise_0.5mm, 10 trials each.
  - `dev_seed2026`: seed 2026, 60 trials, gantry noise_0.5mm, noise_1mm, noise_2mm, mf_noise_1mm;
    arm the same plus friction_1. Reported only.
- DAgger: G with the models installed at the start of this step (the learned-prior workstream's
  `gantry_residual_k2` and `arm_residual_k3`, trained on Checkpoint 2's C), run on the integrated
  code, seeds 3033-3040, same families and trial counts (`dagger_g_main`, `dagger_g_noise05`).

## Candidates (per backend, the recipe's fixed hyperparameters; models under `prior/models/`)

residual K=2, residual K=3, residual K=2 tempered, posterior K=3, ratio K=3 (from the posterior K=3
network). Residual K=1 and the C-only ablation are not trained: the learned-prior rules never
carried them forward.

## Offline rule (as `OFFLINE_RULE.md`)

Score: mean grid NLL of the true mouth cell under G's combined posterior on the stopping split
(3026-3030 of the C data, 3039-3040 of the DAgger data), integration weight 1. Carry the three
lowest-scoring candidates per backend to seed 4002. Dev 2026 is reported, not used.

## Closed-loop rule (as `SELECTION_RULE.md`), seed 4002

- Variants: `adaptive` (integrated C); `g_v1` (the v1 models, byte copies in
  `results/v0.2c_learned_prior/models/v1_contact_prior_<backend>.json`, the reference the rule
  names); the three carried candidates. Also run and reported, but neither a candidate nor a
  reference: `g_lp` (the learned-prior workstream's installed models, trained on Checkpoint 2's C).
- Ranking families, 100 trials each: gantry noise_0.5mm, noise_1mm, noise_2mm, mf_noise_1mm; arm the
  same plus friction_1. Safety: mf_nominal, mf_moderate and the four bad parts, 30 trials each.
- Per backend:
  1. Gate: a candidate is eligible only with 0 bad units (escapes) over all its 4002 runs.
  2. Rank the eligible candidates and `g_v1` on the ranking families pooled: most successes, then
     lower median cycle time of successes, then lower p95.
  3. The top candidate is installed only if it ranks above `g_v1`. Otherwise the v1 model is
     installed (the rule's "v1 stays installed").
- Reported for every variant: successes with Wilson 95% intervals, paired exact McNemar p against C
  and against `g_v1`, bad units, protective stops, median and p95 cycle time.

## After selection (a check, not a choice)

Dev seed 2026, 60 trials per condition, C, `g_v1` and the installed model, as `dev_check.sh`.
