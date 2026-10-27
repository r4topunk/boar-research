# Qwen3-4B-Instruct-2507: web sweep (leads, not conclusions)

Date: 2026-10-19. Read-only sweep, one output file. Tags: [F] = page read in full (WebFetch), [S] = search snippet only. Every number is quoted from its source; self-reported vs independent is marked. Nothing here was re-run locally.

## TL;DR

- Vendor card (self-reported): 4.0B params, 262,144-token native context, Apache-2.0, non-thinking only, sampling temp 0.7 / top_p 0.8 / top_k 20 / min_p 0. Tool calling is pointed at Qwen-Agent; no raw tool-call format and no llama.cpp notes on the card.
- Our engine uses temp 0.7 / top_k 40 / top_p 0.95 / min_p 0.05 (per CLAUDE.md). That differs from the card on top_k, top_p and min_p. Worth a check, not a conclusion.
- Independent numbers are thin. Artificial Analysis lists the Intelligence Index as an estimate (7, v4.3.2). A third-party page shows AA-Omniscience -59.63, but it conflicts with AA's own page, so treat it as unconfirmed.
- No SimpleQA or Vectara hallucination figure for this checkpoint was found.
- No phone llama.cpp tok/s or RSS number for this checkpoint was found. The only mobile data point is a Qualcomm AI Hub page with no numbers shown.

## 1. Vendor

| # | Finding | Value / quote | Tag | Source |
|---|---|---|---|---|
| V1 | Size, context, license, mode | 4.0B total, 3.6B non-embedding; 36 layers; GQA 32 Q / 8 KV heads. Context "262,144 natively"; suggests dropping to 32,768 on OOM. Apache-2.0. No `<think>` blocks; non-thinking only. | [F] | https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 |
| V2 | Benchmark table, 2507 column (self-reported) | MMLU-Pro 69.6; MMLU-Redux 84.2; GPQA 62.0; SuperGPQA 42.8; AIME25 47.4; LiveBench 20241125 63.0; LiveCodeBench v6 35.1; IFEval 83.4; Arena-Hard v2 43.4; Creative Writing v3 83.5; BFCL-v3 61.9; TAU1-Retail 48.7; TAU2-Retail 40.4; TAU2-Airline 24.0; TAU2-Telecom 13.2; MultiIF 69.0; PolyMATH 31.1. The card's comparison column for Qwen3-4B non-thinking: MMLU-Pro 58.0, GPQA 41.7, IFEval 81.2, BFCL-v3 57.6. | [F] | https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 |
| V3 | Sampling recommendations | Temperature 0.7, TopP 0.8, TopK 20, MinP 0. presence_penalty 0 to 2 (higher can cause language mixing). Output length 16,384 for most queries. | [F] | https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 |
| V4 | Tool calling | Card recommends Qwen-Agent (bundled templates and parsers) with an OpenAI-compatible endpoint; no raw tool-call format given. | [F] | https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 |
| V5 | llama.cpp / GGUF | Card gives no GGUF instructions; lists llama.cpp, Ollama, LM Studio, MLX-LM, KTransformers as supported and links 351 quantized variants. Transformers < 4.51.0 raises `KeyError: 'qwen3'`. | [F] | https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 |
| V6 | Hermes-style tool format for llama.cpp | Dynamo parser docs group Qwen3-Instruct with the Hermes parser (`<tool_call>` JSON). llama.cpp docs list the Hermes handler for Hermes 2/3 and Qwen 2.5, not Qwen3; unrecognized templates fall back to the generic handler. Whether the 2507 template is detected is NOT confirmed. Check with `llama-server --jinja` logs. | [S] | https://docs.dynamo.nvidia.com/dynamo/parsing/tool-call-parsing.md ; https://mintlify.com/ggml-org/llama.cpp/advanced/function-calling |
| V7 | SimpleQA | Not reported on the card. Card's evaluation_results list MMLU-Pro 69.6 and GPQA Diamond 62. | [F] | https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 |

Gap for vendor: no Qwen technical report section specific to 2507 was read; the Qwen3 tech report (arXiv 2505.09388) covers the original family, not this checkpoint.

## 2. Agentic (tool calling, agent benchmarks, on-device agents)

