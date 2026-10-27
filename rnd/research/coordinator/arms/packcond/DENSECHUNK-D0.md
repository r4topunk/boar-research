# DENSECHUNK D0: would chunk vectors reach the fact chunk? (PACKCOND, 0 LLM / 0 judge calls, 2026-10-12)

**Headroom numbers (the coordinator decides):** the F0 fact chunk is in its pack's dense top-12 at cos ≥ 0.55 on **23/32** in-pack items (all 23 also clear 0.70). In the fused simulation the F0 article is in raw6 on **22/32** (baseline 19). With dense-first2 it is on **23/32**. The gold count over 86 v0.2 items rises 19 → 22–23. On the 9 resolvable gold items, fused drops 7 → 6 and dense-first2 holds 7 → 7. Churn is total: 85–107 of 107 retrieving lists change, and R20 changes 13–18/20.

## Method
- `tools/densechunk_embed.mjs`: every chunk of both packs (no sampling, **f = 1**, so every rank below is exact). Embedding text: `${articles.title}\n${sectionAt(article, start)}: ${chunk text}`, or `title\n text` when the chunk has no heading. That is packHitToChunk's body under the plain title that the lead vectors use. It runs through the builders' `embedChunks` (bge-small q8_0, the app GGUF sha ec38e8…, 1,200-character cut) and then `quantizeInt8`. Scoring uses the dequantized int8 vectors.
- Throughput on the MacBook: Metal at 8 threads runs at 163–167 chunks/s (Wikivoyage 548,051 in 55.4 min). CPU at 3 threads, run in parallel, did 62.6/s (crypto 54,998 in 14.7 min). Total compute was 55 min, under the 75-min cap.
- Query vector: the replay shim's own call (`getEmbeddingFor(query)`, ctx 512, no prefix) on the `query` of p4b-v02.jsonl (107/110; 3 items never retrieve). Check: lead cosines vs replay-p4b's top-5 lists, 1,070 pairs, max |Δ| 5e-5.
- `tools/densechunk.py` (`python3 -I`): per item, the cosine against every chunk of its F0 pack(s); the R20 control items use both packs. F0 hit chunks are the 105 P1 jev hits. "F0 article" = the article of any hit chunk (the SECTIONHIT definition, baseline 19) ∪ the p4-diag f0_articles; `_p4def` columns use p4-diag only (baseline 17).
- Simulation over all 110 v0.2 items, with both packs installed. Semantic list = per-pack top-12 at cos ≥ floor (0.55; variant 0.70 = gateByRelevance). Lexical list = the engine's raw minus its named/step prefix (`prefix_n`), scored linearly by rank (raw has no scores). Fusion follows fuseRetrievalResults: max-normalised 0.5/0.5, summed when the chunk id (`pack:<id>:<chunk>`) is in both lists, at most 2 per title. Then prefix first and cut at 6. Dense-first2 = prefix + top-2 dense chunks + the rest of raw, cut at 6.

## Per P1 bucket (in-pack 32)
| bucket | n | F0 chunk in top-12 ≥ .55 | best F0 chunk rank ≤ 100 | median best rank | F0 article rank ≤ 5 | art raw6 base / fused / gate.70 / dense-first2 |
|---|---|---|---|---|---|---|
| used-right | 7 | 7 | 7 | 1 | 7 | 7 / 7 / 7 / 7 |
| used-wrong | 5 | 5 | 5 | 4 | 5 | 4 / 5 / 5 / 5 |
| retrieved-not-used | 7 | 4 | 4 | 5 | 4 | 4 / 4 / 4 / 5 |
| dropped-by-grounding | 7 | 5 | 7 | 10 | 3 | 4 / 4 / 4 / 4 |
| not-retrieved | 6 (1 no retrieve) | 2 | 4 | 20 | 2 | 0 / 2 / 2 / 2 |
| **all** | 32 | **23** | 27 | 3 | 21 | 19 / 22 / 22 / 23 |
Best F0 chunk rank ≤ 1/3/6/12/50/1000: 9/16/21/23/27/29. Median best F0 chunk cos 0.750 vs median best non-F0 cos 0.764; the F0 chunk beats every non-F0 chunk on only 13/31. Median 4 of the top 12 come from an F0 article.

## Simulation (raw6; 110 v0.2 items, 107 retrieve)
| variant | F0 art /32 (p4def /32) | F0 chunk /32 | gold /86 | gold resolvable /9 | R20 changed | v0.2 changed | F0 enter/leave |
|---|---|---|---|---|---|---|---|
| baseline (engine raw) | 19 (17) | 9 | 19 | 7 | 0 | 0 | – |
| fused, floor .55 | **22** (21) | 17 | 23 | **6** | 18 | 107 | 4/1 |
| fused, gate .70 | 22 (21) | 17 | 22 | 6 | 13 | 85 | 4/1 |
| dense-first2, .55 | **23** (22) | 18 | 23 | **7** | 18 | 107 | 4/0 |
| dense-first2, gate .70 | 23 (22) | 18 | 22 | 7 | 13 | 87 | 4/0 |
- Gold: crypto-A06 enters, travel-local-A01 leaves (all variants), and crypto-B05 also leaves (fused). Most of the +3/+4 on the 86 items comes from items with no resolvable gold, through the scorer's bare-title rule. Dense ranks of the 9 resolvable gold articles: 1, 1, 1, 5, 8, 13, 19, 104, 359.
- Declared gate: part 1 is 23 ≥ 12 (PASS). Part 2 is fused 22 ≥ 22 (exactly at the bar); gold not lower holds on /86 (23 ≥ 19) and fails on /9 (6 < 7). Dense-first2 meets both parts on both gold counts.

## Cost
- Pack size: Wikivoyage 548,051 × 384 int8 + 4-byte scales = **212.6 MB** (+61 % on 351 MB). Crypto 54,998 → **21.3 MB**. Row order = chunk id, so no id column is needed.
- Desktop numpy scan per query: 19 ms on the prenormalised f32 matrix (842 MB RAM), 90 ms when converting int8 per query. Crypto 2 / 9 ms.
- Phone JS brute force (assumed 20–50 M int8 multiply-adds/s, single thread, vectors in RAM): Wikivoyage 210 M MAC = **4.2–10.5 s per query**, crypto 0.4–1.1 s. Reading 212 MB from SQLite per query would add more.
- Two-stage (lead scan → chunks of the lead top-50 articles): 13.1 M + ~0.3 M MAC = 0.27–0.67 s. The F0 chunk stays in the two-stage top-12 on **20/32** (vs 23 brute force). The F0 article's lead rank is ≤ 5 on 19 and ≤ 50 on 23; 2 brute-force hits have lead rank > 50.

## Caveats
- Format-1 packs in the app do **not** brute-force their vectors: `searchPacks` reranks only the BM25 top-400 candidates by cosine. Only the bundled KB's `semanticSearch` scans everything. A full scan over a format-2 pack would be a new code path (cost above).
- The lexical scores are rank-linear stand-ins, and dedupeArticleCopies/explainingFirst are not replayed. The fused raw6 and the churn figures are approximations; the dense ranks are exact.
- This is dev-style v0.2 (burnt) and one seed's queries. F0 = jev hits (P1), so the 23/32 says the right chunk is reachable, not that the answer improves.
- Outputs: `aggregates/densechunk.json`, `blind/bench-v02/runs-packcond/densechunk-v02.jsonl` (simulated lists, script-only). Vector caches are in `shared-data/packs/work/densechunk/` (~1.2 GB incl. f32).
