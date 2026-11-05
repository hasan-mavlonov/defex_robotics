# v0.2g rig prep: cheapest rig for the housing-only power analysis

Prepared for Hasan's review. Nothing was bought and nobody was contacted. Choosing a rig,
spending money and sending any draft are Hasan's decisions (ASK HASAN). This folder adds
files only; it does not change hardware/BOM.md or anything else.

Files:
- `BOM_PRICE_CHECK.md`: every BOM line rechecked on 2026-11-05, with sources and the
  totals per rig option.
- `QUOTE_DRAFTS.md`: unsent quote requests for ATI, Bota, Franka, a machine shop, and an
  optional technical question to Zaber.

## What the power analysis needs

`results/v0.2f_checkpoint/CHECKPOINT_REPORT.md` (item 7) and `hardware/RIG_POWER.md`:
C against I on the rig's four housing-only conditions (nominal, lateral_3mm, noise_1mm,
noise_2mm) needs, for 80% power with the exact McNemar test at simulation rates:
- success: 70 paired trials (gantry) or 100 (arm);
- bad units passed: 90 (gantry) or 100 (arm).

These are paired trials pooled over the four conditions, so about 23-25 per condition.
`hardware/TEST_PROTOCOL.md` plans 100 per condition (400 per controller), which leaves
margin if the rig's rates differ from the simulation's. On this part I and F are the same
program (TEST_PROTOCOL.md section 2), so one RCC run scores both.

So the rig needs only the housing-only part. It must still have:
- a rigid wrist for C and a passive RCC for I;
- a 2 ms control period (TEST_PROTOCOL.md section 1);
- an F/T range of at least 56.25 N axially to read the housing-only part's 45 N damage
  bound (45 / 0.8), with about 0.1 N resolution;
- a socket jig that sets x, y, yaw and tilt per trial;
- the final-pose measurement of TEST_PROTOCOL.md section 5 (laser heads, a camera pair,
  a go/no-go gauge), because C's measured edge over I is bad units seated 3-5 deg off.

## The cheapest rig that meets this on paper

**Option 1, the desk gantry, with a Bota MiniONE Gen A: $23,333 for the priced core**
(Zaber stages $19,600 + sensor CHF 3,045 = $3,733; BOM_PRICE_CHECK.md section 8). It is
also the rig the simulator models, so it compares with the `gantry` predictions, which
need the fewest trials (70 and 90).

With price indications for the lines BOM.md left unsourced (all from search snippets,
low confidence; BOM_PRICE_CHECK.md sections 5-6):

| Line | Price |
|---|---|
| Zaber stages: 2 x X-LSM100A, X-LRQ150AL-DE51, X-GSM40, X-GSM60, X-RSW60A-E03 | $19,600 |
| Bota MiniONE Gen A (Fz 100 N, 800 Hz) | $3,733 |
| Calibration certificate (optional) | $1,349 |
| ATI RCC 9116-001-A (current version of 9115-001-A) | not public, quote |
| Manual two-axis tilt for the socket (Thorlabs GNL20 pair) | $356 (S) |
| Manual XY table and rotary for the socket | not priced |
| 4-6 laser triangulation heads (Panasonic HG-C1030 class) | $2,436-3,654 (S) |
| Two cameras (FLIR Blackfly S class) | $2,610 (S), lenses not priced |
| Housing-only plug and socket pairs | not public, quote |
| Go/no-go gauge, reference plug, gauge blocks | not priced |
| Zaber power supplies and cables, frame, PC, gripper | not priced (the BOM has no gripper) |
| **Priced total** | **about $28,700-30,000** without the certificate |

Two conditions on this choice:
1. **Zaber loop rate.** Zaber publishes no 500 Hz external command rate (BOM.md). My
   estimate, not measured: at 115,200 baud a short ASCII command and its reply take about
   3.5 ms per axis, so six axes on one serial chain would update near 50 Hz. Draft 5 in
   QUOTE_DRAFTS.md asks Zaber. If they cannot reach 500 Hz, this option fails the
   protocol's 2 ms period.
2. **Goniometer load.** The X-GSM stages are rated 30 N, which equals the housing-only
   protective stop. The 3-8 N push and C's 20 N abort are inside the rating. A transient
   above the stop, or the 45 N damage bound, is not. For the Micro-Fit they do not fit at
   all.

If the Zaber answer is no, the cheapest priced rig with a published loop rate of 500 Hz
or more is **a Franka Research 3 with a Bota MiniONE Gen A: $32,951 core** ($29,218 +
$3,733), or about $38,400-39,600 with the same jig and measurement indications. FCI
licence status is not stated by Vention (draft 3). The Franka is not the modelled arm, so
its comparison uses the `arm` rows labelled "different arm" (100 paired trials for both
endpoints). The UR3e option is $39,898 core and Vention now marks the UR3e "Obsolete".

The UFactory 850 option is cheaper ($12,732 core at UFactory's own price, S), but its
servo mode tops out at 250 Hz, so it does not meet the 2 ms period. It is cheapest only
if Hasan accepts a slower loop, which the frozen predictions did not assume.

## Lead times

- In the cheapest rig, the longest published lead time is the **Bota sensor: 3-5 weeks**.
  Zaber stages: 1-10 days.
- Not published, and possibly longer: the ATI RCC and the machined housing-only part.
  Both need quotes.
- Longest anywhere in the BOM: the **UFactory 850, 2-3 months** (BOM.md, not re-confirmed;
  the page did not load). If the Micro-Fit is added, a search snippet lists 7 weeks for
  the 43045-0429 header and 11 weeks for the 43030-0001 terminals at the factory, both
  with stock on hand.

## Decisions for Hasan

1. **Option.** Gantry (matches the simulator, cheapest, depends on Zaber's loop rate), or
   Franka FR3 (published 1 kHz loop, about $9,600 more for the core, not the modelled
   arm), or relax the 2 ms period and use the UFactory 850.
2. **Budget ceiling.** About $29-30k for the gantry rig and $38-40k for the Franka rig,
   plus the quoted lines (RCC, test parts) and the unpriced ones (frame, PC, gripper,
   power supplies, XY table and rotary).
3. **Target connector.**
   - Housing-only part only: enough for the C vs I power analysis. Needs the machined part
     (draft 4).
   - Add the Micro-Fit: rates only, no between-controller claim (it needs 780 or more
     paired trials). It needs a sensor with at least 72.5 N axial range, tilt stages that
     carry 48 N (the X-GSM do not), Molex parts and a crimp tool, and the pull and
     continuity checks. The RCC's 22 N tension rating is below the 29 N pull test.
   - The pilot customer's part: needs its own connector file and a new pre-registered
     prediction before any rig run.
4. **F/T sensor.** MiniONE Gen A is the cheapest priced sensor that fits both parts.
   ATI Mini40 SI-40-2 also fits both, price on quote. Mini40 SI-20-1 and MiniONE Pro fit
   the housing-only part only, and the MiniONE Pro cannot read up to the 45 N damage
   bound.
5. **Calibration certificate** for the Bota sensor (CHF 1,100), yes or no.
6. **Which drafts to send, and when.** None has been sent.
