# STACK (2026-10-22 22:4x-23:1x; 0 LLM / Haiku 0 of 200 / Opus 0 / paid 0 / phone 0; MacBook replays only; criterion STACK-criterion.md sha c0fabf99, not edited)
Tree kiln-local/rs-STACK = cp -Rc rs-H4 + SEFIX-F1, F2, F4 + R1-RERANK (patch shas fc6aa040 / 225a226a / d1b1b117 / db60aa3f; F3 not applied). Applied in order, F1 -> F2 -> F4 -> R1: all clean except ONE F2 hunk (the `rsSeStats` field of the unused F2 global-df variant, context moved by F1): applied by hand; F1 and F2 both add the identical `rsIsSE` getter, the second copy removed. No other deviation. File shas (12 hex): packs.ts 996bf108, wikiPack.ts ff1b5979, retrieve.ts 50ec8266, denseCandidates.ts 5d31e2e6, answer.ts 8e42610c, context.ts e4e7b39c. Not a byte-identical SEFIX-ALL base (that has F3).
Recipe (run_stack.sh): 13-pack N10 kit, cooking/money from v3proto (79ed2699 / 87e4a4cd), RS_MERGE=gidf, RS_SE_LEAD=0.78, RS_SE_MAXDF=0.25, RS_KEEP_NOPROPER=1, RS_RERANK=mix, packHeadPass a2 + packDense2 extra, funnel-K3 traces, MAIN 97.
Identity: all switches off, first 20 items: **20/20** (raw, wide, kept ids, reason codes) vs sefix/replays/main.v3-extra.jsonl (F1b).
## Chunk-level (tools/cl_stack.py -> chunklevel_stack.json; MAIN 92 = v0.1 52 + cm 40)
| arm | article /92 | chunk /92 | cm /40 | v0.1 /52 | junk own (no-fact items) | kept chunks / words |
|---|---|---|---|---|---|---|
| N10.gidf (ARM-G) | 32 | 28 | 2 | 26 | 3.22 | 343 / 30.6k |
| F1b | 45 | 32 | 7 | 25 | 2.92 | 321 / 25.9k |
| R1 mix | 49 | 42 | 16 | 26 | 2.84 | 340 / 27.1k |
| SEFIX-124 (v2) | 50 | **42** | 14 | 28 | 3.28 | 381 / 34.3k |
| SEFIX-ALL (v2) | 55 | 47 | 19 | 28 | 3.64 | 411 / 36.8k |
| **STACK** | 51 | **45** | 16 | **29** | 2.83 | 355 / 28.1k |
Note: the criterion text says SEFIX-124 and 47; measured SEFIX-124 chunk-level is 42 (cm 14, v0.1 28), so the bar is max(42, 47) + 5 = 52.
## Rule (frozen)
- chunk-level kept 45 vs bar 52: **FAIL** (+3 over SEFIX-124, -2 vs SEFIX-ALL, +3 vs R1 mix alone).
- losses among SEFIX-124's 42: **8 > 2: FAIL** (cooking-002/007/009/016/019, money-012, vit-cry-006, vit-trv-003); 11 gained (cooking-001/004/011/020, money-007/011/014/018, lan-cmp-005, vit-cry-002, vit-hum-003).
- junk 2.83 vs 3.28 = 0.86x (both-set 2.56 vs 2.95): pass. v0.1 29 vs 28-1: pass. Kept words 0.82x of SEFIX-124.
- **Verdict: NOT DELIVERS** (two clauses fail). Answer screen NOT run; nothing generated on the mini (its 2 slots are busy with SEFIX-124 s42/s43 anyway).
## Reading
- The stack is not additive: on cooking/money the v3 files have chunk_vecs, so F1 (lead scan) and F2 (OR-query widening) are inert there (both scoped to SE packs WITHOUT vecs); the stack = F1b + R1 mix there (cm 16 = R1 mix alone) and the lexical fixes only add on the 3 other SE packs and F4 (+3 v0.1 vs R1 mix: 26 -> 29, F4's lever is the v0.1 side).
- The chunks SEFIX-124 delivers by lexical widening (v2 files) are not the ones the dense re-rank + sidecars deliver: 8 lost, 11 gained, net +3.
- Diagnostic (post hoc, not the verdict): RS_SE_SCOPE=all (F2 also on the vec packs) = article 57 but chunk-level 45 / cm 16 / v0.1 29 unchanged (main.scopeall.jsonl): the extra article-level hits are not fact chunks. Junk 3.23.
- Kept tokens and junk are the stack's good side (fewest kept words of the SEFIX arms, junk 0.86x); wall unmeasured (R1 pays a second wide retrieve + embed; MacBook shared with R3+R4 replays).
Caveats: dev items, self-tests written from these two threads (install value), 0 LLM so no answer quality, deterministic replay so margins are item counts. UNKNOWN: whether SEFIX-124's own answer screen (running) converts its 42; if it does, the cheaper route is SEFIX-124 on v2 files, not a stack.
Files: run_stack.sh, tools/cl_stack.py, chunklevel_stack.json, replays/main.{off20,on,scopeall}.jsonl (+ .packs/.err/.rerank.log; gitignore-class), CALLS.md.
