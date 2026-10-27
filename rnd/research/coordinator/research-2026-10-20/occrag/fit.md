# OCC-RAG-1.7B: task fit for BOAR (research-2026-10-20, angle "task fit")

TL;DR: OCC-RAG-1.7B is a strong span-extraction RAG reader with a structured, citation-anchored trace and built-in abstention. Its published numbers are on multi-hop span benchmarks (HotpotQA, MuSiQue, TAT-QA, ConFiQA, MuSiQue-Un), not on casual 2-5 sentence answers. Its output is a five-section trace ending in a short answer span, so BOAR would need a second step to produce the 2-5 sentence answer with [n] citations. Trace length is not published, so the latency is unknown. Licence is MIT per three cards, but the LICENSE file could not be fetched and must be checked.

Sources read (no model weights downloaded; only cards, configs, and GGUF listings):
- HF model card: https://huggingface.co/occ-ai/OCC-RAG-1.7B
- HF config: https://huggingface.co/occ-ai/OCC-RAG-1.7B/raw/main/config.json
- HF tokenizer_config: https://huggingface.co/occ-ai/OCC-RAG-1.7B/raw/main/tokenizer_config.json
- HF 0.6B card: https://huggingface.co/occ-ai/OCC-RAG-0.6B
- GGUF cards: https://huggingface.co/occ-ai/OCC-RAG-1.7B-GGUF , https://huggingface.co/occ-ai/OCC-RAG-0.6B-GGUF
- Paper (arXiv 2606.00683, submitted 30 May 2026): https://arxiv.org/abs/2606.00683 and https://arxiv.org/html/2606.00683v1 (the HTML fetch was used through a summariser; the PDF stream was not readable)
- Secondary: https://researchpapers.dev/en/papers/occ-rag-faithful-qa/ , https://www.alphaxiv.org/abs/2606.00683
- GitHub org: https://github.com/optimal-cognitive-core (one repo, OCC-RAG, MIT, updated 2026-06-28; the README fetch was partial)

Not reachable: raw LICENSE (HTTP 404), GitHub README (partial), PDF body text (compressed). Tool output that tried to steer the summariser was ignored.

---

## Findings

### F1. Output is a five-section trace ending in an answer span, not a 2-5 sentence answer [load-bearing]
- Sections, each wrapped in special tokens: query analysis, source analysis, reasoning, status (`ANSWERABLE` / `UNANSWERABLE`), answer.
- The answer is "the answer span, or a refusal phrase" (HF card).
- Card worked example: question "Which country is the inventor of the telephone, Alexander Graham Bell, buried in?" with three short sources; extracted answer "Canada".
- Paper Appendix A: "Answer: Counter Terrorist Unit (CTU)".
- BOAR impact: the model does not write the 2-5 sentence answer with [n] citations that BOAR's prompt expects. Options: (a) parse `<|answer_start|>` and feed the span plus the source-analysis text to the main Qwen3-1.7B as context to write the sentences, or (b) accept short spans for factoid questions only. Either way it changes the answer pipeline. The citation source is the source-analysis section (source ids), not a [n] in the answer.

### F2. Every published benchmark is span/substring scoring; casual explanation and comparison questions are not measured
- In-Acc = "A prediction counts as correct if the gold answer appears as a substring of it" (HotpotQA, MuSiQue, ConFiQA). TAT-QA = token F1.
- R-Acc = "fraction of predictions containing the phrase 'Not enough information'".
- None of the eight evaluation sets covers explanations, comparisons over open text, or travel/crypto-style questions. The 2-5 sentence style of BOAR answers is not tested.
- Paper limitation (from the researchpapers.dev summary of the paper): synthetic data "risks teaching the model the _style_ of grounded answering on machine-generated text more than the messy retrieval failures of real corpora."
- BOAR impact: the headline numbers do not predict BOAR's judged quality. A BOAR-specific eval on the self-test items (factoid + explanation + no-source) is required before any adoption decision.

