# On-device runtime for a learned emergency classifier (Forge, 2026-10-03)

TL;DR
- **Recommendation:** run any encoder classifier through **llama.rn**, the runtime the app already ships. **Not through ONNX Runtime.** Order:
  1. **(a) linear head on bge-small:** ~0 ms and 0 MB. Try first.
  2. **(b) mmBERT-small GGUF via llama.rn, head in JS:** if (a) misses the recall bar on PT/ES.
  3. **(c) the 4B one-token gate:** only as a **3rd label fused into the existing B6 route gate**. Never as a separate call, and never as the only detector: it can't cover the 1.5B / iPhone 13 tier.
- **Why ORT loses:** the same speed as llama.cpp q8_0 on the same model (measured). The costs:
  - **+25.8–33.0 MB** `libonnxruntime.so` per ABI;
  - floating native versions (`latest.integration` on Android, an unpinned `onnxruntime-c` pod on iOS);
  - no tokenizer: mmBERT's 256k-vocab Gemma-style BPE would have to run in Hermes JS or through onnxruntime-extensions.
  - llama.rn tokenizes in C++, and the GGUF tokenization matched HF exactly.
- **mmBERT-small works on llama.rn's own llama.cpp** (b11010 `4bc272f`, the exact commit vendored in llama.rn 0.13.0-rc.4):
  - the converter needs **a 5-line patch**: upstream doesn't recognize mmBERT's tokenizer;
  - the pooled vector matches HF (cos 1.0000 f16, ≥ 0.9996 q8_0);
  - but the in-GGUF classifier head drifts at q8_0, and llama.rn can't return 2 labels anyway → **the head lives in JS**.

