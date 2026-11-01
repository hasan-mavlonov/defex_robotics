# Latch-spread check of the Checkpoint 2 code (development)

The v0.2c fairness review (`v0.2c/review-fairness` a55be7b, dev seed 2026) found
that C's latch check uses the connector file's *assumed* latch geometry, the same
values the simulator builds every part from, so the dev seeds cannot show what a
part-to-part spread does. This repeats the check on the Checkpoint 2 code
(883db25, the code of benchmark_v0.2b) on dev seed 2027, which the review did not
use. Development measurement; tables in `tables.md`
(`python -m experiments.latch_spread_tables`); commands in `run.sh`.

The only change is a simulator-side hook in `defex/sim/mating.py` (environment
variables, off by default, copied from the review branch): it shifts the latch
onset, peak and snap depths, scales the latch peak force, or scales the terminal
friction. The controllers keep the connector file's values.

## Result

| Simulated part | C good seated (gantry / arm) | F good seated (gantry / arm) | C bad passed | F bad passed |
|---|---|---|---|---|
| as modelled | 54 / 52 of 60 | 53 / 57 | 0 / 0 of 80 | 51 / 59 |
| latch snaps 0.1 mm earlier | 57 / - | 53 / - | 0 / - | 42 / - |
| latch snaps 0.15 mm earlier | **4 / 30** | 53 / 57 | 0 / 0 | 42 / 59 |
| latch snaps 0.2 mm earlier | **1** / - | 53 / - | 0 / - | 39 / - |
| latch snaps 0.2 mm later | 56 / - | 53 / - | 0 / - | 59 / - |
| latch peak force x0.5 / x1.5 | 57 / 57 | 53 / 53 | 0 / 0 | 43 / 59 |
| terminal friction at the datasheet maximum (8 N per circuit) | 0 / 0 | 0 / 0 | 0 / 0 | 54 / 54 |

- **C's good-part success collapses if the latch engages 0.15 mm earlier than the
  model assumes.** Most of those cycles end in a protective stop (53 of 56 gantry
  failures): the pull test allows only the assumed 0.5 mm post-snap stroke plus
  0.3 mm, so a good, latched part fails it, and retracting it against the latch
  trips the 48 N stop. F does not depend on the latch geometry.
- **C's "click" check does not see the latch.** Its window (1.6 to 0.3 mm above
  the floor) contains the terminal-friction drop of 8 N on every part, so it
  passes even on broken-latch parts. In practice C rejects bad parts with the pull
  test alone (code reading, `_click_in_trace` in `defex/control/adaptive_fsm.py`;
  the review counted a click on 40 of 40 broken-latch checks).
- **At the datasheet's maximum terminal force no controller can seat the part**:
  four terminals need 32 N and every controller's insert budget is 30 N. The
  latching results hold only for the modelled friction.
- **C passes 0 bad parts in every spread.** But only C and G run a retention test
  at all; D, E and F check depth only. The bad-part gap measures having a pull
  test, which a conventional cell could also add. That was not measured.

## What this means for benchmark_v0.2b

The pre-registered numbers stand as measured, but two readings of them do not:

1. "C passes far fewer bad parts than a conventional cell" is a comparison of a
   cell with a pull test against cells without one.
2. C's latching good-part rate depends on the simulated part matching the assumed
   latch geometry to within about 0.1 mm. A real part may not.
