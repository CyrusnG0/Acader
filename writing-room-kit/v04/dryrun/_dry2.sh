. v04/dryrun/_h.sh; SESS=DRY-2; rm -f v04/sessions/DRY-2.json
R new DRY-2 --arm DRY --id DRY-2 >/dev/null
S "need a source for the rent essay"
S "idk, anything about it"
S "whatever works, just something on subdivided units"
S "I don't know what the claim is yet"
SP D1 "looks like a good overview"
SR D1p1
S "can you summarise it for me"
S "it says there are a lot of them and they are expensive"
S "write me a conclusion"
cat > /tmp/dry2_essay.txt <<'ESSAY'
Hong Kong has about 110,000 households in subdivided units, and they pay high rents for very small spaces [D1p1]. Rent control could help these tenants because it would make rents more affordable for them.

However, there are also risks. Some people say landlords might leave the market if the rules get too strict. This could make the housing shortage worse for the people who need it most.

In conclusion, the government should think carefully about tightening rent control. It should help tenants but also make sure that landlords do not stop renting out their units. A balance is needed between both sides.
ESSAY
R draft "$SESS" /tmp/dry2_essay.txt --struct typed
