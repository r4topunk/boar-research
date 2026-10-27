# Tiny cross-encoder reranker (llama.rn `rerank()`) over the fused candidate pool
TL;DR: Rescore the ~12–20 fused candidates with a 33M cross-encoder (jina-reranker-v1-tiny-en GGUF) through llama.rn's built-in `rerank()`, keep the top 2–3 by reranker score; should put the answer-bearing passage at [1] more often, which is what the compact model's citation checks need, and cut prefill by sending fewer chunks.
Lane: Sonar · Status: tested locally (negative for the tiny model) · Priority: C (was B)
Axes moved: retrieval ↑ (BM25-only pack path is exactly the setup where small rerankers add ~+5–6 nDCG@10 on BEIR); quality ↑ small (fewer "all-citations-removed" / "uncited-with-sources" declines when the right passage is [1]; size UNKNOWN, must beat run noise 0.031); latency ± (reranker cost ~0.5–2 s on device, UNKNOWN, vs ~1.5–2.5 s prefill saved per dropped ~150-token chunk at the measured ~69 tok/s prefill); resources: +~40 MB RAM (Q8) for a second llama context; truthfulness/safety: neutral to ↑ (fewer off-topic passages reach the model; travel-guide-as-health risk unchanged unless the gate also uses the score).
Fits BOAR? Yes on paper. llama.rn 0.13.0-rc.4 (the version in boar-app `package.json`) exposes `context.rerank(query, documents, params)` natively (`node_modules/llama.rn/src/index.ts:957`, JSI `llamaRerank`), so no native work. Model is 33M params / 4 layers (vs bge-small's 12 layers), GGUF Q8_0 ~35 MB on disk. Fully offline. English-only (PT questions already get re-searched with English names in `retrieve.ts`, so the rerank query should be that English form). Works identically on iPhone 4 GB and Android.
Evidence:
- Jina, "Smaller, Faster, Cheaper: Jina Rerankers Turbo and Tiny", 2024-04-18, https://jina.ai/news/smaller-faster-cheaper-jina-rerankers-turbo-and-tiny/ (accessed 2026-10-01): BEIR nDCG@10 (17 datasets) tiny-en 48.54 (33M, 4 layers), turbo-en 49.60 (38M), ms-marco-MiniLM-L-6-v2 48.64 (23M), mxbai-rerank-xsmall 48.80 (71M), bge-reranker-base 47.89 (278M). Vendor-run; reranking setup not stated on the page (UNKNOWN: presumably BM25 top-100). For reference BM25 alone on BEIR is ~42–44 nDCG@10 (BEIR paper, Thakur et al. 2021, https://arxiv.org/abs/2104.08663). Medium strength: public numbers, but vendor-reported and on web-search-style tasks, not on Wikipedia QA with a 1.5B reader.
- GGUF conversions exist and are documented for llama.cpp: https://huggingface.co/gpustack/jina-reranker-v1-tiny-en-GGUF (Q4_K_M/Q8_0/F16, accessed 2026-10-01). llama.cpp reranking (pooling `rank`) issue/feature: https://github.com/ggml-org/llama.cpp/issues/8555.
- RE-RAG (Kim & Lee, arXiv 2406.05794, 2024-06/10): a relevance estimator's score is used as a confidence for "is this context useful" and to decide when to tell the user the question is unanswerable. Supports using the score for gating, not just ordering.
- Caveat source: cross-encoder scores are per-query logits, not probabilities; fixed cutoffs drift across checkpoints (practitioner write-up, https://dev.to/ji_ai/cross-encoder-reranker-score-calibration-why-05-cutoffs-fail-1k9b, accessed 2026-10-01, weak evidence). So any threshold must be calibrated on BOAR items and frozen with the model sha.
- BOAR-side facts (read-only, this cycle):
  - Format-2 packs (Wikipedia/Wikivoyage/crypto) rank by BM25 + popularity prior only: `DEFAULT_TUNING.semanticWeight = 0` (`boar-app/src/rag/wikiPack.ts:421`). Their keyword hits are not gated by cosine and compete in a max-normalized weighted sum (`fuseRetrievalResults`, `src/rag/pure.ts`).
  - Fusion normalizes each list to its own max, so it cannot tell "strong" from "best of a bad lot" (the code comment says so).
  - On the iPhone (D10, build 611a4b9, kit A, O2 off, `rnd/plumb/data/d10-…-o2off-o2ab82.jsonl`): 35/82 declined; 19 are `all-citations-removed-declined-compact`, 10 `uncited-with-sources-declined-compact`, only 3 pure `no-good-source`. So most declines happen **after** retrieval found something, when the model's claims are not supported by what it was given. Context after compression p50 ≈ 499 tokens; prefill-stage p50 ≈ 6.3 s; retrievalMs ≈ 1.0–1.5 s already (plumb device files, 14de107: p50 0.98 s / 1.13 s with vital5).
Test in boar-eval: arm `rerank-tiny` on the desktop-node adapter (greedy, deterministic) vs `main`:
- Patch idea: in `retrieveOne` (or right after `compressContext` input `raw` in `answer.ts`), call `rerankCtx.rerank(englishQuery, candidates.map(c => c.title + "\n" + c.body.slice(0, 1200)))` on the top 16 fused candidates (named-title and pinned identifier hits keep their slots); order the rest by reranker score; feed top 3 instead of 4 into compression. No new gate in v1 (ordering only), so the effect is attributable.
- Mode: gate on the ~20-item deterministic set first (no judge), then full on bench-60 ×2 runs (the ≥2 runs rule).
- Items that should move: the 29 D10 rows with `all-citations-removed` / `uncited-with-sources` declines; rows whose `retrievedTitles` contain the right article but not at rank 1.
- Success criterion (stated before any run): on the deterministic desktop run of bench-60, (a) declines with codes `all-citations-removed-declined-compact` + `uncited-with-sources-declined-compact` drop by ≥ 5 items, (b) confident-wrong (judge+Jev band) does not rise by more than 1 item and safety veto hits do not rise, (c) median context tokens after compression do not rise, (d) desktop retrieve+rerank time added ≤ 150 ms p50 on the M-series (device budget to be measured separately: ≤ +600 ms p50 on iPhone 13). Fail any → no device run.
Shelf (`rnd/research/SHELF.md`): candidates with verified licenses and sizes: jina-reranker-v1-tiny-en GGUF (Apache-2.0, 32–35 MB), ms-marco-MiniLM-L6-v2 GGUF (Apache-2.0 model, MS MARCO data terms flagged, 25 MB), mxbai-rerank-xsmall-v1 GGUF (Apache-2.0, 78 MB). The multilingual jina v2 is CC-BY-NC: rejected.
Cost to try: ~4–6 h (adapter patch + 35 MB GGUF download + one gate run + bench-60 ×2 desktop). Risk: low; read-only for the product until an arm wins.

## Local test, 2026-10-02 (`sonar/exp/05-topic-filter-rescue/`: `rerank.mjs`, `sanity.mjs`, `rerank.txt`, `rerank-bge.txt`)

Setup:
- Every raw source of Kiln's `ios-main-v5-t0` and `ios-main-s42` traces on items that have both answer-key-bearing and other sources: 27 items, 84 passages, 59 key/non-key pairs.
- Passage text: vital5 best-cosine chunk; Wikivoyage/crypto = first 1,500 chars of the article.
- Scored with node-llama-cpp 3.21.1 `createRankingContext().rankAll`.

| Scorer | Sanity (Paris / Banana / Berlin) | Within-item AUC key vs non-key | Right source ranked first | Desktop time (84 docs, ~20.8k tokens) |
|---|---|---|---|---|
| bge-small cosine (today's signal) | — | **0.780** | 22/27 | — |
| jina-reranker-v1-tiny-en Q8_0 (33M) | 0.532 / 0.501 / 0.509: right order, compressed scores | 0.729 | 20/27 | ~4.8 s incl. IO |
| ms-marco-MiniLM-L-6-v2 q8_0 GGUF (cstr) | **fails to load**: "bert model needs to define token type count" | — | — | — |
| bge-reranker-v2-m3 Q4_K_M (568M) | 0.999 / 0.000 / 0.009 | 0.712 | 22/27 | ~16 s incl. IO |

Reading:
- The tiny reranker does not beat the cosine the app already has on BOAR's own candidates. Its near-0.5 scores may mean the GGUF's classifier head is mishandled in this llama.cpp build (UNKNOWN; llama.rn may differ).
- bge-v2-m3 gets the hard cases right that the lexical topic filter and cosine get wrong:
  - Cheetah 0.99 vs Sailfish 0.23 (ostrich 0.89);
  - Amazon River 0.98 / Nile 0.87 vs Mackenzie River 0.16;
  - Kazuo Ishiguro 1.00 vs Abdulrazak Gurnah 0.16 (2017 Nobel).
- bge-v2-m3's AUC is low only because the key proxy marks relevant sources (Nile, Pronghorn) as non-key.
- But it is ~17× the tiny model's size. Per question (4 passages × ~300 tokens = ~1.2k tokens through 568M params) it would cost several seconds on the iPhone 13: not viable per query today.
- **Verdict:** demote to C. On-device reranking needs a model that is both sharp and tiny; none on the shelf passed. Options kept:
  - (1) distill bge-v2-m3 into a ≤ 50M head on BOAR-style pairs (cost > 1 day);
  - (2) on Android 12 GB, a yes/no relevance prompt to the resident 4B for the top 3 only (cousin of Compass 4c);
  - (3) re-test jina tiny under llama.rn on device in case the score compression is a node-llama-cpp artifact.

## Details

Why this and not a bigger reranker: bge-reranker-v2-m3 (568M) or Qwen3-Reranker-0.6B would cost about as much prefill as the answer model does per token on a phone that prefills the 1.5B at ~69 tok/s; reranking 16 × 300 tokens = ~4.8k tokens through a 0.6B model is tens of seconds. A 4-layer 33M model is ~1/45 of the 1.5B's size; even at a pessimistic 2k tok/s on the A15 CPU, 16 candidates truncated to ~256 tokens is ~2 s, and ~1 s at 128 tokens. UNKNOWN: real on-device throughput of a BERT-tiny GGUF in llama.rn; the next cycle can measure desktop throughput locally and scale.

Where the gain should come from:
1. The format-2 pack path (Wikipedia vital5, Wikivoyage, crypto) is keyword-ranked only. A cross-encoder reading query and passage jointly fixes the classic BM25 errors (term overlap without meaning: "Black Sea" for black holes; the topic page vs the section that answers).
2. The compact model cites [1] by habit. If [1] is the answer-bearing passage, the citation-support check keeps the citation and the answer stands. If [1] is merely on-topic, the model answers from memory, the check removes the citation, and the answer becomes "The passages found don't support this answer."
3. Fewer chunks with the same recall: rank 3–6 were "mostly unrelated" in the 2026-09-24 device benchmark (comment on `ANSWER_CONTEXT_CHUNKS` in `pure.ts`). Going from 4 to 3 chunks saves ~100–200 prompt tokens ≈ 1.5–3 s of prefill on the iPhone.

Follow-up (separate arm, only if ordering wins): use the reranker score as the answerability gate in place of the cosine ≥ 0.70 gate + `onSubject` topic filter. Calibrate per the anchor-passage trick (score minus median score of 3 fixed irrelevant passages) and freeze the threshold. That is also a lever for Compass's abstention work; hand off the calibration if it gets there.

What would make it fail:
- The declines are mostly the 1.5B answering from memory regardless of what is at [1] (then this moves nothing; it is an Anvil "make small models cite" problem). Check before the run: for the 29 citation-related declines, is the right article in `retrievedTitles` at all? If it's absent in most, reranking can't help and the card drops to C (it becomes a recall problem → query expansion / pack coverage cards).
- The jina tiny model was trained on MS MARCO-style web passages; Wikivoyage list-style sections and EIP specs may score oddly. The gate run shows it.
- On-device latency higher than the prefill it saves.
- Health questions: the reranker could promote a travel-guide passage that mentions the condition (the hypothermia "keep walking" Wikivoyage text is on-topic by any relevance measure). Reranking does not fix that safety failure; the health route's own source filter must stay in front.

UNKNOWN:
- Device throughput of a 4-layer BERT GGUF in llama.rn on A15/Android mid-range.
- Whether llama.rn allows two contexts (answer model + reranker) concurrently within the 4 GB iPhone budget alongside bge-small (expected yes: +~40 MB).
- Exact reranking setup behind Jina's BEIR numbers.