Lane: Forge · Status: sizing done on the desktop (M1 Pro, CPU, 2 threads = the app's embedder setting); no device numbers · Time box: ~1.5 h, interleaved with the parked iOS session prep

## 1. Numbers

**Message length** (`exp/classifier-runtime/toklen.py`; dev sets only: chat-slice v0 64 messages + v0.1 public 60):
- tokens p50 / p90 / max: **mmBERT 11 / 26 / 51**, bge 12 / 25 / 44;
- bge needs 1.26–1.34× more tokens on PT/ES chat (English WordPiece); the same on EN;
- with 1–2 turns of history: ~64–128 tokens.

**Latency per call** (ms; M1 Pro, CPU, 2 threads, min over 3–4 interleaved reps × 8 runs; `bench1.csv`, `bench2.csv`, `ort_bench.py`):
- The Mac was shared: load average 20–66 from other agents. So **min, not median**: medians were 2–10× noisier.
- The ratios between rows are the robust part.

| Tokens | bge-small q8_0 (llama.cpp) | mmBERT-small q8_0 (llama.cpp) | mmBERT-small f16 (llama.cpp) | mmBERT-small int8 (ORT 1.30) | mmBERT-small fp32 (ORT) |
|---|---|---|---|---|---|
| 16 | **4.3** | **6.7** | 7.7 | 6.3 | 17.4 |
| 32 | **5.9** | **13.7** | 13.0 | 11.0 | 28.5 |
| 64 | 15.3 | 19.0 | 26.6 | 20.5 | 49.7 |
| 128 | 34.7 | 40.3 | 53.4 | 35.8 | 89.3 |

- **mmBERT ≈ 1.2–2.3× bge** per call at the same token count. Its non-embedding compute is ~2× bge's (42 M vs 21.5 M params; 22 vs 12 layers at width 384).
- **ORT int8 ≈ llama.cpp q8_0**: within ±20%, no speed case for ORT.

**Scaled to the devices** (estimates):

| Message | g75 (×2.4, range ×2.0–3.0, as in forge/README L0) | iPhone 13 (A15 ≈ M1 single-core: ×1.05–1.3; the embedder runs on CPU) |
|---|---|---|
| bge, message only (16–32 tok) | **≈ 10–15 ms** | ≈ 5–8 ms |
| mmBERT, message only (16–32 tok) | **≈ 16–35 ms** (13–41) | ≈ 7–18 ms |
| mmBERT, message + history (64–128 tok) | ≈ 45–100 ms (38–121) | ≈ 20–52 ms |

- Conflicting note: Sonar's P-4 card says bge is "~17× slower on the iPhone" for ~250-token passages, which these ratios don't predict. UNKNOWN until the device `embedMs` stage timer runs (the PHONE-SESSION / IOS-SESSION legs).

**Memory and files** (`rss.py`; macOS footprint = what iOS jetsam counts; `n_parallel 8` = llama.rn's default, which sets `n_seq_max`):

| Model | File | Peak footprint | Notes |
|---|---|---|---|
| bge-small q8_0 (shipped) | 36.8 MB | **42 MB** | |
| mmBERT-small q8_0 | 155.5 MB | **127 MB** (+85 vs bge) | Of that: mapped weights + 42.9 MiB CPU_REPACK copy (repacks on arm64 dotprod/i8mm, so likely on the g75; Anvil saw no repack for the 1.5B on the A15 today) + 10.5 MiB compute + **7.8 MiB logits buffer** |
| mmBERT-small q8_0 + **q4_0 token table** | **106.4 MB** | ≈ same | Pooled vector cos vs HF ≥ 0.9992 (q8_0: ≥ 0.9996). The 256k × 384 token table is 2/3 of the file |
| mmBERT-small int8 ONNX | 141.5 MB | +47 MB RSS at session load (Python process delta, rough) | |

- **Trap found:** llama.cpp allocates a logits buffer of `n_vocab × n_seq_max` floats **even in embedding mode** (`llama-context.cpp:2066`, `has_logits = true`).
  - For mmBERT's 256k vocab that is **1 MB per sequence**.
  - The `llama-embedding` CLI defaults to 256 sequences: **250 MiB**, footprint 349 MB.
  - llama.rn's default `n_parallel` 8 gives 7.8 MiB. **Set `n_parallel: 1` on the classifier context** (→ ~1 MiB).
- **Budget check, iPhone 13 (4 GB):** 1.5B footprint ~346–377 MB (Anvil, today) + bge 42 + mmBERT ~120 → ~0.55 GB. That is within reach even with the increased-memory-limit entitlement stripped. Android g75 8 GB: not a constraint.

**Binary size** (`onnxruntime-react-native` 1.24.3, the latest on npm, modified 2026-07-16):

| Runtime | Native size per ABI | Already in the app? |
|---|---|---|
| llama.rn (`librnllama_v8_2_dotprod_i8mm.so` etc.) | 11.5–14.6 MB per variant | **yes: +0** |
| ORT `libonnxruntime.so` arm64 | **25.8 MB** (1.24.3) / **33.0 MB** (1.30.0), uncompressed | no |
| ORT iOS (`onnxruntime-c` pod, static) | UNKNOWN; desktop-derived ~15–25 MB of app size | no |
| ORT Mobile reduced-ops build (~3–5 MB) | needs building ORT from source with an op config, per platform | no: a heavy toolchain for a stranger's build |

## 2. Option by option

### (a) Linear head on the existing bge-small embedding (llama.rn `embedding()`)
- **Cost:**
  - **0 extra ms** on messages that retrieve anyway: the same text, one embedding, passed down via `retrieve(opts.queryVec)`;
  - **+1 embedding (≈ 10–15 ms g75, ≈ 5–8 ms iPhone)** on messages that skip retrieval (smallTalk/calc/instant) or when the classifier reads message + history;
  - the head is a 385-float dot product: µs;
  - RAM 0, download 0, build 0, no native change.
- **Integration:**
  - `isHealthQuestion` is sync, so the vector must exist before routing: embed first, then route, then hand the vector to `retrieve`;
  - `EmbeddingEngine` serializes calls (`src/rag/embed.ts` queue), so a second text (history) adds its full cost.
- **Catch:** `embedding()` L2-normalizes by default (`embd_normalize`). Train the head on L2-normalized vectors, or call with `{embd_normalize: -1}`. Either way, use the same choice in training and in the app.
- **Accuracy is the open question** (Sonar/Compass, not Forge): bge-small-**en** is English-only. Compass's prototype head (2026-10-01) had D1 recall 23/24 but 3/55 FP on bench.

### (b) mmBERT-small: GGUF via llama.rn vs ONNX Runtime RN

| | **GGUF via llama.rn** | ONNX Runtime RN |
|---|---|---|
| Speed (M1, 2 threads, 16–32 tok) | q8_0 6.7–13.7 ms | int8 6.3–11.0 ms |
| Output vs HF | **f16 pooled cos 1.0000; q8_0 ≥ 0.9996**; 155-token sliding-window path not separately checked on GGUF | **fp32 exact (incl. 155 tok)**; dynamic int8 drifts up to 2.7 logits on an *untrained* head |
| Tokenizer | **built-in C++; ids identical to HF** on the PT sentence checked (17/17) | **none**: Gemma-style SentencePiece-BPE (byte_fallback, 256k vocab, 580k merges; tokenizer.json 17.5 MB) in Hermes JS, or onnxruntime-extensions ops. Parity and startup cost UNKNOWN |
| Binary | **+0** | +25.8–33.0 MB/ABI Android; iOS UNKNOWN |
| Model download | **+106 MB** (q8 + q4_0 tokens) / +156 MB (q8) | +141.5 MB (int8) |
| RAM (footprint) | ~+80–85 MB with `n_parallel: 1` | ~+50 MB (rough) |
| Head | **in JS** on the pooled vector (see below) | in the graph |
| Build / reproducibility | **converter patch** (superseded by Sonar's `convert-mmbert-e5-vocab.patch`, see §3b; mine was 5 lines: `_set_vocab_llama_hf` fallback when the BPE pre-tokenizer isn't recognized). Model conversion is offline; the app is unchanged except a 3rd `initLlama` context (`embedding: true, pooling_type: mean, n_parallel: 1, n_threads: 2`) | new native dependency on both platforms + prebuild; **floating versions to pin** (`extractLibs …:latest.integration@aar` in its build.gradle; unpinned `onnxruntime-c` pod); JSI install via `RCT_EXPORT_BLOCKING_SYNCHRONOUS_METHOD` (bridge interop): **New Arch / RN 0.86 behaviour UNKNOWN** until built |
| **Verdict** | **GO, if (b) is needed** | **KILL** for now |

- **Head in JS, not in the GGUF:**
  - llama.cpp does run ModernBERT's sequence-classification head (`cls_out`, RANK pooling): f16 logits match HF (e.g. −0.120/2.632 vs −0.125/2.614).
  - At **q8_0 the head drifts up to 1.0 logit**.
  - llama.rn's JS exposes `embedding()` (pooled vector) and `rerank()` (one score), not a 2-label output.
  - So: export the pooled vector, then run HF's head in JS: dense 384×384 → GELU → LayerNorm → 384×2, ≈ 148k floats ≈ 0.6 MB f32, < 1 ms.
  - Or train only a linear head on the pooled vector, the same shape as (a).
- **Ship gate for any GGUF classifier** (Sonar's arm), computed on Compass's 300-item dev set, HF fp32 vs the shipped GGUF + JS head:
  - token ids identical on 100%;
  - decision agreement ≥ 99%;
  - max |Δp| reported.
  - Quantization error on a trained head is UNKNOWN: my head was random.
- **Size lever (training side, UNKNOWN effort):** pruning the 256k vocab to the EN/PT/ES tokens actually used would cut the table, which is 2/3 of the file → ~60–70 MB.

### (c) The 4B one-token gate (Anvil's spec: `anvil/specs/probe-gate-prefix-cache.md`, `anvil/exp/chat-routing/README.md`)
- **Cost as a separate EMERGENCY call** (same mechanics as the route gate):

  | Setup | Overhead |
  |---|---|
  | g75 4B, prefix cached (session swap) | **+0.7–1.4 s p50**, ≤ 3.3–5 s with history |
  | g75 4B, uncached | **+15–22 s** |
  | iOS 4B profile | +0.2–0.4 s (desktop-derived; no ≥ 8 GB iPhone) |

  Plus ~36 MiB per cached prefix file on disk. Every number is a prediction: Probe B and gate leg B never ran (the g75 went before session 2).
- **Fused as a 3rd label in the B6 route gate** (SEARCH / ANS / EMERGENCY): **≈ 0 marginal ms**, the same single forward. The costs:
  - it changes the B6 prompt, which passed v2-fresh (55/57), so L0 → L1 → fresh confirm must be redone;
  - the gate today runs **after** smallTalk/calc/danger/geo, but an emergency check must run before instant paths, so the order must move.
- **Coverage gap:** the gate ships on the 4B only (B6 collapses the 1.5B's label mass < 0.4 on 5/12 items). The iPhone 13 / 4 GB tier would have **no learned detector**. So (c) can be a second opinion on the 4B tier, never the base layer.

## 3. Decision

- **Decisions (Forge's lane, reversible):**
  - runtime = llama.rn for any encoder classifier;
  - ORT RN not adopted;
  - mmBERT head in JS;
  - `n_parallel: 1` on any big-vocab embedding context.
- **Options (Sonar/Compass pick on accuracy):** (a) bge head first, because it is free. Move to (b) mmBERT only if (a) fails the recall bar on PT/ES. Then cost = +106 MB download, +~85 MB RAM, +16–35 ms per message on the g75. Optionally (c) fused into B6 on the 4B tier.
- **Tasks if (b) is chosen:**
  1. Sonar: fine-tune `ModernBertForSequenceClassification`, then export with the converter patch;
  2. Forge: a JS head + 3rd context arm, the parity gate above, and device `embedMs` on the g75/iPhone;
  3. Kiln: desktop identity run.

UNKNOWN:
- real device ms: the in-app `embedMs` timer isn't measured on any phone yet; this conflicts with Sonar's "17× on iPhone" note;
- the trained head's quantization tolerance;
- ORT iOS binary size and New-Arch behaviour (moot if KILL holds);
- the effort of mmBERT vocab pruning;
- (c) device cost (Probe B pending).

## 3b. Review of Sonar exp-30 (2026-10-03, after the above)

- **My converter patch was wrong** (`exp/classifier-runtime/convert-mmbert-vocab.SUPERSEDED.patch`):
  - `_set_vocab_llama_hf` writes the placeholder score −1000 for every token, so llama.cpp's SPM splits rare words differently from HF.
  - Only 55/300 were identical on Sonar's set. My single-sentence check missed it.
  - **Use `sonar/exp/30-learned-detector/convert-mmbert-e5-vocab.patch`** (score = −merge rank).
  - Forge fuzz of his GGUF (`/tokenize` vs HF; 1,006 strings): real queries 72/72, answers 149/149, 600 random vocab-piece strings 600/600.
- **Runtime contract fixes sent to Sonar:**
  1. strip leading whitespace after the 700-code-point cut (18/150 random cuts mismatched, 0/150 after `lstrip`);
  2. a token-aware input budget of 126 + BOS/EOS. Training and HF parity truncate at 128 tokens; llama.rn doesn't (700 PT chars ≈ 163 tokens; 700 emoji = 703 tokens > n_ubatch). On an `embedding()` error, fail safe;
  3. `pooling_type: 1` as an int (the GGUF has no pooling key; llama.rn ignores a string);
  4. report gate agreement at the shipped threshold 0.071. Recomputed: 298/300 and 900/903 → still PASS.
- **Vocab pruning via an id remap is impossible through llama.rn:** `embedding()` takes text only.

## 4. Reproduce

`exp/classifier-runtime/`. The scratch models were not kept in the repo; sha256 prefixes are in `artifacts.sha256`.

```fish
# llama.cpp = llama.rn's vendored commit
git clone --depth 1 --branch b11010 https://github.com/ggml-org/llama.cpp; cd llama.cpp; git apply ../../../sonar/exp/30-learned-detector/convert-mmbert-e5-vocab.patch
cmake -S . -B build -DGGML_METAL=OFF -DLLAMA_CURL=OFF; cmake --build build -j 8 --target llama-embedding llama-bench llama-quantize llama-tokenize
# venv: torch transformers onnx onnxruntime onnxscript sentencepiece + pip install -e llama.cpp/gguf-py
# mmbert-small-cls = jhu-clsp/mmBERT-small loaded as AutoModelForSequenceClassification(num_labels=2), saved (random head, seed 0)
python llama.cpp/convert_hf_to_gguf.py mmbert-small-cls --outtype f16 --outfile mmbert-small-cls-f16.gguf
llama.cpp/build/bin/llama-quantize mmbert-small-cls-f16.gguf mmbert-small-cls-q8_0.gguf q8_0
llama.cpp/build/bin/llama-quantize --token-embedding-type q4_0 mmbert-small-cls-f16.gguf mmbert-small-cls-q8-te4.gguf q8_0   # q4_K fails validation
python parity.py; python export_onnx.py; python ort_bench.py; python rss.py; python toklen.py
llama.cpp/build/bin/llama-bench -m <gguf> -embd 1 -p 16,32,64,128 -n 0 -t 2 -r 8 -o csv
```
