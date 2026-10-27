# Honesty / abstention fine-tuning for small models (<= 3B): research notes

Date: 2026-10-20. Angle: cheap fine-tuning so small models abstain ("I don't know") and answer faithfully from context.
Status of each source: "opened" = I fetched the arXiv abstract or HTML and read the stated numbers. "snippet" = seen only in search results, not opened. Anything marked "not verified" was not checked against the paper.

## TL;DR

- Abstention is learnable by SFT alone on a 3B base with no RL and no reward model (R-Tuning, arXiv 2311.09677). The refusal gains are large on unanswerable sets. The cost on answerable questions is the open question, and it is measured in only one paper at 7B+.
- Every paper that measured the cost found over-refusal of roughly 10-15 points at 7B and 13B (Alignment for Honesty). No opened paper measured the cost at 1-3B.
- The only opened 1-4B faithfulness-under-unanswerable-context baseline (FaithEval, ICLR 2025) shows 3.8B models at 6-13 % accuracy when the context has no answer. That matches BOAR's reading wall and says a base model is far from abstaining on its own.
- Nothing I opened tests 1B-3B models on abstention plus context faithfulness with a permissively licensed dataset. That gap is the main finding for BOAR.

## Findings

### 1. R-Tuning (Refusal-Aware Instruction Tuning). arXiv 2311.09677, NAACL 2024. Status: opened (abstract + HTML v3)

- Models: OpenLLaMA-3B, LLaMA-7B, LLaMA-13B.
- Method: split the training questions into certain and uncertain by comparing the model's own answers with gold labels. Append "I am sure" to the certain answers and "I am unsure" to the uncertain ones. The appended prompt is "Are you sure you accurately answered the question based on your internal knowledge?". Then SFT. No RL, no reward model.
- Training data: ParaRel 5575, MMLU 2448, WiCE 3470, HotpotQA 10000 (sampled from 99564), FEVER 10000 (sampled from 145449).
- Refusal rate on unanswerable sets (Table 3, R-Tuning / Vanilla):
  - FalseQA: OpenLLaMA-3B 87.32 / 2.07; LLaMA-7B 96.62 / 18.35; LLaMA-13B 95.90 / 6.00.
  - NEC: OpenLLaMA-3B 95.72 / 0.96; LLaMA-7B 99.18 / 20.55.
  - SelfAware (unanswerable): OpenLLaMA-3B 90.99 / 5.23; LLaMA-7B 95.45 / 34.79.
- In-domain accuracy (Table 1, AP %): ParaRel ID OpenLLaMA-3B 93.23 vs vanilla 92.89. MMLU ID OpenLLaMA-3B 24.96 vs 24.19 (chance level, so the 3B base is not a useful MMLU reference).
- Out-of-domain (Table 1): ParaRel OOD LLaMA-7B 74.61 vs vanilla 78.08 (R-Tuning loses here). LLaMA-13B 77.30 vs 64.12.
- Caveat: the refusal tables are measured on unanswerable sets. I did not find an over-refusal rate on answerable questions in the opened text (first 100k of 105k characters read). The "unknown" label is not a judge score, so it does not map directly onto BOAR's Haiku-judged correctness.
- Code: github.com/shizhediao/r-tuning. Code licence not verified. Paper licence: arXiv non-exclusive.

### 2. Alignment for Honesty. Yang et al., arXiv 2312.07000, NeurIPS 2024. Status: opened (HTML v1)

- Models: LLaMA2-Chat-13B (main). Table 6 adds 7B and 70B.
- Training: 8000 TriviaQA samples, balanced between known and unknown questions. Multisample expands data by m = 10.
- Metrics: Prudence = share of should-refuse cases that are declined. Over-conservativeness = share of originally-correct answers that are now refused. Honesty = 1/2 (Prudence + (1 - Over-conservativeness)).
- Table 5 (TriviaQA, LLaMA2-Chat-13B):
  - Unaligned: prudence 0, over-cons 0, honesty 50.00, acc 73.71.
  - Prompt-based: prudence 33.77, over-cons 12.50, acc 64.70.
  - Confidence-Verb: prudence 58.91, over-cons 10.68, honesty 74.12, acc 73.34.
  - Multisample: prudence 67.72, over-cons 15.89, honesty 75.91, acc 68.88.
