# TOPICS27-SUCCINCT: the same 27 Research Topics, Qwen3-1.7B, Succinct instead of Detailed (bench engine)
Criterion: SUCCINCT-criterion.md sha256 `88220fabda6a7ebeed9c136188ec907c81863a739017c0f078edc8aba3bd4212` (frozen before any run, never edited). Parent arm TOPICS27 (criterion c97bd9d7...). Splitter tools/split.py b8a389a4... unchanged.

## Result: KEEP 19, FIX-PACK 2, SWAP 6 (Detailed: KEEP 7, FIX-PACK 0, SWAP 20)
- Same system, persona only: kept titles identical to the Detailed run on 27/27 topics, dumped contexts identical in length on 27/27; IN KEPT 23/27 (same misses b13 b15 b19 b20).
- Answers: mean 44 words (Detailed 330), 60 sentences (385). Haiku: UNSUPPORTED 17 (**0.283**; Detailed 0.468), PARTIAL 21, SUPPORTED 22 (0.37 vs 0.14); invented specifics **7** (98); 0-LLM numbers absent from the context 10 (39; 5 of them b12's Brazil/Russia figures).
- Banner ("Not found in this phone's offline library ... may be wrong") on **13**/27 (Detailed 11): q2 q4 q8 b2 b3 b4 b5 b8 b11 b12 b13 b17 b18; 12 of them with on-topic chunks kept (all but b13). Shorter answers do not stop it (see ENG-BANNER-KEPT: the banner is the engine's CMP30OFF release line, not a length effect).
- Flips SWAP -> KEEP: q2 q8 b2 b4 b7 b8 b9 b10 b11 b14 b17 b21 (12); KEEP -> SWAP: none. All 9 "near the bar" topics of the TOPICS27 reading (q2 q8 b4 b8 b10 b11 b14 b17 b21) are KEEP under Succinct (q8 b8 b10 b11 b21 with a watch note).
- Still SWAP: b3 (photosynthesis, 1 invented), b12 (Brazil figures from memory), b16 (Kilimanjaro), b18 (cheetah), b19 (emergency table, plugs/voltage never answered), b20 (one sentence, no context). FIX-PACK: b13 (kept empty, 2/2 unsupported but no invented specific), b15 (Kyoto dropped).
- Haiku 162 invocations (cap 300): primary 53 (46 per-sentence q1..b14#2 + 7 batched calls b15..b21, mirroring the Detailed keys), sensitivity 109 (14 Succinct + 95 Detailed batched units re-audited per sentence); 0 missing, 0 retries. Opus 0, paid 0, phone 0.

## Predictions (frozen) vs result
| # | prediction | result | |
|---|---|---|---|
| P1 | unsupported share <= 0.318 (Detailed - 0.15) | 0.283 | HIT |
| P2 | invented specifics <= 49 | 7 | HIT |
| P3 | banner <= 5 | 13 | MISS (banner rises: 11 -> 13) |
| P4 | KEEP >= 12/27 | 19 | HIT |

Sensitivity (not deciding): with every sentence of both arms audited per sentence (no batching), Detailed 0.447 unsupported / 103 invented / KEEP 9 (b14 b17 flip to KEEP); Succinct 0.283 / 6 / KEEP 19 (b20 SWAP -> FIX-PACK). The gap holds (-0.16 vs -0.19 under the mirrored batching).

## Per topic (D = Detailed, TOPICS27; S = Succinct; (b) = batched audit; verdict = frozen TOPICS27 rule)
| key | D sent | D unsup (+part) | D inv | D banner | D verdict | S sent | S unsup (+part) | S inv | S banner | S verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| q1 | 17 | 3 (+7) | 3 | - | KEEP (watch) | 2 | 0 (+0) | 0 | - | KEEP |
| q2 | 16 | 7 (+3) | 4 | - | SWAP | 2 | 0 (+1) | 0 | yes | KEEP |
| q4 | 14 | 6 (+5) | 0 | - | KEEP (watch) | 3 | 2 (+0) | 0 | yes | KEEP (watch) |
| q7 | 14 | 2 (+7) | 2 | - | KEEP (watch) | 2 | 0 (+1) | 0 | - | KEEP |
| q8 | 15 | 7 (+7) | 3 | yes | SWAP | 2 | 1 (+1) | 0 | yes | KEEP (watch) |
| q9 | 16 | 4 (+9) | 7 | - | KEEP (watch) | 1 | 0 (+1) | 0 | - | KEEP |
| b1 | 18 | 4 (+12) | 1 | yes | KEEP (watch) | 3 | 0 (+1) | 0 | - | KEEP |
| b2 | 15 | 10 (+5) | 7 | - | SWAP | 2 | 0 (+1) | 0 | yes | KEEP |
| b3 | 18 | 10 (+7) | 12 | yes | SWAP | 2 | 1 (+1) | 1 | yes | SWAP |
| b4 | 15 | 6 (+9) | 4 | yes | SWAP | 2 | 0 (+2) | 0 | yes | KEEP |
| b5 | 17 | 2 (+11) | 2 | yes | KEEP (watch) | 2 | 0 (+0) | 0 | yes | KEEP |
| b6 | 17 | 5 (+7) | 0 | - | KEEP | 2 | 0 (+1) | 0 | - | KEEP |
| b7 | 13 | 6 (+5) | 7 | - | SWAP | 3 | 0 (+2) | 0 | - | KEEP |
| b8 | 15 | 8 (+5) | 1 | yes | SWAP | 3 | 1 (+1) | 0 | yes | KEEP (watch) |
| b9 | 15 | 9 (+6) | 4 | - | SWAP | 2 | 0 (+0) | 0 | - | KEEP |
| b10 | 14 | 6 (+7) | 2 | - | SWAP | 3 | 1 (+1) | 0 | - | KEEP (watch) |
| b11 | 14 | 7 (+7) | 2 | yes | SWAP | 3 | 1 (+1) | 0 | yes | KEEP (watch) |
| b12 | 14 | 10 (+3) | 9 | - | SWAP | 3 | 2 (+1) | 2 | yes | SWAP |
| b13 | 10 | 10 (+0) | 6 | yes | SWAP | 2 | 2 (+0) | 0 | yes | FIX-PACK |
| b14 | 13 | 5 (+6) | 1 | - | SWAP | 2 | 0 (+2) | 0 | - | KEEP |
| b15 | 14 | 6 (+5) | 5 | yes | SWAP | 3 | 1 (+1) | 0 | - | FIX-PACK (b) |
| b16 | 13 | 9 (+4) | 5 | yes | SWAP | 2 | 1 (+0) | 1 | - | SWAP (b) |
| b17 | 15 | 7 (+6) | 1 | - | SWAP | 2 | 0 (+1) | 0 | yes | KEEP (b) |
| b18 | 13 | 8 (+4) | 4 | yes | SWAP | 2 | 1 (+1) | 1 | yes | SWAP (b) |
| b19 | 2 | 1 (+0) | 1 | - | SWAP | 2 | 1 (+0) | 1 | - | SWAP (b) |
| b20 | 15 | 15 (+0) | 4 | - | SWAP | 1 | 1 (+0) | 1 | - | SWAP (b) |
| b21 | 13 | 7 (+3) | 1 | - | SWAP | 2 | 1 (+0) | 0 | - | KEEP (watch) (b) |
| **total** | **385** | **180 (+150)** | **98** | **11** | **KEEP 7, FIX 0, SWAP 20** | **60** | **17 (+21)** | **7** | **13** | **KEEP 19, FIX 2, SWAP 6** |

## Commands
- Requests: in/t27-succinct-s42.requests.jsonl = the Detailed requests with personalityId succinct and runId t27-succinct-s42 (diff otherwise empty).
- Generation: `bash tools/run_gen_succinct.sh` (run_gen.sh with paths only; mini job t27-succinct-s42, slot gen1, base-tree sha guards passed, 27/27 rows, 0 errors, run 86 s, peak RSS 2.67 GB, disk 30 GiB) -> gen-succinct/ (gitignored).
- `python3 -I tools/prep_succinct.py` -> judge-succinct/prep.json (60 units).
- `node tools/audit_succinct.mjs judge-succinct/prep.json judge-succinct/audit.jsonl primary 0` (audit.mjs with the batching keys mirrored; same prompts and schema).
- Sensitivity: `node tools/audit_succinct.mjs judge-succinct/sens-{succinct,detailed}.prep.json judge-succinct/sens-{succinct,detailed}.jsonl single-all <start>`.
- `python3 -I tools/agg_succinct.py` -> aggregates/succinct-topics27.json, aggregates/succinct-summary.json. Detailed files (gen/, judge/, aggregates/topics27.json, summary.json) untouched.

## Maintainer note (3 lines)
For 1.5-1.7B models, show the Research Topics with the Succinct style: on the same 27 topics and the same retrieved passages it cuts unsupported sentences from 47 % to 28 % and invented specifics from 98 to 7, and 19/27 topics pass (7 with Detailed).
Swap or narrow b19 (plugs/voltage go to the emergency table), b20 (Japan/Germany: off-topic retrieval), b12 (Brazil figures from memory), b3, b16, b18; b13 and b15 need retrieval fixes (mosquito chunks dropped, Kyoto dropped).
The "Not found in this phone's offline library" banner still shows on 12 answers that did use on-topic passages, in both styles: worth checking in the native app.

## Caveats
Bench engine K1 tree, not the native Kotlin app; one seed; EN only; 1.7B only. Haiku support audit, not a correctness or completeness judge: Succinct answers are about 2 sentences, so they say less (coverage of multi-part topics such as b4, b12, b19, b20 is not measured) and the per-topic 1/3 rule is coarse (1-3 sentences per topic: one sentence moves a verdict). The batched audit labels more strictly than per-sentence (sensitivity above); it touches b14..b21 in both arms the same way.
