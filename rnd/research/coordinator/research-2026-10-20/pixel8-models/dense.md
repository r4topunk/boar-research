# Dense instruct models 2.5-4.5B (and near) for the Pixel 8a slot, angle: dense

Date: 2026-10-20. Researcher: haiku sweep (dense angle). Weights not downloaded.
Target: model + KV + app around 4 GB RSS, decode >= ~8 tok/s on Pixel 8a (Tensor G3, 8 GB).
Baselines (from the brief, not re-measured): Qwen3-1.7B Q4_K_M, decode 12-16 tok/s; Qwen3-4B-Instruct-2507 decode 3.6-6 tok/s.

## Caveats (read first)
- Benchmark protocols differ per card (CoT vs 5-shot, thinking vs non-thinking, base vs instruct). Cross-card deltas are indicative only. Where a card gives a Qwen3-1.7B or Qwen3-4B row, that row is quoted from that card, not re-run.
- Qwen3.5 cards report thinking and non-thinking separately. Both are shown.
- No candidate card reports SimpleQA or a RAG/grounding number we can use. Gap: "knowledge from weights" and "reading retrieved text" are not measured by any card here.
- GGUF sizes are the Q4_K_M file sizes from the Hub API (blobs=true). They are file sizes, not RSS. Add KV cache and runtime overhead when judging fit.
- Decode speed on Pixel 8a is not measured for any candidate here. Speed is estimated from parameter count only; Qwen3-4B measured at 3.6-6 tok/s on the same phone.
- Licence strings are as read from the Hub tag and card. Gemma and Llama licence terms need a legal read before shipping.

## Reference rows (from the brief / cards)
Qwen3-1.7B (non-thinking, as printed on Qwen3.5 card): MMLU-Pro 40.2, MMLU-Redux 64.4, IFEval 68.2.
Qwen3-1.7B (thinking, Qwen3.5 card): MMLU-Pro 56.5, MMLU-Redux 73.9, GPQA 40.1, IFEval 72.5.
Qwen3-1.7B (non-thinking, SmolLM3 card): Global MMLU 49.5, GPQA 31.8, IFEval 74.0.
Qwen3-1.7B (non-thinking, EXAONE card): MMLU-Pro 43.7, MMLU-Redux 63.4, GPQA 28.6, IFEval 68.2.
Qwen3-4B-2507 (non-thinking, Qwen3.5 card): MMLU-Pro 69.6, MMLU-Redux 84.2, IFEval 83.4.
Qwen3-4B-2507 (thinking): MMLU-Pro 74.0, MMLU-Redux 86.1, GPQA 65.8, IFEval 87.4.

## Candidates

### 1. Qwen3.5-2B (dense, hybrid thinking)
- Sources opened: https://huggingface.co/Qwen/Qwen3.5-2B (card), https://huggingface.co/unsloth/Qwen3.5-2B-GGUF (API, file size).
- Params: 2.27B total (safetensors). Multimodal-capable family; text use only here.
- Q4_K_M: 1.281 GB (unsloth). Q4_K_S 1.218 GB.
- Knowledge (non-thinking): MMLU-Pro 55.3 (vs Qwen3-1.7B 40.2), MMLU-Redux 69.2 (vs 64.4).
- Knowledge (thinking): MMLU-Pro 66.5 (vs 56.5), MMLU-Redux 79.6 (vs 73.9), GPQA 51.6 (vs 40.1).
- Instruction following: IFEval non-thinking 61.2 (vs 68.2, worse); thinking 78.6 (vs 72.5, better).
- SimpleQA / RAG: not in card.
- Context 262,144 native. Licence Apache-2.0. GGUF: yes (unsloth, plus other builds on Hub).
- Verdict: strongest knowledge gain per byte under the 1.7B size class. Non-thinking IFEval is weaker than the 1.7B, so the answer format needs testing. Candidate for the 1.7B slot. Needs a device decode check.

