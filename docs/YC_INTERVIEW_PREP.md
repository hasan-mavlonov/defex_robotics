# YC interview prep: Defex Robotics (draft for Hasan)

> **Update 2026-11-06:** the company site (defexrobotics.com) has now been read. Where this file disagrees with [`YC_ANSWERS_SITE_WORDING.md`](YC_ANSWERS_SITE_WORDING.md), that file wins: the site sells a $65,000 robot (not software per cell) and says 27 factories paid to be first in line.

How to use this file:
- Draft answers come from this repo, as of commit 9aab5a6 (2026-11-06).
- Every number names its source file, so you can defend it when a partner pushes.
- `[FILL]` marks what the repo cannot tell me: team, customers, money, location. These
  are the questions YC weighs most, so fill them before you rehearse anything else.
- The technical defense (12 hard questions) is in
  [`HASAN_DEFENSE_NOTES.md`](HASAN_DEFENSE_NOTES.md). This file covers the rest of the
  interview and points there for depth.

Where the questions come from:
- The question bank in
  [surkyl/labs-yc-mock-interview-simulator](https://github.com/surkyl/labs-yc-mock-interview-simulator):
  `src/assets/data/data.yml`, 8 categories, about 150 questions, plus its tips.
- That repo's `yc-more-questions.md`, about 140 questions, which includes the full
  [iPG](https://jamescun.github.io/iPG/) list.
- [ycinsight.com/interview](https://ycinsight.com/interview): its ten practice questions,
  pasted in by Hasan, are answered in section 0b.
- ycombinator.com/interviews could not be fetched from the session that wrote this file
  (its network blocks it). Check it by hand.
- Duplicates are merged below. Every distinct question is covered once.

---

## 0. The format, and how this project is judged

- **The interview runs about 10 minutes.** Partners interrupt often and move fast. Expect
  20-30 questions, and expect each follow-up to be a sharper version of the last one.
- **Answer first, then give one sentence of context.** Aim for 10-25 seconds per answer.
  Use numbers, not adjectives.
- **Say "I don't know yet. Here's how I'll find out."** That beats a guess every time.
  Partners know robotics well enough to catch a bluff.
- **They are judging three things:**
  - Is the founder clear and fast?
  - Does the founder understand the user?
  - Is something real moving?

  On this project, the technical work answers the first well. The second and third are
  the open gaps (section 2).

---

## 0b. The ten must-answer questions (ycinsight.com/interview)

The format, per that page: a 10-minute hard cap, 2-3 partners, and a live demo you
should be ready to show. Each draft answer below is short enough to say in 10-25
seconds. Memorize the facts in it, not the wording.

### Q1. What does your company do?

> **We make software that lets robots plug in electrical connectors and prove each one
> is seated right, so assembly lines stop shipping mis-mated connectors.**

If they ask "how far along?":
> It's a simulation prototype today. In about 100,000 trials against the spiral search
> cobot vendors ship, theirs passed 138-178 crooked plugs per 7,400 as good. Ours
> passed none. Next is a real rig.

Avoid "adaptive insertion engine," "AI" and "DAIE" in the first sentence.

### Q2. Why is now the right time?

> Three things changed:
> 1. **Robots are now doing this step, and they check the wrong thing.** Cobot vendors
>    now ship connector-insertion routines: Flexiv Adaptive Assembly, Robotiq's
>    Insertion node, ABB and Nachi cells. Those routines are spiral search with a
>    depth check. The plug that goes in crooked is a new failure, and nobody owns it.
> 2. **The hardware got cheap.** A 6-axis wrist force sensor costs about $3,700 (Bota
>    MiniONE), and cobots have 500 Hz external control (UR's RTDE). Feeling a 0.5 mm
>    wall now works on a $10-35k arm (`hardware/BOM.md`).
> 3. **Simulation is now good enough to test before building.** We run 96,000 paired
>    trials per benchmark, against tuned industrial baselines, before buying any
>    hardware.

[FILL from customer calls, if you can source it: a demand shift such as EV
wire-harness volume, reshoring or a labour shortage.] Don't say "AI is hot."

### Q3. Who's your competition? Why will you win?

> 1. **Cobot vendors' built-in insertion:** Flexiv Adaptive Assembly, the Robotiq
>    Insertion node, UR force-control apps. All of them are spiral search, which is
>    exactly the baseline we benchmark against.
> 2. **Industrial connector cells:** ABB's flexible-cable cells and Nachi's
>    vision-based connector insertion.
> 3. **General-purpose robots demoing wire-harness work:** for example Sanctuary AI.
>
> And the real one: a person with a tug test.
>
> **Our wedge is the proof of seat.** It's a verification layer that sits on top of
> the spiral-search cell a customer already runs, on any robot brand. Added to a spiral
> cell in simulation, it cut escapes from 178 to 2 per 7,400 parts. Robot vendors sell
> motion. We sell "this connector is in right."

Follow-up: "Why can't Flexiv add it?" They can add a check, but not one that works
across robot brands, with per-connector force models and a failure-mode library behind
it. If we stay one feature, we lose, so we have to become the insertion layer that
integrators use across robots.

### Q4. Why you? Why are you the right team?

[FILL. This is a story, not a résumé. Structure:]
> 1. **How I got here:** [the moment you saw this problem: a factory, a job, a project].
> 2. **What I've shipped:** [the strongest thing you've built before].
> 3. **Proof of how I work, from this project:** in two weeks I took this from a first
>    simulation to six pre-registered benchmark rounds against tuned industrial
>    baselines. When the data said we were losing somewhere, I published it and
>    changed the pitch, not the numbers.
> 4. [Cofounder: how you met, what you've built together. Or, if you are solo: how you
>    cover hardware and sales, and whether you're recruiting.]

Be ready for "Who wrote the code?" If you directed AI agents, say so plainly, then
prove you own the system: whiteboard section 6.

### Q5. What's your growth?

> **Brutally honest: zero users and zero revenue. We're pre-product.**
>
> **What has grown is evidence.** v0.1 was 2026-10-24. Since then: six pre-registered
> benchmark rounds, a clean held-out test, 12 randomized simulators, and a frozen rig
> test plan.
>
> **The diagnosis:** we built the evidence before talking to customers. That's the gap
> I'm closing now.
>
> **Next targets:** [FILL: N engineer conversations by DATE, first real insertion by
> DATE, first pilot by DATE.]

Give each number with its date and how you measured it, as the page advises.

### Q6. What have you learned from your users?

The weakest answer today. Do the calls in section 4 first, then use this shape:
> Last [week], a [quality engineer at a contract manufacturer] told me [their connector
> check is a tug test plus a look, and an escape found at end-of-line test costs $X].
> So we [changed what we're building first: the verification module that sits on their
> existing cell], and now [two of them asked for a feasibility run on their part].

Have three of these, all real, all recent. If you have none on the day, say so in one
sentence:
> I haven't talked to enough users yet. Here's what the first [N] told me.

Then move to what the data taught you: spiral search fails by being confidently wrong,
not by missing the hole. A generic "users love it" is fatal.

### Q7. How big can this be?

Bottom-up, with your own numbers. The arithmetic below is **illustrative only**. Every
input is a `[FILL]` to replace with figures from your calls:
> 1. **The wedge:** [N] robot cells doing connector mating in final assembly, times
>    $[X] a year per cell licence. Example arithmetic: 10,000 cells x $10k a year is
>    $100M ARR.
> 2. **The expansion:** every contact-rich assembly step where "did it go in right?"
>    matters: connectors, clips, snap fits, fasteners, cable routing, across [N]
>    cells.
> 3. **The data layer:** every verified insertion logs a force signature as a quality
>    record. That becomes the training data for learned assembly policies.
>
> The billion-dollar path is step 2: becoming the verification layer for robotic
> assembly, not one connector app.

Don't quote a market-report TAM. Know your [N] and [X], and where each came from.

### Q8. What would you do with the YC money?

> Specifics, 6 months:
> - **Month 1:** buy the rig. The cheapest option is about $13.6k; the UR3e option is
>   about $39.8k plus the jig, measurement and parts (`hardware/BOM.md`). Make the
>   first real insertions.
> - **Months 2-3:** run the pre-registered rig test, about 3,000 insertions of four
>   controllers on two connectors, against the simulation's frozen predictions
>   (`hardware/TEST_PROTOCOL.md`).
> - **Months 3-6:** two or three paid pilots on customer connectors in their own cells.
> - **One hire:** [FILL: a robotics hardware engineer to own the rig and pilots].
> - **The rest:** [FILL: N months of runway].

No marketing team. Know your monthly burn.

### Q9. What's the hardest thing about this business?

> **Proving that it works on real parts, and that escapes cost enough to pay for it.**
> - We're slower: 5.3 s against 2.4 s per part, and 1.9 s of that is verification. The
>   pitch only works where a mis-seated connector costs much more than 1.9 s.
> - The tolerance we score against, 3 degrees, is assumed. Our edge shrinks if the real
>   spec is looser.
> - Sim-to-real is the technical risk. That's why the rig predictions are frozen before
>   the rig exists.
>
> The plan: customer calls for the real spec and the cost of an escape, then the rig,
> then pilots. Industrial sales are slow, so we go through the integrators who build
> these cells.

### Q10. If we don't fund you, what will you do?

> Keep building. I'll [FILL: self-fund / raise from angels] the cheapest rig, run the
> rig test, and get pilots. YC makes it faster. It doesn't decide whether it happens.

Never say "go back to my job."

### The live demo (be ready)

The page says to show the main user action, not slides. The main action here is a
crooked plug caught. The current video (v0.1) and `demos.run_demo` only show controllers
A, B and C, so they can't show it. A ready-made case from the benchmark:
- Gantry, `noise_1mm` trial 38, seed 20261130
  (`results/benchmark_v0.2e/gantry_standard/trials.csv`).
- I (spiral + passive compliance + pull test) declares success with the plug at
  14.83 mm and 3.67 deg yaw, a bad unit.
- C, on the identical socket and noise, seats it correctly after 2 retries.
- There are 30 such trials on that seed.

**To build:** let `demos.run_demo` take `spiral_rcc_pull` (I) and play I then C on that
trial. Rehearse screen sharing. Say "simulation" out loud before you press play.

### The page's prep checklist, mapped to this project

1. **Numbers with dates:** revenue 0, users 0. The progress numbers are the benchmark
   rounds (this file, section 1). [FILL: conversations and pilots, with dates.]
2. **One mock with follow-ups:** use section 8.
3. **Working demo:** see above.
4. **Who knows each part:** [FILL]. You must be able to explain the product end to end
   (section 6).
5. **Keep building and talking to users:** section 4. Bring any progress since the
   application, above all a first real insertion.

---

## 1. What you have, in one page (memorize this)

**What exists (simulation only, nothing on hardware):**
- DAIE is an adaptive connector-insertion controller (C), built in MuJoCo with a real
  socket cavity, noisy vision, a 500 Hz wrist F/T sensor and bounded actuators. It runs
  on two machines: a gantry and a UR5e arm model (README, "How the simulation works").
- About 9,600 lines in `defex/`, 15,400 in `experiments/` and 5,000 in `tests/`. The
  suite has 315 tests, and 170 commits since the first one on 2026-10-24 (git history).
- The benchmarks are pre-registered and paired. benchmark_v0.2e alone ran 96,000 trials:
  ten controllers, four suites, two machines (`results/benchmark_v0.2e/REPORT.md`). Two
  earlier seeds, a clean held-out test (heldout2, 8,000 trials) and 12 randomized
  simulators (26,052 trials) back it up.
- **The fair baselines are what industry ships today:**
  - force-controlled spiral search, the method in Flexiv Adaptive Assembly and Robotiq's
    Insertion node;
  - a passive RCC compliance stage;
  - both of those with C's retention pull test added (D, E, F, H, I).

  Each was tuned by a rule committed before its runs.
- A frozen rig test plan, a power analysis and a bill of materials exist. Nothing has been
  bought (`hardware/`).
- A 64 s demo video exists. It is v0.1, controllers A, B and C only
  (`demos/media/defex_daie_v01_investor_demo.mp4`).

**What the evidence says, honestly:**

| Claim | Number | Source |
|---|---|---|
| C seats more housing-only connectors than the best fair baseline, on both machines, on all 3 seeds | gantry 99.1% vs 96.8%, arm 98.1% vs 96.2% (seed 20261130) | `results/benchmark_v0.2e/REPORT.md` |
| That lead sits entirely where the camera is poor (1-2 mm error) | in nominal, 0 mm and 0.5 mm camera error, C and I seat **exactly the same trials** | `results/v0.2f_evidence/PERCOND.md` |
| C almost never passes a mis-seated good part as good | 0 of 7,400 per seed, against I 138 and F 178 | `results/v0.2f_evidence/BAD_UNITS.md` |
| That edge comes from C's VERIFY step, not its insertion | J (F's insertion plus C's VERIFY) passes 2 | same |
| The edge depends on the assumed 3 deg seating spec | at 4 deg the arm lead is not significant on any seed | `results/v0.2f_evidence/TOLERANCE.md` |
| Bad *parts* (stubbed pin, half latched) are caught by a pull test, and the baselines get the same pull | C, H, I all 0 of 2,200 | `results/benchmark_v0.2e/REPORT.md` |
| C is slower | gantry median cycle 5.30 s vs F 2.43 s; good units/h 601 vs 1,100 | `results/benchmark_v0.2e/HEADLINE_TABLES.md` (c) |
| On errors no sensor reports (heldout2), C is ahead in 5 of 10 cells and below in 3 | unseen socket yaw: 100% vs 37.5%; unseen grasp offset: 75% vs 98.8% | `results/heldout2_v0.2f/REPORT.md` |

**The one-sentence truth:** a conventional spiral-search cell gets the connector in
almost as often and twice as fast. But when the socket's position is uncertain, it
sometimes declares a plug seated when the plug is 3-5 deg crooked. Defex's verification
catches that. The depth-only checks in the routines cobot vendors ship do not.

---

## 2. What a partner will find in 60 seconds (fix or prepare for each)

Ranked by how much each one hurts:

1. **No users, no customers, no conversations on record.** The repo has none. The
   interview is weakest here. *Before the interview:* talk to 15-20 manufacturing,
   process or quality engineers (section 4) and bring back three real stories.
2. **Simulation only, and about two weeks old.** *Prepare:* the answer is the rig plan
   and its frozen predictions. A first real insertion, even on a $13.6k hybrid rig,
   would change the interview.
3. **The baseline is close, and faster.** 96.8% against 99.1%, at twice the
   throughput. *Prepare:* lead with escapes, not success rate (section 3).
4. **The key spec is assumed.** The 3 deg seating tolerance came from us, not from a
   customer. *Prepare:* ask every engineer you talk to for their real spec.
5. **Who built it.** The history shows agent-driven development (for example commit
   916d6f8, "agents could not write .md"). YC likes founders who move fast with AI,
   but it will check that you understand every part of the system. *Prepare:* be able
   to whiteboard section 6 without notes.
6. **"Is this a feature?"** A verify step could ship in a Flexiv or Universal Robots
   software update. *Prepare:* section 5, Market and Competition.

---

## 3. Positioning: the recommended story (your call)

The data supports one story much better than "a smarter insertion controller":

> **Robots can insert connectors now. What they can't do is know when they did it
> wrong.** Spiral search, what cobot vendors ship, gets the plug to depth and declares
> success. In our simulation, about 1 in 50 parts (F 178, I 138 of 7,400) is declared
> good while sitting 3-5 deg crooked, almost all when the socket position was uncertain. It passes depth, and it fails later
> at test or in the field. Defex feels the walls, squares the plug and proves the seat
> before it says "done." Bolted onto a conventional spiral cell, our verification cut
> those escapes from 178 to 2 per 7,400 parts.

Why this framing:
- **It rests on the strongest, most replicated result.** Bad units are 0 against
  138-178, on three seeds, and the gantry result holds in 12 of 12 randomized simulators
  (`results/sim_randomization_v0.2f`).
- **The J result means there is no rip-and-replace.** The verification works on top of
  the cell a customer already runs, which lowers the adoption barrier.
- **Escapes are what quality engineers pay for.** A two-point success-rate gain is not.
- **It names the customer segment.** The edge exists only when the socket's position is
  uncertain by 1-2 mm. Precisely fixtured PCBs do not need you. Final assembly does:
  connectors on boards already mounted in an enclosure, cable-to-board in appliance or
  automotive modules, high-mix lines.

The cost to face head-on: verification adds 1.9 s per part on the gantry
(`results/v0.2f_evidence/PHASES.md`). So the pitch only works where an escape costs much
more than 1.9 s of cycle time. **That number has to come from customers.** It is the
most important thing to learn before the interview.

Alternative, if customers say speed matters more than escapes: position on the heldout2
result. Defex handles unseen socket yaw and tilt that spiral search cannot (100% against
37.5%). That is one seed, and VERIFY likely carries most of it (POST HOC).

---

## 4. Before the interview: the gap-closing plan

| Priority | Do this | Why |
|---|---|---|
| 1 | Talk to 15-20 people who own a connector step: process, test or quality engineers at EMS and contract manufacturers, wire-harness shops, automotive tier-1 and tier-2, appliance makers. Also 3-5 robot integrators. | Users and traction are most of the interview. |
| 2 | Ask each one: How are connectors mated today, by hand or robot? What is your seating spec in angle, depth, click or pull? How do you catch a mis-seat, and where (in-cell, end-of-line test, field)? What does one escape cost? What is your cycle-time budget? Who signs the PO? | These answers fill sections 1-3 with real numbers and replace the assumed 3 deg. |
| 3 | Get one letter of intent, a paid pilot, or even "send me a quote." | "Who is your first customer?" needs a name. |
| 4 | Make the first real insertion: the cheapest rig option (UFactory 850 hybrid, about $13.6k, `hardware/BOM.md`), or borrow a cobot at a university or integrator. Run C and F on 20 trials. | "Have you tried it on a real robot?" is certain to come up. |
| 5 | Build a bottom-up market model from your conversations: (lines with a robot or manual connector step) x (connectors per line per year) x (your price per cell). | Do not quote a top-down TAM you cannot defend. |
| 6 | Re-cut the demo: one housing-only insertion where spiral search declares success on a crooked plug and Defex rejects and fixes it. | The v0.1 video shows the old story, a fixed program tripping a stop. |
| 7 | Fill every `[FILL]` below and rehearse out loud, interrupted, 5 times. | |

---

## 5. Questions and draft answers, by category

Format: **question** (merged duplicates in brackets), then a draft answer and the likely
follow-up. Keep each answer to 10-25 seconds when spoken.

### Product and idea

**What are you working on? / So what are you working on?**
> Software that lets a robot plug in connectors and prove they are seated right.
> Connector mating is one of the last manual steps in electronics and wire-harness
> assembly. The robots that do it today use spiral search, and they can't tell a seated
> plug from one sitting 4 degrees crooked. In about 100,000 simulated trials against the
> methods cobot vendors ship, ours passed zero mis-seated parts. Theirs passed 138-178
> per 7,400.

*Follow-up: "In simulation?"* Yes, simulation only. The rig test is designed and its
predictions are frozen. [FILL: rig status, or "first real trials on DATE"].

**Do you have a demo? / Show me the product.**
> [Recommended: the re-cut video from section 4, item 6.] Today there is a 64-second
> v0.1 video of a real benchmark trial reproduced from its seed: a fixed program trips a
> protective stop, and Defex detects, retracts, corrects and verifies on the same
> socket.

Say that it is simulation and v0.1. Do not let them think it is hardware.

**How does this actually work? / How does your product work in more detail? / Walk me
through a typical flow.** See section 6 for the 60-second version.

**Where is the rocket science? / What's technically hard? / What's your tech insight?**
> Two things. First, one blocked contact tells you where the hole is. When the plug
> lands on the face, the wrist torque gives the centre of pressure, and a forward model
> turns that into a probability map of the hole. That model matches the simulator's
> contacts to 0.07 mm on average. Second, proving a seat: we probe both walls of the
> cavity. A plug perched on a ledge or crooked in the chamfer can't push back from both
> walls.

Backup: the evaluation itself. The comparisons are pre-registered and paired, against
tuned industrial baselines, with losses published. Few robotics teams can show that.

**How is your product different? / What can you do that competitors can't? / What's new?
/ What exactly makes you different from existing options?**
> Existing insertion routines check depth. We check the seat: walls, squareness and
> yaw, and on latching parts a pull at 1.1 times the datasheet's maximum mating force.
> Depth alone passes 3-5 degree crooked plugs. We don't.

**How much better is your solution? / How much better than existing ones?**
> On escapes, near-total: 0 against 138-178 mis-seated parts per 7,400, across three
> seeds. On seating rate, small: 2-3 points, and only with 1-2 mm camera error. On speed
> we are worse, 5.3 s against 2.4 s per part.

Say the speed cost before they find it.

**Why does this need to exist? / Why hasn't someone built this before? / Why isn't someone
already doing this?**
> Vendors optimized for getting the plug in fast, and spiral search does that. The
> failure that matters is the confident wrong seat, and you can't see it with a depth
> check. Catching it takes force sensing fine enough to feel 0.5 mm walls, a 500 Hz
> external control loop, and a way to test thousands of edge cases before touching a
> line. The first two only recently got affordable.

**Why now? / What changed recently?**
> 1. Cobots with 500 Hz external control (UR's RTDE) and 6-axis F/T sensors for about
>    $3,700 (Bota MiniONE, `hardware/BOM.md`) make force-guided assembly cheap.
> 2. Simulation is now good enough to run 100,000 paired trials before buying hardware.
> 3. [FILL from customer calls: labour cost, reshoring, EV wire-harness volume.]

Only use 3 with evidence.

**What part will you build first? / What is the next step in product evolution?**
> First, the verify step as a module for an existing spiral-search cell. That is our J
> configuration, and it got most of the escape reduction. Then the rig, to prove it
> transfers. Then the full adaptive insertion for sockets whose position varies.

**How much of what you're building is AI? / Why not learning?**
> Mostly not, on purpose. The core is physics-based estimation and a state machine. We
> tried a small learned contact prior (G). It helped on 6 of 8 benchmark cells and gave
> no gain on the clean held-out test. End-to-end learned policies need real force
> traces, and we don't have those yet. Once a rig and pilots produce data, learning is
> where it goes.

Source: `HASAN_DEFENSE_NOTES.md` question 5.

**What's your unfair advantage?**
> [FILL: domain access, customer relationships, background.] Technically: a test harness
> that runs 100,000 paired trials against tuned industrial baselines in hours, so we
> find failure modes before a customer does. Example: we found and documented a
> sensor-drift failure in our own verify step before any hardware existed.

**What have you learned so far?**
> 1. Spiral search is better than people think. It is within 2-3 points of us and twice
>    as fast.
> 2. The real gap is false confidence. The baselines' failures are mostly full-depth
>    plugs just past 3 degrees.
> 3. Our own zero rests partly on a constant sensor bias. Under F/T drift on the arm we
>    passed 8 bad units, so the product needs a depth re-check.

**Could this be a feature of a bigger product? / Have you considered a variation? / What
did you cut?** See Market and Competition below: "Isn't this a feature?". Variation to
mention: verify-only as a quality gate, against full insertion. Cut so far: deformable
cables, multiple connector families and vision re-measurement (README, limitations).

**What's the single most important feature? / What do early users care about most?**
> The seat proof, so that no mis-seated part leaves the cell. [FILL: confirm from users.]

### Users and customers

**Who needs this? / Who is your user? / Who is your *actual* user? / Who buys vs who
uses?**
> [FILL from calls.] Hypothesis: the user is the manufacturing engineer who owns a
> connector-mating step at a contract manufacturer or tier-1 supplier, in final assembly
> where the socket isn't precisely fixtured. The buyer is the plant's automation or
> quality lead, often through a robot integrator.

**How do you know people want this? / How do you know customers need it?**
> [FILL: names, quotes, numbers.] Honest version today: "We haven't validated it with
> customers yet. That's what I'm doing this month. Here's what the first N told me: ..."

This is the answer to work hardest on. "Nobody yet" is survivable once. Twice is not.

**What do they do now? / What do they *really* do now?**
> [FILL.] Expected: people mate connectors by hand, then check them visually, with a
> tug test or at the electrical test station. Or a cobot runs spiral search, followed
> by a vision check or end-of-line test.

**Why is it a big problem? / How much time and money do they waste?**
> [FILL: cost per escape, rework time, warranty cost.] Without this number, the 1.9 s
> verify cost can't be justified.

**How many users / active / paying / signed up / last week / in 3 months?**
> Zero today. We are pre-product, simulation only. [FILL: target for 3 months, for
> example "2 pilot cells running".]

Say it plainly. Do not dress it up.

**Ideal customer profile / smallest viable segment / power user?**
> Final assembly with 1-2 mm socket-position uncertainty, latching or keyed connectors,
> a tight seating spec, and an expensive escape. Our data shows no advantage on
> precisely fixtured sockets.

That last sentence is a strength: it shows you know where you don't win.

**What do users dislike about current tools / what do they wish they could do / why would
they switch / what objections do they have?**
> [FILL from calls.] Expected objections: cycle time, trusting software over a vision
> check, integration effort, and "does it work on my connector?"

**Technical or non-technical users?** Technical: automation and process engineers.

**What surprised you / what are users doing that you didn't expect?** [FILL from calls.]
Without users, give a technical surprise: "Our own verify step could lift a seated plug
when the force sensor drifts. We found it on a test no one had developed against."

### Growth and traction

Almost all of these (growth rate, channels, retention, conversion, activation, virality,
funnel, churn) have the same honest answer today:

> We're pre-revenue and pre-pilot. The metric for the next 3 months is [FILL: N
> conversations, N pilots, first rig result by DATE].

Then show speed: v0.1 to v0.2f in about two weeks (git history, 2026-10-24 to 2026-11-06),
six pre-registered benchmark rounds, and losses published.

**How will you grow? / Distribution strategy? / How will customers find out about you?**
> [FILL.] Hypothesis:
> - Through robot integrators, who build these cells and carry the risk of escapes.
> - Through cobot app stores: the UR+ and Flexiv ecosystems.
> - Direct to a few EMS and tier-1 lighthouse customers.
> - Credibility through public, pre-registered benchmarks that integrators can rerun.

**How are you measuring success?**
> For pilots, escapes per 10,000 parts and cycle time against their current cell, on
> their spec.

### Business model and revenue

**How will you make money? / Who pays? / Pricing?**
> [FILL: decide before the interview.] A hypothesis to test: a per-cell software licence
> plus annual support, sold through integrators, priced against the cost of escapes it
> prevents. Recurring revenue, not hardware margin.

**How do you know they'll pay? / First paid offering? / First paying customer?**
> [FILL.] Best answer: a named pilot with a price. Otherwise: "a paid feasibility study
> on their connector: we run their part through our simulator and rig."

**CAC, LTV, margins, profitable, burn, runway, how much capital?**
> [FILL: burn, runway, months without funding.] CAC and LTV: "Too early. Integrator-led
> sales usually take months. I'll know after the first pilots."

Know your monthly burn to the dollar.

**What would you do with $500k?**
> 1. Buy the rig: about $14-40k depending on option, plus F/T, jig and parts
>    (`hardware/BOM.md`).
> 2. Run the pre-registered rig test, about 3,000 insertions.
> 3. Run 2-3 paid pilots on customer connectors.
> 4. [FILL: first hire.]

**How big can this be? / Total revenue potential? / Revenue in 3 and 12 months?**
> [FILL with a bottom-up model, section 4, item 5.] Do not quote a market-report TAM you
> haven't checked.

### Market and competition

**Who are your competitors? / Who might become competitors? / Who do users compare you
to?**
> - Cobot vendors' built-in insertion: Flexiv Adaptive Assembly, the Robotiq Insertion
>   node, UR force-control apps. These are spiral search, our baseline D/F.
> - Vision-and-force connector cells from ABB and Nachi.
> - Wire-harness automation: Komax, and general-purpose robot companies demoing harness
>   work, such as Sanctuary AI.
> - Learned-policy research.
> - The real competitor: a human with a tug test.

**What competition do you fear most?**
> The cobot vendors adding a verify step themselves. They own the robot and the app
> store.

**Isn't this a feature? / What stops UR, Flexiv or Google from copying you? / What if a
large competitor cloned you? / Will this be easy to copy?**
> The verify step alone could be copied. What's hard to copy:
> - the test harness and the failure-mode library behind it;
> - per-connector models, latch and force budgets, fitted from rig curves;
> - being robot-agnostic across vendors, which a vendor won't be.
>
> Honestly, if we stay a single feature we lose. We have to become the insertion layer
> that integrators use across robots.

**Why hasn't someone won this market? / Why isn't a big company doing it?**
> Every line has different connectors, specs and fixturing, so it's fragmented, and
> vendors sell robots, not assembly outcomes. [FILL: what customers say.]

**How big is the market? / How fast is it growing? / What trends support it?**
> [FILL: bottom-up.] Trends to verify: wire-harness content per vehicle, reshoring of
> electronics assembly, and labour scarcity.

### Team

**Who are the founders? / Background? / Domain expertise? / Why are you the right
team?** [FILL.] Lead with the most relevant thing you have done in robotics or
manufacturing.

**Who built this? Who wrote the code?**
> [FILL, honestly.] If you directed AI agents, say so with confidence, then prove you
> own it: whiteboard section 6 and explain one failure you diagnosed yourself, such as
> the F/T-drift lift.

**Who does what? / Who is the boss? / How did you meet? / Will you stick together? /
Disagreements?** [FILL.] If you are a solo founder, say how you'll cover sales and
hardware, and whether you're looking for a cofounder.

**Who would you hire first?** [FILL.] A natural answer: a robotics hardware engineer to
own the rig and pilots, or a manufacturing person with customer access.

**What systems have you hacked? / Something impressive you built? / Tough problem you
solved?**
> Technical candidate: finding why our controller failed on a high-friction arm in only
> some simulators. It was MuJoCo ignoring a friction time constant under the pyramidal
> cone, so floor friction stopped our wall probe before it reached the wall
> (`results/v0.2f_friction_diagnosis/REPORT.md`).

[FILL: something outside this project too.]

**Biggest mistake?**
> Early on we claimed "C leads in all 13 simulators" and called C "gentle". Both
> stopped being true as the baselines got fair. We now pre-register everything and
> publish the losses.

**What do you personally struggle with? / Open to changing the idea?**
> [FILL.] On changing the idea: yes, and the data already moved us, from "smarter
> insertion" to "verified insertion."

**Will you stick with this for 10 years? / Why dedicate your life to this?** [FILL:
personal reason.]

**Funniest / worst / most surprising thing?** [FILL: have one short story ready.]

### Vision and strategy

**What do you understand that others don't? / Your secret?**
> In connector assembly, the dangerous failure isn't the robot missing the hole. It's
> the robot succeeding wrong. Spiral search's failures are mostly plugs at full depth,
> just past spec, declared good. Optimizing insertion speed makes that worse. The
> product is the proof of seat.

**10-year vision / how does this become a billion-dollar company? / Next products / What
else could you expand into?**
> First, the verified-insertion layer for every connector, on any robot. Then every
> contact-rich assembly step where "did it go in right?" matters: clips, snap fits,
> fasteners, cable routing. Every step logs a force signature as proof of quality,
> which becomes the dataset for learned policies.

Keep this to 15 seconds unless they ask for more.

**Biggest risks / obstacles / what keeps you up at night / biggest problem in 6 months?**
> 1. Sim-to-real: contact physics may not transfer. That's why the rig predictions
>    are frozen in advance.
> 2. Customers may not value escapes enough to accept 1.9 s more per part.
> 3. Vendors may bundle a verify step.
>
> In 6 months the biggest problem is integration effort per customer connector.

### YC-specific

**Why YC? / What do you want most from YC?** [FILL.] Concrete answers beat flattery:
introductions to manufacturing customers among YC companies (hardware and EV), help
with the pricing model, and a forcing function for speed.

**What if we don't fund you?** [FILL.] The strong answer: "I keep going. I build the
rig and run pilots either way."

**What will you do in the next 30 days?**
> Make the first real insertions, talk to 20 engineers, and get one pilot commitment.

**How much are you raising / use of funds / have you raised?** [FILL.]

**Relocate to the US / San Francisco? Reincorporate as a US company?** [FILL.] Answer
yes or no directly.

**"Someone pitched us something like this earlier and we didn't like it. What else have
you got?"**
> Stay calm. Ask what they didn't like, then separate yourself: "The difference is we
> measured it against what vendors ship, and published where we lose."

---

## 6. The 60-second technical explanation (be able to whiteboard it)

1. **Approach.** The camera gives one noisy socket estimate. The robot moves above it
   and aligns the plug.
2. **Insert.** It pushes under force control, with software compliance so the plug can
   slide and rotate on contact. A monitor watches for a stall or excessive force.
3. **Diagnose.** If it is blocked on the face, the plug first settles flat. The wrist
   torque then gives the centre of pressure, the point where the plug is supported. A
   Bayesian filter over the hole position combines that reading with every earlier
   blocked probe and picks the most likely entry point. If two confident probes still
   block, the error is rotational and it searches yaw (3, 6, 9 and 12 deg, both ways).
4. **Recover.** Retries are bounded: at most 8 attempts and 26 s, with hard force
   limits.
5. **Verify.** This is the part that matters:
   - square the plug to the floor;
   - probe both short-axis walls (each must push back at 2 N or more within the
     clearance);
   - centre the plug, and on the gantry centre its yaw between its rotational limits;
   - on latching connectors, pull at 1.1 times the datasheet's maximum mating force.

   Only then does it declare success.

Know the numbers:
- the socket is 12 x 8 mm with 0.5 mm clearance and 15 mm depth;
- the chamfer captures a 1.3 mm offset;
- a centred plug jams past about 4.9 deg of yaw. Spiral search corrects position, not
  yaw, which is why it loses on unseen socket yaw;
- control runs at 500 Hz, and C's per-tick work takes about 45 us at the median
  (`results/v0.2f_realtime/REPORT.md`).

---

## 7. Never say these (they are false, retracted, or a trap)

- "C leads in all 13 simulators." That was v0.2a code and is not repeated
  (`results/sim_randomization_v0.2f`).
- "We catch bad parts the others miss." With the same pull test, H and I also pass 0 of
  2,200.
- "Our controller is gentle" or "faster". The p95 contact force was higher than F's in
  v0.2a, and C is slower everywhere.
- "Zero bad units, ever." There were 8 under F/T drift on the arm in heldout2, and 1 per
  machine across randomized simulators.
- "Validated", "proven" or "production-ready" with no "in simulation" attached.
- "AI-powered" as the headline. The learned prior gave no gain on the clean held-out
  test.
- Any market-size number you cannot source.

---

## 8. The 15 sharpest follow-ups for this project (drill these)

| # | Partner says | Core of your answer |
|---|---|---|
| 1 | "The baseline gets 96.8%. You're fighting over 2 points." | The 2 points aren't the product. Escapes are: 0 against 138-178 per 7,400. |
| 2 | "And you're twice as slow." | Yes, 5.3 s against 2.4 s. 1.9 s of that is verify. It pays wherever an escape costs more than 1.9 s of cycle time. [FILL: the customer's cost of an escape.] |
| 3 | "Your edge vanishes at 4 degrees on the arm. What's the real spec?" | Correct. On the gantry it holds at 4-5 deg. The real spec is the first thing I ask customers. [FILL: what they said.] |
| 4 | "Has this touched a real robot?" | No. The rig test and its predictions are frozen: 387/400 against 336/400 housing-only on the gantry. [FILL: date of first real run.] |
| 5 | "Why spend two weeks in sim instead of buying a $14k arm?" | Simulation found failure modes cheaply: friction, drift, grasp offset. The rig plan needed the power analysis first. [Better: "I'm buying it on DATE."] |
| 6 | "Who's paying you?" | [FILL.] |
| 7 | "So it's just a verify step. Why not let Universal Robots add it?" | See "Isn't this a feature?" in section 5. |
| 8 | "Why not train a policy?" | No real force data yet. The learned prior gave no held-out gain. Rig and pilot data come first. |
| 9 | "On the unseen grasp offset you lost 75% to 99%. Why?" | The offset shifts our centre-of-pressure reference 0.8 mm, so an edge contact reads as a jam and we loop. We diagnosed it. A fix needs a new pre-registered round. |
| 10 | "Simulators lie about contact." | Agreed on absolute numbers. 12 randomized simulators: the gantry holds 29 of 29 comparisons, the arm 24 of 29, and we publish which ones fail and why. |
| 11 | "Who's the customer: integrators, OEMs or robot vendors?" | [FILL: pick one and say why.] |
| 12 | "How many connector types does this work on?" | Two in simulation: a housing-only part and a Molex Micro-Fit 3.0. Generalization comes through per-connector models fitted from rig curves. The fitter exists but hasn't seen a real curve. |
| 13 | "What happens when the sensor drifts?" | We found it: verify can lift a seated plug. The fix is a depth re-check before success, not yet implemented. |
| 14 | "Did you tune on your test set?" | Not on any reported seed. Each benchmark was pre-registered with a fresh seed, and heldout2 was new families no one had developed against. We say exactly where earlier tests leaked. |
| 15 | "What will you have in 3 months?" | [FILL: rig result, N pilots, revenue.] |

---

## 9. Practice protocol

1. Fill every `[FILL]`. Memorize facts, not scripts.
2. Have someone fire random questions from section 5 at you (or use the simulator in
   the repo above) with a 10-minute timer. They should interrupt at 15 seconds.
3. Record yourself. Cut any answer that runs past 25 seconds or opens with context
   instead of the answer.
4. Do one full round of only section 8, at speed.
5. Rehearse the first 30 seconds ("What are you working on?") until it is identical
   every time.

---

## Sources

- This repo: `README.md`, `docs/HASAN_DEFENSE_NOTES.md`, `docs/TECHNICAL_BRIEF.md`,
  `results/v0.2f_checkpoint/CHECKPOINT_REPORT.md`, `hardware/BOM.md` and the result
  files cited inline.
- Question banks:
  [surkyl/labs-yc-mock-interview-simulator](https://github.com/surkyl/labs-yc-mock-interview-simulator)
  (`data.yml`, `yc-more-questions.md`, which includes the
  [iPG](https://jamescun.github.io/iPG/) list).
- Competitive context, unverified beyond search results:
  - [arXiv 2503.09409](https://arxiv.org/abs/2503.09409) (learned connector mating for
    wire harnesses);
  - [arXiv 2602.22100](https://arxiv.org/abs/2602.22100) (behavioral cloning for
    connector assembly);
  - [ABB FPC cable assembly cells](https://new.abb.com/news/detail/127283/wbstr-abbs-cobots-and-small-robots-bring-efficiency-and-precision-to-flexible-printed-circuits-cable-assembly);
  - [Nachi connector insertion](https://www.nachi-fujikoshi.co.jp/eng/news/pre/211110.html);
  - [Assembly Magazine on Komax harness automation](https://www.assemblymag.com/articles/87619-wire-processing-automating-harness-assembly);
  - [Sanctuary AI wire-harness claim](https://mikekalil.com/blog/sanctuary-ai-wire-harness-assembly/).
