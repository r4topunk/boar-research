# Retrieval: on-device recall at small k for a strong reader (no-kept-source bucket)

Researcher notes, 2026-10-12. Scope: question-shaped indexing, small embedders, learned sparse / late interaction, quantized vector stores on Android, query-side methods, recall ceilings for long-form QA. Extends `websweep-2026-10-06/offline-retrieval.md` (rows 15, 19-23) and `websweep-2026-10-06/precomputed-knowledge.md` (PAQ/RePAQ, Doc2Query--, HyDE, RAPTOR, contextual retrieval abstracts). Numbers below were read from the primary page (paper HTML/PDF, model card, vendor post) unless marked "abstract only" or "unverified".

**Framing constraint from our own data (read first).** Retrieval recall levers can only fix items whose facts are *in the kit*. LOSSMAP: no kept source on 29/51 V-para, 54/110 v0.2; WIKISECTION: missing fact absent from the enwiki pack on 12/13 V-para items checked; RETRIEVAL-SCORECARD (v0.1): B1 coverage 49 % of gold item-runs vs B2 ranking 18 %, recall@5 0.333. So the addressable share of the no-kept-source bucket is the B2-type slice (fact in kit, not retrieved), probably a minority. Everything below should be gated on a 0-call replay that counts gold entering the kept-6, not on BEIR deltas.

