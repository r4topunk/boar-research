# LFM2.5-8B-A1B web sweep (leads, not conclusions)

Date: 2026-10-19. Sweep agent: Haiku 5.5, read-only web research. Only this file was written.

Tags: **[F]** = primary or vendor page fetched in this sweep (vendor-reported numbers unless stated). **[S]** = search-result snippet or secondary site, not fetched or not verified. Every number below is a lead to check before use in any claim.

Models: LFM2.5-8B-A1B (8.3B total, 1.5B active, 24 layers: 18 double-gated conv + 6 GQA) is the target. LFM2.5-1.2B-Thinking and LFM2-8B-A1B are the siblings.

---

## 0. Summary

- **Vendor headline numbers are strong on instruction following and tau2 telecom, weak on math and knowledge.** Qwen3.5-4B beats LFM2.5-8B-A1B on tau2 retail, BFCL v3 and v4, AIME25 and AIME26 in the vendor's own tables [F].
- **The vendor's own tables disagree on BFCL.** BFCL v3 is 64.36 in Table 1 and 64.79 in Table 3, and BFCL v4 is 48.50 vs 49.73 [F]. Use a range and cite both.
- **Artificial Analysis gives no measured values for this model.** Intelligence Index is 7, labelled "Estimated", "independent evaluation forthcoming", index v4.3.2, rank #79 of 141 [F]. AA also lists a 33k context window against the vendor's 128K [F]. The AA page shows no AA-Omniscience value, so the 63.47 non-hallucination figure remains vendor-cited only [F].
- **Reasoning cannot be turned off, and no budget control is documented** [F, HF page and blog]. The main operational failure mode is the reasoning block, and the vendor's own serving guide says to not cap `max_tokens` [F].
- **Speed claims are vendor-only.** "253 tok/s M5 Max, 146 tok/s Ryzen AI Max+ 395, under 6 GB" and "~30 tok/s on a phone" come from the blog with no device or quantization given for the phone [F]. The one community number on an 8B-A1B is for LFM2 (not 2.5) on a Snapdragon 8 Gen 3 [S].
- **The vLLM guide says all experts stay resident and asks for a 24 GB GPU** [F]. This conflicts with the "under 6 GB" and "8 GB phone" framing and needs a measured reconciliation on a device.

---

## 1. Vendor (Liquid AI blog, HF card, docs, vLLM recipe)

