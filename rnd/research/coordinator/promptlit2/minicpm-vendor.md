# MiniCPM vendor sweep (OpenBMB), read-only leads

Date of sweep: 2026-10-19. Output is LEADS, not conclusions.
Tags: [F] = read in full from the official page or file (for the leaderboard image: read in full as an image); [S] = search snippet or third-party page, not verified against the official source.
All numbers are vendor-reported unless marked otherwise. Nothing here is independently reproduced.

## 1. MiniCPM5-1B (primary)

### Findings

| # | Claim | Value (exact) | Tag | Source |
|---|---|---|---|---|
| 1 | Parameters | 1,080,632,832 total; 679,552,512 non-embedding | [F] | https://huggingface.co/openbmb/MiniCPM5-1B |
| 2 | Architecture | Causal LM, standard `LlamaForCausalLM`; no custom code needed | [F] | https://huggingface.co/openbmb/MiniCPM5-1B |
| 3 | Layers / heads | 24 layers; 16 Q heads, 2 KV heads (GQA) | [F] | https://huggingface.co/openbmb/MiniCPM5-1B |
| 4 | Context length | 131,072 | [F] | https://huggingface.co/openbmb/MiniCPM5-1B |
| 5 | Precision | BF16 (card) | [F] | https://huggingface.co/openbmb/MiniCPM5-1B |
| 6 | License | Apache-2.0 | [F] | https://huggingface.co/openbmb/MiniCPM5-1B |
| 7 | Training data | Pre-training: stable + decay, then mid-training; corpora Ultra-FineWeb, Ultra-FineWeb-L3, UltraData-Math. Post-training: "200B tokens of deep-thinking SFT" and "200B tokens of hybrid-thinking SFT" (SFT data released as UltraData-SFT-2605). RL on DAPO-Math-17k, TriviaQA/NQ-Open (closed-book QA), LongWriter-Zero-RLData, synthesized RLVR data, pair-wise RLHF signals. Final step: On-Policy Distillation (OPD) of RL teachers into one model. Note: the card text is for the MiniCPM5 family; I did not confirm that every sentence applies to 1B only. | [F] | https://huggingface.co/openbmb/MiniCPM5-1B (WebFetch summary of the card; the summary did not separate 1B-specific from family-wide text, so re-check the rendered page before quoting) |
| 8 | RL + OPD effect (vendor) | "raises the average score by ↑16 points" on math, code, instruction-following; "cuts overlong responses by ↓29 percentage points" | [F] | https://huggingface.co/openbmb/MiniCPM5-1B/raw/main/README.md |
| 9 | Hybrid thinking | Built-in `<think>` chat template, switched with `enable_thinking`; same checkpoint = fast assistant + reasoner | [F] | https://huggingface.co/openbmb/MiniCPM5-1B-GGUF ; https://huggingface.co/openbmb/MiniCPM5-1B/raw/main/README.md |
| 10 | Thinking switch (code) | `apply_chat_template(..., add_generation_prompt=True, enable_thinking=False, return_dict=True, return_tensors="pt")`; card example uses `enable_thinking=False`. Default value of the flag not stated. | [F] | https://huggingface.co/openbmb/MiniCPM5-1B/raw/main/README.md |
| 11 | Recommended sampling, Think | `temperature=0.9, top_p=0.95`, `enable_thinking=True` | [F] | https://huggingface.co/openbmb/MiniCPM5-1B/raw/main/README.md ; https://huggingface.co/openbmb/MiniCPM5-1B-GGUF |
| 12 | Recommended sampling, No Think | `temperature=0.7, top_p=0.95`, `enable_thinking=False` | [F] | same as 11 |
| 13 | top_k / min_p / repetition penalty for 1B | Not specified on the 1B pages | [F] (absence) | https://huggingface.co/openbmb/MiniCPM5-1B |
| 14 | Quant files (GGUF repo) | Q4_K_M 688 MB; Q8_0 1.15 GB; F16 2.17 GB | [F] | https://huggingface.co/openbmb/MiniCPM5-1B-GGUF |
| 15 | llama.cpp (vendor card) | `llama serve -hf openbmb/MiniCPM5-1B-GGUF:Q4_K_M` ("OpenAI-compatible server with a web UI"); `llama cli -hf openbmb/MiniCPM5-1B-GGUF:Q4_K_M`; `docker model run hf.co/openbmb/MiniCPM5-1B-GGUF:Q4_K_M` | [F] | https://huggingface.co/openbmb/MiniCPM5-1B-GGUF |
| 16 | Ollama | `ollama run hf.co/openbmb/MiniCPM5-1B-GGUF:Q4_K_M`; also `docker model run hf.co/openbmb/MiniCPM5-1B` | [F] | https://huggingface.co/openbmb/MiniCPM5-1B-GGUF ; https://huggingface.co/openbmb/MiniCPM5-1B |
| 17 | MLX | Separate repo MiniCPM5-1B-MLX, "MLX / 4bit for Apple Silicon" (no run commands on card) | [F] | https://huggingface.co/openbmb/MiniCPM5-1B |
| 18 | llama.cpp deployment doc (2B examples) | `llama-server -m MiniCPM5-2B-Q4_K_M.gguf --port 8080 -ngl 99 -c 8192 --jinja`; `llama-cli ... -n 2048 --temp 1.0 --top-p 0.95 --min-p 0.0 -ngl 99`. Doc gives 1B per-mode temps (Think 0.9, No-think 0.7). Doc says llama.cpp default `min_p=0.05` "can lead to repetitive output", so set `min_p=0.0`. No thinking-control flag mentioned (only temperature differs by mode). Doc also mentions converter: `convert_hf_to_gguf.py` (does not say the converter is merged for MiniCPM5). | [F] | https://raw.githubusercontent.com/OpenBMB/MiniCPM/main/docs/deployment/llama_cpp.md |
| 19 | llama.cpp upstream merge status | Not found in any official page read. Card states the standard Llama architecture, "no custom kernels, no model-code fork". | [F] (absence) | https://huggingface.co/openbmb/MiniCPM5-1B-GGUF |
| 20 | Tool-use backend note | Card recommends SGLang for tool calling; does not mention llama.cpp for that | [F] | https://huggingface.co/openbmb/MiniCPM5-1B-GGUF |
| 21 | On-device speed (vendor) | None given on official pages; card only says "built for on-device, local deployment, and resource-constrained scenarios" | [F] (absence) | https://huggingface.co/openbmb/MiniCPM5-1B |
| 22 | Known issues (vendor) | None listed on card; limitations text only: "may produce inaccurate, biased, or unsafe outputs". GGUF repo has 9 community discussions (contents not visible). | [F] | https://huggingface.co/openbmb/MiniCPM5-1B-GGUF |

