# OCC-RAG-1.7B: ecosystem notes (angle: who, licence, format, reception, reproduction)

Date of research: 2026-10-20. Method: WebSearch (standard and extended) plus WebFetch on primary pages (HF model, GGUF, ONNX, org, collection, GitHub repo and issues, arXiv abstract, Qwen base card, AIRI/Sber news). No weights downloaded. Claims are copied from the pages or marked as paraphrase. WebFetch returns model summaries, so quoted phrases are short and checked against the fetch text, not against raw HTML.

## 1. Who is behind it

- Org: `occ-ai` on Hugging Face, typed "Non-profit", no description, no website/GitHub/X links. Six HF members: Andrey Galichin, Vasily Konovalov, Dmitrii Tarasov, Daria Pugacheva, Alexander Gambashidze, Maksim (handle mks-logic). Source: https://huggingface.co/occ-ai
- Paper: arXiv 2606.00683, "OCC-RAG: Optimal Cognitive Core for Faithful Question Answering", v1 submitted 30 May 2026. Ten authors: Maksim Savkin, Mikhail Goncharov, Alexander Gambashidze, Alla Chepurova, Dmitrii Tarasov, Nikita Andriianov, Daria Pugacheva, Vasily Konovalov, Andrey Galichin, Ivan Oseledets. Affiliations not on the abstract page. Source: https://arxiv.org/abs/2606.00683
- Institutional attribution (Russian press, kod.ru, dated 3 Jun 2026, at SPIEF): AIRI Institute is the developer, Sber gives support, and Ivan Oseledets (AIRI General Director) announced it. The article's figures are AIRI's own claims: 1.5-2x faster than LLM-based solutions, 1.5x fewer tokens, 0.6B and 1.7B sizes, open source, "can run on a laptop or smartphone". Stated next step: an "agentic core" that searches for missing context. Source: https://kod.ru/airi-sber-occ-rag-kompaktnye-ii-modeli
- Implication: the lab is AIRI/Sber-linked, which is a credible research group, but the org on HF is small and has no public blog, announcements or prior models found in this search. No "prior work" by this org was found beyond the OCC family.

## 2. Licence (load-bearing)

- HF model card for `occ-ai/OCC-RAG-1.7B`: licence MIT (metadata). Base model: Qwen/Qwen3-1.7B-Base. Source: https://huggingface.co/occ-ai/OCC-RAG-1.7B
- GGUF and ONNX repos: licence MIT. The ONNX card says "Released under the MIT License," inherited from the base model. Sources: https://huggingface.co/occ-ai/OCC-RAG-1.7B-GGUF and https://huggingface.co/occ-ai/OCC-RAG-1.7B-ONNX
- GitHub `optimal-cognitive-core/OCC-RAG`: MIT per repo sidebar. Source: https://github.com/optimal-cognitive-core/OCC-RAG
- Base model licence: `Qwen/Qwen3-1.7B-Base` shows `License: apache-2.0`. Source: https://huggingface.co/Qwen/Qwen3-1.7B-Base
- arXiv listing: "License: CC BY 4.0" applies to the paper, not the weights. Source: https://arxiv.org/abs/2606.00683
- Caveat: the card's phrase "inherited from the base model" is not how Apache-2.0 works. A downstream fine-tune relicensed under MIT does not change the base licence's obligations (attribution and NOTICE). For an app redistributing the GGUF, the safe reading is MIT for the fine-tune plus Apache-2.0 terms for the base. This is a reading of the licences, not legal advice; it needs a check before the app ships.
- Third-party listings (Featherless, search snippets) also say MIT. Not independent confirmation.

## 3. Output format and prompt contract (load-bearing)

- Input: question wrapped in query tokens; each source wrapped in source tokens with an ID. The chat template accepts a `documents=` argument that builds these. Source: https://huggingface.co/occ-ai/OCC-RAG-1.7B and the GitHub README (`documents=` kwarg; vLLM via `chat_template_kwargs`).
- Output: five delimited sections: query analysis, source analysis, reasoning, status (ANSWERABLE or UNANSWERABLE), answer. The final answer sits between answer tags. Abstention prints "Not enough information". Sources cited as literal quotes/IDs inside the trace.
- Decoding: greedy (`do_sample=False`, `--temp 0`) recommended; set in `generation_config.json`. Keep `skip_special_tokens=False` to parse structure. Stop token IDs in the ONNX card: 151643, 151645, 151683.
- Implications for BOAR:
  - BOAR's contract is 2-5 sentences with [n] citations. This model emits a long structured trace before the answer. Its token cost on a phone is not measured here; AIRI claims fewer tokens than LLM baselines, with no method given.
  - A parser or a post-processing step is needed to strip the trace and map source IDs to BOAR's [n] numbering.
  - The `documents=` template is a Jinja-level feature. Whether llama.cpp `--jinja` (GGUF) and Ollama pass a structured documents list, or whether BOAR must build the special tokens by hand, is NOT verified here. The GGUF card only shows `llama-cli -hf ... -p "Hello" -no-cnv` and the Ollama `run` example, with no document example.
  - The status token (ANSWERABLE / UNANSWERABLE) is a usable signal for BOAR's no-source fallback, but the model is trained to refuse when context is insufficient, which may conflict with BOAR's "answer from memory under a warning" path.

