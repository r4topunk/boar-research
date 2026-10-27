# Retrieval-side model usage audit (2026-10-20 20:51)

TL;DR: the embedding model itself is used correctly: CLS pooling, correct [CLS]/[SEP] tokens, q8_0 matches the fp32 reference (cosine >= 0.9998), packs and queries use the same text rule and model on the desktop and the phone, and the missing BGE query instruction changes nothing measurable on our data. The problems are in how the engine uses the scores. (1) The dense-append floor (0.55) never filters anything in the two-stage path. (2) The X1 head-pass appends chunks that the model scores at random level. (3) The X2b budget drops higher-cosine chunks to keep lower-cosine ones. (4) The phone bench engine has none of the X1/X2b append path that today's desktop arms ran. Detector :8094 is configured the way it was trained. There is no reranker in the engine (X3 closed at its gate).

Scope: kiln-local/be-0cfd4a77-cut7-litepacks (src/rag, src/routing/emergencyHead.ts, be/app-shims), boar-app/scripts (pack builders), arms/densechunk-st sidecar builder, bench-app/engine and llama.rn 0.13.0-rc.4, shared-data/packs (v3proto, wave3, kit), litepacks traces K1. 0 LLM generations, 0 judge calls, 0 paid. Embeddings only: 220 self-test questions + 100 K1 MAIN questions (raw and instructed), 40 texts for the fp32 reference. Scripts and outputs: `retrieval-tools/` (they read /tmp/rmaudit paths; inputs are rebuilt by the first lines of each script).

## Checked OK (with evidence)

| Check | Evidence | Verdict |
|---|---|---|
| Pooling | GGUF `bert.pooling_type = 2` (CLS) in bge-small-en-v1.5-q8_0.gguf (sha ec38e8da…). HF 1_Pooling/config.json: `pooling_mode_cls_token: true`. Numpy fp32 reference: CLS vs GGUF cosine median 0.99986, mean-pool vs GGUF 0.9386 | OK, CLS |
| Special tokens, desktop | node-llama-cpp 3.21.1 `_prepareInput` adds bos 101 + sep 102 for WPM: "What is the capital of Kyrgyzstan?" → [101 … 102] | OK |
| Special tokens, phone | llama.rn vendored llama-vocab.cpp: WPM `add_bos = true; add_sep = true` (GGUF has no add_* keys), and rn-completion loadPrompt tokenizes with `add_bos` → [CLS] … [SEP] | OK, same as desktop |
| Tokenizer | HF BertTokenizer (re-implemented, uncased, accent strip) vs llama.cpp ids: 40/40 identical (20 questions + 20 corpus passages) | OK |
| Quantization q8_0 | fp32 safetensors (sha 3c9f3166…, HF rev 5c38ec7c) vs q8_0 GGUF: cosine min 0.99981, median 0.99986 over 40 texts | OK, negligible |
| int8 pack vectors | quantizeInt8 per-vector max-abs/127; cosineSimilarityInt8 is scale-invariant so ignoring `scale` is correct | OK |
| L2 normalization | All comparisons are cosine (pure.ts cosineSimilarity / Int8, wikiPack denseChunks divides by both norms). llama.rn normalizes (embd_normalize 2), node-llama-cpp doesn't; cosine makes this irrelevant | OK |
| BGE query instruction | Not used anywhere (queries raw, passages `title\nbody` or `title\nsection: text`). Measured on 220 public self-tests, 11 packs, raw vs "Represent this sentence for searching relevant passages: ": gold article lead@1 131 vs 132, lead in top-50 205 vs 207, gold chunk in dense top-12 148 vs 146, in top-2 92 vs 96 (dense only on the 9 packs with chunk_vecs). Within noise; v1.5 model card says the instruction is optional | OK; not a lever |
| Query/passage symmetry desktop vs build | Builders (boar-app/scripts/lib/embedding.mjs, sidecar_embed.mjs) and engine use the same GGUF sha, contextSize 512, same text rule, no prefix; packs checked meta `embeddingModelSha256 = ec38e8da…` (simplewiki, factbook, medlineplus, firstaid, top100k, wikivoyage, crypto) | OK |
| Passage truncation | Builders cut the embedded text at 1,200 chars (embedFitting). Chunks over 1,200 chars incl. title: simplewiki 0.9 %, factbook 2.1 %, medlineplus 1.1 %, firstaid 2.8 %, travel-se 0.4 %, health-se 1.1 %; mean share of chunk text not embedded 0.05–0.27 %. 1,200 chars ≈ 250–300 tokens, under 512 | OK, negligible |
| Bundled corpus | corpus-full/standard max 793 chars, corpus.json 1 doc > 1,200: no truncation on the phone or the desktop | OK |
| Desktop embed backend | eval shim uses gpu auto (Metal) for queries; builders CPU or Metal (builder note: cosine >= 0.9998 Metal vs CPU) | OK |
| Detector :8094 | llama-server b11010 `--embeddings --pooling mean -np 1 -c 512 -b 512 -ub 512`, model sonar-mmbert-small-emergency-v3b-q8te4.gguf sha a86fe8b9 = SHA256SUMS; adapter sends `embd_normalize: -1` (raw mean pool), head kind mmbert-cls, threshold 0.2 (frozen 10-03), 126 content tokens + bos/eos = training 128. Phone (emergencyDetector.ts:90) `pooling_type: "mean"`, embd_normalize -1, plus a canary. The mmbert GGUF has no pooling_type key, so the flag carries it; it is set on both sides | OK (desktop has no canary; one wrong restart flag would go unnoticed) |
| e5 detector option | GGUF pooling_type 1 (mean), "query: " prefix on both inputs, embd_normalize 2: matches e5 usage | OK (not used today) |
| Reranker | None in the engine (grep rerank: 0 hits in src/). X3 (bge-reranker-v2-m3 Q4_K_M via llama-server --rerank) closed at its step-0 gate; it ranked well (fact top-2 108/155), so no sign of a broken head | OK / closed |

