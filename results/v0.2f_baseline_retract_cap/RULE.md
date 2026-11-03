# v0.2f baseline retract cap: decision rule

Written and committed before any run of the capped baselines. Not changed after.

## Why

`results/v0.2f_realtime/REPORT.md` (part 2) found that C caps any retract pull on a
latching part at 36 N (`AdaptiveConfig.retract_pull_cap_fraction` 0.75 x the 48 N
protective stop, the "gentle retract"), and D, F, H and I have no cap. On development
seed 2027 H's retry retract tore the latch of two good gantry parts (`mf_noise_1mm`,
trials 17 and 19; hook 58.5 and 59.1 N) and loaded a third to 54.1 N (seed 2026, trial 7).
This is an equal-effort item: the brief counts a weak baseline as a failed deliverable.

## The change (one candidate)

`SpiralSearchConfig.retract_pull_cap` (default **off** until this rule says keep). On a
latching connector (mating spec with a retention force, the same test as C's
`latching`), with the cap value computed exactly as C's: `retract_pull_cap_fraction`
(read from `AdaptiveConfig`) x the connector force budget's `protective_stop_n`
(fallback, never used on the Micro-Fit: C's `max_force_n x retract_stuck_force_factor`).
On the Micro-Fit that is 0.75 x 48 = 36.0 N for every controller.

- Retry retract (after INSERT's or the floor check's jam/limit abort, `_jam_or_fail`): if
  the tared axial force pulls harder than the cap, stop pulling and hold the plug where it
  is. The first time in a trial, push it back and run INSERT's seat rule again (H and I
  then run their latch check, as after any seat), as C re-seats a held plug and checks
  the latch once per cycle. A second hold fails the part as `stuck_during_retract`,
  plug left in place.
- Failure retract (any abort): a pull past the cap stops the retract and leaves the
  plug in place, as C's failure retract does.
- The guarded pulls of H and I's latch check (35.2 N target) are not retracts and are
  not capped, as C's own latch-check pull is not.
- D, F, H and I get the flag on both machines (gantry config and the arm's
  `stiff_fixture_cfg`). **J** runs F's insertion with F's config, so the flag reaches
  J's F phase (its retry retract and failure retract before the hand-over); J's VERIFY
  is C's code with C's own cap, unchanged.

## Development runs (seeds 2026 and 2027 only)

Suites `latching` and `latch_spread`, machines `gantry` and `arm`, 20 trials per
condition, controllers D, F, H, I, J uncapped (v0.2e code) and capped (`X@cap`, the
variant `{"retract_pull_cap": true}` in `variants.json`), all in the same run so every
pair is the same trial. 2 seeds x 2 suites x 2 machines x 10 controllers x 16 conditions
x 20 = 12,800 trials. Folders `dev/<machine>_<suite>_s<seed>`.

Pairs are compared by `experiments/v02f_retract_cap_compare.py` (written before the
run). A cell = machine x suite x controller, both seeds pooled.

## Keep criteria (all must hold, on every cell)

1. **No new torn latch**: no trial in which the capped controller ends with a broken
   latch (`final_latch_intact` False) and the uncapped one does not.
2. **No new bad unit**: no good-part trial that is an escape (failed, no protective
   stop, not declared failed) for the capped controller and not for the uncapped one.
3. **No new bad part passed**: the same, on the deliberately bad parts.
4. **Success**: on good parts the capped controller seats at most 2 fewer than the
   uncapped one in the cell (net: uncapped successes minus capped successes <= 2).
5. **Identity**: every row (every `trials.csv` column except `controller` and
   `wall_time_s`) is identical between the pair wherever the capped trial has no
   cap trip (no `gentle_retract` event that the uncapped trial does not also have; J's
   VERIFY logs C's own). Any difference there is a bug: it is fixed, and the rule is
   applied to a new run of the fixed code; no decision is made on the buggy run.

D, F, H and I are judged together: the cap is kept only if all four pass every cell
(the same rule for every fair baseline). If any of the four fails, the cap is dropped for
all, the flag stays off, and the fairness item stays open, with the failing cells named.
J is judged by the same criteria; if D, F, H and I pass and J fails, the flag is on for
D, F, H and I and off for J (J keeps the v0.2e insertion), and this is reported.

## Validation (once, after a keep on development)

Seed **4008** (fresh, given to this agent; not in any `config.json` under `results/`),
the same suites, machines, controllers, 20 trials per condition (6,400 trials), the same
five criteria applied to the same cells. If it passes, the flag defaults on in a
commit after the validation. If it fails, the cap is dropped and nothing else is tried
on this seed. No tuning on either seed: the cap value and the behaviour above are
fixed by C's code.

## Reported either way

Per cell: trials with a trip, good parts seated, latches torn, bad units, bad parts,
protective stops, and each tripped trial's outcome uncapped and capped
(`TABLES.md`, `trips.csv` in each run folder). `events.json.gz` is not committed;
`trips.csv` holds the trip events the numbers need.
