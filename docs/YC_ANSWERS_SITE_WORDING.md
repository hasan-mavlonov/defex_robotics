# YC answers in defexrobotics.com's own wording

The live site was read on 2026-11-06. Its full text is in
[`SITE_SNAPSHOT_2026-11-06.md`](SITE_SNAPSHOT_2026-11-06.md). Phrases in "quotes" are
copied from the site. **Backed by** points to evidence in this repo. `[CONFIRM]` marks a
site claim that only you can back up, and YC will ask about every one of them.

**Where this file disagrees with `YC_INTERVIEW_PREP.md` and `YC_ANSWERS_EXPLAINED.md`,
this file wins.** Those files were written before the site was read. They assumed
software sold per cell and zero customers. The site sells a **$65,000 robot** and says
**"27 factories paid to be first in line."**

---

## 0. Fix or prepare these before the interview

| # | Issue | Why it matters | What to do |
|---|---|---|---|
| 1 | "27 factories paid to be first in line." | YC will ask: which ones, paid what, when, and can we call one? | Know the exact list, the amounts ($1,000 holds? $5,000 bench tests?), the total and the dates. If any of the 27 are friends or family, say so. |
| 2 | The "Partners" strip lists NVIDIA, Andreessen Horowitz, Google, AWS, Microsoft Azure, Lambda and others. | A partner will ask what "partner" means. If these are startup credit programs (NVIDIA Inception, AWS Activate and similar), calling a16z a partner reads as a misleading claim. | Be ready to say exactly what each one is. Consider relabelling the strip "Programs" or "Credits from" if that is what they are. |
| 3 | "AI-powered robots" | The site's own prototype page says the search is "a fixed routine, not a trained robot policy." In this repo, the learned prior (G) gave no gain on the clean held-out test. Expect "Where is the AI?" | Answer: "Today it's cameras plus force control. Learning from demonstrations is what our Robot Learning Engineer role is for." |
| 4 | The site and the repo describe slightly different checks. | Site: "The latch force signature, a pull, and continuity and isolation on every wire." Repo: wall probes, twist and lean straightening, latch click and pull. There is no electrical test in the repo. Site: "A compliant press lets the chamfer guide it home. A search is only a fallback." That is closer to the repo's J (RCC press plus Defex's check) than to C. | Pick one story. The repo's strongest result supports the site: the test is the product. Without VERIFY, Defex called 41 crooked plugs good, the same as spiral search's 40; with it, 0 (`results/v0.2g_noverify_dev`). |
| 5 | "Half the engineering hours for the next part" | The site labels it "Target." Nothing in the repo measures setup time. | Always say "our target," never "we cut it in half." |
| 6 | Team | The careers page says "You'll work with the founders." | Know who the founders are and who does what. |
| 7 | Logos under "Works with us": ghost, GRAND, UzChasys, ATH, NOVA Solutions, Artel, Texnopark | YC will ask what each relationship is. | Know each one: customer, pilot, letter of intent, or advisor. |

---

## 1. The ten questions from ycinsight.com/interview

### 1. What does your company do?
> **"Defex is building AI-powered robots that plug connectors into circuit boards and
> wiring harnesses, then test that each one is actually connected. For electronics and
> AI server factories."**

If they ask how far along:
> "We are building it now." 27 factories have paid to be first in line. Today we have a
> simulation of the robot; you can try it on our site at /prototype.

### 2. Why now?
> "Robots are cheap. Setting them up is not." The arm is no longer the expensive part.
> But "every new product means weeks of programming. So factories still plug connectors
> by hand." And electronics and AI server factories are building more boards and
> harnesses than ever. [CONFIRM: a number with a source.]

- **Backed by:** cobot prices in `hardware/BOM.md` (UR3e about $33k, UFactory 850
  about $9.9k), and a 6-axis force sensor for about $3.7k.
- **The site's blog:** "The AI Inference Revolution Is Here: today's tidal wave of
  queries is forcing hardware makers to pivot."

