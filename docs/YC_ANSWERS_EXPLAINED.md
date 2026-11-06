# YC answers, explained (study guide for Hasan)

For each question:
- **Say this:** the words to use. Learn the facts in it; don't recite it word for word.
- **What it means:** every part of the answer, in plain English.
- **If they push:** the likely follow-up and your reply.

Everything is simulation only. `[FILL]` means only you know it. Part 1 explains the ideas
that every answer uses, so read it first.

---

## Part 1: Ten ideas you must understand first

**1. The task.** A robot holds a plug and pushes it into a socket.
- Our test plug is a 12 x 8 mm rectangle.
- The hole is 13 x 9 mm, so there is only **0.5 mm of gap on each side**. It is 15 mm
  deep.
- The top edge of the hole has a small slope, the **chamfer** (0.8 mm). If the plug
  lands a little off, the slope guides it in. That works up to about 1.3 mm off.

**2. Why it is hard.** The robot does not know exactly where the socket is.
- A camera tells it, but the camera is off by 0.3 to 2 mm.
- With only 0.5 mm of gap, a 1-2 mm camera error means the plug often lands on the
  top face, not in the hole.

**3. Yaw and tilt.**
- **Yaw:** the plug is *twisted*, rotated around the direction you push.
- **Tilt:** the plug is *leaning*.

In our test, **"seated"** means:
- at least 14.5 mm deep;
- centred;
- yaw and tilt both **under 3 degrees**;
- no force alarm and no damage.

**4. The crooked-plug problem. This is the key idea of the company.**
- The hole is a little bigger than the plug, so a plug can go **all the way down while
  twisted**. Up to 4.9 degrees of twist still fits.
- So a plug can be at **full depth but 3-5 degrees crooked**. If you only measure depth,
  it looks finished, but it is out of spec.
- When the robot says "done" on a plug like that, we call it a **bad unit** or an
  **escape**: a bad connector escaping the cell as if it were good.

**5. The force sensor.** A sensor at the robot's wrist (an **F/T sensor**, for
force/torque) measures push and twist forces 500 times a second. It is how the robot
"feels."

**6. Spiral search: what industry uses today.**
- The robot presses the plug lightly on the surface and moves it in a growing spiral
  until it drops into the hole. Then it pushes in.
- When the plug reaches the right depth, it says "done." **It only checks depth.**
- Cobot companies ship this method (Flexiv Adaptive Assembly, Robotiq's Insertion
  node).
- An **RCC** is a passive spring part between the robot and the gripper. It lets the
  plug wiggle into place by itself.

**7. What Defex (controller "C") does differently.** Two things:
- **(a) Smarter search.** When the plug is blocked on the surface, the wrist sensor's
  twist reading shows where the plug is resting. From that, C calculates where the hole
  probably is and tries there next. If that fails twice, it tries twisting the plug.
- **(b) VERIFY, the important part.** After the plug reaches the bottom, C:
  - straightens the plug against the floor;
  - pushes gently left and right to feel **both walls of the hole** (only a plug that
    is truly inside can feel both walls);
  - centres it;
  - finds both twist limits and centres the twist.

  Only then does it say "done." On latching connectors it also **pulls** the plug to
  check that the latch holds.

**8. The names in our tests.**

| Name | What it is | Why it's in the test |
|---|---|---|
| **C** | Defex | our product |
| **F** | spiral search + RCC | the best industry method |
| **I** | F + our pull test | we gave the baseline our pull test, to be fair |
| **J** | F's insertion + only Defex's VERIFY step | shows how much of our win comes from VERIFY alone |

**9. Bad unit vs bad part. Do not mix these up.**
- **Bad unit:** a *good* part that the robot called done but that is not seated right
  (crooked or short). **This is where we win.**
- **Bad part:** a part that is *broken on purpose* (broken latch, bent pin, wrong
  polarity). The pull test catches these, and the baseline with the same pull test (I)
  catches them too, 0 of 2,200. **Never claim bad parts as our advantage.**

