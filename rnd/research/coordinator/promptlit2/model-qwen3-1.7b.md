# Qwen3-1.7B: web research sweep (leads, not conclusions)

Date: 2026-10-19. Scope: Qwen3-1.7B as the BOAR lite tier (llama.cpp Q4_K_M, thinking off). Read-only sweep; nothing here is verified against our harness.

Tags: **[F]** = page or paper body fetched and read by the sweeper. **[S]** = search-result snippet or secondary/aggregator page only, not opened. Numbers marked [S] conflict across sources in several places (see Gaps).

---

## 1. Vendor (model card, tech report, modes, sampling)

| # | Finding | Value | Tag | URL |
|---|---|---|---|---|
| V1 | Params, layers, context, license | 1.7B total, 1.4B non-embedding, 28 layers, 32,768 ctx, Apache-2.0 | [F] | https://huggingface.co/Qwen/Qwen3-1.7B |
| V2 | Hybrid thinking, default on | `enable_thinking` defaults to True; hard off = `enable_thinking=False` in `apply_chat_template`. `/no_think` soft switch is ignored when `enable_thinking=False` | [F] | https://huggingface.co/Qwen/Qwen3-1.7B |
| V3 | Sampling, thinking mode | T 0.6, top-p 0.95, top-k 20, min-p 0; "DO NOT use greedy decoding" | [F] | https://huggingface.co/Qwen/Qwen3-1.7B |
| V4 | Sampling, non-thinking mode | T 0.7, top-p 0.8, top-k 20, min-p 0 | [F] | https://huggingface.co/Qwen/Qwen3-1.7B |
| V5 | llama.cpp listed as supported local runtime; card points tool use to Qwen-Agent (no Hermes wording on the page) | Text: "Ollama, LMStudio, MLX-LM, llama.cpp, and KTransformers" | [F] | https://huggingface.co/Qwen/Qwen3-1.7B |
| V6 | Tech report, Table 19 (1.7B, thinking) | MMLU-Redux 73.9, GPQA-Diamond 40.1, **BFCL v3 56.6**, LiveCodeBench v5 33.2, MATH-500 93.4, AIME'24 48.3, AIME'25 36.8 | [F] | https://arxiv.org/html/2505.09388v1 |
| V7 | Tech report, Table 20 (1.7B, non-thinking) | MMLU-Redux 64.4, GPQA-Diamond 28.6, **BFCL v3 52.2**, LiveCodeBench v5 11.6, MATH-500 73.0, AIME'24 13.4, AIME'25 9.8 | [F] | https://arxiv.org/html/2505.09388v1 |
| V8 | Tech report, Sec 4.6 sampling | Thinking: T 0.6 / top-p 0.95 / top-k 20. Non-thinking: T 0.7 / top-p 0.8 / top-k 20 / presence penalty 1.5 | [F] | https://arxiv.org/html/2505.09388v1 |
| V9 | Repetition: greedy discouraged; presence penalty 1.5 suggested for repetition (0.6B card) | Secondary copies only | [S] | https://huggingface.co/Qwen/Qwen3-1.7B-MLX-8bit ; https://friendli.ai/models/yrrhall/Qwen3-0.6B |
| V10 | Tech report: 1.7B-Base beats larger Qwen2.5 bases on over half of benchmarks | Base model, not the chat model | [S] | https://arxiv.org/pdf/2505.09388 |

Notes for us:
- The 1.7B table is in the arXiv HTML (v1), not on the HF card. The card has no benchmark table for 1.7B.
- Our "thinking off" = hard switch (`enable_thinking=False`), not `/no_think`. Confirm our llama.cpp chat template actually passes that kwarg (not covered by this sweep).
- Tool-call template format (Hermes-style tags, or other) was NOT confirmed from a fetched page. Gap.

---

## 2. Agentic (tool calling, BFCL, tau-bench, When2Call, agent papers, RAG use)

