# FACTS r5 (2026-10-06): two-sided neighbour guard. All frozen gates green; nearmiss-lc FP 0/40. Set 3 not run (coordinator).
- Commit: wt/facts `802c28bb` (branch coord/facts, on r3 `45d5d058`; r4 WIP patch 0d8adc47… reused as rule D). 2 files, +155 −24.
- Patch `facts-r5.vs-cut6.patch` (base `5e5567ca` = cut 6/DETMAX, same base as r3: `git diff 5e5567ca 45d5d058` reproduces 37e65204…),
  sha256 `9c86bf3fd166832842a14b098ac48d174188c86d666860d5149ee112005aa763`. Criterion FACTS-r5-criterion.md sha `54ab7a1b…` (followed as written).
- Asset unchanged (f4d3ab2e…), templates/properties/data/scorer v2 unchanged. Deterministic only: no LLM, no judge, no network.

## Rules as implemented (src/rag/facts.ts)
A. `neighbourBlocked()` runs after all names resolve; any occurrence of any resolved name (any casing) with a bad neighbour → no answer.
   Per side: a glued feature word of the entity's kind (mount/mt/mountain/river/lake) extends the name (r3 exception); then R5_SKIP
   words and numbers are skipped (punctuation is not a token); the first remaining token must be: absent, a word of another resolved
   name, inside a multi-word FACT_LEXICON phrase ("capital city", "square kilometres"), or in one of these sets:
   - R5_SKIP (exact): the a an of in at on for to and or
   - R5_QUESTION: wh-words (+ whats/what's/hows/how's/wheres/where's), auxiliaries/modals and their n't forms, pronouns
     (i you we they he she it its their there this that these those me my your our us), function words (if tell give list name show
     know wonder by with from into as so but not no yes any some all both each also just really very much many more most less fewer
     then compare above below over under up down), question-frame verbs (use/uses/used/using, speak/speaks/spoken/speaking,
     live/lives/living, located, stand/stands/stood, put, placed)
   - R5_PROPERTY: the criterion list + depth/official/shorter/higher/lower/deeper/shallower, superlatives (biggest … lowest),
     point/top/peak/rnd/research/agent-notes/total, and every one-word FACT_LEXICON cue (populous, inhabitants, built, founded, hosted, won, plug, …)
   - R5_HEDGE: roughly about approximately approx around exactly today now currently called please again anyway days nowadays
   - R5_UNITS: m km feet ft foot miles mile mi sqkm sq square km2 km² meters metres meter metre kilometres kilometers kilometre kilometer
   - R5_COMPARE (exact): or than vs versus compared
   The r3 capitalised-only glue guard and FUNCTION_WORDS are removed (subsumed); the r3 MODIFIERS rule ("new mexico") is kept.
B. QUESTION_OPENERS: ^(whats|what's|hows|how's|wheres|where's) or ^(size|capital|population|elevation|height|length) of → a question.
C. r4 safe-lowercase multi-word rule drops the LOWER_RISK check (keeps HOMONYMS = georgia): "lake victoria", "new zealand" resolve.
D. r4 rules kept verbatim (safe lowercase multi-word names with one entity; thw/teh/hte/tje/th as "the" before a resolved name).
Tests: r5 block of 6 `it`s covering every criterion case; 3 r2/r3 assertions updated for rule D (lake baikal, amazon river, mexico city).
Added for the gate targets: "stood"/"point" (lan-rsn-002), "use" (trv-002), "speak" (v2-054), "have" (lan-cmp-001).

## Gates
| gate | r3 | r4 | r5 |
|---|---|---|---|
| G1 tsc + full vitest | 0; 1335/1335 | not run | **0; 1341/1341** (118 files) `g1-r5.out.txt` |
| 13 DATA-REVIEW probes | 0 fires | not run | **0 fires, P13 block identical to r3** `probes-r5.out.txt` |
| 39 wider probes (no bar) | — | — | 37/39 identical; 2 fires removed: "Swiss schools", "Paris, the city of light" |
| r4 fresh probes (22) | 5 wrong fires | 10 wrong + 1 right | **1/22: kuala lumpur tower only** `probes-r5-fresh.txt` |
| G2 precheck | 7/8 | not run | **7/8; output identical to r3** `g2-precheck-r5.out.txt` |
| G3 v0.1 other / safety / V-exact / dev chat | 0/52, 0/12, 0/11, 2/192 | not run | **0/52, 0/12, 0/11, 2/192 same items**; facts-check-r5.jsonl byte-identical to r3 (275/275) |
| G4 replay non-target raw vs cut 6 | 52/52 | not run | **52/52**; r5 vs r3 60/60; targets fast→instant; median ms 118/127/122 `g4-compare-r5.txt` |
| G5 warm latency (5,500 calls) | p95 0.077 ms | not run | **p50 0.051 / p95 0.085 / p99 0.137 / max 0.312 ms**; cold 86 ms |

## Dev sets (scorer v2)
| set | r3 recall / prec / FP | r4 | r5 |
|---|---|---|---|
| set 1 | 30/40 / 88.2 % / 0/20 | 33/40 / 89.2 % / 0/20 | **33/40 = 82.5 % / 89.2 % / 0/20** (same items as r4) |
| set 2 | 26/40 / 100 % / 0/20 | 28/40 / 93.3 % / 0/20 | **31/40 = 77.5 % / 93.9 % / 0/20** |
Set 2 r4→r5: +f17 elevation of lake titicaca, +f23 lake victoria, +f25 capital of new zealand, +f36 whats … philippines; −f15 "height fo the".

## nearmiss-lc (run once, after commit 802c28bb; `shasum -c nearmiss-lc.sha256` OK, sha 517de417…)
**FP 0/40** (`nearmiss-lc-r5.jsonl`, `.out.txt`). No code change after the run.

## Remaining dev misses (16) by cause
- Stale/wrong value in data (6): set 1 f15 India 2020, f22 Nigeria 2021, f31 Mexico +3.4 %, f37 China vs India (stale India); set 2 f29 Mekong 4,350 km, f33 "złoty" lacks "Polish".
- Entity or value not in table (7): f18 Eiffel Tower, f39 Mount Fuji, r2-f20 Rhine, r2-f30 CN Tower, r2-f04 Lake Geneva, r2-f32 Vietnam and r2-f09 Netherlands population.
- Lowercase one-word non-country name (1): f29 kilimanjaro. Lowercase alias not allowed (1): r2-f10 uae.
- Rule A cost (1): r2-f15 "fo" (typo of "of") is a non-allowed neighbour. Extra dev probe: "how tall is the burj khalifa in dubai" → no fire (unresolved lowercase "dubai").

UNKNOWN: recall on set 3 (blind; coordinator). The allowlists are hand-made; 5 words were added because gate targets needed them,
so recall cost of rule A on unseen phrasing (location qualifiers, typos, chatty tails like "right now") is unmeasured beyond 1 dev miss.
nearmiss-lc was written blind to the code but by a Claude-family agent; real lowercase homonym traffic is not measured.
