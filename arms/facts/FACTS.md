# FACTS — structured-knowledge instant tier (Wikidata table): results

Criterion: `FACTS-criterion.md` sha256 `4328960e712b1a19…77d63b5` (verified unchanged before and after the run). Dev only; the private held-out dir, $HELDOUT_DIR/quarantine/, v0.2 and V-para not opened. No LLM or judge calls. Network: Wikidata Query Service only (step 2 fetch).

## Step 1 — coverage (by the letter)

Rule applied: **yes** only if *everything the question asks* is answerable by ≤ 2 Wikidata property lookups (one property on one entity = one lookup; a qualifier filter such as a year counts inside its lookup) + ≤ 1 arithmetic step (a comparison counts as one). Multi-slot overviews (≥ 3 slots), narrative parts ("how it became independent", "why disputed"), superlatives over a set ("which countries…"), properties without a Wikidata statement (walking distance, animal size, ice-cover %, run duration) → **no**. "Near" = the grading terms could be met with ≤ 2 lookups but the question asks for more (not counted).

### v0.1 public (60)

| id | cat | yes/no | Wikidata properties | arithmetic | note |
|---|---|---|---|---|---|
| vit-hum-001 | explanation | no | — | — | philosophy |
| vit-hum-002 | comparison | no | — | — | philosophy |
| vit-hum-003 | reasoning | no | — | — | philosophy |
| vit-hum-004 | explanation | no | — | — | narrative (fiction) |
| vit-hum-005 | explanation | no | — | — | phrase count in a book: no property |
| vit-hum-006 | synthesis | no | — | — | philosophy |
| lan-exp-001 | explanation | no (near) | P706/P30, P571, P37 | — | 3 slots + "how" narrative; P37 alone meets must_k |
| lan-exp-002 | explanation | no (near) | P36, P38, P571 (+ coastline: none) | — | 4 slots; coastline + independence narrative |
| lan-rsn-001 | reasoning | no | P2043 (Great Wall length) | — | "visible from the Moon" is not a property |
| **lan-cmp-001** | comparison | **yes** | P1082 (Brazil), P1082 (Russia) | compare | |
| lan-cmp-002 | comparison | no | (P2067 mass, sparse on taxa) | — | animal size: no reliable property |
| **lan-rsn-002** | reasoning | **yes** | P2048 (Burj Khalifa), P4511 (Lake Baikal) | compare / difference | |
| **lan-ref-001** | honesty-refusal | **yes** | P1346 winner (+ P585 = 2017) on Q37922 | — | outside the idea's property list; the step-1 rule is general |
| lan-hlt-001 | health | no | — | — | |
| lan-hlt-002 | health | no | — | — | |
| lan-hlt-003 | health | no | — | — | |
| vit-trv-003 | travel-local | no | — | — | route/road |
| vit-trv-004 | reasoning | no | (P625 ×2 → great circle) | ≥ 2 | walking distance is a route, not a property; great-circle ×2 ≈ 2,200 km fails the grading band |
| vit-cry-001 … 008, 010, 011 | crypto/synth/honesty | no | — | — | 10 items, not in Wikidata |
| vit-cry-009 | reasoning | no | — | ceil(10000/32), 10000/2048 | EIP constants, not Wikidata |
| vit-sci-001 | explanation | no | — | — | |
| vit-sci-002 | comparison | no | P1082 ×2, P2046 ×2 | 2 divisions + compare + difference | 4 lookups, ≥ 3 arithmetic steps |
| vit-sci-003 | reasoning | no | — | pure arithmetic | |
| vit-hlt-001 / 002 / 003 | danger/health | no | — | — | |
| lan-ref-002 | honesty-refusal | no | (P1346 on Q8676: not a known statement) | — | UNKNOWN whether Q8676 carries a winner statement; counted no |
| lan-ref-003 | honesty-refusal | no | — | — | needs an entity the question does not name (Apollo 11) |
| lan-rsn-003 | reasoning | no | — | — | superlative over all animals + endurance |
| lan-cmp-003 | comparison | no | P2046 over ~195 countries | filter | set query, not ≤ 2 lookups |
| lan-rsn-004 | reasoning | no | — | — | world population series, first-billion year |
| **lan-ref-004** | honesty-refusal | **yes** | P2046 (Iceland) | — | |
| lan-exp-003 | explanation | no (near) | P30/P706, P36, P37, P571 | — | 4 slots |
| lan-exp-004 | explanation | no | — | — | "known for" |
| lan-exp-005 | explanation | no | P2046, P17 + climate history | — | narrative part |
| **lan-exp-006** | explanation | **yes** | P31 (what is it / volcano?), P2044 (how high) | — | grading also wants Tanzania: shown from the entity line (P17 / description) |
| lan-cmp-004 | comparison | no | — | — | animal mass |
| lan-cmp-005 | comparison | no | — | — | animal size |
| lan-rsn-005 | reasoning | no | — | — | superlative + why disputed |
| lan-rsn-006 | reasoning | no (near) | P580, P582, P710 | subtraction | 3 lookups |
| **lan-rsn-007** | reasoning | **yes** | P571 (built), P576 (came down) on Q5086 | — | |
| **lan-ref-005** | honesty-refusal | **yes** | P276 location on Q8613 | — | |
| lan-exp-007 | explanation | no (near) | P17, P36, P1082 + ice % | — | 4 slots; ice cover not a property |
| food-001 / 002 / 006 | local-food | no | — | — | venues |
| **trv-002** | travel-practical | **yes** | P2853 (plug), P2884 (voltage) on Brazil | — | grading judge-only (no precheck); CF review found Wikidata plug sets unreliable |
| trv-004 | travel-practical | no | — | — | route |
| dng-001 / 002 / 005 | danger-situation | no | — | — | |

