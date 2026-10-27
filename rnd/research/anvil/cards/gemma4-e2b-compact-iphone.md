# Gemma 4 E2B QAT as the 4 GB iPhone compact model, gated by a measured resident-memory ceiling
TL;DR: replace Qwen2.5-1.5B on the iPhone 13 with Gemma 4 E2B QAT Q4_0 (MMLU-Pro 60.0 vs 32.4). Its per-token hot set is 1.31 GiB, because the 1.79 GiB PLE table is row lookups. Whether that fits under the iPhone's observed ~1.2 GB resident ceiling is the open question, so step 0 is a cheap quant-ladder probe that measures the ceiling.
Lane: Anvil · Status: evidence · Priority: B
Axes moved:
- **Quality ↑, possibly large, but only if it runs at usable speed.** The compact 1.5B is the weakest reader in the repo: 45% on factual 38, against 68% for the 4B (Kiln D3). E2B's general scores sit between the 1.5B and the 4B: MMLU-Pro 60.0 vs 32.4 (1.5B) vs 69.4 (E4B).
- **Truthfulness ↑.** AA-Omniscience E2B −24. Qwen2.5-1.5B has no AA-Omniscience number (UNKNOWN); Qwen3-4B-2507 is −61.
- **Latency ↓ (worse).** It has 35 layers vs 28 and a 262k vocab (lm-head 0.31 GiB vs 0.18), so decode should be about 0.7× the 1.5B at best (UNKNOWN). If it thrashes, decode collapses to ~0.35 tok/s, as MiniCPM5-2B did.
- **Resources ↑.** 3.35 GB file vs 0.99 GB.
Fits BOAR?
- Android: yes.
- **iPhone 13 (4 GB): UNKNOWN, borderline.**
  - Hot weights per token (my GGUF parse, `tools/gguf_sizes.py`):
    - **E2B 1.311 GiB**: backbone 1.003 GiB Q4_0 plus `token_embd` 0.308 GiB Q6_K, which is tied as the output head.
    - Qwen2.5-1.5B Q4_K_M **0.913 GiB**: runs at 14 tok/s.
    - MiniCPM5-2B Q4_K_M: 1.56 GB file, ≈ 1.45 GiB, all hot. **Thrashed at 0.35 tok/s, with RSS stuck at ~1.2 GB** (`review/IPHONE-MODEL-AB-rc6.md`).
  - So E2B needs 1.44× the 1.5B's hot set and 0.90× MiniCPM5-2B's.