### Benchmark table, MiniCPM5-1B (Thinking mode), vendor leaderboard image [F]

Source image: https://raw.githubusercontent.com/OpenBMB/MiniCPM/main/assets/minicpm5/public_leaderboard_en.png (linked from the 1B card; the card has no numeric text table, only images). Read in full as an image. Columns in the image: MiniCPM5-1B (Thinking), Qwen3-0.6B (Thinking), Qwen3.5-0.8B (Thinking), LFM2.5-1.2B (Thinking). Single mode shown in image: Thinking. No No-Think numbers in this image.

| Benchmark | MiniCPM5-1B (Thinking) | Qwen3-0.6B (Thinking) | Qwen3.5-0.8B (Thinking) | LFM2.5-1.2B (Thinking) |
|---|---|---|---|---|
| Average Score | 42.57 | 26.77 | 25.14 | 35.61 |
| MMLU-Pro | 48.85 | 35.63 | 42.74 | 47.98 |
| MMLU-Redux | 70.06 | 55.47 | 61.50 | 66.08 |
| GPQA-Diamond | 26.26 | 25.42 | 30.98 | 34.85 |
| SuperGPQA | 23.14 | 20.79 | 22.92 | 22.83 |
| LCB-Pro 25Q2 (Easy) | 22.68 | 4.12 | 0.00 | 6.19 |
| OJBench | 7.33 | 0.86 | 0.43 | 1.94 |
| LCB-v6 (@Avg3) | 33.52 | 16.00 | 5.33 | 21.33 |
| IFBench | 46.67 | 25.67 | 29.33 | 41.67 |
| IFEval | 80.41 | 59.89 | 59.89 | 84.84 |
| Multi-IF | 43.54 | 36.56 | 32.31 | 55.61 |
| MultiChallenge | 19.48 | 18.97 | 23.97 | 23.28 |
| AIME-2025 (@Avg16) | 40.42 | 16.25 | 1.04 | 31.88 |
| AIME-2026 (@Avg16) | 40.42 | 12.29 | 0.21 | 31.67 |
| HMMT Feb 2026 (@Avg16) | 25.76 | 9.85 | 0.57 | 21.21 |
| MATH-500 | 91.60 | 72.60 | 30.40 | 89.00 |
| BBH | 71.89 | 47.86 | 54.58 | 57.32 |
| BBEH | 12.14 | 3.78 | 8.53 | 8.64 |
| BFCLv4 | 25.15 | 25.43 | 25.53 | 10.60 |
| τ²-Bench Telecom-AA | 79.53 | 21.10 | 47.70 | 19.60 |

Not in the image: GSM8K (not reported on this table), base-model (non-thinking) numbers, RAG/long-context, SimpleQA/hallucination.

