# OCC-RAG verify-2 (adversarial check of 9 load-bearing claims)

TL;DR: 2 confirmed, 7 corrected, 0 refuted. Every number copied from Table 2 matches the paper. The corrections are about the licence chain, the LFM2-RAG facts, the 0.6B gap and some details of trace length and abstention. One new finding matters most for the device plan: the authors dropped every training trace whose reasoning section went over 1,256 tokens, and the per-subset work budget points to short responses. The 2,048-token cap is therefore probably not the expected cost (this still needs measuring).

Checked 2026-10-20 20:11 from primary sources fetched with curl:
- HF raw files for occ-ai/OCC-RAG-1.7B, -0.6B and -1.7B-GGUF: README, chat_template.jinja, generation_config.json, tokenizer_config.json, tokenizer.json (11 MB) and the API sibling lists.
- arXiv 2606.00683v1, HTML version (abstract page: v1 only, submitted 30 May 2026, paper licence CC BY 4.0).
- GitHub optimal-cognitive-core/OCC-RAG: API, LICENSE, README, examples/.
- Upstream HF licence metadata.
- The LiquidAI HF card, LICENSE and docs.liquid.ai.
- llama.cpp master: tools/server/README.md and common/chat.cpp.

No weights were downloaded.

## Verdicts

| # | Claim (short) | Status |
|---|---|---|
| 1 | Five-section output contract, greedy decoding, `documents=`, "Not enough information" | confirmed (with additions) |
| 2 | Card table compares against Qwen3-1.7B think mode; no-think numbers only in the paper | corrected (minor) |
| 3 | The answer is a short span or a refusal phrase | confirmed |
| 4 | Abstention measured only on fixed 10-source contexts; context-grounded only | corrected (attribution + training detail) |
| 5 | No trace-length number published; latency unknown | corrected (new evidence bounds it) |
| 6 | MIT licence "inherited from base model"; LICENSE 404 | corrected |
| 7 | Table 2 numbers (OCC vs Qwen3-1.7B no-think and think) | confirmed |
| 8 | LFM2-1.2B-RAG deprecated, no numbers, unverified licence, no GGUF | corrected |
| 9 | 0.6B within about 1–4 points of 1.7B; GGUF only from third parties | corrected |

### 1. Output contract: confirmed, with additions
- The card's format table lists five sections delimited by `<|query_analysis_*|>`, `<|source_analysis_*|>`, `<|reasoning_*|>`, `<|status_*|>` (ANSWERABLE / UNANSWERABLE) and `<|answer_*|>`.
- Highlights: "outputs `Not enough information` when the context does not support an answer".
- Decoding: greedy is "baked into `generation_config.json`" (`do_sample: false`, `temperature: 0.0`, `max_new_tokens: 2048`). The card's quickstart and GitHub's examples/quickstart_vllm.py both use `skip_special_tokens=False`.
- Additions the claim did not state:
  - **The `documents` branch of the template fires only if `documents` is non-empty and the user message is the last one.** Otherwise the question goes in as a plain user turn with no `<|query_start|>` wrapper. That input shape never appears in training, so a zero-source call is out of distribution.
  - The generation prompt pre-fills `<think>\n\n</think>\n\n<|query_analysis_start|>\n`, so think mode is always empty.
  - `eos_token_id` = [151643, 151645, 151683]. Id 151683 is `<|answer_end|>` (checked in tokenizer.json). A runtime that ignores the generation_config EOS list needs `<|answer_end|>` added as a stop string.
  - **llama.cpp:** llama-server documents a per-request `chat_template_kwargs` field and a `--chat-template-kwargs` flag, and common/chat.cpp copies `extra_context` keys into the template context. So `{"documents":[...]}` should reach the embedded Jinja template under `--jinja`, but nobody has tested this.
  - **Ollama:** it uses Go templates, so the GGUF card's line "llama.cpp/Ollama apply it automatically" is unverified for the `documents` path.
  - For BOAR (llama.rn), the simplest route is the hand-built token string that the card shows as the "Alternative". It bypasses the question entirely.

### 2. Card baseline is think mode: corrected (minor)
- The card table's Qwen3-1.7B row is labelled "(think)": 60.9 / 30.7 / 74.8 / 70.4 / 8.3 / 82.8 against OCC 60.9 / 38.2 / 81.0 / 81.4 / 5.0 / 87.2. All values match.
- The correction: the claim says the no-think baselines are not on the card, but the card text does include one: "Mid-training reduces the memorization ratio from 12.7 (8.3 in thinking mode) for Qwen3-1.7B down to 5.0." The other no-think values (47.7, 20.1, 74.4, 64.8, 54.7) appear only in paper Table 2.
- Evaluation conditions:
  - OCC was run greedy. Baselines were run "with sampling parameters as recommended in the corresponding technical reports" (paper §5.1).
  - The paper reports one number per cell, with no seeds and no confidence intervals.