## Findings

### F1 (medium-high): the 0.55 dense floor doesn't gate; two-stage max-of-many always passes it
- Where: src/rag/wikiPack.ts:118 `DENSE2_FLOOR = MIN_SEMANTIC_SIMILARITY` (0.55), used in denseChunks (:966-1019). Calibration comment at src/rag/pure.ts:40-51 (question vs ONE random article lead: median 0.380, p99 0.530).
- The path takes the top-50 articles by lead cosine, then all of their chunks, then the top-12 chunks. That is a maximum over hundreds of chunks, so its null distribution sits far above that of a single random lead.
- Measured (raw queries, top-2 dense chunks = what X2b appends, D = 2):
  - simplewiki: off-pack SE questions (cooking, money, travel, bitcoin, ethereum, outdoors) 100 % ≥ 0.55; only 28–53 % ≥ 0.70.
  - firstaid: off-pack money / bitcoin / ethereum questions 100 % ≥ 0.55, **0 % ≥ 0.70** (median 0.60–0.62).
  - Random-chunk baseline for the same questions: median 0.38–0.47, p99 0.50–0.65.
  - On-pack questions: 90–93 % ≥ 0.70.
- In other words, 0.55 is a single-pair "random" threshold applied to a best-of-many score. Every question gets 2 appended chunks whenever a sidecar pack is installed, relevant or not. The engine's own answer-time gate for every other source is 0.70 (pure.ts:256 ANSWER_MIN_SIMILARITY).
- K1 MAIN traces (litepacks): 101 dense chunks appended on 100 items; 57 of them (56 %) score < 0.70 to the question.
- Cheapest test: replay retrieval (0 LLM calls) with DENSE2_FLOOR 0.70, or a margin over the item's own top-1, on the K1 MAIN and the 180. Count appended chunks and fact-chunk reach vs X2b. Then run a Haiku screen only if many low-cosine appends disappear while fact reach holds.

