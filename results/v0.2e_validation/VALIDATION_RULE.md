# v0.2e validation rule (seed 4006)

Committed before any run on seed 4006. Seed 4006 has not been used by any run.

## What is validated

The v0.2e code changes three things, each developed on seeds 2026 and 2027 only:

1. Simulator: payload and fixture dynamics are derived with the nominal grasp, not the
   previous trial's (`results/v0.2e_arm_reset`). Expected to change no outcome.
2. H and I: pull retry rule version 5, a depth gate before the second pull, lateral
   compliance in the pull, re-push and re-seat, and the pull retry counted in `retries`
   (`results/v0.2e_pull_retry`).
3. C, G and J: a force guard on the latching tilt check (`results/v0.2e_tilt_guard`).

## Runs

All ten controllers A-J, both machines, suites `standard`, `latching`, `heldout`,
`latch_spread`, 20 trials per condition, seed 4006, `--workers 9`, twice:

- `before/`: the benchmark_v0.2d code (42df5c8; run from v0.2d/integration, whose
  code is unchanged since 42df5c8).
- `after/`: the v0.2e integration code.

Pairs are matched on machine, suite, controller, condition and trial index.

## Rule, per fix

A fix is **kept** for benchmark_v0.2e unless, on its controllers (fix 1: all; fix 2: H
and I; fix 3: C, G and J), on either machine, pooled over the four suites:

- good parts seated fall, with exact McNemar p < 0.05 (after-only against before-only); or
- bad parts passed, or bad units passed on good-part trials, rise, with p < 0.05; or
- for fix 1, any outcome (success, declared success, protective stop) changes.

A fix that is not kept is reverted before the pre-registration, and the benchmark
pre-registration says so. Controllers outside a fix's list must give identical
outcomes; if they do not, the run is investigated before any pre-registration.

Everything else (seated gains, cycle times, protective stops, retries) is reported, not
used. No fix is tuned on seed 4006; if one is not kept, it is not retried on this seed.
