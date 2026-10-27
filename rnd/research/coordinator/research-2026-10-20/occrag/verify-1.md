# OCC-RAG-1.7B — adversarial verification, pass 1

TL;DR: 9 claims checked against primary sources fetched 2026-10-20 20:0x (arXiv PDF v1, HF cards/API/tree, chat_template.jinja, tokenizer.json, generation_config.json, GitHub LICENSE, upstream model cards). **Table 2 numbers are copied correctly.** Licence chain is MIT on every OCC repo + GitHub. The base is Apache-2.0. Every teacher used to make the data is Apache-2.0. The training corpus is built from English Wikipedia (CC BY-SA) and MuSiQue (CC BY 4.0) and is not released. Corrections: (a) the "inherited from the base model" phrase is in the GGUF/ONNX cards, not the main card, and it is wrong, since the base is Apache-2.0; (b) DRAGOn contributed only a question taxonomy, not data; (c) `<|query_analysis_start|>` is part of the prompt, not a forced generated token, and `documents=` is not the only input path; (d) the training abstain examples have *partial* gold context, never zero context. Nothing in the paper measures behaviour when no sources are given.

Sources (all opened by this verifier):
- PDF: https://arxiv.org/pdf/2606.00683 (v1, 30 May 2026, 17 pp.; the abs page shows the CC BY 4.0 licence)
- HF: occ-ai/OCC-RAG-1.7B (README, API, chat_template.jinja, tokenizer.json, generation_config.json), -GGUF (README, tree API, `expand[]=gguf` metadata), -ONNX README, OCC-RAG-0.6B (+GGUF, ONNX) API
- GitHub: optimal-cognitive-core/OCC-RAG (LICENSE + API licence field)
- Upstream cards: Qwen/Qwen3-1.7B-Base, Qwen/Qwen3.5-27B, Qwen/Qwen3-4B, openai/gpt-oss-120b; StonyBrookNLP/musique LICENSE
- HF datasets by occ-ai: none (`/api/datasets?author=occ-ai` → `[]`)

## Verdict table

| # | Claim (short) | Status |
|---|---|---|
| 1 | Abstention policy conflicts with BOAR's no-source path | confirmed (with precision) |
| 2 | Table 2 gains vs Qwen3-1.7B | confirmed |
| 3 | Licence/provenance not cleared; LICENSE 404; paper silent on corpus/teacher terms | corrected |
| 4 | No latency/length numbers; trace likely long | confirmed (+ derived estimate) |
| 5 | All OCC repos MIT; GitHub MIT; paper CC BY 4.0; base not checked | corrected |
| 6 | GGUF sizes, date, embedded template | confirmed |
| 7 | Template details | corrected |
| 8 | Context-grounded only (card) | confirmed |
| 9 | MIT vs Apache-2.0 base, "inherited" phrase | confirmed (with precision) |

## Claim 1 — abstention vs BOAR no-source path — CONFIRMED

- README Limitations, verbatim: "Context-grounded only. The model is trained to answer from the supplied sources and to ignore parametric knowledge. It is not a general-purpose chat or knowledge model."
- Paper abstract: "faithful question answering (QA) grounded in the provided context ... while ignoring memorized knowledge." §3: every training instance has "the final answer (or 'Not enough information' for refusal cases)". Status section emits `ANSWERABLE`/`UNANSWERABLE` (§3.3).
- Precision 1: the quoted sentence "We instruct the model to output the phrase 'Not enough information'..." is from §5.1 (Refusal eval) and describes how *all* evaluated models were prompted on MuSiQue-Un. It is not a training statement. The training statement is the one in §3.
- Precision 2 (important): the abstain examples are built by giving a DeBERTa-SQuAD extractor "reduced subsets of the original gold contexts" (§3.2.3). Every training example therefore has sources, and refusals are partial-context cases. The paper never evaluates or trains a zero-source/closed-book input. If BOAR calls the template with no `documents`, it renders a plain user turn (out of distribution). Behaviour there is unknown, not "abstains".
- Numbers: 43k / 3.25M = **1.32 %** of pairs; by tokens 0.029B / ~8B ≈ **0.36 %** (Fig. 4).
- BOAR consequence: correct as stated. Only the has-source path is in scope.