| # | Finding | Value | Tag | URL |
|---|---|---|---|---|
| V1 | Vendor benchmark table, 8B-A1B vs LFM2-8B-A1B | IFEval 91.84 (vs 79.44), IFBench 56.47 (vs 26.00), Multi-IF 79.93 (vs 58.54), MATH500 88.76 (vs 74.80), AIME25 42.53 (vs 20.00) | [F] | https://www.liquid.ai/blog/lfm2-5-8b-a1b |
| V2 | Comparison vs Qwen3.5-4B, Gemma-4-26B-A4B, Qwen3-30B-A3B-Thinking-2507, gpt-oss-20b (vendor table) | IFEval: LFM 91.84 vs Qwen3.5-4B 87.80, gpt-oss 86.73. AIME25: LFM 42.53 vs Qwen3.5-4B 54.28, Gemma 68.67, Qwen3-30B 71.67. MATH500: LFM 88.76 vs Gemma 94.20 | [F] | https://www.liquid.ai/blog/lfm2-5-8b-a1b |
| V3 | Knowledge / hallucination (vendor-cited) | AA-Omniscience Index -24.70 (vs -78.42 for LFM2), accuracy 8.67, non-halluc 63.47 (vs 7.46). Qwen3.5-4B index -51.53 (non-halluc 16.99) | [F] | https://www.liquid.ai/blog/lfm2-5-8b-a1b |
| V4 | Speed claims (vendor, CPU laptop class) | "253 tok/s on an M5 Max and 146 on a Ryzen AI Max+ 395 while staying under 6 GB" | [F] | https://www.liquid.ai/blog/lfm2-5-8b-a1b |
| V5 | Phone claim (vendor, no device, quant or context given) | "It even holds ~30 tokens/s on a phone." | [F] | https://www.liquid.ai/blog/lfm2-5-8b-a1b |
| V6 | GPU throughput (vendor, SGLang 0.5.12, BF16, 1024 in / 256 out) | "18.5K output tokens per second at high concurrency" on a single H100 | [F] | https://www.liquid.ai/blog/lfm2-5-8b-a1b |
| V7 | Reasoning control | "reasoning-only model", "explicit chain of thought before its final answer". No on/off switch and no thinking budget are documented in blog, HF card or docs | [F] | https://huggingface.co/LiquidAI/LFM2.5-8B-A1B ; https://docs.liquid.ai/lfm/models/lfm25-8b-a1b |
| V8 | Loop-suppression training (vendor) | RL reward "discourages excessive use of common loop-inducing restart words like 'Wait…'" | [F] | https://www.liquid.ai/blog/lfm2-5-8b-a1b |
| V9 | Sampling defaults (card) | temperature 0.2, top_k 80, repetition_penalty 1.05; top_p not given. SGLang text default is temperature 0.3 | [F] | https://huggingface.co/LiquidAI/LFM2.5-8B-A1B ; https://docs.liquid.ai/lfm/models/lfm25-8b-a1b |
| V10 | Chat template and special tokens | ChatML-like, `<|startoftext|>`, `<|im_start|>`, `<|im_end|>`, `<|tool_call_start|>`, `<|tool_call_end|>`. Tools passed as JSON in system prompt or `tools=` in `apply_chat_template` | [F] | https://huggingface.co/LiquidAI/LFM2.5-8B-A1B |
| V11 | Tool-call format | Default is Pythonic calls between tool-call tokens; can be overridden with a system-prompt instruction to emit JSON. Tool results via `tool` role | [F] | https://huggingface.co/LiquidAI/LFM2.5-8B-A1B |
| V12 | Serving flags | vLLM: `--reasoning-parser qwen3 --enable-auto-tool-choice --tool-call-parser lfm2`. SGLang: `--tool-call-parser lfm2`, `--reasoning-parser qwen3`. Parser turns Pythonic call into `tool_calls` array | [F] | https://recipes.vllm.ai/LiquidAI/LFM2.5-8B-A1B ; https://docs.liquid.ai/lfm/models/lfm25-8b-a1b |
| V13 | max_tokens advice (vendor) | "Leave `max_tokens` unset so the `<think>` block and answer aren't truncated mid-stream." | [F] | https://recipes.vllm.ai/LiquidAI/LFM2.5-8B-A1B |
| V14 | Empty reasoning is expected on simple prompts (vendor) | "a simple prompt may be answered directly, in which case `reasoning` is empty." | [F] | https://recipes.vllm.ai/LiquidAI/LFM2.5-8B-A1B |
| V15 | Memory sizing (vendor) | "MoE keeps every expert resident in VRAM, so size the GPU for the full ~8B of weights"; prerequisite 1x GPU with at least 24 GB VRAM; vLLM 0.23.0+ | [F] | https://recipes.vllm.ai/LiquidAI/LFM2.5-8B-A1B |
| V16 | Structured outputs | "The model does not see the schema itself — put semantic instructions in the system prompt." | [F] | https://recipes.vllm.ai/LiquidAI/LFM2.5-8B-A1B |
| V17 | Limitations (vendor) | "not the best fit for heavy programming or knowledge-intensive question answering without retrieval"; fine-tuning recommended for specific use cases | [F] | https://huggingface.co/LiquidAI/LFM2.5-8B-A1B |
| V18 | Training budget | 38 trillion tokens (HF card). Secondary sites say 34T, but that came from LFM2.5-2.6B coverage and is unverified for this model | [F] / [S] | https://huggingface.co/LiquidAI/LFM2.5-8B-A1B |
| V19 | Context | 128K on vendor card; 33k on AA page. Unresolved | [F] both | https://huggingface.co/LiquidAI/LFM2.5-8B-A1B ; https://artificialanalysis.ai/models/lfm2-5-8b-a1b |
| V20 | DSpark speculative drafter (vendor) | 328M drafter, "~2.5x faster decoding" in SGLang with identical outputs; llama.cpp needs a recent build with `draft-dspark`, `-hfd`, `--spec-draft-n-max 10` | [F] | https://huggingface.co/LiquidAI/LFM2.5-8B-A1B |
| V21 | Release and formats | Blog dated May 28, 2026. GGUF, MLX 8-bit, ONNX, 102 quantizations. Install via `brew install llama.cpp` and `llama-cli -hf LiquidAI/LFM2.5-8B-A1B-GGUF` | [F] | https://huggingface.co/LiquidAI/LFM2.5-8B-A1B |
| V22 | Tokenizer fix for llama.cpp tool calls | Users told to re-download tokenizer files and GGUFs were re-converted | [S] | https://huggingface.co/LiquidAI/LFM2.5-8B-A1B-GGUF (via search snippet, not fetched) |
| V23 | LEAP / edge SDK | Not mentioned on the HF card or the docs page | [F] (absence) | https://docs.liquid.ai/lfm/models/lfm25-8b-a1b |

