# PACKCOND P4b step 0, D0 diagnostic: PACKDENSE (2026-10-12; 0 LLM, 0 judge calls, MacBook)

Criterion: PACKDENSE-criterion.md (sha256 e2815dd8…), stage 0. D0 has no pass/fail; it declares the variant (below).

## Method
- `tools/replay-p4b.ts` (copy of replay-pg.ts + `--p4b`) runs the engine's OFF retrieval exactly as P4 did (`--deep --gate rules --k 6 --pool 20`, wt/packcond, packGround off, `--tasks-from` the H v0.2 s42 traces, cache deepcovfb). On the engine's search query and `embeddingEngine.embed(query)`, it then uses the tree's own functions (`searchWikiPacks`, `titlesInQuestion`, `bm25Candidates`, `articlePassages`, `coverage`, `cosineSimilarityInt8`) for every target article: resolved with `resolveTitle(fuzzy false)`, then checked for named/share, BM25 article rank at pool 80/400/2000 (perArticle 1), in_pool80 (perArticle 2), cov_best over all chunks, lead cosine, and lead rank from a full `lead_vecs` scan. It also records the top-10 lead-cosine articles per pack with their passages.
- `tools/p4b_diag.py` → `aggregates/p4b-diag.json`, one row per item (110 v0.2 + 60 v0.1) with ids, titles, ranks, cosines and booleans only.
- Identity: the OFF raw lists equal pg-off-H32 **32/32** and pg-off-R20 **20/20**. raw, kept, codes, pool, k and task are all identical, and the raw lists match the H traces 110/110. The v0.1 recall@6 is 0.3846, the same as pg-off-v01.
- Targets: F0 = 63 articles on the 32 items (58 resolve; 5 Wikivoyage titles do not). Of the v0.2 gold titles, 9 of 129 resolve in a pack: 3 are Wikivoyage and 6 are in the crypto enwiki subset. None of the 46 v0.1 gold titles resolve. One class-(a) item, travel-practical-A02, never calls retrieve, so a dense rule cannot reach it.

## Headroom (best F0 article per item; lead rank is within its pack)
| | n | lead rank ≤1/3/5/10 | lead cos ≥.50/.55/.60/.65/.70 | BM25 ≤80/400/2000 | cov ≥0.5 | named |
|---|---|---|---|---|---|---|
| class (a), not in raw | 15 | 2 / 5 / 5 / 6 | 12 / 10 / 8 / 5 / 1 | 7 / 12 / 14 | 2 | 5 (share < 0.5) |
| in raw (b/c/d) | 17 | 10 / 12 / 13 / 14 | 17 / 16 / 15 / 11 / 9 | 17 / 17 / 17 | 13 | 9 |

- Noise floor: the best non-target lead cosine per item has p50 **0.687** and p90 0.755 on the 32 (p50 0.672 / p90 0.777 over the 107 retrieving v0.2 items). The F0 targets have p50 0.617. Per pack, the top-1 cosine has p50 0.566 in crypto and 0.650 in Wikivoyage. bge-small cosines are compressed, so the floors 0.50–0.60 sit **below** the noise and filter almost nothing.
- Scan cost (node:sqlite, 161 queries): Wikivoyage has 34,002 vectors, scan p50 74.8 ms, p90 100 ms, max 155 ms (the cold first query). Crypto has 3,141 vectors, scan p50 5.8 ms. The SQL read of the blobs dominates: the cosine alone over cached vectors takes p50 27 ms (Wikivoyage). Engine retrieve() p50 is 156 ms.

## Rule simulation on the engine's raw list (k = 6)
Rule: per pack, take the top-M articles with lead cosine ≥ floor that are not engine named hits, P passages each. Insert them after the named/step prefix and before the rest, dedupe by chunk id, cut at 6. Baselines (raw6): F0 **17/32**, v0.2 gold 19/86, v0.1 gold 15/39. Subset of the P = 1 grid (full grid with P = 1/2, M = 1/2/3/5 and floors .50–.75 is in the json):
| M | floor | G1 F0 raw6 | gold v0.2 | gold v0.1 | R20 raw changed | v0.2 changed /107 | F0 enter/leave |
|---|---|---|---|---|---|---|---|
| 1 | .50/.55/.60 | 19 | 24/25/25 | 18/19/19 | 18/18/15 | 107/107/95 | 2/0 |
| 2 | .50/.55 | 21 | 24 | 19 | 18 | 107 | 4/0 |
| **2** | **.60** | **21** | **24** | **19** | **15** | **95** | **4/0** |
| 3 | .60 | 21 | 25 | 19 | 15 | 95 | 4/0 |
| 3 | .50 | 17 | 21 | 19 | 18 | 107 | 5/5 |
| 5 | .60 | 20 | 25 | 20 | 15 | 95 | 4/1 |
| 2 | .65 | 20 | 24 | 18 | 11 | 66 | 3/0 |
| 1–5 | .70 | 17–18 | 19–20 | 17 | 6 | 33 | 1/0–1 |

## DECLARED VARIANT (fixed before the gate replay)
**M = 2 per pack, floor = 0.60, 1 passage per article.** The passage is the best-scoring non-lead section from `articlePassages(id, stems, 1, action, explain)`, or the lead when the article has none (for an explain question, articlePassages' first passage). Dense hits go after the named and step hits and before the fused BM25/semantic hits, and they never displace a named hit.
- Why: it reaches the highest projected G1 (21) of any grid cell that keeps both gold counts at or above baseline. Among the cells tied at 21, it has the lowest R20 churn (15) and the fewest added slots (192 vs 273 for M = 3). Above 0.60 the floor costs G1 (0.65 → 20, 0.70 → 18). Below 0.60 it adds churn with no G1 gain (M = 3 even loses in-raw F0 articles). Passages: the best section's coverage beats the lead's on the F0 articles (mean 0.38 vs 0.22), which matters for G2 (onTopic/compression). G1 and the gold rules match on titles only, so the simulation does not depend on which passage is chosen.
- **Projected gate: G1 21/32 < 22 (FAIL by 1).** The ceiling is also short. Only 5 of the 15 class-(a) F0 articles rank in their pack's lead top-5 (6 in the top 10), and 2 of those are already counted. Even a lossless M = 5 reaches at most 22. Projected G3 raw passes (24 ≥ 19, 19 ≥ 15). The R20 raw churn is 15/20, above the 10/20 kept-churn limit if raw churn carries over into kept churn.

## Caveats
- The simulation ignores dedupeArticleCopies, the action-path lay-source additions, compression, grounding and the health filter. G2 and the kept-side G3 cannot be projected here. Of the 4 F0 entries, danger-B01 runs under grounding:health-strict, which may drop it. honesty-refusal-A02 has an empty raw list today, so its kept list depends on grounding accepting a lone dense passage.
- Most of the projected gold gain comes from the scorer's bare-title rule: a "Wikivoyage: X" passage matches the Wikipedia gold "X". The genuine changes are +1/−1 on v0.2 and 0/−1 on v0.1, so under a strict-source rule v0.1 raw6 would be 14 < 15.
- The floor does almost no work at 0.60 (it is below the noise p50 of 0.69), so the rule effectively adds the top-2 articles per pack on almost every question: 95/107 v0.2 and 45/54 v0.1 raw lists change.
- Gold targets that do not resolve (120/129 v0.2, 46/46 v0.1) are counted in the gold metrics by title match, not in the headroom.
- The scan is near the G4 limit on the cold query (155 ms). A cached int8 matrix (13 MB) brings it to about 27 ms.