Notes on this table:
- Vendor's own comparison set; competitor settings (thinking budget, sampling, harness) not stated in the image.
- Readings of small values from the image may have a last-digit error; re-check against the image before quoting in a claim.
- BFCLv4 is the one tool-use number here where MiniCPM5-1B is not ahead of the Qwen rows (25.15 vs 25.43 / 25.53). τ²-Bench Telecom-AA is far ahead (79.53).

### Thinking control and sampling, summary
- Switch: `enable_thinking=True|False` in `apply_chat_template` (HF). Default not stated.
- Sampling: Think temp 0.9 / No Think temp 0.7, top_p 0.95. Top-k, min_p, repetition penalty: not given for 1B.
- llama.cpp: no documented thinking flag; the vendor doc only switches temperature per mode. Whether `enable_thinking` reaches the GGUF chat template via `--jinja` is not documented (open question).

### Phone and device speed (community, [S] only)

| Claim | Value | Tag | Source |
|---|---|---|---|
| Snapdragon 865 (Samsung S20 FE), GGUF listing | 27.9 tok/s on phone; 18.1 tok/s CPU; 656 MB file; "verified on real phone hardware, June 2026" | [S] | Search snippet; community page reached via https://huggingface.co/SandLogicTechnologies/MiniCPM5-1B-GGUF or similar (exact page not opened) |
| iPhone 17 Pro (A19 Pro), Core AI int8 conversion | 66.8 tok/s decode; 68.0 tok/s prefill; 1.0 GB; PipelinedBench, random 128-token prompt, greedy; int8 ~2.2x fp16 | [S] | https://huggingface.co/mlboydaisuke/MiniCPM5-1B-CoreAI (snippet only) |
| Other community mobile build | https://huggingface.co/dispatchAI/MiniCPM5-1B-mobile (not opened) | [S] | snippet only |

Caveats: single community runs, different hardware, quant and prompts. Not comparable with each other. No OpenBMB official figure.

### Gaps (1B)
1. The 1B card has no numeric benchmark text; the table is an image. Found only the Thinking-mode image. No No-Think / base table found.
2. GSM8K for 1B not found anywhere.
3. No RAG, long-context (beyond context length), SimpleQA or hallucination numbers for 1B.
4. No BFCL-style tool-use table beyond BFCLv4 in the image; no tool-call template documentation for 1B.
5. Default value of `enable_thinking` not stated; behaviour of `enable_thinking=False` on GGUF / llama.cpp not verified.
6. Whether upstream llama.cpp has merged MiniCPM5 support: not found. The vendor doc uses a 2B example for conversion.
7. The 1B card's `enable_thinking` snippet and recommended sampling were read from raw README; confirm against the rendered page before quoting.
8. The training-data summary came from a WebFetch summary, not a verbatim copy; confirm the exact wording on the rendered 1B card.
9. Community phone speeds are unverified single runs; no official phone benchmark.
10. Not read: the radar image, the RL gains images (rl_gains.png, rl_overlong.png), the GitHub MiniCPM5 cookbook beyond the llama.cpp page (ollama.md, mlx.md, and any vLLM/SGLang docs).

## 2. MiniCPM5-2B (close sibling)

### Findings

| # | Claim | Value (exact) | Tag | Source |
|---|---|---|---|---|
| 1 | Parameters | 2,516,756,480 total; 1,981,982,720 non-embedding (page header says "3B params") | [F] | https://huggingface.co/openbmb/MiniCPM5-2B |
| 2 | Architecture | Dense causal LM, standard `LlamaForCausalLM`, BF16 | [F] | https://huggingface.co/openbmb/MiniCPM5-2B |
| 3 | Layers / heads | 42 layers; GQA 16 Q / 2 KV heads | [F] | https://huggingface.co/openbmb/MiniCPM5-2B |
| 4 | Context | 131,072 | [F] | https://huggingface.co/openbmb/MiniCPM5-2B |
| 5 | License | Apache-2.0 | [F] | https://huggingface.co/openbmb/MiniCPM5-2B |
| 6 | Thinking switch | Transformers example passes `enable_thinking=True`; no other mechanism described | [F] | https://huggingface.co/openbmb/MiniCPM5-2B |
| 7 | Sampling (vendor) | `temperature=1.0, top_p=0.95, min_p=0.0`; add `repetition_penalty=1.05` if outputs repeat; support varies by framework | [F] | https://huggingface.co/openbmb/MiniCPM5-2B |
| 8 | MMLU-Pro | 70.8 | [F] | https://huggingface.co/openbmb/MiniCPM5-2B |
| 9 | MMLU-Redux | 84.7 | [F] | same |
| 10 | GSM8K | Not reported; "MATH-500" 94.6 and AIME 2025 86.5 instead | [F] (absence) | same |
| 11 | IFEval / IFBench / Multi-IF | 86.7 / 66.3 / 71.8 | [F] | same |
| 12 | BFCL v4 | 66.6 | [F] | same |
| 13 | τ²-Bench Telecom | 97.1 | [F] | same |
| 14 | τ³-Bench Banking | 20.8 (†, AA-sourced) | [F] | same |
| 15 | Long context | NoLiMa 68.1; LongBench v2 43.7; LongBenchPro 44.8; AA-LCR 59.0 (†) | [F] | same |
| 16 | Code | LiveCodeBench v6 69.1; SWE-bench Verified 46.4; SWE-bench Pro 14.4 | [F] | same |
| 17 | Math | AIME 2025 86.5; AIME 2026 86.5; HMMT Feb 2026 63.8; MATH-500 94.6 | [F] | same |
| 18 | Average over comparison set | 53.9 | [F] | same |
| 19 | llama.cpp example (2B) | `llama-server -m MiniCPM5-2B-F16.gguf ... -c 8192 --jinja` | [F] | same |
| 20 | Speed | No speed figures; mentions DSpark speculative decoding in SGLang, no numbers | [F] | same |

