# Extractive and hybrid readers for on-device QA: research notes

Date: 2026-10-20. Angle: small encoder span/sentence readers, answer-sentence selection, extract-then-generate, copy and constrained decoding. Scope for BOAR: offline Android, RAM ~8 GB total, Pixel 8a (Tensor G3, CPU llama.cpp), main reader now Qwen3-1.7B, licences must allow redistribution (no NC), no paid APIs.

Method: 14 WebSearch calls (standard mode only; extended not used) and 17 WebFetch calls. Most arXiv fetches returned only the abstract page (no tables). Items marked "snippet only" were seen in search results and were NOT opened. Items marked "abstract only" were opened but the page had no numbers.

---

## TL;DR

1. The only span readers with clean licences and published SQuAD 2.0 numbers are small encoders. DeBERTa-v3-xsmall (MIT, 22M backbone + 48M embedding params) has 84.8 F1 / 82.0 EM on SQuAD 2.0 dev per its model card. MobileBERT (Apache-2.0) has 79.2 F1 on SQuAD 2.0 dev per the arXiv abstract page, and 62 ms latency on a Pixel 4 for a GLUE task (not QA).
2. A span reader trained on SQuAD 2.0 has a native "no answer" output. That maps directly onto BOAR's current routing (no source found -> answer from memory under a warning). This is the strongest reason to test one: it is a cheap gate that does not depend on the 1.7B using the text.
3. The closest published evidence that "quote first, then answer" helps a small model a lot (LLMQuoter, +25 points at 3B) depends on fine-tuning the quote extractor. BOAR's prompt-only quote instruction failed. Whether a fine-tuned quoter at 1-3B beats prompt-only on BOAR's 180 self-test items is untested.
4. Copy-constrained decoding (CoCoLex, Lazy-k, STOC-TOT) exists in the literature but the fetched sources give no QA numbers, and the one with numbers in its abstract is for legal text. Low priority.
5. No 2024-2026 paper directly compares extractive readers against 1-3B generative readers in RAG. The best-known comparison is from 2022 (Luo et al.) and is qualitative in its abstract.

---

## Findings

