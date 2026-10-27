# MiniCPM independent evaluations and practitioner reports (LEADS, not conclusions)

Sweep date: 2026-10-19. Scope: non-OpenBMB evaluations and practitioner reports of MiniCPM5-1B, MiniCPM5-2B, and MiniCPM4/4.1 small sizes. Output is leads. Every row needs a primary-source check before any claim use.

Tags: [F] = first-hand measurement by the author. [S] = secondary report that cites someone else. Strength column: how close the source is to a measurement.

## Findings table

| # | Source (URL) | Model | What was measured | Exact numbers | Comparators | Tag | Strength / caveats |
|---|---|---|---|---|---|---|---|
| 1 | Artificial Analysis article, 2026-05-26: https://artificialanalysis.ai/articles/minicpm5-1b-the-leading-1b-open-weights-model/ | MiniCPM5-1B (non-reasoning row) | Intelligence Index; AA-Omniscience; output token count | Index 17.9; 12.6M output tokens; AA-Omniscience -1 (article: highest in size class, attributed to abstention) | Qwen3.5 0.8B Reasoning 10.5; Qwen3.5 2B Reasoning 16.3 (389M tokens); MiniCPM-V 4.6 1.3B NR 12.7 (5.4M tokens, Omniscience -85); Qwen3.5 0.8B NR Omniscience -89; Exaone 4.0 1.2B Omniscience -83 | [F] (AA-run) | Strongest independent source found. Index version not stated in text. Speed and price not reported. Per-eval breakdown is an image (not read). |
| 2 | AA model pages (MiniCPM5-1B Reasoning / Non-reasoning, multiple locales): https://artificialanalysis.ai/models/minicpm5-1b-non-reasoning | MiniCPM5-1B | Index listing; "1 - hallucination rate" listed as an eval | Korean-locale page: Index 12 vs median 3 (version v4.1 on non-English pages, v4.1.1 on English) | Median of comparable models | [F] | Conflicts with 17.9 in row 1. Likely version or mode difference; unreconciled. Pages are JS-rendered; per-eval numbers not extracted. |
| 3 | BenchLM comparison pages: https://benchlm.ai/md/compare/minicpm5-1b-vs-o3-mini.md | MiniCPM5-1B | "Independent public score" | 5.12 (site says not a controlled head-to-head) | o1, o3-mini, GPT-5.5, MiniMax M2.5, Qwen3.5 Plus, o4-mini | [S] | Most cells "Coming soon" (last updated 2026-10-07). Low value. Conflicts with rows 1-2. |
| 4 | eWeek: https://www.eweek.com/news/minicpm5-2b-ai-model-benchmarks/ (fetch returned 403; search snippet only) | MiniCPM5-2B | Index (via AA) | AA Intelligence Index v4.2: 15, top open-weights below 4B at release. Vendor: beats Qwen3.5-4B on 20 of 34 tests, loses 14 | Qwen3.5-4B | [S] | Snippet only, not read in full. Says most results were run or reproduced by OpenBMB. |
| 5 | eesel.ai review: https://www.eesel.ai/blog/minicpm5-2b-review | MiniCPM5-2B | Cited independent Index; hands-on anecdotes | AA Index 15 (cited via Reddit/HN, article says "highest below 4B"); OpenBMB launch tweet claims 23 + 20 Agentic Index (article says it does not reconcile; 15 is the conservative figure). Vendor: 53.9 avg across 34 benchmarks vs Qwen3.5-4B 51.1 | Qwen3.5-4B, others | [S] | Secondary. Reports one X user saying it "fails when driven through a real coding harness" (quantized 2B plus drafter; no detail). No repetition/thinking/empty-output reports in this article. |
| 6 | Decrypt: https://decrypt.co/369068/openbmb-minicpm5-half-gigabyte-ai-model-local-agents-phone | MiniCPM5-1B | Three informal tests (logic trap, A/B choice, tool call); vendor numbers quoted | Vendor avg 42.57 vs 35.61 next-best 1B (source unnamed, likely OpenBMB). Post-training: runaway-length responses -29 pp (vendor). 8T tokens vs Qwen3 36T | Qwen3-0.6B, Qwen3.5-0.8B, LFM2.5-1.2B-Thinking | [F] anecdotes / [S] numbers | Missed logic trap; hedged instead of choosing; hallucinated chain-of-thought; "poor knowledge", "codes poorly". Hallucination on obscure facts reduced with MCP tool use (single test). No memory or speed figures. |
| 7 | MindStudio guide: https://www.mindstudio.ai/blog/run-minicpm5-2b-locally-ollama-llamacpp/ | MiniCPM5-2B | Memory and SGLang behaviour on a 48 GB card | Weights ~4 GB VRAM (stated, method not given). Total VRAM with SGLang default KV cache ~44 GB on a 48 GB card ("in testing", no config). Author's advice: 8-12 GB floor (untested). No tok/s, no system RAM, no quantization tested | None named | [F] (partial) | Memory is a serving/KV-cache default issue, not a model defect (author). Verbose reasoning: responses "can balloon", sometimes recomputes same steps (qualitative). Multilingual: terms of endearment fabricated or wrong; only a handful correct. |
| 8 | Better Stack guide: https://betterstack.com/community/guides/ai/minicpm5-2b/ | MiniCPM5-2B | Cites a GitHub issue investigation on repetition | Q4_K_M, default settings without repeat-penalty: runaway rate 92.1% (cited). With --repeat-penalty 1.15: runaway 11.0%, HumanEval+ 6.1 -> 71.3. Article says "all four" settings required (repeat-penalty 1.15, min-p 0.0, temp 1.0, top-p 0.95). Older mlx-lm misread EOS and ran forever (fix: mlx-lm >= 0.3.1) | None | [S] | Secondary citing a GitHub issue (not fetched). Internal contradictions ("one flag" vs "all four"; 14x vs 11.7x; 11% residual). Says the Q8 GGUF is "more stable" with no numbers. The GitHub issue itself is the thing to read. |
| 9 | Hallucination detection with small LMs (Cheung): https://arxiv.org/pdf/2506.22486 | MiniCPM (as edge backbone) | Hallucination detection | Not extracted (PDF unreadable via WebFetch) | Qwen2 and others | [F] | Only academic paper found using a MiniCPM model in a small-model factuality setting. Numbers unread. Needs manual check. |
| 10 | MiniCPM4 tech report (self-reported, for context): https://arxiv.org/pdf/2506.07900 | MiniCPM4 0.5B / 8B | Vendor benchmarks | 0.5B beats Llama3.2-1B and Gemma3-1B; 8B beats Gemma3-12B and Phi4-14B; parity with Qwen3 on 8T vs 36T tokens | Llama3.2-1B, Gemma3-1B, Gemma3-12B, Phi4-14B, Qwen3 | [S] (vendor) | Not independent. Included only to mark the vendor baseline. No independent MiniCPM4 eval found. |
| 11 | Llama.cpp / phone speed search (no direct MiniCPM phone result) | MiniCPM-2B on RK3576 board | tok/s on Rockchip rknn-llm | 6.45 tok/s INT4 (Megrez-3B README, not llama.cpp) | None | [F] (board, not phone) | Only hardware speed datapoint found for MiniCPM. MiniCPM3 unsupported on that board. Phone llama.cpp numbers for MiniCPM5 not found. |
| 12 | Phone-class llama.cpp/ExecuTorch baselines (non-MiniCPM): https://github.com/pytorch/executorch/pull/2927.diff | Llama-2 4-bit | tok/s | ~8-11 tok/s on Galaxy S22/S24 and OnePlus 12; ~6 tok/s iPhone 15 Pro | n/a | [F] | Context only. Not MiniCPM. Use as order-of-magnitude baseline. |
| 13 | Memory-by-quant estimate (oflight): https://www.oflight.co.jp/en/columns/minicpm5-2b-requirements-on-device-2026 | MiniCPM5-2B | File-size memory per quant | Q2_K ~1.04 GB; Q3_K_M ~1.29; Q4_K_M ~1.56 (official GGUF); Q5_K_M ~1.81; Q6_K ~2.07; Q8_0 ~2.68 (official); F16 ~5.04. "High-end 8 GB+ phone: plenty of headroom" (assessment). No measured tok/s | None | [S] (estimate) | Explicitly "weight-size-only estimates"; excludes KV cache (131k context). Phone speed admitted unverified. Does not match row 7 on quant or context. |

