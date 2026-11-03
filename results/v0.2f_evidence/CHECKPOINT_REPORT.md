# Checkpoint report: C's remaining edge, made exact (v0.2f)


Simulation only. This is an analysis of committed results; nothing was rerun. Sources:
benchmark_v0.2d (seed 20261123), benchmark_v0.2d_rep (20261124) and benchmark_v0.2e
(20261130). Numbers come from `experiments/v02f_evidence.py`, and each is listed in
`KEY_NUMBERS.md` with its table. Details are in `REPORT.md`.

## Result

C still leads every fair baseline only on the `standard` suite, on both machines and all
three seeds. That lead comes from three high-camera-error conditions: noise_1mm, noise_2mm
and generalization_combined (POST HOC). They hold 53 of the 53 gantry trials that C seats
and I does not, and 53 of 54 on the arm (seed 20261130). The other two seeds give the
same picture (60/60, 62/62; arm 49/51, 49/51).

More than half of those trials are ones where I declared success on a plug that was out
of tolerance (bad units): 30 of 53 on the gantry and 30 of 54 on the arm. Those bad units
are 14.4-15.0 mm deep with yaw or tilt at 3.0-5.5 deg (gantry). That puts them just past
the assumed 3 deg seating spec, on a housing-only part.

The bad-unit gap comes from C's VERIFY step, which aligns tilt and centres yaw after the
seat. J (F's insertion plus C's VERIFY) seated all 32 of F's gantry bad-unit trials, and
it passed 2 bad units in 7,400 good-part trials against F's 178. C's own insertion adds a
smaller edge over J: 32/10 on the gantry and 43/16 on the arm.

C loses to I on all three seeds in four places: the worst-case condition, the 1.5 mm
hand-eye bias, arm friction 1.0, and gantry latching with 1 mm camera noise. In each,
C runs out of retries or time, or (on the arm) hits a protective stop.

Does the bad-unit edge survive a looser seating spec? This is a POST HOC rescoring of
seed 20261130 only, from an exact replay with the per-axis offset, TCP speed and latch
flags logged. All 6,000 replayed rows match the benchmark. It is not a replacement for any
pre-registered result. With yaw and tilt allowed to 4 or 5 deg:
- I's bad units on standard fall from 32 to 8 and 3 (gantry), and from 32 to 7 and 3
  (arm). C stays at 0.
- C's standard lead over I shrinks to 31/10 and 26/10 on the gantry (p = 0.0015, 0.011).
  On the arm it shrinks to 30/17 and 27/18 (p = 0.079, 0.23), no longer significant.
- On heldout, I seats more than C as the spec loosens (gantry 23/69 at 5 deg).
- At 2 deg the lead widens: gantry 122/2, arm 119/7.
- A depth tolerance of 1.0 mm instead of 0.5 mm changes at most two trials per cell.

Full table: `TOLERANCE.md` (3) and `REPORT.md` part 3. C's slow tail is its retries,
and the retries sit in the same high-camera-error trials (`PHASES.md` (d), (d2)).

| Seed 20261130, POST HOC rescore | Yaw/tilt 2 deg | 3 deg (as run) | 4 deg | 5 deg |
|---|---|---|---|---|
| gantry standard, C-only / I-only | 122 / 2 | 53 / 8 | 31 / 10 | 26 / 10 |
| gantry standard, bad units C / I / J | 3 / 110 / 7 | 0 / 32 / 0 | 0 / 8 / 0 | 0 / 3 / 0 |
| arm standard, C-only / I-only | 119 / 7 | 54 / 16 | 30 / 17 | 27 / 18 |
| arm standard, bad units C / I / J | 1 / 107 / 5 | 0 / 32 / 0 | 0 / 7 / 0 | 0 / 3 / 0 |
| gantry heldout, C-only / I-only | 88 / 46 | 48 / 60 | 30 / 68 | 23 / 69 |
| arm heldout, C-only / I-only | 92 / 50 | 52 / 60 | 35 / 64 | 33 / 68 |

On housing-only suites F equals I. Depth tolerance 0.5 mm (as run).

## Results (seed 20261130, benchmark_v0.2e, v0.2e code ddd0d34)

Seated and p95 cycle are on `standard` (2,000 trials per machine). Throughput is good
units per hour with 60 s lost per protective stop, on `standard`. Bad parts passed are
counted over latching and latch_spread on both machines. Bad units are counted over all
7,400 good-part trials. Protective stops are counted over all 9,600 trials of each
controller. From `CHECKPOINT_TABLE.md`.

| Ctrl | Seated gantry / arm | p95 cycle (s) gantry / arm | Units/h gantry / arm | Bad parts passed | Bad units | Protective stops |
|---|---|---|---|---|---|---|
| A fixed | 24.3% / 20.9% | 4.32 / 4.32 | 21 / 15 | n/a | n/a | 7,853 |
| B correction | 86.7% / 82.2% | 4.33 / 4.33 | 275 / 212 | n/a | n/a | 2,960 |
| D spiral | 96.4% / 94.3% | 5.90 / 8.29 | 895 / 573 | 1,275 / 2,200 | 136 | 157 |
| E correction_rcc | 89.0% / 89.0% | 10.83 / 4.09 | 197 / 317 | n/a | n/a | 2,491 |
| F spiral_rcc | 96.8% / 96.2% | 4.59 / 9.94 | 1,100 / 593 | 1,510 / 2,200 | 178 | 134 |
| H spiral_pull | 96.4% / 94.3% | 5.90 / 8.29 | 895 / 573 | 0 / 2,200 | 101 | 166 |
| I spiral_rcc_pull | 96.8% / 96.2% | 4.59 / 9.94 | 1,100 / 593 | 0 / 2,200 | 138 | 136 |
| **C adaptive** | 99.0% / 98.1% | 8.65 / 13.96 | 601 / 377 | 0 / 2,200 | 0 | 104 |
| G adaptive_learned | 99.9% / 98.8% | 8.58 / 13.66 | 624 / 384 | 0 / 2,200 | 1 | 116 |
| J spiral_rcc_verify | 98.0% / 96.8% | 7.46 / 13.60 | 643 / 381 | 0 / 2,200 | 2 | 191 |