### 2. Qwen3.5-4B (dense, hybrid thinking)
- Sources opened: https://huggingface.co/Qwen/Qwen3.5-4B (card), https://huggingface.co/unsloth/Qwen3.5-4B-GGUF (API).
- Params: 4.66B total (safetensors). Multimodal family.
- Q4_K_M: 2.741 GB (unsloth). Q4_K_S 2.59 GB.
- Benchmarks (card; mode not stated for the table, likely thinking): MMLU-Pro 79.1, MMLU-Redux 88.8, GPQA Diamond 76.2, IFEval 89.8, IFBench 59.2, AA-LCR 57.0, LongBench v2 50.0. MMLU and SimpleQA not in card.
- Context 262,144 native, up to 1.01M with YaRN. Licence Apache-2.0.
- Verdict: strongest knowledge number in this set, but it is 4.66B params and about the same memory footprint as Qwen3-4B (already measured at 3.6-6 tok/s, killed once at 4.4 GB RSS). Likely fails the speed gate. Listed because it is the frontier of the family. Not a practical candidate.

### 3. SmolLM3-3B (dense, hybrid thinking)
- Sources opened: https://huggingface.co/HuggingFaceTB/SmolLM3-3B (card), https://huggingface.co/bartowski/HuggingFaceTB_SmolLM3-3B-GGUF (API).
- Params: 3.08B (safetensors).
- Q4_K_M: 1.915 GB (bartowski). Q4_K_S 1.818 GB.
- Knowledge (non-thinking): Global MMLU 53.5 (Qwen3-1.7B 49.5, Qwen3-4B 65.1). GPQA Diamond 35.7 (1.7B 31.8, 4B 44.4).
- Knowledge (thinking): Global MMLU 64.1 (1.7B 62.3, 4B 73.3). GPQA 41.7 (1.7B 39.9, 4B 55.3).
- Instruction following: IFEval non-thinking 76.7 (1.7B 74.0, 4B 68.9). Thinking 71.2 (1.7B 74.2, 4B 85.4).
- Code/math: LiveCodeBench non-thinking 15.2 (1.7B 15.0, 4B 24.9). GSM-Plus non-thinking 72.8 (1.7B 68.3, 4B 82.1).
- Context: 64k trained, 128k with YaRN.
- Licence Apache-2.0. GGUF: yes.
- Verdict: a small, clear step above Qwen3-1.7B on knowledge and IFEval, and 1.9 GB file. Still well below Qwen3-4B on knowledge. Good fit for the speed budget.

### 4. Phi-4-mini-instruct (3.84B, dense)
- Sources opened: https://huggingface.co/microsoft/Phi-4-mini-instruct (card), https://huggingface.co/unsloth/Phi-4-mini-instruct-GGUF (API).
- Params: 3.84B (safetensors).
- Q4_K_M: 2.492 GB (unsloth and bartowski, same size).
- Benchmarks (card, 5-shot/0-shot CoT as labelled): MMLU 67.3 (5-shot), MMLU-Pro 52.8 (0-shot CoT), GPQA 25.2 (0-shot CoT), MATH 64.0, ARC-C 83.7, BoolQ 81.2, OpenBookQA 79.2, TruthfulQA MC2 66.4, Arena Hard 32.8. No Qwen comparison columns in the card.
- SimpleQA / IFEval / RAG: not in card.
- Context 128K. Licence MIT.
- Verdict: strong MMLU and MMLU-Pro on paper, weak GPQA (25.2). 2.49 GB file. MMLU-Pro 52.8 with a different protocol. Must test factual recall on our kit before any claim.

### 5. Phi-4-mini-flash-reasoning (3.85B, reasoning-focused)
- Sources opened: https://huggingface.co/microsoft/Phi-4-mini-flash-reasoning (API only; card not fetched).
- Params: 3.85B (safetensors). Licence MIT.
- GGUF: not found under the names tried (unsloth and bartowski lookups returned auth errors). Architecture is non-standard, so llama.cpp support is unverified.
- Verdict: reasoning model, not an instruct model for short answers. Excluded from the slot unless a GGUF exists and it runs.

### 6. Granite 4.0 micro (3.4B, dense)
- Sources opened: https://huggingface.co/ibm-granite/granite-4.0-micro (card), https://huggingface.co/bartowski/ibm-granite_granite-4.0-micro-GGUF (API).
- Params: 3.40B (safetensors). Dense transformer (not the hybrid Mamba variants).
- Q4_K_M: 2.10 GB (bartowski). Q4_K_S 1.998 GB.
- Benchmarks (card, the card compares only Granite variants): MMLU 65.98 (5-shot), MMLU-Pro 44.5 (5-shot CoT), GPQA 30.14 (0-shot CoT), BBH 72.48, IFEval 82.31 (strict, instruct+prompt), ArenaHard 25.84, GSM8K 85.45, HumanEval 80.
- RAG / grounding: none in card. SimpleQA: not in card.
- Context 128K. Licence Apache-2.0.
- Verdict: MMLU 66 and IFEval 82 are both above Qwen3-1.7B (non-thinking IFEval 74.0 on SmolLM3 card, 68.2 on Qwen3.5 card); knowledge is in the mid-range. Good candidate for the IFEval/format side. Decode speed unmeasured.

