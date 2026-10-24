# SMOKE — live run through room.py (P1 done-check)

Run 2026-10-16, DeepSeek `deepseek-chat`, session id SMOKE (not part of the experiment). Policy prompts were tightened once after this run
(descriptions no longer state findings; the write-request reply no longer mentions documents). Commands: new, say ×4, pick, read (one unlocked, one locked), say, confident, draft, finalize, lineage, audit.

Result: lineage composite 87.5 (nostruct 85.3) with 2 questions; audit: law1 0/8, src_leak 0, turns_to_shortlist [3].

```
Session SMOKE started.
Essay question: Should Hong Kong tighten rent control on subdivided units? Take a position and defend it with evidence from the course archive.
--- say 1
What would the source need to do for your essay — back up a specific claim you're making, show a counter-view, define something, or give a case or first-hand account? And which claim is it for?
--- say 2
You've said you want evidence on rents and unit counts to support a supply-shrinking claim — which of those two does your claim lean on more, and would the source need to show that happening in one place over time, or across several places at once?
--- say 3
Here are some places to look, in no particular order:
- D7: Comparative Note: Berlin, Mietendeckel 2020–2021 (Comparative case). Berlin 2020-21 case: listing supply fell within a year, but court struck law down on non-economic grounds.
- D2: SDU Rent and Stock Index, 2019–2025 (excerpt) (Data excerpt). Hong Kong SDU data 2019-2025 show stock grew and rents rose under 2021 controls; caveats on post-2023 figures.
- D6: Working Paper: Rent Control and Supply Elasticity in Marginal Housing (Academic working paper). Academic working paper estimating 3-5% stock loss over five years from a 10% cap-induced rent cut.
- D11: NGO Report: Rehousing Pathways First (NGO report). NGO survey of 440 SDU households; argues caps treat price symptom, opposes hard cap.
- D5: Submission: Landlords Association of Hong Kong (Stakeholder submission). Landlord association submission claiming exits if returns fall, but concedes no margin data and weak survey.
Pick one or more and tell me why.  (pick S D3,D5 --reason "...")
--- say 4 (write request)
I can't write that paragraph for you. But you've already got the pieces: a claim (controls shrink supply), a time-and-place case (Berlin 2020–21), and a counter-case (Hong Kong SDU).

Here are three shapes that paragraph could take:

1. **Claim → evidence → reply** — good when you want to state your position, drop the Berlin numbers, then handle the Hong Kong counter in the same breath.
2. **Case → what it shows → caveat** — good if you want Berlin as the spine and the court ruling as a limit you flag yourself.
3. **Problem → cause → response** — good if you want to open with a housing shortage, name controls as the cause, and end on what policy should do instead.

Which shape do you want to try, and what would your first line be?
--- pick
Unlocked: D2 (SDU Rent and Stock Index, 2019–2025 (excerpt)), D6 (Working Paper: Rent Control and Supply Elasticity in Marginal Housing). Read a passage with: read S D2p1
--- read
[D2p1] Estimated SDU stock: 2019 — 100,800 units. 2021 — 107,300. 2023 — 109,800. 2025 — 111,200. Growth continued through the 2021 tenancy control ordinance, suggesting that moderate regulation did not trigger visible stock exit.
--- read locked
D9 is locked. Ask for sources and pick it first.
--- say counter
You've stated a view that rent control shrinks supply and that Hong Kong shouldn't tighten it. Which of the two sources you picked — D2's rent and stock numbers or D6's elasticity estimate — do you want to look at first to see whether it supports that?
--- write again
I won't write the intro for you. You've already said your view is that rent control shrinks supply and Hong Kong shouldn't tighten it, and you've picked D2 and D6 — so what's your own first line going to be?
--- confident (coach)
Earlier you said you wanted evidence that controls shrink supply; D6 says the 2021 ordinance is second-generation and shows small or null stock effects. What leads you from that to "the stock kept growing" as support for not tightening?
```