- Corrected claim: the card's table compares against think mode only; the card's prose also quotes the no-think M_R of 12.7.

### 3. Short span answer: confirmed
- Card format table, Answer row: "The final answer span, or the refusal phrase." The brief's evidence quote dropped the word "final".
- How the training data was made (paper §3.1 and §3.2):
  - Single-hop QA came from gpt-oss-120B with the instruction that "answers must be short and extractive".
  - Multi-hop answers "must be a literal span of the supplied context".
  - The Figure 6 example answer is "Counter Terrorist Unit (CTU)".
- So a 2–5 sentence answer with [n] citations is out of distribution. The implication in the brief (a second writing step, or span-only output for factoids) follows.

### 4. Abstention scope: corrected (quote attribution and a training detail)
- Evaluation: "We fix the number of input sources to 10. We instruct the model to output the phrase 'Not enough information' … and report Refusal Accuracy (R-Acc) as the fraction of predictions that contain it" (paper §5.1). Scores: 87.2 for OCC-1.7B, 54.7 for Qwen3-1.7B no-think, 82.8 for think.
- What is not reported anywhere:
  - zero-source behaviour;
  - irrelevant-only-source behaviour;
  - the false-refusal rate on answerable items.
- Because R-Acc only counts refusals on unanswerable items, over-refusal is invisible in it.
- Training detail missing from the claim (§3.2.3): the 43k abstain examples are built from **reduced subsets of the original gold contexts**, where a SQuAD DeBERTa model fails to recover the answer. Relevant-looking evidence is still present in these examples; they are not empty or off-topic contexts. They are 1.3 % of pairs and 0.029B of about 8B tokens.
- Attribution fix: the quote "The model is trained to answer from the supplied sources and to ignore parametric knowledge" comes from the **HF card Limitations** (and the GGUF card), not from the arXiv paper. The paper's equivalent wording is in §1, about "disregarding parametric knowledge".
- Corrected claim: same substance. Refusal training uses partial gold contexts, the quote's source is the HF card, and R-Acc cannot detect over-refusal.

### 5. Trace length unpublished: corrected (new bounding evidence)
- Confirmed: neither the card nor the paper gives a token count per answer.
- Not found: "max_new_tokens 256 in one example". The card, examples/quickstart_transformers.py and quickstart_vllm.py all use 2048.
- New evidence from the paper:
  - **Overthinking filter (§3.3):** "we drop any trace whose reasoning section exceeds 1,256 tokens", and traces with more than 10 markers such as "Wait" or "Alternatively" are also dropped. So training never contains a reasoning section longer than 1,256 tokens.
  - **Figure 4 per-subset totals (prompt plus response, Qwen3 tokens):**

    | Subset | Tokens | Pairs | Tokens per example (my division) |
    |---|---|---|---|
    | single-hop | 7.76B | 2.78M | ≈ 2,790 |
    | multi-hop multi-context | 0.21B | 165k | ≈ 1,270 |
    | multi-hop single-context | 0.16B | 262k | ≈ 610 |
    | abstain | 0.029B | 43k | ≈ 670 |

    Distractor and gold contexts make up most of these totals ("35%–75%" distractors), so responses are a few hundred tokens at most. One caveat: it is unclear whether the counts include the ×3 oversampling.
  - The Figure 6 example response is about 190 words, which I estimate at about 250 tokens.
- Your arithmetic is correct:
  - 150 tokens ≈ 9.4–12.5 s;
  - 300 tokens ≈ 19–25 s;
  - 2048 tokens ≈ 128–171 s at 16–12 tok/s.
- Corrected claim: no official length is published. Training traces are capped at 1,256 reasoning tokens, and the corpus statistics point to roughly 200–500 response tokens. The likely decode cost is about 15–40 s at 12–16 tok/s, plus prefill for about 10 sources, which the brief left out. A GGUF run is still required.

### 6. Licence: corrected
- The weights are MIT in three places:
  - the HF card front matter on all three repos;
  - the GitHub repo LICENSE (SPDX MIT, "Copyright (c) 2026 optimal cognitive core");
  - the GGUF card.
- There is no LICENSE file in either HF weight repo: the sibling list has none and `/raw/main/LICENSE` returns 404 on both. The readable MIT text lives in the GitHub repo.
- **"Inherited from the base model" is misread in the claim.** On the GGUF card, "base model" means `occ-ai/OCC-RAG-1.7B` (front matter `base_model: occ-ai/OCC-RAG-1.7B`, and the header link "Base model" points there), not Qwen.
- Upstream licences (HF metadata):

  | Component | Role | Licence |
  |---|---|---|
  | Qwen3-1.7B-Base | base model | apache-2.0 |
  | Qwen3-0.6B-Base | base model | apache-2.0 |
  | Qwen3.5-27B | trace teacher (§3.3) | apache-2.0 |
  | gpt-oss-120b | QA generator (§3.1–3.2) | apache-2.0 |
  | Qwen3-4B | verifier judge | apache-2.0 |
  | English Wikipedia XML dump | source corpus | CC BY-SA |
  | MuSiQue train split | source corpus (§3.2) | CC BY 4.0 (GitHub API for StonyBrookNLP/musique) |