### F1. MobileBERT: on-device encoder, SQuAD 2.0 F1 79.2
- Source: https://arxiv.org/abs/2004.02984 (abstract page opened; ACL 2020)
- Quote: "62 ms latency on a Pixel 4 phone" (GLUE NLI tasks). SQuAD: "Dev F1 of 90.0/79.2" (v1.1/v2.0), "1.5/2.1 higher than BERT_BASE". EM not reported on the page.
- Size: not stated on the fetched page. Treat parameter count as unverified (widely cited as about 25M; check the checkpoint).
- Licence: google/mobilebert-uncased on Hugging Face is tagged apache-2.0 (https://huggingface.co/google/mobilebert-uncased, opened). The checkpoint is pretraining-only (AutoModelForPreTraining, fill-mask example), so QA needs a fine-tune on SQuAD 2.0. The fine-tuned checkpoints found by search were aggregator pages with no numbers, so use a checkpoint with a model card.
- Latency is for GLUE, not QA. There is no QA latency number on the phone in what I opened.

### F2. DeBERTa-v3-xsmall: best small-encoder reader with a clean licence
- Source: https://huggingface.co/microsoft/deberta-v3-xsmall (opened)
- Quote: "License: mit"; "It has only 22M backbone parameters" and "introduces 48M parameters in the Embedding layer"; SQuAD 2.0 dev F1/EM "84.8/82.0" (fine-tuning table).
- Community fine-tune: https://huggingface.co/nbroad/deberta-v3-xsmall-squad2 (opened). Licence tag cc-by-4.0 (the fine-tune's own licence; check before redistributing). Self-reported "F1 81.500 and exact 78.300", with the author's note: "I got 81.5/78.3 but I only did one run and I didn't use the official squad2 evaluation script." The page's eval block gives F1 81.641 / EM 78.534 on squad_v2 validation (11,870 examples). Our own reproduction would be needed, since the two numbers differ by about 3 points.
- Latency and size on device: not reported anywhere I opened. The 48M embedding table is most of the storage; in int8 the file is still well under 100 MB (my estimate, not measured).
- Relevance: a reader that scores each (question, passage) pair in tens of milliseconds on a laptop CPU is plausible, but it is an estimate. Latency on the Tensor G3 is unmeasured.

### F3. DeBERTa-v3 base and small SQuAD 2.0 numbers (from DeBERTaV3 paper)
- Source: https://arxiv.org/pdf/2111.09543 (snippet only, NOT opened).
- Snippet: small (44M backbone) "82.8 F1 and 80.4 EM"; base (86M backbone) "88.4 F1 / 85.4 EM"; large about 91 F1 (community model cards, e.g. https://huggingface.co/deepset/deberta-v3-large-squad2, snippet only; the card lists exact match 88.0876 and F1 91.1623 on squad_v2 validation).
- Use: these give the accuracy-vs-size ladder for the encoder family. Verify in the paper before quoting.

### F4. ModernBERT-base: Apache-2.0 encoder, longer context, no QA numbers
- Source: https://huggingface.co/answerdotai/ModernBERT-base (opened)
- Quote: "149 million parameters across 22 layers"; native context "up to 8,192 tokens"; licence "apache-2.0"; GLUE 88.4 (base), 90.4 (large).
- QA: the card gives no general QA benchmark (StackQA 56.4 base / 59.5 large is a code task). No latency numbers; the card notes full-length inference may be slower.
- Groundedness-task fine-tune (F5 below): ModernBERT-base reaches 86.4 on SQuAD v2 as a yes/no classifier. That is not a span reader, but it shows the family is competitive at ~149M params.
- BOAR relevance: 149M is about 3-4x a DeBERTa-xsmall backbone plus embeddings. Its 8k context could let a whole retrieved page go in one pass, which matters for the 2-chunk/350-token context BOAR uses now. Not needed for that context size.

### F5. Small encoders vs LLMs for grounded-or-not classification (SQuAD v2, NewsQA, TREC-COVID, Touché)
- Source: https://arxiv.org/abs/2506.21288 (abstract opened) and https://arxiv.org/html/2506.21288 (HTML opened; tables read from it).
- Authors: Abbes, Prato, Fournier, Rodriguez, Boukhary, Elwood, Chandar (Jun 2025).
- Task: yes/no classification of whether the context grounds the query. NOT span extraction, NOT answer selection. Included because it gives the only 2025 numbers I found that put small encoders and 1-3B LLMs on the same SQuAD 2.0 grounding task.
- Accuracy, SQuAD v2.0 column (mean over five seeds for fine-tuned rows):
  - RoBERTa-base FT 75.8 ± 0.3; RoBERTa-large FT 90.2 ± 0.4; Nomic-BERT FT 79.8 ± 0.5; ModernBERT-base FT 86.4 ± 0.2; NeoBERT FT 79.0 ± 0.3.
  - Llama-3.2-1B-Instruct: 0-shot 55.2, FT 56.8 ± 1.4.
  - Llama-3.2-3B-Instruct: 0-shot 75.9, FT 82.2 ± 0.8.
  - Llama-3.1-8B-Instruct: 0-shot 81.9, FT 91.1 ± 0.8.
  - GPT-4o 0-shot 95.5.
- Compute (Table 1, FLOPs per inference): ModernBERT-base 5.1e11; RoBERTa-large 1.1e12; Llama-3.2-1B 2.9e12; Llama-3.2-3B 7.0e12; Llama-3.1-8B 1.6e13. So ModernBERT-base is about 5.7x cheaper per example than the 1B LLM and about 14x cheaper than the 3B, by this count. Latency is not reported.
- Caveats: the paper has internal inconsistencies (text vs table averages, e.g. Llama-8B Touché 74.5 in text vs 75.4 in the table). Code is linked at github.com/chandarlab/Hallucinate-less, no licence stated.
- Read for BOAR: a fine-tuned encoder beats a fine-tuned 3B LLM on the grounding decision (RoBERTa-large 90.2 vs Llama-3B FT 82.2), at a fraction of the compute. That supports using an encoder as the gate (source supports question or not), not as the generator.

### F6. LLMQuoter: fine-tuned quote extractor lifts small-model accuracy
- Source: https://arxiv.org/html/2501.05554v1 (HTML opened; abstract at https://arxiv.org/abs/2501.05554). Authors: Bezerra and Weigang (Jan 2025).
- Method: a LLaMA 3.2 3B "quoter", LoRA fine-tuned for one epoch (60 steps, about 24M trainable parameters, about 5 min on one A100), with gold quotes produced by Gemini Pro 1.5. The quotes are then passed to the answering model ("quote-first-then-answer").
- Data: HotpotQA, a random 15,000-sample subset; 600 held out as test, 14,400 for train/val.
- Quoter quality (Table 3): before fine-tuning recall 48.3 / precision 43.6 / F1 41.3; after fine-tuning recall 68.0 / precision 71.0 / F1 69.1.
- Semantic accuracy, full context vs extracted quotes (Table 4):
  - LLaMA 1B: 24.4% -> 62.2% (+37.8)
  - LLaMA 3B: 57.7% -> 83.0% (+25.3)
  - GPT-3.5 Turbo: 75.8% -> 88.5% (+12.7)
- The abstract says "over 20-point accuracy gains across both small and large language models". That is true for the 1B and 3B rows, not for GPT-3.5 (+12.7). Quote the table, not the abstract.
- Reference (Table 5): LLaMA2-7B full context 26.43%; RAFT (LLaMA2-7B) 35.28% on HotpotQA.
- Caveats: the judge is an LLM (the paper says "GPT-4.0", run through DSPy) scoring semantic overlap and answer correctness, so the same judge-noise problem BOAR measured applies. The answering-side numbers are not span-level. Code: github.com/yurifacanha/LLMQuoter; no software licence stated (only arXiv's non-exclusive licence on the paper).
- Read for BOAR: this is the strongest quantified "quote first" result for small models I found. BOAR's prompt-only "quote the source sentence first" failed because the model paraphrases. LLMQuoter's gain comes from a fine-tuned extractor, not from the prompt. BOAR's earlier fine-tune line was closed for the 4B (no LoRA); a quoter at 1-3B on the phone is a separate question, untested here.

### F7. Choose Your QA Model Wisely (Luo et al. 2022): extractive vs generative readers
- Source: https://arxiv.org/abs/2203.07522 (abstract opened; numbers not in the abstract). Venue: SpanLP 2022.
- Quote (abstract): "generative readers do better on long context QA, while extractive readers do better on short context QA and generalize better out-of-domain"; "the T5 encoder turns out to be a strong extractive reader and outperforms the standard choice of encoder-only PrLMs."
- Numbers: not retrieved (full paper at https://arxiv.org/pdf/2203.07522 not opened). Models: T5 and BART as generative readers, nine pretrained models in total (not listed in the abstract).
- Read for BOAR: BOAR's context is short (2-5 chunks, 350-token cap after the 1.7B tests). The finding says extractive should be competitive exactly in that regime. Old (2022) and on T5/BART-era models, so it needs a re-test on current encoders.

### F8. RoseRAG: small generative RAG model with preference training (non-extractive, for contrast)
- Source: https://arxiv.org/html/2502.10993v1 (HTML opened; Findings of ACL 2025; Liu et al.).
- Models: Qwen2.5-1.5B-Instruct, Llama-3.2-1B-Instruct, gemma-2-2b-it.
- Qwen2.5-1.5B results (Table 1): HotpotQA EM/F1 34.8/44.8 (RoseRAG) vs 31.2/39.6 (InstructRAG); 2WikiMultiHopQA EM/F1 31.6/35.0 vs 23.6/26.9; StrategyQA acc 59.8 vs 59.4 (BlendFilter).
- Answer format: generative with reasoning ("So the answer is..."), not extractive. No code or licence stated.
- Read for BOAR: a training-based fix (rejection sampling plus margin-aware preference optimization) for a 1.5B reader, reporting +3.6 EM on HotpotQA and +8 EM on 2Wiki over the best baseline. It is a fine-tune of the generator, which BOAR's closed list does not cover explicitly, but BOAR's DATA line was closed for the 4B. Not load-bearing.

### F9. CoCoLex: confidence-guided copy-based decoding (decoding-time copy)
- Source: https://arxiv.org/abs/2508.05534 (abstract opened; Aug 2025).
- Method: blends the model's own vocabulary distribution with a distribution from copying context tokens, weighted by model confidence. Claimed to beat context-aware decoding methods "particularly in long-form generation tasks".
- Numbers, models and code licence: not in the abstract page. Evaluation on "five legal benchmarks" (names not given).
- Read for BOAR: the closest published copy-mechanism method in 2025. It is a decoding-time change in the 1.7B's sampler, which is feasible in llama.cpp only with custom logit code. Not measured here.

### F10. Lazy-k decoding: constrained decoding helps smaller models (IE, token classification)
- Source: https://aclanthology.org/2023.emnlp-main.416 (opened; EMNLP 2023, Hemmer et al.).
- Quote: constrained decoding "can significantly improve the models' performances, especially when using smaller models". No numbers on the page.
- Read for BOAR: a token-classification method, not QA. The point is only that constraints help small models more. Not load-bearing.

### F11. Answer-sentence selection: selector-only fails when all candidates are weak (snippet only)
- Source: https://arxiv.org/pdf/2106.00955 (snippet only, NOT opened; "Answer Generation for Retrieval-based QA Systems", Findings of ACL 2021).
- Snippet: selector-only models fail when every retrieved candidate is weak; a seq2seq model that generates from the top candidates gained "up to 32 points" on three English datasets.
- Read for BOAR: this is the same failure mode BOAR sees (wrong top passages -> confident wrong answer). Extractive selection cannot abstain on its own unless it has a no-answer score, which is a reason to use a SQuAD 2.0-style reader rather than a plain sentence ranker.
- Verify before quoting the 32-point figure.

### F12. Adobe SlimLM: small models for on-device document QA (snippet only)
- Source: https://research.adobe.com/publication/slimlm-an-efficient-small-language-model-for-on-device-document-assistance (search snippet only, NOT opened). ACL 2025 system demo.
- Snippet: SLMs tested from 125M to 7B on a Samsung Galaxy S24, for question answering, summarization and suggestion. Generative, so not an extractive reader.
- Read for BOAR: a published on-device document-QA data point at the same size class (125M) that claims phone feasibility. Worth opening for the latency table and the QA score; not opened here.

### F13. BERT-base on phone CPU latency (snippet only)
- Source: https://arxiv.org/pdf/2106.00526 (snippet only, NOT opened).
- Snippet: BERT-Base on TFLite CPU about 352 ms on the phone; a compressed model about 5.2x faster on CPU with 0.5-2% accuracy drop.
- Read for BOAR: a scale reference, not a DeBERTa-xsmall number. A 22M-backbone DeBERTa-xsmall is far smaller than BERT-base (110M), so its latency is lower, but no measured value was found. The BOAR team would need its own measurement with ONNX Runtime or LiteRT on the Pixel 8a.

---

## Searched and found nothing useful (or only aggregator sites)

- "extractive QA small encoder on-device mobile 2025": returned mostly AI Indigo aggregator pages for MobileBERT and TinyRoBERTa, with no numbers. Not used as evidence.
- Answer-sentence selection (AS2) with small models and RAG in 2025: no 2025 AS2 paper surfaced. Only older AS2 work.
- Faithfulness papers from 2025 (Generate-but-Verify, IJCNLP 2025, https://aclanthology.org/2025.ijcnlp-long.56): on the search page only; not opened. These are verifiers, so not a reader.
- ModernBERT extractive QA fine-tunes with SQuAD 2.0 F1: none found.
- 2024-2026 comparison of extractive vs generative readers in RAG with 1-3B models: none found. The only controlled comparison I found is Luo et al. 2022.
- Span-constrained decoding (generation restricted to context spans) in a small model with QA numbers: none found. Closest: CoCoLex (F9), Lazy-k (F10), STOC-TOT vocabulary restriction (https://arxiv.org/pdf/2407.03687, search snippet only, not opened).
- ONNX Runtime or LiteRT int8 latency for MiniLM or DeBERTa-xsmall on Android: none found with numbers. This is the largest gap for the phone plan.
- Licence checks for Qwen3-1.7B, the knowledge-pack corpora or any reader pairing were out of scope.

## Search-coverage caveats

- Most arXiv abstract pages returned no tables. F1 (MobileBERT) and F7 (Luo) are abstract-level.
- Two WebFetch calls returned 404 or an abstract only (aclanthology preview URL for RoseRAG; Luo PDF not opened).
- The LLMQuoter judge is named "GPT-4.0" in the paper. Treat judge details as the paper's claim.
- F3 and F11 to F13 are snippet-only. Do not quote their numbers without opening the source.

---

## What this means for BOAR

Mapping to BOAR's walls (reading wall; judge noise; prompt fixes failed):

1. Span or sentence readers sidestep the reading wall. The output is the cited passage, not a paraphrase, so the 1.7B does not have to "use" the text. The cost is that spans lose multi-sentence answers (e.g. list-style Wikivoyage questions). A hybrid is the natural test: encoder picks the answer-bearing sentence(s) and the 1.7B only composes around them, or the encoder gates and the 1.7B answers as now.
2. Native no-answer output maps onto BOAR's routing. A SQuAD 2.0-style reader gives a source-supports-question score, which can drive the "answer from memory under warning" branch with a number instead of the model's own confidence. The 28% confident-error rate is the target. The grounding result (F5) supports an encoder gate at a fraction of the cost of a 1-3B LLM.
3. Scoring: span readers can be scored deterministically (containment of the gold answer string, EM/F1 on answer spans) without an LLM judge. That removes the Haiku re-judging noise (13 of 37 items changed) for this arm. Keep the Haiku judge only for the generative composition arm.
4. Licences: DeBERTa-v3-xsmall base (MIT) and ModernBERT (Apache-2.0) are redistributable. The community squad2 fine-tune is cc-by-4.0 and the MobileBERT checkpoint is Apache-2.0 but pretraining-only. Check each fine-tune's own card before shipping.
5. Latency is the open risk. No on-device QA latency for DeBERTa-xsmall was found. The Pixel 8a test must come first, before any accuracy work.

### Proposed next steps (for the coordinator to decide; not executed)

- Step 1 (no phone needed, ~1 h): run microsoft/deberta-v3-xsmall fine-tuned on SQuAD 2.0 (use a checkpoint with a clear licence and an official eval script) on the 180 self-test items, over the top-k pack chunks already in the retrieval replay. Measure gold-answer containment and no-answer accuracy. Compare to the 1.7B's containment on the same chunks. Deterministic scoring, no judge.
- Step 2 (phone): export to ONNX int8 or LiteRT and time it on the Pixel 8a for a 384-token input x k chunks. Decision rule: total reader + gate latency under the 1.7B decode budget.
- Step 3 (only if Step 1 shows the encoder finds the answer-bearing chunk): LLMQuoter-style quoter at 1B-3B with a LoRA fine-tune on HotpotQA-style data, vs the prompt-only baseline. Note this is a new fine-tune line on a different model size than the closed 4B DATA line; log it as such.
- Do not re-propose the closed list (cross-encoder rerank, HyDE, PRAG, DoLa, verifier best-of-N, GraphRAG, text-to-SQL). Note that DeBERTa-style cross-encoders are a reranker; the gate use here (no-answer score on the top passage) is a different job from the closed rerank line, but the same model family. Say so in the QUEUE row to avoid a duplicate.

UNKNOWN:
- Parameter count and int8 file size for MobileBERT and DeBERTa-v3-xsmall in a phone format.
- Actual Tensor G3 latency for an encoder reader of any size (none published in what I found).
- Whether Luo et al.'s extractive advantage on short contexts holds for 2025 encoders (the paper used T5/BART-era models).
- Exact numbers in DeBERTaV3 (F3) and the answer-sentence selection paper (F11): snippet only.