### 3. Who's your competition? Why will you win?
> - **People:** factories plug connectors by hand and catch mistakes at final test.
> - **Robot integrators:** they program each cell, which means "weeks of programming"
>   for every new product.
> - **Cobot vendors' insertion routines:** Flexiv and Robotiq ship spiral search. It
>   pushes the connector in, but it doesn't test it.
> - **Big automation makers:** ABB and Nachi connector cells.
>
> We win on two things:
> - "It tests every one": seated, held and every wire, on every unit.
> - "A new part is not a new project": a new fixture and the same tests.

**Backed by:** spiral search called 138-178 bad plugs good per 7,400 good parts; Defex
called 0 (`results/v0.2f_evidence/BAD_UNITS.md`).

### 4. Why you?
[FILL: the founders, how you met, what you've built.] Add from the site and repo:
> We're "building the robot, starting with connectors." We've already built a full
> simulation of the cell and tested it against what vendors ship. We publish where we
> lose. 27 factories paid to be first in line before the robot exists.

### 5. What's your growth?
> 27 factories paid to be first in line. [CONFIRM: over how many weeks, how much in
> total, how many at $1,000 and how many at $5,000.] Revenue from robots: none yet, "we
> are building it now."

### 6. What have you learned from your users?
In the site's wording, the two things factories told you:
> 1. "By hand, a connector can look seated without being latched. Nobody notices until
>    final test."
> 2. "Every new product means weeks of programming." That's why "factories still plug
>    connectors by hand."
>
> So we built the test into the robot, and made "a new part not a new project."

[CONFIRM: which factory told you each one, and what you changed after hearing it.]

### 7. How big can this be?
Bottom-up from the site's prices (the arithmetic is illustrative):
> - **Each robot:** $65,000, plus $500 a month to keep it running, plus $5,000 each time
>   it learns a new part.
> - **If all 27 factories in line bought one robot:** 27 x $65,000 = about $1.8M in
>   orders.
> - **The big number:** [N] factories x [robots per factory] x $65,000, plus recurring
>   support and new parts. "Starting with connectors", then "more jobs after that."

[FILL N from your factory research.] Never quote a top-down TAM.

### 8. What would you do with the money?
> Build the robot and "run it on customer parts." Hire our first two engineers, already
> posted on the site:
> - a Founding Robotics Engineer, Controls & Integration ($135-165k);
> - a Robot Learning Engineer, Manipulation ($150-180k).
>
> Then turn the 27 factories in line into robot orders.

**Backed by:** rig hardware costs in `hardware/BOM.md` and the test plan in
`hardware/TEST_PROTOCOL.md`.

### 9. What's the hardest thing about this business?
Use the site's own list. It's honest and specific:
> "Not yet proven: false passes from half-seated plugs, damage at seating force, pallet
> repeatability, cycle time, and safety near people."

Cycle time is the one to lead with. In simulation, the check costs about 2 seconds per
part (`results/v0.2f_evidence/PHASES.md`).

### 10. If we don't fund you, what will you do?
> Keep building. 27 factories already paid to be first in line, and they're waiting for
> the robot.

---

## 2. The fourteen questions (LinkedIn list)

### 1. What are you building? Be specific.
Use the site's "Meet the robot":
> - **"Your part."** "Your board rides in on its pallet."
> - **"Vision."** "One camera finds the header. One below checks the plug in the
>   fingers."
> - **"Touch."** "It presses, feels the latch click, then pulls. A plug that moves
>   fails."
> - **"Tester."** "Seated? Held? Every wire? The light says pass or fail."
> - **"Brain."** "Every unit logged: what it saw, what it felt, the verdict."
> - **"Reset."** "Next unit in. Good ones to the tote. Rejects locked away."

### 2. Pick one customer. Walk us through how they use your product.
Use one of the 27, by name: [FILL]. The path, from the site's pricing:
> 1. **Free:** they "send us your part. A short video or a drawing, how many you make
>    and how you check it." We tell them if it's a fit.
> 2. **$1,000:** "Hold your place." It's refunded if it isn't a fit.
> 3. **$5,000:** "Put your part on our bench." They get "a yes or no, the test it has to
>    pass in writing and a fixed price for your robot." They only pay for a yes.
> 4. **$65,000:** "One robot, running your part on your floor." "30% with the order. The
>    rest when it passes your test on your floor."
> 5. **Every day after that:** their team will "load the parts, say what counts as a
>    good part, and handle the odd problem. The robot does the rest."

### 3. What does your product actually do for them?
> "Plugged in and tested." "The robot checks seated, held and every wire on every
> unit." "Good ones to the tote. Rejects locked away." They stop finding bad connectors
> at final test. And "a new part is not a new project."

**Backed by:** 0 bad plugs called good, against spiral search's 138-178 per 7,400
(simulation).

### 4. Are people using it yet?
> Not yet. "We are building it now." What you can use today is the interactive
> simulation of the robot at defexrobotics.com/prototype. "27 factories have paid to be
> first in line."

### 5. How much are they paying?
> [CONFIRM the real split.] The site's options: $1,000 to hold a place, $5,000 to put
> their part on our bench. "Whatever you pay first comes off the price of your robot."
> The robot is $65,000, plus $500 a month.

### 6. We see this idea a lot. Why will you be the one to crack it?
> Most teams try to make the robot insert smarter. We think the real problem is what
> happens around the insertion:
> - "a connector can look seated without being latched", so the robot must test every
>   one;
> - "every new product means weeks of programming", so "a new part is not a new
>   project."
>
> In our simulation we even turned off our own test step. Without it, our robot passed
> as many bad plugs as spiral search: 41 against 40. With it, zero. So we know the test
> is the product. And 27 factories paid before the robot exists.

**Backed by:** `results/v0.2g_noverify_dev/REPORT.md`.

### 7. Aren't you just building custom software for every customer?
> No. "A new part is not a new project. No weeks of an engineer programming it. A new
> fixture and the same tests." Teaching it a new part is a fixed $5,000. Our target is
> "half the engineering hours for the next part."

Be honest if pushed:
> The fixture is still per part, and "half the hours" is a target we haven't measured
> yet.

### 8. What will you get done by demo day?
> Build the robot and "run it on customer parts", the site's "Next." First robot passing
> a customer's test on their floor, which is when the other 70% gets paid. [FILL: how
> many of the 27 turn into $65,000 orders.]

