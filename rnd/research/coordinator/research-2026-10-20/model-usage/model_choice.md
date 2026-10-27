# Model choice sanity at the 8 GB (lite) tier — 2026-10-20

TL;DR: the lite engine is **Qwen3-1.7B (April 2025 hybrid, Q4_K_M unsloth @d7f544ee)**. Every lite reader screen so far compared it against *older or degraded* siblings: LFM2-1.2B (not LFM2.5), Gemma-3-1B (not Gemma 4 E2B), Bonsai2-2B ternary PTQ1_0 (not the native Qwen3.5-2B it is built on), Qwen2.5-1.5B, MiniCPM5-1B/2B. The three newest same-size, permissive, GGUF-available instruct checkpoints — **Qwen3.5-2B (2026-02-28, Apache-2.0)**, **Gemma 4 E2B-it (2026-03-02, QAT Q4_0 GGUF 2026-05-01, Apache-2.0)** and **LFM2.5-1.2B-Instruct (2026-01-04, LFM Open License)** — were never quality-screened. Qwen3.5-2B is also the model in the post author's own a competitor team copy. None of today's 7 NOs is a model-choice artefact per se (they test levers on a fixed model), but the "1.7B is the best lite reader" conclusion (LITEREADERS, LITE2) is not established against the current generation.

## What BOAR already screened (lite / small)
| model | arm | condition | result | source |
|---|---|---|---|---|
| Qwen2.5-1.5B Q4_K_M | CMP30, CMP30OFF | Pixel 8a, 30 v0.1 dev | 1.7B ≥ 1.5B (+0.045 with declines off); 1.5B faster | QUEUE.md:1422, 1426 |
| Bonsai2-2B PTQ1_0 (base Qwen3.5-2B, ternary) | LITE2, BONSAI2-2B | kit random20 + selftest20 | 2B − 1.7B −0.057 kit / −0.020 st20 | QUEUE.md:1205; CLOSED.md:111-112 |
| LFM2-1.2B (July 2025) | LITEREADERS | ORACLE-ST ADD contexts, random20 | −0.060 vs 1.7B | arms/litereaders/LITEREADERS.md:8-12 |
| Gemma-3-1B-it | LITEREADERS | same | −0.065 vs 1.7B | same |
| Qwen3-1.7B Q8_0 vs Q4_K_M | QUANTLITE | selftest20 + X2b | −0.003 (flat) | QUEUE.md:1239 |
| Qwen3-1.7B thinking 256/512 | LITETHINK | selftest20 | flat / −0.041 | CLOSED.md:126 |
| MiniCPM5-1B | anvil cycle 16 | offline replay vs 1.5B | no gain, 8/120 runaway | SHELF.md:70; anvil/LOG.md:23 |
| [private correspondence with the app maintainer, or a result of a run on his device, removed] |
| LFM2.5-8B-A1B | PACKREAD, SAFEPACK, maintainer | pack items | −0.096 vs 4B, least safe | QUEUE.md:1390, 1389 |
| 4B-class: Qwen3.5-4B, Gemma 4 E4B, Qwen3.5-9B, Ministral 3 8B, Bonsai2-4B | Q35, G4E4B, G4ENG, BONSAI2 | closed-book / engine | none beat Qwen3-4B-2507 | CLOSED.md:16, 107 |

