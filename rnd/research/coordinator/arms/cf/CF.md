# CF: country-facts lookup (Wikidata CC0) on cut 3 (engine engineer, 2026-10-04, DEV only)

TL;DR: CF is built as one commit (f57c81fb, branch `coord/cf` in `wt/cf`, from `coord/final` = cut 3) with 36 unit tests and a deterministic L0. No generation, no judge, nothing on the Mac mini. Trigger-set scoring (bar 2) and the data review (bar 1) are left to the coordinator and a reviewer. Criterion: `CF-criterion.md` (frozen, untouched).

## Deliverables
- **Patch:** `cf-on-cut3.vs-0cfd4a77.patch` (cut 3 + CF), sha256 `13766d72f5ef79f9c45cad725ed1d388906b2d41632f63cfb2738fdf007577ec`. Applies cleanly to a fresh `git archive 0cfd4a77`; tsc clean there; vitest **1326/1326** (cut 3 is 1290, +36 CF).
- **Files:** `src/routing/countryFacts.ts` (gazetteer, slot/overview/compare/list triggers, renderer, `constrainToFacts`), `countryFacts.v1.json` (data), `countryFacts.test.ts` (36 tests), `answer.ts` (one fast-path block + `country-facts` in `NOT_A_MODEL`), `answer.test.ts`.
- **Data:** `countryFacts.v1.json`, 197 states (UN members + Vatican, Palestine, Taiwan, Kosovo), 118 KB, source "Wikidata (CC0 1.0)", retrieved 2026-10-04, the SPARQL texts are stored in the file. **sha256 `5503bdd133bd0c38a09cfb8aa21d3dc29335a650aae82a701d5c3b32d091b774`**. Empty where Wikidata has nothing (e.g. Japan's driving side). Build: `build/build-cf-data.mjs` (generic UA `boar-cf-build/0.1`), raw results in `build/sparql-raw`.
- **countryFacts.ts sha256** `bbcbc8827643f149285e77a5743bba9a3c2f8278d6781fae8c60ee46ce493b61`.
- **Scorer:** `tools/cf-trigger-score.mts <tree>` pins both files above by sha256, scores `trigger-set/items.jsonl` (`id,text,expect`), prints recall, false fires, missed and false-fire ids. Smoke-tested on a fake 4-item file in the scratchpad only; `trigger-set/` was not opened.

## Behaviour
- Fires on: country + fact slot (capital, currency, population, area (+rank), density, languages, calling code, driving side, plugs/voltage, time zone, continent, neighbours, head of state), an overview ("Tell me about Japan"), a two-country numeric comparison (population/area/density, with a computed verdict line: ratio and difference), and "which countries are bigger than X" (list <= 15).
- Output: "Facts:" block first, one fact per line with units, then "Wikidata, 2026-10-04"; the 4B then writes <= 2 sentences, and a sentence with a number not in the block is dropped (`constrainToFacts`). Compact model: facts only.
- Abstains on homonyms without a country cue (Georgia, Jordan, Turkey the bird, Chad, China as porcelain, Niger, Jersey, Panama hat, guinea pig), subnational places, history/why questions, 3+ countries, other languages. Placed after the health/danger/card/calculator/venue paths; skipped on learned-detector emergencies, the deep tier and reused sources.

## L0 results per bar
| bar | result |
|---|---|
| 1 data | 197 rows (>= 190) **PASS** on count. `data-review-sample.jsonl`: 30 random rows (fixed LCG seed 20261004) x 5 fields (capital, currency, plugs, population+year, area), for the reviewer to check against live Wikipedia. **Pending reviewer** |
| 2 trigger | Blind set: **pending, coordinator**. Dev pools: **1 fire on 1,328 EN dev messages** (aligned 1010 + terse-live 213 + compass-dev 105), "capital of Australia", a true country-slot message. `dev-fires.jsonl`. Reviewer to label it |
| 3 replay | v0.1 EN 60 + V-exact 11 + venue6 6, cut 3 requests, stub LLM, no `--places`, cut 3 tree vs CF tree. **9 items changed**: 8 of the 9 targets (trv-002, lan-exp-001/002/003, lan-ref-004, lan-cmp-001/003, vit-sci-002; **lan-exp-007 does not fire**) + vx-001. 0 other v0.1 items change; 0 changes on health/danger/card/calculator/venue items, venue questions byte-identical. **PASS** (>= 6 of 9 and vx-001, <= 3 others). Real venue/GPS checks need the `--places` run in L1 |
| 4 units | 36 CF tests incl. density ratio (Japan vs Germany), population difference/ratio, area rank, bigger-than-India = 6 named. vitest 1326/1326. **PASS** |
| 5 latency | Lookup over 1,332 messages: p50 0.015 ms, p95 0.052 ms (0.3 ms on fires); the first call builds the index once (about 290 ms, cold). Retrieval p50 (stub replay): cut 3 99.6 ms vs CF 99.3 ms (ratio 1.00). **PASS** |

## UNKNOWN
- Trigger recall/false fires on the blind set; reviewer agreement on the data sample (Wikidata quirks possible: Japan has no driving side and 2 US plug types, Kenya population year 2017, Niger 5 plug types, neighbour lists as Wikidata states them).
- Independence date and government type are not in the data (the criterion fields don't include them): "how it became independent" asks (lan-exp-001/002/003) get the standard lines and the 4B may only write from them. lan-exp-007 does not fire (not diagnosed).
- Replay used a stub LLM, so the real 4B sentences and `constrainToFacts` drop rate are unmeasured; L1 decides.
- Ambiguous "capital of Georgia" abstains by design (costs recall on that phrasing).

## Revision 1 — stopped (2026-10-04)
The coordinator stopped the trigger revision after CF L0 bar 1 FAILED (`data-REVIEW.md`: 84 % agreement vs the 98 % bar; 3 currency and 7 plug errors). Bar 1 has no revision clause, so data quality killed the arm for this round. trigger-set2 was not opened or scored.

What had been changed before the stop (WIP commit on `coord/cf`, in `wt/cf`; NOT a candidate, tests not re-run, the patch `cf-on-cut3.vs-0cfd4a77.patch` and the scorer pin still describe the pre-revision commit f57c81fb):
- **Data bug found and fixed in `build/build-cf-data.mjs`:** Wikidata item Q13196750 (left-hand traffic) is a redirect to Q11920728, so 54 countries (Japan, India, Australia, UK-style) had no driving side. The build now maps both ids; rebuilt data has driving for all 197 rows. The plug and currency errors the reviewer found were not investigated.
- **Government type added** (P122, 160 of 197 rows); GDP per person was tried (P2132, USD, dated) and dropped: only 9 rows, so the slot declines (GDP stays in the off-topic gate).
- **Trigger work started:** aliases (KSA, NZ, U.A.E.), government-type slot allowed and rendered, and a `canon()` typo/short-form table (capitol, currncy, pop, tz, dial code, neighbors); `canon()` is defined but not yet wired into `countryFacts()`.
- **Not done:** new driving, "how many people", neighbours, time zone, continent-membership and overview patterns, reverse lookup by calling code, the generic proximity fallback, the scorer re-pin and the patch re-cut.