| # | Finding | Value | Tag | URL |
|---|---|---|---|---|
| A1 | BFCL v3, official tech report (thinking vs non-thinking) | 56.6 thinking / 52.2 non-thinking (see V6, V7) | [F] | https://arxiv.org/html/2505.09388v1 |
| A2 | TinyLLM (edge agentic evaluation), Qwen3-1.7B prompted | BFCL overall ~55.5, multi-turn ~16.9 (snippet). Fetched abstract does **not** name Qwen3-1.7B, so this row is unconfirmed | [S] (conflict) | https://arxiv.org/pdf/2511.22138 |
| A3 | TinyLLM, Qwen3-4B for contrast | BFCL overall 62.04 (snippet) | [S] | https://arxiv.org/pdf/2511.22138 |
| A4 | BFCL and tau-bench via aggregators (disagree) | BFCL "28.4 overall" with AST non-live 82.9 / live 74.6 / multi-turn 11.0 vs "BFCL-v3 54.7" on the same page; tau-bench v2 26.0 (Reasoning) on llmbase | [S] | https://benchmarklist.com/models/qwen3-1.7b-5/ ; https://llmbase.ai/compare/qwen3-1.7b-instruct-reasoning,qwen3-4b-instruct/ |
| A5 | When2Call: tool-call abstention benchmark (NVIDIA; multiple choice; macro F1 over 4 actions incl. "cannot answer") | Community models F1 16.6–37.8 (snippet) | [S] | https://arxiv.org/pdf/2504.18851 ; https://alphaxiv.org/benchmarks/harvard-university/when2call |
| A6 | Constrained-decoding preprint, Qwen3-0.6B/1.7B/4B on When2Call | Mean abstention change about −14.7 pts, tool selection about +30 pts (constrained decoding makes models call tools more) | [S] | https://arxiv.org/pdf/2608.13959 |
| A7 | Other preprint, small quantized Qwen (0.5B, 1.5B) | Never abstained on 128 should-abstain items (one fixed prompt) | [S] | https://arxiv.org/pdf/2604.01202 |
| A8 | When2Tool (tool-need decision, 18 envs) lists Qwen3-1.7B | No number pulled | [S] | https://benchmarklist.com/models/qwen3-1.7b-when2tool/ |
| A9 | AgentFloor (30 tasks, 0.27B–32B): suggests a capability threshold between Qwen3-1.7B and 4B for executable tool calls | Mirror only; title/venue not verified | [S] | https://benchmarklist.com (mirror pages) |
| A10 | Fine-tuned Qwen3-1.7B for restaurant tool calls (vendor-side, not zero-shot) | LLM-judge 0.866, staged_tool_call 0.765 (S1 baseline). Not comparable to zero-shot | [S] | https://featherless.ai/models/distillabs/tft-benchmark-s1-tft-Qwen3-1.7B |
| A11 | Local tool-calling practical eval (Docker blog) | Not opened | [S] | https://www.docker.com/blog/local-llm-tool-calling-a-practical-evaluation/ |

Read-across for us: the BFCL overall on 1.7B is between 28 and 57 depending on source. Multi-turn is the weak spot in every source that breaks it out. Abstention (know when not to call) looks weak in several preprints, but none is peer-reviewed or uses our prompt.

---

## 3. Independent (AA, leaderboards, hallucination/faithfulness, phone speed, failure modes)

