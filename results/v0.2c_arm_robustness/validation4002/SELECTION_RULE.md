# Selection rule: two rate-mode conform constants for C on the UR5e (validation seed 4002)

Written and committed before any trial on seed 4002 has run. Seed 4002 has not been used by any
development, training or selection step before this file.

## Question

Two constants of the W5b rate-mode conform (stiff wrists only; exact no-ops on the gantry) were left at
their W5b values: the settle threshold `rate_conform_settle_deg` (0.03 deg) and the tilt range
`rate_conform_limit_deg` (4 deg). Development traces on seed 2026 did not show a clear effect of either.
This sweep decides whether either changes.

## Candidates (AdaptiveConfig overrides on top of the committed code)

| Name | rate_conform_settle_deg | rate_conform_limit_deg |
|---|---|---|
| base (current default) | 0.03 | 4.0 |
| settle01 | 0.1 | 4.0 |
| limit6 | 0.03 | 6.0 |
| settle01_limit6 | 0.1 | 6.0 |

## Trials

Controller C (`adaptive@<name>`), arm backend, seed 4002, paired: standard suite conditions noise_1mm,
noise_2mm, friction_1 and latching suite condition mf_noise_1mm, 30 trials each (120 per candidate).

## Rule

1. A candidate with any escape (failed unit not stopped and not declared failed) is out.
2. Rank the rest by successes (more is better), then median cycle time of successes, then p95 cycle time
   of successes (lower is better).
3. A candidate other than base is adopted only if it ranks first. Report every candidate with paired
   McNemar p against base and Wilson 95% intervals, whatever wins.
