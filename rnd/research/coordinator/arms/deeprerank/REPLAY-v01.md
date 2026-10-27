# DEEPRERANK step 0: 0-call rerank replay on bench v0.1 (public, 60 items)

TL;DR: bge-reranker-v2-m3 over the engine's top-20 moves gold into the deep tier's top-6 on **2 items**, takes it out of 0, and empties 0. That fails the promotion gate (≥ 5 items). On v0.1 the gate can't be met at all: only 2 gold items have a gold source in the top-20 pool that is missing from the baseline top-6, and the rerank recovers both. Retrieval recall is the limit here, not ordering. Rerank wall time is p50 ≈ 3.7 s per item on a contended MacBook CPU.

## Setup
- Tree `wt/cut7`. Kit = the `boar-crypto` and `boar-wikivoyage-en` packs plus the essential seed corpus, as in the deep traces' `config.kit`.
- Engine `answer()` runs as the adapter's `--deep-model` configuration: settings `{quickFirst, alwaysComplete: true, deepModelId: qwen3.6-35b-a3b-ud-q2kxl}`. The deep model has role `reasoning`. Generation is stubbed out.
  - The gate is `rules` (no nextTokenProbs), matching the gate-less server backend.
  - The detector is lexical (see caveats).
  - The engine asked for k = 6 on 46/46 retrieving items.
- Candidate pool = `Rt.retrieve(query, 20)`. Baseline = `Rt.retrieve(query, k)`, the engine's real top-k for k = 6 and k = 4. Reranked top-k = the k highest-scoring candidates in the pool.
- Chunk text comes from `chunk.body` in the engine's RetrievedChunk objects; no SQLite lookup was needed.
- Each reranker document is `title + "\n" + body`, cut to 2000 chars. That cut never binds: the longest document is 1516 chars and p90 is 1022. The largest call is 4233 prompt tokens.
- Reranker: `shared-models/bge-reranker-v2-m3-q4km.gguf`, sha256 `e186a244ed455b4ab66ec64339ce7427a6ae13f5c0b5e544de96e50f0f8b3673` (checked by the script).
  - Endpoint: `POST /rerank {query, documents}`. It returns raw logits; the script reports the logit and its sigmoid `p`.
- Exact server command, started by the script:
  `…/0565dfd2-…/scratchpad/home/boar/llama-b11010/build-cpu/bin/llama-server -m shared-models/bge-reranker-v2-m3-q4km.gguf --rerank --host 127.0.0.1 --port 8097 -c 8192 -b 8192 -ub 8192 --parallel 1 -t 4 --no-webui`
  - Build: llama.cpp version 0.4.1-dev, commit 4bc272f, CPU-only.
  - A rerun with `-b 2048 -ub 2048` produced identical scores (max |Δ| = 0) and identical top-6 and top-4 on 46/46 items. The scores are deterministic.

## Metrics (60 items: 46 retrieve, 14 do not; gold on 39, of which 31 retrieve; 4 retrieving items return an empty pool)
| | k = 6 (deep) baseline | k = 6 reranked | k = 4 (4B) baseline | k = 4 reranked |
|---|---|---|---|---|
| recall@k, 31 retrieving gold items | 0.3226 | **0.3710** | 0.2903 | 0.3387 |
| recall@k, all 39 gold items (non-retrieving = 0, the replay-retrieval convention) | 0.2564 | 0.2949 | 0.2308 | 0.2692 |
| items whose top-k set changed (any of 46) | — | 28 (10 without gold) | — | 30 |
| gold enters top-k (key-in-context +) | — | **2**: vit-sci-002, trv-004 | — | 2: vit-trv-003, vit-sci-002 |
| gold leaves top-k (key-in-context −) | — | **0** | — | 0 |
| recall up / down | — | 2 / 0 | — | 2 / 0 |
| items whose kept top-k is emptied | — | 0 (reranking only reorders a non-empty pool) | — | 0 |
| baseline retrieve(q,k) ≠ first k of retrieve(q,20) | 2 items | — | 1 item | — |