## Never screened, current generation (vendor-reported numbers)
| candidate | date / licence / GGUF | vendor numbers (non-thinking unless noted) | vs Qwen3-1.7B (vendor) | BOAR status |
|---|---|---|---|---|
| **Qwen3.5-2B** | 2026-02-28, Apache-2.0, unsloth/Qwen3.5-2B-GGUF Q4_K_M 1.28 GB (Q4_0 1.21, IQ4_XS 1.17) | MMLU-Pro 55.3, MMLU-Redux 69.2, SuperGPQA 30.4, IFEval 61.2; thinking: MMLU-Pro 66.5, GPQA 51.6, IFEval 78.6 (HF card) | 1.7B non-thinking MMLU-Redux 64.4, GPQA-D 28.6 (Qwen3 TR Table 20); MMLU-Pro 42.9, IFEval 73.7 (Liquid's table) | SHELF.md:68 "checked (header parsed)"; card anvil/cards/compact-reader-by-hot-set.md "ready-to-test", RADAR.md:28 "work stopped" |
| **Gemma 4 E2B-it** | 2026-03-02; QAT Q4_0 GGUF 3.35 GB (2026-05-01), Apache-2.0; 2.3B effective / 5.1B with PLE | MMLU-Pro 60.0, GPQA-D 43.4 (HF card; mode not stated, may be thinking); AA-Omniscience −24 (AA, per anvil card) | AA-Omniscience 1.7B ≈ −83 (benchmarklist mirror, [S]) | SHELF.md:23 "checked (header parsed)"; RADAR.md:29 "work stopped" |
| **LFM2.5-1.2B-Instruct** | 2026-01-04, LFM Open License v1.0 (not OSI; free < USD 10M revenue), official GGUF incl. QAD-Q4_0 | GPQA 38.9, MMLU-Pro 44.4, IFEval 86.2, IFBench 47.3; card: "recommend for agentic tasks, data extraction, and RAG… not recommended for knowledge-intensive tasks"; sampling T 0.1, top_k 50, rep 1.05 | same table: 1.7B 34.9 / 42.9 / 73.7 / 21.3 | never run; LITEREADERS ran the predecessor LFM2-1.2B |
| Granite 4.2-3B | 2026-08-25, Apache-2.0, thinking default | MMLU-Pro 67.8, GPQA 54.8 (thinking presumably) | — | never seen in BOAR files; 3B is above the lite budget (speed) |
| SmolLM3-3B | 2025-07, Apache-2.0 | — | — | never screened; 3B, same caveat |
Not candidates: Nemotron-Labs-Dory1.0-4B (2026-10-16, looped 4B reasoning model, OpenMDW licence, Q5_K_M 3.67 GB only, AA-Omniscience 10 vs Qwen3.5-4B 15 on its own card); no small Qwen3.6/3.8 exists (HF API, Qwen org, latest small text LM = Qwen3.5 0.8B/2B 2026-02-28); no new Gemma small since E2B/E4B; no new Phi-mini; MiniCPM-V-4.7-1B is a VLM.

## Findings
1. **Qwen3.5-2B (native quant) never screened** (high for the lite line). The only measurement is its 1-bit ternary derivative (Bonsai2-2B PTQ1_0), which confounds base model with a 1.58-bit quant and still landed only −0.020 on selftest20 vs the 1.7B (CI crosses 0). Vendor gap vs Qwen3-1.7B is +4.8 MMLU-Redux and ≈ +12 MMLU-Pro in non-thinking mode; IFEval is lower (61.2 vs 73.7), a risk for BOAR's rule-heavy prompts. Template check: Qwen/Qwen3.5-2B chat_template.jinja l.149-152 emits an empty `<think>\n\n</think>` unless `enable_thinking` is true (non-thinking default; the 4B template is the opposite), so `--reasoning off` is consistent. Unknowns: hybrid Gated DeltaNet may not reuse a partial prompt prefix in llama.cpp (PREFIXKV), and ARM CPU prefill for DeltaNet is unmeasured; decode ≈ 0.85× the 1.7B by hot-set ratio (1.18 vs 1.03 GiB). Vendor non-thinking text sampling is unusual: T 1.0, top_p 1.0, top_k 20, presence_penalty 2.0 — the engine's 0.7/40/0.95/0.05 would be off-vendor.
   Cheapest test: LITEREADERS protocol unchanged (ORACLE-ST ADD random20 seed 777, 40 Haiku) + LITE2 selftest20 with X2b (40 Haiku) on unsloth Q4_K_M; ≤ 80 Haiku, ~1.3 GB download, MacBook.
2. **LITEREADERS screened the previous generation** (medium). It ran LFM2-1.2B and Gemma-3-1B (LITEREADERS.md:11-12, "Models: LiquidAI/LFM2-1.2B-GGUF @ 5399e76c… unsloth/gemma-3-1b-it-GGUF") while LFM2.5-1.2B-Instruct (MMLU-Pro 44.4, IFEval 86.2 vendor) and Gemma 4 E2B (MMLU-Pro 60.0 vs Gemma-3-1B 14.0 in Liquid's table) were available with official GGUFs. Its conclusion "no reader ≤ 1.2 GB beats the 1.7B" is therefore about 2025 models. LFM2.5-1.2B is vendor-pitched for RAG/extraction, exactly BOAR's grounded-reading slot (it can add +1.8× decode per LITEREADERS' LFM2 speed). Licence caveat: LFM Open License (not OSI). Gemma 4 E2B caveat: 3.35 GB file, PLE table (1.79 GiB) needs lazy load; fine on 8 GB Android, E4B needed enable_thinking:false handling (anvil LOG cycle 10).
3. **Weekly NEWMODEL sweep for the official orgs was planned for 10-19 and never ran** (low). SWEEP-2026-10-16.md is the only file in arms/newmodel; QUEUE.md:1232 says "Qwen/Gemma/Phi org pages not checked → next sweep Mon 10-19 covers them". This sweep (HF API by author, 13 orgs) closes that gap: nothing newer than the three above at ≤ 2.5B.
4. **Q35 (Qwen3.5-4B) screen ran off-vendor sampling** (low; 4B tier, closed): Q35-screen.md "sampler 0.7/40/0.95/0.05" while Qwen3.5 recommends top_k 20/top_p 0.8 and presence 1.5 (non-thinking general). Gap was −0.08 below bar with cw 45 vs 30, so sampling unlikely to flip it; relevant only if a Qwen3.5-2B screen copies that harness.

## Checked and OK
- Lite engine checkpoint: Qwen3-1.7B has no 2507 instruct refresh (Qwen released 2507 only for 4B/30B/235B); the hybrid model with thinking off is the right Qwen3 1.7B artefact. `--reasoning off` in every LITEREADERS/LITE2 server log, 0 reasoning tokens (LITE2 row, LITEREADERS.md).
- Quant: Q8_0 = Q4_K_M within −0.003 (QUANTLITE), same producer/revision; Q4_K_M is fine.
- Thinking on the 1.7B: measured, flat/negative (LITETHINK).
- 4B-class swaps exhaustively screened (Qwen3.5-4B, Gemma 4 E4B both closed-book and in-engine, Qwen3.5-9B, Ministral, Bonsai2-4B).
- No Qwen3.6/3.8 small dense release exists (HF API 2026-10-20); no new HuggingFaceTB/Phi/Meta small instruct LM since SmolLM3 (2025-07).
- Gemma 4 E2B and Qwen3.5-2B both load on b11010 / llama.rn rc.4 (`gemma4`, `qwen35` archs; Q35 and G4E4B ran on b11010).

## Sources
- https://huggingface.co/Qwen/Qwen3.5-2B (card + chat_template.jinja), https://huggingface.co/unsloth/Qwen3.5-2B-GGUF
- https://huggingface.co/google/gemma-4-E2B-it, https://huggingface.co/google/gemma-4-E2B-it-qat-q4_0-gguf
- https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct, https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-GGUF
- https://huggingface.co/ibm-granite/granite-4.2-3b, https://huggingface.co/nvidia/NVIDIA-Nemotron-Labs-Dory1.0-4B-GGUF
- https://arxiv.org/html/2505.09388v1 (Qwen3 TR Table 20, via promptlit2/model-qwen3-1.7b.md)
- HF API `api/models?author=<org>&sort=createdAt` for Qwen, google, LiquidAI, HuggingFaceTB, microsoft, ibm-granite, openbmb, allenai, mistralai, nvidia, meta-llama, tencent, baidu (2026-10-20)

UNKNOWN: Gemma 4 E2B card mode (thinking vs not) for MMLU-Pro 60.0; AA-Omniscience for Qwen3.5-2B and LFM2.5-1.2B; Qwen3.5 DeltaNet prefix-cache reuse in the engine's llama.rn path; phone decode of E2B/Qwen3.5-2B on the Pixel 8a.
