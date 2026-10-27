# P-8: batch the pack search's single-row SQLite lookups (title resolution, article rows, article meta): −63% bridge calls, identical results
TL;DR: Besides decompression (P-7b), the moto's 3.2 s retrieval pays for **~445 separate `expo-sqlite` async calls per question**. Each crosses the JS↔native bridge, and Android's `expo-sqlite` async path is the slow one in public comparisons. Most are exact title lookups (≈ 140 per question: every n-gram candidate × every source × title + redirect) and per-candidate article/meta rows in the BM25 loop. Prefetching them in **2 queries per table per question** cuts calls to **~164 per question (−63%)**, with **byte-identical** search output (0/178 hit lists differ, full hit objects, at k = 3 and k = 6; 0 of 25,596 title keys differ from the original single-row queries).
Lane: Sonar (retrieval latency; F2) · Status: ready-to-test, **criterion frozen 2026-10-03, before any run** · Priority: A (run in the same phone session as P-7b)
Axes moved:
- latency ↓, size UNKNOWN until the phone measures the per-call cost: at 1–3 ms per async call, −0.3 to −0.85 s of retrieval;
- quality/safety unchanged by construction;
- memory: the prefetch holds one question's rows (≤ ~80 article rows + meta per pack), cleared at each search.
Fits BOAR? One file, `src/rag/wikiPack.ts`: patch `exp/24-sql-batching/p8-wikiPack.patch` (146 lines, sha256 `75751ea52af4f2cb…`, against `upstream/main` 0cfd4a77).
- `prefetchTitles()` at the start of `titlesInQuestion`: one `articles … title COLLATE NOCASE IN (…)` query and one `redirects … IN (…)` query. `resolveTitle` answers exact lookups from it (most-viewed per (title, source), ties to the lowest id, then the most-viewed redirect: the single-row queries' answer, checked key by key).
- `prefetchArticles()` after `bm25Candidates`: one `articles WHERE id IN (…)` query and one `article_meta` query. `article()` reads from it.
- Fuzzy lookups, blocks, FTS and stems are untouched.

Evidence (`exp/23-device-retrieval-profile/`, `exp/24-sql-batching/`):
- Device: moto retrieval p50 3.1–3.3 s vs desktop 0.2 s (P-7 card). Per question, the pack search issues ~445 SQL calls (`prof2.txt`, `p7.txt`).
- Public data on the per-call cost:
  - PowerSync's React Native database comparison (2024-07, Expo 51, async APIs only, unbatched 1000-insert test, Galaxy S22) reports op-sqlite far ahead of expo-sqlite on Android; the per-op numbers are only in images, so they are not used here.
  - op-sqlite's author reports ~8× vs expo-sqlite on Android for a large query.
  - No published per-call figure for `getFirstAsync` → UNKNOWN, measured by this run.
- Identity:
  - `p8.txt`: 25,596 (source, title) keys, prefetch vs original queries, 0 mismatches.
  - `verify.txt`: clean patch vs `upstream/main` in the replay harness, 89 public questions × 2 packs, `JSON.stringify(hits)` identical 178/178 at k = 3 and at k = 6.
- Remaining calls after P-8 (`p8b.txt`, per question):
  - blocks 61 (P-7b shrinks their cost, not their count);
  - stemmer df/temp-table 26 + 3 × 17;
  - FTS vocab 15;
  - BM25 ~2.

Frozen criterion (arm `p8-sqlbatch` = engine 0cfd4a77 + `p8-wikiPack.patch`; packs = the P-7b 16 KB packs if P-7b passes, else the current ones; moto g75, 1.5B, airplane mode, 2 reps, the P1 protocol):
0. Desktop pre-check: the 72 items' pre-answer sources (title, section, source, similarity, passage text), `retrieval.raw` and answer text are **byte-identical** to the same packs without the patch. The unit suite passes. Any difference → stop.
1. **Moto retrieval p50 ≤ 0.9× the same packs without the patch.** Run back to back in one session, so the pair also measures the per-call cost: Δms ÷ 281 calls.
2. TTFT p50 reported; 0 BOAR kills; 0 errors.
- Suggested session order: base → P-7b (packs only, no build) → P-7b + P-8 (one dev build). Three arms, each 2 reps.
