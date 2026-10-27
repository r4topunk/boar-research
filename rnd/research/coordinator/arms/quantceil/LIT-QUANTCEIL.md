# QUANTCEIL — published research that bears on the arm (web sweep 2026-10-12, coordinator; read-only, 0 judge calls)

TL;DR: the literature supports QUANTCEIL's mechanism (2-bit → recalled-but-wrong facts) and its direction, but predicts the gain is bounded and seed-noisy at our MDE. Three usable inputs: (1) Unsloth's own KLD table on the sibling MoE puts IQ3_XXS at roughly half the mean KLD of Q2_K_XL and half the 99.9 % tail; (2) 3-bit sits in the "signal degradation" regime (same computation, less precision), not the 2-bit "collapse" regime, so the model's knowledge is still there to recover; (3) mid-popularity facts degrade most under 3–4-bit quantization, which matches the *wrong* bucket on V-para (comparison + crypto items). Nothing published measures GGUF 2- vs 3-bit on a MoE end-to-end with a judge; QUANTCEIL is a first measurement, not a replication.

## 1. Direct numbers for our quant pair (sibling model)
Unsloth "Qwen3.5 GGUF Benchmarks" page (table unlabelled, almost certainly 35B-A3B; Wiki-test, 512 ctx; Qwen3.5, not 3.6 — treat as a prior):

| quant | GB | PPL | KLD 99.9 % | mean KLD |
|---|---|---|---|---|
| IQ2_XXS | 9.09 | 7.716 | 4.222 | 0.185 |
| **Q2_K_XL (our H)** | 12.04 | 7.044 | 2.909 | **0.097** |
| **IQ3_XXS (our Q)** | 13.12 | 6.783 | 1.530 | **0.050** |
| IQ3_S | 14.13 | 6.772 | 1.419 | 0.046 |
| Q3_K_XL | 16.06 | 6.725 | 0.954 | 0.031 |
| Q4_K_XL | 19.17 | 6.592 | 0.410 | 0.014 |
| Q8_K_XL | 36.04 | 6.535 | 0.103 | 0.003 |

Reading: +0.9 GB buys the single largest KLD step in the ladder (mean 0.097 → 0.050, tail 2.9 → 1.5). IQ3_S (+0.5 GB more) adds little; the next real step is Q3_K_XL at 16 GB, outside both the mini and a 12 GB phone. So IQ3_XXS was the right pick, and there is no cheaper intermediate worth a second arm. Qwen3.6-35B-A3B GGUF sizes on HF match (12.3 / 13.2 GB); the 3.6 page has the KLD chart as an image only, Unsloth claims "top in 21 of 22 sizes".

## 2. Mechanism: what low-bit quantization does to factual recall
- **Two failure modes** (arXiv 2604.19884, Llama-3.1-8B + Qwen3-8B/Mistral/Gemma, GPTQ/AWQ, PARAREL): 4-bit = *signal degradation* (computation intact, answer logit weakened by accumulated error); 2-bit = *computation collapse* (early layers destroy the signal; recall → 0 %, model emits stop words). AWQ failure subset: 4-bit 28 % → 3-bit 18 % → 2-bit 0 %. 3-bit behaves like 4-bit mechanistically (attention/FFN near baseline). Training-free repair recovers 64–81 % of the failure subset at 4-bit and nothing at 2-bit. → Our Q2_K_XL is a *dynamic* 2.6 bpw quant with important tensors kept higher, so it is not the collapsed uniform-2-bit model of these papers, but it sits on the cliff edge; IQ3_XXS moves the deep tier squarely into the recoverable regime. This is the strongest published argument for the arm's sign.
- **Which facts break** (EMNLP 2025, arXiv 2506.12044, 3–4-bit, Qwen2.5-7B/Llama3-8B/Mistral-12B/Llama3-70B): methods fail on the *same* inputs (error ρ 0.82 across method pairs); PopQA degradation is largest for **mid-popularity entities** (log10 pop 2.8–4.8: > 10 pts), least for the very rare and the very famous; long-tail examples have small errors, head examples can have large ones. Cause = accumulated activation error amplified in upper-layer MLPs after RMSNorm, not last-layer weights (restoring the last 18 % of layers to fp16 recovers little). → Matches LOSSMAP: *wrong* is concentrated in comparison (4/7) and crypto (3/5, all with an on-topic source) items — mid-popularity named facts (numbers, protocol names, dates), exactly the bucket the papers say quantization flips.
- **Task-stratified PTQ scaling law** (arXiv 2508.18609, Qwen3 0.6–32B, GPTQ 2/3/4/8-bit): −ln(Acc_adj) = A·N^α·(log₂B)^β·(log₂Cb)^γ·G^δ. Memorization bit-exponent β −0.96 vs reasoning −1.36 (reasoning is more bit-sensitive); at 2-bit, memorization is *recoverable* for N ≥ 4B with tuned group size/calibration while reasoning collapses (R² 0.22). Memorization is the only stratum whose calibration-set exponent excludes zero ("calibration-sensitive"). Dense only; MoE listed as future work. → Expect the 3-bit step to move correctness (facts) more than reasoning items; and the *imatrix calibration* Unsloth uses (chat + tool-calling text, not Wikipedia) is a plausible reason the 2-bit quant loses encyclopaedic facts specifically.
- **Undertrained models quantize better** (arXiv 2411.17691, 1 500+ checkpoints): quantization-induced degradation grows with training tokens per parameter; the authors warn low-bit quants of models trained past ~100 T tokens "may not be desirable". → Qwen3.6 is heavily over-trained for its active size (3B active), so it is in the regime where 2-bit hurts most; another reason to expect a non-zero QUANTCEIL effect, and a reason NEWMODEL (B5) should not assume a 2-bit quant of a *newer* model is free.
- **Flips** (Microsoft, NeurIPS 2024, arXiv 2407.09141): quantized models with unchanged accuracy still flip up to 13.6 % of answers right↔wrong; flips correlate with KLD (Spearman 0.98 on MMLU) and predict worse free-form generation (MT-Bench). → Our h2h pattern (slice 10/4/6 under Opus: many wins *and* losses, small net) is exactly the flip signature; the KLD halving in §1 predicts fewer flips, i.e. a positive but modest net. Seed variance will be large (SEEDVAR already set the rule: 1-seed V-para Δ < 0.03 is noise).