## Independent sources count

Met the done bar (>= 6) only in a loose sense. Of the 13 rows, the ones that are independent measurements of MiniCPM are row 1 (AA, strong), row 6 (informal tests), row 7 (partial measured memory), and row 2 (AA listing, mixed). Rows 3-5 and 8 are secondary citations. Rows 9-13 are paper or context. Treat the set as thin.

## Failure modes reported (candidate list, each needs a primary check)

| Failure mode | Model | Source (row) | Evidence level | Note |
|---|---|---|---|---|
| Repetition / runaway generation with default settings (no repeat-penalty) | MiniCPM5-2B GGUF Q4_K_M | row 8 (GitHub issue, 92.1% runaway) | [S] | Strongest failure signal in this sweep. The fix sets repeat-penalty 1.15 and sampling flags. Residual 11% after fix (per article). Verify in the upstream issue. |
| Runaway with older mlx-lm (EOS misidentified) | MiniCPM5-2B on MLX | row 8 | [S] | Version-specific. Fix: mlx-lm >= 0.3.1. |
| Runaway-length responses (vendor says -29 pp after post-training) | MiniCPM5-1B | row 6 | [S] vendor | Implies runaway was a known problem before post-training. Not independent. |
| Verbose reasoning, recomputes same steps, slow simple prompts | MiniCPM5-2B | row 7 | [F] qualitative | Author's FAQ. |
| Thinking emitted as <think> block; no toggle described | MiniCPM5-2B | row 8 | [S] | Article calls it expected behaviour. Article gives no disable switch. Unverified whether a flag exists. |
| Thinking-mode hallucinated chain-of-thought | MiniCPM5-1B | row 6 | [F] anecdote | Single informal test. |
| Missed logic trap; hedged instead of choosing | MiniCPM5-1B | row 6 | [F] anecdote | Small sample. |
| Fabricated or wrong multilingual terms (only a handful correct) | MiniCPM5-2B | row 7 | [F] qualitative | Tested on terms of endearment only. |
| Coding harness failure on quantized 2B build plus drafter | MiniCPM5-2B | row 5 (X post cited) | [S] anecdote | No detail. Possibly the drafter, not the base model. |
| Poor knowledge, weak coding (author opinion) | MiniCPM5-1B | row 6 | [F] opinion | Consistent with AA-Omniscience abstention (row 1). |
| Abstention rather than answering (Omniscience -1, abstains on most questions) | MiniCPM5-1B | row 1 | [F] AA | Can look like a high "reliability" score while being unhelpful. Watch for this in any hallucination metric. |
| Language scope: English and Chinese confirmed only; text-only; no vision | MiniCPM5-1B/2B | rows 5, 6 | [S] OpenBMB card | Relevant to bounty scope (English only). |
| Not found: empty outputs, language mixing, thinking-cannot-disable reports | - | sweep | not found | Searches returned nothing MiniCPM-specific. Absence is not evidence of absence. |

