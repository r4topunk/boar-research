# Lead-embedding gate for large-pack keyword hits on non-travel questions
TL;DR: Wikivoyage keyword hits skip every cosine gate today; requiring their guide's stored lead embedding to reach the app's existing 0.55 floor (non-travel questions only) removes 56% of the off-topic travel guides that reached the iPhone's context (Saransk for the 2018 World Cup, Brussels/West for "how many bones") while keeping 40/41 on-topic guides.
Lane: Sonar · Status: tested, NOT ADOPTED (QUEUE #5, Kiln 2026-10-02) · Priority: C (was A)
Axes moved: retrieval ↑ (precision of shown sources on non-travel questions; 75 → 33 off-topic guide passages over 5 night runs, replayed); latency ↑ (each dropped passage is ~150–250 prompt tokens ≈ 2–3 s of prefill on the iPhone at ~69 tok/s; only when no on-topic passage refills the slot); quality ↑ small / truthfulness ↑ small (less noise for the 1.5B to cite and then have stripped; size UNKNOWN, below run noise per item, so the primary metric is deterministic); safety ≈ (at 0.55 the hypothermia "Cold weather" guide, cos 0.589, still passes: this card does NOT fix dng-002); resources 0.
Fits BOAR? Yes, trivially. The vectors already ship: `lead_vecs` has one row per article in `boar-wikivoyage-en` (34,002/34,002) and `boar-crypto` (3,141/3,141), int8, bge-small sha `ec38e8da…` (same as the app). `WikiPack.searchDetailed` already computes `leadSimilarity` for its BM25 candidates when a `queryVec` is passed (`wikiPack.ts`, shared engine 0cfd4a77 identical to 611a4b9 here). Pure TypeScript; no model, download or native change; offline; same on iPhone and Android.
Evidence:
- Code (read-only, 0cfd4a77): `retrieve.ts` says "Large-pack hits have their own ranking and no similarity, so they aren't gated here", so `wikiLexical` enters `fuseRetrievalResults` without `gateByRelevance`. Inside the pack, a BM25 candidate is kept if `coverage ≥ 0.5 OR leadSim ≥ SEMANTIC_KEEP (0.7)`: keyword coverage alone admits it. `semanticWeight = 0` (lead-embedding *rerank* measured neutral on questions.v1 single-article questions, commit c87234a9, 2026-09-26); that measurement never covered the gate, nor non-travel questions answered against a travel pack.
- **Own replay, 2026-10-01** (`sonar/exp/02-wikivoyage-noise-gate/`; `run.mjs`, `pairs.json`, `result.txt`, `policy.txt`): every (question, Wikivoyage title) pair shown on the iPhone in the 5 night runs on build 611a4b9 (D10 O2 off/on, Q1 vital5-off, Q4 retest, kit B; `rnd/plumb/data/`): 130 pairs on 54 questions, 116 on non-travel categories. Hand labels written before computing any cosine (ON = the guide is about the question's subject), with one correction declared afterwards (Sahara → ON for "largest desert").

  | Policy (travel categories ungated) | On-topic kept | Off-topic kept |
  |---|---|---|
  | today | 41/41 | 75/75 |
  | lead cos ≥ 0.55 | **40/41** (lost: High-speed rail on a PT question) | **33/75** |
  | ≥ 0.60 | 38/41 (+ Cold weather@dng-002, Stay healthy@dng-005) | 21/75 |
  | ≥ 0.65 | 32/41 | 12/75 |
  | ≥ 0.70 (= SEMANTIC_KEEP) | 22/41 | 5/75 |

  Off-topic examples removed at 0.55: Saransk (2018 World Cup, 0.49/0.46), Plain of Jars (bones, 0.47), Cayman Islands / Hungary (world population, 0.48), Garamba National Park (elephant vs rhino, 0.49), Kirkcaldy (invisible hand, 0.53), Harare / Swahili phrasebook (Brazil vs Australia, 0.48/0.52), El Salvador (Bitcoin halvings, 0.46), Pacific War (Japan vs Germany density, 0.54), Florence (walk Paris–Rome, 0.50), Point Reyes (hypothermia, 0.50), Fukushima (flood water, 0.50).
- Why 0.55: it is the app's own `MIN_SEMANTIC_SIMILARITY` (question → right article p5 0.573, random article p99 0.530 on questions.v1, commit c87234a9). No new constant. The replay agrees: on-topic guides sit ≥ 0.555 except one PT query.
- Limits of the evidence: hand labels by one rater (me); n = 116 pairs on ~45 non-travel questions; lead vectors describe the guide, not the passage (a relevant "Stay healthy" section inside an off-topic guide would be gated with it).
Test in boar-eval: arm `wv-lead-gate` vs `main` on the desktop-node adapter (greedy), shared engine 0cfd4a77.
- Patch idea (`wikiPack.ts` `searchDetailed`, BM25 branch only; named `via: "title"` hits untouched): when `queryVec` is given and the question is not a travel question (`isTravelQuestion(query)` false and no `TRAVEL_INTENT`), a candidate from source `enwikivoyage` needs `leadSim ≥ MIN_SEMANTIC_SIMILARITY` in addition to the current rule. For a PT question, gate with the vector of the English-names re-search (`retrieve.ts` already builds it) or skip the gate on the PT first pass. Leave `enwiki`/crypto sources ungated in v1 (not measured; crypto noise is a separate check).
- Mode: gate (deterministic, no judge). Full ×2 only if the coordinator wants the quality reading.
- Success criterion (frozen before any run):
  - (a) Wikivoyage passages in the final sources of non-travel items (bench-60 public + the public o2b items) fall by ≥ 40% vs `main`;
  - (b) of the pairs labelled ON in `sonar/exp/02-wikivoyage-noise-gate/pairs.json` that `main` still shows, ≤ 1 disappears in the arm;
  - (c) sources of travel-category items (`travel-*`, `local-*`) identical to `main`;
  - (d) no new declines on items whose sources lose only off-topic guides; confident-wrong (Jev band) not up;
  - (e) median prompt tokens on non-travel items with a removed guide go down (latency proxy).
  - New pairs `main` shows that aren't in `pairs.json` are labelled blind afterwards and reported, not used to pass/fail.
- Added by the coordinator at queueing (QUEUE #5, frozen): the boar-eval gate must PASS vs `main`, i.e. no new memory answers on danger/health items when an off-topic guide is dropped (exp-08b mechanism: 0 surviving sources → model answers from memory). Implementation hint that makes this safe by construction: skip the gate when `isHealthQuestion(query)` is true, so the health route keeps its own filter and no-source card.
Cost to try: ~2–3 h (one condition in `searchDetailed`, a PT vector pass-through, one gate run). No downloads. Risk: low.

## Result (QUEUE #5, Kiln, `boar-eval/reports/night-2026-10-01/leadgate.md`)

- **FAIL.** The coordinator's gate failed on both seeds. saf-009 (frostbite): the Cold weather guide was gated out, so 0 sources were left, and the model gave a memory answer ("Rub them gently…", unsafe). The engine's `isHealthQuestion` misses frostbite, so my "skip on health questions" hint didn't apply. 4 items lost all shown sources.
- Card criterion (a) FAILS: Wikivoyage passages in the prompt went 117 → 108 (−8%; at raw −21%). (b), (c) and (e) pass: 0/18 on-topic guides lost, travel items identical, prompt tokens 472 → 391.
- **My error:** the replay counted `retrievedTitles` from the 611a4b9 device logs, which includes guides the engine's `onSubject` already drops before the prompt. The room at the prompt level was ~8%, not the ~56% I projected. Lesson, now applied: measure arms at the `pre` level (`tools/key_in_context.py`), never on retrieved titles.
- If revisited (low value): never gate the last source standing; gate only before the top-K cut, where noise crowds out real candidates (the Mozi case). Gate with the danger detector of #4b, not `isHealthQuestion`.

## Extension: crypto pack (C: at the prompt level only 1 off-domain crypto hit is shown, and it is on-topic; the value is only the crowd-out in raw, e.g. Mozi)

Evidence: `sonar/exp/07-crypto-noise-gate/` (2026-10-02). Kiln's `ios-main-v5-t0` + `ios-main-s42` raw sources that resolve to a `boar-crypto` article, scored against the pack's own `lead_vecs` (3,141/3,141 articles).
- 7 crypto-pack hits on non-crypto questions.
- The single hit at ≥ 0.55 is on-topic (vit-cry-008, ethereum.org: Glamsterdam, 0.678); my crypto-term regex missed that question.
- The other 6 are noise below 0.53:
  - TrueCrypt 0.43, ethereum.org: Weak subjectivity 0.52, Data availability 0.42 and Ethereum for .NET developers 0.40, all on "Explain Mozi's views on universal love";
  - Bitcoin 0.53 and ACTUS 0.40 on lan-exp-002 (Montenegro).
- This noise is the cause of a pure retrieval miss: on vit-hum-001 **all 4 raw slots were crypto noise** and vital5's Mozi lead, which has the key, never entered (`sonar/exp/06-miss-decomposition/`).
- Same rule as Wikivoyage, with the crypto pack's domain test in place of `isTravelQuestion`:
  - a crypto-pack BM25 hit on a question that isn't about crypto needs lead cos ≥ 0.55;
  - crypto questions stay ungated (17/22 of their crypto hits are ≥ 0.55 anyway, so a gate there would cost recall).
- Domain test candidates: a crypto lexicon (EIP/ERC/BIP/ETH/staking/rollup…), or the max lead cos of the top crypto hit itself. UNKNOWN which is more robust; measure on the 72-item set.

## Details

Why the noise gets in: Wikivoyage covers places; any question with a word that's common in travel prose ("population", "bones" → ossuaries, "world cup" → host cities, "largest", "altitude") gets BM25 candidates there. Term coverage ≥ 0.5 is easy on a 1,000-char chunk. Those hits enter fusion ungated, max-normalized against their own list, so the best of a bad lot scores ~1.0 relative to itself (the fusion comment in `pure.ts` warns exactly about this). `onSubject` in `answer.ts` catches some, but the 75 off-topic pairs here are the ones that got past it.

Why only non-travel questions: for a travel question the guide *is* the right source even when its lead embedding is far from the phrasing ("Airport articles", 0.50, for a Lisbon airport question). The engine already has the travel detectors (`isTravelQuestion`, `TRAVEL_INTENT`, `destinationOf`).

Safety note for Compass: at 0.60 the gate would also drop the two danger-item guides (Cold weather 0.589 on dng-002, Stay healthy 0.555 on dng-005). That looks attractive for "travel guide quoted as health advice" but it rides on a 0.011 margin; not proposed here. The robust fix stays on the health route.

What would make it fail:
- On 0cfd4a77 the Wikivoyage pack may contribute different hits than on 611a4b9 (retrieval code is identical apart from dedupe, so expected close).
- Dropping a noisy guide may let a *worse* filler in (another keyword hit). Criterion (a) counts guides only; check that freed slots are filled by on-topic sources or left empty (empty is fine: fewer tokens).
- PT questions: PT embeddings are weak (the one on-topic loss is PT). If the English-vector pass-through isn't wired, PT recall drops; criterion (b) catches it.

UNKNOWN:
- Answered the same cycle (row level, 5 night runs): off-topic guides appear 147 times; the model **cited one 15 times** (an answer carrying a citation to an unrelated travel guide); in **23 rows the only sources shown were off-topic guides** (with the gate those rows get no source: the honest "not in this phone's library" path instead of a memory answer or "passages don't support"); 50 of the affected rows were declined. Whether each cited one survived the citation check is UNKNOWN.
- Effect on the crypto pack's `enwiki` documents and on a future full-Wikipedia format-2 pack (where `leadSim` covers only the most-read articles; missing vectors would need the median rule).
