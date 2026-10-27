# Lit review: fine-tuning a small RAG reader for faithful, complete, grounded answers (2026-10-06)

## TL;DR
1. **Fine-tuning ≤8B readers for grounded QA works, and in 5+ papers the gains transfer out of domain.** Examples: InstructRAG, RankRAG (biomedical zero-shot), CANOE (11 unseen tasks), Trust-Align (ExpertQA), R-Tuning (refusal as a meta-skill). RAFT, by contrast, is same-domain only.
2. **Effect sizes at 3–8B:** short-form accuracy +1 to +9 pts over vanilla RAG-SFT (InstructRAG) and +5 to +22 over the untuned instruct model (RankRAG, ChatQA). Long-form faithfulness +6 to +10 pts (CANOE FaithScore). Long-form fact recall/completeness +5 to +10 pts, but only with RL or DPO (RioRAG). Trust-Score +5 to +30 with DPO on 19k pairs (Trust-Align, Qwen2.5-3B/7B, Llama-3-8B).
3. **My extrapolation to our 1–5 completeness scale** (not measured anywhere): a good SFT(+DPO) run might take 2.6 to roughly 2.9–3.3. A **1k-example LoRA SFT alone: about +0.1 to +0.4, and zero is plausible.** No paper closes a frontier-sized gap like 2.6 → 4.9.
4. **1k examples is enough for behaviour** (RetRobust: 1k examples make a 13B robust to irrelevant context; ChatQA: 1.5k unanswerable samples is the optimum). It is **not enough for big capability gains.** The large results used 10k–150k examples or RL.
5. **Our failure modes are documented at this size.** Small models' answers get overwritten by retrieved context: ClashEval >60%; "Can SLMs use what they retrieve" reports 42–100% of answers the model already knew are destroyed. MoE does not fix reading: Vectara Qwen3-235B-A22B hallucinates 9.3% vs 4.8% for Qwen3-8B, which matches our +0.03.
6. **Main risks:**
   - Q4_K_M can eat fine-tune gains: 0.99 → 0.89 on a 1B QLoRA model. Small weight deltas get "rounded away" (unlearning paper: 21% → 83% of forgotten knowledge comes back after 4-bit quantization).
   - Benign fine-tuning raises harmfulness: 0.3% → 16.1% on Llama-2-7B-chat.
   - Numeracy/domain fine-tuning can *increase* numeric hallucination: Mistral-7B 5% → 83–91%.
   - Length gaming of the judge: a 41-pt win-rate swing from verbosity alone.

