# Qwen3.6-35B-A3B: web research sweep (LEADS, not conclusions)

Date: 2026-10-19. Scope: deep-tier model (Qwen3.6-35B-A3B, Q2 GGUF, 512-token thinking budget, target 12 GB phones).
Method: one WebSearch pass per angle, plus WebFetch of the HF model card, the Unsloth GGUF card and the Artificial Analysis page.

Tags: **[F]** = read from the primary page in this sweep (WebFetch of the vendor/AA/Unsloth page). **[S]** = search snippet or third-party aggregator; not checked against the primary page.
Every row is a lead to verify before a decision rests on it (per the haiku-output rule in the execution policy).

---

## UNKNOWN / gaps to close first

1. **Q2_K_XL file is 12.3 GB** [F] (Unsloth). On a 12 GB-class phone that is the whole RAM budget before KV cache, the app and the OS. This is the key constraint of the deep tier; it is not a quality question.
2. **No vendor Q2 quality data.** Unsloth gives sizes but no KL or perplexity numbers [F]. No Q2 MoE KL study on Qwen3.6 was found.
3. **BFCL-V4 and TAU2 for Qwen3.6 are not in the Qwen card** [F]. The card has TAU3-Bench (67.2) and MCP-Atlas (62.8) instead. Red Hat's BFCL-V4 57.8 is from a third-party table [S].
4. **SimpleQA is not in the Qwen card** [F]. The AA-Omniscience hallucination value for this model was not visible on the AA page [F].
5. **llama.cpp thinking-budget flags are not documented** by Unsloth or Qwen [F]. The 512 budget is app-side only.
6. **No phone speed or expert-streaming report** for this model was found [S, search returned nothing relevant].
7. **BrowseComp: no published score** for Qwen3.6-35B-A3B found (a comparison page shows "Coming soon") [S].

---

## 1. Vendor (HF card, Unsloth card, vLLM recipe)

| Finding | Value | Tag | URL |
|---|---|---|---|
| Total / active params | 35B total, 3B activated; Safetensors metadata says 36B | [F] | https://huggingface.co/Qwen/Qwen3.6-35B-A3B |
| Experts | 256 per MoE layer, 8 routed + 1 shared active (from vLLM recipe, aggregator agrees) | [S] | https://recipes.vllm.ai/Qwen/Qwen3.6-35B-A3B |
| Context | 262,144 native; up to 1,010,000 via YaRN | [F] | https://huggingface.co/Qwen/Qwen3.6-35B-A3B |
| License | apache-2.0 | [F] | https://huggingface.co/Qwen/Qwen3.6-35B-A3B |
| Benchmarks, Qwen column | MMLU-Pro 85.2; MMLU-Redux 93.3; GPQA 86.0; SuperGPQA 64.7; HLE 21.4; LiveCodeBench v6 80.4; AIME26 92.7; SWE-bench Verified 73.4; Terminal-Bench 2.0 51.5; TAU3-Bench 67.2; MCP-Atlas 62.8 | [F] | https://huggingface.co/Qwen/Qwen3.6-35B-A3B |
| Thinking default | On by default; off via `chat_template_kwargs.enable_thinking=False`; keep past reasoning via `preserve_thinking=True` | [F] | https://huggingface.co/Qwen/Qwen3.6-35B-A3B |
| Thinking budget | Not mentioned in the card. Output default 32,768 tokens (81,920 for hard math/code) | [F] | https://unsloth.ai/docs/models/qwen3.6 |
| Sampling, thinking general | temp 1.0, top_p 0.95, top_k 20, min_p 0.0, presence 1.5, rep 1.0 | [F] | https://huggingface.co/Qwen/Qwen3.6-35B-A3B |
| Sampling, thinking coding | temp 0.6, top_p 0.95, top_k 20, presence 0.0 | [F] | https://huggingface.co/Qwen/Qwen3.6-35B-A3B |
| Sampling, instruct | temp 0.7, top_p 0.80, top_k 20, presence 1.5 | [F] | https://huggingface.co/Qwen/Qwen3.6-35B-A3B |
| Sampling conflict | Unsloth's "non-thinking reasoning" set (top_p 1.0, top_k 40, presence 2.0) disagrees with its own quickstart. Our engine uses 0.7/40/0.95/0.05 | [F] | https://unsloth.ai/docs/models/qwen3.6 |
| Presence penalty warning | Higher values can cause language mixing and a slight drop in quality | [F] | https://huggingface.co/Qwen/Qwen3.6-35B-A3B |
| Soft switch | `/think` and `/nothink` not officially supported | [F] | https://huggingface.co/Qwen/Qwen3.6-35B-A3B |
| Tool-call parser | vLLM: `--enable-auto-tool-choice --tool-call-parser qwen3_coder`; SGLang: `--tool-call-parser qwen3_coder`; both `--reasoning-parser qwen3`. Raw message format not described | [F] | https://huggingface.co/Qwen/Qwen3.6-35B-A3B |
| Hardware (BF16) | 1x H200 or 2x H100; FP8 fits one H100/H200 | [S] | https://recipes.vllm.ai/Qwen/Qwen3.6-35B-A3B |
| GGUF file sizes | Q2_K_XL 12.3 GB; IQ2_M 11.5 GB; Q3_K_M 16.6 GB; Q3_K_XL 16.8 GB; Q4_K_M 22.1 GB; Q8_0 36.9 GB; BF16 69.4 GB | [F] | https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF |
| llama.cpp support | Unsloth's card gives `llama serve -hf unsloth/Qwen3.6-35B-A3B:UD-Q4_K_M`; no `--reasoning-budget` or chat-template flags | [F] | https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF |
| Static YaRN caveat | Can hurt short-text performance; enable only for long contexts | [F] | https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF |
| Red Hat base-model row | MMLU-Pro ~85.3, GPQA 84.5, IFEval 93.1 (0-shot), BFCLv4 57.8; lm-eval/lighteval, thinking mode | [S] | https://friendli.ai/models/RedHatAI/Qwen3.6-35B-A3B-NVFP4 |

