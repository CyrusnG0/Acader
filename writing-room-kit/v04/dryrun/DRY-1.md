# DRY-1 - honest student

**Audit:** law-1 violations 0 of 13 assistant turns; source leaks 0; student turns to each shortlist [2, 2].

About 20 student turns: 3 source requests (2 shortlists served after 2 student answers), 3 picks with reasons, 6 reads, own claims, one counter-claim, a structure request, one draft. I (the executor) played the student, so this shows the assistant, not a real student.
Final essay (not shown below) has 5 citations, all from passages read. Coherence report: composite 95.6, claim 87.5, 2 questions, both about figures the student read in a passage and then quoted (see the note in PREREG-v0.4.md, section 'Open design notes').

Transcript = what the student sees. `STUDENT>` lines are what I typed.

```text
STUDENT> I'm starting the rent control essay and I know nothing about subdivided units. Can you find me a source to start?
What would you need that source to show for your essay — for example, evidence for a specific claim, a counter-view, a definition, or a first-hand account — and which claim would it be supporting?

STUDENT> Mostly I need to understand the basic situation first: who lives in these units and what the rents are like.
Here are some places to look, in no particular order:
- D1: Subdivided Housing in Hong Kong: A Primer (Policy brief). Policy brief primer giving basic SDU context: who lives there, rent levels, and policy debate.
- D2: SDU Rent and Stock Index, 2019–2025 (excerpt) (Data excerpt). Data excerpt tracking SDU stock and rents from 2019 to 2025, with caveats.
- D3: Tenant Interview: Mr Chan, Kwai Chung (Interview). Interview with a tenant describing his living situation, rent, and views.
- D11: NGO Report: Rehousing Pathways First (NGO report). NGO report surveying tenants and arguing for rehousing pathways over hard rent caps.
- D6: Working Paper: Rent Control and Supply Elasticity in Marginal Housing (Academic working paper). Academic working paper modeling rent control effects on supply and welfare.
Pick one or more (by id) and tell me why.

STUDENT> (pick D1,D3) D1 is a primer so I can learn the basics, and D3 is a tenant's own account so I get a real person's view of rent and income
Unlocked: D1 (Subdivided Housing in Hong Kong: A Primer), D3 (Tenant Interview: Mr Chan, Kwai Chung). You can now read their passages by id, for example D1p1.

STUDENT> (read D1p1)
[D1p1] About 110,000 households in Hong Kong live in subdivided units (SDUs): flats carved into small cubicles, often with shared kitchens and bathrooms. Median SDU rent is roughly 30 percent below mainstream private flats, but on a per-square-foot basis SDU tenants pay a premium of 15 to 25 percent, because space is carved and priced at its most desperate margin.

STUDENT> (read D3p1)
[D3p1] Mr Chan, 41, delivery driver, lives with his wife and two children in a 120 sq ft cubicle. He moved in after a factory injury. Rent is 5,800 dollars, about a third of household income. He says the worst part is not price but insecurity: the landlord ended his previous tenancy with two weeks notice when he asked to repair a leaking window.

STUDENT> I think SDU tenants pay a high share of their income on rent, so there is a case for some cap. Mr Chan pays about a third of his household income.
You're noting that Mr Chan spends about a third of household income on rent, and that this supports a case for some cap. What would you want to check next — for instance, whether a third is typical across SDU tenants, or what a cap would do to the rent he pays?

STUDENT> (read D3p2)
[D3p2] On the proposed tightening he is split. A hard cap would free maybe 800 dollars a month, which is food for a month. But he fears landlords would rather convert cubicles back to storage rooms than deal with regulated tenants. He has seen two units on his floor emptied and locked for a year.

STUDENT> Can you find me a source with the other side, like what landlords or economists say about caps?
You've said you want "the other side" from landlords or economists. Before I point anywhere, what would that source need to show for your essay — is it evidence against a claim you're making, or a counter-view you plan to answer?

STUDENT> I want to know whether landlords would really leave the market if rents are capped, and whether the data shows it.
Here are some places to look, in no particular order:
- D11: NGO Report: Rehousing Pathways First (NGO report). NGO report surveying tenants, arguing against hard caps and for tenure security instead.
- D6: Working Paper: Rent Control and Supply Elasticity in Marginal Housing (Academic working paper). Academic working paper modeling supply elasticity, distinguishing first- and second-generation rent controls.
- D7: Comparative Note: Berlin, Mietendeckel 2020–2021 (Comparative case). Comparative case study of Berlin's 2020–2021 rent cap and its aftermath.
- D2: SDU Rent and Stock Index, 2019–2025 (excerpt) (Data excerpt). Data excerpt from an index tracking SDU stock and rents from 2019 to 2025.
- D5: Submission: Landlords Association of Hong Kong (Stakeholder submission). Stakeholder submission from a landlords association opposing hard rent caps.
Pick one or more (by id) and tell me why.

STUDENT> (pick D5,D2) D5 is the landlords' own claim that they would leave, and D2 has rent and unit numbers to check whether that happened
Unlocked: D5 (Submission: Landlords Association of Hong Kong), D2 (SDU Rent and Stock Index, 2019–2025 (excerpt)). You can now read their passages by id, for example D5p1.

STUDENT> (read D5p2)
[D5p2] It commits that members will exit the segment if returns fall below mortgage cost: every unit converted back, locker rooms or simply emptied, removes housing that, however poor, houses someone tonight.

STUDENT> (read D2p1)
[D2p1] Estimated SDU stock: 2019 — 100,800 units. 2021 — 107,300. 2023 — 109,800. 2025 — 111,200. Growth continued through the 2021 tenancy control ordinance, suggesting that moderate regulation did not trigger visible stock exit.

STUDENT> The stock kept growing from 2019 to 2025 even after a 2021 control. So I think the landlord exit threat is weaker than they say.
You're reading the 2019–2025 stock trend as evidence that the exit threat is weaker than the landlords' submission claims. What would you want to check in D2 or D5 next — for example, whether the index counts units or buildings, or what the landlords say specifically about exiting?

STUDENT> Who argues against that? I'd like to hear the strongest objection.
Document D6, the working paper on rent control and supply elasticity, argues that the stable stock you're pointing to may be an artifact of the 2021 ordinance being a non-binding, second-generation instrument — and that a binding cap on initial rent levels behaves differently, with contraction effects that the current stability would not reveal.

How do you answer this?

STUDENT> I would say the 2021 control was mild, and a hard cap is a different thing, so the data may not carry over. I need a source on what a hard cap would do to the number of units.
You've said the 2021 control was mild and a hard cap is different, so that data may not carry over. For the claim you want to make about a hard cap and the number of units, what would a source need to show you — evidence of a hard cap's effect, a counter-view, or something else?

STUDENT> (pick D6) D6 is the academic working paper on whether caps shrink supply, which is the objection I have to answer
Unlocked: D6 (Working Paper: Rent Control and Supply Elasticity in Marginal Housing). You can now read their passages by id, for example D6p1.

STUDENT> (read D6p2)
[D6p2] Crucially, the paper distinguishes first-generation controls (hard caps on levels) from second-generation controls (caps on increases within tenancies). First-generation controls show consistent contraction effects; second-generation show small or null effects on stock — the 2021 Hong Kong ordinance is second-generation, which explains the stable stock in the D2 index.

STUDENT> How could I structure the essay? I have a position and two kinds of evidence.
Three tracks you could try:

- Claim, evidence, objection, reply — good if you want your cap argument to lead and D6 to be answered directly.
- Problem, cause, response — good if you want to start from tenant rent burden and build to a policy fix.
- Compare and contrast — good if you want the 2021 mild control and a hard cap set side by side throughout.

Which one fits what you want to say, and why?

STUDENT> I'll take the first one, claim then evidence then objection then reply. My claim: tightening in a measured way is defensible, but a hard cap is risky.
You've picked claim, evidence, objection, reply, with the claim that measured tightening is defensible but a hard cap is risky. Where in that track does Mr Chan's one-third-of-income figure do its work — is it part of the claim, or the evidence for it?
Draft 1 saved (180 words).
```