## 4. Scope limits (stated by the card)

- "Context-grounded only": trained to answer from supplied sources and ignore parametric knowledge, so it is "not a general-purpose chat model". This is the main fit question for BOAR, where 20 of 27 confident errors had no relevant source (absent knowledge). Source: https://huggingface.co/occ-ai/OCC-RAG-1.7B
- Reasoning depth capped at three hops in training and evaluation; longer chains out of distribution. Same source.

## 5. Reported benchmark numbers vs the Qwen3-1.7B think baseline (load-bearing)

The HF card table compares against Qwen3-1.7B (think) and Qwen3-4B (think), not the no-think row used in the brief. Copied as printed:

| Model | HotpotQA In-Acc | MuSiQue In-Acc | TAT-QA F1 | ConFiQA In-Acc | ConFiQA M_R (lower better) | MuSiQue-Un R-Acc |
|---|---|---|---|---|---|---|
| gemma-3-4b-it | 55.8 | 30.1 | 65.3 | 69.8 | 8.9 | 55.8 |
| Qwen3-1.7B (think) | 60.9 | 30.7 | 74.8 | 70.4 | 8.3 | 82.8 |
| Qwen3-4B (think) | 67.1 | 41.5 | 79.1 | 74.1 | 7.5 | 84.0 |
| Pleias-RAG-1.2B | 48.5 | 15.0 | 8.4 | 37.3 | 25.3 | 21.9 |
| OCC-RAG-0.6B | 57.6 | 36.6 | 75.0 | 79.9 | 5.2 | 86.9 |
| OCC-RAG-1.7B | 60.9 | 38.2 | 81.0 | 81.4 | 5.0 | 87.2 |

Source: https://huggingface.co/occ-ai/OCC-RAG-1.7B (WebFetch summary of the table; verify against the paper's Table 2 before quoting).

Reading against the think baseline: HotpotQA equal (60.9 vs 60.9); MuSiQue +7.5; TAT-QA +6.2; ConFiQA +11.0; M_R 8.3 to 5.0; MuSiQue-Un +4.4. The brief's no-think figures (HotpotQA 47.7 to 60.9, MuSiQue 20.1 to 38.2, MuSiQue-Un refusal 54.7 to 87.2) are from the paper, not the card; the no-think refusal figure (54.7) appeared in a search snippet, not in a page I fetched, so it stays unverified here. The gap to think mode is much smaller than the no-think gap, which is the comparison that matters for BOAR (BOAR runs the 1.7B with thinking off, but the card and the paper pick the baseline in its favour).

- Note: the card calls OCC-RAG-1.7B the best faithfulness "across all evaluated scales (up to 32B)". Only the card is the source for this; the paper's full table was not fetched.

## 6. Packaging and sizes