## TL;DR
- **Question-shaped indexing over the kit's own text (not model-written notes) is the strongest untested retrieval mechanism.** HyPE (bge-m3, generated questions per chunk mapped back to the chunk): mean claim recall 53.6 → 71.5 and context precision 42.3 → 63.5 over 6 datasets; RAG-12000 recall@5 49.0 → 80.1; zero query-time cost; no gain on MS MARCO (short, lexical passages). Raina & Gales: synthetic-question retrieval R@1 BiPaR 33.7 → 53.7 (mpnet), but SQuAD with e5-base only 76.2 → 80.2 and R@5 94.4 → 94.5: **the gain shrinks with a stronger embedder.** [HyPE](https://arxiv.org/html/2607.29402), [Raina & Gales](https://arxiv.org/html/2405.12363)
- **Doc2Query-- (filtered expansion) is a big BM25 win in-domain, small out-of-domain.** MS MARCO dev RR@10 BM25 0.185 → Doc2Query n=80 0.279 → +ELECTRA filter (keep 30 %) 0.323; index 0.71 → 0.95 GB (+34 %), latency 5 → 23 ms. But on BEIR zero-shot docT5query is only +1.6 % over BM25 on average (NQ 0.329 → 0.399, HotpotQA 0.603 → 0.580). [Doc2Query--](https://arxiv.org/abs/2301.03266), [BEIR](https://arxiv.org/html/2104.08663v4)
- **Embedder swap: the only big jump is Qwen3-Embedding-0.6B.** MTEB-v2 English retrieval 61.83 (card) vs bge-small-en-v1.5 53.9 (granite card); Apache-2.0, official GGUF. Sub-100M options give +0.3 to +3: arctic-embed-s 51.98 vs bge-small 51.68 (MTEB retrieval v1), LEAF-IR 23M 53.9 / 54.8 asymmetric (BEIR-14), arctic-embed-m 54.90. [Qwen3-Embedding](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B), [arctic-embed-s](https://huggingface.co/Snowflake/snowflake-arctic-embed-s), [LEAF](https://arxiv.org/html/2509.12539)
- **Inference-free learned sparse fits our SQLite stack with no query model.** opensearch-neural-sparse-encoding-doc-v3-distill (67M, Apache-2.0): BEIR-13 nDCG@10 0.517; v3-gte 0.546; queries = tokenizer + IDF table lookup; docs encoded at build time. BM25 on BEIR-14 = 42.5 (LEAF table). [model card](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-doc-v3-distill)
- **Query-side LLM expansion (HyDE, query2doc, multi-query) is the wrong tool for our failure mode.** It hurts strong retrievers (strong negative correlation of gain with retriever quality; 11 techniques × 24 retrievers × 12 datasets) and fails when the LLM lacks the knowledge (= our absent-knowledge bucket). Multi-query + RRF raised raw recall but Hit@10 fell 0.51 → 0.48 after rerank/truncation in a 2026 deployment study. [Weller et al.](https://arxiv.org/abs/2309.08541), [Abe et al.](https://arxiv.org/html/2505.12694v1), [Dell RAG-Fusion](https://arxiv.org/abs/2603.02153v1)
- **Late chunking is a free build-time +1.4 to +1.9 nDCG@10** (BEIR subsets, 3 embedders), but needs a long-context embedder (bge-small is 512 tokens) and is inconsistent for some embedders (BGE-M3 NFCorpus 0.225 → 0.067 in a replication). [Late chunking](https://arxiv.org/html/2409.04701v3), [Reconstructing Context](https://arxiv.org/html/2504.19754)
- **Vector store scale is not our wall up to ~1M vectors.** sqlite-vec brute force on M1: 1M × 192-d float 192 ms, 1M bit vectors ~124 ms, 100k × ≤1024-d float < 75 ms; Android compiles but no prebuilt; ANN (DiskANN, IVF) only in v0.1.10 alphas. [sqlite-vec post](https://alexgarcia.xyz/blog/2024/sqlite-vec-stable-release/index.html), [releases](https://github.com/asg017/sqlite-vec/releases)
- **Recall ceilings on long-form questions are low everywhere, not just for us**: CRAG straightforward RAG 44 % accuracy (LLM-only ≤ 34 %); in a long-form study only 45 % (Bing docs) to 85 % (WebGPT docs) of retrieved sets contained enough to answer (20 Qs); insufficient context raises Gemma's wrong answers 10.2 % → 66.1 %. [CRAG](https://arxiv.org/abs/2406.04744), [LFQA retrieval](https://arxiv.org/html/2310.12150), [Sufficient context](https://research.google/blog/deeper-insights-into-retrieval-augmented-generation-the-role-of-sufficient-context/)

## Q1. Indexing methods that make a corpus answer question-shaped queries

### Takeaway
Generated-question indexing (HyPE, PAQ-style, Doc2Query--) raises recall@small-k substantially when the base retriever is weak or the text is long and not lexically aligned with questions; gains shrink toward zero with strong embedders and short lexical passages. It is a new mechanism vs NOTES35 (which indexed model-written topic notes, not questions over existing kit text) and vs QNOTES (model-written Q→A notes from the model's own knowledge). It cannot add facts that are not in the kit.

### Table
| item | date | URL | what it is | key numbers | licence | fit | bucket | novelty | proposed action + 0-call gate + cost |
|---|---|---|---|---|---|---|---|---|---|
| HyPE (Hypothetical Prompt Embeddings) | arXiv 2026-07-31 (IEEE Access 2025) | https://arxiv.org/html/2607.29402 | LLM writes several questions per chunk at index time; each question vector points to its chunk | mean claim recall 53.6 → 71.5, context precision 42.3 → 63.5 (6 sets, k = 1/3/5/10); RAG-12000 R@5 49.0 → 80.1; Ragas-WikiQA R@5 65.0 → 85.6; MS MARCO R@5 80.6 → 77.3 (loss); noise sensitivity worse (21.0 vs 13.8); bge-m3 embedder; questions/chunk and index size not reported; Holm p ≈ 0.06-0.09 | paper (arXiv licence) | build-time only; vectors × q per chunk (e.g. 5 q × N chunks × 384-d int8); phone cost = same query embed | no-kept-source (B2 slice) | new (QNOTES/NOTES35 are different mechanisms; precomputed sweep L2 listed PAQ-style index only as an idea) | **QINDEX**: 35B (or 4B) on the mini writes 5 questions per chunk for Wikivoyage + health + crypto packs (not enwiki first), embed with bge-small, max-pool question/chunk scores. Gate (0 calls): v0.1 replay recall@5 ≥ 0.41 (from 0.333) AND kept-6 changes ≤ 12/60 raw lists (NAMEDSLOT bar), plus v0.2 kept-source count +≥ 5 items. Cost: chunk count × ~150 output tokens on the mini (UNKNOWN chunk count) |
| Raina & Gales, question-based retrieval with atomic units | 2024-05 (v2 2024-08) | https://arxiv.org/html/2405.12363 | split chunks into atoms, generate questions per atom, retrieve by question | SQuAD mpnet R@1 65.5 → 76.3, R@5 89.3 → 92.6; e5-base R@1 76.2 → 80.2, R@5 94.4 → 94.5; BiPaR mpnet R@1 33.7 → 53.7, R@5 54.7 → 72.9; e5 R@5 63.7 → 74.5; up to 15 q/atom, plateau; pruning redundant questions halves storage | paper | same as HyPE | B2 slice | new | evidence that gains shrink with stronger embedders: run the QINDEX gate with bge-small (weak) before considering a bigger embedder |
| Doc2Query-- | ECIR 2023 | https://arxiv.org/abs/2301.03266 (PDF read) | docT5query expansions + relevance filter (keep top 30 %) appended to doc text for BM25 | MS MARCO dev RR@10: BM25 0.185, D2Q n=80 0.279, + ELECTRA filter 0.323 (+16 % over D2Q); DL'19 nDCG 0.499 → 0.670; index 0.71 → 1.41 → 0.95 GB; query 5 → 30 → 23 ms; filtering adds up to 78 % GPU time | code released | FTS5-compatible (append text to the indexed column) | B2 slice, lexical side | known (precomputed sweep row 25, abstract only); numbers new | fold into QINDEX as the lexical half: append filtered questions to the FTS5 text column. Same gate |
| BEIR: docT5query out-of-domain | NeurIPS D&B 2021 | https://arxiv.org/html/2104.08663v4 | zero-shot benchmark | docT5query vs BM25 avg +1.6 %; NQ 0.329 → 0.399; HotpotQA 0.603 → 0.580; FiQA 0.236 → 0.291; index DBPedia 1M docs: BM25/docT5query 0.4 GB, dense 3 GB, ColBERT 20 GB | CC BY-SA (paper) | — | — | new (number) | caution: a T5 trained on MS MARCO generalises weakly; use an LLM generator instead (HyPE/InPars style) |
| Promptagator | 2022-09 | https://arxiv.org/abs/2209.11755 (abstract) | ≤ 8 examples → LLM synthetic queries → train task-specific retriever | > +1.2 nDCG over ColBERTv2 on 11 sets; +5.0 nDCG for rerankers trained on same data | paper | needs desktop training; FLAN 137B generator originally | B2 slice | new | see GPL row (cheaper variant) |
| GPL (Generative Pseudo Labeling) | 2021-12 (NAACL 2022) | https://arxiv.org/abs/2112.07577 (abstract) | domain-adapt a dense retriever with generated queries + cross-encoder pseudo-labels | up to +9.3 nDCG@10 over zero-shot SOTA dense on 6 domain sets; +1.4 avg over TSDAE combo | Apache-2.0 code (UNKNOWN, not checked) | desktop fine-tune of bge-small (33M), re-embed kit; phone cost 0 | B2 slice | new | **GPLKIT**: reuse QINDEX questions to fine-tune bge-small on our packs; same replay gate. Cost: < 1 GPU-day class (UNKNOWN on M-series) |
| Anthropic contextual retrieval | 2024-09 | https://www.anthropic.com/news/contextual-retrieval | LLM-written chunk context prefix before embedding + BM25 | top-20 failure 5.7 % → 3.7 % (emb), 2.9 % (+BM25), 1.9 % (+rerank) | vendor | build-time | B2 slice | known (offline-retrieval row 23) | cheap variant first: title + section path prefix (0 LLM calls). UNKNOWN whether our chunks already carry title prefixes |
| Reconstructing Context (late chunking vs contextual) | 2025-04 | https://arxiv.org/html/2504.19754 | replication on NFCorpus subset | contextual (rank fusion + rerank) nDCG@10 0.308 vs late chunking 0.294; contextual with Phi-3.5-mini needed ~20 GB VRAM, run on 20 % only; "smaller models performed worse" | paper | — | — | new | weakens contextual retrieval with a small local generator; use the 35B or title-path prefix |
| Late chunking | 2024-09 (v3 2025-07) | https://arxiv.org/html/2409.04701v3 | embed whole doc, pool token vectors per chunk | BEIR subsets avg naive → late: fixed 52.2 → 54.0, sentence 52.4 → 54.3, semantic 52.4 → 53.8; gains biggest at small chunks | paper | needs long-context embedder (granite-small-r2 8k, nomic 8k, Qwen3-Emb 32k); query side unchanged | B2 slice | new | only if we switch embedder; not with bge-small (512 ctx) |
| Chroma chunking report | 2024-07-03 | https://www.trychroma.com/research/evaluating-chunking | token-level recall by chunker | recall@5 (te-3-large): recursive 200/0 88.1, 400/0 89.5, 800/400 85.4, LLM chunker 91.9; MiniLM: 250/125 TokenText 82.4, 200/0 75.7 | vendor report | — | — | new | context only: chunk-size choice moves recall ≤ ~9 %; check our chunk size (UNKNOWN) |
| Is semantic chunking worth it | 2024-10 | https://arxiv.org/abs/2410.13070 (abstract) | semantic vs fixed-size chunking | "costs not justified by consistent performance gains" | paper | — | — | new | closes semantic chunking (relevance 0) |
| Dense X propositions | 2023-12 | https://arxiv.org/html/2312.06648 | proposition units | R@5 +2.6 (DPR) to +12.0 (SimCSE); index 6.2× passages | — | — | — | known (offline-retrieval row 15) | do not redo; same "weaker retriever gains more" pattern |
| LongRAG | 2024-06 | https://arxiv.org/abs/2406.15319 (abstract) | 4K-token retrieval units, long reader | NQ EM 62.7, HotpotQA 64.3, < 8 units | — | conflicts with our context cap (DEEPCTX closed) | — | new | relevance 0 |

### Inferences
- Every question-shaped indexing paper shows the same shape: large gains with weak retrievers / long narrative chunks (BiPaR, Single-Topic, RAG-12000), near zero with strong embedders on short lexical passages (SQuAD+e5, MS MARCO). bge-small is a mid-strength embedder, and our travel/health/crypto chunks are narrative, so a positive gate is plausible but not assured.
- The mechanism differs from NOTES35 in the one place that failed there: NOTES35 notes were *new text* that had to win kept slots; QINDEX keeps the original chunk as the returned unit and only adds question vectors as keys. Crowding (DEEPWIKI/VITALPACK failure) should not apply because no new chunks enter.
- If the gate passes, expected effect on V-para is bounded by the B2-type share; I estimate +0.00 to +0.02 floor-adjusted (inference, no source).

### Gaps
- HyPE questions per chunk and index size are not reported; RAPTOR/contextual retrieval have no small-reader long-form evaluation.
- No paper measures question-shaped indexing with a 4B/35B reader scored on long-form answers.

## Q2. Better small embedders than bge-small-en-v1.5 (llama.cpp GGUF / ONNX on ARM)

### Takeaway
Within ≤ 50M parameters the field moved +0.3 to +3 BEIR points since bge-small; only the 0.6B decoder embedders (Qwen3-Embedding-0.6B) give a large jump (+~8 MTEB-v2 retrieval). LEAF-IR's asymmetric mode (tiny query encoder, big doc encoder at build time) is the cheapest phone-side upgrade.

### Table
| item | date | URL | what it is | key numbers | licence | fit | bucket | novelty | proposed action + gate + cost |
|---|---|---|---|---|---|---|---|---|---|
| bge-small-en-v1.5 (baseline) | 2023 | https://huggingface.co/Snowflake/snowflake-arctic-embed-s | our embedder | MTEB retrieval (v1, BEIR-15) 51.68; MTEB-v2 retrieval 53.9 (granite card) | MIT | in use | — | — | — |
| Qwen3-Embedding-0.6B | 2025-06 | https://huggingface.co/Qwen/Qwen3-Embedding-0.6B | decoder embedder, MRL 32-1024, 32k ctx, instruction-aware | MTEB-v2 Eng retrieval 61.83, mean 70.70 (vs multilingual-e5-large-instruct 53.47) | Apache-2.0 | official GGUF (639 MB Q8_0, SHELF); per-query cost on phone UNKNOWN (≈ 0.6B forward over ~20 tokens); re-embed whole kit at build | B2 slice | known (SHELF "checked", offline-retrieval row 20 secondary); number now verified | **EMBSWAP**: replay gate with Qwen3-Emb-0.6B at MRL 256-d int8 on v0.1/v0.2 (0 judge calls); bar: recall@5 ≥ 0.41 and kept-source +≥ 5 on v0.2. Cost: re-embed packs on the mini (hours) |
| LEAF-IR (mdbr-leaf-ir) | 2025-09 | https://arxiv.org/html/2509.12539 ; https://huggingface.co/MongoDB/mdbr-leaf-ir | 23M distilled from arctic-embed-m-v1.5; asymmetric: docs with teacher, queries with leaf | BEIR-14 avg 53.9 (standard), 54.8 (asymmetric), teacher 56.1, arctic-xs 50.9, BM25 42.5, SPLADE++ 49.3, ColBERTv2 48.4; card: bge-small 51.65; CPU query ×7.3 faster than teacher | Apache-2.0 | BERT-family, GGUF conversion likely (UNKNOWN); 768-d docs | B2 slice | new | cheaper alternative to EMBSWAP: phone runs 23M query encoder; same gate |
| snowflake-arctic-embed-s / m | 2024-04 | https://huggingface.co/Snowflake/snowflake-arctic-embed-s | BERT embedders | MTEB retrieval xs 50.15, s 51.98, m 54.90 (110M, 768-d), l 55.98; nomic v1.5 53.25 | Apache-2.0 | GGUF via BERT arch | — | new | s: no gain (0); m: +3.2 at 3× size |
| granite-embedding-small-english-r2 | 2025-08-15 | https://huggingface.co/ibm-granite/granite-embedding-small-english-r2 | 47M ModernBERT, 8k ctx | BEIR-15 50.9; MTEB-v2 retrieval 53.9 = bge-small 53.9 | Apache-2.0 | llama.cpp ModernBERT support partial ("without head.norm", b7515 note); ONNX exists | — | new | no retrieval gain; only useful as a long-context embedder for late chunking |
| EmbeddingGemma-300m | 2025-09 | https://huggingface.co/google/embeddinggemma-300m | 308M, MRL 768-128, 2k ctx | MTEB Eng v2 mean 69.67 (768d) / 66.66 (128d); Q4_0 69.31; retrieval-only not on card | Gemma terms | GGUF exists | — | known (SHELF "seen") | licence review; superseded by v2 |
| EmbeddingGemma 2 | 2026-10-06 | https://blog.google/innovation-and-ai/technology/developers-tools/embeddinggemma-2/ | Gemma-4-based, text-only 270M, MRL 768-128, 8k ctx, multimodal options | ~191 MB RAM text-only quantized on a Pixel; no MTEB text retrieval number published in the post; GGUF `ggml-org/embeddinggemma-2-GGUF` linked | Apache-2.0 (per post) | llama.cpp GGUF (llama.rn support of the Gemma-4 embedder arch UNKNOWN) | B2 slice | new | watch: run in EMBSWAP replay only once a text retrieval score is published |
| jina-embeddings-v5-text small/nano | 2026 | https://jina.ai/models/jina-embeddings-v5-text-small/ | 677M / 239M, GGUF | Eng MTEB avg 71.7 (small, vendor) | CC-BY-NC-4.0 on GGUF card (per search result) | licence blocks | — | new | relevance 0 (licence) |
| potion-retrieval-32M (static) | 2025 | https://huggingface.co/minishlab/potion-retrieval-32M | model2vec static embeddings | retrieval 35.06 vs MiniLM 42.92 | MIT | trivial on phone | — | known (offline-retrieval row 20) | relevance 0 for recall |
| Granite Embedding Multilingual R2 97M | 2026-05 | https://arxiv.org/html/2605.13521v1 | multilingual small | MTEB-v2 multilingual retrieval 60.3 (vendor, per search summary, unverified) | Apache-2.0 (UNKNOWN, not checked) | — | — | new | English-only bounty: relevance 1 |

### Inferences
- An embedder swap mostly helps the ranking slice; given the scorecard (B2 18 % on v0.1, rerank gate moved gold into top-6 on only 2 items), the realistic gain is small. Qwen3-Emb-0.6B is the only candidate whose published delta is large enough to be worth a replay.
- Our measured AUC on BOAR candidates (sonar exp-05: bge-small cosine 0.78) is the right local metric to compare embedders without judge calls.

### Gaps
- No phone latency for Qwen3-Emb-0.6B or LEAF-IR query encoding found. No MTEB text retrieval figure for EmbeddingGemma 2 yet.

## Q3. Learned sparse and late interaction on device

### Takeaway
Inference-free ("doc-only") learned sparse is the best structural fit: no model at query time, inverted index fits SQLite, BEIR quality ≈ bge-small to arctic-m. ColBERT-style late interaction has the best small-model quality but no llama.cpp path and large indexes.

### Table
| item | date | URL | what it is | key numbers | licence | fit | bucket | novelty | proposed action |
|---|---|---|---|---|---|---|---|---|---|
| opensearch-neural-sparse-encoding-doc-v3-distill | card updated 2025-06; paper SIGIR 2025 (2504.14839) | https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-doc-v3-distill | doc-side SPLADE-like expansion; query = tokenizer + IDF weights | BEIR-13 nDCG@10 0.517; doc-v3-gte (133-137M) 0.546; doc-v2-distill 0.504; splade-v3-doc 0.470 (sbert table); avg FLOPS 1.8 | Apache-2.0 | build-time doc encoding (67M); store (term, chunk, weight) in SQLite and score by dot product; no GGUF needed on phone | B2 slice (vocabulary mismatch) | new | **SPARSEDOC**: encode packs on the mini, add as a third retriever in the hybrid; replay gate as QINDEX. Cost: index size UNKNOWN (expansion adds terms; measure on one pack) |
| answerai-colbert-small-v1 | 2024-08 | https://huggingface.co/AnswerDotAI/answerai-colbert-small-v1 | 33M late interaction, 96-d per token | BEIR avg 53.79 vs bge-small 51.68; usable as reranker | Apache-2.0 | no llama.cpp late-interaction path; ONNX + custom MaxSim; index = tokens × 96-d | — | known (offline-retrieval row 20, snippet) | relevance 1: as a reranker it falls in the closed DEEPRERANK family (gold not in candidates) |
| mxbai-edge-colbert-v0 17M / 32M | 2025-10 | https://huggingface.co/mixedbread-ai/mxbai-edge-colbert-v0-17m | edge late interaction, 48-d tokens | BEIR avg 17M 0.490, 32M 0.521, answerai-small 0.534, ColBERTv2 0.488 | Apache-2.0 | ONNX; PLAID index recommended | — | new | relevance 1 |
| BEIR index sizes | 2021 | https://arxiv.org/html/2104.08663v4 | per-method index for DBPedia 1M docs | BM25 0.4 GB, dense 3 GB, ColBERT 20 GB | — | late interaction = 50× BM25 | — | new | closes full-corpus ColBERT on phone (relevance 0) |

### Gaps
- Index size of doc-v3-distill expansions on our chunk lengths not found; no Android benchmark for learned sparse in SQLite.

## Q4. Binary/int8 embeddings and vector stores on Android

### Takeaway
Up to ~1M vectors brute force is fine (≤ 0.2 s on M1 with 192-d float or bit vectors); int8 keeps ~99 % and binary + rescore ~96 % of quality (known). Store choice is a speed lever, not a recall lever, and only matters if we index millions of chunks or many question vectors (QINDEX multiplies vector count by q).

### Table
| item | date | URL | key numbers | licence | fit | bucket | novelty | action |
|---|---|---|---|---|---|---|---|---|
| sqlite-vec v0.1 stable | 2024-08-01 | https://alexgarcia.xyz/blog/2024/sqlite-vec-stable-release/index.html | M1: sift1m 1M×128 static 17 ms / vec0 33-35 ms; 1M×192 float 192 ms; 1M×3072 float 8.52 s; 1M bit ~124 ms; 100k ≤1024-d < 75 ms; "compiles on Android", no prebuilt | Apache-2.0 | via op-sqlite (SHELF) | speed | known (SHELF "seen"); numbers new | if JS brute force > 1 s on device (UNKNOWN), move to sqlite-vec int8/bit + rescore |
| sqlite-vec v0.1.10 alphas (DiskANN, rescore, IVF experimental) | 2026 (Mar-May, year inferred) | https://github.com/asg017/sqlite-vec/releases | ANN alphas; expensive DELETEs | Apache-2.0 | alpha | speed | new | wait; brute force suffices ≤ 1M |
| HF embedding quantization | 2024-03 | https://huggingface.co/blog/embedding-quantization | int8 ~99 %, binary + rescore ~96.45 % retention | — | — | speed/size | known (offline-retrieval row 19) | — |
| USearch / expo-vector-search | 2025-26 | https://pypi.org/project/usearch/ | HNSW with i8/f16; Android listed as supported; RN wrapper claims sub-ms (no benchmark); mobile SoC paper reports HNSW memory exhaustion at high recall (snippet, unverified) | Apache-2.0 (usearch; not re-checked) | JSI wrapper maintenance uncertain | speed | new | relevance 1 |

## Q5. Query-side methods usable with a 4B

### Takeaway
Do not spend on query-side LLM rewriting. Evidence: gains anti-correlate with retriever strength, and expansion fails exactly when the LLM lacks the topic knowledge (our absent-knowledge bucket). Fusion of multiple rewritten queries raises raw recall but the gain vanishes after rerank/truncation to small k. Also overlaps closed families (FOLLOWQ, DEEPITER, MP4B).

### Table
| item | date | URL | key numbers | fit | novelty | action |
|---|---|---|---|---|---|---|
| When do generative query/doc expansions fail? (Weller et al.) | EACL 2024 | https://arxiv.org/abs/2309.08541 (abstract) | 11 techniques, 12 datasets, 24 retrievers: "strong negative correlation between retriever performance and gains from expansion" | closes query expansion with a mid/strong retriever | new | relevance 0 (closes) |
| LLM-based QE fails for unfamiliar and ambiguous queries | SIGIR 2025 | https://arxiv.org/html/2505.12694v1 | QE degrades retrieval when the LLM's knowledge is insufficient; popularity bias toward common interpretations (search summary; tables not read) | our failure items are by definition outside model knowledge | new | relevance 0 (closes) |
| Query2doc | EMNLP 2023 | https://arxiv.org/abs/2303.07678 (abstract) | BM25 +3 % to +15 % on MS MARCO / TREC DL | needs large LLM pseudo-doc; 4B pseudo-docs hallucinate on tail | new | relevance 0 |
| HyDE | 2022-12 | https://arxiv.org/abs/2212.10496 (abstract) | beats Contriever, ≈ fine-tuned retrievers (InstructGPT) | weak-retriever result | known (precomputed sweep row 26) | relevance 0 |
| HyDE on BEIR with a modern dense retriever | 2026 (2608.25521) | https://arxiv.org/pdf/2608.25521 | TREC-COVID .7436 → .7692, FiQA .4492 → .4641, Touché .2539 → .2525 (search summary, unverified) | small, mixed | new | relevance 0-1 |
| RAG-Fusion in production (Dell) | 2026-03 | https://arxiv.org/abs/2603.02153v1 | fusion raises raw recall; after rerank/truncation Hit@10 0.51 → 0.48 in several configs; extra latency | matches our kept-6 regime | new | relevance 0 (closes multi-query + RRF) |
| RAGElo RAG-Fusion eval | 2024-06 | https://arxiv.org/pdf/2406.14783 | MRR@5 BM25 0.855 vs 0.821; KNN 0.396 vs 0.407 (search summary) | mixed | new | relevance 0 |
| Step-back prompting | ICLR 2024 | https://arxiv.org/abs/2310.06117 (abstract) | PaLM-2L: TimeQA +27 %, MuSiQue +7 %, MMLU physics +7 %, chemistry +11 % | large-model result; extra generation pass on a 5 tok/s device | new | relevance 0 |

## Q6. Recall ceilings: Wikipedia-only vs mixed corpora for long-form questions

### Takeaway
No paper runs the exact Wikipedia-only vs mixed-corpus ablation on long-form questions. Indirect evidence: even web retrieval leaves many long-form questions without sufficient evidence, and straightforward RAG plateaus around 44 % on CRAG. Insufficient context raises confident wrong answers sharply, which matches our "wrong fact" bucket. Combined with CompactDS (Wikipedia +0.7 vs diverse +6.8, known), the ceiling for our no-kept-source items is set by coverage, not by the retriever.

### Table
| item | date | URL | key numbers | novelty | relevance |
|---|---|---|---|---|---|
| Understanding retrieval augmentation for LFQA | 2023-10 (v2 2025-10) | https://arxiv.org/html/2310.12150 | sufficient docs: WebGPT 85 %, human 50 %, Bing 45 % (20 Qs); unsupported sentences: GPT-3.5 + WebGPT docs 11 %, no docs 70 %; random docs ≈ no docs | new | 1 |
| CRAG | NeurIPS 2024 D&B | https://arxiv.org/abs/2406.04744 | 4,409 QA; LLM-only ≤ 34 %; straightforward RAG 44 %; industry RAG 63 % hallucination-free; worse on dynamic, tail, complex | new | 1 |
| Sufficient context (ICLR 2025) | blog 2025-05-14 | https://research.google/blog/deeper-insights-into-retrieval-augmented-generation-the-role-of-sufficient-context/ (paper https://arxiv.org/abs/2411.06037) | Gemma incorrect 10.2 % (no context) → 66.1 % (insufficient context); selective generation with sufficiency label up to +10 % accuracy on answered | new | 1 (links no-kept-source to wrong-fact; a sufficiency gate is an abstention lever, out of this angle) |
| Hurdles to progress in LFQA (ELI5) | NAACL 2021 | https://arxiv.org/abs/2103.06332 (abstract) | answers not grounded in retrieved docs; ≥ 81 % of ELI5 validation questions paraphrased in train | new | 1 |
| RAG-QA Arena / LFRQA | 2024-07 | https://arxiv.org/abs/2407.13998 (abstract) | 26K queries, 7 domains; best LLM answers preferred over LFRQA only 41.3 % | known (WEB-SWEEP-2026-10-07) | 1 |
| CompactDS | 2025-07 | https://arxiv.org/html/2507.01297v1 | Wikipedia-only +0.7 vs diverse +6.8 (8B, reasoning) | known (offline-retrieval row 3) | 1 |

### Gaps
- No primary source gives answer-recall ceilings of a Wikipedia-only corpus on ASQA/ELI5/LFRQA; searches returned dataset descriptions only.

## Searched, found nothing
- "answer recall upper bound … Wikipedia corpus coverage ASQA ELI5 answerable percent": dataset descriptions only, no ceiling numbers.
- "Wikipedia-only versus web corpus RAG long-form answers coverage study": no controlled ablation; only the LFQA 20-question sufficiency check.
- "USearch Android benchmark HNSW int8 mobile React Native": no phone latency/memory numbers for USearch.
- HyDE / query expansion across Qwen model sizes on BEIR: no size-controlled study found.
- Official MTEB text-retrieval number for EmbeddingGemma 2: not published in the launch post.
- Mix-of-Granularity, LongRAG, late-chunking abstracts: no numbers on abstract pages (late chunking numbers then read from HTML).
- A granite-embedding r3 or other 2026 sub-100M English embedder with a clear BEIR jump over LEAF-IR: none found.

## UNKNOWN
- Our pack chunk count, chunk size, and whether chunks carry title/section prefixes (decides cost of QINDEX/SPARSEDOC and whether "contextual headers" are already done).
- On-device query latency of the current JS brute-force cosine, and of Qwen3-Emb-0.6B / LEAF-IR query encoding on an 8-12 GB phone.
- Share of the 29/51 V-para no-kept-source items where the needed fact exists anywhere in the kit (WIKISECTION covered only enwiki, 13 items). This share bounds every lever in this note; a 0-call jev scan of non-wiki packs would measure it.
- Whether llama.rn can load LEAF-IR, granite-r2 (ModernBERT head.norm) and EmbeddingGemma 2 GGUFs.
- HyPE questions-per-chunk and index growth; doc-v3-distill index size on our text.
