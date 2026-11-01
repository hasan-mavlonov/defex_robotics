# v0.2c defect verdict: selection rule (committed before the validation runs)

Choice: how many identical pieces of evidence the defect verdict needs before C (and G, which
inherits C's configuration) declares a latching part defective.

Candidates (AdaptiveConfig values; everything else at the branch defaults):

| Name | defect_verdict | hard_stop_repeats | no_retention_repeats |
|---|---|---|---|
| off | False (C as at Checkpoint 2) | - | - |
| r2 | True | 2 | 2 |
| r3 | True | 3 | 3 |

Data: validation seed 4002 (not used for anything else on this branch), latching suite (all 7
conditions), 20 trials per condition, gantry and UR5e arm, each candidate on C and on G
(`variants.json`, `experiments/v02c_variants.py`). Paired trials.

Rule, on results pooled over both backends and both controllers (840 trials per candidate):

1. A candidate that passes any bad part as good (`is_escape` on the four bad-part conditions)
   is out.
2. Good-part success (mf_nominal, mf_moderate, mf_noise_1mm; 240 trials per candidate): more is
   better, but a candidate whose difference from the best is not significant (paired exact
   McNemar p >= 0.05 against the best) counts as tied with it.
3. Among those tied: higher good units per hour over the whole latching suite, counting every
   cycle plus 60 s per protective stop.
4. Then lower median cycle time of good-part successes, then lower p95.

The chosen candidate becomes (or stays) the default. Wilson 95% intervals and McNemar p for
each candidate against `off` are reported with the choice. If `off` wins, the verdict is left
off by default and the report says so.