### F3. Abstention is trained and measured on a fixed-context setting; the no-source case is not measured [load-bearing]
- MuSiQue-Un: "unanswerable counterpart of MuSiQue, with supporting passages replaced"; 10 sources fixed; 2,417 samples; R-Acc OCC-RAG-1.7B = 87.2 (0.6B = 86.9). Qwen3-1.7B: 54.7 no-think, 82.8 think.
- Training: "a portion of examples have no supportable answer, training the model to abstain instead of hallucinating" (researchpapers.dev summary); 43k abstain examples of ~3.25M.
- The model is "context-grounded only": "The model is trained to answer from the supplied sources and to ignore parametric knowledge" and "is not a general chat model" (HF card / GGUF card).
- Open: the behaviour with zero sources or with sources unrelated to the question is not reported as a number. The abstention set is 1.3% of training data. We have no measure of over-refusal on answerable items (a false UNANSWERABLE), which is the risk for BOAR's short-factoid travel and crypto questions.
- BOAR impact: BOAR's fallback ("answer from memory under a warning line") cannot be produced by OCC-RAG as trained. It would need a separate path for the no-source case, using the main model. The over-refusal rate on answerable casual items must be measured before use.

### F4. Trace length is not published; latency is unknown and must be measured [load-bearing]
- No token count for the trace appears in the card, the GGUF cards, the README (as fetched), the paper summaries, or the researchpapers.dev / alphaxiv pages.
- The only numbers: the HF example uses `max_new_tokens=2048` (and 256 in one example); the GGUF card says "Q6_K/Q8_0 when accuracy matters most".
- Estimate, not measured: a five-section trace for a 3-source question likely runs in the low hundreds of tokens. The appendix example is short. Illustrative decode times at BOAR's 12-16 tok/s (1.7B on the 8 GB Pixel 8a, per the task):

| Trace length (tokens) | Decode at 16 tok/s | Decode at 12 tok/s |
|---|---|---|
| 150 | ~9 s | ~12.5 s |
| 300 | ~19 s | ~25 s |
| 600 | ~37 s | ~50 s |
| 2048 (the card cap) | ~128 s | ~171 s |

  Plus prefill for the packs' retrieved text. For comparison BOAR's current answers are 2-5 sentences (not measured here either).
- BOAR impact: the trace is mandatory in the template as far as the cards show (see F6). The per-answer cost is unknown; a 300-token trace would double the current answer time if the current answer is around 100-150 tokens. Measure on a device before deciding.