| # | Finding | Value / quote | Tag | Source |
|---|---|---|---|---|
| A1 | BFCL-v3 (self-reported) | 61.9 for 2507 vs 57.6 for Qwen3-4B non-thinking, 58.6 for Qwen3-30B-A3B non-thinking, 53.0 GPT-4.1-nano. Card notes agent numbers may depend on Qwen-Agent. | [F] | https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 |
| A2 | TAU2 (self-reported, mirrored) | TAU2-Retail 40.4 (vs 28.1 non-thinking 4B); TAU2-Airline 24.0 (vs 12.0); TAU2-Telecom 13.2 (lower than 17.5 for 4B non-thinking). TAU1-Retail 48.7. | [F] | https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 ; mirror listing https://friendli.ai/models/E2M/mymodel [S] |
| A3 | Official BFCL leaderboard | Page fetched (last updated 2026-04-12, commit f7cf735, bfcl-eval 2025.12.17) but the table did not render; no Qwen3-4B row was readable. Gap: needs a manual check. | [F] | https://gorilla.cs.berkeley.edu/leaderboard.html |
| A4 | When2Tool (secondary) | Benchmarklist lists a Qwen3-4B Instruct result with an average accuracy change of -1.9, labelled self-reported. Treat as a lead; check the original paper. | [S] | https://benchmarklist.com/models/qwen3-4b-inst.-when2tool/ |
| A5 | Tool-call fine-tune of Qwen3-4B (community) | wesjos/Qwen3-4B-toolcall: ToolBench Action Exact Match 0.1667 to 0.3182 after fine-tune. Vendor-reported by the fine-tuner, not an independent eval, and not 2507. | [S] | https://featherless.ai/models/wesjos/Qwen3-4B-toolcall |
| A6 | When2Call / NESTFUL | When2Call (NAACL 2025) and NESTFUL (EMNLP 2025) exist; no paper found that reports Qwen3-4B on either. GPT-4o is the best NESTFUL model at 28% full sequence match. Gap. | [S] | https://aclanthology.org/2025.naacl-long.174 ; https://aclanthology.org/2025.emnlp-main.1702 |
| A7 | Agent hallucination benchmark (method lead) | MIRAGE-Bench: LLM agent hallucination benchmark (arXiv 2507.21017). Not checked for Qwen3-4B. | [S] | https://arxiv.org/pdf/2507.21017 |
| A8 | On-device agent reports | No on-device agent report with this checkpoint found. Gap. | - | - |

## 3. Independent (leaderboards, factuality, speed and memory, failure modes)

