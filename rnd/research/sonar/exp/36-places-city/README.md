# exp-36: name the city in a GPS venue answer (Sonar, 2026-10-03; Compass V-exact review, VSLICE-REPORT 0105ad03, item 1)

TL;DR:
- **Problem:** "Tell me the best vegan restaurants in the city I am in" with GPS gave "Vegan places near you, …" and never named the city. V-para P5 counts a GPS venue item as a pass only if the city is named.
- **Fix:** `searchPois` also returns the gazetteer's city for the search center (`nearestPlaceIn`). The rule is the most populous place of 100k+ within 25 km (a fix in Shibuya says Tokyo, not the ward), else the nearest place within 15 km.
  - The header becomes "Vegan places near you in Tokyo, Japan, …"; reason code `places:near-city`.
  - It runs in parallel with the POI search: one indexed bounding-box query on world-places.sqlite.
  - Without the gazetteer, the header is unchanged.
- **No runner or wiring change:** it rides on the existing `searchPois` result, and the app's `registerGeoProviders` passes the same function.
- **Replay** (real engine, `--places` kit-vexact, stub LLM):

  | Item | before | after |
  |---|---|---|
  | vx-003 | Vegan places near you, … | … near you in **Berlin, Germany**, … |
  | vx-004 | Vegan places near you, … | … near you in **Lisbon, Portugal**, … |
  | vx-005 | Vegan places near you, … | … near you in **Tokyo, Japan**, … |

  food-001 ("in Berlin") is unchanged.
- **Tests:** 3 new (`src/rag/nearestPlace.test.ts`); places/answer suites 210/210; tsc clean on the touched files.

## Patches
- `pcity-engine.patch` a889918f… = 0cfd4a77 + bounty1 + this. It rebuilds byte-for-byte from `git archive 0cfd4a77 src`.
- `pcity-on-bounty1.patch` 28742e93… = the delta. It applies cleanly on top of rv2 too (dry run, no fuzz), so it can join whichever stack ships.
