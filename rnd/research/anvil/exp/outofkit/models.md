# Out-of-kit answer models for the 12 GB Android tier: candidates vs Qwen3-4B-Instruct-2507 (Anvil desk research, 2026-10-03)

Scope: closed-book answers (the question is not in the offline library). Baseline: **Qwen3-4B-Instruct-2507 Q4_K_M, 2.50 GB**. Runtime: llama.rn 0.13.0-rc.4, which vendors llama.cpp **b11010**. b11010 is commit `4bc272fd72`, 2026-09-16; `git rev-list --count` = 11010. No weights were downloaded. Sizes come from the HF API. Tensor layouts come from GGUF headers read with HTTP range requests: about 4–16 MB per file, metadata only.

## TL;DR: top 3 to test

1. **Ministral 3 8B Instruct 2512.**
   - Has the best factual-recall evidence on a shared harness: TriviaQA 5-shot (base models) **68.1 vs 53.0** for Qwen3-4B-Base, the base the 2507 model was post-trained from. Qwen3-8B-Base scores 63.9 on the same harness.
   - Instruct-only, so there is no thinking to switch off. Apache-2.0. Official GGUF, 5.20 GB. `mistral3` has been in llama.cpp since b7216.
2. **Qwen3.5-9B, non-thinking.**
   - The strongest dense model under 10B on knowledge and reasoning benchmarks: MMLU-Pro 82.5 / GPQA-D 81.7 (vendor, thinking mode).
   - AA-Omniscience accuracy is **14.7% vs 12.7%** (independent), a small gain.
   - Same `qwen35` family as the Qwen3.6-35B-A3B that gave +0.06 in BOAR. GGUF 5.68 GB. In llama.cpp since b7990.
3. **Ministral 3 3B Instruct 2512 (the cheap arm).**
   - TriviaQA 5-shot (base) **59.2 vs 53.0** for the Qwen3-4B base, at a **smaller** file (2.15 GB) and the same or faster speed.
   - Instruct-only. Same `mistral3` support. It is the only 3–5B candidate with factual-recall evidence above the baseline.

Caveats that apply to all three:
- **No candidate has a published closed-book SimpleQA score, and neither does Qwen3-4B-2507.** The factual-recall evidence is base-model TriviaQA (same harness, Mistral) and AA-Omniscience (independent).
- The 8–9B dense models decode about **2× slower** than the 4B: about 4–8 vs 8–15 tok/s, estimated.
- They fit 7–8 GB **only with `no_extra_bufts: true`**. With ARM repack, the load peak is about 11 GB, which means an LMK kill.

## How the estimates are computed (the same for every row)

- **Decode** (memory-bound): `tok/s = BW_eff / bytes_read_per_token`.
  - `BW_eff` = 35–50% of a 60–77 GB/s LPDDR5X peak = **21.0–38.5 GB/s**.
  - `bytes_read_per_token` = GGUF bytes of the weights touched per token, taken from the header. That is the whole file minus the input-only embedding when the output head is untied, minus Gemma's PLE table, and for MoE only the active-expert share.
  - KV reads are ignored. They add up to about 0.6 GB/token-step at a full 4k context for 8-KV-head models, so long prompts decode slower.
  - Calibration: with the g75's 25.6 GB/s and the same 24–37% efficiency, the 2.49 GB 4B gives 2.5–3.8 tok/s. That reproduces the earlier prediction.
- **Prefill** (compute-bound): `tok/s = [12–18] × [2–2.5] × (4.022 / P_active)`.
  - 12–18 tok/s is the 4B's predicted prefill on the g75. 2–2.5× is the faster SoC.
  - `P_active` = billions of matmul parameters per token, from the header. The tied output head counts; Gemma's PLE does not.
  - Low end = 12 × 2; high end = 18 × 2.5. Hybrid layers (Gated DeltaNet, short-conv, Mamba) may not scale like attention on ARM: UNKNOWN.
- **RAM:**
  - No-repack: `file + KV(4096, f16) + 0.3 GB compute`.
  - Repack peak: `file + repackable matmul weights (≈ backbone + output) + KV + 0.3`. llama.cpp's ARM repack copies Q4_K/Q4_0/Q8_0 weights to anonymous memory unless `no_extra_bufts` is set. The llama.rn rc.4 switch already exists; see `../../cards/android-lowram-no-repack.md` (Probe A: anon 3.25 → 0.9 GB for the 4B).
  - Budget: about 7–8 GB per process.
