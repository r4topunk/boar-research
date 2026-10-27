# verify-1: adversarial verification of 10 claims (uncertainty, extractive, rag_slms)

Verifier: Opus 5.5, 2026-10-20. Every source below was opened (arXiv HTML/PDF, HF API, GitHub API).

| # | Angle | Status | One-line verdict |
|---|---|---|---|
| 1 | uncertainty | corrected | NLL range is 0.50-0.69, not 0.63-0.69. The paper's own single-pass prompt probe (PC probe) reaches 0.81-0.89 on TriviaQA, so "the gap needs samples" is wrong |
| 2 | uncertainty | confirmed | Numbers exact (Llama 2-7B L16 0.8281 / L20 0.8012; TriviaQA-generated 0.562-0.594) |
| 3 | uncertainty | confirmed | Means check out. Models: Llama-3.1-8B, Mistral-7B-v0.3, Qwen2.5-7B; PopQA + TriviaQA, closed-book; K = 100 |
| 4 | uncertainty | confirmed (sharpened) | Best Platt ECE 0.015 (Qwen2.5-3B, ARC). The 3 certified pairs at 20 % risk are all 7B/14B; no model <= 3B is certified at any budget |
| 5 | extractive | confirmed | 84.8/82.0 (MIT); nbroad squad2 81.5/78.3 self-reported, 81.641/78.534 eval block (cc-by-4.0) |
| 6 | extractive | confirmed | All numbers exact. Judge "OpenAI GPT-4.0" via DSPy; code repo has no licence (all rights reserved by default) |
| 7 | extractive | corrected (minor) | Numbers exact. Code URL is github.com/chandar-lab/Hallucinate-less (not chandarlab), and GitHub API returns 404 for it. Missing context: Llama-3.2-1B FT scores only 56.8 |
| 8 | extractive | confirmed (abstract-level) | MRQA benchmark; readers RoBERTa, ELECTRA, T5-base, BART-large (<= ~400M, 2022). These are fine-tuned readers, not in-context decoder LLMs |
| 9 | rag_slms | corrected | Table numbers exact. Weak points: Qwen3-1.7B *think* equals OCC on HotpotQA (60.9) and reaches 82.8 R-Acc. OCC cites by source id, not literal quotes. It emits a 5-section reasoning trace (output-token cost). GGUF exists (occ-ai/OCC-RAG-1.7B-GGUF, Q4_K_M 1.11 GB), licence MIT |
| 10 | rag_slms | corrected | Third-party numbers exact, but they come from the OCC-RAG paper (a competitor, likely format-mismatched: TAT-QA F1 8.4). 3,126,691 examples at 4096 ctx confirmed in arXiv 2504.18225. The official GGUF is a single unquantized 2.39 GB file |

## 1. Entropy alone is insufficient (arXiv 2603.21172)
- Source: https://arxiv.org/html/2603.21172v1, "Entropy Alone is Insufficient for Safe Selective Prediction in LLMs".
- Models: Llama-3.2-3B-Instruct, Qwen3-4B-Instruct-2507, Gemma-3-4B, Ministral-8B-Instruct-2410. SE uses K = 10 samples at T = 1. Each dataset has 1,000 questions split 70/15/15, so the test set is about 150 questions (wide CIs).
- Sequence NLL AUROC (TriviaQA / BioASQ / MedicalQA):
  - Llama 3B: 0.664 / 0.656 / 0.690
  - Qwen3 4B: 0.632 / 0.663 / 0.613
  - Gemma 3 4B: 0.504 / 0.647 / 0.635
  - The range across the 3-4B models is 0.504-0.690, not 0.63-0.69.
- SE on TriviaQA: Llama 0.884, Qwen 0.844, Gemma 0.752 (all exact). SE probe on Llama TriviaQA: 0.723 (exact).
- **Contradiction of the actionable claim:** the paper's PC probe is a logistic regression on the prompt's hidden state at the last token before generation. It needs one forward pass and no sampling, and it scores on TriviaQA:
  - Llama 3B: 0.813
  - Qwen3 4B: 0.888, above SE's 0.844
  - Gemma 4B: 0.752
- On BioASQ/MedicalQA, SE itself is only 0.65-0.78, so samples do not rescue those domains either.
- Takeaway for BOAR: a cheap single-pass signal is possible, but it needs a probe trained on BOAR's own correctness labels (see claim 2). Raw NLL is not enough.
- Tested at <= 3B: Llama-3.2-3B only. Phone: the probe needs hidden-state access. llama.cpp can expose embeddings, but the app does not do this today.

