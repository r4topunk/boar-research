# CHUNKLEVEL (2026-10-22, 0 LLM / judge / Opus / paid / phone): article-level vs chunk-level fact delivery, MAIN keyed 92 = v0.1 52 + cooking/money 40
**Rule.** Article-level = the existing stage-K flag (union of kept `title+body`, plus the cm docId oracle). Chunk-level = the fact is inside ONE kept chunk BODY (no titles, no union). v0.1: `share_v01(q,[body])` >= 0.5 in some kept chunk (strict = 1.0). cm: a normalised `in_pack_facts` quote is a substring of a kept body (any quote; "all" = every quote found in kept chunks). Tool `tools/chunklevel.py`, data `chunklevel.json` (all 42 replays, per item). Loose token rule on cm gives +0/+1 vs substring: the substring rule is not the cause.

| arm (replay) | article /92 | chunk /92 | cm chunk /40 (all quotes) | v0.1 chunk /52 (strict) | overstated |
|---|---|---|---|---|---|
| B0 stock (K1 kit) | 22 | 21 | 0 | 21 (13) | 1 |
| compose N0.stock | 22 | 21 | 0 | 21 (13) | 1 |
| compose N10.stock | 29 | 26 | 1 (1) | 25 (16) | 3 |
| compose N10.gidf (ARM-G) | 32 | 28 | 2 (1) | 26 (16) | 4 |
| sefix F1 | 40 | 35 | 9 (2) | 26 (16) | 5 |
| **sefix F1b (v3 sidecars, main.v3-extra)** | **45** | **32** | **7 (2)** | 25 (14) | **13** |
| sefix F1b+F3+F4 | 53 | 37 | 10 (3) | 27 (15) | 16 |
| reader RD3off / RD3on | 45 / 47 | 32 / 35 | 7 / 9 (2 / 5) | 25 / 26 | 13 / 12 |
| sefix F1F2F3 | 52 | 45 | 19 (7) | 26 (16) | 7 |
| **SEFIX-ALL (F1F2F3F4, v2 kit)** | **55** | **47** | **19 (8)** | 28 (17) | **8** |
| gate p1 (= off) / g2 v3 / KFULL | 32 / 25 / 28 | 28 / 24 / 23 | 2 / 0 / 0 | 26 / 24 / 23 | 4 / 1 / 5 |

**Corrected deltas (article -> chunk), MAIN 92.**
| step | article | chunk | what changes |
|---|---|---|---|
| N0.stock -> N10.stock | +7 | +5 | packs add real facts; 2 of 7 are other-chunk-of-the-article |
| N10.stock -> N10.gidf | +3 | +2 | gidf merge holds up |
| N0.stock -> N10.gidf | +10 | +7 (8 gained, lan-hlt-003 lost) | cooking-004, -009 were article-only |
| N10.gidf -> **F1b** | **+13** (15 gained, 2 lost) | **+4** (6 gained, 2 lost: lan-hlt-002, vit-trv-003) | cm +2 -> +5 (not +14), v0.1 -1 (unchanged). 9 of the 15 article gains are cm threads whose fact chunk was NOT kept (cooking-006/010/020, money-003/013/014/016/017/020) |
| N10.gidf -> **SEFIX-ALL** | **+23** (0 lost) | **+19** (0 lost) | cm +17, v0.1 +2; 6 article-only (lan-cmp-005, cooking-006, money-007/013/016/019) |
| F1b -> SEFIX-ALL | +10 | +15 | different kits (v3 sidecars vs v2); F1b is the inflated arm, SEFIX-ALL is 85 % real |

**Reading.**
- F1b's "14 newly delivered cm facts" (answer screen, dU +0.001) are +5 at chunk level (cm article 18 -> chunk 7, vs ARM-G 4 -> 2): about 9 of the 14 are threads whose fact chunk was not kept, so "fact present, no gain" rests on ~5 items, and the flat result is mostly missing delivery. (The 9 that still carried the warning line are a separate count.)
- SEFIX-ALL delivers: 19 chunk-level cm vs 2 for ARM-G (the dU +0.0185 over ARM-G is on a real +17, +2 v0.1). 8 of its 19 cm items have all quotes delivered; 11 only partial quotes.
- The v0.1 side is nearly clean (overstatement 1-2 per arm): the lexical rule across chunks rarely differs from one-chunk. Overstatement is a cm / sidecar effect. vit-cry-002 is article-only in every arm (terms split across chunks).
- Order of real lever: F1+F2+F3 (cm 9 -> 19 at chunk) > gidf (+2) > N10 packs (+5) > F1b sidecars (+5 but loses 2 v0.1).

**Live traces (titles only; kept chunk text not logged) -> scored on the matching replay, title-list parity as check.**
f1b-s42 vs main.v3-extra 89/92 parity (art/chunk on the parity items 43/31); sefixall s42 and s43 vs F1F2F3F4 86/92 (50/42); ARM-G vs N10.gidf 83/92 (28/25), ARM-S vs N10.stock 83/92 (26/24); rd2 = F1b traces 89/92; rd3 main vs RD3on 89/92 (45/33); gate P1 vs p1 68/92 (25/22); rd1 main vs v3-extra 63/92 (rd1 is another switch, no exact replay). Non-parity items: ids in `chunklevel.json` `live.*.nonparity`.

Not scored: searchpar r5 replays (qform and longsession chains, not MAIN-97); searchpar/main.r4 (a running job's file, equals main.off at 45/32); sefix RD1-off holds 65 rows (60 keyed, 31 art / 27 chunk). Caveats: lexical, dev items, replays not answers; chunk-level is a lower bound (a fact paraphrased across two kept chunks is not counted).