A, B and E never declare success or failure, so bad parts and bad units do not apply to
them. On standard, I and F are identical (housing-only parts have no pull), and so are H
and D. On all three seeds: C passes 0 bad units and 0 bad parts, and C makes fewer good
units per hour than F on standard (`SEEDS.md` (c)).

## Results that got worse than V0.1

V0.1 is benchmark_v0.1: seed 20261025, gantry standard only, controllers A-C. There, C
seated 1,985 of 2,000, with median 5.41 s, p95 9.87 s, maximum 27.25 s, 0 stops, 0 bad
units and 572 good units/h.

- **The size of C's lead.** V0.1 set C against B (85.9%). On the same suite, the fair
  baselines F and I now seat 96.8%. C's lead is 53 against 8 discordant trials, and it
  sits in three conditions. C's own rate is unchanged: 1,981 of 2,000, a different seed,
  not paired.
- **New suites where C is not ahead.** These suites did not exist in V0.1: heldout
  (gantry 81.4%, arm 76.8%) and latching. On arm latching, C is below F on this seed
  (18/37, all in mf_noise_1mm).
- **Protective stops: 0 in V0.1, 104 now.** None is on gantry standard. 72 are on
  deliberately bad gantry parts (half-latched 70, wrong polarization 2); F and I stop on
  115 there. 32 are on good parts on the arm (heldout_worst_case 12, mf_noise_1mm 6,
  heldout_mischar_2mm 5, friction_1 4, noise_2mm 3, generalization_tight 1), and 1 is on
  a gantry heldout part. V0.1 had no arm, no bad parts and no heldout suite.
- **Throughput against the baselines.** C makes 601 good units/h on gantry standard
  (V0.1: 572), but F and I make 1,100. Two-thirds of C's extra time over F there is
  VERIFY (1.89 s of 2.94 s). The rest is slower insertion and retries.
- **The cycle-time tail still misses the target.** On gantry standard, p95 / median is
  1.63 (V0.1: 1.82); the target is 1.5. C meets it only on gantry latch_spread (1.48).
  The tail is retries. Over the successes that did not retry, p95 / median would be 1.11.
  The retries cluster in the conditions where C wins.

## What each possible claim rests on (Hasan decides which, if any, to make)

- **"Seats more connectors than a force-controlled spiral cell."** This holds on standard
  only, on both machines and three seeds. Inside standard it comes from a camera error
  of 1-2 mm (sigma) or the combined condition. In the nominal (0.3 mm), noise_0mm and
  noise_0.5mm conditions, C and I seat exactly the same trials on every seed and both
  machines (`PERCOND.md`). On heldout and latching, a fair baseline matches or beats C.
- **"Passes no out-of-spec connector."** This rests on the assumed 3 deg seating spec
  and on C's VERIFY, which J shows another insertion can use. Fair baselines have no
  seat-and-align step; that is an open fairness item. Under a 5 deg spec (POST HOC, one
  seed), I passes 3 bad units per machine on standard instead of 32. Under a 2 deg spec it
  passes 110 and 107, and C passes 3 and 1.
- **"Rejects deliberately bad parts."** C shares this with H, I and J: each passed 0 of
  2,200 on every seed. D and F pass most of them.
- **Throughput.** On every seed and both machines, C makes fewer good units per hour than
  F and I on standard.

## Open questions for Hasan

1. The stop condition still holds. What should the pitch claim, given the above?
2. For a pilot customer: **what is the camera's real position error** (spread and fixed
   bias, in mm) at the insertion point? On standard, C's lead is in the conditions with
   camera sigma 1-2 mm, or 0.8 mm plus a 0.8 mm bias (generalization_combined). At
   0.5 mm or less, C and I seat the same trials. With a 1.5 mm hand-eye bias, C loses.
3. For a pilot customer: **what is the seating spec** for their connector? What angle and
   depth count as seated, and is acceptance by angle, by click, or by pull test? The
   3 deg used here is assumed, and the rescoring shows the bad-unit gap and the arm lead
   depend on it.
4. Does the customer's current cell already square up the part after seating? If it
   does, J-like behaviour is the fair comparison for C's VERIFY.
5. The logging needed for exact rescoring now exists (commit 9197b9c, five new
   trials.csv columns, no behaviour change). Should the next benchmark run on it, and
   should a seating spec be pre-registered as a range (for example 2-5 deg), not one
   assumed value?
6. C's tail could shrink with fewer retries, but fewer retries would cost success in the
   high-noise conditions. Is meeting the W6 target worth that? This was not tested.

## Next PRs

[Placeholder: the lead agent will add the list of branches.]