## Claim 2 — Table 2 gains — CONFIRMED

Checked against Table 2 of the PDF row by row. Qwen3-1.7B non-think (think): HotpotQA 47.7 (60.9), MuSiQue 20.1 (30.7), TAT-QA F1 74.4 (74.8), ConFiQA In-Acc 64.8 (70.4), MR 12.7 (8.3), MuSiQue-Un R-Acc 54.7 (82.8). OCC-RAG-1.7B: 60.9 / 38.2 / 81.0 / 81.4 / 5.0 / 87.2. All match. The MR quote matches §5.2 verbatim.
Caveats the source states, which the claim should carry:
- Eval setting: HotpotQA/MuSiQue/MuSiQue-Un use **10 sources with the gold passages included** plus distractors. TAT-QA keeps only span/multi-span questions (arithmetic and counting are dropped). ConFiQA uses counterfactual Wikidata-triple contexts with 1 source and averages the QA/MR/MC subsets. These are mostly Wikipedia-style extractive tasks with short span answers, not 2–5-sentence explanations.
- In-Acc = the gold answer is a substring of the prediction. R-Acc = the prediction contains "Not enough information". No over-refusal metric on answerable items is reported beyond what In-Acc implicitly absorbs.
- Baselines used "sampling parameters as recommended in the corresponding technical reports"; OCC used greedy (generation_config `do_sample: false`). Single run, no CIs.
- OCC-RAG-0.6B scores 57.6 / 36.6 / 75.0 / 79.9 / 5.2 / 86.9, close to the 1.7B. It is a cheaper A/B candidate.
- "BOAR's measured wall" mapping is the claim's inference. It is plausible for the source-present bucket only.

## Claim 3 — licence/provenance — CORRECTED

What holds:
- HF `raw/main/LICENSE` → HTTP 404, and the repo siblings list has no LICENSE file (README YAML `license: mit` only). Confirmed.
- The paper text contains no licence statement for the data, the teachers or the weights (no occurrence of "licen" in the PDF text). Confirmed.

What is wrong or incomplete:
- **DRAGOn**: the paper only "adopt[s] the question taxonomy of the DRAGOn benchmark" (§3.2.2). No DRAGOn data is used, so DRAGOn's terms are irrelevant.
- **Teachers and their roles** (§3.1–3.3): gpt-oss-120B generates the single-hop and multi-hop QA pairs and runs Wikontic KG extraction. Qwen3.5-27B generates all reasoning traces, so the student is distilled from it. Qwen3-4B is only a verifier/filter, and its outputs are not in the training data. A DeBERTa SQuAD model (Savkin et al. 2024) decides which reduced-context examples become refusals.
- **Teacher licences (now checked)**: gpt-oss-120b apache-2.0 (+ USAGE_POLICY: "comply with all applicable law"); Qwen3.5-27B apache-2.0; Qwen3-4B apache-2.0. None restricts training on or redistributing outputs. The teacher-terms risk is low.
- **Source corpora**: English Wikipedia XML dump (CC BY-SA 4.0 / GFDL text); MuSiQue train split (CC BY 4.0, per StonyBrookNLP/musique LICENSE); Wikidata ontology via Wikontic (CC0). The corpus itself is **not released** (occ-ai has no datasets on HF), so no data-redistribution obligation reaches BOAR. Whether weights trained on CC BY-SA text count as a derivative work is an open legal question that applies to essentially every LLM, including BOAR's current Qwen3.
- GitHub repo optimal-cognitive-core/OCC-RAG does have an MIT LICENSE ("Copyright (c) 2026 optimal cognitive core").
Corrected claim: "OCC repos declare MIT (HF YAML; the GitHub repo has an MIT LICENSE file; the HF repo has none, raw LICENSE 404). The paper states no licences. The data teachers (gpt-oss-120B, Qwen3.5-27B) and the filter (Qwen3-4B) are all Apache-2.0. The source text is Wikipedia (CC BY-SA) + MuSiQue (CC BY 4.0), and the corpus is not released. DRAGOn contributed only a taxonomy. The residual risk is the generic trained-on-CC-BY-SA question, not teacher terms."