**Sibling: LFM2.5-1.2B-Thinking** [F] from https://www.liquid.ai/blog/lfm2-5-1-2b-thinking-on-device-reasoning-under-1gb and https://docs.liquid.ai/lfm/models/lfm25-1.2b-thinking.md

| # | Finding | Value | Tag |
|---|---|---|---|
| S1-1 | Scores vs Qwen3-1.7B thinking (5-run mean, temp 0.6) | MMLU-Pro **49.65 vs 56.68 (LFM loses)**; IFEval 88.42 vs 71.65; IFBench 44.85 vs 25.88; BFCLv3 56.97 vs 55.41; AIME25 31.73 vs 36.27; GPQA 37.86 vs 36.93 | [F] |
| S1-2 | Device speed (vendor table) | Galaxy S25 Ultra CPU llama.cpp Q4_0: prefill 336, decode 70, 720 MB. Snapdragon 8 Elite NPU (NexaML): decode 82. Apple A19 Pro CPU (Cactus INT8): decode 64, 1128 MB | [F] |
| S1-3 | Doom-looping rate (vendor) | Repetitive-text failure 15.74% at mid-training, 0.36% after RLVR (their prompt set) | [F] |
| S1-4 | Sampling for the 1.2B differs from the 8B | temperature 0.05, top_k 50, repetition_penalty 1.05 (card) vs 8B's 0.2 / 80 / 1.05. Context 32K | [F] |
| S1-5 | Vendor use recommendation | "agentic and reasoning-heavy tasks (e.g., tool use, math, programming)"; for chat use the Instruct variant | [F] |

**Sibling: LFM2-8B-A1B** [F] from the LFM2.5 blog's "What changed" table: BFCLv3 45.07, BFCLv4 25.52, Tau2 Telecom 13.60, Tau2 Retail 7.02, AA-Omniscience -78.42 [F]. The LFM2 launch blog and tech report (arXiv 2511.23404) were seen in search results but not fetched [S].

---

## 2. Agentic (tool use, tau-bench, BFCL, When2Call, RAG)

| # | Finding | Value | Tag | URL |
|---|---|---|---|---|
| A1 | tau2 (vendor) | Tau2 Telecom **88.07** (LFM2 13.60); Tau2 Retail **39.82** (LFM2 7.02). Vendor table shows Qwen3.5-4B Retail **71.93**, Qwen3-30B-A3B-Thinking Retail 56.14, gpt-oss 53.51 | [F] | https://www.liquid.ai/blog/lfm2-5-8b-a1b |
| A2 | BFCL (vendor, two versions disagree) | BFCLv3 64.36 (Table 1) vs 64.79 (Table 3); BFCLv4 48.50 vs 49.73. Qwen3.5-4B v3 71.06, v4 54.01; Gemma-4-26B v4 55.87 | [F] | https://www.liquid.ai/blog/lfm2-5-8b-a1b |
| A3 | BFCL 1.2B-Thinking (vendor, custom Liquid handler for tool-use template) | BFCLv3 56.97 vs Qwen3-1.7B thinking 55.41. Caveat: custom handler, so not directly comparable to leaderboard | [F] | https://www.liquid.ai/blog/lfm2-5-1-2b-thinking-on-device-reasoning-under-1gb |
| A4 | Tool-use demo (vendor) | "67 tools across 13 MCP servers" on a single laptop (Localcowork demo); "chains tool calls" | [F] | https://www.liquid.ai/blog/lfm2-5-8b-a1b |
| A5 | Tool-call parser | `--tool-call-parser lfm2` in vLLM and SGLang; Pythonic calls by default | [F] | https://recipes.vllm.ai/LiquidAI/LFM2.5-8B-A1B |
| A6 | Native function calling (docs claim) | "Native function calling for agentic workflows" | [F] | https://docs.liquid.ai/lfm/models/lfm25-8b-a1b |
| A7 | When2Call | No LFM numbers found. Benchmark defined in NAACL 2025; community F1 16.6–37.8 on a secondary alphaXiv page, date and models unconfirmed | [S] | https://alphaxiv.org/benchmarks/harvard-university/when2call ; https://aclanthology.org/people/ameya-sunil-mahabaleshwarkar/unverified/ |
| A8 | RAG | Vendor says the 1.2B is for "agentic tasks, data extraction, and RAG" and the 8B says "not … without retrieval". No RAG benchmark table found for either | [F] (claim only) | https://docs.liquid.ai/lfm/models/lfm25-1.2b-thinking.md ; https://huggingface.co/LiquidAI/LFM2.5-8B-A1B |
| A9 | Structured output | Semantic instructions only; the model does not see the schema | [F] | https://recipes.vllm.ai/LiquidAI/LFM2.5-8B-A1B |

