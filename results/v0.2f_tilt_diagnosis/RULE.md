# v0.2f tilt diagnosis: keep/drop rule for the default-off options

Committed before any run with an option switched on. Written after the frozen-code (flags off) dev
collection of arm latching and latch_spread trials had been read (that is the diagnosis, not a candidate
run). Nothing below changes after the first candidate run.

## Candidates

All default OFF. With them off the code gives the v0.2e rows (proved separately in `identity/`).

| Name | Switch | Controllers | Acts where |
|---|---|---|---|
| P | `AdaptiveConfig.tilt_check_push_below_floor = True` | C, G | a latch check whose tilt window is under the 11.75 N floor or empty: first hold the plug at the proof force (C's bottom-proof push), then take the tilt verdict on that push's window |
| JP | the same switch on J's verifier config | J | the same; on J every first latch check (empty hand-over window) |
| JW | `CompliantSpiralSearchVerifyController.handover_window = True` | J | every hand-over: C's VERIFY gets F's last 25 samples (F's seat push) as its window |

No candidate for item 1 (the socket-axis reference) or item 3 (housing-only tilt): see REPORT.md.

## Trials

- Development seeds 2026 and 2027, `latching` and `latch_spread` (16 conditions), both machines.
- P: the C and G trials of `runs/*_latch_cg.jsonl.gz` (50 per condition). A trial runs exactly as with the
  switch off up to its first latch check under the floor, so only trials that have such a check in the
  flags-off rows are re-run, plus a control set of 40 trials per machine without one (they must come out
  identical; if any differs, all trials are re-run).
- JP and JW: every J trial of `runs/*_latch_j.jsonl.gz` (20 per condition).
- Validation: seed 4007, once, the same suites, 20 trials per condition, flags-off base and each kept
  candidate (P by the same re-run shortcut).

## Metrics, against the flags-off rows of the same trials

1. Bad units on good-part trials (declared seated, not seated, no protective stop; group not `bad_part`).
2. Bad parts passed (declared seated on a `bad_part` trial).
3. Good-part rejections: good-part trials not seated (`success` False).
4. Protective stops.

## Keep or drop (per candidate, per seed set)

- **Drop** if it adds any bad unit (1) or any bad part passed (2), in any cell.
- **Drop** if its net added good-part rejections (3), summed over both machines, exceed
  max(1, floor(0.001 x the good-part trials of its cells)): P 3 (3,600 good-part trials), JP and JW 1 (720).
- **Drop** if its net added protective stops (4) exceed the same bound.
- Otherwise **keep** (as an option for Hasan; it stays off). The report gives what it changed: bad units
  removed, tilt verdicts gained, cycle time.
- A kept candidate is run once on seed 4007 and must pass the same three tests there (bounds computed from
  4007's trial counts, P: max(1, floor(0.001 x 720)) = 1; JP, JW: max(1, floor(0.001 x 360)) = 1). Pass: "GO as an option". Fail:
  "NO-GO", reported as such.
- Tie-break between JP and JW if both are kept: fewer bad units on good parts, then fewer good-part
  rejections, then JW (no extra motion).