---

## 2. Agentic (tool use, agents, deep research, MCP, RAG)

| Finding | Value | Tag | URL |
|---|---|---|---|
| MCP-Atlas | 62.8 (vendor card); Qwen3.5-27B 68.4 in the same mirrored table | [F]/[S] | https://huggingface.co/Qwen/Qwen3.6-35B-A3B ; https://haimaker.ai/models/qwen/qwen3.6-35b-a3b |
| MCPMark | 37.0 (mirrored general-agent table) | [S] | https://haimaker.ai/models/qwen/qwen3.6-35b-a3b |
| Tool Decathlon | 26.9 (mirrored table) | [S] | https://haimaker.ai/models/qwen/qwen3.6-35b-a3b |
| WideSearch | 60.1 (mirrored table; the closest to deep research) | [S] | https://haimaker.ai/models/qwen/qwen3.6-35b-a3b |
| TAU3-Bench | 67.2 (vendor card; this is TAU3, not TAU2) | [F] | https://huggingface.co/Qwen/Qwen3.6-35B-A3B |
| BFCL-V4 | 57.8 (Red Hat table; no vendor figure found) | [S] | https://friendli.ai/models/RedHatAI/Qwen3.6-35B-A3B-NVFP4 |
| BrowseComp | No score for 3.6. A comparison page lists "Coming soon"; Qwen3.5-35B-A3B is 61 | [S] | https://benchlm.ai/md/compare/gpt-5-5-vs-qwen3-6-35b-a3b.md |
| Predecessor reference | Qwen3.5-35B-A3B: BFCL-V4 67.3, TAU2 81.2 (not 3.6 numbers; do not reuse) | [S] | https://haimaker.ai/models/qwen/qwen3.5-35b-a3b |
| Failure: empty tool args | Multi-turn loop with `{}` tool arguments in LM Studio; reporter says dropped think blocks unless `preserve_thinking=true`. Client-side, not llama.cpp | [S] | https://github.com/earendil-works/pi/issues/3325 |
| Failure: repetition loops | Endless reflect/tool/repeat loop on vLLM, same tool and params; recommended settings did not fix it | [S] | https://forums.developer.nvidia.com/t/qwen-qwen3-6-35b-a3b-and-fp8-has-landed/366822/180 |

Reading for us: the agentic numbers are vendor-reported and mostly on server runtimes. The only failure modes found come from other clients and runtimes, so the transfer to our llama.cpp + 512 budget is unverified. The multi-turn `preserve_thinking` point is worth a check in our chat path.