Note for agentic use: the vendor table shows LFM2.5-8B's tau2 Telecom (88.07) far above Qwen3-30B-A3B (21.93) but its tau2 Retail (39.82) far below Qwen3.5-4B (71.93). That split could be a domain effect or a harness effect. Check the tau2 harness and whether it was run with the same tool-call parser.

---

## 3. Independent (Artificial Analysis, community speed and memory, failure modes)

| # | Finding | Value | Tag | URL |
|---|---|---|---|---|
| I1 | Artificial Analysis Intelligence Index | 7, labelled "Estimated"; "Estimate (independent evaluation forthcoming)"; index v4.3.2; rank #79 of 141; below the median of 8 | [F] | https://artificialanalysis.ai/models/lfm2-5-8b-a1b |
| I2 | AA-listed specs | Reasoning model; text-only; **33k context**; 8.3B total / 1.5B active; "lfm 1.0" licence. Speed, cost, verbosity: "Unknown" | [F] | https://artificialanalysis.ai/models/lfm2-5-8b-a1b |
| I3 | Third-party index value | 8.32 (verified 2026-07-21) on benchlm / benchlist; differs from AA's own 7 | [S] | https://benchmarklist.com/models/lfm2.5-8b-a1b/ |
| I4 | AA-Omniscience across sites | Vendor -24.70; tinyweights -24.70; BenchLM -33.3%. The AA page does not show it. Non-hallucination 63.47 is vendor-cited only | [F] vendor / [S] BenchLM | https://www.liquid.ai/blog/lfm2-5-8b-a1b ; https://www.benchlm.ai/models/lfm2-5-8b-a1b |
| I5 | Community phone speed, Snapdragon 8 Gen 3, **LFM2-8B-A1B (not 2.5)** Q4_K_M, 16 GB device | 35 tok/s generation at low context, ~28 tok/s at ~1000 tokens; prefill 85 tok/s. One user, compiled llama.cpp, not a controlled benchmark | [S] | https://redlib.groet-infra.nl/r/LocalLLaMA/s/QrYY3jYp54 (r/LocalLLaMA, Jan 2026; the page returned HTTP 502 when fetched, so this is from the search snippet) |
| I6 | Mac decode, LFM2-8B-A1B 3-bit, M4 (10c, 16 GB), context 4k | Prefill 817.7 tok/s, decode 93.7 tok/s, peak 5.2 GB, TTFT 5011 ms. Title says LFM2, not LFM2.5 | [F] | https://omlx.ai/benchmarks/qvap66h3 |
| I7 | Phone "~30 tok/s" | No device, quant or context. Repeated by German and Spanish blogs; no primary measurement found | [S] (copy of vendor V5) | https://pasqualepillitteri.it/de/news/3758/liquid-ai-lfm2-5-8b-a1b-on-device-moe-aktive-parameter |
| I8 | Chat template risk | Third-party GGUF repo advises `--jinja`, because without it the model "can emit malformed turns" | [S] | https://huggingface.co/AlexAtomic/lfm25-8b-a1b-GGUF |
| I9 | Empty answer / truncation | Vendor: reasoning block is expected, `max_tokens` cap truncates it; empty `reasoning` on simple prompts is normal. No bug report found | [F] vendor | https://recipes.vllm.ai/LiquidAI/LFM2.5-8B-A1B |
| I10 | Repetition | Vendor sampling 0.2 / 80 / 1.05 and RL against "Wait…" loops; 1.2B doom-loop rate 15.74% → 0.36%. No independent measurement for the 8B | [F] vendor | https://www.liquid.ai/blog/lfm2-5-8b-a1b ; https://www.liquid.ai/blog/lfm2-5-1-2b-thinking-on-device-reasoning-under-1gb |
| I11 | Memory on device | Vendor "under 6 GB" (laptop, not phone); vLLM "all experts resident", 24 GB VRAM prerequisite; third-party GGUF guide says Q4 ~4.8 GB on disk and "fits 8 GB RAM" (unverified); one aggregator estimates ~25 GB | [F] / [S] | https://recipes.vllm.ai/LiquidAI/LFM2.5-8B-A1B ; https://runaihome.com/blog/lfm2-5-8b-local-ai-hardware-guide-2026/ |
| I12 | 1.2B-Thinking independent memory note | Reddit commenter disputes sub-1 GB claim and says at least 2 GB needed | [S] | (search snippet only; no URL fetched) |
| I13 | 1.2B-Thinking AA-Omniscience | -83 vs Qwen3-1.7B thinking -78 (secondary coverage) | [S] | https://www.deeplearning.ai/the-batch/liquid-ais-small-reasoning-model-mixes-attention-with-convolutional-layers-for-efficiency |

