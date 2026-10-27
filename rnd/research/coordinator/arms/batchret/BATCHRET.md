# BATCHRET result (2026-10-20, main): batching the format-2 pack lookups cuts SQL calls per retrieve() by 94.9 % (937 → 48) with byte-identical retrieval on 390/390 public dev items. PASS

Criterion: BATCHRET-criterion.md, sha256 27bf34a2 (frozen and committed in rnd ced08c38 before any engine change). 0 LLM calls, 0 judge calls, 0 paid. MacBook (desktop node:sqlite). Phone not touched.

## TL;DR
- Change: src/rag/wikiPack.ts only (+ a new test file). Per-term df lookups, per-title-candidate tokenizer passes, per-(n-gram × source) title and redirect probes, and per-candidate article/url-license/block reads become one `IN (...)` or VALUES-join query each, plus small caches. On a tie for the best title match, the one-row query still runs, so SQLite's own tie order is kept.
- Parity: **390/390 identical** on every field: the full chunk objects with text, score, similarity, `action` and order, reasonCodes, and the full sources event. The base was also identical to itself across two passes (390/390), and the candidate likewise (390/390).
- SQL calls per retrieve() (all databases, mean): **937.2 → 47.9 (-94.9 %)**. On the claim kit (v0.1): 517 → 33 (-93.7 %).
- Desktop retrieve() wall p50 (pass 2): **154.4 → 136.0 ms (-12 %)**, and p90 242.8 → 209.3 ms. The desktop gain is small because node:sqlite calls are synchronous and in-process. The phone pays 7–9 ms of bridge round trip per call (LITELAT).
- Tests: full suite 125 files / 1594 tests pass (base 124 / 1586, +8 new). `tsc --noEmit` is clean on both trees.
- Projected phone gain (a projection, not a measurement): TTFT -2.7 to -3.4 s on the 1.7B (9.4 → about 6.0–6.7 s), and safety-card wait 8.9 → about 3.5–4.4 s. The coordinator times it on the phone.

## 1. Verdict by the frozen rule
| clause | needed | measured | ok |
|---|---|---|---|
| (a) parity, cand p1 vs base p1 | 390/390 identical | 390/390 (v01 60/60, st180 180/180, cw150 150/150) | yes |
| (a) harness determinism, base p1 vs base p2 | 390/390 | 390/390 (cand p1 vs p2 also 390/390) | yes |
| (b) full test suite + no new tsc error | pass | 1594/1594 pass; tsc 0 errors (base 0) | yes |
| (c) SQL calls per retrieve() drop | >= 80 % | -94.9 % (pooled mean, pass 1) | yes |
| (c) desktop retrieve() p50 drops (pass 2) | candidate < base | 136.0 < 154.4 ms | yes |

**PASS.**

## 2. SQL calls and desktop time per set (374 retrieve() calls; 16 items never retrieve: instant, places or small talk)
| set | items | identical | SQL calls/call base → batched (mean) | p50 | pack-only mean | retrieve ms p50, pass 2 | ms p90, pass 2 | summed SQL ms p50 (desktop) |
|---|---|---|---|---|---|---|---|---|
| v01 (kit) | 60 | 60 | 517.2 → 32.6 (-93.7 %) | 479 → 33 | 515.2 → 30.6 | 120.8 → 99.2 | 170.5 → 139.6 | 60.8 → 38.5 |
| st180 (kit + pack) | 180 | 180 | 1001.1 → 50.1 (-95.0 %) | 976 → 49 | 999.1 → 48.1 | 162.0 → 139.9 | 232.7 → 209.7 | 71.0 → 52.4 |
| cw150 (kit + pack) | 150 | 150 | 987.1 → 49.8 (-95.0 %) | 956 → 49 | 985.1 → 47.8 | 158.3 → 144.3 | 259.4 → 230.9 | 68.7 → 54.8 |
| **all** | **390** | **390** | **937.2 → 47.9 (-94.9 %)** | 934 → 48 | 935.2 → 45.9 | **154.4 → 136.0** | 242.8 → 209.3 | |

By statement kind (mean per retrieve() call, pooled, base → batched): title probe 199.6 → 0, redirect probe 199.3 → 0 (replaced by 5.8 VALUES-join queries; the harness files them under `other:WITH q(t)`), qtok (tokenizer) 124.3 → 8.9, article 121.3 → 2.9, block 114.4 → 14.1, article_meta 68.4 → 1.9, df 63.9 → 2.9, fts_v 36.7 → 2.8, disambiguation title 0.7 → 0. Unchanged: BM25 2.9, lead_vecs 2.9, format-1 FTS 1, knowledge-base 1. The remaining calls per pack are about 3 tokenizer + 2 df/fts_v + 2 title + 1 BM25 + 1 lead_vecs + 1–2 article rows/meta + about 5 block windows.