- The training corpus itself is not released. No teacher terms forbid training a competing model, and the Apache-2.0 base allows an MIT derivative, but Apache §4 NOTICE and attribution duties carry over.
- UNKNOWN: whether CC BY-SA on the Wikipedia text reaches the weights. This is legally unsettled; common industry practice treats it as not reaching them.
- Corrected claim: the weights are MIT, with the text in the GitHub LICENSE. The upstream chain is Apache-2.0 models plus CC BY-SA and CC BY 4.0 data, and no licence clause blocks redistribution in the app. Ship the MIT text plus an Apache-2.0 attribution to Qwen.

### 7. Table 2 numbers: confirmed
- Paper Table 2, Qwen3-1.7B row: 47.7 (60.9) | 20.1 (30.7) | 74.4 (74.8) | 64.8 (70.4) | 12.7 (8.3) | 54.7 (82.8).
- OCC-RAG-1.7B row: 60.9 | 38.2 | 81.0 | 81.4 | 5.0 | 87.2.
- The In-Acc quote is verbatim from §5.1.
- Caveats to keep with these numbers:
  - TAT-QA covers only span and multi-span questions (arithmetic and counting were excluded).
  - ConFiQA is averaged over the QA, MR and MC subsets.
  - Each benchmark uses 10 sources, with gold sources mixed with distractors.
  - Decoding differs between OCC and the baselines (see claim 2).
- "Only comparison … self-reported": I did not search for independent evaluations in this pass, so that part is unverifiable here; nothing contradicting it turned up.

### 8. LFM2-1.2B-RAG: corrected
- **Deprecation is true, but the source is docs.liquid.ai, not the HF card.** The page docs.liquid.ai/lfm/models/lfm2-1.2b-rag says: "This model is deprecated. For generation, use LFM2.5-1.2B-Instruct. For retrieval, pair it with LFM2.5-Embedding-350M or LFM2.5-ColBERT-350M." The HF card (last modified 2026-08-03) has no deprecation note.
- No benchmark numbers on the card: confirmed.
- **The licence is readable.** The repo LICENSE file is "LFM Open License v1.0": Apache-style grants, with Commercial Use conditioned on annual revenue below USD 10M (§5). The claim that only the bare tag is visible is wrong.
- **An official GGUF exists:** `LiquidAI/LFM2-1.2B-RAG-GGUF`, linked from the card's "How to run" section and carrying the same lfm1.0 licence.
- Corrected claim: deprecated per Liquid's docs; no numbers on the card; licence LFM Open License v1.0 (revenue-threshold commercial limit); official GGUF available. The conclusion "do not adopt" still holds, because the model is deprecated and has no evidence.

### 9. OCC-RAG-0.6B fallback: corrected
- The numbers match the card and paper: 57.6 / 36.6 / 75.0 / 79.9 / 5.2 / 86.9.
- The gaps to the 1.7B are 3.3 / 1.6 / **6.0 (TAT-QA F1)** / 1.5 / 0.2 (M_R) / 0.3. "Within about 1 to 4 points" is wrong on TAT-QA.
- MIT: confirmed.
- **Official GGUF and ONNX builds exist from occ-ai itself:**
  - `occ-ai/OCC-RAG-0.6B-GGUF` (MIT, base_model occ-ai/OCC-RAG-0.6B);
  - `occ-ai/OCC-RAG-0.6B-ONNX`;
  - `occ-ai/OCC-RAG-1.7B-ONNX`.

  Third-party quantizations are not needed.
- Corrected claim: the 0.6B is 0.2–3.3 points behind on five metrics and 6.0 behind on TAT-QA F1. Official GGUF and ONNX builds exist, which removes the provenance concern.

## Points for BOAR
1. The answer path needs a stop on `<|answer_end|>`, a parser that maps `<|source_id|>N` to [n], and a second writing step if the 2–5 sentence format stays. Zero-source calls must stay on the main model.
2. The decisive measurements:
   - tokens per answer, plus prefill time for 10 sources;
   - the false-UNANSWERABLE rate on answerable dev items.

   Neither is published.
3. Licence chain: MIT, Apache-2.0 and CC BY-SA/CC BY. Ship the attribution texts with the app.

UNKNOWN:
- whether llama.cpp's `chat_template_kwargs` and the embedded template work end to end;
- whether the GGUF metadata includes 151683 as an EOS token;
- the effect of Q4_K_M quantization on trace quality;
- whether Figure 4 counts tokens before or after the ×3 oversampling.
