# Travel-distance calculator (EN): V-exact Paris–Rome 0.29 → 0.89 (Anvil, 2026-10-03, dev)

**TL;DR:** "How far is it to walk from Paris to Rome and back?" failed on the 4B for three reasons:
- retrieval returned an irrelevant Wikivoyage Florence line;
- from memory it said "~1,200 km… not feasible";
- the 2-3-sentence style left no room for the breakdown.

Even with oracle text in context it scored 0.25–0.43, refusing to compute. A deterministic calculator route (an EN pattern, two cities from a bundled GeoNames table, great-circle × a stated route factor, round trip, time at a stated pace, always labelled an estimate) answers it instantly:
- **judge.v1 0.89 on V-exact** (engine 0.29, Haiku no-web 0.62);
- **0.86 on v0.1** vit-trv-004.

| File | sha256 | What |
|---|---|---|
| `travel-calc-on-b6h13-coldload.patch` | `44ddc6bb…` | on b6-on-health13 (6f841ab6) + gate-coldload (f3beb7dd). Adds `src/routing/travelDistance.ts`, `worldCities.v1.json` (6,000 most populous cities, GeoNames CC BY 4.0, 272 KB), tests, the `answer.ts` hook (after the other calculators), and the GeoNames credit in `docs/MODELS.md`. Units 1201/1201, tsc clean |

## Behaviour (coordinator guards)
- **Triggers (EN only, anchored, general):**
  - "how far / how many km|miles (is it) (to walk|hike|cycle|bike|drive) from X to Y (by car|bike|foot) (and back)";
  - "how long / how many days|hours (would it take) to <mode> from X to Y (and back)";
  - "how far (away) is X from Y";
  - "(what's the) distance between|from X and|to Y".
- **Cities:** the most populous city of that name (an optional ", Country").
  - If either place isn't in the table, or both are the same, it returns **null and the normal path answers**.
  - It never runs on PT/ES, on a learned-detector emergency, in deep mode or with reused sources.
- **Text:**
  - always "an estimate" plus "computed from the cities' coordinates, not a mapped route";
  - walking: route +30%, 25 km/day, 5 km/h;
  - cycling: +25%, 80 km/day, 18 km/h;
  - driving: +25%, 80 km/h. It only states the factor and never claims a road distance;
  - no mode: the straight line plus "roads and trails are usually ~a quarter longer";
  - time questions lead with the time.
- **Paraphrases** were written by Anvil, not taken from any blind set (V-para untouched).

## L0 / L1
- **Fire scan, 1,034 EN dev messages:** v0.1 public 1/60, V-exact 1/11, Anvil pool 1/599, Compass emergency-dev 0/300, chat-slice v0 0/64. The only fires are the Paris–Rome item itself; **0 false fires**, including on 300 emergency messages.
- **Judged (judge.v1, both orders):**
  - **V-exact vit-trv-004: 0.89** (pass) vs engine 0.29, Haiku 0.62;
  - **v0.1 vit-trv-004: 0.86** (pass);
  - the hand-written L0 text scored 0.93.

## Caveats
- **It doesn't generalise to every travel question.** Only city-to-city trips with both cities in the top 6,000 trigger it. Towns, landmarks and trails fall back to the model.
- **Route factors are averages.** Mountain crossings are longer, and the text says so ("the real route can differ").
- **Impact on the headline is one item** in v0.1 (~+0.01 ratio) and in V-exact (~+0.05 on 11 items). V-para paraphrases are blind; their count is unknown to Anvil.
