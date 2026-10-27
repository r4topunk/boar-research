# exp-26: Doc2Query-- at pack build time, L0 (Sonar, 2026-10-02 night)

TL;DR: **KILL at L0** (fast loop, ~50 min of the 2 h box). Even a *perfect* expansion gains 0 genuine keys on the 24 retrieval-inkit items: the test question itself, appended to the key chunk's FTS row, puts that chunk at BM25 rank 0–2 on 24 of 26 (item, pack) pairs. The engine never lacked BM25 rank. Two later checks block the expanded chunks: the passage-text coverage gate and the named-article path. Generated questions can't beat the oracle, so the Qwen generation run was not spent.

## What was measured

| Step | What | Result |
|---|---|---|
| 0 ceiling (`ceiling.mts` → `ceiling.json`) | Per keyed slice item and pack: chunks whose own text passes the precheck key; best rank of such a chunk in the BM25 list (pool 2000); whether today's `searchDetailed` hits carry it | Doc2Query can only reorder `bm25Candidates`. Named-article passages are chosen by `passageScore` on raw text, not FTS. On most items the key chunk is already at BM25 rank 0–7 and is lost later. About 8 items have it at rank 24–1215 or outside the pool. |
| FTS rewrite check (`fts.mts`, `fts_selftest.mts`) | Contentless FTS5 `'delete'` with the builder's exact (title, heading path, span), then reinsert | Rewriting 2,000 crypto chunks with identical text gives identical candidates and scores on 60/60 v0.1 questions; `integrity-check` OK |
| **L0 oracle** (`oracle.mts` → `oracle.json`) | Pack copies where the best key chunk per (item, pack) gets the **test question appended** (26 pairs). `searchDetailed` with the engine's k (from and-qwen-s42) and the bge-small query vector, base vs oracle | Picked chunk's pool-80 rank improves on 19/26 pairs and ends at 0–2 on 24/26 (e.g. 38 → 2, 73 → 0, −1 → 0). The other 2 stay outside the pool: vit-sci-002, vit-hlt-002. **Key-in-hits: +1 / −1, and both are false keys** (below) |
| Off-topic rate (`offtopic.mts` → `offtopic.json`) | Every pack hit for the 24 items, rated by bge-reranker-v2-m3 (exp-25 AUC 0.912): unhelpful < 0.46 (helpful p25), off-topic < 0.10 | base 109 hits: unhelpful 78.0%, off-topic **70.6%**. Oracle 97 hits: 74.2% / **67.0%** |

**Key-in-context@k:**
- The oracle already fails before compression.
- Its only key gain, vit-trv-004 → "Marathon race § Destinations", is a false positive: the key `28` matches "1920 to 1928".
- Its only loss, vit-trv-003 in the crypto pack, was a false key too: "bus/route" inside EIP text.
- **Genuine Δ key-in-context = 0** on 24 items.

**Off-topic:**
- The oracle's −3.6 pt comes from idf shift, not from better ranking. Appending a question adds rare terms ("singapor", "montenegro") to the crypto index, which moves stem weights, so some garbage crypto hits fall under the 0.5 coverage gate.
- An oracle-only artifact; not a property of real Doc2Query.

## Why it can't work alone (mechanism)
1. `searchDetailed` keeps a BM25 candidate only if `coverage(title + passage text, topic stems) ≥ 0.5` or its lead cosine is ≥ 0.70. An expansion-only match fails that gate by construction.
2. Example: vit-cry-005's genuine Privacy Pools passage (ERC-8262 § Related Work: "Association Set Providers") moves from rank 19 to 1 and is still dropped. It lacks "Tornado"/"Cash", the other half of the comparison.
3. Named articles (most in-kit items) take passages by raw-text `passageScore`, which FTS doesn't touch.
4. So Doc2Query is a **two-knob** idea (index + gate counts expansions). Under the fast-loop "one knob" rule, the index knob alone is dead.

## Not done (and why)
- Question generation with an open model:
  - benchmarked only. Qwen2.5-1.5B-Instruct: 1.6 s/chunk, 1 sequence. Qwen3-4B-2507: 5.7 s/chunk.
  - this MacBook is at 16 GB with RAM nearly full; 8 parallel sequences produced garbled text.
  - Script `genbench.mjs` is kept for a rerun.
  - The real slice set is pool-80 ≈ 3.7k chunks (~1.6 h): not worth it under a 0-key ceiling.
- Doc2Query-- filtering: not needed.

## If reopened (new mechanism, not new wording)
- "Gate counts the questions": the coverage gate also reads the chunk's generated questions (stored in a side table).
  - Needs real generation (an oracle would pass the gate trivially) and a guard for off-topic entrants.
  - Target cases are comparison passages like vit-cry-005. That overlaps `cards/comparison-entity-split-retrieval.md`, which attacks the same gate more cheaply.

## Files
`cands.mts`/`count.mts` (expansion-set sizing: pool 80 = 1.9k wv + 1.8k cr chunks; pool 300 = 13k), `ceiling.mts`, `fts.mts`, `fts_selftest.mts`, `lib.mts`, `oracle.mts`, `peek.mts`, `offtopic.mts`, `genbench.mjs`. Pack copies live in the session scratchpad (not shipped). Base retrieval inputs come from `boar-eval/runs/night-2026-10-01/and-qwen-s42.traces.jsonl` (k per item). Code: `exp/09` src copy of `wikiPack.ts`.

UNKNOWN: whether whole-pack expansion (548k + 55k chunks) shifts idf enough to change the off-topic rate on its own. It doesn't matter for keys, because of the gate.