## 3. What changed (wt/batchret, branch `batchret`, commit 8e9c49d6 on b546706c)
- `stemsMany(texts)`: one DELETE + one multi-row INSERT + one read of a new `temp.qtok_i` (fts5vocab instance) `ORDER BY doc, term` (the row vocabulary's byte order), then `docFreqs` (df `IN`, then fts_v `IN` for terms df lacks; df still wins with doc 0; push only doc > 0). `stems(text)` = `stemsMany([text])[0]`. searchDetailed stems the question and all its title n-grams in one pass. Caches: stems 512 texts, df 8192 terms.
- `prefetchTitles(titles, sources)`: one articles and one redirects query, with the titles as `WITH q(t) AS (VALUES …)` joined with `a.title = q.t COLLATE NOCASE` and `r.title = q.t`, so each comparison uses the same collation as the bound-parameter query. It keeps the max-views row per (title, source). On a tie between different ids it puts nothing in the cache, so resolveTitle's own `ORDER BY views DESC LIMIT 1` query runs. It also records id → title for `isDisambiguationPage`. `resolved` LRU 512 → 8192. Called at the top of titlesInQuestion (n-grams + singulars × sources).
- `prefetchArticles(ids)`: article rows (no text) and url/license in one query each, in a row cache (2048). Block ids go on a per-search plan in candidate order. `block()` on a miss fetches that block plus the next un-cached planned blocks (window 8) as compressed bytes, and decompresses only the block asked for. Per-search state is cleared at searchDetailed entry and in `finally`. Called for named articles, keyword candidates, the action pool and `bm25()`.
- Unchanged: ranking, gates, the fuzzy title path, articlePassages' chunk query, the decompressed block/article LRUs (16).
- New tests (src/rag/wikiPack.batch.test.ts, 8): a hand-built pack with ties (same title and views), case variants, a non-ASCII title (NOCASE folds ASCII only), tied redirects, partial article_meta and a partial df, with both NOCASE and BINARY redirects. Batched title, article and stem lookups equal the one-row reference queries, ties fall back exactly as intended, and call counts are pinned. On the built mini-wiki pack: stemsMany equals per-text stems and the pre-batching algorithm; search is identical cold and warm in at most 20 SQL calls.

## 4. Projected phone effect (LITELAT per-call cost; a projection, not measured)
LITELAT (Pixel 8a, 1.7B, litelat-9): 435 serial pack SQL calls per model question (3,650 ms summed, 7.3–8.7 ms per call), and 665 calls (5,729 ms) per safety-card question. Applying the kit's -93.7 % call cut:
| question type | calls before → after | serial SQL saved | caveat | projected |
|---|---|---|---|---|
| model answer (TTFT 9.4 s) | 435 → about 27 | 408 × 7.3–8.7 ms = 3.0–3.5 s | the batched calls carry more data (block windows up to 8 blobs, IN lists): allow +0.1–0.3 s | TTFT **-2.7 to -3.4 s** (to about 6.0–6.7 s, -29 to -36 %) |
| safety card (8.9 s) | 665 → about 42 | 623 × 7.3–8.7 ms = 4.5–5.4 s | same | card wait to about 3.5–4.4 s |
The JS remainder of the pack search (about 1.6 s: zstd, scoring) is not touched. LITELAT's E2 (card before retrieval) remains the lever for cards.

## 5. Deliverables
- Patch: arms/batchret/batchret.patch (`git diff b546706c 8e9c49d6`, wikiPack.ts + wikiPack.batch.test.ts), sha256 `57367f4adab2ee8fed5ab9d3f539fe97e84f033c0f89d87ccb2533d2e63f09cf`. Same file at handoff/batchret-2026-10-20/batchret.patch (+ .sha256).
- Port note for the native Kotlin engine: handoff/batchret-2026-10-20/PORT-NOTE.md. It covers the function-by-function mapping onto android-native/.../rag/WikiPack.kt (fullnative-dev 0be84ac), the batched SQL and the identity rules. Nothing was sent to anyone.
- Worktree: <workspace>/wt/batchret, branch `batchret` (off wt/pr1 `pr/cut7-engine` b546706c), commit 8e9c49d6. Not pushed. boar-app/ untouched.

## 6. Notes and deviations
- Harness: tools/parity-replay.ts (copy of replay-retrieval.ts + full-chunk output + a per-statement SQL log via tools/expo-sqlite-log.mjs), tools/run_parity.sh, tools/compare_parity.py. After the runs, compare_parity.py was changed only to read the gzipped outputs; the numbers it prints are unchanged. Runs: runs/{base,cand}.p{1,2}/ (gzipped), with summaries in compare-p1.json (parity and SQL) and compare-p2.json (timing).
- Desktop SQL counts on v0.1 (517 per call) are higher than LITELAT's phone count (435) because the item sets differ (v0.1 60 vs litelat-9). The cut ratio is what the projection uses.
- The native Kotlin engine calls SQLite through JNI and is synchronous, so its per-call overhead is far below expo-sqlite's 7–9 ms. The port's gain there has not been measured.
- Not done here: phone timing (coordinator), and a window size sweep (BLOCK_WINDOW 8 leaves 14 block calls per retrieve(); a larger window trades round trips for blob bytes).