**10. How the tests work.**
- **Simulation:** MuJoCo, a physics engine. No real robot yet.
- **Trial:** one insertion attempt.
- **Paired:** every controller faces exactly the same socket position and the same
  sensor noise in trial number *i*, so the comparison is fair.
- **Seed:** one random set of test cases. We ran **three different seeds** and got the
  same main result, so it is not luck.
- **Pre-registered:** we wrote the rules and what counts as a win *before* running, so
  we cannot cherry-pick.
- **p-value:** roughly, the chance the difference is just luck. Below 0.05 is usually
  treated as a real difference.

### The three numbers to know by heart

1. **Escapes** (crooked or short plugs called "done"), out of 7,400 good parts:
   - spiral search: 178 (F) and 138 (I);
   - **Defex: 0**;
   - spiral + our VERIFY (J): 2.
2. **Success rate:** Defex 99.1% against the best baseline's 96.8% (gantry). The
   advantage exists **only when the camera error is 1-2 mm**. With a good camera, both
   seat exactly the same trials.
3. **Speed:** Defex takes **5.3 s per part** against spiral's **2.4 s**. VERIFY is 1.9 s
   of that.

Sources: `results/benchmark_v0.2e/REPORT.md`, `results/v0.2f_evidence/BAD_UNITS.md`,
`results/v0.2f_evidence/PERCOND.md`, `results/v0.2f_evidence/PHASES.md`. The escape
numbers are from the latest run, seed 20261130. The other two seeds gave F 197 and 176,
I 161 and 138, and Defex 0 and 0.

---

## Part 2: The ten answers

### Q1. "What does your company do?"

**Say this:**
> We make software that lets robots plug in electrical connectors and prove each one is
> seated right, so assembly lines stop shipping mis-mated connectors.

**What it means, piece by piece:**
- **"We make software."** We don't build robots. Our software runs on robots factories
  already buy, like a UR arm or a gantry. That makes it cheaper to adopt and easier to
  scale.
- **"Lets robots plug in electrical connectors."** This is the job. In electronics, car
  and appliance factories, cables get plugged into boards and modules, and much of it is
  still done by hand.
- **"And prove each one is seated right."** This is the part that matters (ideas 4 and
  7). Other robots push until the depth is right and stop. We feel the walls and check
  straightness and twist before we say "done."
- **"So assembly lines stop shipping mis-mated connectors."** A mis-mated connector
  looks plugged in but isn't fully or correctly in. It can pass the factory and fail
  later: a loose contact, a failure under vibration, a warranty return. What that costs
  is something you must learn from customers (Q6).

**Why one sentence:** the first question tests whether you can be clear under pressure.
If you ramble, the rest of the interview is uphill. Practise it until it comes out the
same every time.

**If they push: "How far along are you?"**
> It's a simulation prototype. On our latest run of 7,400 good parts, the spiral search
> cobot vendors ship called 138 to 178 crooked plugs good. Ours called none. Next is a
> real robot rig.

- "138 to 178" is idea 9's bad units: I passed 138 and F passed 178.
- Say "simulation" yourself, before they ask. It builds trust.

---

### Q2. "Why is now the right time?"

**Say this:**
> Three things changed:
> 1. Robots now do this step, and they check the wrong thing. Flexiv, Robotiq, ABB and
>    Nachi all ship connector insertion. It's spiral search with a depth check, so the
>    crooked plug is a new failure that nobody owns.
> 2. The hardware got cheap. A wrist force sensor is about $3,700, and cobots have
>    500 Hz control, so feeling a 0.5 mm wall works on a $10-35k arm.
> 3. Simulation got good enough to test 96,000 cases before building hardware.

