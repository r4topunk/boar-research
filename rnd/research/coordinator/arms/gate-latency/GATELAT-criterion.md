# GATELAT criterion (frozen 2026-10-20 before any gate-latency run)

## Question
RU (arms/refuse-unsupported) passed with the GATE17 groundedness gate, but its card-order prompt (rubric first, ~790 tokens) costs a second
prefill of ~9.3 s p50 on a Pixel 8a and shares no prefix with the answer prompt. Can a reordered and/or trimmed gate prompt keep the gate's
quality and agreement with V0 while cutting the phone's extra prefill to <= 4 s p50?

## Items and labels (reused, 0 new labels, 0 judge calls)
- The 124 RU gated answers (56 unwarned + 68 warned), arms/refuse-unsupported/gate/items.json (gated == true): same question, MacBook K3
  answer (warning line removed) and mini-dumped context (traces/ru-K3-dump-s42.prompts.jsonl, last generate prompt) as RU.
- Support labels: arms/refuse-unsupported/labels/labels.jsonl, majority A/B (C on disagreement) exactly as RU analyze.py.
- V0 = the existing RU gate outputs (gate/boar.outputs.jsonl); not re-run.

## Gate (unchanged weights)
Qwen3-1.7B-Q4_K_M (b139949c) + gate17-lora-f16.gguf (d022352e), llama-server b11010 CPU -t 4 -c 8192 --reasoning off -np 1 on the mini,
slot lock gen1/gen2, own port, stopped after. /completion n_predict 1, temperature 0, n_probs 50; P(FAIL) = pF / (pP + pF) with the PASS/FAIL
first-token ids (mini_gate.py logic). For the cached ("hybrid") variants the same LoRA is loaded as an **activated LoRA (aLoRA)**: an
identical copy of the GGUF plus the metadata key `adapter.alora.invocation_tokens` = the tokens of `<|im_start|>user\nYou are a groundedness
guardrail` (the start of the gate turn). llama.cpp then evaluates every token before the invocation with the base weights (= the answer
model's KV, so it is legitimately reusable) and applies the adapter from the invocation on. Reason: the LoRA touches all linear layers, so a
KV prefix computed by the base answer model is not the KV the full-LoRA gate would compute; only the aLoRA mode makes a cache hit valid.

## Variants
- **Answer prompt** (what the KV holds after answering): the dumped messages rendered with the Qwen3 template, thinking off:
  `<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n` + answer text.
  Validated on the mini: rendered prompt token count == the trace's promptTokens (reported; mismatches listed).
- **Gate turn** (V1, V3): `<|im_end|>\n<|im_start|>user\n` + the card RUBRIC (verbatim) + "\n\nThe CONTEXT is the numbered passages in the
  system message above, the QUESTION is the user message above, and the RESPONSE is the assistant reply above.\nAnswer with exactly one word:
  PASS or FAIL." + `<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n`.
- V0: card order, full context (existing).
- V1 (context-first): answer prompt + answer + gate turn. Run twice: **V1h** (aLoRA, cache_prompt on, the answer prompt + answer prefilled first
  by a separate request = the deployable path) and **V1f** (plain LoRA on all tokens, cache off; diagnostic of the reorder alone).
- V2 (trimmed, card order): gate17 render(question, trimmed context, response); trimmed context = the chunks whose number the answer cites
  ([n], n present in the context), in context order with their original numbers; if none is cited, chunks [1] and [2] (top-2 kept). Plain LoRA, cache off.
- V3 (V1 + V2): the answer prompt with the system message's Context block replaced by the trimmed context, + answer + gate turn. Run as **V3h**
  (aLoRA, answer prompt + answer with the FULL context prefilled first, so the cache hit is only the shared token prefix).

## Metrics (tools/analyze.py; bootstrap item rows B 2000 seed 11, 2.5/97.5 percentiles)
- AUC of P(FAIL): UNSUPPORTED (positive) vs SUPPORTED over the 124 labelled gated answers (ties 0.5), bootstrap CI; unwarned-56 AUC reported.
- Decision agreement with V0 at t = 0.919: share of the 124 where (P >= 0.919) equals V0's; also at t = 0.5 (reported).
- Prompt tokens (total) and non-cached tokens per call. Non-cached = total - longest common token prefix with (answer prompt + answer) tokens for
  the aLoRA variants (V1h, V3h); = total for plain-LoRA variants (V0, V1f, V2: an adapter-on KV is never the answer model's KV).
  The server's measured prompt_n on the cached request is reported as an empirical check.
- Mini wall per gate call (the gate request only; the prefill of the answer prompt stands for work the answer already did).
- Projected Pixel 8a extra prefill = non-cached tokens / 85 tok/s (arms/litelat measured 1.7B prefill rate); p50 / p90.

## Decision rule
A variant QUALIFIES iff ALL of
1. AUC (point, 124) >= 0.90;
2. decision agreement with V0 at t = 0.919 >= 95 % (of 124);
3. projected Pixel 8a extra prefill p50 <= 4 s on the 56 unwarned gated answers (the product path).
V1f is diagnostic and cannot qualify (its cache hit is not valid). Best = the qualifying variant with the lowest projected p50; tie -> higher AUC.
If none qualifies: report "none" and the nearest miss.

## Budget / limits (stated before the run)
0 judge calls, 0 Haiku calls, 0 paid APIs, 0 Opus. Mini: one job, one slot, ~1 h. Projection assumes the phone's prefill rate is flat in
context position, llama.rn keeps the answer's KV and supports aLoRA (not verified), and the answer KV equals the re-tokenized answer text
(sampled tokens may differ from re-tokenization; the engine may post-process text, e.g. citations removed on warned answers).
t = 0.919 was set on V0; reordered variants have a different P(FAIL) scale, so agreement at a fixed t is a strict test.