- **KV formula:** `layers_with_own_KV × KV_heads × head_dim × 2 (K,V) × 2 B × 4096`. Examples:
  - Qwen3-4B: 36 × 8 × 128 × 4 × 4096 = **0.60 GB**.
  - Ministral 3 8B: 34 × 8 × 128 × 4 × 4096 = **0.57 GB**.
  - Qwen3.5-9B/4B: only 8 of 32 layers have attention (4 KV heads × 256), so 8 × 4 × 256 × 4 × 4096 = 0.13 GB. Add the DeltaNet state, 24 layers × 32 heads × 128 × 128 × 4 B ≈ 0.05 GB, for **≈ 0.19 GB**.
  - Gemma 4 E4B: 24 layers own KV, 18 are shared. 4 global layers (2 × 512) × 4096 plus 20 SWA layers (2 × 256) × ~1024 cells gives **≈ 0.11 GB**, or 0.24 GB with a full SWA cache.
- **Illustration** (400-token prompt + 200-token answer), Qwen3-4B vs an 8B:
  - Qwen3-4B: TTFT 9–17 s, total ≈ 22–41 s.
  - An 8B: TTFT 17–33 s, total ≈ 43–80 s.
  - The 8B is about 2× worse on both. Against the default-answer bar in `README.md` (8 s / 15 s), the 8B models only fit as an on-demand "answer from memory, slower" path or with much shorter prompts. Out-of-kit prompts carry no sources, so their prompts are short. That helps.

## Group 1: dense 7–9B (Q4 ≈ 4.5–5.7 GB)

Columns: SimpleQA / MMLU-Pro / GPQA. "think" = the vendor reports the number in thinking mode, not the mode BOAR would run.

