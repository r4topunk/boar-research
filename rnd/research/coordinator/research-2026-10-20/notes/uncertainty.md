# Uncertainty estimation and selective answering for small LMs (<= 3B)

Angle: can a <= 3B model tell when its short factual answer is wrong, cheaply enough for a phone (Qwen3-1.7B Q4_K_M, 12-16 tok/s decode, 8 GB device)?
Date of search: 2026-10-20. Method: WebSearch (standard mode, 6 queries) and WebFetch of abstracts, HTML and GitHub pages. Where only an abstract or snippet was read, this is stated per finding.

## TL;DR for BOAR

- Nothing found reports AUROC for any uncertainty method at 1.7B. The closest numbers are at 3-4B (Llama-3.2-3B, Qwen3-4B, Gemma-3-4B, Phi-3-mini 3.8B) and 7-8B.
- Plain answer-token NLL is weak at 3B: AUROC 0.63-0.69 on TriviaQA/BioASQ/MedicalQA (2603.21172). Sampling-based semantic entropy (SE, 10 samples) is much better at 3B (0.884 on TriviaQA for Llama-3.2-3B) but costs about 10x decode. That is not feasible on the phone.
- A linear probe on the model's own hidden states is the only cheap single-pass option with strong published numbers. The numbers are 7-8B (0.90-1.00 AUROC, 2606.02628). The main caveat: probes trained on true/false statements fail on the model's own generated statements (SAPLMA reproduction, 2505.16520: near chance, 0.56-0.59). So a BOAR probe would need labels from BOAR's own answers.
- Single-decode first-token entropy (phi_first, 2605.05166) reports mean AUROC 0.820 over three 7-8B models. It is the cheapest candidate, and it is untested at 1.7B.
- Verbalized confidence tracks commitment (whether the model answers), not correctness (2606.29490). Do not use a verbal confidence number as the abstain threshold without measuring it.
- Certified selective answering is hard at small size: 2608.05064 finds that at 0.5B-14B, certified autonomy at a 20 % risk budget applies to 3 of 11 model-task pairs and to none at 10 %.

## Findings

### F1. Entropy-only signals are weak at 3B; sampling-based SE is strong (2603.21172)
- Title: "Entropy Alone is Insufficient for Safe Selective Prediction in LLMs" (Phillips et al., cs.CL, submitted 2026-03-22). Source opened: https://arxiv.org/abs/2603.21172 and HTML https://arxiv.org/html/2603.21172v1
- Models (HTML): Ministral-8B-Instruct-2410 (8B), Llama-3.2-3B-Instruct (3B), Qwen3-4B-Instruct-2507 (4B), Gemma-3-4B (4B).
- Datasets: TriviaQA, BioASQ, MedicalQA.
- AUROC table (mean, bootstrap), entropy-only rows:
  - Llama 3.2 3B: NLL 0.664 / 0.656 / 0.690; SE 0.884 / 0.737 / 0.688; SE Probe 0.723 / 0.697 / 0.626 (TriviaQA / BioASQ / MedicalQA).
  - Qwen3 4B: NLL 0.632 / 0.663 / 0.613; SE 0.844 / 0.717 / 0.648; SE Probe 0.779 / 0.622 / 0.643.
  - Gemma 3 4B: NLL 0.504 / 0.647 / 0.635; SE 0.752 / 0.777 / 0.701.
  - Ministral 8B: NLL 0.783 / 0.681 / 0.551; SE 0.823 / 0.811 / 0.772.
