# Open-weight model landscape for BOAR, Oct 2026: closed-book knowledge vs phone fit

Date: 2026-10-06. Scope: open-weight GGUF models for an offline Android reader (llama.cpp / llama.rn 0.13, ARM CPU). Team phone: Pixel 8a (Tensor G3, 8 GB, ~5.5 GiB usable); bounty allows 12 GB phones.
Read before this file: `rnd/research/anvil/RADAR.md`, `cards/deep-tier-streamed-moe.md`, `cards/maple-20b-a1b-fast-reader.md`, `exp/outofkit/models.md`. Nothing here was re-run. All numbers come from the web sources cited on each row.

## TL;DR

1. **No published SimpleQA exists for almost any candidate.** The usable common proxy is **AA-Omniscience accuracy** (Artificial Analysis, mirrored by benchlm.ai, updated 2026-10-06). On that scale the baseline Qwen3-4B-2507 scores **12.7%**, and no ≤ 5 GB model beats it. **The fast tier stays Qwen3-4B-Instruct-2507.**
2. Streamable 25–35B MoE models sit at **19–20%**: Qwen3.5-35B-A3B 20.1, Gemma 4 26B-A4B 19.1, Qwen3.6-35B-A3B 18.8. **Qwen3.6-35B-A3B is not the best of its class on knowledge.** Qwen3.5-35B-A3B (same `qwen35moe` arch, so a drop-in) and Gemma 4 26B-A4B (smaller file, better streaming locality) are at least equal on this proxy.
3. The best knowledge at ≤ 30B is **Muse Glimmer 30B (Meta, dense, Apache-2.0, 2026-08-10): 27.0%**. It is dense, so every token reads ~10.7 GB even at IQ2_XXS. Not phone-viable; at most a desktop ceiling probe.
4. **The only middle-ground candidate for an 8 GB phone is Gemma 4 12B (dense):** AA 15.6% at full precision, and its 3-bit GGUFs are ~4.65 GB. Whether the knowledge survives 2–3-bit quantization is UNKNOWN. Allen-Zhu finds int4 already cuts stored knowledge from 2 to 0.7 bit/param.
5. **MoE on phones** = expert streaming (BigMoeOnEdge: 5.0–5.8 tok/s for 26–35B MoE at Q4_K_M on a 12 GB Snapdragon phone). Stock llama.cpp mmap thrashes. Upstream JIT expert streaming is an open feature request (#27562). An 8 GB phone remains out for 30B-A3B: Kiln's peak was 6.59 GiB, over the Pixel 8a's ~5.5 GiB.

## How to read the knowledge column

- **AA acc** = AA-Omniscience accuracy (% correct on 6,000 hard closed-book questions), from [benchlm.ai mirror of Artificial Analysis](https://benchlm.ai/benchmarks/omniscienceaccuracy), "last updated October 6, 2026". The mirror **does not say whether each row is the reasoning or the non-reasoning variant**. Treat ±2 pp as noise between modes.
- **halluc** = AA-Omniscience hallucination rate (wrong answers ÷ (wrong + abstain)), from the [benchlm.ai mirror](https://benchlm.ai/benchmarks/omnisciencehallucinationrate).
- **AA index** = correct % − incorrect %, from artificialanalysis.ai pages. A derived bound: accuracy ≤ (100 + index) / 2.
- **Baseline anchor:** Qwen3-4B-2507 AA acc 12.7%, halluc 84%, index −61 (team file `exp/outofkit/models.md`). AA's comparison page shows index **−62** ([AA](https://artificialanalysis.ai/models/comparisons/qwen3-30b-a3b-2507-vs-qwen3-4b-2507-instruct)). On BOAR: closed-book the post author-style 0.41, Haiku 4.5 no-web 0.59.
- GGUF sizes come from the HF API tree listing (unsloth unless noted), fetched 2026-10-06, in GB (10^9 bytes).

## (a) Fast tier: ≤ 5 GB resident (fits the 8 GB Pixel 8a without streaming)

Ranked by AA acc. Every model below the baseline has already been screened or loses on the proxy.

| # | Model | Total / active | GGUF Q4 / lowest usable | Knowledge (AA acc; halluc) + other | Reported ARM tok/s | License | Source |
|---|---|---|---|---|---|---|---|
| 1 | **Qwen3-4B-Instruct-2507** (baseline) | 4.0B dense | Q4_K_M 2.50 | **12.7%**; 84%; MMLU-Pro 69.6, GPQA 62.0, IFEval 83.4, Arena-Hard v2 43.4; SimpleQA not published | team: 8.4–15.5 est. (12 GB) | Apache-2.0 | [HF card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) · [AA](https://artificialanalysis.ai/models/comparisons/qwen3-30b-a3b-2507-vs-qwen3-4b-2507-instruct) |
| 2 | Qwen3.5-4B (screened: worse) | 4.2B dense | Q4_K_M 2.74 | 12.8% (reasoning; team file) | not found | Apache-2.0 | [unsloth GGUF](https://huggingface.co/unsloth/Qwen3.5-4B-GGUF) |
| 3 | LFM2.5-8B-A1B | 8.3B / ~1.5B MoE | LFM2-8B-A1B Q4_K_M 5.04 / Q4_0 4.73 (LFM2.5 sizes not fetched) | 9.4%; 46.9% | not found on phone; 13.8 tok/s on a 4-thread laptop CPU (Q4_0) | LFM Open License ("other") | [benchlm](https://benchlm.ai/benchmarks/omniscienceaccuracy) · [LFM2 GGUF](https://huggingface.co/LiquidAI/LFM2-8B-A1B-GGUF) |
| 4 | Granite 4.2 3B | 3.7B dense | Q4_K_M 2.24 | 9.2% | not found | Apache-2.0 | [benchlm](https://benchlm.ai/benchmarks/omniscienceaccuracy) |
| 5 | Gemma 4 E4B (screened: worse) | 7.5B in file / 4.6B matmul | QAT Q4_0 5.15 | 8.6%; 30.9% | not found | Apache-2.0 | [benchlm](https://benchlm.ai/benchmarks/omniscienceaccuracy) |
| 6 | Ling 3.0 Tiny (screened: killed) | MoE | — | 8.5%; 30.5% | — | — | [benchlm](https://benchlm.ai/benchmarks/omniscienceaccuracy) |
| 7 | MiniCPM5-2B | 2.6B | — | 8.4% | — | — | [benchlm](https://benchlm.ai/benchmarks/omniscienceaccuracy) |
| 8 | Granite 4.0 H-Tiny | 7B / 1B MoE (hybrid Mamba) | Q4_K_M 4.25 / UD-IQ2_XXS 2.39 | not in AA list (Granite-4.0-H-1B: 5.2%) | not found | Apache-2.0 | [unsloth GGUF](https://huggingface.co/unsloth/granite-4.0-h-tiny-GGUF) |
| 9 | K2 Horizon 3.7B (IFM/MBZUAI, Sep 2026) | 3.7B dense | Q4_K_M 3.16 | not in AA list; MMLU-Pro 59.3 (vs 69.6), GPQA-D 65.4; reasoning-tuned | not found; llama.cpp support only via issue #29424 → PR #29535 (merged, date UNKNOWN), so likely not in llama.rn 0.13 | Apache-2.0 | [HF GGUF](https://huggingface.co/IFM/K2-Horizon-3.7B-GGUF) · [issue](https://github.com/ggml-org/llama.cpp/issues/29424) |
| 10 | LFM2.5-2.6B | 2.7B | Q4_K_M 1.67 | 4.4% | — | LFM Open License | [benchlm](https://benchlm.ai/benchmarks/omniscienceaccuracy) |

**Verdict (a):** Qwen3-4B-Instruct-2507 is still the best ≤ 5 GB model on the only cross-vendor closed-book proxy, and it is non-thinking by design. Every 2026 small model is reasoning- or agent-tuned and scores ≤ 12.8% on knowledge.

## (b) Deep tier: 8–13 GB on-disk MoE for 12 GB phones (expert streaming)

Ranked by AA acc.

| # | Model | Total / active | GGUF Q4_K_M / lowest usable (GB) | Knowledge (AA acc; halluc) + other | Reported ARM tok/s | License | Source |
|---|---|---|---|---|---|---|---|
| 1 | **Qwen3.5-35B-A3B** (2026-02) | 35B / 3B (same `qwen35moe` arch as 3.6) | 22.02 / **UD-Q2_K_XL 12.16**, UD-IQ2_XXS 10.66 | **20.1%**; 85.4%. AA index (reasoning) −48. MMLU-Pro 85.3, SuperGPQA 63.4 (thinking default) | not published for 3.5; expect ≈ 3.6 (same arch) | Apache-2.0 | [HF card](https://huggingface.co/Qwen/Qwen3.5-35B-A3B) · [GGUF](https://huggingface.co/unsloth/Qwen3.5-35B-A3B-GGUF) · [benchlm](https://benchlm.ai/benchmarks/omniscienceaccuracy) |
| 2 | **Gemma 4 26B-A4B** | 25.2B / 3.8B | 16.95 / **UD-Q2_K_XL 10.55**, UD-IQ2_XXS 9.92 | **19.1%**; 86.4%. MMLU-Pro 82.6, GPQA-D 82.3 | **5.0 tok/s** (Q4_K_M, k = 6 "turbo", 4000 MB cache, 12 GB Snapdragon phone, BigMoeOnEdge); flash read 98 MiB/token, 83% cache hit | Apache-2.0 | [BigMoeOnEdge](https://github.com/Helldez/BigMoeOnEdge) · [GGUF](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF) · [datalearner](https://www.datalearner.com/en/ai-models/pretrained-models/gemma-4-26b-a4b) |
| 3 | Qwen3.6-35B-A3B (current deep tier) | 35B / 3B | 22.3 / UD-Q2_K_XL 12.29 | 18.8%; 50.5% (mirror row; probably the reasoning variant). AA non-reasoning index **−60** (acc ≤ 20%) | **5.8 tok/s** Q4_K_M (BigMoeOnEdge, 12 GB phone); CPU prefill 1,418 tok in 80.6 s (≈ 17.6 tok/s), NPU 10.0 s; a competitor team 4–6 tok/s Q2_K_XL on a Pixel 8 Pro (team card) | Apache-2.0 | [HF card](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) · [BigMoeOnEdge v0.26.0](https://github.com/Helldez/BigMoeOnEdge/releases/tag/v0.26.0) |
| 4 | Nemotron 3 Nano 30B-A3B (2025-12-15) | 30B / 3.5B (hybrid Mamba-2 + MoE, 6 of 128 experts) | 24.57 / smallest found **UD-IQ2_XXS 18.11** (no ≤ 13 GB file) | 17.3%; 83.3%. MMLU-Pro 78.3, GPQA 73.0 (reasoning on) | not found (BigMoeOnEdge lists `nemotron_h_moe`) | NVIDIA Open Model License | [HF card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16) · [GGUF](https://huggingface.co/unsloth/Nemotron-3-Nano-30B-A3B-GGUF) |
| 5 | gpt-oss-20b | 21B / 3.6B | 11.62 / 11.47 (Q2_K ≈ Q4: experts are MXFP4) | 16.0%; 94.1%. **Model-card SimpleQA 6.7%, halluc 91.4%**. Always reasons (harmony format) | 2–3 tok/s, Snapdragon 8 Elite, 24 GB ROG Phone 9 Pro, Ollama (2025-08-07) | Apache-2.0 | [model card arXiv 2508.10925](https://arxiv.org/pdf/2508.10925) · [Android Authority](https://www.androidauthority.com/i-installed-gpt-oss-on-my-phone-3584439/) |
| 6 | Qwen3-30B-A3B-Instruct-2507 | 30.5B / 3.3B | 18.56 / UD-Q2_K_XL 11.79, UD-IQ2_XXS 10.34 | AA acc **not public**; AA index **−66** (vs 4B's −62), so acc ≤ 17% and more confident errors. MMLU-Pro 78.4, GPQA 70.4, IFEval 84.7, Arena-Hard v2 69.0. **Non-thinking by design** | **5.2 tok/s** Q4_K_M (BigMoeOnEdge, 12 GB phone, "best production recipe"; 225 MiB/token flash, 76% hit). PowerInfer, in memory (Q4_0), OnePlus 13: 20.18 tok/s | Apache-2.0 | [HF card](https://huggingface.co/Qwen/Qwen3-30B-A3B-Instruct-2507) · [AA](https://artificialanalysis.ai/models/comparisons/qwen3-30b-a3b-2507-vs-qwen3-4b-2507-instruct) · [SmallThinker paper](https://arxiv.org/html/2507.20984) |
| 7 | GLM-4.7-Flash (2026-01-19) | 30B / 3B | 18.31 / UD-Q2_K_XL 11.89, UD-IQ2_XXS 10.51 | AA acc not found. GPQA 75.2, HLE 14.4 (thinking) | not found | MIT | [HF card](https://huggingface.co/zai-org/GLM-4.7-Flash) · [GGUF](https://huggingface.co/unsloth/GLM-4.7-Flash-GGUF) |
| 8 | ERNIE-4.5-21B-A3B | 21B / 3B | 13.33 / UD-Q2_K_XL 8.22, UD-IQ2_XXS 7.76 | Vendor SimpleQA **24.2, disputed**: an HF user's spot test gave ~3, suspecting contamination. AA not found | not found | Apache-2.0 | [HF discussion](https://huggingface.co/baidu/ERNIE-4.5-21B-A3B-PT/discussions/1) · [GGUF](https://huggingface.co/unsloth/ERNIE-4.5-21B-A3B-PT-GGUF) |
| 9 | SmallThinker-21B-A3B (2025-07) | 21B / 3B (ReGLU, built for offload) | Q4_0 ≈ 11.5 GB resident (card); file list not fetched | AA not found. MMLU 84.4 vs Qwen3-30B-A3B 85.1; GPQA-D 55.1 | **PowerInfer:** 23.03 tok/s in memory and **15.50 tok/s under an 8 GB cap** (OnePlus 13). llama.cpp has the arch (#14898), but the speed claims need PowerInfer | Apache-2.0 | [SmallThinker paper](https://arxiv.org/html/2507.20984) · [HF card](https://huggingface.co/PowerInfer/SmallThinker-21BA3B-Instruct) |
| 10 | LFM2-24B-A2B (2026-02-24) | 24B / 2B | 14.42 / Q4_0 13.47 (no Q2 published) | AA not found; MMLU-Pro 44.35, GPQA 38.89 (weak) | not found | LFM Open License | [Liquid blog](https://liquid.ai/blog/lfm2-24b-a2b) · [GGUF](https://huggingface.co/LiquidAI/LFM2-24B-A2B-GGUF) |
| 11 | Granite 4.0 H-Small | 32B / 9B | 19.57 / UD-Q2_K_XL 12.38 | AA: Granite 4.2 30B 10.1% (family low); 9B active means slow decode | not found | Apache-2.0 | [GGUF](https://huggingface.co/unsloth/granite-4.0-h-small-GGUF) · [benchlm](https://benchlm.ai/benchmarks/omniscienceaccuracy) |
| 12 | K2 Horizon MoVA 36B-A4B (2026-09-03) | 37.4B / 5.95B incl. embeddings | GGUF sizes not fetched | AA acc not public; Intelligence Index 25 (reasoning) | not found; llama.cpp PR #29535 merged (date UNKNOWN), so not in llama.rn 0.13 | Apache-2.0 | [AA](https://artificialanalysis.ai/models/k2-horizon-mova-36b-a4b) · [issue](https://github.com/ggml-org/llama.cpp/issues/29424) |
| — | *Out of class:* **Muse Glimmer 30B** (Meta, 2026-08-10) | **~29.6B dense** (+1.8B vision) | UD-Q4_K_XL 15.9 / UD-IQ2_XXS 10.7 | **27.0%**; 81.9%. Best knowledge ≤ 30B. MMLU-Pro 74, GPQA-D 83.5; knowledge cutoff 2026-01-04 | none for phones. Dense: ~10.7 GB read per token, so ≤ ~2–3.5 tok/s even fully resident (team bandwidth formula); expert streaming does not apply | Apache-2.0 | [unsloth GGUF](https://huggingface.co/unsloth/Muse-Glimmer-30B-GGUF) · [HF blog](https://huggingface.co/blog/muse-glimmer) |
| — | *Out (> 50 GB or too slow):* Ling 3.0 Flash 18.2%, GLM-4.5-Air 16.3%, Llama 4 Scout 15.2%, Mistral Small 4 21.7%, Qwen3.5-122B-A10B 24.4% | ≥ 100B | — | — | — | — | [benchlm](https://benchlm.ai/benchmarks/omniscienceaccuracy) |

**Verdict (b):** at the deep-tier size, Qwen3.6-35B-A3B is a reasonable but not dominant pick. On knowledge alone, Qwen3.5-35B-A3B (+1.3 pp) and Gemma 4 26B-A4B (+0.3 pp, ~1.7 GB smaller, lower flash read per token) are equal or better. Mode labels on the mirror are unclear, so all three are within noise until screened. Avoid gpt-oss-20b: SimpleQA 6.7% and 91–94% hallucination.

## (c) In between: fits an 8 GB phone (≤ ~5 GiB resident, or mmap/streaming)

| # | Model | Total / active | GGUF Q4 / lowest usable (GB) | Knowledge | Reported or estimated ARM tok/s | License | Source |
|---|---|---|---|---|---|---|---|
| 1 | **Gemma 4 12B** (dense, 2026-06) | 11.9B dense | Q4_K_M 7.12, QAT Q4_0 6.98 / **UD-Q2_K_XL 4.66, UD-IQ3_XXS 4.64**, UD-IQ2_M 4.21 | **15.6%**; 81.0% (full precision). MMLU-Pro 77.2, GPQA-D 78.8 (team file) | not found. Estimate ≈ 4.5–8 tok/s at 4.65 GB (team formula: 21–38.5 GB/s ÷ bytes read) | Apache-2.0 | [GGUF](https://huggingface.co/unsloth/gemma-4-12b-it-GGUF) · [benchlm](https://benchlm.ai/benchmarks/omniscienceaccuracy) |
| 2 | Phi-4 (14B, 2024-12) | 14.7B dense | sizes not fetched | 14.1%; 81.2% | not found | MIT | [HF](https://huggingface.co/microsoft/phi-4) · [benchlm](https://benchlm.ai/benchmarks/omniscienceaccuracy) |
| 3 | Ministral 3 14B Instruct 2512 | ~14B dense | Q4_K_M 8.24 / UD-IQ3_XXS 5.49, UD-IQ2_M 4.91 | AA not found. Base TriviaQA 74.9 (8B: 68.1; Qwen3-4B-Base 53.0). **But the 8B lost on BOAR despite +15 TriviaQA**, so this is a weak predictor | not found | Apache-2.0 | [GGUF](https://huggingface.co/unsloth/Ministral-3-14B-Instruct-2512-GGUF) · [datalearner](https://www.datalearner.com/en/ai-models/pretrained-models/ministral-3-14b-25-12) |
| 4 | Ling-mini-2.0 (2025-09) | 16B / 1.4B | Q4_K_M 9.94 / IQ2_M 5.28, Q2_K 5.84 (bartowski) | AA not found. Same lab as Ling-3.0-tiny (8.5%, lost on BOAR) | not found; vendor 300+ tok/s on H20 | MIT | [HF](https://huggingface.co/inclusionAI/Ling-mini-2.0) · [GGUF](https://huggingface.co/bartowski/inclusionAI_Ling-mini-2.0-GGUF) |
| 5 | ERNIE-4.5-21B-A3B at ≤ 2 bits | 21B / 3B | UD-IQ1_M 7.24 / UD-IQ2_XXS 7.76 | see (b): SimpleQA claim disputed | not found; on 8 GB this needs mmap paging | Apache-2.0 | [GGUF](https://huggingface.co/unsloth/ERNIE-4.5-21B-A3B-PT-GGUF) |
| 6 | SmallThinker-21B-A3B + PowerInfer | 21B / 3B | Q4_0 | AA not found; MMLU 84.4 | **15.50 tok/s at an 8 GB cap on a OnePlus 13**, but only with the PowerInfer runtime | Apache-2.0 | [paper](https://arxiv.org/html/2507.20984) |
| 7 | 30–35B-A3B streamed on 8 GB | — | — | — | **Fails:** Kiln P0 peak 6.59 GiB vs ~5.5 GiB usable on the Pixel 8a (team card). A search snippet put stock llama.cpp Qwen3-30B-A3B at 0.18 tok/s under an 8 GB cap on a phone (not confirmed in fetched text). The paper's PC figure under an 8 GB cap is 10.11 tok/s | — | team `deep-tier-streamed-moe.md` · [paper](https://arxiv.org/html/2507.20984) |

**Verdict (c):** on an 8 GB phone the realistic lever is a **dense 12B at ~3 bits** (Gemma 4 12B). Streamed MoE does not fit the Pixel 8a's budget without bounded prefill (ADR T2). LFM2.5-8B-A1B and Granite are below the 4B on knowledge.

## Why the gap: total params store knowledge, active params set speed

- **Factual knowledge scales with total stored parameters, not with the parameters used per token.**
  - Allen-Zhu & Li find LMs store ~**2 bits of knowledge per parameter**.
  - **MoE with 32 experts loses only ~1.3× capacity** versus dense, while using a fraction of the parameters per token.
  - **int8 keeps the capacity; int4 drops it to ~0.7 bit/param** ([Physics of LMs 3.3, arXiv 2404.05405](https://huggingface.co/papers/2404.05405.md)).
- Jelassi et al. show that adding experts at fixed active parameters **keeps improving memorization while reasoning saturates** ([Mixture of Parrots, arXiv 2410.19034, ICLR 2025](https://arxiv.org/abs/2410.19034)).
- So a 35B-A3B model holds roughly 6–8× the 4B's fact capacity but decodes at a ~3B model's cost: per-token bytes come from the active experts only.
- AA's own paper finds "a clear positive association between model size and factual accuracy". Hallucination rate does not fall with size, which depends on post-training ([AA-Omniscience, arXiv 2511.13029 §3.4](https://arxiv.org/pdf/2511.13029)).
- The AA numbers fit this picture:
  - 4B dense: 12.7%;
  - 26–35B MoE: 18.8–20.1%;
  - 30B dense (Muse Glimmer): 27.0%, consistent with dense > MoE at equal total size;
  - 2026 RL-heavy refreshes can lose knowledge (Qwen3.5-27B 20.7% → Qwen3.8-27B 15.6%).
- Caveat for BOAR: the deep tier runs at 2-bit, where the Allen-Zhu result predicts more knowledge loss than at Q4. The team's +0.06 desktop gain was measured at Q2_K_XL, so the effect survives, but it is probably smaller than at Q4.

## Phone feasibility of MoE in llama.cpp (Q4)

| Mechanism | State (Oct 2026) | Numbers | Source |
|---|---|---|---|
| Stock llama.cpp mmap (default) | Works, but no expert awareness: pages fault through the OS | 93 GB model on 12 GB VRAM + 30 GB RAM: 1.18 tok/s generation (2026-08); team/ADR: 0.1–2 tok/s and unstable on a phone | [discussion #19163](https://github.com/ggml-org/llama.cpp/discussions/19163) |
| `--cpu-moe` / `--n-cpu-moe N` / `-ot` | GPU↔CPU tensor placement only, irrelevant on a CPU-only phone. The `--load-mode` refactor (#20834) removed the `--no-mmap --mlock` combo; bug #26110 (2026-07-25) is open, fix PR #26135 linked | 7.55 vs 25–27 tok/s on a desktop when the CPU-resident experts swap | [issue #26110](https://github.com/ggml-org/llama.cpp/issues/26110) |
| Upstream JIT expert streaming | **Feature request only** (#27562, 2026-08-22, open; cites BigMoeOnEdge) | — | [issue #27562](https://github.com/ggml-org/llama.cpp/issues/27562) |
| **BigMoeOnEdge** (on llama.cpp's public API, Apache-2.0) | v0.26.0 (2026-09-28) adds Hexagon NPU prefill (SD 8 Gen 2+; **no Q2/Q3 experts on the NPU**) | 12 GB phone (11.3 GB usable, UFS 4): Qwen3.6-35B-A3B Q4_K_M **5.8**, Qwen3-30B-A3B **5.2**, Gemma 4 26B-A4B **5.0** (k = 6), gpt-oss-120b 2.2 tok/s. CPU prefill ≈ 17.6 tok/s (1,418 tok / 80.6 s). Supported archs: qwen3moe, qwen35moe, gemma4, gpt-oss, nemotron_h_moe, lfm2moe, deepseek4, bailingmoe3 | [repo](https://github.com/Helldez/BigMoeOnEdge) · [v0.26.0](https://github.com/Helldez/BigMoeOnEdge/releases/tag/v0.26.0) |
| PowerInfer / SmallThinker (model co-designed for offload) | Separate runtime, not llama.rn | OnePlus 13: SmallThinker-21B-A3B 23.03 tok/s in memory, **15.50 at an 8 GB cap**; Qwen3-30B-A3B 20.18 in memory. PC at an 8 GB cap: SmallThinker 20.30 vs Qwen3-30B-A3B 10.11 | [arXiv 2507.20984](https://arxiv.org/html/2507.20984) |
| Tensor G3 / Pixel 8a specifically | **No published MoE numbers found.** Tensor G3 has no Hexagon NPU, so BigMoeOnEdge's NPU prefill does not apply | — | — |
| Dimensity 9300 / SD 8 Gen 3 with a 20–35B MoE | **Not found** | — | — |

## Shortlist for a closed-book screen on the team harness (≤ 4)

| # | Candidate (file) | Why | Kill rule hint |
|---|---|---|---|
| 1 | **Qwen3.5-35B-A3B UD-Q2_K_XL** (12.16 GB) | Highest AA acc among streamable MoE (20.1 vs 3.6's 18.8). Same `qwen35moe` arch, template family and file size as the current deep tier, so zero engine work. Run `enable_thinking: false` | Δ vs Qwen3.6 deep < MDE: keep 3.6 |
| 2 | **Gemma 4 26B-A4B UD-Q2_K_XL** (10.55 GB) | 19.1% at a ~1.7 GB smaller file. Best streaming locality measured (98 MiB/token, 83% hit); 5.0 tok/s on a phone; already ADR plan B. Thinking off (cycle-10 lesson) | Same; plus a check for leaked thinking and empty answers |
| 3 | **Gemma 4 12B dense, UD-IQ3_XXS 4.64 GB (and QAT Q4_0 6.98 GB as a quant-loss control)** | The only model that fits the 8 GB Pixel 8a resident with a knowledge proxy above the 4B (15.6 vs 12.7). The Q4_0 run separates "model knows more" from "2/3-bit erased it". Also a 12 GB candidate | IQ3 ≤ baseline + MDE: drop 8 GB middle ground; Q4_0 ≤ baseline: drop the model |
| 4 | **Qwen3-30B-A3B-Instruct-2507 UD-Q2_K_XL** (11.79 GB) | Natively non-thinking (no hidden-thinking latency or leakage risk); same lineage as the baseline 4B; best BigMoeOnEdge production recipe (5.2 tok/s). AA index −66 flags more confident-wrong answers, so watch cw | cw > baseline per seed: drop |

**Not shortlisted:**
- Muse Glimmer 30B: best knowledge (27.0%) but dense and not phone-viable. **Option:** one desktop closed-book run as a "ceiling at ~11 GB disk" data point, only if r4to wants the number for the write-up.
- gpt-oss-20b: SimpleQA 6.7%, halluc 91–94%.
- Nemotron 3 Nano: no ≤ 13 GB GGUF.
- ERNIE 21B: contamination doubt.
- LFM2.5-8B / LFM2-24B and Granite: low knowledge.
- K2 Horizon: not in llama.rn.

## Decisions / Options / Tasks

- **Decision (reversible):** the fast tier stays Qwen3-4B-Instruct-2507; no 2026 ≤ 5 GB model beats it on the knowledge proxy.
- **Option:** swap the deep-tier model to Qwen3.5-35B-A3B or Gemma 4 26B-A4B only if the closed-book screen shows Δ ≥ MDE over Qwen3.6.
- **Option:** Gemma 4 12B as the middle ground for 8 GB phones, if the 3-bit screen passes.
- **Task (minimum that closes the loop):** the existing closed-book all-57 screen (same as the Q35 / G4E4B screens), no-think, seed 42. Order: #1 Qwen3.5-35B-A3B → #3 Gemma 4 12B (IQ3 + Q4_0) → #2 → #4. One model at a time on the mini (disk ≥ 25 GiB; 12 GB downloads need the disk plan). Metric: ratio + cw vs the 4B's 0.487 and vs Qwen3.6 deep.

## UNKNOWN

- **Reasoning vs non-reasoning mode of each benchlm/AA accuracy row.** Qwen3.6's mirror halluc of 50.5% conflicts with its non-reasoning index of −60. The ranking among the three 19–20% models may flip in non-thinking mode.
- **SimpleQA (closed-book) for every shortlisted model and for the baseline:** not published.
  - Only gpt-oss-20b (6.7%) and ERNIE-21B (24.2%, disputed) have vendor SimpleQA.
  - ERNIE's own comparison table lists original Qwen3-30B-A3B at 4.7 (per the HF discussion).
- AA-Omniscience accuracy for Qwen3-30B-A3B-Instruct-2507 (only index −66 is public), GLM-4.7-Flash, ERNIE-4.5-21B-A3B, SmallThinker-21B, LFM2-24B-A2B, Ling-mini-2.0, Ministral 3 14B, Granite 4.0 H-Tiny, K2 Horizon 3.7B/7B/36B.
- **Knowledge loss at 2–3-bit quantization** for any of these models (KLD is known for some Unsloth quants, but not factual recall).
- Any 20–35B MoE tok/s on **Tensor G3**, Dimensity 9300 or SD 8 Gen 3, and on any **8 GB** phone with stock llama.cpp. The 0.18 tok/s figure (Qwen3-30B-A3B, 8 GB cap, phone) appeared only in a search snippet, not in the fetched paper text.
- Gemma 4 26B-A4B and Qwen3.5-35B-A3B resident dense-part sizes under BigMoeOnEdge (for the 8 GB question). Prefill peak for the 400-token deep context on Gemma (Kiln measured only Qwen3.6).
- Whether llama.rn 0.13 includes the archs for Muse Glimmer, K2 Horizon (#29535) and GLM-4.7-Flash; the llama.cpp build it pins was not checked here.
- Haiku 4.5's AA-Omniscience accuracy, which would calibrate "AA acc → BOAR closed-book score": not shown on public pages.
- Gemma 4 12B ARM tok/s (only estimated); Phi-4 GGUF sizes (not fetched).