| Model | GGUF repo · file · bytes | Release | License | llama.cpp arch · in b11010? (PR → build) | Params total / active | No-think mode | SimpleQA / MMLU-Pro / GPQA | Other factual-recall evidence | PT/ES evidence | RAM: no-repack / repack peak | Decode / prefill tok/s (12 GB phone, est.) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Reference: Qwen3-4B-Instruct-2507** | `unsloth/Qwen3-4B-Instruct-2507-GGUF` · `Qwen3-4B-Instruct-2507-Q4_K_M.gguf` · 2,497,281,120 | 2025-07/08 | Apache-2.0 | `qwen3` · yes (#12828 → b5092) | 4.02B / 4.02B | instruct-only | UNKNOWN / **69.6** / **62.0** (GPQA, non-think) | AA-Omniscience: **acc 12.7%, halluc. 84%, index −61** (AA calls it "Qwen3 4B 2507"; Instruct or Thinking variant UNKNOWN). TriviaQA 5-shot of its base Qwen3-4B-Base: **53.0** (Mistral harness) | MMLU-ProX 61.6, INCLUDE 60.1, MultiIF 69.0 | 3.40 / 5.57 GB | 8.4–15.5 / 24–45 |
| **Ministral 3 8B Instruct 2512** | `mistralai/Ministral-3-8B-Instruct-2512-GGUF` (official) · `Ministral-3-8B-Instruct-2512-Q4_K_M.gguf` · 5,198,911,904 (alt. `bartowski/…` IQ4_XS 4,696,414,464) | 2025-12-02 | Apache-2.0 | `mistral3` · **yes** (#17644, merged 2025-12-01 → **b7216**) | 8.49B LM (+0.4B vision encoder in a separate mmproj, not needed) / 7.95B matmul | **no thinking at all** (Reasoning is a separate model). Vendor: temp < 0.1 | UNKNOWN / UNKNOWN / 39.9 (base, 0-shot); 66.8 is the *Reasoning* variant | **TriviaQA 5-shot (base): 68.1** vs Qwen3-8B-Base 63.9 vs **Qwen3-4B-Base 53.0** (same table). MMLU 5-shot (base) 76.1. Arena Hard 0.509 (Qwen3-VL-8B-Instruct 0.528) | PT and ES listed. Multilingual MMLU (base): **European avg 73.4**; 0.706 vs Qwen3-4B-Base 0.677. Per-language PT/ES: UNKNOWN | 6.07 / 10.96 GB | 4.3–7.9 / 12–23 |
| **Qwen3.5-9B** | `unsloth/Qwen3.5-9B-GGUF` · `Qwen3.5-9B-Q4_K_M.gguf` · 5,680,522,464 (alt. IQ4_XS 5,168,653,536; `lmstudio-community/Qwen3.5-9B-GGUF` Q4_K_M 5,627,044,256) | 2026-03-02 (HF repo 2026-02-27) | Apache-2.0 | `qwen35` (hybrid Gated DeltaNet) · **yes** (#19468, merged 2026-02-10 → **b7990**) | 8.95B (text GGUF) / 7.94B matmul. The output head is untied, so 5.10 GB is read per token | `enable_thinking: False` (**thinking is the default**) | UNKNOWN / **82.5 (think)** / **81.7 GPQA-D (think)**. Non-thinking numbers are unpublished | AA-Omniscience (reasoning): **acc 14.7%**, halluc. 82%, index −56. AA Intelligence Index (current page): **non-reasoning 13** vs Gemma 4 E4B non-reasoning 7; Qwen3-4B-2507 Instruct page: 7 (estimated) | MMMLU 81.2, **MMLU-ProX 76.3, INCLUDE 75.6**, WMT24++ 72.6 (think) | 6.17 / 11.27 GB | 4.1–7.6 / 12–23 |
| Qwen3-8B (hybrid, 2504) | `Qwen/Qwen3-8B-GGUF` (official) · `Qwen3-8B-Q4_K_M.gguf` · 5,027,783,488 | 2025-04 (GGUF 2025-05-03) | Apache-2.0 | `qwen3` · yes (#12828 → b5092) | 8.19B / 7.57B | `enable_thinking: False` or `/no_think` | UNKNOWN / UNKNOWN / **39.3 (GPQA-D, non-think)**, below the 4B-2507's 62.0 | **TriviaQA (base) 63.9 vs 53.0.** PopQA 20.4 (no reasoning, Olmo harness) | INCLUDE 62.5, MMMLU 66.9 (non-think). ES avg 52.5, PT avg 52.0 (non-think, Qwen3 report Tables 24/26) | 5.93 / 10.60 GB | 4.5–8.2 / 13–24 |
| Granite 4.2 8B | `ibm-granite/granite-4.2-8b-GGUF` (official) · `granite-4.2-8b-Q4_K_M.gguf` · 5,347,917,952 (Q4_0 5,055,955,072) | 2026-08-25 | Apache-2.0 | `granite` (dense) · yes (#9412 → b3774; IBM GGUF dated 2026-08-12) | 8.79B / 8.38B | `enable_thinking=False` (thinking is the default; also `low_effort`) | UNKNOWN / 74.04 / 64.14 (mode not stated; default is thinking). **Granite 4.1 8B (non-reasoning): SimpleQA 4.82**, MMLU-Pro 55.99, GPQA 41.96 | none beyond 4.1's SimpleQA | 12 languages incl. pt, es. MMLU-ProX-lite 61.06 (4.2). 4.1: MMMLU 64.84, INCLUDE 58.89 | 6.32 / 11.43 GB | 4.1–7.5 / 12–22 |
| Llama 3.1 8B Instruct | `bartowski/Meta-Llama-3.1-8B-Instruct-GGUF` · `Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf` · 4,920,739,232 | 2024-07-23 | Llama 3.1 Community License | `llama` · yes | 8.03B / 7.51B | instruct-only | UNKNOWN / 48.3 / 30.4 | TriviaQA-Wiki (base, Meta harness, **not comparable** with the 53.0) 77.6. Knowledge cutoff Dec 2023 per Meta card (not re-fetched), so crypto and recent facts are stale | MMLU PT 62.12, ES 62.45 | 5.76 / 10.38 GB | 4.5–8.3 / 13–24 |
| Olmo 3 7B Instruct | `unsloth/Olmo-3-7B-Instruct-GGUF` · `…-Q4_K_M.gguf` · 4,471,602,048 | 2025-11/12 | Apache-2.0 | `olmo2` key (Olmo3 via #16015 → b6492) · yes | 7.30B / 7.06B | instruct-only | UNKNOWN / UNKNOWN / 40.4 | **PopQA 14.1** vs Qwen3-8B 20.4 (same table): weaker recall | **English only** | 6.92 / 11.16 GB (KV ≈ 2.15 GB: 32 KV heads; the SWA window of 4096 equals n_ctx) | 5.0–9.1 / 14–26 |
| GLM-4-9B-0414 | `bartowski/THUDM_GLM-4-9B-0414-GGUF` · `…-Q4_K_M.gguf` · 6,166,574,464 | 2025-04-14 | MIT | `glm4` · yes (#12867 → b5115) | 9.40B / 8.78B | instruct-only (Z1 is the reasoning sibling) | UNKNOWN (not researched further) | UNKNOWN | UNKNOWN | 6.63 / 12.44 GB | 3.6–6.6 / 11–21 |
| Nemotron Nano 9B v2 | `bartowski/nvidia_NVIDIA-Nemotron-Nano-9B-v2-GGUF` · `…-Q4_K_M.gguf` · 6,525,629,280 (IQ4_XS 5,267,107,680) | 2025-08 | NVIDIA Open Model License | `nemotron_h` · yes (#15507 → b6315) | 8.89B / 8.30B | reasoning by default; off-switch UNVERIFIED | UNKNOWN | UNKNOWN | en, es, fr, de, it, ja (HF tags); no PT | 7.03 / 13.14 GB | 3.4–6.3 / 12–22 |
| Gemma 4 12B (stretch; **over budget**) | `google/gemma-4-12B-it-qat-q4_0-gguf` · `gemma-4-12b-it-qat-q4_0.gguf` · 6,975,879,296 | 2026-06-03 | Apache-2.0 | `gemma4` · yes (#21309 → b8637; 12B GGUFs on ggml-org since 2026-06-03) | 11.91B / 11.91B | omit `<\|think\|>` | UNKNOWN / 77.2 / 78.8 (GPQA-D, mode unstated) | none published (the tech report has no factuality tables) | MMMLU 83.4 | **7.85** / 13.98 GB | 3.0–5.5 / 8–15 |

## Group 2: newer 3–5B (released after Qwen3-4B-2507)

| Model | GGUF repo · file · bytes | Release | License | llama.cpp arch · in b11010? | Params total / active | No-think mode | SimpleQA / MMLU-Pro / GPQA | Other factual-recall evidence | PT/ES evidence | RAM: no-repack / repack peak | Decode / prefill tok/s (est.) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Reference: Qwen3-4B-Instruct-2507 | see Group 1 | | | | | | UNKNOWN / 69.6 / 62.0 | AA acc 12.7%; base TriviaQA 53.0 | MMLU-ProX 61.6 | 3.40 / 5.57 | 8.4–15.5 / 24–45 |
| **Ministral 3 3B Instruct 2512** | `mistralai/Ministral-3-3B-Instruct-2512-GGUF` (official) · `Ministral-3-3B-Instruct-2512-Q4_K_M.gguf` · 2,147,023,008 | 2025-12-02 | Apache-2.0 | `mistral3` · **yes** (#17644 → **b7216**) | 3.43B (tied head) / 3.43B | **no thinking** (instruct) | UNKNOWN / UNKNOWN / 33.8 (base); 53.4 is the *Reasoning* variant | **TriviaQA 5-shot (base) 59.2 vs Qwen3-4B-Base 53.0.** MMLU (base) 70.7 vs 72.99 (Qwen3-4B-Base, Qwen report). Arena Hard 0.305 vs Qwen3-VL-4B-Instruct 0.438: weaker chat quality | European-avg Multilingual MMLU 68.4 (base); PT/ES listed | 2.88 / 4.69 GB | 9.8–18.0 / 28–53 |
| Qwen3.5-4B | `unsloth/Qwen3.5-4B-GGUF` · `Qwen3.5-4B-Q4_K_M.gguf` · 2,740,937,888 (IQ4_XS 2,477,053,088) | 2026-03-02 | Apache-2.0 | `qwen35` · yes (#19468 → b7990) | 4.21B / 4.21B | `enable_thinking: False` (thinking is the default) | UNKNOWN / 79.1 (think) / 76.2 GPQA-D (think) | AA-Omniscience (reasoning): **acc 12.8%** (vs 12.7%), halluc. 80%, index −57. Liquid's own Omniscience run: acc 17.20 | MMMLU 76.1, MMLU-ProX 71.5, INCLUDE 71.0 (think) | 3.23 / 5.44 GB | 7.7–14.1 / 23–43 |
| Gemma 4 E4B (QAT Q4_0) | `google/gemma-4-E4B-it-qat-q4_0-gguf` · `gemma-4-E4B_q4_0-it.gguf` · 5,154,941,280 (already in the BOAR catalog) | 2026-04-02 (QAT repo 2026-05-01) | Apache-2.0 | `gemma4` · yes (#21309 → b8637) | 7.46B in file (PLE 2.31 GB is not read per token) / 4.64B matmul | omit `<\|think\|>`. **The BOAR fast tier currently forces thinking** (see the card) | UNKNOWN / 69.4 / 58.6 (GPQA-D) | AA-Omniscience **index −20** (AA). But Liquid's run gives **acc 8.10** vs Qwen3.5-4B 17.20. **BOAR test (thinking on): Δ −0.016, NOT ADOPTED** | MMMLU 76.6; 35+ languages | 5.57 / 7.84 GB | 7.4–13.6 / 21–39 |
| Granite 4.2 3B | `ibm-granite/granite-4.2-3b-GGUF` · `granite-4.2-3b-Q4_K_M.gguf` · 2,244,011,552 | 2026-08-25 | Apache-2.0 | `granite` · yes (b3774) | 3.66B / 3.40B | `enable_thinking=False` (thinking is the default) | UNKNOWN / 67.84 / 54.80 (mode unstated) | none (4.1-8B SimpleQA 4.82 suggests weak recall) | 12 languages incl. pt, es | 2.88 / 4.98 GB | 10.0–18.4 / 28–53 |
| Spark-X2.5-4B | `XHToken/Spark-X2.5-4B-GGUF` (official) · `Spark-X2.5-4B-Q4_K_M.gguf` · 2,600,224,352 | 2026-09-01 | Apache-2.0 | `spark2_5` · yes, but new (#27868, merged 2026-09-06 → **b10828**, 10 days before b11010) | 4.11B / 4.11B | `enable_thinking: false` (thinking is the default) | UNKNOWN / UNKNOWN / 67.4 (vendor) | none; agent/coding-focused. A "loses on knowledge" claim seen only in a search snippet: UNVERIFIED | "200+ languages" claim | 3.16 / 5.48 GB | 8.1–14.8 / 23–44 |
| SmolLM3-3B | `ggml-org/SmolLM3-3B-GGUF` · `SmolLM3-Q4_K_M.gguf` · 1,915,305,312 | 2025-07-08 | Apache-2.0 | `smollm3` · yes (#14581 → b5847) | 3.08B / 3.08B | `/no_think` | UNKNOWN / UNKNOWN / **35.7** (no_think) vs Qwen3-4B 44.4 | Global MMLU 53.5 vs Qwen3-4B 65.1 | PT Global MMLU 36.88 vs Qwen3-4B 40.66; ES 38.51 vs 41.22 | 2.52 / 4.21 GB | 11.0–20.2 / 31–59 |
| Nanbeige4.2-3B | no official GGUF (community repos only; tied to the vendor's `nanbeige42` branch) | 2026-07-27 | Apache-2.0 | `nanbeige` · upstream yes (#25994 → b10153); community-GGUF compatibility UNKNOWN | 4B / 3B non-embedding, **looped** (layers re-run, so decode cost > 1 pass: UNKNOWN) | `enable_thinking=False` | UNKNOWN / UNKNOWN / 87.4 GPQA-D (think) | none | **EN/ZH only** | UNKNOWN | UNKNOWN |
| LFM2.5-2.6B | `LiquidAI/LFM2.5-2.6B-GGUF` · `LFM2.5-2.6B-Q4_K_M.gguf` · 1,674,455,040 | 2026-08-06 | LFM Open License v1.0 | `lfm2` · yes (#14620 → b5873) | 2.70B | UNKNOWN | UNKNOWN (not researched) | UNKNOWN | pt, es in HF tags | 2.04 / 3.49 GB | 12.6–23.1 / 36–67 |

Not candidates:
- Phi successor: no Phi-5 found on the `microsoft` HF org. The newest 4B there is `FrogNano-4B-2609`, a Qwen3.5-4B SWE-agent RL finetune, English-only.
- Qwen3.6 and Qwen3.8 have no models below 27B.
- Apertus v1.5 8B: no published numbers yet.
- EuroLLM-9B-Instruct-2512: strong PT coverage, but no benchmarks on the card and "not aligned to human preferences".

## In-RAM MoE (≤ 6 GB file, ≤ 3B active): secondary

| Model | GGUF · bytes | License · arch (b11010) | Total / active (header) | No-think | Knowledge evidence | RAM (no-repack / peak) | Decode / prefill (est.) |
|---|---|---|---|---|---|---|---|
| LFM2.5-8B-A1B (local Q4_0) | `LiquidAI/LFM2.5-8B-A1B-GGUF` · `LFM2.5-8B-A1B-Q4_0.gguf` · 4,844,678,368 | LFM Open License v1.0 · `lfm2moe` yes (#16464 → b6709) + its tokenizer (#23826 → b9419) | 8.47B / 1.69B matmul (32 experts, 4 used); 1.02 GB read per token | **no: "reasoning-only model"** (Liquid) | Liquid's AA-Omniscience run: **acc 8.67**, index −24.7, non-halluc. 63.5%, vs Qwen3.5-4B acc 17.20 in the same table. Low hallucination, low knowledge | 5.19 / 9.82 GB | 20.6–37.7 / 57–107 |
| Granite 4.0 H Tiny | `ibm-granite/granite-4.0-h-tiny-GGUF` · `…-Q4_K_M.gguf` · 4,230,976,352 | Apache-2.0 · `granitehybrid` yes (#13550 → b5868) | 6.94B / 1.47B | instruct | Liquid's table: acc 9.37, **non-halluc. 6.38%** | 4.58 / 8.68 GB | 23.0–42.2 / 66–124 |
| Ling-3.0-tiny, Maple-Preview | see `../../../SHELF.md` (Kiln measured both) | | | | | | |

Verdict: the in-RAM MoEs are fast, but every one with a knowledge number is below the 4B class on accuracy. Not the lever for out-of-kit answers.

## Risks per top pick

**1. Ministral 3 8B Instruct**
- The evidence is base-model TriviaQA. The instruct model's closed-book accuracy and hallucination rate are UNKNOWN (no SimpleQA, no AA-Omniscience found).
- Cascade-distilled on only 1–3T tokens (vs 36T for Qwen3). Knowledge cutoff: UNKNOWN. That matters for crypto questions.
- About 2× slower decode and TTFT than the 4B. It needs `no_extra_bufts: true` (repack peak ≈ 11 GB vs a 7–8 GB budget). No-repack prefill cost on ARM: UNKNOWN (Probe B pending).
- Vendor recommends temp < 0.1; BOAR's sampler settings may need a per-model override. Uses the tekken tokenizer and Mistral template, so check the jinja template in llama.rn with tools off.

**2. Qwen3.5-9B (no-think)**
- Knowledge gain is small on the only independent closed-book metric: AA accuracy 14.7 vs 12.7. Its hallucination rate stays at 82%, so it may move "confidently wrong" less than quality.
- Thinking is on by default. BOAR's fast tier forces thinking (Gemma lesson), so it must pass `enableThinking: false`, or it pays the hidden-thinking latency.
- Hybrid Gated DeltaNet prefill on ARM CPU is UNKNOWN. The family runs in BOAR already (qwen35moe deep35), but only on desktop.
- 5.68 GB file with an untied 0.83 GB head. Same no-repack requirement as Ministral 8B. The vendor publishes only thinking-mode numbers.

**3. Ministral 3 3B Instruct**
- Weaker instruction-following and chat than Qwen 4B-class (Arena Hard 0.305 vs 0.438 for Qwen3-VL-4B-Instruct). The trivia gain may not survive the judge.
- MMLU (base) is slightly below the Qwen3-4B base (70.7 vs 72.99, different harnesses).
- Same unknown cutoff and SimpleQA as the 8B.

## Decisions / Options / Tasks

- **Decision (reversible):** shortlist = Ministral 3 8B, Qwen3.5-9B (no-think), Ministral 3 3B. Next alternate: Qwen3-8B (no-think): +10.9 base TriviaQA, but GPQA non-think 39.3 vs 62.0, so its post-training is older.
- **Option:** Gemma 4 E4B *non-thinking* is still untested in BOAR, but its factual-recall evidence is contradictory (AA index −20 vs Liquid accuracy 8.1). Low prior.
- **Task (minimum that closes the loop):** run the 24-item outofkit slice × 3 seeds (`README.md` harness), no-think, for Ministral 3 3B first (2.15 GB, cheap), then the two 8–9B models.
  - Metric: ratio and cw count vs the 4B's 0.440 / 11.
  - Speed is measured separately on desktop with `-t 4`, plus a no-repack phone probe when a 12 GB device exists.

## UNKNOWN

- Closed-book SimpleQA for every model here, including the baseline.
- Instruct-mode MMLU-Pro and GPQA for Ministral 3 and for Qwen3.5 in non-thinking mode.
- Whether AA's "Qwen3 4B 2507" Omniscience row is the Instruct or the Thinking variant.
- Knowledge cutoffs: Ministral 3, Qwen3.5, Granite 4.2.
- ARM no-repack prefill cost; the efficiency of DeltaNet, short-conv and Mamba layers on CPU.
- Effective bandwidth on a real Dimensity 8300/8400 or SD 7+/8s Gen 3: the 35–50% is an assumption.
- Nemotron Nano 9B v2's no-think switch.
- Nanbeige looped decode cost.
- LFM2.5-2.6B mode and benchmarks.

## Sources (all accessed 2026-10-03)

Model cards and vendor pages:
- Qwen3-4B-Instruct-2507 card (MMLU-Pro 69.6, GPQA 62.0, MMLU-ProX 61.6, INCLUDE 60.1, 36 layers / 8 KV): https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507
- Qwen3.5-9B card (MMLU-Pro 82.5, GPQA-D 81.7, multilingual table, architecture, enable_thinking): https://huggingface.co/Qwen/Qwen3.5-9B
- Qwen3.5-4B card (79.1 / 76.2, thinking mode is the default): https://huggingface.co/Qwen/Qwen3.5-4B
- Qwen3 Technical Report (Qwen3-8B/4B non-thinking GPQA-D 39.3/41.7, INCLUDE, MMMLU, base MMLU 72.99, ES/PT tables): https://arxiv.org/html/2505.09388v1
- Ministral 3 8B Instruct card (release, license, base TriviaQA table, Arena Hard, temp < 0.1): https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512
- Ministral 3 tech report (architecture, TriviaQA 68.1/63.9/53.0/59.2, MMLU, GPQA base, European MMLU): https://arxiv.org/html/2601.08584v1
- Gemma 4 E4B card (MMLU-Pro 69.4, GPQA-D 58.6, MMMLU 76.6; also the 12B column): https://huggingface.co/google/gemma-4-E4B-it
- Gemma 4 12B card (11.95B, 48 layers, 77.2 / 78.8 / 83.4): https://huggingface.co/google/gemma-4-12B-it
- Gemma 4 Technical Report (no SimpleQA/TriviaQA tables): https://arxiv.org/html/2607.02770v2
- Granite 4.2 8B card (2026-08-25, modes, 74.04 / 64.14, MMLU-ProX-lite 61.06): https://huggingface.co/ibm-granite/granite-4.2-8b
- Granite 4.1 8B card (SimpleQA 4.82, MMLU-Pro 55.99, GPQA 41.96, MMMLU 64.84, INCLUDE 58.89): https://huggingface.co/ibm-granite/granite-4.1-8b
- Llama 3.1 8B Instruct card (MMLU-Pro 48.3, GPQA 30.4, TriviaQA-Wiki 77.6, PT/ES MMLU): https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
- Olmo 3 7B Instruct card (PopQA 14.1 vs Qwen3-8B 20.4, GPQA 40.4, English): https://huggingface.co/allenai/Olmo-3-7B-Instruct
- SmolLM3-3B card (no_think GPQA 35.7, Global MMLU, PT/ES rows): https://huggingface.co/HuggingFaceTB/SmolLM3-3B
- Spark-X2.5 repo (2026-09-01, benchmark table, GPQA 67.4): https://github.com/XHToken/Spark-X2.5
- Nanbeige4.2-3B card (looped, EN/ZH, enable_thinking): https://huggingface.co/Nanbeige/Nanbeige4.2-3B
- FrogNano-4B-2609 card: https://huggingface.co/microsoft/FrogNano-4B-2609
- Apertus v1.5 8B card: https://huggingface.co/swiss-ai/Apertus-v1.5-8B
- EuroLLM-9B-Instruct-2512 card: https://huggingface.co/utter-project/EuroLLM-9B-Instruct-2512
- LFM2.5-8B-A1B blog (reasoning-only; AA-Omniscience table: LFM 8.67, Qwen3.5-4B 17.20, Gemma-4-E4B 8.10, Granite-H-Tiny 9.37): https://www.liquid.ai/blog/lfm2-5-8b-a1b

Independent evaluations and release trackers:
- Artificial Analysis, Qwen3.5 small models (2026-03-05): Qwen3.5-9B acc 14.7% / −56 / 82%; 4B 12.8% / −57 / 80%; "Qwen3 4B 2507: −61, 84%, 12.7%": https://artificialanalysis.ai/articles/qwen3-5-small-models
- Artificial Analysis, Gemma 4 (2026-04-06): Omniscience E4B −20, E2B −24: https://artificialanalysis.ai/articles/gemma-4-everything-you-need-to-know
- Artificial Analysis, Gemma 4 E4B vs Qwen3.5 9B (Intelligence Index non-reasoning 7 vs 13): https://artificialanalysis.ai/models/releases/comparisons/gemma-4-e4b-vs-qwen3-5-9b
- Artificial Analysis, Qwen3-4B-2507 Instruct page (Index 7, estimated): https://artificialanalysis.ai/models/qwen3-4b-2507-instruct
- Release trackers (no Qwen3.6/3.8 below 27B; Granite 4.2, LFM2.5 dates):
  - https://www.llm-releases.com/changelog
  - https://www.betterclaw.io/blog/gemma-4-vs-qwen-3-5
  - https://github.com/QwenLM/Qwen3.8

GGUF sizes and headers:
- HF API `https://huggingface.co/api/models/<repo>?blobs=true` for every repo named in the tables; GGUF headers via HTTP range on `…/resolve/main/<file>`. Parser: a range-request variant of `../../tools/gguf_sizes.py` (scratch script, not committed).

llama.cpp support:
- Merge commit → `git rev-list --count` in a treeless clone of ggml-org/llama.cpp, plus `merge-base --is-ancestor <sha> b11010`.
- Arch list at the tag: https://github.com/ggml-org/llama.cpp/blob/b11010/src/llama-arch.cpp
- Support PRs:

  | Arch | PR | Build |
  |---|---|---|
  | qwen3 | https://github.com/ggml-org/llama.cpp/pull/12828 | b5092 |
  | qwen35 | https://github.com/ggml-org/llama.cpp/pull/19468 | b7990 |
  | gemma4 | https://github.com/ggml-org/llama.cpp/pull/21309 | b8637 |
  | mistral3 | https://github.com/ggml-org/llama.cpp/pull/17644 | b7216 |
  | granite | https://github.com/ggml-org/llama.cpp/pull/9412 | b3774 |
  | granitehybrid | https://github.com/ggml-org/llama.cpp/pull/13550 | b5868 |
  | glm4 | https://github.com/ggml-org/llama.cpp/pull/12867 | b5115 |
  | nemotron_h | https://github.com/ggml-org/llama.cpp/pull/15507 | b6315 |
  | olmo3 | https://github.com/ggml-org/llama.cpp/pull/16015 | b6492 |
  | smollm3 | https://github.com/ggml-org/llama.cpp/pull/14581 | b5847 |
  | lfm2 | https://github.com/ggml-org/llama.cpp/pull/14620 | b5873 |
  | lfm2moe | https://github.com/ggml-org/llama.cpp/pull/16464 | b6709 |
  | LFM2.5 tokenizer | https://github.com/ggml-org/llama.cpp/pull/23826 | b9419 |
  | nanbeige | https://github.com/ggml-org/llama.cpp/pull/25994 | b10153 |
  | spark2_5 | https://github.com/ggml-org/llama.cpp/pull/27868 | b10828 |

In-repo:
- `../../cards/gemma4-e4b-reader-android.md`: BOAR Gemma result, forced thinking
- `../../cards/android-lowram-no-repack.md`: repack and the `no_extra_bufts` switch
- `README.md`: outofkit slice baseline 0.440 / cw 11; default-answer latency bar
- `../../../SHELF.md`: Ling, Maple, Qwen3.6-35B-A3B rows