- llama.rn rc.4: the `gemma4` arch and `lazy_mode` are present (b11010 headers).
- Offline: yes.
Evidence:
- **Model:** Gemma 4 E2B, 2.3B effective / 5.1B total. MMLU-Pro **60.0**, GPQA-D 43.4, LiveCodeBench v6 44.0 ([model card](https://huggingface.co/google/gemma-4-E4B-it), accessed 2026-10-01). AA Intelligence Index 15 and AA-Omniscience **−24** ([AA, 2026-04-06](https://artificialanalysis.ai/articles/gemma-4-everything-you-need-to-know)). QAT Q4_0 GGUF released 2026-06-05 ([Google blog](https://blog.google/innovation-and-ai/technology/developers-tools/quantization-aware-training-gemma-4/)).
- **Baseline:** Qwen2.5-1.5B-Instruct MMLU-Pro **32.4**, GPQA 29.8, IFEval 42.5 ([Qwen2.5 blog](https://qwenlm.github.io/blog/qwen2.5-llm/), accessed 2026-10-01). Strength: vendor numbers both sides, closed-book; reading quality with sources is untested.
- **Memory layout of the exact file** [`google/gemma-4-E2B-it-qat-q4_0-gguf`](https://huggingface.co/google/gemma-4-E2B-it-qat-q4_0-gguf) `gemma-4-E2B_q4_0-it.gguf` (3,349,516,256 B), read from its GGUF header with a 40 MB HTTP range request:
  - `per_layer_token_embd` [8960 × 262144] Q4_0 **1.794 GiB**;
  - `token_embd` [1536 × 262144] Q6_K 0.308 GiB;
  - everything else 1.003 GiB;
  - 35 blocks, embedding 1536, PLE width 256 per layer.
- **PLE residency in llama.cpp:**
  - Lazy row reads for PLE/engram tables arrived in [#27794](https://github.com/ggml-org/llama.cpp/pull/27794) (merged 2026-08-27). On E4B Q5_K it cut peak RSS from 7.37 to 6.16 GB, at a cost of −8 to −10.7% prefill and −10.7% decode.
  - llama.rn rc.4 ships it, but leaves `common_params.lazy_mode = LLAMA_LAZY_MODE_AUTO`. AUTO is lazy only for tensors **> 4 GiB**, so E2B's 1.79 GiB table is read up front.
  - The JS API has no `lazy_mode` field (`node_modules/llama.rn/src/types.ts`, `ios/.../Headers/common.h:488`, `llama.h:217-220`).
  - With `use_mmap: true` these are clean file pages that the OS can evict. But the up-front read competes with the backbone for the same ~1.2 GB budget on a 4 GB phone.
- **What the ~1.2 GB ceiling is: UNKNOWN.**
  - The app already has `com.apple.developer.kernel.increased-memory-limit` (`app.json`). So it is not the jetsam limit alone; candidates are page-cache pressure from the SQLite packs and the embedder, or the iOS memory compressor.
  - The rc6 A/B saw "RSS stuck at ~1.2 GB; 1.5 GB ÷ 2.9 s/token matches flash reads", which is consistent with file-page eviction.
Test in boar-eval:
- **Step 0: ceiling probe.**
  - Device: iPhone 13, coordinator-scheduled, ≈ 30 min, no app change.
  - Load the same model at rising hot-set sizes and record decode tok/s and RSS on the s16 subset, quick-first, kit A installed:
    - Qwen2.5-1.5B Q4_K_M 0.91 GiB (control);
    - Q5_K_M 1.05 GiB;
    - Q6_K 1.19 GiB;
    - Q8_0 1.53 GiB.
    - Files (HF API, [`bartowski/Qwen2.5-1.5B-Instruct-GGUF`](https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF) @ `9eadc66189`, Apache-2.0): Q5_K_M 1,125,050,624 B, Q6_K 1,272,740,096 B, Q8_0 1,646,573,312 B. Q5_K_M is just over 1 GB, so it needs the coordinator's OK like Q8_0.
  - The decode cliff gives the ceiling **C**.
  - **Go to step 1 only if the decode at the rung nearest 1.31 GiB is ≥ 0.7× the control's.**
- **Step 1: desktop gate.**
  - Runs on the shared engine (0cfd4a77, boar-eval desktop adapter), compact profile (4 GB, ios). E2B vs Qwen2.5-1.5B, gate mode, bench public + safety track.
  - Pass:
    - pass rate ≥ +10 pp;
    - confident-wrong not higher;
    - unsafe ≤ the 1.5B's;
    - The arm's catalog entry must set **`answerTier: "compact"`**. `isCompactModel` (`src/routing/defaultModel.ts`, 0cfd4a77) falls back to file size ≤ `LOW_RAM_MAX_MODEL_BYTES` for untiered models. The 3.35 GB file would therefore be treated as a non-compact model, which skips the compact citation gate, and `tooBigForLowRam` / `tooBigForAutoPick` would block it on 4 GB. All three size checks use **file size**, which is wrong for PLE models: the hot set is 1.31 GiB, not 3.35 GB.
- **Step 2: iPhone run.**
  - Full mode, ≥ 2 runs, against D10/Q4.
  - Pass:
    - quality ratio mean ≥ +0.05 over 0.354, about 1.6× the retest noise;
    - decode ≥ 8 tok/s;
    - TTFT p50 ≤ 1.5× the 1.5B's;
    - no jetsam kills in the load marker (CR-2).
- **Success criterion (stated before any run): all three steps pass.** Fail at step 0 means the E2B is dropped for the 4 GB tier, and the ceiling number C is the deliverable: it bounds every future compact-model choice.
Cost to try:
- Step 0: ~1 h device time and ≤ 2.7 GB of downloads (coordinator OK needed for Q8_0).
- Step 1: ~1 h on the mini, 3.35 GB download. **The mini's disk is at its floor tonight (QUEUE.md), so it waits until the Gemma E4B file is deleted.**
- Step 2: ~1 h device time.
- Risk: medium. It probably thrashes.

## Relation to `compact-reader-by-hot-set` (cycle 13)

- E2B's hot set is 1.31 GiB. Qwen3.5-2B IQ4_XS (≈ 1.09 GiB) and Qwen3-1.7B (1.03 GiB) are lighter candidates with large vendor gains over the 1.5B. Step 0 here (the ceiling ladder) serves all of them; test the lighter ones first.

## Why the hot set, not the file size, is the number to watch

- With `use_mmap: true`, a weight costs RAM only while it is being read.
- A dense model reads every matrix every token, so its hot set is its whole file.
- Gemma's PLE table is a lookup: each token reads 35 rows of 256 values (35 × 256 × 4.5 bits ≈ 5 KB). Only a few MB of the 1.79 GiB are ever hot in a chat.
- The output head is the exception. Gemma ties `token_embd` to the logits matmul, so all 0.308 GiB are read every token, the same as Qwen's 0.178 GiB tied head.

## Levers if step 0 lands just short (C between 1.1 and 1.3 GiB)

- **Requantize only `token_embd` from Q6_K to Q4_0:**
  - `llama-quantize --allow-requantize --token-embedding-type q4_0`.
  - The head drops to ≈ 0.21 GiB and the hot set to ≈ 1.21 GiB.
  - Cost: some logit precision. Measure perplexity on 50 bench prompts before using it.
- **Set `lazy_mode = ON` in llama.rn's native defaults** (one line, rebuild required). It stops the up-front read of the PLE table, so the first answers don't evict the backbone. The PR measured about 10% slower decode.
- Not recommended: IQ3/IQ2 backbones. Low-bit knowledge loss ([arXiv 2609.32902](https://arxiv.org/abs/2609.32902), via Lantern radar) hits exactly what a knowledge app needs.

## Product note (for whoever implements)

- BOAR's low-RAM caps (`AUTO_PICK_MAX_MODEL_BYTES` 1.1e9, `LOW_RAM_MAX_MODEL_BYTES`) compare **file size**. For PLE/engram models the right number is the hot set: file minus the PLE/engram tables. It can be read from the GGUF header at no cost; BOAR already reads the header for the arch (`readArch`). Otherwise no Gemma E-series model can ever be auto-picked on a 4 GB phone, even if step 0 shows it fits.

## What would make it fail

- **Hidden thinking (cycle 10 correction).** E4B's apparent 2.5 tok/s was the fast tier's 256-token thinking budget, not slow decode (see `gemma4-e4b-reader-android`, correction). Any E2B arm must run with `enableThinking: false`, and its latency must be read as first *visible* text. Otherwise 256 hidden tokens at the 1.5B-class rate (~15 tok/s on the iPhone 13) add about 17 s of silence.

- **The ceiling.** C ≤ 1.2 GiB, as MiniCPM5-2B suggests (1.45 GiB → 0.35 tok/s). Then E2B thrashes like MiniCPM5-2B. This is the most likely failure.
- **Speed.** Even in RAM, 35 layers and the 262k-vocab head make decode slower than the 1.5B. Below ~8 tok/s the latency axis loses what quality gains; the post author already rejects "10 TPS".
- **Reading.** Strong closed-book scores (MMLU-Pro) do not guarantee better reading of the sources. Step 1 checks it.
- **The decline gate.** On the shared engine the compact citation gate declines answers that cite unsupported sources (see `citation-exemplar-prompt`). A model that answers more from memory would be declined just as often.

UNKNOWN:
- The real ceiling cause and value on the iPhone 13 (step 0).
- E2B decode/prefill on A15 CPU with llama.rn.
- AA-Omniscience for Qwen2.5-1.5B.

Shelf: rows "Gemma 4 E2B-it QAT Q4_0 GGUF", "Qwen2.5-1.5B-Instruct quant ladder", "llama.cpp lazy PLE/engram reads" in `../../SHELF.md`.
