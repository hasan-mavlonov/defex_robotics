# J's response to a failed check: selection rule

Written and committed before any run it ranks. J is F's insertion up to the tick
at which F would declare the connector seated, then C's VERIFY
(`defex/control/spiral_verify.py`). When one of VERIFY's checks fails, C's own
code retracts the plug as it does before a retry (compliance frozen, gentle
retract on latching parts). What happens next is the choice ranked here.

## Candidates

Both are registered and run under their own names:

- **(a) reject**, `spiral_rcc_verify_reject`: the part is declared failed
  (`aborted:verify_failed`).
- **(b) re-search**, `spiral_rcc_verify_research`: control goes back to F, whose
  jam retry descends again at the position it found (plus its compliance offset)
  and searches from there, inside F's own attempt budget (`max_attempts` 2 on both
  machines). A check that fails on F's last attempt rejects the part, as in (a).

Both run C's VERIFY with the two RCC terms (`rcc_terms`, see the module
docstring): the plug position given to VERIFY is the encoder position plus the
measured lateral force over the stage's datasheet stiffness (5.78 N/mm), and the
wall probe's setpoint-lead allowance grows by the stage's deflection at C's 2 N
wall force (0.35 mm). These were added after smoke trials on seed 2026 (trial
indices 0-2 of `nominal`, `noise_1mm`, `noise_2mm`, `mf_nominal`,
`mf_broken_latch`, gantry and arm) showed C's wall probe running out of travel
at 1.35 mm with 1.4-1.6 N on good parts: the stage absorbs 0.35 mm of the probe
before a wall pushes back with 2 N. Neither term has a free parameter. The same
runs include `spiral_rcc_verify_reject_no_rcc`, candidate (a) without these
terms, as an ablation; it is not ranked.

## Runs ranked

Dev seed 2026, gantry and arm, all four suites (`standard`, `latching`,
`heldout`, `latch_spread`), 20 trials per condition, both candidates in the same
run as C, F, I and the ablation (`run.sh`, section dev2026).

## Rule

Over both machines and all four suites pooled, in this order:

1. **Fewer bad units passed**: escapes on good-part conditions plus deliberately
   bad parts passed (`is_escape`: failed, no protective stop, not declared
   failed).
2. **More good parts seated.**
3. **Lower median cycle time** of the successful good-part trials.

A step decides only when the two differ; exactly equal at all three: (a), the
simpler response.

Why bad units first: on every paired trial (b) runs exactly as (a) until (a)
rejects, so (b) seats at least as many good parts by construction, and a rule
that ranked seated parts first would pick (b) as soon as one trial is rescued.
What the second search can cost is a bad unit passed on the later attempt, and
the question J answers is whether C's VERIFY on the spiral cell gives C's zero
escapes.

## Validation

After the pick is committed, both candidates (and F, for the hand-over check) run once on validation seed 4003
(same machines, suites and trials). The same rule is applied. If it ranks the
other candidate first, the pick does not change and the report says so.
Tables: `python -m experiments.v02d_j_tables results/v0.2d_j_verify`.