Notes:
- († = scores from the official Artificial Analysis release, others reproduced internally by the authors; per the card.)
- Search snippet ([S]) claims Qwen3.5-4B IFEval 90.2 vs 2B 86.7; not verified on the card.
- Search snippet ([S]) says Artificial Analysis Intelligence Index 15 (r/LocalLLaMA, HN) vs OpenBMB claim 23 (+20 Agentic Index). Unverified; tag [S] only.
- 2B card lists "Layers: 42" and 2.52B params, which conflicts with the search snippet claim of "2.5B" (consistent) and Artificial Analysis "2.6B" (different). Use card.

### Gaps (2B)
1. No GSM8K; no base MMLU (only MMLU-Pro and MMLU-Redux).
2. No explicit thinking-off switch documented beyond the `enable_thinking` example.
3. No on-device speed.
4. Not read: a 2B leaderboard image, if any, and the AA release page.

## 3. MiniCPM 4 / 4.1 (0.5B, 8B) and other MiniCPM5 releases

Status: NOT SEARCHED in this sweep (scope priority was 1B and 2B). Gaps:
1. MiniCPM4 0.5B and MiniCPM4.1 0.5B/8B model cards: parameters, benchmarks, thinking switch, GGUF status.
2. MiniCPM5 release notes beyond the 1B and 2B cards (any MiniCPM5 larger models, dates).
3. OpenBMB GitHub release notes for the MiniCPM5 family.

Suggested next step (not done): fetch https://huggingface.co/openbmb (listing) and the GitHub repo https://github.com/OpenBMB/MiniCPM for release notes.

## 4. Discrepancies and cautions
- The search engine summary called MiniCPM5-1B a non-SFT base model. The 1B card lists post-trained, thinking-capable checkpoints. Card wins.
- A Spanish Decrypt summary gave "1.000M" params and 128K context: conflicts with the card (1,080,632,832 params; 131,072 ctx). Card wins.
- The 1B leaderboard image is a vendor table (Thinking mode only), comparing to four sub-1.2B competitors; not a general leaderboard.
- Two different temperature rules exist for the same family: 1B card (Think 0.9 / No Think 0.7) vs 2B card (1.0). Do not transfer one to the other.
- llama.cpp doc says the default `min_p=0.05` "can lead to repetitive output"; vendor sets `min_p=0.0`. Relevant if we run the GGUF through llama.cpp defaults.

## 5. Sources list
- https://huggingface.co/openbmb/MiniCPM5-1B (card, [F])
- https://huggingface.co/openbmb/MiniCPM5-1B/raw/main/README.md (raw card, [F])
- https://huggingface.co/openbmb/MiniCPM5-1B-GGUF (GGUF card, [F])
- https://huggingface.co/openbmb/MiniCPM5-2B (card, [F])
- https://raw.githubusercontent.com/OpenBMB/MiniCPM/main/assets/minicpm5/public_leaderboard_en.png (1B leaderboard image, [F] as image)
- https://raw.githubusercontent.com/OpenBMB/MiniCPM/main/docs/deployment/llama_cpp.md (llama.cpp guide, [F])
- https://huggingface.co/mlboydaisuke/MiniCPM5-1B-CoreAI ([S])
- https://huggingface.co/SandLogicTechnologies/MiniCPM5-1B-GGUF ([S], not opened)
- https://huggingface.co/dispatchAI/MiniCPM5-1B-mobile ([S], not opened)
- https://aiweekly.co/alerts/openbmb-ships-minicpm5-2b-a-25b-apache-20-on-device-model-averaging-539-across ([S])
- https://artificialanalysis.ai/articles/openbmb-releases-minicpm5-2b ([S])