**What it means:**
- **Point 1: automation created the problem.**
  - When a person plugs in a connector, they see and feel it. When a robot does it with
    spiral search, it only measures depth (idea 6), so nobody checks the robot's work.
  - The more factories automate this step, the bigger the crooked-plug problem gets
    (idea 4).
  - That is a good "why now": the market for our product grows *because* robots are
    taking over this job.
  - **Before the interview, check the launch dates** of Flexiv Adaptive Assembly,
    Robotiq Insertion, ABB's flexible-cable cells and Nachi's connector insertion
    (Nachi's is from 2021). YC likes "what changed in the last 18 months," so only claim
    dates you have checked.
- **Point 2: cost.**
  - Feeling a wall 0.5 mm away needs a sensitive wrist force sensor, plus a robot that
    lets your software read that sensor and correct the motion 500 times a second.
  - A Bota MiniONE sensor costs CHF 3,045, about $3,700 (`hardware/BOM.md`). Universal
    Robots e-Series arms offer a 500 Hz external control interface (RTDE).
  - Arms cost about $10k (UFactory 850) to $33k (UR3e).
  - Meaning: this works on cheap, common robots, not just on expensive custom machines.
- **Point 3: simulation.**
  - MuJoCo is a free physics engine. One benchmark run was 96,000 insertion trials.
  - A small team can find the problems before buying a $30k robot. Example: we found
    three weaknesses in our own method in simulation (sensor drift, a plug held off
    centre in the gripper, high friction on the arm).

**`[FILL]`, optional:** a demand trend, *only if you can source it*: more wire harnesses
in electric cars, factories coming back to the US or Europe, a lack of workers.

**If they push: "Spiral search is old. What's new?"**
> Exactly. Everyone uses it because it's good at *finding* the hole. It just never
> checks the result. That's the gap.

---

### Q3. "Who's your competition? Why will you win?"

**Say this:**
> Cobot vendors' built-in insertion, like Flexiv Adaptive Assembly and Robotiq's
> Insertion node. That's spiral search, exactly what we benchmark against. Industrial
> connector cells from ABB and Nachi. General-purpose robot companies demoing harness
> work, like Sanctuary AI. And a person with a tug test.
>
> Our wedge is proof of seat: a check that sits on top of the spiral-search cell a
> customer already runs, on any robot brand. Added to a spiral cell in our simulation,
> it cut escapes from 178 to 2 per 7,400 parts.

**What it means:**
- **Name real competitors. Never say "we have no competition."** They will search for
  30 seconds and find five.
- **The four competitors:**
  1. **Cobot vendors' insertion apps.** These are our baseline method (idea 6). Our
     benchmark *is* a comparison against them, which is a strong point.
  2. **ABB and Nachi.** Big industrial companies with cells that use vision and force to
     insert connectors and flexible cables.
  3. **Sanctuary AI and similar.** Humanoid or general robot companies showing
     wire-harness demos. They aim to do everything; we do one thing deeply.
  4. **A person with a tug test.** The real status quo: a worker plugs it in and tugs it.
- **"Wedge"** means the narrow first thing that gets you into customers.
- **Ours is the check, not the robot.** It works with what they already have, so the
  customer doesn't throw anything away. That makes buying easier.
- **"178 to 2"** is the J experiment (idea 8). We took the industry method (F) and
  added only our VERIFY step. Escapes fell from 178 to 2 out of 7,400 good parts (seed
  20261130). This is our best proof that VERIFY alone has value.
- **"Any robot brand":** a robot company only builds for its own robots. We can work on
  all of them, and an integrator who uses several brands wants one tool.

**If they push: "Why can't Flexiv just add a check?"**
> They can add a check. What's hard is a check that works across robot brands, with
> force models for each connector type and the library of failure cases behind it. If
> we stay one feature we lose, so we have to become the insertion layer that integrators
> use across robots.

**If they push: "If J does almost as well, isn't your product just VERIFY?"**
> Yes, VERIFY is the core. Our insertion adds more on top: about half of our success
> advantage on the gantry. But the check is what customers pay for.

That is honest, and it shows you understand your own data (source:
`results/v0.2f_checkpoint/CHECKPOINT_REPORT.md`).

---

### Q4. "Why you? Why are you the right team?"

**Say this, filled in with your own story:**
> 1. [The moment you saw this problem: a factory, a job, a project.]
> 2. [The strongest thing you built before this.]
> 3. On this project, I went from a first simulation to six benchmark rounds against
>    tuned industrial methods in two weeks. When the data showed we were losing
>    somewhere, I published it and changed the pitch, not the numbers.
> 4. [Your cofounder: how you met, what you've built together. Or, if you are solo: how
>    you cover sales and hardware.]

**What it means:**
- YC bets on **people** more than ideas. They want proof that you will keep going when
  it gets hard.
- **Tell a story, not a CV.** "I worked at X" is weak. "I saw workers at X plugging 500
  connectors a shift, and 1 in 100 came back from test" is strong.
- **Part 3 shows two qualities YC loves:**
  - **Speed:** the first version on 2026-10-24, six benchmark rounds by 2026-11-06.
  - **Honesty:** our own reports say where we lose, for example "Defex is below F on arm
    latching parts" and "8 bad units under sensor drift."

**If they push: "Who wrote the code?"** They may ask, because the git history shows much
of the work was done with AI agents.
- **Say the truth plainly.** For example: "I designed it and directed AI coding agents
  to build it. I review every result."
- **Then prove you own it.** Be able to draw and explain idea 7 on a whiteboard without
  notes, and explain one problem you diagnosed yourself (Q9 has good ones).
- YC does not mind AI tools. It minds a founder who can't explain their own product.

---

### Q5. "What's your growth?"

**Say this:**
> Zero users and zero revenue. We're pre-product.
>
> What has grown is evidence. Version 1 was October 24. Since then we've run six
> pre-registered benchmark rounds against industrial methods, a clean held-out test,
> tests on 12 different simulator settings, and we have a frozen plan for a real-robot
> test.
>
> Our mistake was building the evidence before talking to customers. That's what I'm
> fixing now: [N] engineer conversations by [date], first real insertion by [date].

**What it means:**
- **Be brutally honest.** Inflating numbers is the worst thing you can do. YC checks
  references and will catch it. Zero, said clearly, is fine at this stage.
- **"What has grown is evidence."** You have no customers, so show that the *work* is
  moving fast. The six rounds were benchmarks v0.2a, v0.2b, v0.2c, v0.2d, its repeat
  run, and v0.2e.
- **"A clean held-out test"** is heldout2: five new kinds of problems no one had tuned
  the software for. It tests whether Defex handles surprises.
- **"12 different simulator settings":** we changed the physics engine's settings 12
  ways, to check the result is not an accident of one setting. On the gantry, every
  main result held.
- **"Frozen plan for a real-robot test":** we wrote down *before* building the rig
  exactly what the simulation predicts. If the real robot matches, the simulation can be
  trusted.
- **Admitting the mistake shows self-awareness.** Giving dated targets shows you have a
  plan.

---

### Q6. "What have you learned from your users?"

This is your weakest answer today, because you have no users yet. Fix it before the
interview: talk to 15-20 people who own a connector step (process, test or quality
engineers at contract manufacturers, wire-harness makers, car suppliers, appliance
makers).

**Ask each one:**
1. How are connectors plugged in today, by hand or by robot?
2. How do you decide a connector is "in"? By angle, depth, a click or a pull?
3. How do you catch a bad one, and where: at the station, at final test, or from
   customer returns?
4. What does one bad connector cost you when it is found late?
5. How many seconds per part can the step take?
6. Who decides to buy new equipment?

**Then say a story with this shape:**
> Last week a quality engineer at [company] told me [their check is a tug test, and a
> bad connector caught at final test costs $X to fix]. So we [decided to build the
> check-on-your-existing-cell version first]. Now [two of them asked us to test their
> part].

**What it means:**
- YC asks this to see whether you **actually talk to customers**. "Users love it" tells
  them you don't.
- A good story has four parts:
  1. **who** (a real person and role);
  2. **what they said** (a specific fact or number);
  3. **what you changed** because of it;
  4. **what happened next**.
- Have three stories, all real and recent.
- **The cost answer (question 4 in the list above) is the most important number in the
  company.** Our product is slower (Q9). It is only worth buying if a bad connector
  costs much more than the extra 1.9 seconds.

**If you still have no users on the day, say:**
> I haven't talked to enough users yet. Here's what the first [N] told me: ...

Then add the data lesson:
> The surprise in our data is that spiral search fails by being confidently wrong, not
> by missing the hole.

That is idea 4: most of the baseline's failures are plugs at full depth, just past
3 degrees, that it called good.

---

### Q7. "How big can this be?"

**Say this, with your own numbers:**
> Start with the wedge: [N] robot cells doing connector mating, times $[X] a year for
> our software per cell. For example, 10,000 cells at $10,000 a year is $100 million a
> year.
>
> The billion-dollar path is expanding to every assembly step where "did it go in
> right?" matters: clips, snap fits, screws, cable routing. And every check we do
> records a force signature, a quality record that becomes training data for robot
> learning.

**What it means:**
- **"Bottom-up"** means you build the number from units:

  > number of customers x price = revenue

  "Top-down" ("the market is $50 billion") sounds lazy to YC. Use bottom-up.
- **ARR** means annual recurring revenue: money that comes in every year, like a
  subscription. Software licences give recurring revenue, which investors value highly.
- **The $100M example is only arithmetic, not data.** Replace [N] and [X] with numbers
  you got from calls and research.
  - **[N]:** ask integrators how many cells they build with a connector step.
  - **[X]:** price from value, below.
- **How to set the price [X] (value pricing).** Price below what you save the
  customer. Illustrative example only:
  - A cell makes 500 parts an hour for 4,000 hours a year, so 2 million parts a year.
  - Suppose 1 in 1,000 is a bad connector found late, at $50 each to fix.
  - That is 2,000,000 x 0.001 x $50 = **$100,000 a year in losses per cell**.
  - A $10,000 licence that removes most of that is an easy yes.
  - The real numbers (bad rate and cost per bad connector) must come from Q6's calls.
- **Expansion:** connectors are the first product. The same skill (feel the part, prove
  it's in right) applies to many assembly steps. That's how it becomes a big company.
- **The data point:** each verified insertion leaves a record of forces. Over time that
  is a unique dataset for training learned robot policies, which nobody else has.

---

### Q8. "What would you do with the YC money?"

**Say this:**
> - **Month 1:** buy a test robot rig, from about $14,000 to $40,000 depending on the
>   option, and do the first real insertions.
> - **Months 2-3:** run our planned real-robot test, about 3,000 insertions, and compare
>   it with the predictions the simulation made in advance.
> - **Months 3-6:** two or three paid pilots on customers' own connectors.
> - **One hire:** [a robotics hardware engineer].
> - **The rest is runway:** [N] months.

**What it means:**
- YC's standard deal is $500k. They want to see you know exactly where it goes in the
  next six months.
- **The rig** is a real robot plus test equipment. The options in `hardware/BOM.md`:

  | Option | Approximate cost |
  |---|---|
  | UFactory 850 arm + force sensor | ~$13.6k |
  | Desk gantry | ~$23.3k + sensor |
  | UR3e arm + Bota sensor | ~$39.8k |

  None of these totals includes the spring stage (RCC), the socket jig that sets each
  trial's socket position, the tool that measures the final plug angle, or test parts.
- **"About 3,000 insertions"** (`hardware/TEST_PROTOCOL.md`):
  - four methods: Defex, spiral, spiral + pull and spiral + VERIFY (plus a fixed
    program as a sanity check);
  - two connector types;
  - 100 trials per condition.
- **"Compare with predictions made in advance"** is very important. The simulation
  already predicted, for example, that on the gantry Defex seats 387 of 400 and spiral
  seats 336 of 400 (`results/v0.2f_rig_predictions/REPORT.md`). If the real robot comes
  close, the simulation is trustworthy, and every other simulation result becomes
  believable. This is the answer to "simulation isn't real."
- **Pilots:** a real customer tests it on their part, and pays something. This turns
  "evidence" into "traction."
- **Say no marketing team.** YC sees that as the wrong move this early.
- **Know your monthly burn** (how much you spend a month) and your runway (how many
  months you can last).

---

### Q9. "What's the hardest thing about this business?"

**Say this:**
> Proving it works on real parts, and that bad connectors cost enough to pay for it.
>
> - We're slower: 5.3 seconds against 2.4 per part, and 1.9 seconds of that is the
>   check. It only pays where a bad connector costs much more than 1.9 seconds.
> - The 3-degree spec we test against is our assumption. If real customers allow more,
>   our edge shrinks.
> - Simulation might not match reality. That's why we froze our predictions before
>   building the rig.
>
> The plan: customer calls for the real spec and cost, then the rig, then pilots,
> selling through the integrators who build these cells.

**What it means:** YC asks this to test self-awareness. "Nothing is hard" is an
arrogance red flag. There are three real hard things:

1. **Slower.**
   - Our check takes time, so Defex makes about **601 good parts per hour** where spiral
     makes **1,100** (gantry, `results/benchmark_v0.2e/HEADLINE_TABLES.md`).
   - A factory pays for speed. We win only if catching a bad connector saves more money
     than the lost speed costs. Q7's example shows how to calculate that.
2. **The assumed 3-degree spec.**
   - We decided "seated" means under 3 degrees. Most of spiral search's bad plugs are
     just over 3 degrees, between 3 and 5.
   - We rescored the same tests with other limits:
     - **At 4 degrees,** many of those plugs count as good, so our advantage shrinks. On
       the arm it is no longer statistically significant.
     - **At 2 degrees,** our advantage grows a lot.
   - So the customer's real spec decides how valuable we are. That's why you ask for it
     in every call (`results/v0.2f_evidence/TOLERANCE.md`).
3. **Simulation vs reality.**
   - A physics engine can be wrong about how plastic parts slide and push.
   - We tested 12 different simulator settings. Most results held, but some arm results
     changed.
   - Only the real rig settles it, so we froze the predictions in advance (Q8).

**Other true weaknesses, in case they ask:**
- **Sensor drift.** When the force sensor's zero drifts, our check can lift a seated
  plug slightly and still say "done": 8 bad units on the arm in heldout2. We found the
  cause. The fix, re-checking depth before "done," isn't built yet.
- **Plug held off-centre in the gripper.** Defex can get stuck retrying the same spot:
  75% success against spiral's 98.8%.

Both are in `docs/HASAN_DEFENSE_NOTES.md`. Saying them shows you know your product
deeply.

---

### Q10. "If we don't fund you, what will you do?"

**Say this:**
> Keep building. I'll [self-fund / raise from angels] the cheapest rig, run the real
> test, and get pilots. YC makes it faster. It doesn't decide whether it happens.

**What it means:**
- They are testing **commitment**: would you do this anyway?
- "I'd probably go back to my job" means instant rejection.
- Mention the cheapest rig, about $13.6k. That shows you have a realistic plan that
  doesn't need their money.
- Fill in honestly how you would pay for it.

---

## Part 3: The live demo (be ready to share your screen)

**What to show:** the main thing your product does, which is catching a crooked plug.
Show it, don't use slides.

**A ready example from our benchmark:**
- Gantry, condition `noise_1mm` (camera off by about 1 mm), trial 38, seed 20261130.
- **Spiral + pull (I)** pushes the plug to 14.83 mm deep, twisted **3.67 degrees**, and
  says "done." That is a bad unit (idea 4).
- **Defex (C)**, on the exact same socket with the same noise, feels the problem, tries
  again twice and seats it correctly.
- That seed has 30 cases like this.

**Problem:** today's demo (`demos.run_demo`) and the old video only show the fixed
program, vision correction and Defex. They cannot show spiral search, so the demo
program needs to be extended to play I and then Defex on that trial.

**When you share:** say "this is simulation" before you press play.
