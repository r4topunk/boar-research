# PIXEL8-MODELS shortlist (2026-10-20)

TL;DR: 5 models ranked for a screen on BOAR's harness. Every one is Apache-2.0 except LFM2-2.6B (lfm1.0, $10M revenue threshold), and all have GGUFs on the Hub. Every architecture is in the llama.cpp vendored by llama.rn 0.13.0-rc.7 (the boar-app node_modules binaries contain the arch names gemma4, mistral3, smollm3, granitehybrid, lfm2, qwen35). No candidate is both clearly faster than the 4B and clearly as good at reading. The best bets are **Gemma 4 E2B-it** (fast enough on paper, strong knowledge for its size, Apache) and **Ministral 3 3B** (best world-knowledge evidence: TriviaQA above Qwen3-4B base, but it sits at the speed edge). Qwen3.5-2B is already being screened and is not re-proposed. Its numbers are in the table as the in-flight anchor.

Sources: HF Hub API (`/api/models/<id>`, `/tree/main`, `config.json`, README) fetched 2026-10-20; llama.cpp `src/models/*.cpp` via GitHub API; `boar-app/node_modules/llama.rn` (0.13.0-rc.7) binary strings. No weights downloaded.

## Estimation method (all numbers are estimates, none measured on the Pixel 8a)

- **RSS (Q4, 4k ctx)** = resident weights (GGUF size; for Gemma 4 the per-layer-embedding (PLE) table is mmapped and only partly touched, so a range is given) + f16 KV at 4096 tokens (computed from config.json) + 0.5 GB runtime/compute buffers + 0.6 GB app. The method gives 4.2 GB for Qwen3-4B, against a measured peak of 4.4 GB RSS. It gives 2.7 GB for Qwen3-1.7B.
- **Decode tok/s** = k / bytes read per token, with k fitted to the anchors. Qwen3-1.7B (1.11 GB × 12-16 tok/s) gives k ≈ 13-18 GB/s. Qwen3-4B (2.5 GB × 3.6-6 tok/s) gives k ≈ 9-15 GB/s. For files of 1.5-2.2 GB, k = 11-16 GB/s. MoE models read only their active experts per token.
- Gates: RSS ≤ ~4.0 GB, decode ≥ ~6 tok/s (product target 8), permissive licence, quality evidence above Qwen3-1.7B.

## Ranked shortlist