### 7. Ministral 3 3B Instruct 2512 (3.85B incl. vision encoder?, dense)
- Sources opened: https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512 (card), https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF and bartowski mirror (API).
- Params: 3.85B (safetensors). Card lists vision support; text-only use is what we need.
- Q4_K_M: 2.146 GB (unsloth and bartowski, same size).
- Benchmarks (card, base MMLU 5-shot, reasoning and instruct tables as labelled): MMLU 0.707 (base table; Qwen3-4B base 0.713, Gemma 3 4B base 0.589). GPQA Diamond 0.534 (reasoning table; Qwen3-VL-4B-Thinking 0.601). Arena Hard 0.305 (Gemma 3 4B IT 0.318, Qwen3-VL-4B-Instruct 0.438). MATH 0.830 (Maj@1, instruct table).
- IFEval / MMLU-Pro / SimpleQA: not in card.
- Context 256k. Licence Apache-2.0. Official GGUF: not stated on card; community GGUFs exist (unsloth, bartowski).
- Verdict: MMLU 0.707 on the base table is near Qwen3-4B base. Arena Hard 30.5 is low-to-mid. Strong math. Worth a knowledge test; the card does not show knowledge at instruct level.

### 8. Falcon-H1-3B-Instruct (hybrid Mamba-Transformer)
- Sources opened: https://huggingface.co/tiiuae/Falcon-H1-3B-Instruct (card; the table is labelled Falcon-H1-3B, base vs instruct not stated), https://huggingface.co/tiiuae/Falcon-H1-3B-Instruct-GGUF and unsloth mirror (API).
- Params: 3.15B (safetensors).
- Q4_K_M: 1.889 GB (tiiuae official GGUF; same size on unsloth).
- Benchmarks (card table, Falcon-H1-3B vs Qwen3-4B vs Llama3.2-3B vs Gemma3-4B; mode and base/instruct not stated): MMLU 68.3 (Qwen3-4B 67.01), MMLU-Pro 43.69 (Qwen3-4B 29.75), GPQA 33.89 (Qwen3-4B 28.02), IFEval 85.05 (Qwen3-4B 84.01), GSM8K 84.76, MATH-500 74.2 (Qwen3-4B 85.0).
- Context: not stated in extracted card text.
- Licence: "Falcon-LLM License" (non-standard, not an OSI licence). Read the terms before shipping.
- Verdict: numbers look strong on paper, but the card does not say which mode produced them, and the Qwen3-4B row here may not be the 2507 instruct. Hybrid architecture is llama.cpp supported on the official GGUF. Licence is the main risk. Re-check the card wording before any claim.