## 2. Hidden states hiding something (arXiv 2505.16520v3)
- Source: https://arxiv.org/html/2505.16520v3. Paper licence CC BY 4.0.
- Llama 2-7B, leave-one-topic-out on the True-False dataset (avg), by layer: last 0.7326, 28 0.7351, 24 0.7586, 20 0.8012, 16 0.8281.
- On TriviaQA LLM-generated facts (Table 6, threshold 0.5): 0.562 (last) to 0.594 (L16). Threshold tuning does not help.
- Models are 7B only (Llama 2-7B, OPT-6.7B); nothing at <= 3B.
- Code: github.com/sisinflab/HidingInTheHiddenStates. The repo exists; GitHub API reports no licence.

## 3. The first token knows (arXiv 2605.05166)
- Source: https://arxiv.org/html/2605.05166.
- Models: Llama-3.1-8B-Instruct, Mistral-7B-Instruct-v0.3, Qwen2.5-7B-Instruct. Benchmarks: PopQA test and TriviaQA val, n = 1000 each. K = 100 top logits.
- Per-cell phi_first AUROC: PopQA 0.887 / 0.842 / 0.895; TriviaQA 0.794 / 0.727 / 0.772. The mean is 0.820.
- Comparator means are also exact: Sem. AU 0.793, AU-full 0.791.
- Gaps and caveats:
  - The paper reports no NLL baseline.
  - The setting is closed-book short answers. BOAR answers are 2-5 RAG sentences, so the "first content-bearing token" has to be defined for that format.
  - Nothing was tested at <= 3B.
  - Phone fit: yes. llama.cpp exposes top-n probs, and the score adds no extra decode. No code link.

## 4. Provable limits and certified deferral (arXiv 2608.05064)
- Source: https://arxiv.org/html/2608.05064.
- 11 models:
  - Qwen2.5-0.5/1.5/3/7/14B
  - Llama3.2-1B/3B, Llama3.1-8B
  - Gemma3-1B/4B/12B
- Setup: ARC-Challenge + TruthfulQA (multiple choice), verbalized confidence. 25,168 predictions over 22 pairs.
- Best Platt ECE: 0.015 (Qwen2.5-3B, ARC); the abstract rounds it to 0.02.
- Certified autonomy at 20 % risk:
  - Qwen2.5-14B ARC (99.8 % coverage)
  - Qwen2.5-7B ARC (93.3 %)
  - Qwen2.5-14B TruthfulQA (43.6 %)
- At 10 % risk: none. So no model <= 4B is certified at either budget.
- Caveat: the tasks are multiple choice, not open QA. No code; arXiv licence only.

## 5. DeBERTa-v3-xsmall (HF)
- microsoft/deberta-v3-xsmall: MIT licence, "22M backbone parameters" + "48M parameters in the Embedding layer". SQuAD 2.0 dev 84.8/82.0 (F1/EM).
- nbroad/deberta-v3-xsmall-squad2: cc-by-4.0. Card text: "I got 81.5/78.3 but I only did one run and I didn't use the official squad2 evaluation script". The eval block gives squad_v2 EM 78.534 / F1 81.641.
- No on-device latency is published, as the claim says.

## 6. LLMQuoter (arXiv 2501.05554v1)
- Semantic accuracy, full context -> quotes: LLaMA 1B 24.4 -> 62.2, LLaMA 3B 57.7 -> 83.0, GPT-3.5 Turbo 75.8 -> 88.5.
- Quoter before -> after fine-tuning: P 43.6 -> 71.0, R 48.3 -> 68.0, F1 41.3 -> 69.1.
- Setup:
  - Teacher: Gemini Pro 1.5.
  - Data: 15k HotpotQA = 14.4k train/val + 600 test.
  - LoRA: about 24M trainable parameters.
  - Judge: "OpenAI GPT-4.0" via DSPy.
- Caveats:
  - The full context is the HotpotQA distractor set (long, 10 paragraphs), unlike BOAR's 2-5 short chunks, so the gain may be smaller for BOAR.
  - The answerers are not fine-tuned and are compared without a retrieval baseline.
- Code: github.com/yurifacanha/LLMQuoter. GitHub API licence = null, so the code is not redistributable without asking. A reimplementation is easy.