| # | Model (GGUF) | Licence (verified) | Q4_K_M file | KV f16 @4k | est. RSS | est. decode | Key quality evidence |
|---|---|---|---|---|---|---|---|
| 1 | google/gemma-4-E2B-it (unsloth/gemma-4-E2B-it-GGUF) | apache-2.0, not gated | 3.107 GB (Q3_K_M 2.537) | ~0.03 GB (15 own-KV layers, 1 KV head, SWA 512) | 2.9-4.2 GB (Q3_K_M 2.5-3.6) | 7.5-11 | Card: MMLU-Pro 60.0, GPQA-D 43.4 (thinking-family table; Qwen3-1.7B thinking 56.5 / 40.1) |
| 2 | mistralai/Ministral-3-3B-Instruct-2512 (unsloth/...-GGUF, text only, mmproj separate) | apache-2.0 | 2.146 GB | 0.44 GB (26 L × 8 KV × 128) | 3.7 GB (3.5 with q8_0 KV) | 5-7.5 | Base card: TriviaQA 5-shot 0.592 vs Qwen3-4B base 0.530, MMLU 0.707 vs 0.713. Instruct: Arena Hard 0.305, WildBench 56.8 (= Qwen3-VL-4B) |
| 3 | HuggingFaceTB/SmolLM3-3B (bartowski/HuggingFaceTB_SmolLM3-3B-GGUF) | apache-2.0 | 1.915 GB | 0.30 GB (36 L × 4 KV × 128) | 3.3 GB | 5.7-8.3 | Card, no-think: GPQA-D 35.7 vs Qwen3-1.7B 31.8, IFEval 76.7 vs 74.0, Global MMLU 53.5 vs 49.5 |
| 4 | ibm-granite/granite-4.0-micro (bartowski/ibm-granite_granite-4.0-micro-GGUF) | apache-2.0 | 2.100 GB | 0.34 GB (40 L × 8 KV × 64, dense attention) | 3.5 GB | 5.2-7.6 | Card: MMLU 66.0, MMLU-Pro 44.5 (5-shot CoT), GPQA 30.1, IFEval avg 82.3 |
| 5 | LiquidAI/LFM2-2.6B (LiquidAI/LFM2-2.6B-GGUF, official) | lfm1.0: Apache-style, but Commercial Use is licensed only below $10M annual revenue (Section 5) | 1.564 GB | 0.07 GB (8 attention of 30 layers) | 2.7 GB | 7-11 (conv layers are cheap; the vendor's "2x vs Qwen3" is uncited) | Card, non-think: MMLU 64.4, IFEval 79.6, GPQA 26.6 (Qwen3-4B-2507: 72.3 / 85.6 / 34.9) |
| ref | Qwen/Qwen3.5-2B (unsloth) | apache-2.0 | 1.281 GB | 0.05 GB (6 full-attn of 24 layers, 2 KV × 256) | 2.4 GB | 8.5-12.5 | Already in screen; card no-think MMLU-Pro 55.3 vs 40.2 |

The KV figures confirm one thing. Hybrid and SWA models (Gemma 4 E2B, LFM2, Qwen3.5) keep KV near zero. Dense GQA models in the 3B class spend 0.3-0.45 GB on KV at 4k, which can be halved with `cache_type_k/v = q8_0`.

## Per-candidate notes

### 1. Gemma 4 E2B-it
- **Why:** it has an Apache licence, which Gemma 3/3n did not. PLE gives about 2.3B effective params per token. The Gemma line has strong factual recall per size. Thinking is optional, and on E2B/E4B with thinking off the model emits no empty thought block.
- **Risk:** the 3.1 GB file is the largest here. How much of the PLE table (35 × 256 × 262k ≈ 2.35B params) Android counts in RSS/PSS once mmapped is unknown, and on the 8a that decides between 2.9 and 4.2 GB. The MMLU-Pro 60.0 is probably a thinking number, and the non-thinking value is not in the card. Arch support arrived in llama.cpp 2026-05-04 (gemma4.cpp), and the string is present in llama.rn rc.7.
- **Onboarding:** Gemma 4 template with standard system/user/assistant roles. Thinking is ON only if `<|think|>` opens the system prompt, so the screen leaves it out. Vendor sampling is temp 1.0, top_p 0.95, top_k 64. Also run the engine sampler (0.7/40/0.95/0.05) as a second arm, because temp 1.0 is risky for short cited answers. Strip previous thoughts from history. Use Q3_K_M as the RSS fallback.

### 2. Ministral 3 3B Instruct 2512
- **Why:** this is the only candidate with a world-knowledge benchmark that beats Qwen3-4B. Base TriviaQA is 59.2 vs 53.0, which matters because the CE taxonomy shows most 1.7B errors are missing knowledge. The context is 256k.
- **Risk:** the estimated speed of 5-7.5 tok/s sits on the gate. It is about 1.4-1.7× the 4B but slower than the 1.7B. The GGUF is community-built (unsloth/bartowski). The instruct card publishes no IFEval, MMLU-Pro or SimpleQA. Arena Hard 0.305 is mid.
- **Onboarding:** Mistral v7-style template from the GGUF, with no thinking mode in the Instruct variant. The vendor recommends temperature ≤ 0.1, so add a greedy/0.1 arm next to the engine sampler. Do not load mmproj.

### 3. SmolLM3-3B
- **Why:** fully open data and recipe, strong non-thinking IFEval, a modest knowledge step over the 1.7B, and the smallest file of the 3B class. One LiteRT-LM data point exists: decode 11.5 tok/s CPU on a 2026 Galaxy S26, peak 3.12 GB (different runtime and a faster SoC).
- **Risk:** the knowledge gain is small. The LFM2 card places it at MMLU 59.8, below LFM2. Speed is borderline.
- **Onboarding:** ChatML-style template. Thinking is ON by default, so pass `enable_thinking=false` or put `/no_think` in the system prompt, and check that the GGUF template honours the kwarg. Vendor sampling is temp 0.6, top_p 0.95.

### 4. Granite 4.0 micro
- **Why:** a dense transformer (not the Mamba hybrid), with the highest instruction-following of the set (IFEval 82) and MMLU-Pro 44.5. IBM positions Granite 4 for RAG/enterprise use, though that is not verified on its card.
- **Risk:** 40 layers × 2560 hidden with head_dim 64 make it the slowest per byte, at 5.2-7.6 tok/s. It is weak on GPQA. The card compares it only with other Granite models.
- **Onboarding:** Granite 4 template from the GGUF, no thinking mode. Granite has a documents/citations system-prompt convention, so try BOAR's prompt first. The card gives no vendor sampling, so use the engine sampler.

### 5. LFM2-2.6B
- **Why:** it is the fastest and lightest candidate (2.7 GB RSS) and leaves room for a 4k+ context. IFEval 79.6 is above the 1.7B. The official GGUF comes from LiquidAI.
- **Risk:** the licence is not OSI. It allows redistribution with notices, but commercial use is licensed only under $10M revenue. r4to/the app maintainer need to accept this. Knowledge is at parity with the 1.7B (MMLU 64), so this tests reading and format, not knowledge. It uses "dynamic hybrid reasoning" (`<think>` traces on complex prompts), so suppression must be checked.
- **Onboarding:** ChatML-like LFM2 template. Vendor sampling is temp 0.3, min_p 0.15, repetition_penalty 1.05. Strip any `<think>` block.

## Screen plan (all candidates, same stages)

0. **Desktop speed proxy (mini, 0 judge calls):** `llama-bench -t 4 -p 512 -n 128` per GGUF next to Qwen3-1.7B and Qwen3-4B Q4_K_M on the mini. Drop any model whose tg ratio to the 1.7B projects below 6 tok/s on the 8a (projection = 12-16 × ratio). Expected to settle the edge cases for #2-#4.
1. **Stage 1, LP-SCREENS K0/K1 (mini, 27 problems + 10 sentinels, Haiku 5.5-low N4 both orders):** each candidate as a model-swap arm against the mini control. Freeze the criterion (sha256) before generation. Count fixed confident errors under refuse-by-default (per REREAD 2026-10-20) and keep the same "need 6" bar as the other screens. Sentinels must not regress, format-break count is ≤ 1.7B's, and the decline share is reported.
2. **Stage 2, kit read-off (winners only):** the identical-context reading kit (n 97 / claim kit) vs 1.7B and 4B, Opus L2. The target is at least half of the 4B-over-1.7B reading gap (+0.055 of +0.11).
3. **Stage 3, Pixel 8a device (winner only):** bench-app s16 subset with fast-iteration A/B (about 6 min per model). Gate: PSS peak ≤ 4.0 GB, decode ≥ 8 tok/s (≥ 6 hard floor), no LMK kill over 16 items. Gemma 4 E2B runs Q4_K_M and Q3_K_M here because of the PLE RSS question.
4. Log each exposure in EXPOSURES.md and one QUEUE row per stage.

## Rejected / not shortlisted

| Model | Reason |
|---|---|
| Qwen3.5-2B | Already being screened (in flight); not a new proposal. Use it as the anchor above |
| Qwen3.5-4B | 4.66B dense, 2.74 GB; decode ≈ 4-6 tok/s, the same class as the measured Qwen3-4B that failed the speed gate and had an LMK kill |
| Phi-4-mini-instruct | MIT, but 2.49 GB plus a 200k-vocab tied head gives an estimated 4.4-6.4 tok/s, and the 0.54 GB KV pushes RSS to ~4.1 GB. GPQA 25 |
| Phi-4-mini-flash-reasoning | Reasoning-only model with a non-standard arch, and no GGUF verified. Not a short-answer model |
| Gemma 4 E4B-it | Q4_K_M 4.98 GB, over the RSS budget. Phone decode for the E4B class is 5-9 tok/s (Gemma 3n E4B rows) |
| Gemma 3n E2B-it | Gemma Terms (gated), and Gemma 4 E2B under Apache supersedes it |
| Gemma 3 4B IT / Gemma 3 1B / Gemma-2-2B | Gemma Terms. Gemma 3 4B is weak on MMLU-Pro (29) and slow. The 1B/2B have no evidence above the 1.7B |
| Llama 3.2 3B Instruct | Llama 3.2 Community Licence (attribution, AUP, 700M MAU), and MMLU-Pro 39.2 ≈ Qwen3-1.7B |
| Falcon-H1-3B-Instruct | Falcon-LLM licence ties use to a TII Acceptable Use Policy that "may be updated from time to time", which is a mutable restriction. The card does not state the eval mode. Parked: reopen only if r4to accepts the licence |
| Falcon-H1-1.5B-Deep | Same licence, 1.5B class, no GGUF verified |
| EXAONE 4.0 1.2B | Non-commercial licence |
| SmallThinker-4BA0.6B-Instruct | Apache, and arch present in mainline llama.cpp and llama.rn rc.7. Fast (est. 15-25 tok/s), but the RSS of ~3.9 GB is above the 1.7B's with only on-paper parity in its own card (MMLU 66.1 vs 64.2, IFEval 69.7 vs 69.5). No quality case. Reopen as a speed-only fallback if the 1.7B is ever too slow |
| granite-4.0-h-tiny | 6.94B total MoE: IQ4_XS 3.79 GB, so RSS ≈ 4.9 GB. IBM notes Mamba2 llama.cpp kernels may lag |
| granite-4.0-h-1b | 1.46B class, no GGUF checked, no evidence above the 1.7B |
| OLMoE-1B-7B-0924-Instruct | Q4_K_M 4.21 GB, and a 2024 model below the Qwen3 class |
| bitnet-b1.58-2B-4T | I2_S needs bitnet.cpp, and MMLU 53 is below Qwen2.5-1.5B |
| Phi-tiny-MoE-instruct | No GGUF, and quality was not published in the pool |

## UNKNOWN

- How Android accounts for mmapped PLE pages (Gemma 4 E2B) in RSS/PSS. Only stage 3 can tell.
- All decode figures are bandwidth projections, with no Tensor G3 measurement for any candidate. Hybrid/conv kernels (LFM2, Qwen3.5 DeltaNet) may run faster or slower on ARM CPU than the dense projection.
- No candidate publishes SimpleQA or a RAG-faithfulness number, so knowledge evidence comes only from MMLU/TriviaQA-type proxies.
- The app maintainer's native app has its own llama.cpp build. Its arch support (gemma4 is 2026-05+) must be checked before any recommendation reaches him.