## Claim 4 — no latency/length numbers — CONFIRMED (+ estimate)

- The paper has no latency, throughput or answer-length figures. "at a fraction of the cost of full thinking-mode inference" (§5.1) is unquantified. Filter (§3.3): drop traces whose **reasoning section** exceeds 1,256 tokens (the section only, not the whole response) or that contain more than 10 "Wait/Alternatively" markers. HF `generation_config.json`: `max_new_tokens: 2048`, greedy. Max training sequence 6,144.
- Derived estimate (verifier arithmetic on Fig. 4, not a paper number): the reasoning share of tokens per subset × subset tokens ÷ pairs gives about **280 tokens per response for single-hop** (7.76B×10 %/2.78M), ~240 for MH-single (0.16B×40 %/262k), ~355 for MH-multi (0.21B×28 %/165k) and ~280 for abstain. At 12–16 tok/s that is roughly **15–30 s of decode per answer**, before prefill. The training prompt averages ~2.8k tokens for single-hop (7.76B/2.78M, about 75 % distractors), so prefill dominates if BOAR sends similar context.
- The 12–16 tok/s figure is BOAR's own number and was not verifiable here.

## Claim 5 — repo licences — CORRECTED

- HF API `cardData.license` = `mit` for all 6 repos: OCC-RAG-1.7B, -0.6B, -1.7B-GGUF, -0.6B-GGUF, -1.7B-ONNX, -0.6B-ONNX. Confirmed. GitHub MIT LICENSE confirmed (API `spdx_id: MIT`). arXiv CC BY 4.0 confirmed. No HF LICENSE file confirmed.
- Correction 1: the evidence quote "Released under the MIT License ..., inherited from the base model." is **not on the main model card** (the source_url). It appears in the **GGUF and ONNX** READMEs. The main card has YAML `license: mit` only.
- Correction 2: the base licence is now checked. Qwen/Qwen3-1.7B-Base is **apache-2.0**, with a LICENSE file and no NOTICE file in the repo. So "inherited from the base model" is factually wrong. MIT redistribution is still fine, but keep the Apache-2.0 attribution for the Qwen base (see claim 9).

## Claim 6 — GGUF quants — CONFIRMED

- Tree API sizes match byte for byte: Q4_0 1,054,420,096; Q4_K_M 1,107,405,952; Q5_K_M 1,257,876,608; Q6_K 1,417,751,680; Q8_0 1,834,423,424; F16 = BF16 3,447,346,304. Repo `createdAt` 2026-06-09T09:59:03Z. The card marks Q4_K_M as "recommended balance".
- Embedded template: confirmed via HF GGUF metadata (`expand[]=gguf`). `chat_template` is present and ends with the same `<|query_analysis_start|>` generation prompt; arch qwen3, context_length 32768, GGUF `eos_token` = `<|endoftext|>`.
- No llama.cpp version is pinned. The card mentions only "newer llama.cpp: use llama-completion".
- Additions from the source: the card says "Lower-bit quants (Q4) trade some quality for size; prefer Q6_K/Q8_0 when accuracy matters most", and the paper's numbers are bf16 HF greedy. Q4_K_M quality is unmeasured. Implementation risk (verifier observation): HF `generation_config.json` stops on ids 151643, 151645 and **151683 = `<|answer_end|>`**, but GGUF metadata lists `eos_token` `<|endoftext|>`. Whether llama.cpp treats `<|answer_end|>` as end-of-generation is unverified (needs the GGUF header), so BOAR may need an explicit stop string.

