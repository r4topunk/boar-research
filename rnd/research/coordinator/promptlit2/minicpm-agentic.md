# MiniCPM agentic use: web sweep (leads, not conclusions)

Date: 2026-10-19. Scope: OpenBMB MiniCPM (0.5B to 8B), tool calling, MCP, survey/deep-research agents, RAG/long context, on-device agent demos, and comparisons with Qwen3-1.7B/4B, Llama-3.2, Gemma-3, LFM2.
Tags: [F] = page or paper read in full via WebFetch (HTML or model card); [S] = search snippet or secondary write-up only.
Nothing here is a reproduction. Numbers are as the source reports them.

## Findings table

| # | Source (URL) | Model and size | Task / benchmark | Setup (prompt, tools) | Measured numbers | Tag |
|---|---|---|---|---|---|---|
| 1 | MiniCPM4 tech report, arXiv 2506.07900, sec. 6.2 Table 13 (https://arxiv.org/html/2506.07900) | MiniCPM4-MCP, 8B (built on MiniCPM4-8B) | Human-annotated MCP tool-calling test, 16 MCP servers; scored func / param name / param value | Servers in Docker; only tools passing a Claude-4 quality check exposed; ~140k converted tool-learning instances + Claude-3.7 reverse-generated data. Tool-offering prompt format not given in the paper | Avg func/param/value: GPT-4o (size n/s) 80.2/70.2/49.1; Qwen3-8B 83.5/67.7/43.8; MiniCPM4-MCP 88.3/76.1/51.2 | [F] |
| 2 | openbmb/MiniCPM4-MCP model card (https://huggingface.co/openbmb/MiniCPM4-MCP) | 8B, BF16 | Same per-server table, 16 servers | Call format `<\|tool_call_start\|>` + Python-style call + `<\|tool_call_end\|>`; tool list from MCP handshake; the card does not say whether tools go in the system prompt or a `tools` field | Per-server examples: GitHub func/param/value 62.8/25.7/17.1 (gpt-4o 92.0/80.0/58.0); Calculator value 6.67 (gpt-4o 20.0); Slack 100/100/100 | [F] |
| 3 | MiniCPM4 tech report, sec. 6.1 Table 12 (https://arxiv.org/html/2506.07900) | MiniCPM4-Survey, 8B | SurveyEval (20 test examples), GPT-4o judge: Relevance, Coverage, Depth, Novelty, Fact Score | Plan-Retrieve-Write pipeline; arXiv abstract index (~2.71M, MiniCPM-Embedding-Light + Faiss); 3,750 Query2Plan + 61,684 Plan2Survey samples; SFT then section-level and survey-level RL | Avg 3.50 (= OpenAI Deep Research 3.50); FactScore 68.73 (highest of the systems listed); w/o RL: avg 3.11, FactScore 50.24. Naive RAG / AutoSurvey (Gemini-2.0-Flash-Thinking) FactScore 43.68 / 46.56 | [F] |
| 4 | openbmb/MiniCPM4-Survey model card (https://huggingface.co/openbmb/MiniCPM4-Survey) | 8B, BF16 | Same survey pipeline, table restated; reward = structure, content, citations | Scripts run retriever then run.sh; vLLM/SGLang serving; no latency or device numbers | Same table as #3 | [F] |
| 5 | MiniCPM4 tech report, sec. 3 Table 10 and Fig. 7 (https://arxiv.org/html/2506.07900) | MiniCPM4.1 8B (Full and Sparse variants) | RULER 32K weighted avg; RULER-NIAH up to 128K | YaRN to 128K; ~6K attended tokens per query (about 5 % sparsity at 128K) | RULER 32K: Full 88.93, Sparse 85.84; NIAH 100 % up to 128K (figure, value read from text) | [F] |
| 6 | openbmb/MiniCPM5-2B model card (https://huggingface.co/openbmb/MiniCPM5-2B) | 2.52B total (1.98B non-embedding), 42 layers, 131k ctx, Apache-2.0 | Agent/tool table: tau2-Telecom, BFCL v4, SWE-bench, Terminal-Bench v2.1, BrowseComp, GAIA Text-103, Claw-Gym, WildClaw, QwenClaw | XML-style tool calls; SGLang `--tool-call-parser minicpm5`. Card does NOT state tools offered, prompt format, or reasoning mode for these scores. Vendor-reproduced except marked AA (Artificial Analysis) | BFCL v4 66.6 (Qwen3.5-4B 56.8; Qwen3.5-2B 43.6; granite-4.2-3B 52.2; LFM2.5-2.6B 61.1); tau2-Telecom 97.1 (Qwen3.5-4B 92.1; LFM2.5-2.6B 90.4); GAIA Text-103 88.7 (Qwen3.5-4B 78.6); Terminal-Bench v2.1 8.6 AA (Qwen3.5-4B 25.8 AA); overall avg 53.9 vs 51.1 (Qwen3.5-4B). Qwen3-1.7B, Llama-3.2, Gemma-3 NOT in the table (Gemma-4-E2B/E4B are) | [F] |
| 7 | openbmb/MiniCPM5-1B model card (https://huggingface.co/openbmb/MiniCPM5-1B) | 1.08B total (0.68B non-embedding), 24 layers, 131k ctx, Apache-2.0 | Named only as "1B-class SOTA" vs LFM2.5-1.2B-Thinking, Qwen3-0.6B/think, Qwen3.5-0.8B/think | Think mode via enable_thinking; sampling 0.9/0.95 (think) and 0.7/0.95 (no-think). Tools and prompt format not described | NO agent or tool benchmark numbers on the card; RL+OPD "+16 points" avg on math/code/IF (benchmarks unnamed) | [F] |
| 8 | TinyLLM, arXiv 2511.22138 (https://arxiv.org/html/2511.22138v1) | Not MiniCPM. Qwen3-0.6B/1.7B/4B, xLAM-2-1B/3B, TinyLlama-1.1B, TinyAgent-1.1B | BFCL (Overall, Live, Non-live, Multi-turn subsets) on edge devices | Qwen3 = prompt-based calling; xLAM = native FC; hardware and quant not specified | Qwen3-1.7B 55.49 overall / 63.48 live / 80.03 non-live / 16.88 multi-turn; xLAM-2-1b-fc-r 53.97 / 61.57 / 72.42 / 8.38; Qwen3-4B 62.04 overall. Paper has internal inconsistencies (Qwen3-4B multi-turn 35.25 in Table I vs 16.88 in Table IV). No MiniCPM | [F] |
| 9 | "Small Reasoning Models are Instruction Followers in Function Calling", arXiv 2608.22472 (https://arxiv.org/html/2608.22472v1) | Not MiniCPM. Gemma-3 1B/4B/12B; Qwen3 0.6B/1.7B/4B/8B (think and no-think); Phi-4 mini; Granite 4 | BFCL V3 Live and Non-live (Simple, Multiple, Parallel, Parallel Multiple) | IFFC (JSON-list output, tools in system prompt), native FC, and prompt FC (PFC); FP16 and Q4_K_M | Gemma-3 1B IFFC Live Simple 13.9, Live Multiple 7.1; PFC Live Simple 30.0 / Multiple 10.5. Qwen3-1.7B Think IFFC FP16 Live Simple 75.9, Live Multiple 68.6; Q4_K_M 71.7 / 73.5. Paper has table inconsistencies (Gemma-3 1B non-live avg 23.9 vs 21.8/36.0 breakdown). No MiniCPM, no Llama-3.2 | [F] |
| 10 | BFCL, ICML 2025 / PMLR v267 (https://proceedings.mlr.press/v267/patil25a.html) | n/a (benchmark) | Benchmark definition: AST scoring, serial/parallel, multi-step | n/a | No model numbers read | [S] |
| 11 | MiniCPM GitHub README, BFCL for MiniCPM3-4B (found via search, https://benchmarklist.com/models/minicpm3-4b/ and MiniCPM repo) | MiniCPM3-4B (not MiniCPM4) | BFCL | Not read | 76.03 overall, reported in the repo as beating several 7-9B models and GPT-3.5-Turbo-0125 | [S] |
| 12 | MiniCPM5-1B secondary coverage (https://letsdatascience.com/news/openbmb-runs-local-agents-with-minicpm5-1b-27472042) | MiniCPM5-1B | Self-reported avg 42.57 over reasoning, knowledge, code, IF, math, logic, agentic | Not stated | Avg 42.57; a hands-on test (Decrypt, https://decrypt.co/369068) reports a hallucinated chain of thought and a failed logic trap. Neither is in the official card | [S] |
| 13 | MiniCPM-V-Apps (OpenBMB) (https://www.sourcepulse.org/projects/30367998) | MiniCPM-V family, on-device | Offline multimodal chat on Android / iOS / HarmonyOS | No document retrieval component found | No numbers read | [S] |

Reading the rows together (not a verdict):
- MiniCPM tool numbers come from vendor cards and the vendor tech report. None is a third-party run.
- The only MiniCPM model with a documented tool-call test is 8B (MCP). No MiniCPM 0.5B, 1B, or 2B row in the sources has a per-tool-call breakdown.
- BFCL version differs across sources (V3 in TinyLLM and IFFC, V4 in MiniCPM5-2B), so the numbers cannot be compared directly.
- The MiniCPM5-2B card's comparison set does not include Qwen3-1.7B, Llama-3.2, or Gemma-3, so no head-to-head against those was found.

## Gaps

1. No BFCL (v3 or v4) number for MiniCPM4-0.5B or MiniCPM4-8B on the official cards. MiniCPM3-4B 76.03 (repo) is the only BFCL figure for a MiniCPM model, and it is a different version.
2. No MiniCPM5-1B agent or tool number on the official card. The 42.57 average is secondary only.
3. No direct MiniCPM vs Qwen3-1.7B / Llama-3.2-1B/3B / Gemma-3 1B on any agent or tool benchmark, from any source found. The MiniCPM5-2B card compares with Qwen3.5-2B/4B, LFM2.5, Gemma-4 E2B/E4B.
4. Tool-passing mode (system prompt vs `tools` field) and reasoning on/off are unstated in the MiniCPM5 cards and the MCP card.
5. No published "small model as offline research assistant over a local document corpus" result with MiniCPM. The survey agent (#3) uses an online-style arXiv index with an 8B model and a GPT-4o judge.
6. No on-device latency or memory number for any MiniCPM agent. The MCP card's "over 5x acceleration" line is a series-level claim.
7. MiniCPM4 tech report sec. 6 was read through an HTML fetch that split the page. The Table 12/13 numbers match the model cards, so they were read from both places.
8. Several sources are internally inconsistent (TinyLLM Table I vs IV; IFFC Table 1 vs 6). Figures here are quoted per table, not averaged.

## Tentative: what this means for a ~1B offline research assistant reading knowledge packs (TENTATIVE)

- T1. Published 1-2B tool-call numbers on BFCL cluster around 50-60 overall (xLAM-2-1B 53.97; Qwen3-1.7B prompt mode 55.49) with multi-turn in the single digits to ~17. A 1B reader is likely best tested on single-turn retrieval-call selection, not long multi-turn sessions. Lead, not a bar.
- T2. Tool-call format changes results a lot: in IFFC, Gemma-3 1B scores 13.9 (IFFC) vs 30.0 (prompt FC) on live simple, and 0.0 vs 31.3 on live parallel. Freeze the call format per model before measuring.
- T3. MiniCPM4-MCP is strongest on function name (88.3) and weakest on parameter value (51.2 avg; GitHub 17.1). A pack reader's analogous risk is argument or value fidelity, so the check should score values, not only the chosen tool or source.
- T4. The MiniCPM4-Survey ablation (FactScore 68.73 with RL vs 50.24 without) suggests citation fidelity responds to training, but it was measured at 8B on a GPT-4o-judged 20-item set. A 1B pipeline would need its own FactScore-style gate with a frozen item set.
- T5. The MiniCPM5 family's self-reported strengths (BFCL v4, tau2-Telecom, GAIA Text-103) use benchmarks and judges different from our rubric. Treat them as a lead to test on our own frozen pack items, not as a transfer estimate.

Sources (all cited in the table above). Model cards and papers accessed 2026-10-19.
