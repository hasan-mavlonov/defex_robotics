# W9: how G's model and integration weight are chosen (written before the validation runs)

Candidates: two models (input sets `contact` and `all`, each the lowest-validation-NLL
network of its grid) x integration weights 0.25, 0.5, 1.0, run paired against C on
validation base seed 4001, conditions noise_0.5mm, noise_1mm, noise_2mm, mf_noise_1mm,
60 trials each (`weights/`).

Rule, applied in order over the four conditions pooled:

1. most successes;
2. fewest bad units passed;
3. fewest protective stops;
4. lowest mean cycle time of the successful trials.

The chosen candidate is installed as `assets/models/contact_prior_gantry.json` and is the
G evaluated on development seed 2026. If no candidate reaches C's success count, the
best one is still installed and evaluated, and the report says that learning did not
help on validation. Seed 2026 is never used for a choice; the Checkpoint 2 seed is never run.
