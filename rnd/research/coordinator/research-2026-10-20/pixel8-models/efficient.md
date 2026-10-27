# Efficient architectures for the Pixel 8a (8 GB) — candidate sweep

Date: 2026-10-20. Angle: MoE with small active params, Gemma 3n/4 E-series (PLE), hybrid Mamba/attention, ternary/BitNet.
Method: Hugging Face Hub API records (`/api/models/<id>`, `/api/models/<id>/tree/main`) read with WebFetch; model cards where noted; WebSearch for llama.cpp support status. No weights downloaded. Phone speed was NOT measured here (no device access); all speed notes are inference from architecture only.

## TL;DR

- Budget reminder from the brief: model + KV + app around 4 GB RSS, decode >= ~8 tok/s on the Pixel 8a.
- **RAM arithmetic for MoE and PLE models:** all experts (MoE) or all per-layer-embedding tables (Gemma 3n/4 E-series) occupy memory, even though the active compute is small. The GGUF file size is the RAM floor (mmap pages still count toward PSS). "Active params" drives decode speed, not RAM.
- Fits the 4 GB budget by file size (Q4_K_M unless noted): **Gemma 4 E2B-it** (3.11 GB, Apache-2.0, not gated), **SmallThinker-4B-A0.6B** (2.63 GB, Apache-2.0, llama.cpp support seen only via a mirror), **LFM2-2.6B** (1.56 GB, LFM 1.0 licence, not Apache), **Gemma 3n E2B-it** (3.03 GB, Gemma licence).
- Does not fit at Q4_K_M: Gemma 4 E4B (4.98 GB), Granite 4.0 H-Tiny (4.25 GB, but IQ4_XS 3.79 GB fits), OLMoE-1B-7B-Instruct (4.21 GB).
- Quality evidence is vendor-reported on all rows. No row has our own kit run. Next step is the runnable check (kit on the desktop, then a Q4 file on the device) for the top 3.

## Candidate table

Q4 file sizes are the exact bytes from the Hub tree listing (GB = bytes / 1e9). "Active" is the stated active or effective count.

