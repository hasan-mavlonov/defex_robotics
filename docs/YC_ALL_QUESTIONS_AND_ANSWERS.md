# Every YC interview question we found, with an answer (Defex Robotics)

**Sources of the questions** (all read on 2026-11-06):
- YC's official guide, [ycombinator.com/interviews](https://www.ycombinator.com/interviews)
- [ycinsight.com/interview](https://ycinsight.com/interview) and
  [ycinsight.com/yc-interview-questions](https://ycinsight.com/yc-interview-questions)
- [iPG](https://jamescun.github.io/iPG/): 77 questions
- [surkyl/labs-yc-mock-interview-simulator](https://github.com/surkyl/labs-yc-mock-interview-simulator):
  `data.yml` and `yc-more-questions.md`
- the LinkedIn list of 14 (Soham Mehta)

Duplicates are merged. Each question appears once, and the sources' other wordings are
in brackets.

**Sources of the answers:**
- The company site, [defexrobotics.com](https://defexrobotics.com). Text in "quotes" is
  copied from it; the full text is in
  [`SITE_SNAPSHOT_2026-11-06.md`](SITE_SNAPSHOT_2026-11-06.md).
- This repo's simulation results (file paths given).

**Placeholders:**
- `[FILL]` is something only you know.
- `[CONFIRM]` is a site claim you must be able to prove. YC's guide says: *"if you state
  numbers in the interview we may ask for verification of them afterwards."*

---

## What YC says about the interview (official guide)

- **Format.** 10 minutes on Zoom. All founders on the call. 2-3 partners, who have your
  application open. "We only do two things: we ask you questions, and we look at what
  you've built."
- **"Don't rehearse."** Prepare the basics, then "make progress" between applying and the
  interview: "Demonstrating you can move fast and make quick progress is the most
  surefire way to impress."
- **The first question is usually "What is your company working on?"** Answer "in a few
  simple, jargon-free sentences." "We'd rather have interesting details than boring
  generalizations."
- **Metrics.** Have your key numbers written down where you can see them. Numbers you
  state may be checked afterwards.
- **Be honest about obstacles.** "We tend to be more convinced by candid discussion of
  difficulties than glib dismissal of them."
- **Know the existing products** "and what, specifically, is wrong with them."
- **Have a demo ready.** For hardware, have it with you, or "have a demo video
  available."
- **Each founder answers at least one question.** "Be earnest."

The style tips from iPG and the simulator: 2-3 sentences, answer first, no "uhm," match
the partners' fast pace, numbers instead of adjectives, and say "I don't know yet,
here's how I'll find out."

---

## Before the interview: what YC will check (details in `YC_ANSWERS_SITE_WORDING.md`, section 0)

1. **"27 factories paid to be first in line."** Know which ones, how much each paid,
   when, and the total.
2. **The "Partners" strip** (NVIDIA, Andreessen Horowitz, Google and others). Know what
   each relationship is. If they are credit programs, don't call them partners.
3. **"AI-powered."** Today it is cameras plus force control; "a search is only a
   fallback: a fixed routine, not a trained robot policy."
4. **The site's checks against the repo's.** The site says "continuity and isolation on
   every wire"; the repo has no electrical test. The repo feels the walls and straightens
   the plug.
5. **"Half the engineering hours for the next part"** is a target, not a result.
6. **The founders and the logos** (Artel, UzChasys, Texnopark, GRAND, ATH, NOVA
   Solutions, ghost). Know who is who and what each relationship is.

---

## 1. The product

**What is your company working on? / What does your company do? / What are you building?
Be specific.**
> "Defex is building AI-powered robots that plug connectors into circuit boards and
> wiring harnesses, then test that each one is actually connected. For electronics and
> AI server factories."

**Do you have a demo? / Show me the product. / What's actually built? Show us.**
> Yes. defexrobotics.com/prototype is an interactive simulation of the robot. "It
> measures every unit, feels its way in and tests every connection." I'll run
> "Misaligned," then "No latch," then "Open circuit." The robot itself we're building
> now.

- In the site's words: "MuJoCo simulates only the plug and socket contact... The
  complete cycle is a scripted illustration."
- Behind it is this repo: a gantry and a UR5e arm, about 100,000 paired trials per
  round, and 315 tests.

**How does it work? / In more detail? / Walk me through a typical flow.**
> - "Your board rides in on its pallet."
> - "One camera finds the header. One below checks the plug in the fingers."
> - "A compliant press lets the chamfer guide it home."
> - "It presses, feels the latch click, then pulls. A plug that moves fails."
> - "Seated? Held? Every wire? The light says pass or fail."
> - "Every unit logged: what it saw, what it felt, the verdict."
> - "Good ones to the tote. Rejects locked away."

**Where is the rocket science? / What's technically hard? / Your tech insight?**
> Doing it every time, not once. In the words of our job post: "Plugging a connector in
> once is easy. Doing it every time, testing it and recovering when it fails is the
> job." By touch, the robot tells a seated plug from one that only looks seated. In our
> simulation, the standard spiral search called 138-178 crooked plugs good per 7,400
> parts; ours called 0.

Backed by `results/v0.2f_evidence/BAD_UNITS.md`.

**How is your product different? / What's new? / What exactly makes you different from
existing options? / What can you do that competitors can't? / How much better is it?**
> Two things:
> 1. "It tests every one": seated, held and every wire, on every unit. "By hand, a
>    connector can look seated without being latched. Nobody notices until final test."
> 2. "A new part is not a new project. No weeks of an engineer programming it. A new
>    fixture and the same tests."

**Why does this need to exist?**
> "Robots are cheap. Setting them up is not. Every new product means weeks of
> programming. So factories still plug connectors by hand."

**What part are you building first? / What's the next step in the product?**
> "Building the robot, starting with connectors." Next: "Build the robot and run it on
> customer parts."

**How much of it is AI?**
> Today it's cameras and force control. The insertion search "is only a fallback: a
> fixed routine, not a trained robot policy." Learning comes next: we're hiring a Robot
> Learning Engineer to "teach the robot connector work from demonstrations and its own
> tries."

**What's the single most important feature? / What do early users care about most?**
> "It tests every connection." The verdict, pass or fail, on every unit.

**What did you cut?**
> Everything except connectors: "starting with connectors," "more jobs after that." We
> also kept learning out of the first robot.

**What have you learned so far from working on this?**
> The test is the product. In our simulation we turned off our own check step. Without
> it, our robot passed 41 bad plugs out of 2,000, as many as standard spiral search did
> (40). With it, zero.

Backed by `results/v0.2g_noverify_dev/REPORT.md`.

**What have you shipped in the last month?**
> Since October 24:
> - a full simulation of the connector cell on two robots;
> - six pre-registered benchmark rounds against the routines vendors ship;
> - a clean held-out test, and tests across 12 simulator settings;
> - a frozen test plan for the real robot;
> - this week, the test proving the check step is what matters;
> - [CONFIRM: the interactive prototype on the site, the pricing page, the job posts,
>   and the date each went live].

**Have you considered a variation? / Could this be a feature of a bigger product?**
> A test station without the robot, or a robot without the test. We think the value is
> both together on one robot: "plugged in and tested."

---

## 2. Users and customers

**Who needs this? / Who is your user? / Who would use it?**
> "Electronics and AI server factories" that plug connectors into "circuit boards and
> wiring harnesses" by hand.

**Who buys vs who uses?** [FILL]
> Expected: the plant or operations manager buys. Operators use it: they "load the
> parts, say what counts as a good part, and handle the odd problem."

**Pick one customer. Walk us through how they use it.**
> [FILL: one of the 27, by name.] They send us their part free ("a short video or a
> drawing, how many you make and how you check it"). Then:
> - $1,000 to hold their place;
> - $5,000 to put the part on our bench, for "a yes or no, the test it has to pass in
>   writing and a fixed price";
> - $65,000 for the robot, "30% with the order, the rest when it passes your test on
>   your floor."

**How do you know people want this? / Need this?**
> "27 factories paid to be first in line" before the robot exists. [CONFIRM: amounts and
> dates.]

**What problem do you solve? / Why is it a big problem?**
> "A connector can look seated without being latched. Nobody notices until final test."
> And "every new product means weeks of programming," so the job stays manual.

**What do they do now? / What do they *really* do now?**
> They "still plug connectors by hand," and they find the bad ones at final test.
> [FILL: one real factory's process.]

**What does their day look like? / Which workflows break?** [FILL from a factory visit.]
> Expected: a worker plugs connector after connector, a plug looks seated but isn't
> latched, and it fails at final test.

**How many users / active / paying / signed up / used last week?**
> No robot is running yet: "we are building it now." 27 factories have paid to be first
> in line. [CONFIRM the split between $1,000 holds and $5,000 bench tests.]

**How many will you have in 3 months?** [FILL: a target.]

**Ideal customer? / Smallest segment? / Power user?**
> A factory that plugs many of the same connectors by hand, into boards or harnesses,
> and catches bad ones only at final test. "Bring us the job your team hates."

**What do users dislike about current solutions? / Wish they could do? / Why would they
switch?**
> Programming a robot takes "weeks of an engineer" for every new product. With us, "a
> new part is not a new project."

**What surprised you? / Unexpected use?** [FILL from customers.]
> From our tests: robots fail by being confidently wrong, passing crooked plugs as good,
> more than by missing the hole.

**What have you learned from users? / What do you understand about them?**
> 1. "A connector can look seated without being latched."
> 2. Setup, not the robot, is the cost: "Robots are cheap. Setting them up is not."
>
> [CONFIRM: which factory said which.]

**What objections do they have? / Why do reluctant ones hold back? / What resistance,
and how do you overcome it?**
> Will it work on *my* part, and at *my* speed? That's why the $5,000 bench test gives
> them a written yes or no first. And they pay the rest only "when it passes your test
> on your floor."

**How much time and money do they waste today?** [FILL: hours per new part, and the cost
of a bad connector found at final test.]

**Retention / churn?** No robots in service yet. $500 a month covers "support,
maintenance and updates."

**Technical or non-technical users?**
> Operators, not programmers: "No weeks of an engineer programming it."

**Will your first customers actually use it?**
> They only pay the rest "when it passes your test on your floor." Their team does only
> "load the parts, say what counts as a good part, and handle the odd problem." The open
> risk is cycle time, which is "not yet proven."

**Where do they need it most?**
> "Circuit boards and wiring harnesses" in "electronics and AI server factories."

In simulation, the robot's edge is largest where the part's position varies by 1-2 mm.

**How many customers have you spoken to? / How are you meeting customers?**
> [FILL: a number.] 27 paid to be first in line. They come in through the site: "Send us
> your part," and "we write back within one working day." [CONFIRM: where the 27 came
> from, and what the "Works with us" logos mean.]

**How are you understanding customer needs?**
> "We write back within one working day and ask about the part and how you check it."
> Every factory sends its part, its volume and its test.

**Who is (or will be) your first paying customer?**
> [CONFIRM: the first of the 27.] The first robot order is [FILL].

**Would they pay more for something better?** [FILL.]

---

## 3. Traction and growth

**What are your numbers? / Traction? / Growth rate? / How fast are you growing?**
> 27 factories paid to be first in line [CONFIRM: over how many weeks]. Robot revenue
> is $0 so far, "we are building it now."

Say "revenue is zero" plainly, and keep paid holds separate from orders.

**Where do new users come from? / How did early users find you? / Channels that work or
failed?** [CONFIRM.]
> The site's funnel: "Send us your part" free, then "Hold your place."

**How will you grow? / Distribution strategy? / How will customers find out about you?**
> - Direct to factories: "Send us your part."
> - Content: we're hiring a Technical Content Producer to "follow a robot test from setup
>   to result."
> - Every robot that passes on one floor is a reference for the next factory.

**What makes new users try you?**
> It costs nothing to ask: "Free. Send us your part." And "whatever you pay first comes
> off the price of your robot."

**Conversion rate? / Funnel? / Activation?** [FILL: site visits → parts sent → $1,000
holds → $5,000 bench tests.]

**How often do they come back? / Growth loops? / Virality?**
> Each new part is a repeat sale: "$5,000. Teach it a new part. Not a new project."

**How are you measuring success?**
> Units that pass, rejects caught, and how often a person steps in. From our job post:
> "Track cycle time, broken parts and how often a person steps in."

---

## 4. Business model

**How will you make money? / Pricing? / Who pays you? / First paid offering?**
> - "$65,000. One robot, running your part on your floor." "30% with the order. The
>   rest when it passes your test on your floor."
> - "$500 a month. Keep it running."
> - "$5,000. Teach it a new part."
> - Before the order: $1,000 to hold a place, $5,000 for the bench test. Both "come off
>   the price of your robot."

**How do you know they'll pay?**
> They already did: "27 factories paid to be first in line." [CONFIRM.]

**CAC? / LTV?**
> - CAC: [FILL]. Leads so far come from the site.
> - LTV per robot: $65,000, plus $6,000 a year in support, plus $5,000 per new part.
>   Five years with two new parts is about $105,000. That is illustrative arithmetic.

**Margins? / Total costs, fixed and marginal?** [FILL: cost to build one robot.]
> Arm prices start around $10k (UFactory 850) to $33k (UR3e), and a force sensor is
> about $3.7k (`hardware/BOM.md`). Cameras, the tester and the pallet system come on
> top.

**Burn rate? / Runway? / How long without funding? / Profitable when?** [FILL.]

**How much capital do you need? / How much are you raising? / Have you raised?** [FILL.]

**Long-term model?**
> Robots sold, plus recurring support, plus every new part, then "more jobs after that."

**Revenue potential? / Revenue in 3 and 12 months? / How much could you make a year?**
> - The 27 factories at one robot each: about $1.8M in orders, if they all convert.
> - [FILL: N factories x robots per factory x $65,000.]
> - [FILL: 3- and 12-month targets.]

**Aren't you just building custom software for every customer?**
> No. "A new part is not a new project. No weeks of an engineer programming it. A new
> fixture and the same tests." Our target is "half the engineering hours for the next
> part."

It's a target. The fixture is still made per part.

**How much are competitors making?** [FILL.]

---

## 5. Market and competition

**How big is the opportunity? / How many $B? / Growth? / Trends?**
> Bottom-up: [N] factories that plug connectors by hand, times $65,000 per robot, plus
> recurring revenue. The trend: AI server and electronics factories are building more
> boards and harnesses. Our blog's lead post: "The AI Inference Revolution Is Here."
> [FILL: a sourced number.]

**Who are your competitors? / Who do users compare you to?**
> - People plugging by hand.
> - Integrators who program each cell, "weeks of programming."
> - Cobot vendors' insertion routines: Flexiv and Robotiq spiral search, which insert but
>   don't test.
> - ABB and Nachi connector cells.

**Who might become competitors? / Which do you fear most?**
> Cobot makers or big integrators adding a test step. That's why we sell the whole job,
> "plugged in and tested," not a feature.

**Why are you better? / How will you win?**
> "It tests every one." And "a new part is not a new project."

In simulation, the standard routine passed 138-178 bad plugs per 7,400; ours passed 0.

**Why hasn't someone already done this? / Why isn't a big company doing it?**
> Every new product meant "weeks of programming," so the economics never worked for one
> connector job. "Robots are cheap. Setting them up is not."

**What stops Google or Amazon copying you? / What if a big company cloned you? / Is it
easy to copy?**
> The insertion is easy to copy. What's hard is the test on every unit, the logged
> verdicts, and making "a new part not a new project," built up part by part across the
> factories in line.

**"Someone pitched us this earlier and we didn't like it. What else do you have?"**
> Ask what they didn't like. Then: "We started from what goes wrong: a plug that looks
> seated but isn't. The robot tests every one."

---

## 6. Team

**Who are the founders? / Background? / Domain expertise? / Why are you the right team?
/ Why uniquely qualified?** [FILL.]
> Add: "Building the robot, starting with connectors," with offices in "San Francisco,
> Hong Kong and Shanghai."

**Who does what? / Who is the boss?** [FILL.]

**How did you meet? / Why did you get together? / What else have you built together?**
[FILL.]

**Will you stick at this? / Stick together? / How do you handle disagreements? / Why
dedicate your life to this? / Ten years?** [FILL.]

**Who would you hire next? / Key roles in 6-12 months?**
> As posted:
> - a Founding Robotics Engineer, Controls & Integration ($135-165k), "our first
>   robotics hire";
> - a Robot Learning Engineer, Manipulation ($150-180k);
> - a Technical Content Producer, on contract.

**What systems have you hacked? / Tough problem solved? / Impressive thing? / Something
surprising? / In what ways are you resourceful?** [FILL with your own.] Project
examples:
> - We found why our robot failed on one physics setting: the simulator ignored a
>   friction setting, so floor friction stopped the wall probe.
> - We found our own check could lift a seated plug when the force sensor drifts.

**How fast can you build?**
> First simulation on October 24. Six benchmark rounds by November 6.

**Biggest mistake?**
> Early on we claimed more than the data showed, for example "leads in all 13
> simulators." Now every test is pre-registered and we publish where we lose.

**Funniest thing / worst thing that happened?** [FILL: one short story each.]

**Open to changing the idea?**
> Yes. The data already changed it: the test turned out to be the product.

---

## 7. Vision and strategy

**What do you understand that others don't? / What do you know about this space that
others don't? / What do outsiders not understand? / Your secret?**
> "Robots are cheap. Setting them up is not." And the failure that matters isn't
> missing the port. It's "a connector can look seated without being latched," and
> "nobody notices until final test."

**Why this idea? / Why did you choose it?** [FILL: your story.]

**Why now?**
> "Robots are cheap." Arms start at $10-33k, so setup and testing are what's left.
> [FILL: the AI-server demand number.]

**Long-term vision / ten-year version / how is this a billion-dollar company / what
next / other areas to expand into?**
> "Starting with connectors." "More jobs after that": every assembly step where "is it
> actually connected?" matters. And every unit logged becomes data for the robot to
> learn new parts faster.

**Biggest risks / obstacles / hurdles / what keeps you up at night / biggest problem in
six months?**
> "Not yet proven: false passes from half-seated plugs, damage at seating force, pallet
> repeatability, cycle time, and safety near people." In six months, cycle time on real
> parts.

**Why will this company survive?** [FILL.]
> Every robot that passes on one floor makes the next part cheaper: "a new fixture and
> the same tests."

**Does the company have a clear and important mission?**
> "Bring us the job your team hates."

---

## 8. YC-specific

**What will you do if we don't fund you?**
> Keep building. 27 factories paid to be first in line, and they're waiting for the
> robot.

**Why YC? / What do you want most from YC?** [FILL.]
> Introductions to hardware and AI-server companies in YC who plug connectors, and help
> pricing a $65,000 robot.

**Why should we fund you?**
> Factories paid before the robot exists, and we know exactly what the product has to
> do: test every one.

**What will you do in the next 30 days? / What will you get done by demo day?**
> Build the robot and "run it on customer parts." First robot passing a customer's test
> on their floor. [FILL: how many of the 27 turn into orders.]

**If we gave you $500k today?**
> Build the robot, hire the two posted engineers, and turn the 27 into orders.

**Would you relocate to the US? / Reincorporate as a US company?**
> "Defex Robotics, Inc., a Delaware corporation," with San Francisco on the site.
> [CONFIRM where the founders live.]
