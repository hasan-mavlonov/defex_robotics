# v0.2c: which candidate models go to the closed-loop validation (offline rule)

Written on 2026-11-01 ~00:40, after the gantry residual K=1 and K=2 models were trained and
scored on the stopping split, before any posterior, ratio, tempered or K=3 model was scored and
before any arm v2 model existed. No closed-loop run with a v2 model has been made.

Candidates trained per backend (results/v0.2c_learned_prior/train_models.sh, train_models_arm.sh):
residual K=2, residual K=3, residual K=2 tempered, posterior K=3, ratio K=3 (the posterior
K=3 network with the training offset marginal divided out), and on the gantry also residual K=1
and residual K=2 trained on C's data only (DAgger ablation, never carried forward).

Offline score: experiments.train_contact_likelihood evaluate on the stopping split (base seeds
3026-3030 of C's data and 3039-3040 of the DAgger data; integration weight 1 for every v2
model): mean grid NLL of the true mouth cell under G's combined posterior, over all
surface-block contacts. Dev seed 2026 is computed and reported but is not used for this choice.

Rule, per backend: carry the three v2 candidates with the lowest stopping-split NLL to the
closed-loop validation on seed 4002, next to C and the current G (installed v1 model). If two
candidates share the network (posterior K=3 and ratio K=3), both may be carried.
