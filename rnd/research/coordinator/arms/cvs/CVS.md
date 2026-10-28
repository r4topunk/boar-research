# CVS: CV rev1 + fact sanity guard on cut 3 (engine engineer, 2026-10-05, DEV only; criterion arms/cvs/CVS-criterion.md, not edited)

TL;DR: branch `coord/cvs` (wt/cvs, from coord/cv = CV rev1 a2b2c9c0), one new file `src/routing/factSanity.ts` + 3 call sites in `computedVerdict.ts`; nothing else changed. Not run on any gate.

## What the guard does
- **Entity class** from the entity's name (keyword lists): ship, building, bridge, river, mountain, celestial (planets, moons, stars), country. A name with city/state/county/province/region, or no keyword, has no class and no range check.
- **Ranges** (checked on the 4B's figure by class and the figure's dimension): ship/building/bridge length 0.5 m–5 km; river length 10–7,500 km; mountain height 100–9,000 m; celestial mass 1e19–1e32 kg and size 100 km–2e11 m; country population 1e3–2e9; any year -3000..current year.
- **Pair rule:** two entities of the same known class whose length or mass differ by more than 100x: abstain. Different or unknown classes: allowed.
- Any failure makes `computeCompare / computeThreshold / computeYear` return null, so CV abstains and cut 3's normal path answers. Figures given in the question are never checked.
- Spec gaps, as specified: Congo 2,090 km is inside the river range, so the third gate failure is NOT caught (no class rule can know it). The same-class 100x rule also abstains on true comparisons of planets by mass (Jupiter vs Earth is 318x) and of a skyscraper vs a small bridge; it is by class, as the criterion says.

## Tests and build
- vitest 1364/1364 (CV rev1 had 1353: +11 new tests in factSanity.test.ts, covering: classes, mass without exponent (Jupiter 1,898 kg), ship in km (Titanic 269 km), river under 10 km, mountain too high, population without scale, dates, unknown class passes, pair 100x, and CV abstain end to end); tsc clean; applies cleanly to a fresh git archive 0cfd4a77.
- Patch `arms/cvs/cvs-on-cut3.vs-0cfd4a77.patch` sha256 17bc6db9ce283d3cf8d3e9d9834ec41b7a70f183307d463f0c5c04b1ac1671ea.

## DEV effect (arms/cvs/cvs-dev-replay.mts, cvs-dev-replay.txt)
The cv-dev-cv-s44 traces carry the rendered Facts lines, so the figures were re-read from them (115 figures from the 89 CV answers in rev1 scope: compare/threshold/year) and passed to the guard: it would turn **1 of 89** into an abstain: vgq-062 (Moon mass 7.342e19 kg vs Pluto 1.303e22 kg: inside the mass range, caught by the 100x same-class rule). The other DEV facts are plausible by class, so the guard does not fire on them. The DEV probes had no ship/bridge slips, so the three gate-failure types are covered by unit tests, not DEV evidence.

## UNKNOWN
- Real-traffic effect of the class keyword lists (recall is limited to named classes; a country, ship or mountain not in the lists is unchecked).
- Facts the 4B gets wrong but plausible (Danube 2,010 km, Congo 2,090 km) pass; CVS cannot fix them.
- Gate not run (set #3 pending).
