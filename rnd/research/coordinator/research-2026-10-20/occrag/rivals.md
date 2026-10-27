# OCC-RAG-1.7B rivals (same-size grounded RAG with citations and abstention)

Date: 2026-10-20. Scope: models <= 3B with permissive licences that compete with OCC-RAG-1.7B for grounded QA, citations and abstention. Weights were not downloaded (100 MB rule). All numbers below are copied from model cards or the OCC-RAG paper; none are independently replicated.

## TL;DR

- OCC-RAG-1.7B (MIT on HF) is the only candidate with a numeric head-to-head table against Qwen3-1.7B on the metrics we care about. The numbers are self-reported by the authors.
- Pleias-RAG-1B (Apache-2.0, 1.2B) is the main same-size alternative with a GGUF. In the OCC paper's own table it scores far below OCC-RAG-1.7B on every metric.
- LFM2-1.2B-RAG is deprecated by Liquid AI in favour of LFM2.5-1.2B-Instruct plus retrieval models. No numbers were published. Do not adopt.
- OCC-RAG-0.6B (MIT, GGUF quantizations on HF) is the fallback if RAM or speed binds. It loses to 1.7B on every row.
- No 2026 model was found that beats OCC-RAG-1.7B on these metrics. This is an absence of evidence from limited search, not proof.
- Checker options (MiniCheck family) are verifiers, not generators. The Bespoke variant is CC BY-NC 4.0 and excluded. The T5 licence was not verified.

## Findings

### F1. OCC-RAG-1.7B: self-reported numbers and the only numeric Qwen3-1.7B comparison

- Source: https://arxiv.org/abs/2606.00683 (HTML: https://arxiv.org/html/2606.00683), HF card https://huggingface.co/occ-ai/OCC-RAG-1.7B
- Paper: "OCC-RAG: Optimal Cognitive Core for Faithful Question Answering", Savkin et al., submitted 30 May 2026. Quote: "The models produce structured reasoning traces with source citations grounded in literal quotes from the context."
- Table 2 values (copied from the paper via the reader):

| Model | HotpotQA In-Acc | MuSiQue In-Acc | TAT-QA F1 | ConFiQA In-Acc | ConFiQA MR (lower better) | MuSiQue-Un R-Acc |
|---|---|---|---|---|---|---|
| OCC-RAG-1.7B | 60.9 | 38.2 | 81.0 | 81.4 | 5.0 | 87.2 |
| Qwen3-1.7B (no-think) | 47.7 | 20.1 | 74.4 | 64.8 | 12.7 | 54.7 |
| Qwen3-1.7B (think) | 60.9 | 30.7 | 74.8 | 70.4 | 8.3 | 82.8 |

- The think-mode row for HotpotQA is equal to OCC (60.9 vs 60.9). The advantage is concentrated in MuSiQue, ConFiQA, MR and refusal, not HotpotQA.
- Metric definitions (quoted): In-Acc is "the gold answer appears as a substring of the prediction". R-Acc is "the fraction of predictions that contain" "Not enough information".
- Implication for BOAR: the claimed refusal and MR gains matter for our "no source, answer from memory" case, but the metric is a substring match and the rubric is not our LLM-judge rubric. Re-measure on our own dev items before any claim.

### F2. OCC-RAG-1.7B licence is inconsistent across sources

- HF tag: MIT (also reported as MIT by Featherless and Friendli listings).
- arXiv page navigation displays "License: CC BY 4.0", which is the paper's licence, not necessarily the weights'.
- Implication: MIT on the model card is the relevant licence for weights. Confirm on the HF LICENSE file before shipping. Low risk, but it is a known ambiguity.

### F3. OCC-RAG-1.7B model card limits and metadata