- **Ceiling:** 12 of 39 gold items have any gold source in the top-20 pool, and 10 have one in the baseline top-6. Only 2 items (vit-sci-002, trv-004) have pool gold outside the baseline top-6, so +2 is the maximum any reordering can reach at k = 6 on v0.1. 10 of the 39 gold items have no candidates at all.
- **Score distribution** (sigmoid p): all 20-candidate scores p10 0.0001 / p50 0.022 / p90 0.795. Top-1 per item p10 0.007 / p50 0.839 / p90 0.985. Lowest score in the reranked top-6 p10 0.0003 / p50 0.051 / p90 0.666.
  - At the exp-27 τ = 0.05, about half the reranked top-6 slots would be gated. No τ was applied here (`--tau` is off by default).

## Rerank latency (20 pairs max per item, 42 non-empty pools)
- Run 1, `-ub 8192`: p50 3.67 s, p90 19.8 s, max 33.9 s.
- Rerun, `-ub 2048`: p50 3.75 s, p90 6.8 s, max 24.3 s. The baseline engine `retrieve()` takes ~0.3–0.6 s.
- Both runs shared the MacBook CPU with another agent's 4B llama-server and the :8094 detector (4 threads, CPU build, no Metal). Treat these as upper bounds, not device numbers.
- A smaller ubatch helps the tail. Use `-ub 2048` for later runs.

## Fidelity check (engine query and k)
- `replay-retrieval.sh --tree wt/cut7 --topk 20 --gate rules` matches this tool's 20-candidate pool on **60/60** items (identical ordered raw titles) and 60/60 queries.
- With `--topk 6`, it matches this tool's baseline top-6 on 60/60.
- Both used `BOAR_REPLAY_CACHE=arms/deeprerank/cache`. The cache key is cb2f82a5073cde89, the same as boar-eval's cache.
- replay-retrieval's recall@6 is 0.2564 over 39 gold items, equal to the row above.
- Extra check: the 2 v0.1 items in the deep smoke traces (`runs/kiln/deepthink/dt-smoke-T`, `deepctx/dx-smoke-X`, cut 6 trees, detector on) have the same query and raw top-6 titles: 2/2 and 2/2.
- Outputs: `fidelity/replay-retrieval-topk{20,6}.jsonl`.

## Caveats
- **Not re-simulated:** the engine's kept `sources` after compressContext, onSubject, the topic filter and the deep 400-token context cap. "In top-k" means in `raw`, not in the prompt. A judged arm also needs the kept set; with a 400-token cap, maybe 2–3 of the 6 survive.
- Detector: lexical predicate only. The deep runs used the learned detector v3b, which can change `health`, and through it the query, on health items. For the 2 smoke items, the query and top-6 matched anyway.
- Gold is title-level (scorers/retrieval.py rule). It covers 39/60 items, and 21 of those are non-retrieving or have no gold in the pool. v0.1 is dev data with small n, so it can't show +5 by construction. v0.2 (dev, 110) is the next place to look.
- The rerank query is the engine's search query: the English question, plus "what to do" on action intents. This is not the user's raw question.
- No item text was printed; the JSONL holds titles and scores only.

## Files
- `tools/rerank-replay.ts` (sha256 d2385957…) and `tools/rerank-replay.sh` (b771c80c…). The setup is copied from replay-retrieval.ts l.148-230, and the deep wiring from runner/adapter.ts l.655-662 and 740-745.
- `replay-v01.jsonl` (per item: pool with scores and rrRank, base/poolHead/rr titles per k, added/removed, recall, rrMs) and `aggregates/replay-v01.json`.
- `rerun-ub2048.jsonl` and `aggregates/rerun-ub2048.json` (determinism and latency rerun).
- `logs/`, `cache/` (25 MB app dir).

## Rerun on another questions file
```sh
cd <workspace>
A=rnd/research/coordinator/arms/deeprerank
$A/tools/rerank-replay.sh --questions <file.jsonl> --gold <sources.json> --tree wt/cut7 --k 6,4 --topk 20 \
  --port 8097 --out $A/replay-<set>.jsonl --agg $A/aggregates/replay-<set>.json [--tau 0.05] [--ids a,b]
# or reuse a server: --server-url http://127.0.0.1:8097 (start it with the command above, -b 2048 -ub 2048)
```

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file; the gate was pre-stated in HANDOFF-2026-10-11.md:60-61 — nothing to freeze (a sha now would fake a pre-registration).
