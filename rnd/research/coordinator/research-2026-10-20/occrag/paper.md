# OCC-RAG deep read (arXiv 2606.00683)

Scope: deep-read of the paper and its Hugging Face model files for BOAR. Angle: recipe, data, format, eval, limits, and what matters for an offline Android research assistant on Qwen3-1.7B. Sources: arXiv abs and HTML v1 (https://arxiv.org/html/2606.00683v1), the PDF (https://arxiv.org/pdf/2606.00683, text extracted with pdftotext -layout, saved under `src/occrag-paper.txt`), HF README and config files (https://huggingface.co/occ-ai/OCC-RAG-1.7B). No weights were downloaded. Note: the HTML pass used a small extraction model; every Table 2 number below was re-checked against the PDF text.

## TL;DR

- OCC-RAG-1.7B = Qwen3-1.7B-Base, full SFT ("mid-training") for 1 epoch on about 3.25M synthetic QA items (about 9e9 Qwen3 tokens), with a five-section trace, citation tags, and an explicit ANSWERABLE/UNANSWERABLE status.
- The gains are for context use: ConFiQA, refusal on MuSiQue-Un, and multi-hop on supplied passages. These are exactly BOAR's measured wall ("the 1.7B receives pack text but does not use it"). The paper does not test closed-book behaviour, which is the case where BOAR's 20/27 absent-knowledge errors live.
- Its training objective is to refuse when the context lacks the answer and to ignore parametric knowledge. BOAR's no-source path answers from memory under a warning. Those two policies conflict.
- Licence on the model card is MIT. The paper gives no licence or terms analysis for its corpus or teachers, and the LICENSE file on the HF repo returned 404.
- No latency, answer-length, or throughput numbers are reported.

## Findings

### F1. Training recipe (verified in PDF Table 3 and Section 4)

- Method: "supervised fine-tuning ('mid-training')", loss on response tokens only. No from-scratch pretraining. Base = Qwen3-1.7B-Base (Qwen3 chosen over Gemma3 and SmolLM3 at fixed compute on a held-out QA slice).
- Hyperparameters (Table 3, 1.7B column): AdamW, peak LR 1e-4, cosine, warmup 0.03, weight decay 0.01, bf16, max seq length 6,144, 1 epoch, per-device batch 16 x 8 GPUs = global 128, FSDP, Liger fused linear CE, about 9e9 tokens, 28 h on 8x H100 80 GB (0.6B: 17 h, global batch 256).
- Not stated: total optimizer steps, and the context length and LR used for the base-model comparison.
- Special tokens: the prompt and response delimiters are added as new tokens, with embeddings initialised from the mean of the subword embeddings of their names (Hewitt 2021). This matters for GGUF conversion and chat-template parity with Qwen3 (see F9).
- Multi-hop subsets are oversampled 3x within the one epoch; single-hop once. A single-hop-first curriculum gave no measurable difference.
- Load-bearing for BOAR: no. BOAR would not re-run mid-training. It matters only if BOAR fine-tunes its own variant later.

### F2. Synthetic data: sources, teachers, and what the paper says about licences (verified in PDF Sections 3.1-3.2)

- Single-hop: English Wikipedia XML dump, chunked and cleaned; gold paragraph plus up to 1,000 child pages (link graph) cleaned and chunked, top 20 by TF-IDF cosine kept as distractors. gpt-oss-120B generates ten short QA pairs per gold paragraph (JSON).
- Multi-hop: knowledge graphs built with Wikontic (Chepurova et al. 2026, gpt-oss-120b as base), sampled along SPARQL-like templates from the DRAGOn taxonomy (simple, three two-hop families, three-hop "bamboo"). The MuSiQue training split is named as a source of gold and distractor paragraphs (Section 3 summary from the HTML pass; not re-verified line by line in the PDF).
- Unanswerable items: a DeBERTa model fine-tuned on SQuAD (cited as Savkin et al. 2024; same first-author surname as this paper, affiliation not checked) answers questions from reduced gold contexts; if its answer does not match the original, the item becomes an abstain example.
- Teachers: gpt-oss-120B (trace/QA generation, Wikontic), Qwen3.5-27B (reasoning traces, native thinking disabled), Qwen3-4B (verifier judge).
- Licences: the paper does not discuss licences for Wikipedia (CC BY-SA), MuSiQue, DRAGOn, or the teacher models' terms. Nothing in the paper covers redistribution of the synthetic data. The HF model card (MIT) covers only the weights as the authors state them.
- Load-bearing: yes (see L4 below). Model redistribution in an app depends on the weight licence and on whether the teacher-output and corpus terms are acceptable. The paper is silent, so this is an open question, not a clearance.

### F3. Data mix and filtering (verified in PDF Section 3.4 and Figure 4 text)

| Subset | QA pairs | Qwen3 tokens (Fig. 4) |
|---|---|---|
| Single-hop | 2.78M | 7.76B |
| Multi-hop, single-context | 262k | 0.21B |
| Multi-hop, multi-context | 165k | 0.16B |
| Abstain | 43k | 0.029B |

- Total about 3.25M QA pairs and about 8B Qwen3 tokens (the paper's Figure 4 subtotals sum to about 8.2B; the stated "roughly 8B" and "about 9e9 tokens" for training are both given).
- Distractor contexts are 35-75 % of tokens, depending on subset.
- Filters, in order: (1) format, all five sections present; (2) exact-match answer, with refusal items dropping any trace that asserts an answer; (3) Qwen3-4B judge re-checks exact-match failures; (4) overthinking: drop traces with reasoning over 1,256 tokens or more than 10 thinking markers (Wait, Alternatively, etc.).
- The overthinking cap means the training traces are short by design (reasoning section at most 1,256 tokens). This is the only length statement the paper makes (see F6).
- Load-bearing: no.

### F4. Output format and an example trace (verified in PDF Section 3.3, Figure 3, Figure 6)

- Five sections, delimited by special tokens: Query Analysis, Source Analysis, Reasoning, Status (ANSWERABLE or UNANSWERABLE), Answer. The Status is placed before the answer on purpose: "turning abstention into a discrete label that the model has to commit to before producing the answer".
- Source citations are numeric source IDs inside the trace, with literal quotes from the context (per the abstract and HF README).
- Figure 6 example (multi-hop, multi-context subset): question "What is the name of the unit that the main character of the series featuring Karen Hayes is a member of?". Reasoning goes Karen Hayes -> "24" (source 1) -> Jack Bauer (source 3) -> Counter Terrorist Unit (CTU). Status ANSWERABLE.
- The format is adapted from Pleias-RAG (Langlais et al. 2025).
- BOAR relevance: this trace is roughly 5 sections of structured text, so output length per answer is much longer than BOAR's current 2-5 sentence answers (see F6).

### F5. Results, Table 2 (verified against the PDF text; numbers copied exactly)

Columns: HotpotQA In-Acc / MuSiQue In-Acc / TAT-QA F1 / ConFiQA In-Acc / ConFiQA MR (lower is better) / MuSiQue-Un R-Acc. Parentheses = thinking mode on, where the model supports it.

| Model | HotpotQA | MuSiQue | TAT-QA | ConFiQA In-Acc | ConFiQA MR | MuSiQue-Un R-Acc |
|---|---|---|---|---|---|---|
| Qwen3-0.6B | 34.8 (41.8) | 13.2 (17.2) | 62.5 (66.3) | 59.7 (64.5) | 9.0 (8.2) | 6.3 (70.0) |
| Qwen3-1.7B | 47.7 (60.9) | 20.1 (30.7) | 74.4 (74.8) | 64.8 (70.4) | 12.7 (8.3) | 54.7 (82.8) |
| Qwen3-4B | 60.6 (67.1) | 33.1 (41.5) | 76.9 (79.1) | 69.7 (74.1) | 10.3 (7.5) | 64.1 (84.0) |
| Qwen3-8B | 68.7 (70.3) | 39.3 (43.9) | 72.9 (74.5) | 75.9 (77.6) | 9.2 (6.9) | 90.7 (90.3) |
| Qwen3-32B | 70.9 (71.4) | 49.7 (49.3) | 75.9 (76.7) | 72.0 (75.8) | 11.5 (8.5) | 80.7 (87.0) |
| SmolLM3-3B | 49.9 (56.5) | 21.5 (29.4) | 71.1 (69.7) | 58.6 (60.5) | 15.4 (13.3) | 32.1 (77.1) |
| Pleias-RAG-1.2B | 48.5 | 15.0 | 8.4 | 37.3 | 25.3 | 21.9 |
| OCC-RAG-0.6B | 57.6 | 36.6 | 75.0 | 79.9 | 5.2 | 86.9 |
| OCC-RAG-1.7B | 60.9 | 38.2 | 81.0 | 81.4 | 5.0 | 87.2 |

The Gemma3 rows (1B, 4B, 12B, 27B, no-thinking) are in the PDF Table 2 as well; the 4B row is HotpotQA 55.8 / MuSiQue 30.1 / TAT-QA 65.3 / ConFiQA 69.8 / MR 8.9 / MuSiQue-Un 55.8.

Reading against BOAR's question:
- The task brief says "vs Qwen3-1.7B think mode the gains shrink (HotpotQA equal)". Verified: 60.9 (think) = 60.9 (OCC). Other pairs: MuSiQue 30.7 vs 38.2, TAT-QA 74.8 vs 81.0, ConFiQA 70.4 vs 81.4, MuSiQue-Un 82.8 vs 87.2. OCC-1.7B beats the think-mode Qwen3-1.7B on every column except MR (where it is lower, i.e. better, 5.0 vs 8.3).
- Non-thinking baseline (BOAR's real setting): the 47.7 -> 60.9, 20.1 -> 38.2, 74.4 -> 81.0, 64.8 -> 81.4, 12.7 -> 5.0, 54.7 -> 87.2 gains. Table 2 has the no-thinking Qwen3 numbers as the main value, so the comparison BOAR cares about is the non-thinking column.
- Caveat on the metric: the MuSiQue-Un R-Acc counts the phrase "Not enough information" in the prediction (Section 5.1). HotpotQA / MuSiQue In-Acc is a substring match (Section 5.1 defines it so). Both are weaker than BOAR's LLM-judged reference. Numbers are not comparable to BOAR's judge without re-scoring.
- The paper's own setting uses 10 sources per question for HotpotQA, MuSiQue and MuSiQue-Un; TAT-QA 1 source; ConFiQA 1 source. BOAR's packs supply fewer and noisier chunks. This is a context-size mismatch to test, not assume away.
- Load-bearing: this is the evidence for the adoption question, but it is on the paper's benchmarks. Included under L2 and L3.

### F6. Length, latency, and throughput (verified: absent)

- The paper reports no answer length, latency, token count per answer, or throughput. It says "chain-of-thought-level transparency at a fraction of the cost of full thinking-mode inference" and "substantially less compute" (Section 5.1 and conclusion) with no figures.
- Inference from the training filter (not measured): the reasoning section is capped at 1,256 tokens in training, and the HF usage sets max_new_tokens 2048. A five-section trace is plausibly several hundred tokens. On a phone at 12-16 tok/s decode (BOAR's measured speed for a 1.7B) that is tens of seconds per answer, against BOAR's current short answers. This is an estimate and must be measured on device with BOAR's own prompts.
- Load-bearing: yes, see L4.

### F7. Behaviour without context, and the abstention policy (verified: partly absent)

- The paper never evaluates closed-book (no passage) behaviour. All benchmarks supply passages (10 sources or 1 for ConFiQA / TAT-QA). The refusal benchmark (MuSiQue-Un) tests abstention when the passages lack the answer, not when no passages are supplied.
- The training and inference prompt says "ignore parametric knowledge" (HF README: "The model is trained to answer from the supplied sources and to ignore parametric knowledge"). Figure 2 shows the 1.7B answering the counterfactual "de Gaulle" from context. So the model is steered away from memory by design.
- BOAR's current policy is the reverse on the no-source path: answer from memory with a warning line. The OCC behaviour when no passage is supplied is unknown and, by its training distribution, likely to output "Not enough information" / UNANSWERABLE. That changes BOAR's product behaviour for a large share of casual questions, which are the cases BOAR cares about. Load-bearing: yes, see L1.
- The abstain training subset is 43k items (1.3 % of the 3.25M), built from SQuAD-style answer-recovery failure, not from "no passage at all".
- Load-bearing for BOAR's policy decision, not for the benchmark.

### F8. Ablations and analysis (verified: thin)

- Multi-hop oversampling (3x): "consistently improves multi-hop benchmark accuracy without measurable regression on single-hop" (no table).
- Curriculum (single-hop first, then mix): no measurable difference.
- Thinking in the teacher (Qwen3.5-27B native thinking): dropped; "did not yield a meaningful improvement in distilled-student quality" on the dev slice (no table).
- Base model: Qwen3 beat Gemma3 and SmolLM3 "at fixed compute" on a held-out QA slice (no table).
- Mid-training effect on Qwen3-1.7B: MR 12.7 (8.3 think) -> 5.0.
- No failure analysis, no per-category breakdown, no seeds, no confidence intervals. Dev-slice numbers are not reported.
- Load-bearing: no. It limits how much the 1.7B number can be trusted as a general claim.

### F9. Usage, prompt format, and decoding (verified in HF README and generation_config.json)

- HF README: load with transformers, `tokenizer.apply_chat_template` with the question as the user message and sources passed as `documents=`; `enable_thinking=False`; `model.generate(..., max_new_tokens=2048)`; parse answer with a regex on `<|answer_start|>`; keep `skip_special_tokens=False` to parse the sections.
- Prompt tags from the README: the question wrapped in `<|query_start|> ... <|query_end|>`, each source wrapped in source tags with a numeric source-ID token. The paper's Figure 6 uses `<|query|>`, `<|source|>`, `<|source_id|>`, `<|*|>`; the README token names are the ones to trust for code.
- System prompt: none specified in the README.
- generation_config.json: do_sample false, temperature 0.0 (greedy), max_new_tokens 2048 (via the code above), EOS token IDs 151643, 151645, 151683, pad 151643; written for transformers 5.5.4.
- Eval decoding: the paper says baselines use each model's recommended sampling settings, but does not state the decoding used for OCC-RAG. The README says greedy is the training and evaluation default.
- Config (1.7B): Qwen3ForCausalLM, qwen3, 28 layers, hidden 2048, max_position_embeddings 32768, vocab 151936, dtype bfloat16.
- Implication for BOAR: greedy decoding is the default, so the 1.7B output is deterministic. Adding the special-token template to a llama.cpp GGUF path is a conversion and template task that the paper does not address. Not load-bearing; it is an engineering task, but it is a real cost.

### F10. Limitations (verified: minimal, from HF card and the paper)

- HF card: "Context-grounded only. The model is trained to answer from the supplied sources and to ignore parametric knowledge." And "Training and evaluation are capped at three-hop reasoning; longer chains are out of distribution."
- The paper has no dedicated limitations section. The discussion of limits is limited to these points and to the lack of compute, latency, and closed-book evaluation.
- Not evaluated: non-English, general chat, casual questions, long multi-document retrieval (BOAR-style 20+ chunks), quantized GGUF, on-device latency.

### F11. Licence and provenance (verified in part; gap noted)

- HF README YAML: `license: mit`. Base model: Qwen/Qwen3-1.7B-Base (its licence was not checked in this pass).
- Featherless page: MIT per the brief. Consistent.
- LICENSE file at https://huggingface.co/occ-ai/OCC-RAG-1.7B/raw/main/LICENSE returned HTTP 404. So there is no separate licence text in the repo at the time of this read. The YAML field is the only licence statement found.
- Not licensed or cleared in the paper: Wikipedia text (CC BY-SA, attribution and share-alike terms apply to the text used to create the data, and the paper does not discuss how this affects the weights), MuSiQue (licence not checked here), DRAGOn, Wikontic, and teacher outputs from gpt-oss-120B and Qwen3.5-27B (their terms were not checked here).
- Load-bearing: yes, see L4 (adoption is gated on the licence and provenance of the weights, not just the MIT label).

### F12. Performance vs BOAR's measured walls (analysis, not from the paper)

- BOAR's walls: the 1.7B receives pack text but does not use it (OCC targets this directly: "faithful" answers from context, ConFiQA MR 12.7 -> 5.0). This is the strongest reason to test.
- BOAR's 28 % confident errors, 20 of 27 with no relevant source retrieved (absent knowledge): OCC does not add knowledge. Its abstention training may turn some confident errors into refusals, but it does not fix absent-knowledge questions unless the packs contain the answer. Expect the gain to live in the "source present but unused" bucket only.
- BOAR's judge: LLM-judged, with a frontier+web reference, on casual research questions. The paper's benchmarks (HotpotQA, MuSiQue, TAT-QA, ConFiQA, MuSiQue-Un) are Wikipedia / finance / counterfactual and are not casual research questions. The transfer is unmeasured.
- Expected direction (inference): OCC-RAG-1.7B should beat plain Qwen3-1.7B non-thinking on source-grounded questions with a good source; it may refuse more on no-source questions; the net effect on BOAR's judge score depends on the mix. Needs a BOAR A/B on the frozen dev items, with the no-source path measured separately.

## Lead list for BOAR (load-bearing, at most 4)

- L1. Abstention policy conflict. OCC is trained to answer only from supplied sources and output "Not enough information" / UNANSWERABLE when the context is insufficient. BOAR's no-source path answers from memory under a warning. Adoption changes product behaviour on the no-source path, which is most of the casual questions. Decide the policy before any measurement, or measure the no-source path separately.
- L2. Targets BOAR's measured wall. The paper's gains are on context use and faithfulness (ConFiQA MR 12.7 -> 5.0, In-Acc 64.8 -> 81.4 non-thinking; MuSiQue-Un 54.7 -> 87.2). These are the "receives pack text but does not use it" failure. Worth a bounded A/B on BOAR's dev items with the same packs.
- L3. Does not address absent knowledge. Its gains are on supplied passages with 10-source contexts. The 20 of 27 confident errors with no relevant source are unchanged by the model alone. The adoption case must rest on the source-present bucket.
- L4. Licence and provenance are unresolved for an app. MIT on the HF YAML, but the LICENSE file returned 404, and the paper says nothing about Wikipedia (CC BY-SA) or the teacher-output terms (gpt-oss-120B, Qwen3.5-27B). Also no latency or answer-length numbers, and the five-section trace is probably long on a 12-16 tok/s phone. Each needs a check before adoption.

## Open questions and gaps

- Teacher and corpus licences: check gpt-oss-120B and Qwen3.5-27B output terms, Qwen3-4B, Wikipedia CC BY-SA obligations, MuSiQue licence, and whether the weights are a derivative of the training data in a way that matters for an app.
- Actual GGUF availability and the special-token chat template under llama.cpp (not checked; weights not downloaded per the brief).
- Output length on BOAR prompts: measure tokens per answer; the 2048 max_new_tokens cap is the upper bound.
- Closed-book behaviour: the paper does not test it. Test with zero passages on BOAR's casual set.
- Retrieval context size: 10 sources in the paper vs BOAR's pack k. Test at BOAR's k.
- Judge transfer: the paper's In-Acc and R-Acc are substring / phrase metrics. BOAR's judge is an LLM. Re-score the same outputs with BOAR's judge before comparing numbers.
- Mismatch between the paper's Figure 6 token names and the HF README token names. Use the README names for code.
- Trace faithfulness: the paper's citations are "literal quotes" per the abstract, but there is no quote-accuracy metric in the paper. Check quote accuracy on BOAR's packs.
- Results are single-paper, single-author-group, no seeds or confidence intervals. Treat the deltas as unverified until reproduced.

## Sources read

- https://arxiv.org/abs/2606.00683 (title, authors, date, abstract)
- https://arxiv.org/html/2606.00683v1 (HTML extraction, cross-checked)
- https://arxiv.org/pdf/2606.00683 (text via pdftotext; saved under `src/occrag-paper.txt`)
- https://huggingface.co/occ-ai/OCC-RAG-1.7B/raw/main/README.md
- https://huggingface.co/occ-ai/OCC-RAG-1.7B/raw/main/config.json
- https://huggingface.co/occ-ai/OCC-RAG-1.7B/raw/main/generation_config.json
- https://huggingface.co/occ-ai/OCC-RAG-1.7B/raw/main/LICENSE (HTTP 404)