- Table 6, 7B Confidence-Verb: prudence 56.04, over-cons 11.43, honesty 72.31, acc 68.12 (unaligned 69.07). 70B: prudence 51.44, over-cons 6.51, acc 83.10 (unaligned 84.55).
- Reading: the best trade-off costs about 1 point of accuracy and about 11 points of over-conservativeness at 7B. This is the only opened paper with a measured false-refusal cost in the fine-tuned setting.
- No 1B-3B model was tested. Note the accuracy columns are overall TriviaQA accuracy, not accuracy restricted to known questions.
- Code: github.com/GAIR-NLP/alignment-for-honesty. Licence for data and code not stated.

### 3. FaithEval (unanswerable / inconsistent / counterfactual contexts). Ming et al., arXiv 2410.03727, ICLR 2025. Status: opened (HTML v3, Table 4)

- Relevant point: the model is given a context that does not contain the answer and must say "unknown".
- Unanswerable-context accuracy (strict S / non-strict N):
  - Phi-3-mini-128k (3.8B): 0.063 / 0.134.
  - Phi-3.5-mini (3.8B): 0.131 / 0.196.
  - Phi-3-medium (14B): 0.074 / 0.253.
  - Mistral-7B-v0.3: 0.290 / 0.395.
  - Llama-3.1-8B: 0.376 / 0.388.
  - Gemma-2-9B: 0.503 / 0.507.
  - Claude 3.5 Sonnet: 0.621 / 0.630. GPT-4o: 0.597 / 0.599.
- Gap between original and unanswerable context: 13.6 % to 68.4 % across chat models. Phi-3-medium scores 75.8 % on the original context and 7.4 % on the unanswerable one.
- No 1B models were tested; the smallest are 3.8B.
- Licence: paper CC BY-NC-SA 4.0. Code: github.com/SalesforceAIResearch/FaithEval. Treat the data as NC: fine for measuring, not for shipping in a redistributed pack.
- Use for BOAR: a base 3.8B model does not abstain from unanswerable context by default. Any recipe needs negative examples and an eval on this condition.

### 4. Rewarding Intellectual Humility (RLVR with abstention reward). arXiv 2601.20126, 2026. Status: opened (abstract)

- Models: Granite-3.3-2B-Instruct and Qwen3-4B-Instruct. This is the only opened paper with a ~2B model in the abstention setting.
- Method: supervised abstention pretraining (SFT) first, then RLVR with a ternary reward: -1 wrong, r_abs for abstain, +1 correct. Moderate rewards r_abs ≈ -0.25 to 0.3 reduce wrong answers on multiple-choice without a severe accuracy loss. Larger models are more robust to abstention incentives.
- Benchmarks: MedMCQA and Hendrycks MATH. Open-ended QA shows "insufficient exploration", which SFT abstention partly fixes.
- Numbers: qualitative only in the abstract; I did not open the full text for the table values.
- Licence: paper CC BY 4.0. Code: github.com/Mystic-Slice/rl-abstention (licence not stated).
- Cost: needs RL. Heavier than R-Tuning's SFT. Not the first recipe for BOAR.

### 5. AbstentionBench. arXiv 2506.09038, NeurIPS 2025. Status: opened (HTML)

- Models: 7-8B only (Llama 3.1 8B, Mistral 7B v0.3, OLMo 7B). No 1-3B model.
- Headline: "model scale has almost no effect on abstention performance". Reasoning fine-tuning degrades abstention by about 24 % on average versus non-reasoning counterparts (the paper does not say whether this is relative or absolute).
- Judge reached 88 % accuracy on a manual sample. Abstention is scored mainly by recall; precision is high.
- Licence: paper CC BY 4.0. Code: github.com/facebookresearch/AbstentionBench.
- Use for BOAR: a candidate measurement tool for abstention. Its finding that scale does not help is a reason not to expect the 1.7B to abstain well without training. It does not supply a training recipe.

### 6. GRAIT (gradient-driven refusal-aware instruction tuning). arXiv 2502.05911, Feb 2025. Status: opened (HTML v1)

- Models: LLaMA2-7B-Chat and LLaMA3-8B-Instruct. Nothing at 1-3B.
- Data: MMLU train 14079 (5000 used), TriviaQA train 87622 (10000 used). Evaluated on MMLU val, ARC-c dev (OOD), TriviaQA dev, NQ dev (OOD).
- Table 2, LLaMA3-8B, GRait vs CRaFT (Pc accuracy / Pw error rate):
  - MMLU: 50.4 / 6.9 vs 53.3 / 9.6.
  - NQ (OOD): 21.9 / 38.8 vs 27.0 / 57.6.