## 7. Hallucinate-less (arXiv 2506.21288)
- SQuAD v2 relevance (binary; decoders answer yes/no), mean ± std over 5 seeds, with inference FLOPs:

| Model | Accuracy | Inference FLOPs |
|---|---|---|
| RoBERTa-base FT | 75.8 ± 0.3 | 3.7e11 |
| RoBERTa-large FT | 90.2 ± 0.4 | 1.1e12 |
| ModernBERT-base FT | 86.4 ± 0.2 | 5.1e11 |
| Llama-3.2-1B FT | 56.8 ± 1.4 | 2.9e12 |
| Llama-3.2-3B FT | 82.2 ± 0.8 | 7.0e12 |
| Llama-3.1-8B FT | 91.1 ± 0.8 | 1.6e13 |
| GPT-4o 0-shot | 95.5 | n/a |

- No latency was measured.
- Code: the URL is github.com/chandar-lab/Hallucinate-less. The GitHub API returns Not Found (the repo is private or missing), so the licence is unknown.

## 8. Choose your QA model wisely (arXiv 2203.07522, Luo et al. 2022)
- The abstract says what the claim says. In the full text:
  - The benchmark is MRQA (6 in-domain + 6 out-of-domain datasets).
  - The readers are RoBERTa, ELECTRA, T5-base and BART-large, fine-tuned as extractive and generative readers (nine configurations).
  - T5-large was excluded as "too large (737M)".
- Relevance to BOAR: weak. It compares fine-tuned small seq2seq generators with encoders, not an in-context 1.7B decoder LLM. It only supports re-testing an encoder reader, which is what the claim says.

## 9. OCC-RAG (arXiv 2606.00683) + HF
- Table 2 values are exact. Qwen3-1.7B no-think (think in parentheses):
  - HotpotQA 47.7 (60.9)
  - MuSiQue 20.1 (30.7)
  - TAT-QA 74.4 (74.8)
  - ConFiQA 64.8 (70.4)
  - MR 12.7 (8.3)
  - MuSiQue-Un 54.7 (82.8)
- OCC-RAG-1.7B: 60.9 / 38.2 / 81.0 / 81.4 / 5.0 / 87.2.
- Corrections:
  - Against Qwen3-1.7B **think**, the HotpotQA gain is 0 and refusal is +4.4. The large gains appear only against no-think.
  - Citations are by source id (`<|source_id|>N`) inside a 5-section structured trace (query analysis, source analysis, reasoning, status, answer), not literal quotes.
  - The trace means many output tokens, so answer latency at 12-16 tok/s must be measured.
  - Prompt format: special tokens via the chat template with `documents=`.
- Training: about 3.25M QA pairs (2.78M single-hop, 262k MH single-context, 165k MH multi-context, 43k abstain), roughly 9e9 tokens, distilled from a larger teacher. Metrics are substring-based, and the numbers are vendor-reported.
- Availability (HF API, 2026-10-20):
  - occ-ai/OCC-RAG-1.7B: MIT, base Qwen3-1.7B-Base, languages en/ru.
  - occ-ai/OCC-RAG-1.7B-GGUF, files: Q4_0 1.05 GB, Q4_K_M 1.11 GB, Q5_K_M, Q6_K, Q8_0, F16/BF16.
  - Mirrors: mradermacher GGUF and ONNX.
  - GitHub: optimal-cognitive-core/OCC-RAG.
- It fits the phone RAM budget as a drop-in (same size as the current main model).

## 10. Pleias-RAG-1B (HF + arXiv 2504.18225)
- HF card: apache-2.0. The card says 1.2B parameters; the paper uses both "1B" and "1.2B".
- Benchmarks appear only in figures. The paper text says it is SOTA on 2Wiki and "comparable to the best available LLMs in the 4-8B range for HotpotQA".
- Mid-training: 3,126,691 examples, about 9.47B tokens, 4096 ctx. Citations are literal `<ref>` quotes, so Pleias, not OCC, is the literal-quote model.
- The third-party numbers (48.5 / 15.0 / 8.4 / 37.3 / 25.3 / 21.9) come from the OCC-RAG paper's Table 2, a competing vendor. TAT-QA F1 8.4 points to a format mismatch (long cited answers vs token-F1), so treat them as a lower bound.
- GGUF: PleIAs/Pleias-RAG-1B-gguf contains one file, Pleias-RAG-1B.gguf, 2.39 GB unquantized. A Q4 needs a local quantization.