- The card says training and evaluation are capped at three-hop reasoning; longer chains are out of distribution (reported via search summary of the card).
- HF metadata says "2B params" in the Safetensors panel while the description says 1.7B. Not explained.
- The model card points to "Browse Quantizations" with three quantized derivatives, but no official GGUF repo was named. Third-party GGUFs exist (not verified for provenance).
- Prompt format (from card): question in `<|query_start|> ... <|query_end|>`, sources in `<|source_start|><|source_id|>N ... <|source_end|>`. Output has five delimited sections ending in `ANSWERABLE` or `UNANSWERABLE`. Greedy decoding recommended. This format is not the chat format BOAR uses and would need a dedicated prompt builder.

### F4. OCC-RAG-0.6B (the smaller OCC variant)

- Source: https://huggingface.co/occ-ai/OCC-RAG-0.6B
- Licence tag: MIT. 0.6B params, BF16. Quantizations: three derivatives, "Browse Quantizations" for llama.cpp, Ollama, LM Studio (no GGUF named officially).
- Numbers from the OCC-RAG-1.7B card table: HotpotQA 57.6, MuSiQue 36.6, TAT-QA 75.0, ConFiQA 79.9, ConFiQA MR 5.2, MuSiQue-Un R-Acc 86.9.
- Implication: 0.6B is within 1 to 4 points of 1.7B on the self-reported table and is the memory and speed fallback. Still a self-reported number. Note it is also a Qwen3 mid-train (same family as the main model).

### F5. Pleias-RAG-1B (and 350M): licence, GGUF, and the OCC paper's comparison

