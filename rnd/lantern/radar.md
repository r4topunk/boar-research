# Radar: phone-inference models, engines, quants and papers (2026-08-01 to 2026-09-30)

> Lantern · R&D sprint 1 · 2026-09-30. Scope: what changed in Aug–Sep 2026 that matters for a ≤12 GB, ≤50 GB, fully offline phone app, measured against the post author's thesis (`vitalik-thesis.md`). Relevance column: **Kiln** = speed/architecture, **Veil** = privacy/verifiability.
> Compiled by a research agent (opus) plus a Lantern spot-check (below). All numbers are the vendor's or author's own. **Nothing here was measured on a phone.**

## TL;DR

- **the post author's "extreme MoE, <1B–1.5B active" now has a runnable point that fits in RAM: Maple-Preview 20B-A1B** (DeepGrove, MIT, 2026-08-04, ternary, 4.64–5.50 GiB). Its `maple` arch and the ARM `tq2_0` kernels are **already in BOAR's llama.rn 0.13.0-rc.4** (verified). So it is a catalog-only experiment. Risk: ternary models lose factual knowledge ([2609.32902](https://arxiv.org/abs/2609.32902)), and BOAR is a knowledge app.
- **The n-gram / Engram direction became real, but not at phone size.** DeepSeek-V4.1-Flash (2026-09-10) ships a 196B Engram table. A community recipe serves it from NVMe at 18 GB RSS, reading 48 rows × 256 B per token. The smallest Qwen3.8-Flash-Next build is still ~65 GB, which is over the 50 GB budget. **The team decision stands** (ADR 0001, models-research).
- **Two cheap deep-tier levers:**
  - Training-free halving of active experts (8→4) on Qwen3.6-35B-A3B for −0.35 MMLU ([2609.04575](https://arxiv.org/abs/2609.04575)). This beats the team's 8→6 plan.
  - RAZOR pruning to 19.4B total (might fit in RAM).
- **Speculation now has phone-class drafters (DSpark: 2.3–2.5× on dense 1–3B, only 1.18× on an 8B-A1B MoE).** llama.rn drives only `draft-mtp` (verified: `shouldUseMTP` in `cpp/rn-completion.cpp`), so DSpark needs a native patch. BigMoMo ([2609.14643](https://arxiv.org/abs/2609.14643)) is the first paper where speculation *helps* a flash-streamed MoE on a phone.
- **NPU prefill (BigMoeOnEdge v0.26: 80.6 s → 10.0 s) is Snapdragon-only.** the post author's "CROPS AI" point (support more than one hardware vendor, `vitalik-thesis.md` R22) argues against betting on it as the default.
- **For Veil:** BadEngram ([2609.13478](https://arxiv.org/abs/2609.13478)) hides backdoors in n-gram/PLE tables while the backbone stays untouched. Any on-disk table needs its own hash pin. Memory-Sovereign Inference ([2608.23805](https://arxiv.org/abs/2608.23805)) says RSS excludes page cache, so "fits in 12 GB" claims must be measured system-wide.

## Lantern spot-check (2026-09-30)

| Claim | Check | Result |
|---|---|---|
| Maple / Spark-X2.5-4B / DeepSeek-V4.1-Flash / Ternary Bonsai 2 dates and licenses | HF API `createdAt`, `cardData.license` | ✅ 2026-08-04 MIT · 2026-08-24 Apache-2.0 · 2026-09-10 MIT · 2026-09-16 Apache-2.0 |
| arXiv 2609.04575, 2609.13478, 2609.32902, 2609.14643 exist with these topics/dates | arXiv API | ✅ all four; published 09-04, 09-11, 09-26, 09-13 |
| `maple`, `spark2_5`, `nemotron_h_moe` archs in BOAR's runtime | `grep` in `wt/release-110/node_modules/llama.rn/vendor/llama.cpp/src/llama-arch.cpp` (llama.rn 0.13.0-rc.4) | ✅ lines 65, 151, 95; ARM `tq2_0_q8_K` present in `arch/arm/quants.c` |
| llama.rn speculation path is MTP-only | `grep` `cpp/rn-completion.cpp` | ✅ only `shouldUseMTP()`; no `dspark` string |
| `k2-horizon` arch absent | same grep | ✅ absent (needs a runtime bump) |

Not spot-checked: the remaining ~35 items (links and numbers are as the agent recorded them from the primary pages).

## Map against the thesis

```
the post author (2026-09-17): "~100B params on disk, <1B active per token, extreme MoE incl. ngrams"

                active/token →   <1B            ~1.5B              3B                 6B+
 total ~200B+   (n-gram)        —              —                  —                  DeepSeek-V4.1-Flash (196B Engram, server only)
 total ~65-80B                  —              —                  AliceAI-80B-A3B    Qwen3.8-Flash-Next shrinks ~65 GB ✗ >50 GB
                                                                  (base, no GGUF)
 total ~20-35B                  —              Maple 20B-A1B ★    Qwen3.6-35B-A3B (deep, deferred)
                                               (5.5 GiB, in RAM)  + RAZOR 19B / k 8→4 / Edge0 prerouter
 total ≤8B                      Needle 3 (Engram, 8-29 MB router)  Ling-3.0-tiny (team)   Spark-X2.5-4B (dense, 2.6 GB)
★ = runnable in BOAR's current runtime, the closest match to the thesis that fits the 12 GB budget
```

Legend for the status column (compared with review/models-research/*, adr-moe-deep/spikes_deep-tier_SOTA.md and research-pipeline/03-estado-da-arte.md):
- NEW: not in the team docs.
- UPDATE: in the team docs, with new facts here.
- already covered: listed at the end, not repeated.

Verification: dates come from HF `createdAt`, arXiv `published`, GitHub `mergedAt` or release dates, all fetched on 2026-09-30. I did not reproduce any number; all of them are the vendor's or author's own.

---

## (a) MoE with few active params (≤3B active)

| Item | Date | Link | Published number (unit, device/setting) | License | Relevance (Kiln = speed/arch, Veil = privacy) | Status |
|---|---|---|---|---|---|---|
| **Maple-Preview 20B-A1B** (DeepGrove), ternary MoE: 24 layers, 256 experts with 8 active, SWA-512 and global attention at 3:1 | HF 2026-08-04; llama.cpp arch merged 2026-09-14 ([#27000](https://github.com/ggml-org/llama.cpp/pull/27000)) | [card](https://huggingface.co/deepgrove/maple-preview) · [GGUF](https://huggingface.co/deepgrove/maple-preview-GGUF) | GGUF TQ1_0+Q4_K head **4.64 GiB**, TQ2_0+Q4_K head **5.50 GiB**. M5 Pro CPU, 16 threads: **pp512 610 tok/s, tg128 253 tok/s** (TQ2_0/Q4_K head). 218 tok/s on an M4 Mac mini (card). The PR smoke test on M4 CPU got ~216 pp / ~88 tg. 1.49B active ([ai-tldr](https://ai-tldr.dev/releases/deepgrove-maple-preview/)). | MIT | **Kiln:** the "~20B total, ~1B active" point that fits in RAM, and it already runs in our b11010 (`maple` arch plus ARM TQ kernels verified locally). Vendor says reasoning-focused and weak on agentic tasks. Factual QA is UNKNOWN because the benchmarks are only in images. | NEW |
| **AliceAI-Foundation-80B-A3B-Base** (Yandex): 48 layers of 3×KDA + 1×gated-attention, 512 experts, top-10 + 1 shared | 2026-09-12 | [card](https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base) | 80B total / 3B active (26.7× ratio). TriviaQA 5-shot **79.0** vs Qwen3.5-35B-A3B-Base 71.4. WikiWebFacts **86.5** vs 62.4. Base only. | Apache-2.0 | **Kiln:** the first ~100B-class, 3B-active model with KDA linear attention (cheap prefill), strong on facts. It is a *base* model, uses `custom_code`, and has no llama.cpp arch (not in b11010). Watch for an instruct release. | NEW |
| **NVIDIA Nemotron-3.5-Lightning-30B-A3B**: Mamba-2 + MoE + attention hybrid, gate-less experts | release 2026-08-11 (card) | [card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16) | MMLU-Pro **81.94** vs Qwen3.6-35B-A3B 85.63. GPQA-D 75.44 vs 83.40. AA-Omniscience 17.50 vs 19.47. The expert layout is up/ReLU²/down, so an expert costs **2/3 the bytes** of a gated one. Q4_0 is 18.9 GB ([BMoE v0.25/v0.27](https://github.com/Helldez/BigMoeOnEdge/releases)). Only 6 of 52 blocks are attention. | OpenMDW-1.1 | **Kiln:** lower flash traffic per expert and a tiny KV. The trade is that quality sits below Qwen3.6. `nemotron_h_moe` is in b11010. | NEW |
| **Edge0-35B-A3B-preview** (Qwen3.6-35B-A3B at int4, with Recover-LoRA and a trained *prerouter*) | HF 2026-09-08; [arXiv 2609.18063](https://arxiv.org/abs/2609.18063) 2026-09-16 | [card](https://huggingface.co/Edge0/Edge0-35B-A3B-preview) | Mac mini M4 Pro 24 GB: **14.9-17.7 tok/s decode, 113/140 tok/s prefill, 2.9 GiB peak active memory** (the paper says 20 tok/s in 3 GiB). Prerouter adds up to **+59% decode**. Runs with K=4 experts. Averages 79.2 vs 83.2 for fp16 (-3.9 points). | Apache-2.0 | **Kiln:** routing is predicted one layer ahead, so SSD reads overlap compute. This is the missing piece in BMoE, whose predictive prefetch measured negative. Mac/MLX only; no Android backend (card: "on roadmap"). | NEW (the team only has Edge0-8B-A1B) |
| **RAZOR expert pruning** → Qwen3.6-35B-A3B-RAZOR-19B-A3B (128 of 256 experts) | arXiv 2026-09-24; checkpoint 2026-09-28 | [arXiv 2609.30465](https://arxiv.org/abs/2609.30465) · [ckpt](https://huggingface.co/Nickyang/Qwen3.6-35B-A3B-RAZOR-19B-A3B-E128of256) | 35B → **19.4B total**, 3B active unchanged. Beats REAP by **+2.12 to 5.59 points** (9-task macro average) at 25-50% removal. The authors note it shifts diversity, formatting and termination. | Apache-2.0 | **Kiln:** a smaller expert bank means a higher cache hit rate. ESTIMATE (not measured): ~6.8 GB at UD-Q2_K_XL-like bpw, which might fit in RAM with no streaming. MoEXBench ([2608.21693](https://arxiv.org/abs/2608.21693)) finds "expert pruning is the dominant degradation source", so knowledge QA risk is high. | NEW |
| **Training-free halving of activated experts** (renormalize by the top-k₂ mass) | 2026-09-04 | [arXiv 2609.04575](https://arxiv.org/abs/2609.04575) | Qwen3.6-35B-A3B at 8→4 experts: MMLU **-0.35 pt with k₂=16** vs -4.65 with standard renormalization, **halving routed-expert compute**. Qwen3.5-397B at 10→5: -0.55 pt. | arXiv | **Kiln:** stronger than the team's k=8→6 lever (+16-24%). It halves the expert bytes streamed per token. Needs a small native patch to the router normalization in llama.cpp; not a GGUF-only edit. | UPDATE (k-reduction lever in moe-and-speed §5) |
| **"You only need 2/3 of the chosen experts"** (12 fine-grained MoE checkpoints, 9 families) | 2026-09-22 | [arXiv 2609.25809](https://arxiv.org/abs/2609.25809) | Keeping ~2/3 of the selected experts retains **98.8%** of performance, with a **1.2-1.7x** measured speedup; it is a one-integer change. | arXiv | **Kiln:** an independent confirmation of top-k reduction. Pair it with 2609.04575. | UPDATE |
| **MobileMoE** (Meta) now runs in MNN | MNN commit 2026-09-29 (weights on HF since 2026-06-11) | [MNN commit log](https://github.com/alibaba/MNN/commits/master) · [HF](https://huggingface.co/facebook/MobileMoE-S-QAT) | Team doc (paper): 0.3/0.5/0.9B active, INT4 0.68/1.48/2.75 GB. No new MNN speed number is published. | CC BY 4.0 (weights), Apache-2.0 (MNN) | **Kiln:** answers the team's UNKNOWN "whether MobileMoE weights will be released". Yes, including QAT checkpoints. Still no GGUF. | UPDATE |

## (b) N-gram / conditional memory (Engram-style, tables on disk)

| Item | Date | Link | Published number | License | Relevance | Status |
|---|---|---|---|---|---|---|
| **DeepSeek-V4.1-Flash**: the first DeepSeek release with **Engram** | 2026-09-10 | [card](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash) | 552B backbone; **8B active in prefill, 16B in decode** (causal encoder-decoder); **Engram 196B params**; KV **890 bytes/token** (1/4 of V4-Flash); MMLU-Pro base 74.1. | MIT | **Kiln:** proves that Engram at scale plus encoder-side prefill is DeepSeek's direction. Unusable on a phone because of size. The same card also ships DSpark as its built-in speculative decoding. | NEW (team: "no weights with Engram exist") |
| **Engram off NVMe: disk prestage recipe** for V4.1-Flash | 2026-09-12 | [HF recipe](https://huggingface.co/nktlabs/dsv41-flash-engram-disk-prestage) | **48 random 256-byte Engram rows/token** from a **190 GiB** table. Disk + prestage: **80.2 tok/s at 18 GB RSS**, vs 26.1 tok/s for the vendor's in-graph disk path and 113.3 tok/s pinned at ~280 GB. GSM8K-200 is unchanged at 97.5%. | MIT | **Kiln:** the exact pattern BOAR's "hash n-gram row-streamer" idea needs (spikes_deep-tier §4). Hash early, `preadv` before the graph, keep the graph static. GPU server numbers, not phone. | NEW |
| Qwen3.8-Flash-Next shrink attempts: REAP-288 / GSQ-RCO / Sushi | 2026-08-27 / 2026-09-07 / 2026-09-28 | [REAP-288](https://huggingface.co/sh0wie/Qwen3.8-Flash-Next-REAP-288-MLX-4bit) · [GSQ-RCO](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF) · [Sushi-2bpw](https://huggingface.co/beamster/Qwen3.8-Flash-Next-Sushi-2bpw) | REAP-288: **68 GB** disk, **39 GB resident with the n-gram table streamed from NVMe** (omlx), HumanEval 91.5% vs 93.9%. GSQ-RCO Q2_0: **66.4 GB** (ZS recovery 101.4%). Sushi: **~65 GiB** (29.8 GiB of it the n-gram table, read from SSD). | Qwen Community 1.0 | **Kiln:** the smallest file dropped from 72.5 to ~65 GB. **Still >50 GB**, so the team decision stands. omlx and Sushi show the table streamed from SSD in practice (Mac only). | UPDATE |
| **Needle 3** (Cactus): 8-29 MB on-device model with an **engram n-gram memory** read by gather | 2026-09-16 | [card](https://huggingface.co/Cactus-Compute/needle3) | Single file of **8-29 MB**. Numbers are in SVG charts only (UNKNOWN). | Apache-2.0 | **Kiln:** a tiny router or tool-call model that already uses Engram-style memory. Could handle BOAR intent routing. Needs its own `cactus-needle` runtime, not llama.cpp. | NEW |
| N-gram memory research: FactorEngram / MoME / Lngram v2 | 2026-09-28 / 09-14 / 09-03 | [2609.35578](https://arxiv.org/abs/2609.35578) · [2609.15126](https://arxiv.org/abs/2609.15126) · [2609.03426](https://arxiv.org/abs/2609.03426) | Lngram v2 scaled to a **30B** VLM. FactorEngram tested at 340M/1B and finds the best insertion point is before attention in the middle layers. MoME is "better than Bigram/STEM at iso-FLOP" (no abstract numbers). | arXiv | **Kiln:** context-aware n-gram memory, meaning the next generation of Engram. No weights yet. | NEW |

## (c) Speculative decoding on device

| Item | Date | Link | Published number | License | Relevance | Status |
|---|---|---|---|---|---|---|
| **LFM2.5-DSpark drafters** (1.2B / 2.6B / 8B-A1B), GGUF in mainline llama.cpp (`--spec-type draft-dspark`) | HF 2026-08-10, GGUF 2026-08-19; blog 2026-08-20; [#27383](https://github.com/ggml-org/llama.cpp/pull/27383) 2026-08-20 | [blog](https://www.liquid.ai/blog/lfm2.5-dspark) · [GGUF](https://huggingface.co/LiquidAI/LFM2.5-2.6B-DSpark-GGUF) | M4 Max: 1.2B **2.54x** (138→350 tok/s); 2.6B **2.27x** (61→139); **8B-A1B only 1.18x** (90→106; "verifying k tokens activates more experts"). Drafter Q4_K_M 191 MB, acceptance -3% vs F16. No phone data. | LFM 1.0 | **Kiln:** fits the dense fast tier only. It confirms the team rule (no speculation on MoE). llama.rn rc.4 runs only `draft-mtp` (checked `rn-completion.cpp`), so this needs a patch. | UPDATE (answer-llms had "~2.6x claimed") |
| **MiniCPM5-2B-DSpark** (324M drafter, block 7) | 2026-09-06 (GGUF 2026-09-09) | [card](https://huggingface.co/openbmb/MiniCPM5-2B-DSpark) · [GGUF](https://huggingface.co/openbmb/MiniCPM5-2B-DSpark-GGUF) | Acceptance length **5.52 at T=0**, 4.05 at T=1 (general domain 4.16 / 3.10). GGUF BF16 is 653 MB and the card documents the `llama-server -md … --spec-type draft-dspark` command. | Apache-2.0 | **Kiln:** answers the team's UNKNOWN ("llama.cpp DSpark support for the `llama` arch"): yes, per the card's command. Grounded RAG answers run near T=0, which favors acceptance. | UPDATE |
| **Ling-3.0-Tiny-DSpark** (community, 274M) + llama.cpp DSpark for `bailingmoe3` | 2026-09-23 (GGUF 2026-09-26); [#27508](https://github.com/ggml-org/llama.cpp/pull/27508) 2026-08-22 | [card](https://huggingface.co/jayyun98/Ling-3.0-Tiny-DSpark) · [GGUF](https://huggingface.co/StefanoBalocco/Ling-3.0-Tiny-DSpark-GGUF) | H200, T=0, reasoning off: acc_len **2.79**, **2.37x** (26.98→63.84 tok/s, single-run pilot). GGUF comes in Q4_0/Q2_0/TQ1_0. | other (community) | **Kiln:** a drafter for our top in-RAM candidate. The low acceptance (2.79) plus the MoE verify cost make a phone gain doubtful. Measure it, don't assume it. | NEW |
| **DFlash2** in llama.cpp (local conv + candidate selector) | 2026-08-27 | [#27342](https://github.com/ggml-org/llama.cpp/pull/27342) | Qwen3.8-27B Q4_K_M, M5 Pro: **10.42 → 19.31 tok/s (1.85x)**, acceptance 4.92. A Q4_K_M draft gives 1.81x. | MIT | **Kiln:** dense targets only. Drafters exist mostly for 27B-class models. | NEW (team has DFlash v1 only) |
| **BigMoMo**: speculative decoding × MoE expert offload on phones | 2026-09-13 | [arXiv 2609.14643](https://arxiv.org/abs/2609.14643) | **4.83x** vs on-demand AR offloading and **1.82x** vs the best speculative MoE baseline; MoEs up to 30B; 2 mobile platforms (NPU). | arXiv | **Kiln:** the first result where speculation *helps* a flash-streamed MoE on a phone. The multi-token window batches expert reads and reorganizes experts on flash. It contradicts BMoE's negative result, so it is worth reading before closing that door. | NEW |
| **S2-MoE**: self-speculative decoding for MoE, implemented in llama.cpp | 2026-08-15 | [arXiv 2608.15018](https://arxiv.org/abs/2608.15018) · [code](https://github.com/angerybob/S2-MoE) | Up to **5.3x**, **~2.0x average** over AR on "edge devices" (device not named in the abstract). | MIT (code) | **Kiln:** also a llama.cpp code base, so it could be ported into llama.rn. | NEW |
| **AcceptMoE**: verifier expert sets aware of cache residency | 2026-08-04 | [arXiv 2608.02989](https://arxiv.org/abs/2608.02989) | Under expert offload: **2.06x** vs EAGLE-3, host-to-device traffic **-73.6 to -77.1%**, accuracy **-0.27 pp** (SGLang, GPU). | arXiv | **Kiln:** the verify step is limited to cached experts. This fixes the root cause of MoE speculation losses. | NEW |
| TreeSpark (draft trees for DSpark-style drafters) | 2026-08-12 | [arXiv 2609.22098](https://arxiv.org/abs/2609.22098) | **+15-25%** accepted tokens per round and **8-14%** faster than a tuned chain, lossless at any temperature. | arXiv | **Kiln:** a small add-on if DSpark is adopted. | NEW |
| GDN Tree-Scan (tree verification for Gated-DeltaNet hybrids) | 2026-09-20 | [arXiv 2609.23900](https://arxiv.org/abs/2609.23900) | Qwen3.6-27B: **23.88 vs 18.80 tok/s** vs native 5-step MTP (+27%), in vLLM on GPU. | arXiv | **Kiln:** tree speculation on hybrid (recurrent-state) models such as Qwen3.5/3.6 needs state replay. Tells us why naive speculation on hybrids is tricky. | NEW |

## (d) KV / prefill acceleration (NPU prefill, caching, sparse or linear attention)

| Item | Date | Link | Published number | License | Relevance | Status |
|---|---|---|---|---|---|---|
| **BigMoeOnEdge v0.26**: prefill on the Hexagon NPU, decode on CPU, model larger than RAM | 2026-09-28 | [release](https://github.com/Helldez/BigMoeOnEdge/releases/tag/v0.26.0) | 12 GB phone, Hexagon v81, Qwen3.6-35B-A3B Q4_K_M streamed: 1418-token prompt **80.6 s → 10.0 s (8.1x)**. Short prompts gain nothing. | Apache-2.0 | **Kiln:** Snapdragon only. The likely Pixel judge phone and our Dimensity 8300 have no Hexagon. | UPDATE (03-estado-da-arte cites 63.8 → 8.2 s) |
| **BigMoeOnEdge v0.28**: routed-expert NPU arena | 2026-09-29 | [release](https://github.com/Helldez/BigMoeOnEdge/releases/tag/v0.28.0) | 130-480-token prompts: Qwen3.6 Q4_0 **7.68 → 4.16 s (1.85x)**; Gemma 4 26B **1.81x**; Nemotron 3.5 1.09x (it routes 79% of experts). Output is bit-identical. | Apache-2.0 | **Kiln:** short RAG prompts touch only ~50% of experts, so reading only the routed ones pays off. The same idea applies to CPU prefill of a streamed MoE. | NEW |
| **BigMoeOnEdge v0.27**: `--decide` + shared-prefix state restore | 2026-09-28 | [release](https://github.com/Helldez/BigMoeOnEdge/releases/tag/v0.27.0) | Nemotron-3.5 Q4_0 streamed on a 12 GB phone: restoring a 29-token prefix cut the prefill **13.9 s → 4.4 s**. The restored state is the whole sequence state, so it also works on hybrids. | Apache-2.0 | **Kiln:** prefix reuse for the deep tier. `--decide` (pick from a list after one prefill, no decode) fits BOAR's routers. | NEW |
| **llama.cpp Hexagon HMX GATED_DELTA_NET** kernel | 2026-09-21 | [#29199](https://github.com/ggml-org/llama.cpp/pull/29199) | Galaxy S26 NPU, Qwen3.5-4B Q4_0: **pp1024 616 → 932 tok/s**; Qwen3.5-0.8B 1807 → 3477 tok/s; decode unchanged. | MIT | **Kiln:** Qwen3.5/3.8 hybrid prefill on Snapdragon NPUs is now fast. Not in b11010; Snapdragon only. | NEW |
| **EStream**: MoE prefill via expert virtualization on mobile NPUs (UFS→NPU arena) | 2026-09-06 | [arXiv 2609.06551](https://arxiv.org/abs/2609.06551) | Snapdragon phone, 7-16B MoEs: **2.25-27.57x** prefill-TTFT speedup and **1.19-12.29x** lower peak memory; scales to 46.7B. | arXiv | **Kiln:** the academic version of BMoE's NPU arena. | NEW |
| HA-NPU: hybrid linear-attention models on edge NPUs | 2026-09-26 | [arXiv 2609.32114](https://arxiv.org/abs/2609.32114) | Linear-attention kernel up to **35.95x** faster; **2.03x** end-to-end latency. | arXiv (code promised) | **Kiln:** Qwen3.5-class hybrids on NPUs. | NEW |
| **TierKV**: predictive multi-tier KV (exact / low-rank / flash) | 2026-09-18 | [arXiv 2609.21172](https://arxiv.org/abs/2609.21172) | Prefill up to **17.6x** vs mobile frameworks; RAM-resident KV **-12.5 to -34%**; 8 models, 3 mobile SoCs. | arXiv | **Kiln:** long-context RAG on 12 GB. | NEW |
| KV reuse on mobile NPUs (prefix and non-prefix) | 2026-09-28 | [arXiv 2609.34727](https://arxiv.org/abs/2609.34727) | TTFT **-40 to -60%** vs no reuse and vs prefix-only caching. | arXiv | **Kiln:** non-prefix reuse, so a retrieved passage's KV can be reused across queries. That is the lever beyond the team's prefix-cache H3. | NEW |
| **mzCache**: on-device LLM memory under multitasking (llama.cpp, Android app) | 2026-09-01 | [arXiv 2609.01338](https://arxiv.org/abs/2609.01338) | TTFT **2.1-5.5x** lower than storage-backed partial offload after OS eviction. | arXiv | **Kiln:** a judge who switches apps will evict our weights and KV; this is the fix pattern. | NEW |
| llama.cpp CPU tiled mul_mat for k-quants | 2026-09-26 | [#27851](https://github.com/ggml-org/llama.cpp/pull/27851) | x86 (9950X3D, 8 threads): prefill **3-7x** vs standard, 2x vs repack; break-even at 32 rows. **ARM microkernel not written yet.** | MIT | **Kiln:** watch for an ARM port; it would speed up CPU prefill of Q2_K/Q3_K experts, which are never repacked on ARM. | NEW |

## (e) New small models (1-4B, dense or hybrid)

| Item | Date | Link | Published number | License | Relevance | Status |
|---|---|---|---|---|---|---|
| **Spark-X2.5-4B** (XHToken), 1 full-attention : 3 SWA hybrid, native 1M context | 2026-08-24 | [card](https://huggingface.co/XHToken/Spark-X2.5-4B) · [GGUF](https://huggingface.co/XHToken/Spark-X2.5-4B-GGUF) | **GPQA 67.4** vs Qwen3.5-4B 67.2; **HLE 12.3** vs 8.6; IFBench 75.0 vs 59.2; AA-LCR 56.3 vs 57.0 (vendor). Q4_K_M **2.60 GB**. The `spark2_5` arch is **in b11010** (checked). | Apache-2.0 | **Kiln:** a drop-in fast-tier candidate. SWA 3:1 means a smaller KV and cheaper long-prompt attention. SimpleQA / factual numbers are not published. | NEW |
| **K2-Horizon-3.7B** (IFM), fully open (data, recipe, checkpoints), 512K context | 2026-09-01 | [card](https://huggingface.co/IFM/K2-Horizon-3.7B) · [GGUF](https://huggingface.co/IFM/K2-Horizon-3.7B-GGUF) | HMMT Feb 2026 **70.5** vs Qwen3.5-4B 61.6 (vendor). Q4_K_M **3.16 GB**. GGUF arch is `k2-horizon`, **not in b11010**. | Apache-2.0 | **Kiln/Veil:** open data and recipe make the model auditable end to end, which fits the Veil narrative. Needs a runtime bump. | NEW |
| (Ternary Bonsai 2 27B and Maple: see (g) and (a)) | | | | | | |

## (f) Engines / runtimes

| Item | Date | Link | Published number | License | Relevance | Status |
|---|---|---|---|---|---|---|
| **llama.cpp: Android CPU affinity fix** (`-C/--cpu-mask`, `--cpu-strict` were silently ignored on Android) | 2026-08-10 | [#26838](https://github.com/ggml-org/llama.cpp/pull/26838) | After the fix, 2 threads on big cores vs little cores: **22.77 vs 11.79 tok/s** (qwen2 1B Q4_0). Before the fix both were ~22.7. | MIT | **Kiln:** BOAR can now pin to big cores through llama.rn `cpu_mask`, which the team listed as a lever. Merged before b11010, so it is available (verify on device). | UPDATE (moe-and-speed §5 "thread pinning") |
| **BigMoeOnEdge v0.25**: Nemotron 3/3.5 gate-less experts + Ornith | 2026-09-28 | [release](https://github.com/Helldez/BigMoeOnEdge/releases/tag/v0.25.0) | Gate-less experts cost **2/3 the bytes**. Predictive prefetch does nothing on Nemotron (no adjacent MoE blocks). | Apache-2.0 | **Kiln:** team clone is `74ba18f` from 2026-09-07. v0.25-0.28 (NPU prefill, decide, routed arena) need a re-pull. | NEW |
| **Routide** (Swift/MLX, Qwen3.6-35B-A3B experts on iPhone storage) | 2026-09-24 | [arXiv 2609.29032](https://arxiv.org/abs/2609.29032) | Footprint **1.87-2.73 GiB** (iOS 27). Demand hit rate **0.00%** with a 512 MiB LRU, **38.58%** at 576 MiB. Includes a thermal stop event. | arXiv | **Kiln (iOS/Harbor):** the only characterized iPhone path for a streamed MoE. Verifies the team's item that was marked UNVERIFIED. | UPDATE |
| **ik_llama.cpp: Prism ternary R8 IQK kernels** | 2026-09-29 | [ik #2550](https://github.com/ikawrakow/ik_llama.cpp/pull/2550) | Ternary-Bonsai-2-27B on i5-13420H (4 P-cores, AVX2): PQ2_0 **pp256 1.93 → 11.45 tok/s (5.93x)**, **tg32 3.30 → 5.04**; bit-identical greedy output. | MIT | **Kiln:** a realistic CPU ceiling for a dense ternary 27B, ~5 tok/s on a laptop CPU. So a phone will be slower (ESTIMATE). AVX2 only; ARM kernels UNKNOWN. | NEW |
| llama.cpp: Hexagon backend fully async + multi-NPU; K-quants on HTP | 2026-08-27 / 2026-09-16 | [#26501](https://github.com/ggml-org/llama.cpp/pull/26501) · [#28994](https://github.com/ggml-org/llama.cpp/pull/28994) | Q4_K and Q6_K (so Q4_K_M) now run on the NPU. Validated on IQ8/IQ9 boards; no phone tok/s in the PR. | MIT | **Kiln:** these were the preconditions for BMoE v0.26 NPU prefill. Snapdragon only. | NEW |
| KleidiAI SME2 F32 GEMV | 2026-08-21 | [#26891](https://github.com/ggml-org/llama.cpp/pull/26891) | Llama-3.2-1B **F32**: TG **+85.5%** (1 thread), +15.7% (8 threads). | MIT | **Kiln:** low value. It is F32 only, SME2 only, and KleidiAI is not compiled into llama.rn (team doc). | NEW (low) |
| MNN: MobileMoE export/inference (2026-09-29), DFlash spec pool (2026-09-11), ARM CPU flash-attention prefill/decode scaling (2026-09-04) | 2026-09 | [commits](https://github.com/alibaba/MNN/commits/master) | No published tok/s (UNKNOWN). | Apache-2.0 | **Kiln:** an alternative runtime with QNN/NeuroPilot plugins. Low priority. | UPDATE (team: MNN "UNKNOWN") |
| ExecuTorch 1.5.0 (Qwen3.5 MoE export, off-graph KV layouts); 1.4.0 (QNN 2-bit 16a2w) | 2026-09-16 / 2026-08-07 | [v1.5.0](https://github.com/pytorch/executorch/releases/tag/v1.5.0) | No published tok/s. | BSD-style (GitHub: NOASSERTION) | **Kiln:** watch only. | NEW (low) |
| LiteRT-LM 0.17.0 (Gemma 4 12B MTP, local-attention memory cut) | 2026-09-09 | [v0.17.0](https://github.com/google-ai-edge/LiteRT-LM/releases/tag/v0.17.0) | No new numbers in the notes. | Apache-2.0 | **Kiln:** watch only. | NEW (low) |

## (g) Quantization (ternary, IQ/UD, QAT, KLD)

| Item | Date | Link | Published number | License | Relevance | Status |
|---|---|---|---|---|---|---|
| **Ternary Bonsai 2 27B** (Prism ML, from Qwen3.8-27B, Hadamard-rotated ternary g128) | 2026-09-16 | [card](https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf) | **5.95 GB** (PTQ1_0, 1.75 bpw) / 7.21 GB (PQ2_0). Averages **84.78 vs FP16 86.32 (98.2%)**, vs Qwen3.8-27B IQ2_XXS 72.59 at 7.27 GB. Knowledge & reasoning category **79.86 vs 85.55**. M5 Pro Metal tg 28.1 tok/s. | Apache-2.0 | **Kiln:** 27B-class reasoning in ~6 GB of RAM. But it is dense 27B compute per token (CPU ceiling ~5 tok/s on a laptop, see ik #2550). It needs the PrismML llama.cpp fork (stock llama.cpp rejects the types). Knowledge takes the biggest hit. | NEW |
| **GSQ-RCO non-uniform GGUFs** (IST-DASLab), standard GGUF types, so stock llama.cpp runs them | 2026-08-28 | [card](https://huggingface.co/ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF) | Qwen3.8-27B at the same **8.4 GB**: GSQ-RCO IQ2_XS GPQA-D **84.85** vs Unsloth UD-IQ2_S **76.26**; AIME25 96.67 vs 86.67. At 9.8 GB: IQ2_S 86.36 vs UD-Q2_K_XL 86.87 (a tie). | Apache-2.0 | **Kiln:** better 2-bit files for the deep tier at no runtime cost. **UNKNOWN:** whether a GSQ-RCO Qwen3.6-35B-A3B exists; I found only 27B, Flash-Next and GLM. | NEW |
| **Knowledge collapse in low-bit LMs** | 2026-09-26 | [arXiv 2609.32902](https://arxiv.org/abs/2609.32902) | Ternary retains as little as **6%** of fp16 factual capacity while perplexity rises only 1.4-1.6x. The PTQ methods tested **recover no measurable capacity below 4 bits**. | arXiv | **Kiln/eval:** BOAR is a *knowledge* app. Treat Maple, Bonsai and IQ2 builds as suspect until BOAR's factual eval passes. Small-scale (≤50M) study, so it points in a direction and does not measure our models. | NEW |
| Capability-stratified degradation (Qwen3.5-0.8B → ternary "Cloe") / PTQ ternarization of Qwen3-4B | 2026-08-28 / 2026-09-02 | [2608.28809](https://arxiv.org/abs/2608.28809) · [2609.01962](https://arxiv.org/abs/2609.01962) | Cloe: MMLU linear probe **43.76% → 26.19%** (near chance). Qwen3-4B ternary PTQ: accuracy **64.5% → 54.7%**, 8.29 → 3.96 GiB, GEMV **4.6x slower** than FP16 cuBLAS. | arXiv | **Kiln:** do not ternarize our own fast-tier model post-hoc; only natively trained ternary (Maple, Bonsai) is worth testing. | NEW |
| BITCOS ternary layout (bitmap + sign vector) | 2026-09-14 | [arXiv 2609.16338](https://arxiv.org/abs/2609.16338) | **1.485 bpw** on the sparsest model; decode **+18%** on CPUs, +27% on Xe2 GPUs. | arXiv | **Kiln:** could shrink Maple-class files later. x86/Xe2 kernels only. | NEW (low) |

## (h) Privacy / verifiability (lighter coverage, for Veil)

| Item | Date | Link | Published number | License | Relevance | Status |
|---|---|---|---|---|---|---|
| **BadEngram**: backdoors hidden in gated n-gram / PLE memory tables | 2026-09-11 | [arXiv 2609.13478](https://arxiv.org/abs/2609.13478) | Controlled Engram model: **96.6% ASR**, 0.1% false activation, 99.6% clean accuracy. **Qwen3.8-Flash-Next PLE: 50.4% ASR (HarmBench)** with the backbone untouched. | arXiv | **Veil:** if BOAR ships any model with on-disk n-gram or PLE tables (Gemma 4 E-series already has PLE), pin and verify the **table file hashes separately** from the backbone. An unchanged backbone proves nothing. | NEW |
| **Memory-Sovereign Inference**: a falsifiable certificate for storage-backed inference | 2026-08-24 | [arXiv 2608.23805](https://arxiv.org/abs/2608.23805) | Qwen3-Next 32K prefill routes all **48×512** layer-experts, a **43.59 GiB** demand lower bound. The async path took **32.3%** of the blocking path's wall time, with outputs byte-exact across 64 tokens. | arXiv | **Veil + Kiln:** "process RSS excludes charged page cache", so any claim like "runs in 12 GB" must be measured board-wide. A template for honest memory claims in the bounty write-up. | NEW |
| ZK-friendly quantization for verifiable LLM inference | 2026-09-29 | [arXiv 2609.36437](https://arxiv.org/abs/2609.36437) | Qwen3-30B-A3B and 8 others: activation precision matters more than weight precision; the **RMSNorm inverse-sqrt lookup** is a recurring bottleneck. | arXiv | **Veil:** background only. ZK-proving an on-phone answer is still far from practical. | NEW (low) |
| Web-CLI: "verifiable privacy by architecture" (zero egress, offline-first) | 2026-08-28 | [arXiv 2608.28950](https://arxiv.org/abs/2608.28950) | No numeric privacy metric; four reference apps (incl. WebLLM chat). | arXiv | **Veil:** gives vocabulary for BOAR's claim: data locality as an independently checkable property (no INTERNET permission after setup, egress test). | NEW (low) |

---

## Already covered by team docs (skipped, no new facts found)
Ling-3.0-tiny / Ling-3.0-flash, MiniCPM5-2B, LFM2.5-2.6B / 1.2B / 8B-A1B, Granite 4.2 3B/8B, Nanbeige4.2-3B, Edge0-8B-A1B, AliceAI-T5-35B-A0.6B, Qwen3.8-Flash-Next (base facts), Qwen3.6-35B-A3B, Gemma-4-26B-A4B, llama.rn rc.5/rc.6, `--lazy-mode` / TENSOR_READ_LAZY (#27794), BMoE `--row-stream` / `--expert-substitute`, BailingMoE3 (#26608), Ling 3.0 parser (#28682), ModernBERT rerank pooling (#29627).

## Top 5 to test first (proposed to Kiln; none started)

| # | What | Why first | Definition of done / metric |
|---|---|---|---|
| 1 | **Maple-Preview 20B-A1B TQ2_0 (Q4_K head, 5.50 GiB)** in the current llama.rn b11010 on the Dimensity 8300 | Closest real match to the post author's thesis that we can run **today with no runtime change**: the `maple` arch and ARM TQ2_0 kernels are both in the vendored tree. 1.49B active means decode speed near LFM2.5-8B-A1B, with 20B of total capacity. | Runs with no crash. Record **tok/s decode, TTFT p50 with RAG** and **% correct on the s32 + crypto + vegan eval** vs Qwen3-4B. Kill it if factual % < Qwen3-4B (the knowledge-collapse risk, 2609.32902). |
| 2 | **Top-k halving with k₂ renormalization** (2609.04575) on the deep tier Qwen3.6-35B-A3B | Halves the routed-expert bytes per token, which is the binding cost of streamed decode, for -0.35 MMLU. Beats the team's k=6 plan. The patch touches only the router normalization. | Native patch behind a flag. Measure decode tok/s and the BOAR eval at k=8 vs k=4/k₂=16. Pass if eval Δ ≥ -1 pt and decode ≥ +30%. |
| 3 | **Spark-X2.5-4B Q4_K_M (2.60 GB)** as a fast-tier candidate | `spark2_5` is in b11010, so it is a catalog add-only change. It matches Qwen3.5-4B on GPQA, with SWA 3:1 for a cheaper KV and long-prompt attention. | Same s32 eval + TTFT p50 vs Qwen3-4B. Adopt only if ≥ on % correct **and** TTFT ≤ 70% (the team's existing gate). |
| 4 | **DSpark drafter on the dense fast tier** (MiniCPM5-2B-DSpark or LFM2.5-2.6B-DSpark Q4_K_M 191 MB) | Mainline llama.cpp supports it; acceptance 5.5 at T=0 fits grounded answers. The M4 Max gain on dense 2B models is 2.3-2.5x. | Patch llama.rn `rn-completion.cpp` to drive `draft-dspark` (today it runs only `draft-mtp`). Pass if decode ≥ 1.4x at T≤0.3 on phone CPU with identical greedy output. Skip on MoE (1.18x even on M4 Max). |
| 5 | **RAZOR-pruned Qwen3.6-35B-A3B (19.4B, 128 experts)** → GGUF at ~2.5-3 bpw | ESTIMATE ~6.8-7.5 GB: it might sit fully in RAM with plain llama.rn mmap, which would remove the need for a streaming engine. At minimum it roughly doubles the expert-cache hit rate. | Convert and quantize on the mini (download ~70 GB BF16: **ask the coordinator first**, since it is >5 GB). Eval on BOAR's factual set. Pass if Δ ≥ -3 pt vs full Qwen3.6 at the same bpw and there is no LMK kill at n_ctx 2048. |

Runner-up: re-pull BigMoeOnEdge v0.28 to take the prefix-state restore (13.9 → 4.4 s) and routed-arena ideas into the deep-tier design. NPU prefill helps only on Snapdragon, and the judge phone is probably a Pixel.

## UNKNOWN
- Phone (ARM CPU) tok/s and TTFT for **every** item above. No vendor published Android or Dimensity numbers for Maple, Spark-X2.5, Bonsai 2, the DSpark drafters or Edge0. The "Maple 127 tok/s on iPhone" figure appears in a search snippet only; the source page does not contain it.
- Maple's benchmark numbers (only in card images) and its factual/SimpleQA quality; whether the Q4_K head uses a repacked type on ARM (affects the mmap vs repack RAM trade).
- Whether llama.rn's `spec_type: 'draft-dspark'` reaches the completion path. The code shows only `draft-mtp` driving speculation (`shouldUseMTP`), so I assume a patch is needed, but I have not tested it.
- The ARM microkernel for the tiled k-quant mul_mat (#27851); ARM kernels for Prism ternary in ik_llama.cpp.
- A GSQ-RCO or RAZOR GGUF for Qwen3.6-35B-A3B (none found); RAZOR's effect on knowledge QA (the paper covers reasoning tasks).
- AliceAI-Foundation-80B-A3B: an instruct release, llama.cpp support (KDA + gated attention, `custom_code`), and GGUF sizes.
- Needle 3 benchmark values (SVG only) and whether its runtime works in React Native.
- Community items I did not evaluate: empero-ai "Qwen3.8-2B/4B/9B/35B-A3B-Distill" (Aug-Sep, high downloads; not official Qwen; card numbers not read); RWKV7-G1j/G1k 1.5B-13B (Sep; no benchmark numbers on the card); Cohere tiny-aya thinker (gated, card not readable); Xing4.0-29B-A4B (4B active, above the ≤3B filter; SWE-V 75.0 per vendor).
- Qualcomm GenieX v0.5-v0.7 (Aug-Sep releases) and MediaTek NeuroPilot: no published LLM tok/s found for this window.
- The golem-app Maple PR (#172, "Maple on the 12 GB Android tier") appeared in search but returns 404 (private or deleted repo). Contents unverified.


## Decisions / Options / Tasks

**Decisions (Lantern, reversible)**
- D1. Radar items enter BOAR only through the eval: `vitalik-evalset.jsonl` + v2, measured on device. No catalog change comes from vendor numbers alone. This is the team rule in `models-research/README.md`.
- D2. The "doesn't fit 50 GB" verdict on Qwen3.8-Flash-Next is reconfirmed (smallest ~65 GB).

**Options (for Kiln / coordinator)**
- O1. ~~Maple on the Dimensity 8300~~ → **decided (coordinator, 2026-09-30): Kiln exp-02**, a Mac mini proxy on the factual subset (`handoff-eval.md` §4). Lantern downloads nothing. The Dimensity 8300 is not in the lab, so the device round is a request to r4to/the app maintainer.
- O2. k 8→4 router patch on the deep tier (top 2). It only matters if the deep tier reopens (ADR 0001 §9).
- O3. DSpark on the dense fast tier (top 4). Needs a llama.rn native patch, and the iPhone (1.5B) benefits most.
- O4. Veil: hash-pin every non-backbone table (PLE, n-gram, draft models) in the manifest; measure memory system-wide, not RSS.

**Tasks**
- [x] T1. Radar with 52 rows, each with date, link, number, license, relevance, and status vs team docs.
- [ ] T2. Kiln and Veil get the relevant rows (sent via maestri).
- [ ] T3 (Kiln or coordinator): pick one of top 1/3 to run through `eval:iphone` / the Android benchmark.

**Metric:** 52 table rows, some grouping 2-3 related papers (42 NEW, 10 UPDATE to team docs); 1 item runnable today that matches the thesis shape (Maple); 0 items measured on a phone.
**Next step:** Kiln exp-02, Maple TQ2_0 vs baseline on the 38-item factual subset, run as a Mac mini proxy.
