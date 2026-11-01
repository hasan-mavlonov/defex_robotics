# v0.2c: closed-loop selection of G's contact model (written before any validation run)

Written 2026-11-01 ~01:10. No closed-loop run with any v2 model, and no run on seed 4002 of
any kind, has been made. Seed 4001 is not used. Selection is per backend; the gantry and the
arm may pick different models.

## Variants (each run as `experiments.eval_learned_prior`, paired, same scenarios)

- `adaptive`: C.
- `g_v1`: the current G, the installed v1 model (byte copy in `models/v1_contact_prior_<backend>.json`), weight 1.
- three v2 candidates, chosen by `OFFLINE_RULE.md` (lowest stopping-split grid NLL at weight 1):
  - gantry, known at writing: `gantry_residual_k2_tempered` (1.940 nats) and `gantry_residual_k2`
    (2.547). The third is `gantry_residual_k3` if its stopping-split NLL is below 2.805
    (`gantry_posterior_k3`), otherwise `gantry_posterior_k3`.
  - arm: the three lowest of `arm_residual_k2`, `arm_residual_k3`, `arm_residual_k2_tempered`,
    `arm_posterior_k3`, `arm_ratio_k3` on the arm stopping split, by the same score.
  Every v2 candidate runs at integration weight 1 (the weight it was trained or built for).

## Runs, base seed 4002

- Ranking families, 100 trials each: gantry noise_0.5mm, noise_1mm, noise_2mm, mf_noise_1mm
  (400 trials per variant); arm the same plus friction_1 (500).
- Safety: the latching suite without mf_noise_1mm (mf_nominal, mf_moderate, mf_half_latched,
  mf_broken_latch, mf_stubbed_terminal, mf_wrong_polarization), 30 trials each.

## Rule, per backend

1. Gate: a v2 candidate is eligible only if it passes 0 bad units (escapes) over all its 4002
   runs (ranking families and safety suite).
2. Rank the eligible v2 candidates and `g_v1` on the ranking families pooled: most successes,
   then lower median cycle time of successes, then lower p95 cycle time of successes.
3. The top v2 candidate replaces the installed model only if it ranks above `g_v1`. Otherwise
   the v1 model stays installed and the report says the new models did not beat it.

Reported for every variant: successes with the 95% Wilson interval, paired exact McNemar p
against C and against `g_v1`, bad units, protective stops, median and p95 cycle time.
Protective stops are reported but are not part of the rule.

## After selection (a check, not a choice)

Dev seed 2026, 60 trials per condition, C, `g_v1` and the chosen variant: gantry noise_0.5mm,
noise_1mm, noise_2mm and the whole latching suite; arm the same plus friction_1. If the v1
model stays, this check is not run for that backend.