| # | Model | Arch | Total / active (stated) | Licence (Hub tag) | Q4_K_M file | Other quants | llama.cpp status | Quality evidence (vendor-reported unless noted) | Fit on Pixel 8a |
|---|---|---|---|---|---|---|---|---|---|
| 1 | google/gemma-4-E2B-it | Gemma 4 PLE | 5.12B raw incl. PLE; 2.3B effective (card) | apache-2.0, not gated | 3.107 GB (3,106,738,272) | IQ4_XS 2.98 GB; Q3_K_M 2.54 GB; Q8_0 5.05 GB | Upstream merged (search; indirect evidence). unsloth GGUF repo with 25 quants | Card: MMLU-Pro 60.0, GPQA Diamond 43.4, LiveCodeBench v6 44.0, MMMLU 67.4 | Tight: 3.1 GB weights + KV. Q3_K_M (2.54) leaves more room |
| 2 | google/gemma-4-E4B-it | Gemma 4 PLE | 8.0B raw (safetensors); effective not fetched | apache-2.0, not gated | 4.977 GB (4,977,171,584) | IQ4_XS 4.72 GB; Q3_K_M 4.06 GB; Q3_K_S 3.86 GB | Same as #1 | Not fetched in this sweep | Over budget at Q4_K_M; only Q3_K_S (3.86 GB) is borderline |
| 3 | google/gemma-3n-E2B-it | Gemma 3n PLE | 5.44B raw (safetensors) | `gemma` (Gemma Terms of Use; gated `manual`) | 3.027 GB (3,026,881,888) | IQ4_XS 2.91 GB; Q3_K_M 2.48 GB | Mainline (unsloth GGUF 25 files; LocalLLMClient issue says bundles up to gemma3n load) | SmallThinker table (vendor-reported, not independent): MMLU 63.04, GPQA 20.2, GSM8K 82.34, IFEval 73.2 | Tight like #1 |
| 4 | ibm-granite/granite-4.0-h-tiny | GraniteMoeHybrid (Mamba2 + attn, MoE) | 6.94B total; 1B active (card, via aggregator) | apache-2.0 | 4.255 GB (4,254,815,392) | IQ4_XS 3.79 GB; Q3_K_M 3.39 GB; UD-Q4_K_XL 4.07 GB; UD-IQ2_XXS 2.39 GB | Community GGUF (unsloth, 27 files). IBM says Mamba2 optimisation can lag in llama.cpp; the dense Micro is recommended for that case | Not fetched in this sweep | Q4_K_M over budget. IQ4_XS fits (3.79 GB) |
| 5 | ibm-granite/granite-4.0-h-1b | GraniteMoeHybrid, dense hybrid | 1.46B (safetensors); dense | apache-2.0 | No GGUF in the repo; size not measured | — | Same family as #4 (arch supported by llama.cpp); no GGUF repo checked | Not fetched | Likely fits (see size estimate below) |
| 6 | PowerInfer/SmallThinker-4BA0.6B-Instruct | SmallThinker MoE (32 experts, top-4) | 4.27B total; 0.6B active (card) | apache-2.0 (custom_code tag) | 2.630 GB (2,630,212,704), from the PowerInfer INT4-QAT repo | Q4_0 2.41 GB; Q4_K_S 2.49 GB; Q3_K_M 2.12 GB; Q8_0 4.55 GB | Commit "model : add support for SmallThinker series (#14898)" seen on a gitlink mirror only. Merge on the official repo NOT confirmed | Card, non-thinking, vendor: MMLU 66.11, GPQA 31.31, GSM8K 80.02, MATH-500 60.60, IFEval 69.69, HumanEval 82.32. Same table, Qwen3-1.7B: 64.19 / 27.78 / 81.88 / 63.6 / 69.50 / 61.59 | Fits (2.6 GB). Decode should be near 0.6B-active class in theory; unmeasured |
| 7 | allenai/OLMoE-1B-7B-0924-Instruct | OLMoE MoE | 6.92B total; 1.3B active (per OLMoE paper arXiv 2409.02060; not fetched) | apache-2.0 (base repo tag) | 4.214 GB (4,213,512,672) | Q4_0 3.93 GB; Q4_K_S 3.96 GB; Q3_K_M 3.34 GB | Community GGUF repo exists; mainline olmoe arch support NOT verified here | Not fetched; 2024 model, expected below 1.7B-class (unverified) | Over budget at Q4_K_M; Q3_K_M (3.34 GB) would fit |
| 8 | LiquidAI/LFM2-2.6B | LFM2 hybrid (conv + attn) | 2.57B (safetensors); dense | `lfm1.0` (license:other; not Apache) | 1.564 GB (1,563,668,704) | Q4_0 1.48 GB; Q5_K_M 1.83 GB; Q8_0 2.73 GB | Official GGUF repo (LiquidAI/LFM2-2.6B-GGUF), so llama.cpp support is in practice | Not fetched in this sweep | Fits well; lots of room for KV |
| 9 | tiiuae/Falcon-H1-1.5B-Deep (base) | Falcon-H1 (Mamba2 + attn, parallel) | 1.55B (safetensors) | `falcon-llm-license` (license:other; not Apache) | No GGUF found: GGUF tree returned 401 | — | Falcon-H1 project says llama.cpp is supported (GitHub) | Not fetched | Likely fits; size unmeasured |
| 10 | microsoft/bitnet-b1.58-2B-4T (GGUF repo) | BitNet b1.58 ternary | 2.41B (GGUF metadata) | MIT | 1.19 GB (ggml-model-i2_s.gguf, 1,187,801,280 B) | — (I2_S only in this repo) | I2_S is a bitnet.cpp format. Mainline llama.cpp loading NOT verified | Vendor, MMLU 53.17, ARC-C 49.91, GSM8K 58.38 vs Qwen2.5-1.5B 60.25 / 46.67 / 56.79. Not comparable to Qwen3-1.7B | Fits. Quality is below the 1.7B bar and the runtime is unproven on Android |
| 11 | microsoft/Phi-tiny-MoE-instruct | PhiMoE | 3.76B (safetensors); active not fetched | MIT | No GGUF in repo | — | `phimoe` in transformers; llama.cpp support NOT verified | Not fetched | Unknown until converted |