### 9. Who does what on the team?
[FILL: the founders and their roles.] Then:
> Hiring next, as posted: a Founding Robotics Engineer, "our first robotics hire", and a
> Robot Learning Engineer. A content producer films the tests.

### 10. How many customers have you spoken to?
> [FILL: total conversations.] 27 of them paid to be first in line. [CONFIRM what the
> "Works with us" logos mean: ghost, GRAND, UzChasys, ATH, NOVA Solutions, Artel,
> Texnopark.]

### 11. How are you selling?
> Straight from the site: "send us your part" free, then "hold your place" for $1,000,
> then "put your part on our bench" for $5,000, then the robot at $65,000. "Whatever you
> pay first comes off the price of your robot." "We write back within one working day."

### 12. What's actually built? Show us.
> - **The interactive prototype:** a MuJoCo simulation of the plug and socket at
>   defexrobotics.com/prototype. Open it and run "Aligned," "Misaligned," "Open circuit"
>   and "No latch." In the site's words: "The complete cycle is a scripted illustration.
>   Forces are examples."
> - **The engineering simulation behind it, in this repo:** a gantry and a UR5e arm,
>   about 100,000 paired trials per benchmark round, and 315 automated tests.
> - **Not built:** the robot itself.

### 13. Will your first customers actually use it?
> They only pay the rest "when it passes your test on your floor," so it has to work on
> their line to get paid. Their team keeps doing what's easy: "load the parts, say what
> counts as a good part, and handle the odd problem." The open risk is cycle time, which
> is "not yet proven."

### 14. Where do they need it most?
> "Circuit boards and wiring harnesses" in "electronics and AI server factories." "Bring
> us the job your team hates": the connector step they still do by hand.

**Backed by:** in simulation, the robot's advantage shows up when the part's position
varies by 1-2 mm, as on boards and harnesses in final assembly (picture 5 in
`YC_ANSWERS_EXPLAINED.md`).