- GGUF (`occ-ai/OCC-RAG-1.7B-GGUF`, all from BF16): Q4_0 1.05 GB; Q4_K_M 1.11 GB ("recommended balance"); Q5_K_M 1.26 GB; Q6_K 1.42 GB; Q8_0 1.83 GB ("near-lossless"); F16 3.45 GB; BF16 3.45 GB. Greedy `--temp 0`. Chat template embedded; apply with `--jinja`. Ollama: `ollama run hf.co/occ-ai/OCC-RAG-1.7B-GGUF:Q4_K_M`. Source: https://huggingface.co/occ-ai/OCC-RAG-1.7B-GGUF
- 0.6B GGUF exists (https://huggingface.co/occ-ai/OCC-RAG-0.6B-GGUF). Not fetched in detail.
- ONNX (`occ-ai/OCC-RAG-1.7B-ONNX`): fp16 ~4.0 GB; q8 ~3.2 GB; q4f32 ~2.3 GB; q4f16 ~1.6 GB (recommended for WebGPU); q4 ~1.3 GB (smallest). Runs under onnxruntime CPU with manual KV-cache loop, or transformers.js with WebGPU. Source: https://huggingface.co/occ-ai/OCC-RAG-1.7B-ONNX
- Quantisation guidance from the GGUF and ONNX cards: Q4 variants "lose some quality"; Q6_K or Q8_0 (or fp16/q8 ONNX) when accuracy matters most. No quantised benchmark numbers published. BOAR's current Q4_K_M would be the card's trade-off case, and the quality cost is unmeasured.
- Weights are above the 100 MB rule (do not download; another agent handles weights).
- Serving: transformers >= 5.5.1, vllm >= 0.19.1, sglang >= 0.5.11. Card claims it "can run on constrained hardware, including CPU-based desktops". Source: HF model card.
- Param count display: HF shows 2B (safetensors metadata; Qwen base is 1.7B with 1.4B non-embedding). Not a model difference.

## 7. Reception, traction, issues

- HF 1.7B: 1,496 downloads last month, 16 likes (page). GGUF 1.7B: 556 downloads last month, 0 likes. ONNX: unlabelled counts of 11. Collection `OCC-RAG` lists 6 models, no datasets. Sources: model pages above.
- GitHub `optimal-cognitive-core/OCC-RAG`: 48 stars, 0 forks, 2 open issues, 0 closed. Source: GitHub page (WebFetch summary).
  - Issue #2 (Jun 4, 2026): "Release OCC-RAG Synthetic Corpus on Hugging Face". Open. Corpus is NOT public. Implies the 3.25M-QA training set cannot be inspected or reused.
  - Issue #1 (Jun 3, 2026): related-work share, "Teaching Large Language Models to Maintain Contextual Faithfulness via Synthetic Tasks and Reinforcement Learning". Title only.
- No format breaks, hallucination, refusal, repetition or quantisation complaints found in issues, HF discussions or search results. The HF discussions page was not fetched separately; the card's collection page showed no discussion data.
- Search for Reddit, Hacker News and X threads returned none. Absence of threads is weak evidence given the paper is 4.5 months old and niche.

## 8. Independent reproduction and review

- No independent reproduction or third-party evaluation found in any search (standard or extended).
- A Pith machine-generated review (https://pith.science/paper/2606.00683) notes: no error bars, no variance across runs, no per-question-type breakdown, and missing method details. It also includes what appear to be author replies saying Table 2 will be revised and an appendix with standard deviation over three training/evaluation runs. Not confirmed as published; the review is automated.
- An unaffiliated summary (https://researchpapers.dev/en/papers/occ-rag-faithful-qa/) and hyper.ai mirrors repeat the authors' numbers.
- Implication: every number in section 5 is single-source (authors), with no CI. For BOAR the paper numbers cannot be cited as independent.

## 9. Unresolved / not checked

- Whether the paper's full Table 2 matches the card summary (only the card table was read).
- Whether any runtime (llama.cpp, Ollama, mlx, LiteRT) passes the structured `documents` list through the embedded template. Needs a local test on the mini, not web research.
- No-think baselines (the brief's source) were not read in the paper body.
- Licence legal reading (MIT over Apache-2.0 base) needs a check.
- Hallucination rate on BOAR-type absent-knowledge questions: unmeasured in any source found.

## 10. Adoption signals (summary for BOAR)

- For: research-grade, citation-style grounded output; GGUF at 1.11 GB (Q4_K_M) fits the 8 GB phone; MIT on the fine-tune; a 0.6B sibling for speed; the paper's claims target exactly "answer from packs, cite, abstain".
- Against: output is a long five-section trace, not 2-5 sentences; design refuses parametric answers (conflicts with BOAR's memory fallback); gains over think-mode Qwen are real but modest on HotpotQA (0); corpus unreleased; no independent reproduction; community traction is small; quantised quality unmeasured.

## Sources (all fetched or searched in this session)

- https://huggingface.co/occ-ai/OCC-RAG-1.7B
- https://huggingface.co/occ-ai/OCC-RAG-1.7B-GGUF
- https://huggingface.co/occ-ai/OCC-RAG-1.7B-ONNX
- https://huggingface.co/occ-ai/OCC-RAG-0.6B-GGUF
- https://huggingface.co/occ-ai (org)
- https://huggingface.co/collections/occ-ai/occ-rag
- https://huggingface.co/papers/2606.00683
- https://huggingface.co/Qwen/Qwen3-1.7B-Base
- https://github.com/optimal-cognitive-core/OCC-RAG
- https://github.com/optimal-cognitive-core/OCC-RAG/issues
- https://arxiv.org/abs/2606.00683
- https://arxiv.org/html/2606.00683v1 (listed in search; not fetched)
- https://kod.ru/airi-sber-occ-rag-kompaktnye-ii-modeli
- https://pith.science/paper/2606.00683
- https://researchpapers.dev/en/papers/occ-rag-faithful-qa/
- https://featherless.ai/models/occ-ai/OCC-RAG-1.7B (licence claim, search snippet)