---

## 3. Independent (AA, leaderboards, quantization, phones, failure modes)

| Finding | Value | Tag | URL |
|---|---|---|---|
| AA Intelligence Index | v4.3.2 score 18, rank #13 of 141 (fetched page). Search snippet shows 32 (reasoning) and 15 (non-reasoning). Index versions differ, so the numbers are not comparable | [F] / [S] | https://artificialanalysis.ai/models/qwen3-6-35b-a3b |
| AA verbosity | 160M output tokens on the Index vs a median of 82M ("very verbose") | [F] | https://artificialanalysis.ai/models/qwen3-6-35b-a3b |
| AA speed and price | 134.4 tok/s (Alibaba API); [usage detail removed]/M in, [usage detail removed]/M out | [F] | https://artificialanalysis.ai/models/qwen3-6-35b-a3b |
| AA-Omniscience / hallucination | Metric defined (-100 to 100); the value for this model is not on the fetched page | [F] | https://artificialanalysis.ai/models/qwen3-6-35b-a3b |
| Quant: Unsloth KL | Unsloth claims rank 1 in 21 of 22 sizes for mean KL; no tables for Q2 found | [S] | https://unsloth.ai/docs/models/qwen3.6 |
| Quant: DWQ vs RTN | Qwen3.6 4-bit: mean KLD 0.0266 (DWQ) vs 0.0742 (RTN). Shows calibration matters | [S] | https://smcleod.net/2026/04/measuring-model-quantisation-quality-with-kl-divergence/ |
| Quant: MoE Q2-class, other model | Qwen3.5-35B-A3B IQ2_M: ppl 7.30, KL mean 0.111 vs F16 ppl 6.54. Different model; a bound at best | [S] | https://localai.io/blog/apex-moe-quantization/ |
| Quant: MoE 3-bit, other model | Qwen3-30B-A3B 3-bit VQ: Wikitext2 ppl 9.26 vs 18.72 baseline (paper's own ablation) | [S] | https://arxiv.org/pdf/2602.11184 |
| Routing stability under quant | Qwen3-30B-A3B A4W4: top-K expert changes 60.21% → 59.58% with KL regularization | [S] | https://arxiv.org/pdf/2604.10496 |
| Phones (12 GB class) | No Android or phone benchmark for this model found. Apple laptops only (M5 Max 72 tok/s at 1k ctx; M3 Max 64 GB 103 tok/s) | [S] | https://omlx.ai/benchmarks/ztzkae6u |
| Expert streaming on phones | Nothing found for this model | [S] | (search, no source) |

Reading: the strongest independent signal is AA's verbosity (160M tokens). That fits the thinking-budget question and the 512-token choice. The quant evidence is for other models or for 4-bit, so the Q2_K_XL quality loss is still unmeasured in public sources.

---

## Coverage check (done = each angle >= 3 findings with URLs)

- Vendor: 13 findings with URLs. Pass.
- Agentic: 10 findings with URLs. Pass (note: several are mirrored, not vendor-primary).
- Independent: 10 findings with URLs. Pass on count; phone and expert-streaming gap is real.

Sources used: https://huggingface.co/Qwen/Qwen3.6-35B-A3B · https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF · https://unsloth.ai/docs/models/qwen3.6 · https://artificialanalysis.ai/models/qwen3-6-35b-a3b · https://recipes.vllm.ai/Qwen/Qwen3.6-35B-A3B · https://friendli.ai/models/RedHatAI/Qwen3.6-35B-A3B-NVFP4 · https://haimaker.ai/models/qwen/qwen3.6-35b-a3b · https://github.com/earendil-works/pi/issues/3325 · https://forums.developer.nvidia.com/t/qwen-qwen3-6-35b-a3b-and-fp8-has-landed/366822/180 · https://smcleod.net/2026/04/measuring-model-quantisation-quality-with-kl-divergence/ · https://localai.io/blog/apex-moe-quantization/ · https://arxiv.org/pdf/2602.11184 · https://arxiv.org/pdf/2604.10496 · https://omlx.ai/benchmarks/ztzkae6u · https://benchlm.ai/md/compare/gpt-5-5-vs-qwen3-6-35b-a3b.md · https://haimaker.ai/models/qwen/qwen3.5-35b-a3b