- LLaMA2-7B TriviaQA: GRait 43.6 / 18.4 vs CRaFT 47.8 / 28.1.
- Method: gradient-based sample selection using LoRA and random projections to make gradient features cheap. Adaptive weighting of the idk loss only (temperature 0.05, correctness threshold 0.5).
- No explicit over-refusal rate reported; over-refusal is handled by the weighting, not measured separately.
- Code: github.com/opendatalab/GRAIT, announced as "will be available". Not verified as live. Licence not stated.
- Use for BOAR: the gradient selection costs more than SFT alone. Only worth it if plain R-Tuning-style splitting over-refuses.

### 7. CRaFT (static and dynamic conflicts in RAIT). arXiv 2410.06913. Status: opened (abstract)

- Finding: "dynamic conflict". As SFT goes on, the model becomes able to answer questions that were labelled "I don't know" at the start, so the labels go stale. Relevant when the training labels come from a single pre-training snapshot.
- Fix: certainty-based filtering and relabelling, plus a preliminary rehearsal to track knowledge change.
- Models and numbers: not in the abstract. Table numbers are in finding 6 (which uses the same paper's tables).
- Code: github.com/opendatalab/CRaFT ("will be released"). Paper licence CC BY-SA 4.0.

### 8. RAFT (Retrieval-Augmented Fine-Tuning). arXiv 2403.10131, Mar 2024. Status: opened (abstract only)

- Method: train on question + golden doc + distractor docs, with chain-of-thought answers that quote the relevant passage. Some examples omit the golden doc.
- Evaluated: PubMed, HotpotQA, Gorilla. The abstract says RAFT "consistently improves" over baselines.
- Model sizes and numbers: not extracted from the abstract (full paper not opened). Treat as unverified for size.
- Relevance: the most direct recipe for "answer from context, ignore distractors". The quote-first pattern is the one BOAR tried at prompt level and that failed (the model paraphrases). RAFT trains it in, so it is a different test from the prompt version.

### 9. Self-Alignment for Factuality. Zhang et al., arXiv 2402.09267, ACL 2024. Status: snippet only

- Method: the model self-evaluates its own answers (Self-Eval), then SK-Tuning improves confidence calibration, then DPO on self-annotated pairs. Evaluated on TruthfulQA and BioGEN. Code: github.com/zhangxy-2019 (per search results).
- Sizes: not verified (Llama-family base models named). Not opened.
- Relevance: a label-free way to get DPO pairs from the model's own correctness. Useful if BOAR cannot afford gold labels.

### 10. RHIO (retrieval-head-masked unfaithful samples). arXiv 2501.13573. Status: opened (abstract)

- Method: mask retrieval heads to create realistic unfaithful training samples, train with control tokens, then contrastive decoding over control tokens at inference. Benchmark GroundBench from 5 LFQA datasets.
- Sizes and numbers: not given in the abstract. No code link found.
- Relevance: contrastive decoding over control tokens is not the layer-contrast decoding already closed in the earlier review. Still a decoding-time cost. Not load-bearing.

### 11. CANOE (synthetic short-form QA with RL). arXiv 2505.16483, May 2025. Status: opened (abstract)

- Method: Dual-GRPO, rule-based rewards, synthetic verifiable QA. Claims gains on 11 tasks.
- Abstention is not part of it. Sizes and numbers not in the abstract. Code link not found.
- Not load-bearing.

### 12. Abstain-R1. arXiv 2604.17073, 2026. Status: opened (abstract)

- Base: Qwen2.5-3B (per search summary; the abstract says "a 3B model"). Clarification-aware RLVR reward.
- "Substantially improves over its base model", competitive with DeepSeek-R1. No numbers in the abstract. Over-refusal not reported.
- Use: a 3B abstention result to chase in the HTML. RL cost.

### 13. PFaithBench / "Rethinking Faithfulness" (arXiv 2610.07894). Status: snippet only (search summary)

- Reported in a search summary: 39 models, most faithfulness errors are over-answering; training results depend on how answer and abstain examples are composed; mismatched source sets can teach shortcuts.
- The listing is dated 2026 and I did not open it. Use only as a lead. The "composition" warning matters for data design.

## Searched and not found

- Small-model (1-3B) abstention training with over-refusal measured on answerable questions. Not found in opened papers. The only cost numbers are at 7B and 13B (finding 2).
- Llama 3.2 1B or 3B abstention or honesty results. Not found.
- RAFT numbers at small sizes. The abstract does not give them and I did not open the full paper.
- A 2024-2026 abstention paper with a permissive dataset licence stated in the paper and checked. TriviaQA, MMLU and HotpotQA licences were not checked. FaithEval is CC BY-NC-SA (NC).
- Featherless.ai "qwen2.5 1.5b/3b lora abstention" model pages (search results): they exist, but they give no benchmark numbers and no training data, so they were not used as evidence.
- Hidden-state answerability study (alphaxiv 2607.08456) and Know2Guess (arXiv 2606.26101): seen in snippets only. Know2Guess reports Qwen2.5-3B-Instruct as the most reliable of its small set, with poor calibration and benign refusals. Not opened.
- "Twin Worlds" (arXiv 2608.28018): snippet only; numbers unverified.

## What this means for BOAR

1. The cheapest recipe is R-Tuning style: sample the model on its own training questions, label each item known/unknown from the judged correctness, add a fixed uncertainty phrase to the unknown answers, then SFT with LoRA. It needs no RL. The published result works at 3B on unanswerable sets (refusal 87-96 %). This is the first candidate to test on Qwen3-1.7B.
2. The cost to measure before any claim is over-refusal on answerable items. Alignment for Honesty shows about 11 points of over-conservativeness at 7B. Expect the 1.7B to be worse. A test is only valid if it reports both refusal on unanswerable items and answer rate on answerable ones, with the same Haiku judge.
3. BOAR's 28 % confident-error rate is partly a context problem, not only a knowledge problem. FaithEval shows base 3.8B models rarely say "unknown" when the context has no answer. Negative examples built from BOAR's own packs (context present but no answer) are the training signal this implies. This is RAFT-style distractor training, not only R-Tuning.
4. The reading wall (the model receives text but does not use it) is not what honesty tuning targets. Abstention training may lower confident errors without raising correctness. The score that moves is the error rate, not the correctness. Report both.
5. AbstentionBench says scale does not fix abstention, so the 1.7B will not abstain well by default. That is a reason to train, not a reason to expect it to work without training.
6. Data licence: do not ship FaithEval data (NC). Build negatives from BOAR's own pack text (licence per pack) and from R-Tuning-style self-labels.

Minimal experiment shape (proposal, not run): Qwen3-1.7B, LoRA r=16, about 2-5k items from non-blind pack text. Labels: answerable (answer in context), unanswerable (answer removed from context). Frozen criterion before the run: refusal rate on unanswerable and answer rate on answerable, both with the Haiku judge. Log exposures per EXPOSURES.md. Do not train on blind or v0.2 items.

## Load-bearing (max 4)

- R-Tuning (2311.09677): SFT-only abstention works at 3B on unanswerable sets.
- Alignment for Honesty (2312.07000): measured over-refusal cost, 7B.
- FaithEval (2410.03727): 3.8B baseline on unanswerable context.
- Rewarding Intellectual Humility (2601.20126): ~2B and 4B, SFT warm start then RL; the small-model reference point.

## Sources opened

- https://arxiv.org/abs/2311.09677 ; https://arxiv.org/html/2311.09677v3
- https://arxiv.org/html/2312.07000v1 ; https://arxiv.org/abs/2312.07000
- https://arxiv.org/abs/2403.10131
- https://arxiv.org/abs/2410.06913
- https://arxiv.org/html/2502.05911v1 ; https://arxiv.org/abs/2502.05911
- https://arxiv.org/html/2506.09038
- https://arxiv.org/html/2410.03727v3 ; https://arxiv.org/abs/2410.03727
- https://arxiv.org/abs/2604.17073
- https://arxiv.org/abs/2601.20126
- https://arxiv.org/abs/2501.13573
- https://arxiv.org/abs/2505.16483
- Snippets only: https://arxiv.org/abs/2402.09267 ; https://arxiv.org/abs/2610.07894 ; https://arxiv.org/abs/2606.26101