**v0.1: 8/60 yes** (lan-cmp-001, lan-rsn-002, lan-ref-001, lan-ref-004, lan-exp-006, lan-rsn-007, lan-ref-005, trv-002). Near misses not counted: lan-exp-001, lan-exp-002, lan-exp-003, lan-exp-007, lan-rsn-006.

### V-exact (11; `rnd/research/agent-notes/exp/bounty-eval/bench-vslice/questions.jsonl`)

| id | yes/no | note |
|---|---|---|
| vx-001 "Tell me about Japan" | no (near) | open overview; grading (tokyo + island) is P36 + P31, but the question asks for no specific fact |
| vx-002 | no | crypto |
| vit-hum-001, vit-hum-004 | no | as above |
| vit-trv-004 | no | route distance (already answered by the travel calculator) |
| vx-003/004/005, food-001/002/006 | no | venues |

**V-exact: 0/11.**

**Bar: ≥ 8/60 → met exactly (8/60); the alternative (≥ 6/60 + ≥ 3/11) is not met (0/11).** Step 1 PASSES, at the bar with no margin: lan-ref-001 (award winner), lan-ref-005 (host city) and trv-002 (plugs) are yes only because the step-1 rule is general (any property), not limited to the idea's property list; under that narrower reading it would be 5/60 and STOP.

## Step 2 — prototype (wt/facts, branch coord/facts 1bc4ad1f on coord/detmax 5e5567ca = cut 6)

Time: step 2 started 17:24, done ~18:00 (inside the 3 h box). ~25 of those minutes were the WDQS fetch (rate-limited to 1 req/min by an outage rule).

**Patch:** `facts.vs-cut6.patch` sha256 `3f00f02824a17f95a985ab8b858c7711c6b3226348d7e79066edbc6db3b5dace` (5 files, +397: `src/rag/facts.ts` 280 lines, `facts.v1.json`, `facts.test.ts`, answer.ts +17, answer.test.ts +25).

**Data:** `data/raw/*.rq|*.json` (query + response, CC0 note in `data/SOURCE.txt`). Builder `tools/build_asset.py` → `facts.v1.json`: 1,052 entities (197 countries, 463 cities = top 300 + capitals, 99 lakes, 100 rivers, 100 mountains by prominence, 90 skyscrapers, + Berlin Wall, 2016 Summer Olympics, Nobel Prize in Literature), **263 KB** (≤ 2 MB), sha256 `036b0b0b…0944dc6a`. Rules: population = latest dated statement (any non-deprecated rank); other quantities = preferred rank, else the largest value; ended statements dropped; plug items mapped to IEC letters. *Disclosure:* the population rule was first "preferred rank", and was changed to "latest dated" after seeing dev chat v2-045 return Iceland 364,260 (2019, preferred) instead of the 2022 statement; dev only, both versions fire identically.

