# YC interview questions, prioritized (for Hasan, CTO)

Every question gathered, with duplicates merged. The order:
1. Technical: you're the CTO, so you must own these.
2. The fundamentals almost every interview asks.
3. Unusual questions that are typical of YC.
4. Everything else.

★ marks a question written from this repo and from defexrobotics.com, because a partner
is likely to ask it. It is not in the public question banks.

Answers are in [`YC_ALL_QUESTIONS_AND_ANSWERS.md`](YC_ALL_QUESTIONS_AND_ANSWERS.md), in the
site's wording. The technical defense is in
[`HASAN_DEFENSE_NOTES.md`](HASAN_DEFENSE_NOTES.md) and
[`YC_ANSWERS_EXPLAINED.md`](YC_ANSWERS_EXPLAINED.md).

Sources:
- [ycombinator.com/interviews](https://www.ycombinator.com/interviews)
- [ycinsight.com](https://ycinsight.com/interview)
- [iPG](https://jamescun.github.io/iPG/)
- [surkyl/labs-yc-mock-interview-simulator](https://github.com/surkyl/labs-yc-mock-interview-simulator)
- the LinkedIn list of 14

---

## 1. Technical (CTO: know these cold)

**How it works**
1. How does this actually work? How does your product work in more detail?
2. Walk me through what the robot does with one connector, start to finish.
3. Where is the rocket science here? What's technically hard about what you're doing?
4. What's your tech insight? What did you build that others couldn't?
5. Do you have a demo? Show me the product. What's actually built? Show us.
6. ★ What exactly does the test check (seated, held, every wire), and how does the robot
   "feel" a latch click?
7. ★ How does the robot find the hole when the camera is off by 1-2 mm?
8. ★ How do the two cameras work (header camera, in-gripper check), and how accurate are
   they?
9. ★ How does the electrical test work: continuity and isolation on every wire?

**Against the standard method**
10. ★ How does it compare with spiral search, what cobot vendors ship?
11. ★ So why not just use spiral search? It's faster.
12. ★ Why are you slower? What does the check cost in seconds?
13. ★ Can't spiral search feel the walls too? What's actually different?
14. ★ What happens if you drop the check step? (Without it: 41 bad plugs against
    spiral's 40.)

**Proof and trust**
15. ★ Why should I trust a simulator? Simulators lie about contact.
16. ★ Has this ever touched a real robot? What would it take to prove it on hardware,
    and what does it cost?
17. ★ What is the cycle time on a real line?
18. ★ Has it ever passed a bad part?
19. ★ Is the 3-degree spec doing the work? What is the customer's real spec?
20. ★ Did you tune on your test set?
21. ★ Does the controller know things a real cell wouldn't?

**Failure modes ("not yet proven" on the site)**
22. ★ False passes from half-seated plugs: how will you prove there are none?
23. ★ Damage at seating force: can the push break the connector or the board?
24. ★ What happens when the force sensor drifts?
25. ★ What happens when the plug sits off-centre in the gripper?
26. ★ Can the plug move after the check, when the gripper lets go?
27. ★ Pallet repeatability: what if the board isn't where it should be?
28. ★ Safety near people: guarding, interlocks, cobot limits?

**AI, generality, engineering**
29. How much of what you're building is AI? ★ Where is the AI, if the search is "a
    fixed routine"?
30. ★ Why not learning, or end-to-end robot policies?
31. ★ How many connector types does it work on? What does "a new part is not a new
    project" mean technically?
32. ★ Which arm, force sensor and cameras, and why?
33. ★ Does a Python state machine fit a 2 ms control loop?
34. What's the hardest technical problem you solved recently? Tell us about a tough
    problem you solved.
35. How fast can you build? What have you shipped in the last month?
36. What part are you building first? What is the next step in the product's
    evolution?
37. What did you cut out of the product?
38. Will this be easy to copy? What stops Google, Amazon or a robot maker from copying
    you?

---

## 2. The fundamentals (asked in almost every interview)

1. What are you working on? What does your company do? What are you building? Be
   specific.
2. Who is your user? Who needs what you're making? Who would use it?
3. What problem are you solving for them? Why is it a big problem?
4. What do they do now to solve it? No, what do they *really* do now?
5. How do you know people want this? How do you know customers need it?
6. What are your numbers? Traction? How many users, paying users, active users?
7. What is your growth like? What is your user growth rate?
8. How will you make money? What's your pricing? Who pays you?
9. How much are they paying?
10. Who are your competitors? Why will you win?
11. How is your product different? What exactly makes you different from existing
    options?
12. Why now? What changed recently?
13. Why you? Why are you the right team? What domain expertise do you have?
14. Who are the founders? Who does what on the team?
15. What have you learned from your users? What surprised you about user behaviour?
16. How many customers have you spoken to? How are you meeting customers?
17. How are you selling? How will you get users? What is your distribution strategy?
18. Are people using it yet?
19. Who is your first paying customer, or who will be?
20. How big can this be? How big an opportunity is there?
21. What is the biggest risk? What obstacles will you face, and how will you overcome
    them?
22. What would you do with the YC money? If we gave you $500k today, what would you do?
23. What will you do if we don't fund you?
24. What are you going to do next?

---

## 3. Unusual questions (typical of YC)

1. Someone just showed us an idea like this right before you. I don't like it. What
   else do you have?
2. We see this idea a lot. Why will you be the one to crack it?
3. Aren't you just building custom software for every customer?
4. Pick one customer. Walk us through how they use your product.
5. Will your first customers actually use it?
6. Where do they need it most?
7. What will you get done by demo day?
8. What have you shipped in the last month?
9. What systems have you hacked?
10. Who is "the boss"?
11. How do we know your team will stick together? Will your team stick at this?
12. How did your team meet? Why did you get together? What else have you created
    together?
13. How do you handle disagreements?
14. Tell us something surprising you have done. What is the most impressive thing you
    have done?
15. In what ways are you resourceful?
16. What's the funniest thing that has happened to you?
17. What's the worst thing that has happened?
18. What's the biggest mistake you have made?
19. What do you personally struggle with?
20. What do you understand that others don't? What do you know about this space that
    others don't?
21. What are the key things about your field that outsiders don't understand?
22. Are you open to changing your idea?
23. Six months from now, what's going to be your biggest problem?
24. What keeps you up at night?
25. Why do you want to dedicate your life to this? Will you stick at this for 10 years?
26. Who will you be in 10 years?
27. Would you relocate to Silicon Valley or the US during YC?
28. Will you reincorporate as a US company?
29. What competition do you fear most?
30. What would you do if a large competitor cloned you?
31. Why isn't someone already doing this? Why hasn't someone won this market?
32. Have you considered [some twist on your idea]? Could this be a feature of a bigger
    product?
33. Why do you want YC? What's the biggest thing you want from YC? Why should we fund
    you?

---

## 4. Everything else

**Users and customers**
1. Who buys vs who uses? Who is your *actual* user?
2. What's your ideal customer profile? Smallest viable segment? Power user?
3. What does your user's average day look like? Which workflows break for them?
4. What do users wish current tools could do? What do they dislike about current
   solutions?
5. Why would they switch? Would they pay more for something better?
6. What objections do they have? Why do reluctant users hold back? How will you
   overcome the resistance?
7. What makes new users try you?
8. What is the moment users realize they need your product?
9. How much time and money do they waste before using your product?
10. What do these users currently pay to solve this problem?
11. Are your users technical or non-technical?
12. What are users doing with the product that you didn't expect?
13. How are you understanding customer needs?
14. Why are these users good users to try to solve problems for?
15. How many people are in your target market?
16. What other kinds of users could you go after later?

**Growth and metrics**

17. How many signed up? How many used it last week? How many will you have in 3 months?
18. Where do new users come from? How did your early users find you?
19. What channels work best? What channels failed?
20. What is your retention? Monthly retention? Why do some users churn?
21. What's your conversion rate? Acquisition funnel conversion rate?
22. What's your activation metric?
23. How often do people come back?
24. What growth loops exist? Do you have virality?
25. What do successful users do differently?
26. How are you measuring success?

**Business model and money**

27. How do you know people will pay for this?
28. What is your first paid offering?
29. What is customer acquisition cost? What is lifetime value?
30. What are your margins? Total costs, fixed and marginal? What are your unit
    economics?
31. What is your burn rate? How long can you go without funding?
32. Are you profitable? When will you be?
33. How much capital do you need? How much are you raising? Have you raised funding?
34. What is the long-term business model?
35. What will your revenue be in 3 months? 12 months? How much money could you make per
    year?
36. How much are your competitors making? How many users do they have?

**Market**

37. How many billions is the market? How fast is it growing?
38. What trends support your idea, in your market and related ones?
39. Who might become competitors? Who do users compare you to?
40. Why isn't a big company doing this?

**Team**

41. What is your background?
42. Who would you hire first? Which key roles do you need in the next 6-12 months?
43. Why did you choose this idea? Why did you pick it?
44. Why are you uniquely qualified to work on this?

**Vision**

45. What's your long-term vision? The 10-year version?
46. How does this become a billion-dollar company?
47. If you succeed, what will be your next product? What else could you expand into?
48. Why will this company survive long-term?
49. Does this company have a clear and important mission?
50. What's your unfair advantage? What's your secret insight?
