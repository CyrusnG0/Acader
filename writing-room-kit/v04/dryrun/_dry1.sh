. v04/dryrun/_h.sh; SESS=DRY-1; rm -f v04/sessions/DRY-1.json
R new DRY-1 --arm DRY --id DRY-1 >/dev/null
S "I'm starting the rent control essay and I know nothing about subdivided units. Can you find me a source to start?"
S "Mostly I need to understand the basic situation first: who lives in these units and what the rents are like."
SP D1,D3 "D1 is a primer so I can learn the basics, and D3 is a tenant's own account so I get a real person's view of rent and income"
SR D1p1
SR D3p1
S "I think SDU tenants pay a high share of their income on rent, so there is a case for some cap. Mr Chan pays about a third of his household income."
SR D3p2
S "Can you find me a source with the other side, like what landlords or economists say about caps?"
S "I want to know whether landlords would really leave the market if rents are capped, and whether the data shows it."
SP D5,D2 "D5 is the landlords' own claim that they would leave, and D2 has rent and unit numbers to check whether that happened"
SR D5p2
SR D2p1
S "The stock kept growing from 2019 to 2025 even after a 2021 control. So I think the landlord exit threat is weaker than they say."
S "Who argues against that? I'd like to hear the strongest objection."
S "I would say the 2021 control was mild, and a hard cap is a different thing, so the data may not carry over. I need a source on what a hard cap would do to the number of units."
SP D6 "D6 is the academic working paper on whether caps shrink supply, which is the objection I have to answer"
SR D6p2
S "How could I structure the essay? I have a position and two kinds of evidence."
S "I'll take the first one, claim then evidence then objection then reply. My claim: tightening in a measured way is defensible, but a hard cap is risky."
cat > /tmp/dry1_essay.txt <<'ESSAY'
Hong Kong can tighten rent control on subdivided units, but it should do so in a measured way and avoid a hard cap on initial rents.

The case for acting starts with the tenants. Mr Chan pays 5,800 dollars for a 120 sq ft cubicle, about a third of his household income [D3p1]. Across the market, SDU tenants pay a premium of 15 to 25 percent per square foot compared with mainstream flats [D1p1].

The landlords warn that members will leave the market if returns fall below mortgage cost [D5p2]. The stock numbers do not show that so far: the estimated stock grew from 100,800 units in 2019 to 111,200 in 2025, including after the 2021 tenancy control [D2p1].

The strongest objection is that the 2021 control was mild, so that growth says little about a hard cap. The working paper argues exactly this, and estimates that a binding cap would cost the market part of its stock over five years [D6p2]. I accept that, which is why I would tighten gradually and watch the stock figures before going further.
ESSAY
R draft "$SESS" /tmp/dry1_essay.txt --struct typed
