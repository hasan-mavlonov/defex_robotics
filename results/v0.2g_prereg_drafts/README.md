# v0.2g draft pre-registrations

**DRAFTS, not frozen. Hasan decides whether to run either. Nothing has been run.** No
seed was spent. Every number comes from committed results; the power numbers come from
`POWER.md`, made by `PYTHONPATH=. python results/v0.2g_prereg_drafts/power_v02g.py`
(reads trials.csv only, no simulation).

**`C_DESIGN_ROUND.md`.** A C design round on the four failures the v0.2f checkpoint
diagnosed: a VERIFY depth hold and re-check (F/T drift), a wall-probe stop on a wall
signature (arm friction 1.0), jam-branch progress after repeated same-probe attempts
(plug offset in the fingers), and a socket-axis reference for the tilt check. Each change
gets its diagnosis, candidates, a development protocol on seeds 2026 and 2027, a keep
rule and common no-harm bounds, the seeds its diagnosis replayed (so it is judged only on
fresh seeds), and the equal-effort question. Three of the four are VERIFY changes, so J
gets them too, and they do not separate C from J. The benchmark runs C, C2, D, E, F, H, I,
J and J2 on every suite plus heldout2 at 100 trials and an arm friction extension at 400.
There are up to 4 Holm-corrected primary tests. If a change fixes half its cases, power is
0.94-1.00 at alpha 0.05 and 0.79-1.00 under Holm. The core plan is about 29 CPU hours, about 3.3 h at 9 workers. The
fourth change has no outcome test, because C's tilted bad units are already near zero.

**`BASELINE_FAIRNESS_RUN.md`.** A benchmark entry for the two fairness items being built
today: seat-and-align (K = I plus the step, K2 = F plus the step) and a gentle retract
for D, F, H and I. Parameters are placeholders until those branches decide by their own
rules. Each item needs a validation seed before it can enter. The primary tests are K
against I on bad units and C against K on seated, standard suite, per machine, plus torn
latches for H against H with the gentle retract. A scenario from the committed rows: if K
seated every part where I passed a bad unit, C's arm standard lead would go to about zero,
and its gantry lead would shrink to about 1.07% against 0.35% of trials. The full plan is
about 43 CPU hours, about 4.8 h at 9 workers. That is over the brief's 4-hour line. The
gentle-retract test rests on 2 torn development trials and may be too weak.

## Decisions for Hasan before either can be frozen

Both drafts:
- [ ] Go or no go for each draft. Run them separately, or run the fairness baselines inside
      the design-round benchmark.
- [ ] Assign fresh seeds: V and B (design round), V2 and B2 (fairness), or one shared pair.
      4008 and 20261210 are unspent and reserved; no draft assigns them.
- [ ] Approve the CPU plan where it crosses the 4-hour line, or choose a cut (fewer
      latching trials, old `heldout` at 50, dropping A, B and G).
- [ ] Keep committing `events.json.gz` or not (checkpoint open question 6). Some
      development keep rules need event counts.

Design round:
- [ ] Which of the four changes are in scope.
- [ ] Whether C may be told an in-hand uncertainty (change 3c). If yes, every baseline is
      told the same.
- [ ] Whether to add a heldout3 (new families written before development) for a clean
      out-of-family test. Without it, the F/T drift and grasp families are development
      families at the benchmark.
- [ ] The no-harm bounds and keep thresholds in sections 3-4 (proposals until a RULE.md
      is committed).
- [ ] Whether G, A and B stay in the controller list. G is not changed in this round.
- [ ] If a change fails validation: re-validate the rest on another fresh seed, or
      disclose that the remaining combination was not validated as a whole.
- [ ] Whether to fund the runner change for an arm pyramidal-cone check at seed B.

Fairness run:
- [ ] Accept K and K2 as fair baselines (they must use nothing from C's VERIFY).
- [ ] Accept the gentle-retract pick, if one is proposed, as a baseline motion change.
      The lead approved it for development seeds only; entering a benchmark is your call.
- [ ] Latching at 400 trials (GR1 power 0.93 if half the tears are prevented) or 200
      (0.38).
- [ ] Primary comparator for GR1: H (proposed) or D.

## Files

- `C_DESIGN_ROUND.md`, `BASELINE_FAIRNESS_RUN.md`: the drafts.
- `POWER.md`: discordance rates, power scenarios, CPU per trial.
- `power_v02g.py`: makes `POWER.md` from committed trials.csv.