- Sources: https://huggingface.co/PleIAs/Pleias-RAG-1B (licence tag apache-2.0), https://huggingface.co/PleIAs/Pleias-RAG-1b-gguf (licence tag apache-2.0), paper https://arxiv.org/pdf/2504.18225
- Pleias-RAG-1B: "1.2 billion parameters" in text, Hub metadata "1B params". Languages listed on the page: French, German, Italian, Spanish, Polish, Latin, Portuguese (Hub says 5 languages; page lists 7). Context length not stated on the card.
- Pleias-RAG-1B GGUF: the card says "This version is unquantized but, thanks to the small size of the original model, still runnable on most CPU infrastructure". Runtime quoted: "about 20 seconds for a complex generation including reasoning traces on 8g RAM and below".
- The official card gives no numeric benchmark scores (figures only). It says it can "outperform most SLMs (4 billion parameters and below)" on HotPotQA and 2wiki and is "competitive with standard 7-8b models".
- OCC paper's table (its own run of Pleias-RAG-1.2B): HotpotQA 48.5, MuSiQue 15.0, TAT-QA 8.4, ConFiQA 37.3, MR 25.3, MuSiQue-Un R-Acc 21.9. The paper also says the 1.7B "significantly outperform[s] other specialized RAG models like Pleias-RAG on MuSiQue".
- Implication: Pleias-RAG-1B has the cleanest Apache-2.0 licence and an unquantized GGUF, but the only numbers available (from a competitor's paper) put it far below OCC. Not a replacement candidate unless our own dev items say otherwise. The 20 s / 8 GB runtime claim is vendor-stated and is on a desktop CPU, not a phone.

### F6. Pleias-RAG-350M

- Source: https://huggingface.co/PleIAs/Pleias-RAG-350M. Licence apache-2.0, 0.4B params BF16. No numeric benchmark in text (images only). Card says it "outperform[s] most SLMs (4 billion parameters and below)" on HotPotQA and 2wiki.
- Implication: smallest licence-clean option, but no numbers that can be compared. Not evaluated against OCC.

### F7. LFM2-1.2B-RAG: deprecated, no published numbers

- Sources: https://docs.liquid.ai/lfm/models/lfm2-1.2b-rag.md (search summary), https://huggingface.co/LiquidAI/LFM2-1.2B-RAG (fetched card).
- Liquid's docs label the model deprecated and point users to LFM2.5-1.2B-Instruct for generation, paired with LFM2.5-Embedding-350M or LFM2.5-ColBERT-350M for retrieval.
- HF licence tag: "lfm1.0" (the LFM Open License). Full terms not on the card; commercial/redistribution terms were not verified and would need a legal read before any app use.
- Parameters: "1B params" in Safetensors metadata vs "1.2B" in the name. Context: 32K per a third-party listing, not stated on the card.
- Template: ChatML-like; the user turn starts "Use the following context to answer questions:", followed by the document text. Greedy recommended.
- No benchmark numbers on the card. No official LFM2-1.2B-RAG GGUF found (LiquidAI/LFM2-1.2B-GGUF is the base model, not the RAG tune).
- Implication: do not adopt. Deprecated, licence needs legal review, no evidence.

### F8. B1ade-1B (Amazon-authored minimalist RAG model)

- Sources: paper https://www.alphaxiv.org/abs/2607.27506, HF https://huggingface.co/w601sxs/b1ade-1b (tree page), bf16 repo https://huggingface.co/w601sxs/b1ade-1b-bf16/tree/main.
- Reported: cites retrieved passages in 42.4% of responses; "exceeding the attribution rate of its training distribution by 5.5 percentage points"; trained with GRPO with rewards on answer similarity only. PopQA 81.82%, PubMedQA 65.8%, FEVER 51.09%.
- Licence: MIT on the HF listing (per search result). Architecture gpt_neox, 1B. Not verified on card page.
- Caveats: the paper is dated 2026-07-29 while the HF file history shows commits about a year earlier. The metrics (PopQA, PubMedQA, FEVER) are not HotpotQA/MuSiQue/ConFiQA, so there is no direct comparison to OCC. Citation rate is not citation accuracy.
- Implication: different axis (answer similarity, low attribution). Not a head-to-head rival on OCC's metrics. Worth a follow-up read of the paper, not an adoption candidate on current evidence.

### F9. lewisdog/qwen3-1.7b-cogs-ask: same base as BOAR main model, LoRA only

- Source: https://huggingface.co/lewisdog/qwen3-1.7b-cogs-ask-lora. Licence apache-2.0. Base loaded in code: Qwen/Qwen3-1.7B (the model tree is inconsistent, also lists Qwen3-1.7B-Base).
- Training data: "cogs distill ask pairs (475 base + abstentions oversampled 3x)".
- Eval (63-record valid set, temp 0, repetition_penalty 1.1): JSON parse 100%, decompose non-empty 100%, "synthesize citation-validity: 77% (→ ~90% with the prefix-repair below)", "abstention preserved: 100% · false-abstention: 4%", eval loss 1.906 → 0.758.
- Implication: the only Qwen3-1.7B-based citation/abstain tune found, and it is an adapter (small download). Its output is JSON with sub-question decomposition, a different output shape from BOAR's 2-5 sentence answers with [n] citations. The 63-record eval is too small to compare to OCC's table. Good candidate for a LoRA-style experiment, not for a number claim.

### F10. Bespoke-MiniCheck-7B: excluded by licence, and wrong size

- Source: https://huggingface.co/bespokelabs/Bespoke-MiniCheck-7B. Licence: "This work is licensed under CC BY-NC 4.0." Commercial licensing via [email removed]. 8B params, base internlm2_5-7b-chat. The card's score table is an image; no numbers in text.
- Implication: excluded (NC licence and 8B).

### F11. MiniCheck family (verifier, not generator)

- Source: https://arxiv.org/pdf/2404.10774 (EMNLP 2024, Tang et al.). MiniCheck-FT5 has 770M params (Flan-T5 base), reported to reach GPT-4 accuracy on LLM-AggreFact. Released code under github Liyan06/MiniCheck.
- Licence for the released T5 checkpoints and code was not verified (search gave no licence text). Must be checked on the HF/GitHub LICENSE file before use.
- Implication: useful as an optional grounding checker on [n] citations (verify each quote is supported), not as the generator. Would need a 770M-class model on device; adds latency. Hold unless the answer-level citation check is needed.

### F12. Larger models in the OCC table (context, not rivals at <= 3B)

- From the OCC-RAG-0.6B card table (the same paper table): gemma-3-4b-it: HotpotQA 55.8, MuSiQue 30.1, TAT-QA 65.3, ConFiQA 69.8, MR 8.9, MuSiQue-Un 55.8. Qwen3-4B (think): 67.1, 41.5, 79.1, 74.1, 7.5, 84.0.
- Implication: at 4B, Qwen3-4B-think beats OCC-RAG-1.7B on HotpotQA (67.1 vs 60.9) and MuSiQue (41.5 vs 38.2). OCC-RAG-1.7B is ahead on TAT-QA (81.0 vs 79.1), ConFiQA (81.4 vs 74.1), ConFiQA MR (5.0 vs 7.5, lower is better) and MuSiQue-Un refusal (87.2 vs 84.0). Gemma 3 4B is clearly below OCC on refusal (55.8 vs 87.2) and HotpotQA (55.8 vs 60.9). The 4B tier is not allowed on the 8 GB phone, so this only sets a ceiling for what a bigger model does on the same metrics.

### F13. No newer model found beating OCC-RAG-1.7B

- Searches (standard and extended) for 2026 small grounded-RAG models with citations surfaced only OCC-RAG, Pleias-RAG, the cogs LoRA and older generic papers (RAG-Instruct, R3-RAG, RAGRouter-Bench, none with a same-metric table at <= 3B).
- Implication: no evidence of a newer same-size model beating OCC on its own table. Limited search, extended mode used once. Re-check before the 10-31 decision date.

## Head-to-head summary (copied numbers only)

| Model | Licence | Params | GGUF | HotpotQA | MuSiQue | TAT-QA | ConFiQA | MR | MuSiQue-Un | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| OCC-RAG-1.7B | MIT (paper CC BY 4.0) | 1.7B | 3rd-party via quantizations | 60.9 | 38.2 | 81.0 | 81.4 | 5.0 | 87.2 | self, OCC paper |
| OCC-RAG-0.6B | MIT | 0.6B | 3rd-party via quantizations | 57.6 | 36.6 | 75.0 | 79.9 | 5.2 | 86.9 | self, OCC card |
| Qwen3-1.7B (think) | Apache-2.0 (base) | 1.7B | n/a | 60.9 | 30.7 | 74.8 | 70.4 | 8.3 | 82.8 | OCC paper |
| Qwen3-1.7B (no-think) | Apache-2.0 (base) | 1.7B | n/a | 47.7 | 20.1 | 74.4 | 64.8 | 12.7 | 54.7 | OCC paper |
| Pleias-RAG-1.2B | Apache-2.0 | 1.2B | official unquantized GGUF | 48.5 | 15.0 | 8.4 | 37.3 | 25.3 | 21.9 | OCC paper (run by OCC) |
| Qwen3-4B (think) | n/a | 4B | n/a | 67.1 | 41.5 | 79.1 | 74.1 | 7.5 | 84.0 | OCC-0.6B card |
| gemma-3-4b-it | n/a | 4B | n/a | 55.8 | 30.1 | 65.3 | 69.8 | 8.9 | 55.8 | OCC-0.6B card |
| LFM2-1.2B-RAG | lfm1.0 (not verified) | ~1.2B | none official | no numbers | | | | | | Liquid card; deprecated |
| B1ade-1B | MIT (listing) | 1B | n/a | not on same metrics | | | | | | paper, different benchmarks |

## Open questions (UNKNOWN)

- OCC-RAG-1.7B numbers are not independently replicated. The metric is substring In-Acc; our judge is an LLM vs frontier+web. We need our own run on the 180 dev items (not blind sets) before any claim.
- Actual OCC GGUF provenance: the card names no official GGUF repo. Need to confirm which third-party GGUF is faithful to the BF16 weights.
- Licence file for OCC-RAG weights (MIT per card) vs the paper's CC BY 4.0 display.
- LFM2-1.2B-RAG full licence terms (lfm1.0) for app redistribution.
- MiniCheck T5 checkpoint licence not verified.
- Context lengths for OCC-RAG and Pleias-RAG-1B not stated on the cards; the OCC prompt format uses special tokens and would need a dedicated builder.
- The 2026-07-29 B1ade paper date conflicts with the HF commit history.