## 1. Fine-tuning for RAG reading / context faithfulness
| Paper | Year | Sizes | Method | Key number | Transfer to unseen corpora? | URL |
|---|---|---|---|---|---|---|
| RAFT | 2024 | Llama-2-7B | SFT, 1 gold + 4 distractors, golden doc in P=40–100% of samples, CoT with verbatim quotes | PubMed 73.3 vs 58.8 (7B+RAG); HotpotQA 35.3 vs 0.03; CoT +9.7 HotpotQA | **No**: same-domain, new questions/docs. Data size and compute not reported | https://arxiv.org/html/2403.10131v2 |
| Self-RAG | 2023 | Llama-2-7B/13B | SFT on 150k examples with reflection tokens | 7B: PopQA 54.9 vs 14.7; Bio FactScore 81.2 vs 44.5; ASQA citation precision/recall 66.9/67.8 | Partial (multi-task eval) | https://arxiv.org/abs/2310.11511 |
| RA-DIT | 2023 | Llama 7B–65B | Dual instruction tuning of LM and retriever | 65B 0-shot avg EM 50.5 vs 43.1 (REPLUG); up to +8.9 0-shot | Held-out tasks, yes | https://arxiv.org/abs/2310.01352 |
| RetRobust (Yoran et al.) | 2024 | Llama-2-13B (QLoRA) | ~1k mixed relevant/irrelevant contexts | NQ +2.9 with relevant context; irrelevant context no longer hurts | Per-dataset training | https://arxiv.org/html/2310.01558v2 |
| ChatQA 1.5 | 2024 | Llama-3-8B/70B | 2-stage SFT; stage 2 uses ~7k conversational QA + 1.5k unanswerable + TAT-QA | ChatRAG avg 55.2 vs 46.7 (Llama-3-8B-Instruct); ConvFinQA 78.5 vs 58.1 | Yes (zero-shot benchmark) | https://arxiv.org/html/2401.10225v5 |
| RankRAG | 2024 | Llama-3-8B/70B | ChatQA mix + ~50k ranking pairs | 8B: NQ 50.6 vs 30.9 (Instruct); PopQA 57.6 vs 34.9; Mirage biomedical avg 64.0 vs 60.0 (ChatQA-8B) | **Yes**: biomedical zero-shot | https://arxiv.org/html/2407.02485v1 |
| InstructRAG | 2025 | Llama-3-8B/70B | SFT on self-synthesized denoising rationales; 4k–167k examples per dataset | 8B vs vanilla SFT: NQ 65.7 vs 56.6; ASQA 47.6 vs 43.8; PopQA 66.2 vs 61.0 | **Yes** (short↔long, single↔multi-hop); exact OOD numbers not extracted | https://arxiv.org/html/2406.13629v2 |
| Trust-Align | 2025 | Llama 1B–8B, Qwen2.5 0.5B–7B, Phi-3.5 | DPO on 19k pairs; negatives cover 5 hallucination types | Trust-Score: Qwen2.5-3B ASQA 46.9 → 65.9; Llama-3-8B +30; DPO > SFT in 26/27 configs; correctness mixed (ASQA 2/9 models up) | **Yes**: ExpertQA, 8B 54.9 vs GPT-4 54.7 | https://arxiv.org/html/2409.11242v4 |
| Context-DPO | 2025 | Llama-2-7B, Qwen2-7B, … | DPO, faithful vs "stubborn" answers (ConFiQA) | +35% to +280% context-faithfulness; TruthfulQA within 1% | ConFiQA-style (counterfactual) | https://arxiv.org/abs/2412.15280 |
| CANOE | 2025 (AAAI '26) | Llama-3-8B, Qwen2.5-7B–72B | 10k synthetic QA from Wikidata (30% counterfactual) + Dual-GRPO | Llama-3-8B: +22.6 overall faithfulness; XSum FaithScore 74.4 vs 64.2; CLAPNQ 64.9 vs 58.5. Plain GRPO made the model copy spans | **Yes**: 11 OOD tasks | https://arxiv.org/html/2505.16483v3 |
| RAG-Instruct | 2025 | Llama-3.1-8B, … | 40k synthetic RAG instructions from Wikipedia, 5 paradigms | PopQA 68.4 vs 60.8; TriviaQA 79.3 vs 73.4 | Zero-shot multi-task | https://aclanthology.org/2025.emnlp-main.192/ |
| RioRAG | 2025 (ACL '26) | Qwen2.5 1.5B/7B/14B | RL with nugget-checklist reward; 10k ELI5 questions, no gold answers | RAGChecker: fact recall 66.3 vs 61.2 (DPO), faithfulness 58.2 vs 53.1; answers get longer without a length penalty | LongFact (38 domains) | https://arxiv.org/abs/2505.20825 |
| FRONT / fine-grained citation rewards (ALCE) | 2024 | Llama-2-7B | Quote grounding, then consistency alignment / RL | FRONT: +14.2% citation quality avg, beats ChatGPT | ALCE datasets | https://aclanthology.org/2024.findings-acl.838.pdf ; https://arxiv.org/abs/2402.04315 |
| OCC-RAG | 2026 | Qwen3-0.6B/1.7B base | Mid-training on 3.25M synthetic QA (teacher Qwen3.5-27B), 43k abstention | **Qwen3-4B baseline**: ConFiQA 69.7, memorization ratio 10.3, MuSiQue-Un refusal 64.1. OCC-1.7B: 81.4 / 87.2 | Not tested | https://arxiv.org/html/2606.00683v1 |
| Pleias-RAG 350M/1B | 2025 | 0.35B, 1.2B | Mid-training on synthetic RAG with literal-quote citations | Beats <4B models on HotpotQA/2Wiki; competitive with Qwen2.5-7B/Llama-3.1-8B (numbers not extracted) | Multilingual | https://arxiv.org/abs/2504.18225 |
| Command R7B (Cohere) | 2024 | 7B | SFT + preference tuning for grounded generation with citations | No ablation numbers published: **not found** | n/a | https://docs.cohere.com/docs/command-r7b |
| Qwen/Llama official "RAG SFT recipe" | — | — | — | **not found** (no published recipe or ablation) | — | https://qwenlm.github.io/blog/qwen3/ |
| Loss of context-awareness after instruction tuning | 2024 | Llama-2/3, TinyLlama | Attention-based diagnosis and fix | General instruction tuning lowers attention to context (detailed numbers not extracted) | — | https://arxiv.org/abs/2411.02688 |

## 2. Number / numeric faithfulness
| Paper | Year | Sizes | Method | Key number | Transfer? | URL |
|---|---|---|---|---|---|---|
| Financial FT fails (numeric hallucination) | 2026 | Mistral-7B | QLoRA r8; 1k domain + 500 QA + 2k numeracy samples | Overt numeric hallucination 5.4% (base) → 82.5–90.8% (FT), even with numbers in the input (58.8–90%). Cause: "template injection". Numeracy SFT made it **worse** | Negative evidence | https://arxiv.org/html/2609.04806 |
| ChatQA (TAT-QA in the mix) | 2024 | Llama-3-8B | Add table/arithmetic QA to context SFT | ConvFinQA F1 78.5 vs 58.1 | Yes (benchmark) | https://arxiv.org/html/2401.10225v5 |
| TAT-LLM | 2024 | Llama-2-7B/70B | Extractor → reasoner → executor SFT | 7B EM: FinQA 64.6, TAT-QA 74.6 (> GPT-4) | In-domain (finance tables) | https://arxiv.org/abs/2401.13223 |
| RSAT | 2026 | Qwen2.5 1.5–7B, Llama 1–8B | SFT + GRPO with cell-level citations and an NLI faithfulness reward | Faithfulness 0.224 (SFT) → 0.826; removing the faithfulness reward drops it 0.97 → 0.03 | Not reported | https://arxiv.org/abs/2605.00199 |
| Number Cookbook (NUPA) | 2025 | small + practical LLMs | 41 numeric task combinations | Naive FT helps many tasks; NUPA-specific tricks don't help pretrained models | — | https://arxiv.org/abs/2411.03766 |
| Numerical representation invariance | 2026 | Qwen 3.5B/9B, Mistral Small 4, gpt-oss-20b | Same quantity in different formats/units | Agreement across formats 0.85–0.98; Mistral 0.699 on unit-converted inputs, 265 errors off by a power of 10 | — | https://arxiv.org/abs/2609.25009 |
| NUMCoT | 2024 | various | Numerals/units in CoT | Magnitude errors (hundred-million vs billion), dropped zeros | — | https://arxiv.org/pdf/2406.02864 |
| Fine-tuning specifically for **number copying in RAG** | — | — | — | **not found** | — | — |

## 3. Length/completeness vs correctness; abstention and factuality alignment
| Paper | Year | Sizes | Method | Key number | Transfer? | URL |
|---|---|---|---|---|---|---|
| Response length vs long-form factuality | 2025 | GPT-4o; Llama-3.1-8B in analysis | Controlled length | Bio precision 94.5% @100 words → 90.5% @500. Cause: "facts exhaustion" (closed-book) | — | https://arxiv.org/html/2505.23295 |
| FActScore | 2023 | many | Atomic-fact precision | Later facts in a generation are less precise | — | https://arxiv.org/abs/2305.14251 |
| FactTune | 2024 | Llama-2-7B | DPO with factuality preferences | Factual error rate −53% (bios), −50% (medical) vs Llama-2-Chat | Two domains | https://arxiv.org/abs/2311.08401 |
| FLAME | 2024 | Llama-2-70B | Factuality-aware SFT (self-generated) + DPO | FActScore +5.6 vs standard alignment; standard RLHF rewards favour long, hallucinated answers | — | https://arxiv.org/abs/2405.01525 |
| Fine-tuning on new knowledge (Gekhman) | 2024 | PaLM-2 | Closed-book QA with a controlled share of unknown facts | Hallucination rises linearly as unknown facts get learned → **teacher targets must not add facts beyond the passages** | — | https://aclanthology.org/2024.emnlp-main.444 |
| R-Tuning | 2024 | Llama 7B/13B | Refusal-aware SFT | Refusal works as a meta-skill and transfers OOD (numbers not extracted) | Yes | https://arxiv.org/abs/2311.09677 |
| RAGChecker | 2024 | Llama-3 8B/70B, … | Claim-level metrics | More context → higher claim recall but more noise sensitivity; trade-off is structural | — | https://arxiv.org/abs/2408.08067 |
| ChatQA unanswerable ablation | 2024 | Llama-2/3 | 1.5k unanswerable samples | Optimum at ~1.5k; more over-refuses | — | https://arxiv.org/html/2401.10225v5 |

## 4. On-device / offline QA with small readers
| System | Year | Sizes | Method | Key number | Transfer? | URL |
|---|---|---|---|---|---|---|
| Apple Foundation Models (2024) | 2024 | ~3B on-device | 3.7 bpw (2/4-bit mix) + rank-16 "accuracy-recovery" LoRA trained **on the quantized base** + task adapters | Beats Phi-3-mini, Gemma-7B, Llama-3-8B in human evaluation (task numbers not extracted) | Product tasks | https://machinelearning.apple.com/research/introducing-apple-foundation-models |
| Apple Foundation Models (2025) | 2025 | on-device + server | 2-bit QAT, adapter fine-tuning framework | Matches same-size open baselines | — | https://arxiv.org/abs/2507.13575 |
| WikiChat | 2023 | GPT-4 → distilled LLaMA-7B | Retrieve, generate, fact-check, distil | 97.9% factual accuracy (GPT-4 pipeline); 7B distillation "minimal loss" | Wikipedia | https://arxiv.org/abs/2305.14292 |
| Pocket RAG | 2026 | unspecified SLM, Android | Hybrid RAG, compression | First aid 94.5% / 97.0%; latency 14.2 s → 3.7 s | Single domain | https://arxiv.org/abs/2602.13229 |
| Can SLMs use what they retrieve? | 2026 | 360M–8B (SmolLM2, Qwen2.5, Llama-3.1) | Oracle passages, split by known/unknown questions | ≤7B fail on 85–100% of unknown questions **even with oracle passages**; context destroys 42–100% of known answers; main failure: ignoring the context | — | https://arxiv.org/abs/2603.11513 |
| KV-cache quantization vs faithfulness | 2026 | Qwen2.5-7B | INT8/INT4 KV cache | INT4: >90% of faithfulness changes are negative, even when the answer stays correct; INT8 ≈ lossless | — | https://arxiv.org/abs/2608.30996 |
| a competitor team / a competitor team | — | — | — | **not found** | — | — |

## 5. MoE vs dense at equal active parameters: reading or knowledge?
| Paper | Year | Sizes | Method | Key number | Transfer? | URL |
|---|---|---|---|---|---|---|
| Mixture of Parrots | 2024 | synthetic + small LMs | Scale experts at fixed active params | More experts → memorization keeps improving, reasoning saturates. MoE helps knowledge, not reasoning | — | https://arxiv.org/abs/2410.19034 |
| Vectara HHEM leaderboard (updated 2026-09-22) | 2026 | Qwen3 4B/8B/14B/32B/235B-A22B | Grounded summarization hallucination rate | 4B 5.7%, 8B 4.8%, 32B 5.9%, 235B-A22B (MoE) 9.3%: size/MoE ≠ faithfulness | — | https://github.com/vectara/hallucination-leaderboard |
| FaithEval | 2025 | many | Unanswerable / inconsistent / counterfactual contexts | "Larger models do not necessarily exhibit improved faithfulness" | — | https://arxiv.org/abs/2410.03727 |
| Controlled MoE-vs-dense test on reading comprehension / grounded QA with real models | — | — | — | **not found**. Our 35B-A3B vs 4B result (+0.03) is consistent with the above | — | — |

## 6. Risks
| Risk | Year | Sizes | Evidence | Key number | URL |
|---|---|---|---|---|---|
| Judge style/length gaming | 2024 | GPT-4 | AlpacaEval verbosity experiment | Win rate swings 22.9% → 64.3% from verbosity prompt alone; length control cuts the swing to 9.7 pts | https://arxiv.org/html/2404.04475 |
| Judge verbosity bias differs by judge family | 2025 | various | Bias audit | Claude judges slightly prefer shorter answers (−0.12); others prefer longer (+0.24 to +0.44) | https://arxiv.org/abs/2510.12462 |
| Q4 after fine-tune | 2025 | Llama-3.2-1B QLoRA | Merge → quantize | FP16 0.99, GPTQ-4bit 0.99, Q5_K_M 0.99, **Q4_K_M 0.89**, Q3_K_M 0.60 | https://arxiv.org/html/2510.21970v1 |
| Small deltas rounded away | 2025 | 7B-class | Quantize unlearned models | Forgotten knowledge 21% → 83% after 4-bit; small-LR fine-tunes collapse back to base | https://arxiv.org/abs/2410.16454 |
| Quantization-aware LoRA | 2024 | LLaMA 7B–65B | QA-LoRA | +2.0 avg vs QLoRA + post-training quantization at 4-bit; larger gap at smaller sizes | https://arxiv.org/abs/2309.14717 |
| Runtime LoRA in llama.cpp | 2024 | any | `convert_lora_to_gguf.py`, `--lora` on a quantized base (adapter kept at f16) | Avoids quantizing the delta; latency cost on phone **UNKNOWN** | https://github.com/ggml-org/llama.cpp/discussions/10123 |
| Safety drift from benign FT | 2024 | Llama-2-7B-chat, GPT-3.5 | Alpaca/Dolly fine-tune | Harmfulness 0.3% → 16.1% (Llama-2-7B Alpaca); 5.5% → 31.8% (GPT-3.5) | https://arxiv.org/html/2310.03693 |
| LoRA forgets less | 2024 | Llama-2-7B | LoRA vs full fine-tuning | LoRA learns less on the target task and keeps more out-of-domain ability | https://arxiv.org/abs/2405.09673 |
| Over-trusting wrong/partial context | 2024 | GPT-4o and others | ClashEval, 1.2k perturbed questions | Wrong context overrides correct prior knowledge >60% of the time | https://arxiv.org/abs/2404.10198 |

## Recipe the literature supports (adapted to a 2-day go/no-go: 1k examples, LoRA on Qwen3-4B, validate on a held-out pack)
**Decisions (supported by the papers above)**
- **Size:** ~1,000 SFT examples (RetRobust, ChatQA's 1.5k unanswerable optimum). Treat this as a behaviour test, not a capability ceiling.
- **Mix:**
  - ~45% gold passage + 3–4 distractors, with the gold passage present in ~80% of these (RAFT P sweep).
  - ~20% number/table/unit-heavy passages (ChatQA TAT-QA effect).
  - ~15% *partial-context* items: the passage covers only part of the answer, and the target says what the passage covers and uses memory only when it is consistent (targets ClashEval-style override and SLM "knowledge destruction").
  - ~10% unanswerable → short abstention (ChatQA, Trust-Align).
  - ~10% multi-passage synthesis needing complete enumeration (completeness target).
  - **Skip heavy counterfactual training** (CANOE/Context-DPO). It teaches "context always wins", which worsens our fragment-override failure.
- **Targets:** frontier-teacher answers written **only from the passages**, then filtered by claim-level rejection sampling (FLAME/Apple-style).
  - Drop any target that adds facts not in the passages (Gekhman).
  - Hard filter: every number in a target appears verbatim in the passages or is an explicit, shown derivation.
  - Set target length by completeness (cover every relevant passage claim), not by a word count, so length is not the learned signal.
- **Format:** short "quote-then-answer" (RAFT CoT gave +9.7 on HotpotQA; InstructRAG rationales) or Qwen3 thinking off with inline evidence quotes. Pick by phone latency budget (**UNKNOWN**: decode cost of the quotes).
- **Loss:** response-only SFT. LoRA on all linear layers, rank 16–32, 2–3 epochs. Generic defaults: no ablation found for Qwen3-4B.
  - Day-2 option: DPO on ~1k pairs where *chosen* = filtered teacher answer and *rejected* = the base 4B's own failures (misread number, fragment override, omission). Trust-Align: DPO > SFT in 26/27 configs.
- **Packs:** training passages come from packs other than the held-out pack (different corpus and format). Never generate data from blind/held-out sets (BOAR rule).

**Validation design (freeze the criterion with sha256 before the run)**
- **Arms**, all on the **deployed artifact** (Q4_K_M GGUF on llama.cpp):
  - A = base + current prompt.
  - B = base + "be complete, ~N words" prompt. This is the **length control**: is the gain just verbosity?
  - C = LoRA merged then quantized to Q4_K_M.
  - D = Q4 base + f16 runtime `--lora`.
- **Metrics:**
  - Judge completeness and faithfulness.
  - Claim-level recall and precision against perfect passages (RAGChecker-style, less length-gameable).
  - Numeric exact-copy rate (regex vs passages).
  - Abstention precision.
  - Words per answer.
  - Plus a safety-refusal regression set and a no-context general-QA regression set.
- **Go (proposal):** on the held-out pack at Q4, all of:
  - completeness ≥ +0.3 over the better of A/B, CI excluding 0;
  - faithfulness non-inferior (≥ −0.1);
  - numeric error rate not higher;
  - safety refusals not lower;
  - gain survives in C or D.
  - Otherwise no-go. 
- **Judge-overfit check:** re-score a 50-item sample with a second judge family, and compare length-matched pairs.

## UNKNOWN
- No paper measures LoRA SFT on **Qwen3-4B** specifically for long-form *completeness* with perfect passages. Effect-size transfer from Llama-3-8B/Qwen2.5 is an extrapolation.
- How the literature's 0–100 metrics map to our 1–5 judge scale. The 2.9–3.3 estimate is my inference, not a measured number.
- Whether 1k examples move completeness at all. Gains above are from 4k–167k examples, or RL/DPO on 10k–19k.
- Whether Q4_K_M erases a 1k-example LoRA delta on a 4B model. Evidence is indirect: one 1B case (0.99 → 0.89) and the unlearning mechanism.
- Phone latency and RAM cost of runtime f16 LoRA in llama.rn on Android.
- No targeted fine-tuning study on number copying in RAG. The closest evidence (financial FT) is negative.
- Not found: a competitor team, a competitor team, an official Qwen/Llama RAG-SFT recipe, Cohere grounding ablations, a controlled MoE-vs-dense grounded-reading benchmark.
- Several numbers above (Pleias, R-Tuning, NUMCoT, the context-awareness paper) were only read at abstract level. Verify before citing externally.