| # | Finding | Value | Tag | URL |
|---|---|---|---|---|
| I1 | Artificial Analysis Intelligence Index, Qwen3 1.7B reasoning | "estimated" 13 (Mar 2026 AA article snippet). Qwen3.5-2B (reasoning) 16, Qwen3.5-0.8B 9, Qwen3-0.6B 6.5 | [S] | https://artificialanalysis.ai/articles/qwen3-5-small-models |
| I2 | AA model page for 1.7B reasoning (German locale, search snippet) | Intelligence Index shown as "Estimate (independent evaluation forthcoming)" | [S] | https://artificialanalysis.ai/de/models/qwen3-1.7b-instruct-reasoning |
| I3 | Benchmarklist mirror of AA-style scores (conflicts with I1) | Intelligence Index 41.1 (non-reasoning) / 57.0 (reasoning); AA-Omniscience −83.47 (non-reasoning) / −77.2 (reasoning), "verified 2026-07-10" | [S] (conflict) | https://benchmarklist.com/models/qwen3-1.7b/ ; https://benchmarklist.com/models/qwen3-1.7b-2/ |
| I4 | AA-Omniscience metric definition: −100..100, wrong answers penalized, refusal not penalized, negative = wrong > right | Metric definition only; 1.7B hallucination rate not found | [S] | https://benchmarklist.com/models/qwen3-1.7b-2/ |
| I5 | OCC-RAG: Qwen3-1.7B fine-tuned for faithful RAG | Memorization ratio baseline 12.7 (8.3, unclear parenthetical) → tuned 5.0; refusal accuracy 87.2 for tuned. Baseline row needs the paper | [S] | https://arxiv.org/pdf/2606.00683 |
| I6 | FaithEval (ICLR 2025): faithfulness to counterfactual/noisy context | Benchmark, no 1.7B number pulled | [S] | https://arxiv.org/html/2410.03727v3 |
| I7 | FaithJudge (RAG hallucination eval, human-annotated few-shot judge) | No Qwen3-1.7B entry seen in snippets | [S] | https://arxiv.org/html/2505.04847v2 |
| I8 | Phone speed, vendor (Qualcomm AI Hub, llama.cpp-based runtime, **q4_0 not Q4_K_M**) | Snapdragon 8 Elite Gen 5: 35–48 tok/s at 512 ctx, 23–28 tok/s at 4096; TTFT 0.07–1.7 s; no RAM reported; no Pixel device | [S] | https://huggingface.co/qualcomm/Qwen3-1.7B ; https://aihub.qualcomm.com/mobile/models/qwen3_1_7b |
| I9 | Memory estimate, not measured on phone | ~1.8 GB at Q4_K_M, up to 4.5 GB at 41K ctx (calculator) | [S] | https://partimus.com/en/ai-language-models/qwen3-1-7b/ (calculator, unverified) |
| I10 | Desktop/Apple community runs (not Android) | M4 Pro 105–171 tok/s, 1.7–2.4 GB peak | [S] | https://omlx.ai/benchmarks/w69i19dw |
| I11 | Repetition in smaller Qwen3 (distillation case, non-English) | Small model repeated reasoning fragments often; poster says the card's presence-penalty suggestion can hurt | [S] | https://huggingface.co/papers/2505.09388 (HF discussion) |
| I12 | Language mixing rises with a higher presence penalty | Slight performance drop reported (secondary copy of official guidance) | [S] | https://app.alphaneural.io/models/rahul7star/Xd |
| I13 | Soft-switch behaviour: last `/think` or `/no_think` wins in multi-turn | Secondary (friendli mirror) | [S] | https://friendli.ai/models/Qwen/Qwen3-0.6B-MLX-4bit |
| I14 | Thinking leak / `/no_think` leak in small models | No GitHub issue found | gap | — |

Read-across: the only phone speed number is a vendor-side q4_0 run on flagship silicon, not our quant or our class of device. Our Q4_K_M Android number has to be measured. The AA index for this model is an estimate, not a verified score.

---

## Qwen3.5 small models (0.8B / 2B), only where sources compare them

| Finding | Value | Tag | URL |
|---|---|---|---|
| AA Intelligence Index (reasoning): Qwen3.5-2B 16 vs Qwen3-1.7B estimated 13; Qwen3.5-0.8B 9 vs Qwen3-0.6B 6.5 | Mar 5 2026 article | [S] | https://artificialanalysis.ai/articles/qwen3-5-small-models |
| All Qwen3.5 small models: Apache 2.0, 262K ctx, native vision, marketed for edge | Vendor claim via secondary | [S] | https://gigazine.net/gsc_news/en/20260303-qwen-3-5-small |
| 2B vs 0.8B composite reasoning/coding (no 1.7B row) | llmbase, secondary | [S] | https://llmbase.ai/compare/qwen3-5-2b,qwen3-8b-instruct-reasoning/ |

---

## Gaps (what the sweep did not settle)

1. **BFCL 1.7B**: 28.4 vs 54.7 vs 56.6 (tech report) vs 52.2 non-thinking. Need the official BFCL leaderboard entry and the mode used.
2. **TinyLLM Qwen3-1.7B row (55.5 / 16.9)**: the fetched abstract does not name Qwen3-1.7B. Read the full PDF tables before citing.
3. **AA numbers**: 13 (estimate, article) vs 41.1 / 57.0 (mirror). Need the AA page for the exact model entry; AA-Omniscience hallucination rate for 1.7B not found.
4. **Tool-call template**: Hermes-style or other format not confirmed on any fetched page; check the chat template in the GGUF / tokenizer config.
5. **llama.cpp thinking-off**: how to pass `enable_thinking=False` through llama-server (chat-template kwargs) is not covered.
6. **Phone**: no Android/Pixel Q4_K_M llama.cpp number for 1.7B; RAM on phone not measured by anyone found.
7. **When2Call Qwen3-1.7B row**: original paper table not opened; abstention numbers above come from preprint snippets.
8. **OCC-RAG baseline parenthetical** (12.7 vs 8.3): unexplained in snippet.
9. **Thinking leaks and language mixing** for the non-thinking mode: only secondary mentions; no GitHub-issue evidence found.

Summary counts: Angle 1 = 10 findings (7 fetched). Angle 2 = 11 findings (2 fetched, rest snippets). Angle 3 = 14 findings (none verified against a primary page). Every angle has at least 3 findings with URLs.
