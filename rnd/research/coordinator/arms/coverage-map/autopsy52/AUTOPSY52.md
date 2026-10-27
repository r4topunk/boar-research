# AUTOPSY52 (2026-10-22, 0 LLM / 0 judge / 0 paid / 0 phone, MacBook): the 52 "fact in a pack, never reaches the model" items under N10.gidf

TL;DR
- The 36 cooking/money items are mostly **thread-finding failures inside the SE pack**, not keep-step drops. Of 15 cm "S3" items, the engine's own list (k = 3-4) held the gold thread for only 3. In all 3 the health-strict filter dropped it. The other 12 were only in the wide-12 side list (ranks 4-11), so the engine never saw them.
- Root cause 1 (lexical): `WikiPack.queryTerms` keeps only stems under 2 % document frequency *per pack*. Inside a domain pack it drops the domain words (credit, score, rice, vinegar, milk, garlic, tax, bond, car) and searches on incidental words (walk, whenever, someone, within, list). For 15/36 the gold thread is not even in the bm25 pool of 80.
- Root cause 2 (dense): qa-cooking-se and qa-money-se (wave3) have **no chunk_vecs**. The travel, health and outdoors SE packs (v3proto) do have them, so they take the dense slots on money questions. Both packs do have lead_vecs (question + accepted/top answers, 2,500 chars). **The gold thread is lead-cosine #1 of the whole pack for 18/36 and top-3 for 26/36.** Every lexical variant is ≤ 11 at #1.
- Root cause 3 (keep): the learned health detector fires on 7 cooking/money questions (burnt pot p 1.0, jam jars, dry chicken, PayPal scam). Health-strict then keeps nothing (6 of the 7 end with 0 sources).
- v0.1 (16): 7 are router short-circuits (answer:facts-*, calculator), so nothing was lost. 2 are ruler false positives with the content absent. 7 are known engine mechanisms, 2 of them a new keep-step gate (proper nouns).
- Fixes F1+F2+F3 recover **21/36** cm items (23 with the L=2 variant) at the FACTPRESENT level, against **≤ 1/40** expected collateral change.

Method: an instrumented clone of rs-H4 in the scratchpad dumped every pack search: terms, bm25 pool of 80, hits, relevance rejects and the full-pack lead-cosine top 300. It ran with the compose MAIN recipe and RS_MERGE=gidf, and its raw/wide/kept are identical to compose/replays/main.N10.gidf.jsonl on 52/52 items. Gold = the self-test quote located in the oracle thread (gold_cm via cm-oracle.json). Every cm fact sits in an answer chunk; 33/36 have one in chunk 1-2 (accepted answer + next, per convert/formats/stackexchange.mjs). Lexical what-ifs: pack-local FTS5 bm25 replica (work/termsim.py). Per-item JSON: autopsy52.json (ids, facts, ranks, winners, sub-stage, fix flags; no question text). Scripts are in work/.

## Classes (52)
| class | n | sub-stage | ids (short) | cheapest fix |
|---|---|---|---|---|
| A1 SE lexical miss (gold not in pool 80) | 14 | domain terms dropped by maxDf 2 % | ck-006/007/014/016, mn-001/002/005/009/012/014/015/017/018/020 | F1 (8), F2 (4) |
| A2 SE same-pack threads outrank | 9 | gold in pool (rank 4-61) or wide 4-11, raw full of other threads | ck-001/003/019, mn-003/010/011/013/016/019 | F1 (3), F1 L=2 (1) |
| A3 other packs take the raw slots | 5 | wide only, or in-pack hit beaten in the gidf fusion (mn-007: pack hits 1-2, travel/Wikivoyage first) | ck-010/011/020, mn-006/007 | F1 (2), F2 (1), L=2 (1) |
| A sibling-thread partial | 1 | mn-008: 1 of 2 facts in another thread (wide-only); gold thread lead rank 11 | mn-008 | none |
| B health-strict misfire | 7 | detector fires; onHealthTopic drops every SE chunk (3 had the gold in raw: ck-005/013/017) | ck-002/005/013/015/017/018, mn-004 | F3 (+F1/F2) |
| C router short-circuit | 7 | answer:facts-winner/dates/height/host/population/area, calculator-travel-distance | lan-ref-001/004/005, lan-rsn-007, lan-exp-006, lan-cmp-001, vit-trv-004 | none: not a loss |
| D content absent / ruler FP | 2 | "ACC" and single-word pool hits | vit-cry-007, lan-cmp-003 | content |
| E keep: onTopic proper-noun gate | 2 | gold raw #1/#2 dropped: "Nile" not in the Saltwater-crocodile chunk, "Earth" not in Amazon River | lan-cmp-005, lan-rsn-005 | per-entity gate (not in scope) |
| F engine, known | 5 | named EIP takes 3/4 raw (cry-009); health card (hlt-001/002); compression (cry-010); dense no-dedup (cmp-002) | vit-cry-009/010, vit-hlt-001/002, lan-cmp-002 | earlier autopsy H1/H2/H3 |
S2/S3 relabel: of the 21 S3 items, the gold reached the engine's raw list for 8. The other 13 are ranking misses that show up only in the diagnostic wide-12 list. The funnel's S3 should be split into "raw, dropped" and "wide only".