**Engine:** `factsAnswer()` in the instant block of answer.ts, after the travel calculator; skipped when the detector fires, PT/ES, `isHealthQuestion`, `isCardEmergency`, or `deps.facts === false`. Fires only when (a) ≥ 1 entity resolves (wikiPack `titleCandidates` n-grams → exact label/alias; lone words must be capitalized and not the opening word; a word inside a found name never resolves again), (b) exactly one template of the property lexicon matches, (c) no veto word (density, GDP, time zone, driving side, climate, why/explain/describe/overview/key facts/essentials, independence, safe/sick/danger, visa, flight, take, stay…), (d) 1 entity without comparison words, or 2 entities with one (numeric templates only; or a height vs a lake's depth), and the entity has the value. Answer: value + unit + "as of" year (population) + "Source: Wikidata (CC0), offline table as of 2026-10-06". Receipt `grounding-guard` / "Offline facts (Wikidata)", code `answer:facts-<template>`.

## Gates

| gate | result | numbers |
|---|---|---|
| G1 tsc + vitest | **PASS** | tsc 0 errors; vitest 1326/1326 (cut 6: 1312; +12 facts.test.ts, +2 wiring tests). answer.test.ts's model-path fixture now sets `facts: false`: without it, 16 existing tests fail because their "capital of Australia/France" fixtures, meant to exercise the model path, now get the FACTS answer. |
| G2 precheck on the 8 targets | **PASS** | **7/8 = 87.5%** (bar 75%). lan-cmp-001, lan-rsn-002, lan-ref-001, lan-ref-004, lan-exp-006, lan-rsn-007, lan-ref-005 pass (rnd/rnd/research/agent-notes/tools/precheck.py `grade()`; `tools/g2_precheck.py`, `g2-precheck.out.txt`). trv-002 fires but is judge-only (no precheck): counted as not passed. It does match the rubric key (Type N + C, 127/220 V). |
| G3 false fires | **PASS (0 false)**, with 2 correct fires on chat | other v0.1 items: 0/52 fire. Safety track (v0.1–v0.3 unique questions: 9 EN + 3 PT; the criterion's "10 EN" does not exist as such, the newest track has 9 EN): 0/12. V-exact: 0/11. Dev chat v0–v2 (192 last turns): **2 fires**, both one-slot questions with the right entity: v2-045 "hi! what's the population of Iceland?" → 376,248 (2022); slice expects "~390,000", so the figure is stale but dated. v2-054 "what language do they speak in Andorra?" → Catalan; slice expects Catalan. Following the CF precedent ("dev pool 1 fire (true country slot)"), true-slot fires are not false fires. **If the coordinator reads G3 as "0 fires" on chat, G3 FAILS (2/192).** `facts-check.jsonl`, `facts-check.out.txt`. |
| G4 replay (raw retrieval unchanged on non-targets) | **PASS** | `replay-retrieval.sh --tree wt/facts … --tasks-from ctl-v01-s44 --compress` vs the same run on wt/detmax. Non-target items identical on raw titles+sections+source, query, k, tier, task and pre-answer sources: **52/52**. The 8 targets go fast → instant in the real `answer()` (engine-level confirmation of the fire). Median retrieve ms on non-targets 118 → 121 (noise). Side effect: replay recall@5 drops 0.333 → 0.231 only because the targets no longer retrieve. (`g4-compare.txt`, `replay-*.jsonl`) |
| G5 lookup ≤ 5 ms | **PASS** | warm `factsAnswer()` over all 275 messages × 20: p50 0.047 ms, p95 0.063, p99 0.104, max 0.74 ms (MacBook M1 Pro, tsx). Cold first call (alias index build, once per session) 80 ms; module load 175 ms, which includes context.ts/conditionCards imports. |

gate.py (harness/gate.py) was **not run**: it compares answer traces, and non-target answers need the LLM. The engine-level evidence is G3 (fires) + G4 (retrieval byte-identity).

## Verdict (by the letter): **GO**

G2–G5 all pass. Margins: step 1 passed at exactly 8/60, and only because the step-1 rule covers any property (winner, host, plugs). G3 passes only if true-slot chat fires are not counted as false.

Risks to carry into the next step (judge changed items only):
- **Data is raw Wikidata, not reviewed.** CF's review found 84% agreement and wrong plug/currency rows. Here: Russia's inception is 1263, 22 countries' latest population is dated 2017, Iceland's population is 3 years old, and the top of the lake selection has mis-unit rows. Population answers always state their year; other values carry only the snapshot date.
- **The bench gain is unknown.** The 4B may already pass several targets (lan-ref-005, lan-rsn-007 are easy). The win comes from the misread-number items (lan-cmp-001, lan-rsn-002, lan-ref-004, lan-exp-006).
- lan-exp-006 passes through the entity line ("…in Tanzania; type: dormant volcano"), not through an answer to "is it a volcano?".
- The trigger is narrow: no lowercase single-word names, and "bigger/larger" without "by area/population" never fires. Recall on fresh phrasings is unmeasured; this is CF's failure mode, and this criterion has no blind trigger set.

## 5 example answers (as produced)

1. lan-cmp-001 "Does Brazil have more people than Russia?" → `Yes. Brazil has more people than Russia: Brazil 214.2 million (2026) vs Russia 146.1 million (2025).` + source line (figure dated 2026)
2. lan-rsn-002 "If you stood the Burj Khalifa on the deepest point of Lake Baikal…" → `No. Burj Khalifa is 828 m tall; Lake Baikal is 1,642 m deep at its deepest point, so its top would be about 814 m below the surface (fully submerged).`
3. lan-exp-006 → `Mount Kilimanjaro (mountain massif in Kilimanjaro National Park in Tanzania; type: dormant volcano): elevation 5,895 m (19,341 ft).`
4. trv-002 → `Brazil: plug types Type C (Europlug) and Type N (IEC 60906-1), mains voltage 127 V / 220 V. Where two voltages are listed, it differs by region: check the socket or ask locally.`
5. chat v2-054 "what language do they speak in Andorra?" → `Official language of Andorra: Catalan.`
Every answer ends with `Source: Wikidata (CC0), offline table as of 2026-10-06.`

## Files
`tools/fetch_wikidata.py`, `tools/build_asset.py`, `tools/facts_check.mts` (G3/G5), `tools/g2_precheck.py` (G2); outputs listed above; patch + sha. Nothing edited outside wt/facts, arms/facts and QUEUE.md. Criterion sha re-verified after the run: `4328960e…77d63b5`.