- Quote from abstract: "identify a model-dependent failure mode of entropy-based uncertainty methods that leads to unreliable abstention behaviour."
- Compute: SE needs multiple samples (10 per question in the authors' setup, as in the SE literature). NLL is a single pass.
- Licence: arXiv non-exclusive (paper). No code link found.
- Reading: at 3-4B, one-pass NLL gives AUROC 0.63-0.69. The gap to SE (+0.22 on TriviaQA for Llama-3.2-3B) is the gap that matters for BOAR, and it is only reachable by sampling.

### F2. A correctness probe combined with entropy helps single-pass detection at 3B (2603.21172)
- Same paper. Probe = logistic regression on last-token prompt representations before generation (C = 0.1, StandardScaler). Combined score = two-feature logistic regression over entropy risk and probe risk.
- Llama 3.2 3B, TriviaQA: PC + NLL 0.826 vs NLL 0.664 (+0.16). BioASQ: 0.674 vs 0.656 (+0.02). MedicalQA: 0.649 vs 0.690 (-0.04, worse).
- Qwen3 4B, TriviaQA: PC + NLL 0.888 vs NLL 0.632 (+0.26).
- The combination does not beat plain SE on every model (SE wins Llama/TriviaQA at 0.884 vs PC+SE 0.863).
- The probe needs labelled correct/incorrect answers from the target distribution. The paper does not report probe training cost or label size in the abstract or HTML I read.
- Reading: the PC probe is a single forward pass plus a tiny classifier, so it fits the phone budget. It needs a labelled set of BOAR's own answers.

### F3. Probes trained on true/false statements do not transfer to model-generated statements (SAPLMA reproduction, 2505.16520)
- Title: "Are the Hidden States Hiding Something? Testing the Limits of Factuality-Encoding Capabilities in LLMs" (Servedio et al., v3 2025-05-30, CC BY 4.0). Source opened: https://arxiv.org/html/2505.16520v3 (first 100k chars of 102k). Code: https://github.com/sisinflab/HidingInTheHiddenStates
- Models: Llama 2-7B and OPT-6.7B (32 layers each).
- Cross-topic accuracy on the True-False dataset (leave-one-topic-out): Llama 2-7B, layer 16 = 0.8281, layer 20 = 0.8012, last layer = 0.7326. OPT-6.7B = 0.6437 (last), 0.6620 (28th), 0.6927 (24th), 0.7110 (20th), 0.6580 (16th).
- On TriviaQA-generated facts (model-generated statements): Llama 2-7B 0.562-0.594, OPT 0.555-0.583 (average accuracy at threshold 0.5). Authors: probes "do not generalize to LLM-generated statements."
- Perplexity-based negative sampling: Llama 2-7B layer 16, 0.7694 (refined) vs 0.7447 (original). "mostly comparable."
- Quote: "the findings from previous studies are partially validated" (abstract).
- Reading: the SAPLMA-style probe is a strong result on curated true/false statements and fails on the distribution that matters for BOAR (the model's own short answers). Any BOAR probe must be trained on labels from BOAR's own generations.
- Original SAPLMA (Azaria and Mitchell, 2023, arXiv 2304.13734): reported accuracy 70.98 % (OPT-6.7B) and 82.98 % (Llama 2-7B) on cross-topic validation. Snippet read only, not opened.

### F4. Mid-layer linear probes reach 0.90-1.00 AUROC at 7-8B, quantized (2606.02628)
- Title: "Hallucination Is Linearly Decodable from Mid-Layer Hidden States in Quantized LLMs" (Aiersilan, submitted 2026-05-30). Source opened: https://arxiv.org/abs/2606.02628
- Models: Llama-3.1-8B, Mistral-7B, Qwen2.5-7B, all 4-bit NF4. Datasets: TruthfulQA, HaluEval-QA, FEVER, a controlled synthetic set.
- Quotes: "A linear probe on a single mid-network layer achieves 0.904--1.000 AUROC on held-out splits." Peak layers: blocks 13-18 of 32 (Llama, Mistral) and 19-25 of 28 (Qwen).
- Baselines: sampling-based detectors (INSIDE EigenScore, self-consistency) "do not exceed 0.541 AUROC under the same protocol." First-block attention entropy 0.866-0.941 on HaluEval-QA.
- MLP probes "rarely surpass linear probes by more than 0.01 AUROC."
- Code: abstract says code and data are released and run on a single 8 GB GPU. No repo link found on the abstract page.
- Caveats: single preprint, not peer reviewed; 7-8B, not <= 3B; probe trained per dataset with labels; the sampling baseline here (0.541) contradicts F1's SE numbers at 3B, which suggests the protocol (labels, datasets) drives the result. Treat as a direction, not a number for BOAR.

### F5. Single-decode first-token entropy (phi_first) is the cheapest published signal with a high AUROC (2605.05166)
- Title: "The First Token Knows: Single-Decode Confidence for Hallucination Detection" (Gabriel, submitted 2026-05-06). Source opened: https://arxiv.org/abs/2605.05166
- Method: phi_first = normalized entropy of the top-K logits at the first answer token, from one greedy decode.
- Models: three 7-8B instruction models (unnamed on abstract page); two closed-book short-answer factual QA benchmarks.
- Mean AUROC across models and benchmarks: phi_first 0.820; semantic agreement (NLI clustering of samples) 0.793; surface-form self-consistency 0.791. Combining with semantic agreement adds little.
- Compute: one greedy decode, no extra samples and no NLI model (the paper's qualitative claim).
- Code: none found on the page. Licence: arXiv non-exclusive (paper).
- Reading: this matches BOAR's constraints (one pass, no extra model) and is the first entropy-type signal that beats sampling-based baselines in this paper. Untested at 1.7B. Top-K logits are available from llama.cpp (see F11).

### F6. Verbal confidence tracks commitment, not correctness (2606.29490)
- Title: "Reported Confidence in LLMs Tracks Commitment More Than Correctness" (Kumaran, submitted 2026-06-28). Source opened: https://arxiv.org/abs/2606.29490
- Models: four non-reasoning and four reasoning models, plus Gemma 3 and 4 for mechanistic analysis. Sizes not stated on the abstract page.
- Quotes: verbal confidence "predicted the commit/abstain decision substantially better than whether the answer was correct." Log-probabilities showed "the opposite profile, with abstention-prediction coupled to correctness discrimination." After removing variance shared with log-probs, the residual link to correctness "fell to near chance."
- No AUROC or correlation numbers in the abstract.
- Reading: a verbalized "how sure are you" number from the 1.7B is likely a measure of whether it will answer, not whether it is right. Any abstain rule must be validated against a correctness label before use.

### F7. Verbalized confidence at 0.5-14B: calibration works but certified selective answering is out of reach (2608.05064)
- Title: "Provable Limits and Certified Deferral for Verbalized Uncertainty in Small Language Models" (Shen, v1 submitted 2026-08-05). Source opened: https://arxiv.org/abs/2608.05064
- Models: eleven instruction-tuned models from three families, 0.5B to 14B (names not on the abstract page).
- Tasks: ARC-Challenge and TruthfulQA, 25,168 local predictions.
- Quotes: Platt scaling reduces ECE "to as low as 0.02." Certified autonomy at a 20 % risk budget is granted to "three model-task pairs" and "none" at 10 %. Temperature scaling "cannot calibrate models whose confidence stays above one half while accuracy falls below it."
- Method: Platt scaling plus a Clopper-Pearson finite-sample risk bound from a 200-question calibration set, under an i.i.d. deployment assumption.
- Compute cost per answer: not reported.
- Reading: low-ECE calibration is achievable at small size, but a guaranteed low-risk answer policy is not. BOAR should frame the goal as a measured risk-coverage trade-off, not a guarantee.

### F8. Semantic Energy beats semantic entropy by 4-5 AUROC points, still needs 10 samples (2508.14496)
- Title: "Semantic Energy: Detecting LLM Hallucination Beyond Entropy" (v3). Source opened: https://arxiv.org/html/2508.14496v3 and abstract https://arxiv.org/abs/2508.14496
- Models: Qwen3-8B and ERNIE-21B-A3B (MoE). Not a small model.
- AUROC SE vs Semantic Energy (CSQA / TriviaQA): Qwen3-8B 71.6 vs 76.1; 69.6 vs 74.8. ERNIE-21B-A3B 77.4 vs 80.2; 75.1 vs 81.0.
- Samples: 10 per question (seeds 1-10). Uses penultimate-layer logits.
- Code: https://github.com/MaHuanAAA/SemanticEnergy/tree/main. Paper licence CC BY 4.0.
- Reading: a gain on top of sampling, not a single-pass method. Not usable on the phone as is.

### F9. Semantic Entropy Probes: predict SE from hidden states, cost near zero at inference (2406.15927)
- Title: "Semantic Entropy Probes: Robust and Cheap Hallucination Detection in LLMs" (Kossen et al.). Source opened: https://arxiv.org/html/2406.15927v1
- Models: Llama-2-7B, Llama-2-70B, Mistral-7B, Phi-3-3.8B (smallest tested is 3.8B), Llama-3-70B.
- SE baseline: N = 10 samples at T = 1.
- Quote: SEP AUROC "reaching values between 0.7 and 0.95 depending on the scenario." Table 2 (generalization, SEP minus accuracy probe, x100): Phi-3-3.8B +9.9 +/- 2.9; Mistral-7B +10.5 +/- 3.5; Llama-2-7B +7.7 +/- 1.3.
- Layers: late layers (Llama-2-7B and Mistral-7B 28-32 of 32; Phi-3-3.8B 21-25 of 32).
- Abstract: SEP computation overhead is "almost zero" vs the "5-to-10-fold increase in computation cost" of SE.
- Licence: arXiv (paper). No code link on the page read.
- Reading: the SE-distillation-to-probe idea is the right shape for BOAR (one forward pass), but the tested models are all >= 3.8B. Not evidence for 1.7B.

### F10. Semantic self-distillation: a student predicts semantic dispersion before generation (2602.04577)
- Title: "Semantic Self-Distillation for Language Model Uncertainty" (Phillips et al., UAI 2026). Source opened: https://arxiv.org/abs/2602.04577
- Abstract: a student predicts the teacher's semantic distribution "before the language model generates an answer token"; the teacher's sampled semantic dispersion has a cost that "prohibits its use in latency-critical applications." Datasets: TriviaQA and MMLU.
- Models and AUROC numbers: not extracted (the page read gives no table; the student was described as "lightweight").
- Licence: CC BY 4.0 (paper). No code link found.
- Reading: pre-generation prediction is attractive for abstention (decide before paying decode time), but the numbers were not verified. Needs the full HTML before any decision.

### F11. llama.cpp exposes top-K token probabilities but not per-layer hidden states on the server
- Source opened: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- /completion: option `n_probs` ("the probabilities of top N tokens for each generated token"), results in `completion_probabilities` with `probs` and `top_logprobs`. `post_sampling_probs` also documented.
- /v1/chat/completions: the visible part of the README does not name logprobs or top_logprobs; the section was truncated.
- Embeddings: `--embeddings` and `--pooling none` return per-token embeddings for embedding-capable models, not per-layer hidden states.
- Not verified: whether the C API eval callback (`cb_eval`) can return a chosen layer's hidden state on Android/ARM for Qwen3. A probe would need a small patch or a callback; this is an engineering check, not a documented feature.
- Licence of llama.cpp (MIT, from memory): not shown on the page read; not verified here.

### F12. Verbal vs semantic uncertainty mismatch as a hallucination predictor (Ji et al., EMNLP 2025)
- Title: "Calibrating Verbal Uncertainty as a Linear Feature to Reduce Hallucinations" (Ji, Yu, Koishekenov, Bang, Hartshorn, Schelten, Zhang, Fung, Cancedda). Source opened: https://aclanthology.org/2025.emnlp-main.187
- Quotes: "the mismatch between semantic and verbal uncertainty is a better predictor of hallucinations than semantic uncertainty alone." Intervention on verbal uncertainty "achieving an average relative reduction of ~30%" in confident hallucinations on short-form answers.
- Models, sizes, AUROC, and code: not found on the page read. The PDF was not opened.
- Reading: this is a steering/intervention line (a linear verbal-uncertainty feature), and it needs model-internal access. Relevant only if BOAR can afford activation steering; not a cheap abstention signal by itself. Note this is the only 2025 paper found on the verbal side with a 2025 venue; the P(True) line was not.

### F13. Conformal abstention with finite-sample guarantees for LLMs (2026, snippets only)
- 2604.27914, "Geometry-Calibrated Conformal Abstention for Language Models" (Xu et al., April 2026): post-hoc, finite-sample guarantees on answer rate and correctness; calibration uses representation geometry; the authors report 75 % conditional correctness on selective answers. Source: https://www.alphaxiv.org/abs/2604.27914 (abstract snippet only; the paper was not opened; model sizes and compute not read).
- 2502.06884 (Feb 2025), learnable conformal abstention with RL-tuned thresholds (LLMs and VLMs). Snippet only: https://www.arxiv.org/abs/2502.06884
- 2502.19110 (Feb 2025), "Conformal Linguistic Calibration" (Jiang, Liu, Van Durme): hedging as answer-set prediction. Snippet only: https://arxiv.org/pdf/2502.19110v4
- Reading: conformal methods give the only guarantee-style answer policy found, but none of these were opened and no small-model result was seen. Consistent with F7, expect the guarantee to cost coverage at small size.

### F14. Early hallucination detection in small LMs via confidence trajectories (TrajECT, NeurIPS 2026 AI4GOOD)
- Title: "Early Hallucination Detection in Small Language Models via Confidence Trajectories" (Mikhael, Borisov). Source opened: https://neurips.cc/virtual/2026/165336
- Method: tracks entropy, max probability and entropy change token by token, scored by a small recurrent model; can flag hallucinations before the response ends.
- Quote: "competitive with feature-rich white-box hallucination detectors" (no values on the page). Abstract says code and evaluation pipeline are released; no repository URL on the page (OpenReview forum: https://openreview.net/forum?id=U3B2Pc5oFT).
- Model sizes, AUROC values and baselines: not on the page read. Title says "small models"; the size range was not confirmed.
- Reading: the most on-topic title for BOAR (single pass, small models, early exit). Numbers unverified; worth fetching the OpenReview PDF before deciding.

### F15. HalluScan (snippet only): Qwen2.5-1.5B and 3B on scientific prompts
- 2605.02443 (HalluScan benchmark): Qwen 2.5-1.5B mean AUROC 0.582, best 0.915 with a self-consistency method on scientific prompts; Qwen 2.5-3B also evaluated. Authors conclude that detection method matters more than model choice. Source: https://arxiv.org/pdf/2605.02443 (snippet only, not opened).
- Reading: the only 1.5B number found. Mean 0.58 is near chance for a naive method; the spread between methods is the signal. Not verified.

## What was searched and not found

- AUROC at 1B-1.7B for any uncertainty method (semantic entropy, NLL, probes, verbal). Not found. The only sub-4B results were 1.5B and 3B in snippets (F15) and 3B in F1 (2603.21172).
- P(True) on small models: the search returned no paper on P(True) directly. Kadavath et al. 2022 (2207.05221) abstract opened; it says P(True) is well-calibrated for "larger models" only, with no small-model results. No 2024-2026 small-model P(True) paper found.
- Hidden-state probes at 1-3B with cross-topic evaluation on the model's own generations: not found. F3 is the closest (7B, true/false vs generated).
- llama.cpp hidden-state extraction for probes: not documented on the server; cb_eval route not checked.
- Compute cost in joules or ms per answer on a phone for any of these methods: not found.
- Licences: most papers are arXiv or CC BY 4.0 (the paper); no software licence found for SEP, SAPLMA, Semantic Energy, phi_first or TrajECT code. Code links were found only for SAPLMA reproduction (2505.16520) and Semantic Energy (2508.14496).

## What this means for BOAR

Inputs: Qwen3-1.7B Q4_K_M, 12-16 tok/s decode on the Pixel 8a, answers 2-5 sentences, 28 % confident errors (measured). Constraints: offline, RAM about 8 GB total, no paid APIs, licence must permit redistribution.

Options (ordered by cost, not by value):

1. Single-pass token entropy (phi_first style, F5). Cost: free, uses logits already computed. Expected: unknown at 1.7B. Test first: compute phi_first and NLL on the existing BOAR answer set (dev traces only), measure AUROC against judged correctness. This is one script, no training.
2. Correctness probe on the model's own hidden state (F2, F3). Cost: one forward pass (already done for generation) plus a dot product per token/layer. Needs hidden-state access (F11: not on the server; C API callback or patch). Needs labels from BOAR's own answers; F3 shows true/false labels do not transfer. Labels from the Haiku judge are noisy (13 of 37 re-judged items changed), so use exact-match gold for short factual items where possible.
3. Sampling-based SE (F1, F8). Cost: about 10x decode. At 14 tok/s and 60-80 tokens per answer, that is roughly 40-60 s per answer, not feasible for the default path. Possibly feasible only as an offline eval reference (the 3B SE number is the ceiling to beat).
4. Verbal confidence (F6, F7). Cost: free. Expected: tracks commitment, not correctness; calibration can be fitted (F7) but not certified at small size. Use only after a risk-coverage check.
5. Certified selective answering (F7, F13). Cost: a calibration set (200 items in F7) plus a bound. Expected: certified low-risk autonomy unlikely at 1-3B. Use a measured risk-coverage curve and report the coverage at a stated risk, not a guarantee.

Proposed next step (one QUEUE row, no new model downloads): on the existing BOAR 1.7B dev traces, compute NLL, phi_first (top-K entropy at first token), and mean token entropy; report AUROC vs judged correctness with bootstrap CI, plus a logistic combination. If AUROC < 0.7 at 1.7B, the abstention line is closed for single-pass signals and the phone answer should be a measured risk-coverage policy, not a confidence threshold.

## Sources opened (all visited on 2026-10-20)

- https://arxiv.org/abs/2603.21172 and https://arxiv.org/html/2603.21172v1
- https://arxiv.org/abs/2606.02628
- https://arxiv.org/abs/2608.05064
- https://arxiv.org/abs/2505.16520 and https://arxiv.org/html/2505.16520v3
- https://arxiv.org/abs/2606.29490
- https://arxiv.org/abs/2508.14496 and https://arxiv.org/html/2508.14496v3
- https://arxiv.org/abs/2207.05221
- https://arxiv.org/html/2406.15927v1
- https://arxiv.org/abs/2602.04577
- https://arxiv.org/abs/2605.05166
- https://aclanthology.org/2025.emnlp-main.187
- https://neurips.cc/virtual/2026/165336
- https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md

Not opened (snippets only): 2604.27914, 2502.06884, 2502.19110, 2605.02443, 2304.13734 (SAPLMA original), 2601.20026, 2601.02170.