### F2 (medium): X1 head-pass appends neighbours of a BM25-only first passage, with no embedding check
- Where: src/routing/answer.ts:1114-1130 (`packHeadPass "a2"`). It appends chunks 1-2 of the first raw user-pack passage's article. That passage comes from WikiPack BM25 with `semanticWeight: 0` (wikiPack.ts:438), so lead cosine never re-ranks it, and appended chunks skip gateByRelevance.
- Measured on K1 MAIN traces (cm + v01, 100 items, simplewiki chunk_vecs as the scorer): 62 X1 chunks appended, median cosine 0.617. 18 (29 %) are below 0.55, which is random level by pure.ts's own calibration, and 51 (82 %) are below 0.70.
- Examples:
  - "I always settle my credit card statement…" → raw[0] "Captain Jack Harkness", 2 neighbour chunks appended.
  - "List the cash I should have ready beyond a 20 % down payment" → "Cash register" ×3.
  - "What stops American credit unions…" → "American Express" ×3.
- This matters because CE-TAXONOMY (QUEUE 19:47) found 20 of 27 K0 confident errors had no relevant source. Context that looks relevant and isn't is the input those errors are made from.
- Cheapest test: the same replay, with X1 adds kept only when the chunk cosine ≥ 0.70 (or the article lead cosine ≥ SEMANTIC_KEEP 0.70), on K1 MAIN. Count removed adds and check whether gold/fact chunks are among them.

### F3 (medium): the X2b budget order keeps the weaker chunks and drops the stronger
- Where: answer.ts:1153-1163. `applyAppendBudget([...pendX1, ...pendDense], …)`: X1 neighbours first, then dense in cosine order. The first chunk over the budget is dropped and the loop stops.
- Measured on K1 MAIN: kept X1 chunks median cosine 0.617; budget-dropped chunks (23, all dense) median 0.706. 13 of the 23 dropped are ≥ 0.70, while 51 kept X1 chunks are < 0.70.
- X3-GATE.md had already seen the same mechanism: "X1's neighbours eat the budget in x3b (26 fact chunks dropped)".
- Cheapest test: replay with the budget filled in cosine order across X1 ∪ dense (0 LLM calls). Count fact-chunk presence on the 180 and on K1 MAIN.

### F4 (medium, transfer validity): the append path that today's desktop arms ran is absent from the phone bench engine and from boar-app
- The desktop lite-line config is `packHeadPass a2 + packDense2 append-budget` (LITEPACKS criterion; all of today's screens on K1).
- bench-app/engine (ENGINE.json arm `cut7-cmp30off-batchret`):
  - has no src/rag/denseCandidates.ts
  - its wikiPack.ts has no DENSE2/denseChunks
  - grep for `packHeadPass|packDense2` in bench-app/engine/src and boar-app/src returns 0 hits
- Paired desktop deltas are still valid for the desktop stack. But "K1 vs K0" and the screens' controls include up to 4 appended chunks per answer that the phone never sees. In K1 MAIN, 163 chunks were appended on 100 items (62 X1 + 101 dense). The size of their prompt-token share was not measured here.
- Cheapest test: add the arm's settings to the trace `config.settings` diff against ENGINE.json in run scripts (already recorded), and state in each verdict that the stack is "desktop X1+X2b". Or rerun one control without the appends (retrieval replay, 0 LLM calls) to size how many contexts differ.

### F5 (low): the desktop detector has no canary
- The phone runs a canary item before first use (emergencyDetector.ts:94-106). The desktop adapter (be/adapter.ts:690-716) trusts whatever server listens on BOAR_DETECTOR_URL. If :8094 were restarted without `--pooling mean`, it would silently score garbage. Today it is correct (process args checked 20:4x).
- Cheapest test: one /embedding call on the canary text at adapter start, comparing p with the head's canary value. A few lines; it belongs to whoever owns the adapter.

## Not findings (looked at, ruled out)
- **BGE instruction prefix:** measured, no effect (see table). Don't spend an arm on it.
- **512 context / truncation:** queries are short; passages are cut at 1,200 chars before the model would truncate; under 3 % of chunks are affected.
- **Desktop vs phone embedding numerics:** same GGUF, same special tokens, cosine-invariant normalization.
- **semanticWeight 0** was a tuned choice (2026-09-26 dev questions). It is noted under F2 only because it lets an off-topic BM25 article lead the X1 path; changing the fusion weight is not proposed here.