### 9. Llama 3.2 3B Instruct (dense)
- Sources opened: https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct (API), card text in the Phi-4-mini comparison table (Meta's Llama-3.2-3B-Ins column), https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF (API).
- Params: 3.21B (safetensors).
- Q4_K_M: 2.019 GB (bartowski).
- Benchmarks (from the Phi-4-mini card comparison table, Meta's numbers): MMLU 61.8 (5-shot), MMLU-Pro 39.2 (0-shot CoT), GPQA 24.3, ARC-C 76.1, BoolQ 71.4, Arena Hard 17.0.
- IFEval / SimpleQA: not in extracted data.
- Context 128K. Licence "llama3.2" (Llama 3.2 Community License; has attribution, acceptable use policy, and a 700M MAU clause). Redistribution in an app is allowed under those terms, but the licence must be read; flag it.
- Verdict: MMLU-Pro 39.2 is about the same as Qwen3-1.7B non-thinking (40.2). Weaker than most candidates on knowledge. Low priority.

### 10. Gemma 3 4B IT (dense, multimodal family)
- Sources opened: https://huggingface.co/google/gemma-3-4b-it (card; the extracted numbers are for the PRETRAINED 4B, not the IT model), https://huggingface.co/bartowski/google_gemma-3-4b-it-GGUF (API). Falcon-H1 card comparison row for Gemma3-4B also used.
- Params: 4.30B (safetensors).
- Q4_K_M: 2.49 GB (bartowski). Q4_K_S 2.378 GB.
- Benchmarks: PT 4B card: MMLU 59.6 (5-shot), MMLU-Pro CoT 29.2, GPQA 15.0 (5-shot), MATH 24.2, HumanEval 36.0. From Falcon-H1 card comparison (mode unstated): MMLU 59.53, MMLU-Pro 29.71, IFEval 77.01, GSM8K 77.41. IT-specific numbers not extracted.
- SimpleQA / FACTS grounding / RAG: not in the extracted text.
- Context 128K input, 8K output.
- Licence: "gemma" (Gemma Terms of Use). The card links to the terms but does not state whether they restrict redistribution. Needs a read of the linked terms before shipping. Flagged.
- Verdict: knowledge numbers look weaker than Qwen3-4B and Phi-4-mini on MMLU-Pro. Gemma licence flag applies. Low priority.

### 11. EXAONE 4.0 1.2B (dense)
- Sources opened: https://huggingface.co/LGAI-EXAONE/EXAONE-4.0-1.2B (card), https://huggingface.co/bartowski/LGAI-EXAONE_EXAONE-4.0-1.2B-GGUF (API).
- Params: 1.28B (safetensors).
- Q4_K_M: 0.812 GB (bartowski).
- Benchmarks (card, reasoning mode): MMLU-Redux 71.5, MMLU-Pro 59.3, GPQA-Diamond 52.0, IFEval 67.8. Non-reasoning: MMLU-Redux 66.9, MMLU-Pro 52.0, GPQA 40.1, IFEval 74.7 (vs Qwen3-1.7B non-thinking 63.4, 43.7, 28.6, 68.2 per the same card).
- Context 65,536. Licence: "EXAONE AI Model License Agreement 1.2 - NC": NON-COMMERCIAL. Card text restricts use against development of competing models.
- Verdict: EXCLUDED for app redistribution. Numbers are strong for its size. Recorded so no one re-proposes it without the licence change.

### 12. Qwen3.5-0.8B (dense, hybrid) — excluded by size
- Sources opened: https://huggingface.co/Qwen/Qwen3.5-0.8B (card, via the Qwen3.5-2B comparison table), API.
- Params 0.87B. Non-thinking MMLU-Pro 29.7, MMLU-Redux 48.5, IFEval 52.1.
- Verdict: below the 1.7B on every row shown. Excluded.

### 13. MiniCPM4 8B / MiniCPM-V-4 (4.06B, vision) — excluded
- MiniCPM4-8B: 8.19B params (API). Too big.
- MiniCPM-V-4: 4.06B params (API), an image-text-to-text model. Vision is not needed for the slot. Not checked further.
- MiniCPM 4 small (0.5B/1B) variants were not checked in this sweep.

## Summary table (Q4_K_M file size, licence, key rows)

| # | Model | Params | Q4_K_M GB | Licence | MMLU-Pro / knowledge | IFEval | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Qwen3.5-2B | 2.27B | 1.281 | Apache-2.0 | 55.3 (non-think), 66.5 (think) | 61.2 / 78.6 | strongest knowledge under 2.5B |
| 2 | Qwen3.5-4B | 4.66B | 2.741 | Apache-2.0 | 79.1 (think) | 89.8 | likely too slow (4B class) |
| 3 | SmolLM3-3B | 3.08B | 1.915 | Apache-2.0 | Global MMLU 53.5 | 76.7 / 71.2 | small step over 1.7B |
| 4 | Phi-4-mini-instruct | 3.84B | 2.492 | MIT | MMLU 67.3, MMLU-Pro 52.8 | not in card | weak GPQA 25.2 |
| 5 | Phi-4-mini-flash-reasoning | 3.85B | n/a | MIT | reasoning-focused | n/a | GGUF not found |
| 6 | Granite 4.0 micro | 3.40B | 2.10 | Apache-2.0 | MMLU 66.0, MMLU-Pro 44.5 | 82.3 | no RAG numbers |
| 7 | Ministral 3 3B Instruct 2512 | 3.85B | 2.146 | Apache-2.0 | MMLU 0.707 (base) | not in card | 256k ctx, strong math |
| 8 | Falcon-H1-3B-Instruct | 3.15B | 1.889 | Falcon-LLM License | MMLU-Pro 43.7, MMLU 68.3 | 85.1 | mode unclear; licence risk |
| 9 | Llama 3.2 3B Instruct | 3.21B | 2.019 | Llama 3.2 Community | MMLU-Pro 39.2 | not extracted | weak knowledge |
| 10 | Gemma 3 4B IT | 4.30B | 2.49 | Gemma Terms | PT MMLU-Pro 29.2 | 77.0 (Falcon card row) | licence to read |
| 11 | EXAONE 4.0 1.2B | 1.28B | 0.812 | EXAONE AI Model License 1.2 - NC | MMLU-Pro 52.0 (non-reasoning) | 74.7 | NON-COMMERCIAL: excluded |
| 12 | Qwen3.5-0.8B | 0.87B | n/a | Apache-2.0 | MMLU-Pro 29.7 | 52.1 | too small |
| 13 | MiniCPM4-8B | 8.19B | n/a | Apache-2.0 | not checked | not checked | too big |

## Decode speed
- No candidate measured on Pixel 8a in this sweep. Speed is inferred from size only. Qwen3-4B (4B class) measured 3.6-6 tok/s; Qwen3-1.7B measured 12-16 tok/s.
- Smallest candidates by file size: EXAONE 1.2B (excluded), Qwen3.5-2B (1.28 GB), Falcon-H1-3B (1.89 GB), SmolLM3-3B (1.92 GB), Granite 4.0 micro (2.10 GB), Ministral 3B (2.15 GB).
- Phone measurement needed for Qwen3.5-2B, SmolLM3-3B and Granite 4.0 micro first (the three most likely to clear the 8 tok/s gate and beat the 1.7B on knowledge or IFEval).

## Recommended next steps (for the coordinator, not executed here)
1. Measure decode and RSS on Pixel 8a (llama.rn or llama-bench on device) for Qwen3.5-2B (non-thinking), SmolLM3-3B, Granite 4.0 micro.
2. Run the kit's reading/knowledge items on those three before any claim.
3. Read the Gemma and Falcon-H1 licence texts if either moves up.
4. Not checked in this sweep: SimpleQA numbers for any candidate, a GPQA/MMLU re-run under one protocol, MiniCPM4 small variants.

## Sources opened (all fetched 2026-10-20)
- https://huggingface.co/api/models/<id> for: Qwen/Qwen3.5-2B, Qwen/Qwen3.5-4B, Qwen/Qwen3.5-0.8B, microsoft/Phi-4-mini-instruct, microsoft/Phi-4-mini-flash-reasoning, HuggingFaceTB/SmolLM3-3B, meta-llama/Llama-3.2-3B-Instruct, google/gemma-3-4b-it, ibm-granite/granite-4.0-micro, openbmb/MiniCPM4-8B, openbmb/MiniCPM-V-4, LGAI-EXAONE/EXAONE-4.0-1.2B, tiiuae/Falcon-H1-3B-Instruct, mistralai/Ministral-3-3B-Instruct-2512
- GGUF API (blobs): unsloth/Qwen3.5-2B-GGUF, unsloth/Qwen3.5-4B-GGUF, bartowski/microsoft_Phi-4-mini-instruct-GGUF, unsloth/Phi-4-mini-instruct-GGUF, bartowski/HuggingFaceTB_SmolLM3-3B-GGUF, bartowski/Llama-3.2-3B-Instruct-GGUF, bartowski/google_gemma-3-4b-it-GGUF, bartowski/ibm-granite_granite-4.0-micro-GGUF, bartowski/LGAI-EXAONE_EXAONE-4.0-1.2B-GGUF, bartowski/mistralai_Ministral-3-3B-Instruct-2512-GGUF, unsloth/Ministral-3-3B-Instruct-2512-GGUF, tiiuae/Falcon-H1-3B-Instruct-GGUF, unsloth/Falcon-H1-3B-Instruct-GGUF
- Model cards (WebFetch): Qwen/Qwen3.5-4B, Qwen/Qwen3.5-2B, microsoft/Phi-4-mini-instruct, HuggingFaceTB/SmolLM3-3B, ibm-granite/granite-4.0-micro, mistralai/Ministral-3-3B-Instruct-2512, google/gemma-3-4b-it, tiiuae/Falcon-H1-3B-Instruct, LGAI-EXAONE/EXAONE-4.0-1.2B
- Not opened (auth error on bartowski/unsloth lookup): Phi-4-mini-flash-reasoning GGUF.