### F5. Benchmark gain vs Qwen3-1.7B: about +13 points on HotpotQA only in think mode; gains are largest on faithfulness and refusal [not load-bearing]
Table 2 (exact values from the paper's table, as the summariser read it; Qwen3 baseline values are shown as no-think (think)):

| Model | HotpotQA In-Acc | MuSiQue In-Acc | TAT-QA F1 | ConFiQA In-Acc | ConFiQA MR (lower) | MuSiQue-Un R-Acc |
|---|---|---|---|---|---|---|
| Qwen3-1.7B | 47.7 (60.9) | 20.1 (30.7) | 74.4 (74.8) | 64.8 (70.4) | 12.7 (8.3) | 54.7 (82.8) |
| Qwen3-4B | 60.6 (67.1) | 33.1 (41.5) | 76.9 (79.1) | 69.7 (74.1) | 10.3 (7.5) | 64.1 (84.0) |
| OCC-RAG-0.6B | 57.6 | 36.6 | 75.0 | 79.9 | 5.2 | 86.9 |
| OCC-RAG-1.7B | 60.9 | 38.2 | 81.0 | 81.4 | 5.0 | 87.2 |

- Versus Qwen3-1.7B think, OCC-RAG-1.7B is equal on HotpotQA (60.9 vs 60.9), +7.5 on MuSiQue, +6.2 on TAT-QA, +11.0 on ConFiQA, -3.3 on MR (better), +4.4 on MuSiQue-Un.
- Versus Qwen3-1.7B no-think: +13.2, +18.1, +6.6, +16.6, -7.7 MR, +32.5 R-Acc.
- Note: OCC-RAG-1.7B has a "closes the gap" claim against Qwen3-4B think (67.1 HotpotQA; OCC 60.9).
- Metric caveat: MR is ConFiQA's memorisation ratio (Po/(Po+Pc), lower = better), not the same as the MR subset name.
- BOAR impact: the ConFiQA and MuSiQue-Un gains are the ones that match BOAR's measured walls (not using pack text; confident errors on absent knowledge). The HotpotQA gain is zero against think mode, so the main gain is on the reading step, not multi-hop knowledge.

### F6. Thinking can be switched off in the chat template call, but there is no documented way to switch off the five-section trace [load-bearing? no; included in F1 decision]
- The HF quickstart calls `apply_chat_template(..., documents=..., enable_thinking=False)` and `generate(..., max_new_tokens=2048)`.
- The card and README never describe a thinking mode for OCC-RAG itself; "(think)" appears only on the Qwen3 baselines.
- The tokenizer_config has no `enable_thinking` logic, only `<|reasoning_start|>` / `<|reasoning_end|>` tokens. Whether the trace can be capped or made shorter is not documented.
- BOAR impact: the flag is probably a no-op for OCC-RAG (inference, not verified). Trace control would need a fine-tune or a prompt test; no config switch is known.

### F7. Context window: 32,768 positions, tokenizer max 131,072; no context budget is published [not load-bearing]
- config.json (1.7B): model_type qwen3, 28 layers, hidden 2048, max_position_embeddings 32768, vocab 151936, dtype bfloat16, rope_theta 1000000, sliding_window null.
- tokenizer_config.json: model_max_length 131072 (tokenizer default; not the model's usable context).
- Neither card states a context length or the number of sources used at inference beyond MuSiQue-Un (10 sources).
- BOAR impact: a pack-based prompt with k chunks must be measured against the 32k position limit and the phone's RAM. The MuSiQue-Un set uses 10 sources, which is a reasonable upper reference.

### F8. Multi-chunk noise: distractors are mined, and MuSiQue-Un uses 10 sources; no crowding curve is given [not load-bearing]
- Paper: "mined 'distractor' paragraphs" (alphaxiv summary). Number of distractors per training example is not stated.
- Appendix A example mixes one irrelevant source (Law & Order) with two relevant ones; the trace marks it "Source 2 is irrelevant".
- BOAR impact: the distractor handling is the one behaviour BOAR needs for noisy packs (crowding was a measured wall for the main model). The paper gives no curve over the number of sources, so BOAR must measure it on its own packs.

### F9. Languages: English and Russian tags on the card; no prose statement; BOAR is English-only [not load-bearing]
- HF card and 0.6B card list language tags "en" and "ru" (English and Russian). The prose does not state language support. The alphaxiv summary shows only the "en" tag.
- BOAR impact: English-only use is not blocked, but the Russian tag means some training data may be Russian. Not measured for English quality beyond the benchmarks (which are English).

### F10. Deployment: GGUF exists for 1.7B and runs on llama.cpp and Ollama; Q4_K_M is 1.11 GB [not load-bearing]
- 1.7B GGUF sizes (card): Q4_0 1.05 GB, Q4_K_M 1.11 GB, Q5_K_M 1.26 GB, Q6_K 1.42 GB, Q8_0 1.83 GB, F16/BF16 3.45 GB.
- Usage: `llama-cli -hf occ-ai/OCC-RAG-1.7B-GGUF:Q4_K_M -p "Hello" -no-cnv`; the chat template is embedded in the GGUF and applied by llama.cpp and Ollama; the card mentions `--jinja`.
- Not stated: thinking flag, context size, and any tokenizer quirk for the custom tokens. Custom special tokens (`<|query_start|>`, `<|source_start|>`, `<|source_id|>`, `<|answer_start|>`) must survive `skip_special_tokens=False` for parsing; the HF card says to keep it off.
- Size is comparable to Qwen3-1.7B Q4_K_M, so the RAM footprint is not the constraint; the trace length is.
- The weights were not downloaded (per the task's 100 MB rule). Only card-listed sizes were read.

### F11. Licence: MIT on three cards, but the LICENSE file could not be read; the "inherited from base model" statement needs checking [load-bearing: licence is a gate]
- HF 1.7B card metadata: MIT. GitHub org repo: MIT, last updated 2026-06-28. GGUF card: "Released under the MIT License," described as "inherited from the base model".
- The raw LICENSE file returned HTTP 404 (URL tried: huggingface.co/occ-ai/OCC-RAG-1.7B/raw/main/LICENSE). The GitHub README fetch was partial.
- The stated base is Qwen3-1.7B-Base. Qwen3 weights are, to our knowledge, Apache-2.0 (not verified in this session). If the base is Apache-2.0, the claim "MIT inherited from base" is inaccurate, and the redistributable licence must come from the OCC release itself.
- The arXiv paper licence shown in the arXiv HTML summary is CC BY 4.0 (for the paper, not the weights).
- BOAR impact: before any app bundling, read the LICENSE file in both repos and the Qwen3 base licence. A redistribution decision cannot rest on the card metadata alone.

### F12. Paper limitations and the "three-hop cap" [not load-bearing]
- "Reasoning is capped at three hops. Longer chains are out of distribution." (HF card; also in the GGUF card). "Training and evaluation are capped at three-hop reasoning."
- BOAR impact: BOAR's casual research questions are rarely multi-hop; the cap is not the main concern, but it means "compare X and Y and Z" with three entities is at the edge.

### F13. Recommended decoding is greedy and baked into generation_config [not load-bearing]
- "We recommend greedy decoding (`do_sample=False`, `temperature=0.0`)" (README). The GGUF card recommends `--temp 0`. Qwen3's default sampling "also work fine" (HF card).
- BOAR impact: greedy decoding on the phone matches the current BOAR settings only if BOAR also uses greedy; check the app's sampler config.

### F14. Sizes and the 0.6B sibling [not load-bearing]
- OCC-RAG-0.6B in Table 2: HotpotQA 57.6, MuSiQue 36.6, TAT-QA 75.0, ConFiQA 79.9, MR 5.2, MuSiQue-Un 86.9. Only 0.6B-vs-1.7B gap is 3.3 on HotpotQA and 1.6 on MuSiQue-Un.
- The 0.6B GGUF Q4_K_M is 0.40 GB. This is a candidate if the 1.7B trace is too slow.
- Metadata of the 1.7B card lists 2B parameters (BF16); the card text says 1.7B. Not material, flagged.

---

## Answers to the angle's questions (a)-(g)

- (a) Over-refusal on answerable questions: not measured. No published false-UNANSWERABLE rate on answerable items. Open; needs a BOAR test on answerable factoid and travel items.
- (b) No useful context: the model is trained to abstain (UNANSWERABLE, phrase "Not enough information") and to ignore parametric knowledge. It does not answer from memory by design. Zero-source behaviour is not reported. BOAR's memory-fallback path must come from the main model.
- (c) Multi-chunk noisy retrieval: MuSiQue-Un (10 sources) and a worked example with an irrelevant source. No crowding curve. Mined distractors; count unknown.
- (d) Explanation/comparison vs factoid: all benchmarks are factoid/multi-hop span tasks. Output is a span. Explanation and comparison are untested.
- (e) Trace length: not published. Estimate from F4: low hundreds of tokens; at 12-16 tok/s that is roughly 10-25 s decode for 150-300 tokens; the 2048 cap would be about 2-3 minutes. Measure.
- (f) Trace disable or cap: no documented switch. `enable_thinking=False` appears in examples; the five-section trace is the output format. Cap by `max_new_tokens` is possible in the runtime; a shorter trace is not supported by any card.
- (g) Multilingual: tags en and ru; prose silent; BOAR needs English only, and the benchmarks are English.

## Open questions (UNKNOWN)

1. What is the trace length in tokens on in-domain questions? (Needs a device or a desktop GGUF run; weights are for another agent.)
2. Does the model output UNANSWERABLE for answerable questions with noisy packs (over-refusal rate)?
3. What does it output with zero sources (no context block at all)?
4. Is the licence MIT for the weights, and what does the Qwen3-1.7B-Base licence require?
5. Does the trace or answer format survive the BOAR prompt structure (short answer with [n] citations)?
6. Is enable_thinking a no-op for OCC-RAG, and is there any way to shorten the trace?
7. Is any Russian-language data a risk for English answers? (Low priority.)

## Next steps (proposed, not run)

1. Read the LICENSE file of occ-ai/OCC-RAG-1.7B and the Qwen3-1.7B-Base licence card. Gate for any redistribution.
2. A 20-item BOAR micro-eval (factoid, explanation, comparison, no-source, answerable-with-distractors) comparing the Qwen3-1.7B main model and OCC-RAG-1.7B Q4_K_M via the GGUF. Record trace token count, UNANSWERABLE rate on answerable items, and time per answer. This is the measurement the paper does not give.
3. Only if (2) passes: design the two-step pipeline (OCC trace → span → main model writes the 2-5 sentences with [n]).