| # | Finding | Value / quote | Tag | Source |
|---|---|---|---|---|
| I1 | Artificial Analysis, own page | Intelligence Index v4.3.2 = 7, marked ESTIMATE ("independent evaluation forthcoming"); #2 of 29 non-reasoning open-weight models in the Tiny (<=4B) class; class median 5. Output speed N/A; cost N/A. Page deprecated in favour of Qwen3.5 4B. No individual scores shown. | [F] | https://artificialanalysis.ai/models/qwen3-4b-2507-instruct |
| I2 | AA-Omniscience (conflicting third-party value) | Benchmarklist shows AA-Omniscience -59.63 and a Tau2-Telecom 26.6% and Intelligence Index 12.88, all dated 2026-06 to 2026-10. These disagree with the AA page (index 7, tau2 not shown, Qwen's own tau2-telecom 13.2). Likely a different variant or a mis-mapped row. UNCONFIRMED. AA-Omniscience definition: correct answers rewarded, hallucinations penalised, refusals not penalised, range -100 to 100. | [F] for the page, [S] for the definition | https://benchmarklist.com/models/qwen3-4b-2507-instruct/ ; https://artificialanalysis.ai/models/qwen3-4b-2507-instruct |
| I3 | Factuality, SimpleQA | No Qwen3-4B-Instruct-2507 SimpleQA score found. SimpleQA definition: 4,326 questions, grades correct / incorrect / not attempted. Closest paper: a 2026 arXiv study on factual hallucination in reasoning models (Qwen3-4B and 8B, thinking variants, not 2507). | [S] | https://arxiv.org/abs/2411.04368 ; https://arxiv.org/pdf/2607.05861 |
| I4 | RAG faithfulness | No paper found that scores Qwen3-4B on RAG faithfulness. Leads: a 2026 SNS draft on faithfulness hallucinations in 2B to 8B open models (HotpotQA, HaluBench; model names not confirmed in the snippet); FaithEval (ICLR 2025). | [S] | https://ricerca.sns.it/retrieve/2e1c4bff-3880-44e4-99f3-3f3c6f2fe92c/draft.pdf ; https://proceedings.iclr.cc/paper_files/paper/2025/file/48404cd9ce03946c6b7177691f3267a1-Paper-Conference.pdf |
| I5 | Vectara hallucination leaderboard | Page fetched, but the table did not render; no Qwen3-4B row was readable. Gap: needs a manual check. | [F] | https://huggingface.co/spaces/vectara/leaderboard |
| I6 | Phone speed / memory, vendor | Qualcomm AI Hub lists Qwen3-4B-Instruct-2507 for Galaxy S25 / S25 Ultra / S25+ / S26 and Snapdragon X Elite / X2 Elite via GenieX-QAIRT, but shows NO numbers ("not currently supported on any All Models chipset"; TTFT and response-rate values absent). | [F] | https://aihub.qualcomm.com/models/qwen3_4b_instruct_2507 |
| I7 | Phone, third-party app | Private LLM lists a Qwen 3 4B Instruct 2507 build (GPTQ-Int4, not GGUF) for iPhone 12 Pro and newer and iPad; Mac needs 16 GB unified memory. No speed or RAM figure. Not llama.cpp. | [F] | https://privatellm.app/models/qwen3-4b-instruct-2507.md |
| I8 | Mac speed and memory, community | oMLX community benchmarks (Mac, not phone): about 34 to 81 tok/s generation depending on chip; peak memory 2.8 to 5.3 GB at 1k to 4k context; one M1 Pro run 34.1 tok/s with 4.7 GB peak at 1k context. Gives a memory order of magnitude only. | [S] | https://omlx.ai/benchmarks/zncqj12e |
| I9 | Llama.cpp phone anecdote | A hobbyist ran Qwen3-4B Q4_K_M on a 12 GB RAM Galaxy Note 20 Ultra via llama.cpp; the author states 12 GB+ phones can stretch to 4B. No speed figure in the snippet. | [S] | https://levelup.gitconnected.com/running-a-local-llm-on-my-old-android-phone-a-complete-journal-25cb30e07c53 |
| I10 | Failure modes (multi-turn evaluation, lead) | A 2026 arXiv paper (2602.24287) describes Qwen3-4B weaknesses: arithmetic errors, rambling, invented citations, some repetitive responses. Unclear whether it used this checkpoint or the thinking variant. No rate given. | [S] | https://arxiv.org/pdf/2602.24287 |
| I11 | Repetition / looping, sibling model | Qwen3-30B-A3B-Instruct-2507 looped in a Cursor agent via OpenRouter (single user report; integration cause not established). Sibling, not this model. | [S] | https://forum.cursor.com/t/agent-loop-doing-the-same-thing-multiple-times-even-user-accept-the-result/139140 |

## Gaps (not found, or needs a manual check)

- SimpleQA score for Qwen3-4B-Instruct-2507: not found.
- Vectara hallucination rate for this checkpoint: page did not render; check https://huggingface.co/spaces/vectara/leaderboard by hand.
- Official BFCL row for Qwen3-4B: page did not render; check https://gorilla.cs.berkeley.edu/leaderboard.html by hand.
- llama.cpp tool-call handler detected for the 2507 template: not confirmed; run `llama-server --jinja` and read the log.
- When2Call / NESTFUL results for Qwen3-4B: not found.
- Independent AA-Omniscience for this checkpoint: only a conflicting third-party value (I2).
- Phone llama.cpp tok/s and RSS on Android for Qwen3-4B Q4_K_M: not found. This is the main gap for our device plan.
- RAG faithfulness of Qwen3-4B: no paper found that scores it.
- Qwen-Agent vs raw-template tool calling results: not measured by any source found.

## Notes for the team (leads only)

- Sampling mismatch to test: card says top_k 20, top_p 0.8, min_p 0; engine uses top_k 40, top_p 0.95, min_p 0.05. Changes may affect tool-call format adherence. Lead, not evidence.
- Card context 262,144 native; our device runs use far less. The card's OOM advice (32,768) is the relevant one for phones.
- Card's self-reported BFCL-v3 61.9 and TAU2-Retail 40.4 are the only agentic numbers found for this exact checkpoint; both are vendor-reported.