## Claim 7 — chat template — CORRECTED

Confirmed from `chat_template.jinja` (byte-identical in 0.6B and 1.7B, verified with `cmp`):
- The generation prompt is `<|im_start|>assistant\n<think>\n\n</think>\n\n<|query_analysis_start|>\n`. The empty think block is also added to every past assistant turn.
- With `documents` and on the last user turn: `<|query_start|>{content}<|query_end|>\n` then, for each doc, `<|source_start|><|source_id|>{i} {text}<|source_end|>\n` (1-based index).
Corrections:
- `<|query_analysis_start|>` is **pre-filled in the prompt**. It is not "forced as the first generated token", and the model's first sampled token comes after it. A custom prompt builder must append it.
- Sources are **not only** passed via `documents=`. The README and GGUF card both document a manual path: build the `<|query_start|>…<|source_start|>…` string in the user content yourself. Without `documents`, the template renders the user content verbatim.
- The template injects no system prompt or instruction text. A system message is passed through if supplied, although training used none (Fig. 6 shows no system turn).
- "Output far more tokens than a 2–5 sentence answer" is inference. See the claim 4 estimate: ~250–350 tokens on average in training.

## Claim 8 — context-grounded only — CONFIRMED

The quote is verbatim in the README Limitations (repeated in the GGUF card). The highlights also say "answers only from the supplied context" and "outputs `Not enough information` when the context does not support an answer". The design consequence (it cannot serve the memory-fallback path) is a sound inference. Add the precision from claim 1: zero-source behaviour is untested, so it is unknown whether it refuses or hallucinates.

## Claim 9 — MIT vs Apache-2.0 base — CONFIRMED (with precision)

- MIT on HF (all 6) and GitHub: confirmed. Qwen3-1.7B-Base: apache-2.0 (YAML + LICENSE file; no NOTICE file in the repo). arXiv CC BY 4.0 is for the paper only: confirmed.
- The phrase "inherited from the base model" is in the GGUF/ONNX cards and is inconsistent with the Apache-2.0 base. Confirmed.
- Precision: Apache-2.0 §4 lets a derivative be distributed under other terms if the redistributor ships a copy of the Apache-2.0 licence, marks modified files, and passes on any NOTICE file. Qwen ships no NOTICE file, so in practice the obligation is to bundle the Apache-2.0 text, credit Qwen alongside the MIT notice from OCC, and say that the weights were modified. That is a small task. "Not cleared until a legal read" is conservative but reasonable for a public bounty submission.

## BOAR consequences (summary)

- Adoption scope: has-source path only. Measure zero-source behaviour before any routing decision, since it is undocumented.
- Licence: shippable under MIT + Apache-2.0 attribution. Teacher terms are not a blocker. The only residual risk is the generic CC BY-SA training-text question.
- Integration: use GGUF `--jinja` or build the manual string ending in `<|query_analysis_start|>\n`. Stop on `<|answer_end|>` explicitly. Parse `<|answer_start|>`.
- Cost: expect ~250–350 trace tokens (≈ 15–30 s at 12–16 tok/s) plus the answer, before prefill. Measure it on device.
- Quality transfer: the paper's tasks are short-span extractive QA with gold passages present, while BOAR's are 2–5-sentence explanations judged against a frontier+web reference. The answer section is a span, so BOAR would need to render a longer answer itself or accept short ones. That is untested.

UNKNOWN:
- Whether the GGUF's EOG token list includes `<|answer_end|>` (needs the GGUF header; download >100 MB, deferred to the weights agent).
- Q4_K_M vs bf16 quality on these benchmarks (not reported).
- Behaviour with zero sources or with long, non-Wikipedia pack chunks (not reported).