---

## 4. Gaps (checked, not found, or unverified)

| # | Gap | What was tried | Next step |
|---|---|---|---|
| G1 | MMLU-Pro for LFM2.5-8B-A1B | Vendor 8B table omits it; BenchLM says "coming soon" [S] | Check the blog image charts or a later vendor update |
| G2 | LFM2.5 technical report | Searches found only secondary coverage | Look for an arXiv or vendor tech report for LFM2.5 specifically; LFM2 report is arXiv 2511.23404 (seen, not fetched) |
| G3 | When2Call numbers for any LFM model | Search only returned benchmark defs and leaderboard shells | Pull the When2Call repo/leaderboard directly |
| G4 | RAG benchmark numbers | None in vendor pages; only claims | Look for a Liquid RAG eval or independent RAG benchmark |
| G5 | Android llama.cpp numbers for LFM2.5-8B-A1B | None found. Only iPhone/phone "~30 tok/s" copies | Search r/LocalLLaMA and llama.cpp GitHub discussions for "LFM2.5" + Android; or run a device test ourselves |
| G6 | Community failure reports (empty answers, loops) for 8B-A1B | Reddit search gave nothing; HF GGUF discussions page not reachable from search | Fetch https://huggingface.co/LiquidAI/LFM2.5-8B-A1B-GGUF/discussions directly; retry Reddit later (redlib returned 502) |
| G7 | LEAP / edge SDK notes | Not on HF card or docs | Check LEAP docs site directly |
| G8 | LFM2-8B-A1B vendor launch page and its tau/BFCL | Search gave the URL (liquid.ai/blog/lfm2-8b-a1b-an-efficient-on-device-mixture-of-experts) but it was not fetched | Fetch it |
| G9 | Independent BFCL leaderboard entry | Not checked | Check the BFCL leaderboard for LFM2.5 directly |
| G10 | Context length conflict (128K vs 33k) | Two pages say different things | Test with a long-context prompt on llama.cpp |
| G11 | Phone "under 6 GB" vs vLLM "24 GB VRAM" | Vendor said laptop; no phone memory measure | Measure RSS on a phone; the one measured RSS (I6) is for LFM2 on a Mac |
| G12 | The tinyweights and benchlm pages | tinyweights DNS failed; BenchLM pages not fetched | Retry later |
| G13 | Sampling for thinking on tool use | Vendor recommends 0.2 / 80; the 1.2B recommends 0.05 / 50 | Test both on our tool-call set |

---

## 5. Leads for the next step (not conclusions)

- L1: the vendor's own tables place tau2 Retail well below Qwen3.5-4B. Test the 8B on our tool-call set before trusting the telecom number.
- L2: the AA index of 7 is an estimate. Wait for AA's measured run before citing it.
- L3: the reasoning block has no off switch. Measure the token cost of thinking on simple tool calls, since vendor says empty reasoning is expected for simple prompts and the cap must stay unset.
- L4: the phone speed number has no device. The only measured community speed is LFM2 (not 2.5) on a Snapdragon 8 Gen 3 at about 35 tok/s, one user report.