## 3. MoE-specific
- Experts tolerate low bits better than dense weights (MoQE 2023: 3-bit experts without calibration; 2-bit needs QAT). Uniform 3-bit expert quantization "almost maintains generalization", uniform 2-bit "significantly degrades" on Mixtral (arXiv 2604.06515, Apr 2026). On Qwen3-30B-A3B at 2-bit, bit-allocation methods (BitsMoE, arXiv 2606.00079) recover tens of points over GPTQ — i.e. at 2 bits *where* the bits go matters more than the average. → Unsloth UD quants are already an expert-aware allocation; the remaining 2-bit loss is what IQ3_XXS buys back. No published GGUF 2- vs 3-bit MoE downstream study exists: QUANTCEIL fills a gap, worth one line in the claim text if it lands.
- Device: BigMoeOnEdge (the "bmoe" engine; README has no version) reports Qwen3.6-35B-A3B **Q4_K_M (22.3 GB)** on a 12 GB phone at 5.0–5.8 tok/s decode via expert paging from flash, NPU prefill 7.8–9.5× over CPU; no thinking-budget flag (`--no-think` only; confirms deep/RESUME.md D6). → If paging a 22 GB quant on a 12 GB phone is their headline, a 13.2 GB IQ3_XXS is inside their operating envelope; the IQ3 CPU-kernel cost we measured on the mini (decode ×0.7) would compound with paging. The device plan can carry IQ3_XXS as the quality option and Q2_K_XL as the speed option; neither has been measured on a phone by us.

## 4. What this changes for the arm (no criterion change; frozen sha 0c4a8896…)
- Prior stays +0.02…+0.05 raw on V-para; literature puts a soft ceiling on it: 3-bit is still "degraded", and the Q3_K_XL/Q4 steps that remove most of the remaining KLD do not fit 12–16 GB. Do not plan a QUANTCEIL-2 with a bigger quant on current hardware.
- Expect the gain in **correctness** on *wrong*-bucket items (comparison, crypto, named numbers), near zero on *absent knowledge* and *hedged*. Worth one extra 0-call read-out when the 110 land: Δ by LOSSMAP bucket (wrong vs absent vs hedged) — if the gain is not in *wrong*, the mechanism story is false regardless of the net.
- If stage 4 says LEVER or SMALL-positive: the claim sentence should name the quant ("3-bit dynamic GGUF, 13.2 GB; exceeds a 12 GB phone's RAM without expert paging").
- If NO: the published prior says the deep tier's remaining *wrong* answers are not a precision artefact → the knowledge is absent at this active-parameter size, which closes the "model knowledge" row of LOSSMAP §46 for the deep tier as well, and raises the weight of SYNTHDEEP (B7, prompt-side) over any further model/quant arm.

## Sources
- Unsloth Qwen3.5 GGUF benchmarks (KLD table): https://unsloth.ai/docs/models/qwen3.5/gguf-benchmarks · Dynamic 2.0 method: https://unsloth.ai/docs/basics/unsloth-dynamic-2.0-ggufs · Qwen3.6 run guide: https://unsloth.ai/docs/models/qwen3.6 · HF sizes: https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF
- Two failure modes of LLM quantization: https://arxiv.org/abs/2604.19884
- Why do some inputs break low-bit quantization (EMNLP 2025): https://arxiv.org/abs/2506.12044
- Task-stratified knowledge scaling laws for PTQ: https://arxiv.org/abs/2508.18609
- Low-bit quantization favors undertrained LLMs: https://arxiv.org/abs/2411.17691
- Accuracy is not all you need (flips, NeurIPS 2024): https://arxiv.org/abs/2407.09141
- Through a compressed lens (factual recall under quantization): https://arxiv.org/abs/2505.13963
- Which quantization should I use? llama.cpp quants on Llama-3.1-8B (3–8 bit, no 2-bit, dense): https://arxiv.org/abs/2601.14277
- MoE quantization: MoQE https://arxiv.org/abs/2310.02410 · generalization guarantees https://arxiv.org/abs/2604.06515 · BitsMoE https://arxiv.org/abs/2606.00079 · EAC-MoE https://arxiv.org/abs/2508.01625
- BigMoeOnEdge (bmoe) README: https://github.com/Helldez/BigMoeOnEdge

UNKNOWN: whether the Unsloth KLD table is 35B-A3B (unlabelled; sizes match); Qwen3.6-specific KLD numbers (chart image only); no paper measures a UD/imatrix 2-bit vs 3-bit GGUF MoE on open QA with a judge.