Notes on sizes:
- Granite 4.0 H-1B (#5): no measured GGUF. Estimate only: 1.46B params x ~4.85 bits/8 ~ 0.9 GB at Q4_K_M. This is arithmetic, not a file listing.
- SmallThinker-21B-A3B and similar: not fetched. Estimate from total params alone (21B x ~4.85 bits/8) ~ 12.7 GB, so excluded by RAM.

## Per-candidate notes (licence flags first)

1. **Gemma 4 E2B-it (apache-2.0).** Best licence fit of the PLE family. Not gated. Quants are the most complete of any row (25 files). Card gives "2.3B effective, 5.1B including embeddings" and says it is designed for laptops and mobile, but states no RAM figure. Expect RAM near the file size plus KV. Strongest first candidate for the device check.
2. **Gemma 4 E4B-it (apache-2.0).** Same family and licence. Q4_K_M 4.98 GB is over the 4 GB budget. Only useful at Q3_K_S (3.86 GB) and that would probably lose too much. Keep as a reference row, not a candidate.
3. **Gemma 3n E2B-it (gemma licence).** Redistribution in an app is allowed under the Gemma Terms of Use, but it carries use restrictions and the model is gated. Flag for legal review. Also flag: the API call for `google/gemma-3n-E2B-it` returned base_model metadata pointing at `gemma-3n-E4B-it`, and 5.44B raw params, so the E2B/E4B identity should be checked on the card before any use.
4. **Granite 4.0 H-Tiny (apache-2.0).** Good licence. 1B active gives the decode case, but all 6.9B weights sit in RAM, so the RAM floor is 3.8-4.3 GB. IQ4_XS (3.79 GB) is the only quant that fits. The aggregator's "Mamba2 optimisation" caveat means llama.cpp speed may lag; check on the device, not on paper.
5. **Granite 4.0 H-1B (apache-2.0).** The smaller hybrid. No GGUF checked yet. Fits by estimate, but it is a 1.5B-class model, so quality is likely at or below Qwen3-1.7B. Low priority.
6. **SmallThinker-4B-A0.6B (apache-2.0).** Best RAM/active ratio in this sweep: 2.6 GB Q4_K_M for 4.27B total and 0.6B active. Vendor benchmark is near Qwen3-1.7B (MMLU +1.9, GPQA +3.5, IFEval -0.2, GSM8K -1.9, MATH-500 -3.0). That is parity on paper, so the decode and RAM gain has to come from speed. Blocker: llama.cpp mainline support is seen only in a mirror of commit #14898; check that it is on the official repo at the version the app's llama.rn bundles. Also `custom_code` tag: check that the GGUF path does not need it.
7. **OLMoE-1B-7B-Instruct (apache-2.0 base).** Fully open model, Apache-2.0 base tag. Q4_K_M 4.21 GB is above budget; Q3_K_M 3.34 GB fits but loses quality. Old (2024) so expect weaker knowledge than Qwen3-1.7B. Low priority; documented for completeness.
8. **LFM2-2.6B (LFM 1.0 licence, not Apache).** Small file (1.56 GB) and an official GGUF. Licence is custom. The LFM 1.0 licence has a revenue-based threshold for commercial use, reported at around $10M annual revenue; that is from memory, NOT read from the licence text in this session, so verify before any redistribution decision. Also note the existing screen covers LFM2.5-8B-A1B, not LFM2-2.6B.
9. **Falcon-H1-1.5B-Deep (falcon-llm-license, not Apache).** Hybrid, llama.cpp support claimed by the project. No GGUF checked (tree endpoint 401 in this sweep). Custom licence: read the TII terms, including attribution and any use restrictions, before any redistribution.
10. **BitNet b1.58-2B-4T (MIT).** Tiny file (1.19 GB) and MIT licence, but vendor numbers put it below the Qwen2.5-1.5B class on MMLU and MATH-500, and the 1.7B-class bar is unlikely to be met. The official speed claims are for bitnet.cpp, not mainline llama.cpp, and the GGUF uses I2_S. Reject unless a mainline run shows a quality gain.
11. **Phi-tiny-MoE (MIT).** Licence is clean. No GGUF exists in the repo, so conversion and llama.cpp `phimoe` support would both need to be checked first. Not scored.

## llama.cpp support status (summary)

| Arch | Status | Evidence |
|---|---|---|
| gemma4 (E2B/E4B) | Merged upstream (indirect) | WebSearch: LocalLLMClient issue; vendored gemma4.cpp mention; unsloth GGUF repos (25 files each) |
| gemma3n | Supported | Unsloth GGUF repo (25 files); LocalLLMClient note that its build stops at gemma3n |
| granitehybrid (Granite 4.0 H) | Supported in practice | Unsloth GGUF repo (27 files). IBM says Mamba2 optimisation can lag in llama.cpp |
| smallthinker | Commit #14898 seen on a mirror; official merge NOT confirmed | WebSearch, gitlink mirror of llama.cpp |
| lfm2 | Supported in practice | Official LiquidAI GGUF repo |
| falcon-h1 | Claimed by project | Falcon-H1 GitHub README (via WebSearch) |
| olmoe | Community GGUF exists; mainline arch NOT verified | Unsloth-style GGUF repo, no arch confirmation |
| bitnet (I2_S) | bitnet.cpp format; mainline NOT verified | Microsoft model card |
| phimoe | NOT verified | — |

## Sources opened

Hub API records (WebFetch):
- https://huggingface.co/api/models/ibm-granite/granite-4.0-h-tiny
- https://huggingface.co/api/models/unsloth/granite-4.0-h-tiny-GGUF/tree/main
- https://huggingface.co/api/models/ibm-granite/granite-4.0-h-1b
- https://huggingface.co/api/models/PowerInfer/SmallThinker-4BA0.6B-Instruct
- https://huggingface.co/api/models/PowerInfer/SmallThinker-4BA0.6B-Instruct-INT4-QAT/tree/main
- https://huggingface.co/PowerInfer/SmallThinker-4BA0.6B-Instruct (model card, benchmarks)
- https://huggingface.co/api/models/google/gemma-3n-E2B-it
- https://huggingface.co/api/models/unsloth/gemma-3n-E2B-it-GGUF/tree/main
- https://huggingface.co/api/models/google/gemma-4-E2B-it
- https://huggingface.co/google/gemma-4-E2B-it (model card, benchmarks)
- https://huggingface.co/api/models/google/gemma-4-E4B-it
- https://huggingface.co/api/models/unsloth/gemma-4-E2B-it-GGUF/tree/main
- https://huggingface.co/api/models/unsloth/gemma-4-E4B-it-GGUF/tree/main
- https://huggingface.co/api/models/tiiuae/Falcon-H1-1.5B-Deep-Base (licence: falcon-llm-license)
- https://huggingface.co/api/models/tiiuae/Falcon-H1-1.5B-Deep (licence)
- https://huggingface.co/api/models/microsoft/bitnet-b1.58-2B-4T-gguf
- https://huggingface.co/microsoft/bitnet-b1.58-2B-4T (model card, benchmarks and caveat)
- https://huggingface.co/api/models/allenai/OLMoE-1B-7B-0924
- https://huggingface.co/api/models/allenai/OLMoE-1B-7B-0924-Instruct-GGUF/tree/main
- https://huggingface.co/api/models/LiquidAI/LFM2-2.6B (licence: lfm1.0)
- https://huggingface.co/api/models/LiquidAI/LFM2-2.6B-GGUF/tree/main
- https://huggingface.co/api/models/microsoft/Phi-tiny-MoE-instruct

Failed or not fetched:
- https://huggingface.co/api/models/tiiuae/Falcon-H1-1.5B-Deep-GGUF/tree/main returned 401; Falcon-H1 GGUF not checked.
- Falcon-H1-1.5B-Deep-Base API returned 401 on one attempt (the Deep one succeeded).

WebSearch (snippets only, not opened as full pages):
- Granite 4.0 H-Tiny licence and llama.cpp caveat (IBM docs, unsloth docs, aggregator pages)
- SmallThinker licence and GGUF repos (Mungert, PowerInfer, Tiiny)
- Gemma 3n/4 GGUF sizes and llama.cpp support (aggregators)
- llama.cpp gemma4 merge (LocalLLMClient issue; hex.pm vendored source)
- bitnet.cpp vs mainline (arXiv 2410.16144; wavect blog; bitnet.cpp repo)
- SmallThinker llama.cpp commit (gitlink mirror of #14898)

## UNKNOWN (not checked this session)

- Ling-lite / Ling-mini, Hunyuan-A0.5B, and other small MoEs in the 0.5-2B active class: not searched.
- Gemma 4 E4B effective parameter count and benchmarks: not fetched.
- Granite 4.0 H-1B and Falcon-H1 GGUF sizes, benchmarks and llama.cpp arch confirmation: not fetched.
- Whether mainline llama.cpp (at the version llama.rn bundles) loads smallthinker, olmoe, phimoe, and granitehybrid GGUFs.
- Decode and TTFT for every row on the Pixel 8a: not measured.
- Licence text for LFM 1.0 and Falcon-LLM: revenue thresholds and attribution need reading from the full licence before any redistribution decision.

## Recommended next steps (for the device check, not run here)

1. Gemma 4 E2B-it Q3_K_M or Q4_K_M and SmallThinker-4B-A0.6B Q4_K_M: confirm llama.rn loads them, measure RSS, decode and TTFT on the Pixel 8a with the kit's 57 dev items.
2. LFM2-2.6B Q4_K_M as a speed reference (small file, official GGUF).
3. Confirm llama.cpp mainline support for smallthinker (PR #14898) at the llama.rn version.
4. Licence review on LFM 1.0, Falcon-LLM and Gemma terms before any shipping decision.