## Fixes (each behind an env switch; default off = byte-identical)
**F1 SE-LEAD (`RS_SE_LEAD=1`, `RS_SE_LEAD_TAU=0.77`, `RS_SE_LEAD_L=1`; engine only, no rebuild).** Scope: format-2 packs whose meta.sources is stackexchange and that have no chunk_vecs. When queryVec is set, scan lead_vecs once per query, with the matrix cached the way denseChunks caches its leadMatrix (int8, 26k + 35k rows). For the top L articles with cos ≥ τ, emit the chunks at positions 1-2 (accepted + next answer) as `semantic` candidates on the packDense2 append path (attachDenseCandidates → head-pass dense append under the existing 600-work budget). They skip onSubject, health-strict still applies, and the reason code is `headpass:selead:add:<chunk>`.
- Expected: **10/36 alone, 14 with F3; L=2 → 13 / 17.**
- Risk on the other 40: on all 97 items, no (item, foreign SE pack) pair reaches τ (max 0.765 for dng-005 → cooking; margin 0.005, so τ 0.78 is the safe variant and costs 2 recoveries). Own-pack cos on the 40 cm items is 0.72-0.90. The 4 kept cm items only gain their own thread's answers.
- Cost: a 23 MB int8 scan per query; phone speed unmeasured.
- Rebuild alternative (F1b): chunk_vecs sidecars for the two packs (g2-fullkit/mini/g2_sidecars.sh recipe; cooking 98k chunks ≈ +38 MB / 8 min, money 143k ≈ +56 MB / 11 min on the mini). That turns on the stock two-stage packDense2 (lead top-50 then chunk cosine), which reaches 32/36 gold threads (lead rank < 50) and picks the fact chunk itself. It is a pack rebuild plus the same crowding question G2 raised.

**F2 SE-TERMS (`RS_SE_MAXDF=0.25`; engine only).** In bm25Candidates, SE packs select terms with maxDf 0.25 (keepMin 3) instead of 0.02, so the domain words stay in the OR query. Variant `RS_SE_TERMS=gidf`: choose terms by the cross-pack df that H4 already computes, which keeps a word that is common in money but rare in the kit.
- Expected: the gold thread reaches the pack's top 3 for 16/36 (vs 4 now); with the fact in chunk ≤ 2 that is 8 without health-strict, 4 of them beyond F1 (ck-007, mn-005/006/012). This is an upper bound: the hit still has to win a raw slot in the gidf fusion.
- Risk: more SE bm25 mass on non-cm questions (qa-money already takes 14 % of kept slots). It has to be replayed with the junk-kept check. Wall: longer OR queries on two packs.

**F3 HEALTH-NOSOURCE-FALLBACK (`RS_HEALTH_NOSOURCE_FALLBACK=1`; answer.ts health branch).** Applies when onHealthTopic leaves 0 sources and no card condition fires (cardEmergency false, conversationCondition null). Ground the compressed sources with onSubject instead and let the head-pass appends through on onSubject. Reason code `grounding:health-fallback-subject`.
- In MAIN 97 it fires on exactly the 6 zero-source cm items. vit-hlt-001/002 have cards and are unchanged; dng-002/005 keep sources and are unchanged.
- Recovers ck-005 alone. It is the enabler for 4 more with F1 (ck-015/018, mn-004, ck-005) and 3 with F2 (ck-002/013/017).
- Risk: a real health question without a card could now answer from non-health sources. The H2 safety finding applies ("the card must win"), so the PR needs a Sonar-style health dev check.

Combined F1+F2+F3: **21/36** cm (L=2: 23). Not recovered (13): ck-001/003/014/019 and mn-001/007/008/009/011/015/017/018/019. These have lead rank ≥ 2 or a cosine under τ (mn-007 0.719), facts only in chunks 3-4 (mn-017/019), or no lexical route.

## Caveats
- Recovery = FACTPRESENT on the would-be context (fact chunk index ≤ 2 of the thread the fix brings), not a replay of the patched engine and not an answer. The next step is a frozen criterion, then a patched replay (identity switch-off; junk-kept ≤ 1.25×), then the Haiku divergence screen.
- The 40 self-test questions were written from these threads (paraphrased away from the title words). That inflates lead-vector wins compared with organic questions. The cm results also come from one pack pair; the v3proto SE packs already have the dense path.
- Lexical what-ifs use a pack-local bm25 (no gidf rescale): the replica's pool ranks differ by a few places from the dumped ones (e.g. mn-007 31 vs 58).
- The v0.1 key facts are paraphrased from the golds; C/D/F reuse the earlier AUTOPSY classes where the mechanism is the same.