## Gaps (what the sweep did not find)

1. **AA hallucination numbers.** The AA-Omniscience values for MiniCPM5-1B are known (-1). The 2B figure, and the AA hallucination-rate eval, were not extracted. AA model pages are JS-rendered; per-eval values are in images.
2. **Index version conflict.** 17.9 (AA article, 1B) vs 12 (AA Korean page, 1B) vs 5.12 (BenchLM, 1B) vs 15 (AA, 2B, cited) vs 23 (OpenBMB claim, 2B). Need the AA methodology version per row.
3. **eWeek primary** (403). Read the AA 2B page directly.
4. **Upstream GitHub issue** behind the 92.1% runaway claim (row 8). Not fetched. Need the issue URL from the article or from openbmb/MiniCPM and the HF Community tab for openbmb/MiniCPM5-2B.
5. **Phone llama.cpp numbers for MiniCPM5 (1B or 2B).** None found. Only a 6.45 tok/s RK3576 board datapoint for MiniCPM-2B (non-llama.cpp). Need a llama-bench on the target phone (Pixel 8a 8 GB or POCO X6 Pro, per the project) or a community Android report.
6. **Independent factuality, RAG-faithfulness, instruction following, tool-use papers including MiniCPM5 or MiniCPM4 small sizes.** Only one paper (row 9) uses a MiniCPM backbone, and its numbers were not readable. Suggested next queries: "MiniCPM RAGTruth", "MiniCPM HHEM", "MiniCPM SimpleQA", "MiniCPM BFCL tool use".
7. **LMArena / Open LLM Leaderboard entries** for MiniCPM5 or MiniCPM4 small. Not searched in this sweep.
8. **Reddit r/LocalLLaMA threads.** Not directly indexed. The "skeptical Reddit reaction" in row 5 is second-hand.
9. **Thinking toggle.** Whether MiniCPM5 supports an enable_thinking or equivalent switch, and whether it can be disabled, is unknown from these sources. Check the model card chat template.
10. **Ollama / LM Studio community speed reports** on a laptop or phone, beyond row 13's estimates.
11. **Artifacts from rows 5 and 6 that rely on X posts** (@PendelaPhani, @aijoey). Not verified. The 931 tok/s figure is a 32-subagent DGX Spark batch, not single-stream on a phone.

## Next steps (for coordinator, not run here)

- Read the AA 2B model page and the eWeek article in full.
- Pull the openbmb/MiniCPM5-2B Community tab and the GitHub issue behind the 92.1% figure. Check whether the sampler settings there match the engine's (0.7/40/0.95/0.05) and whether repeat-penalty is in our config.
- Run a repetition probe on our own 4B-class configs at the same settings as row 8 before any claim about MiniCPM5 loops.
