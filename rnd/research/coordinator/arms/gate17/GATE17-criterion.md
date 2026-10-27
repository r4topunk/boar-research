# GATE17 criterion (frozen 2026-10-20 before the gate runs on any BOAR item)

## Question
On BOAR's existing Qwen3-1.7B answers (LITEPACKS system, mini controls) that had at least one kept source, does the groundedness gate
`aaryand/qwen3-1.7b-context-adherence-guardrail` (Apache-2.0 QLoRA on Qwen/Qwen3-1.7B, rev daa91b0d) separate confident errors (CE) and
judge-wrong answers from judge-correct ones well enough to drive "refuse when the answer is not supported"? Diagnostic arm: no system change.

## Gate
- Adapter: PEFT LoRA r16 (adapter_model.safetensors sha256 8ed04f95...) converted with llama.cpp b11010 `convert_lora_to_gguf.py --outtype f16`
  (base config Qwen/Qwen3-1.7B rev 70d244cc, no base weights) -> gate17-lora-f16.gguf sha256 d022352e...; run as
  `llama-server -m Qwen3-1.7B-Q4_K_M.gguf (b139949c) --lora gate17-lora-f16.gguf -c 8192 -t 4` on the mini (slot lock gen1/gen2, own port, stopped after).
- Prompt: the card's exact RUBRIC + QUESTION/CONTEXT/RESPONSE block + "Answer with exactly one word: PASS or FAIL.", Qwen3 chat template,
  enable_thinking=False (tools/build_items.py `render`). /completion, n_predict 1, temperature 0, n_probs 50.
- Score: P(FAIL) = p(FAIL) / (p(PASS) + p(FAIL)) at the first position, tokens = first id of tokenize("PASS") / tokenize("FAIL") (card: 2-way softmax).
- Smoke (done before freezing, card's own example + 2 variants): FAIL 0.998 / PASS 0.002 / PASS 0.011, as the card.

## Items (0 judge calls; labels exist)
- Rows: the mini controls lpctl-K0-main-s42 (n 97) and lpctl-K1-screen-s42 (n 37; no K1 MAIN control exists), regenerated unchanged on the mini
  with `--dump-prompts` (tools/gen_dump.sh) to recover the exact context. Labels (CE, corr, warned) from the controls' existing Haiku 5.5-low
  aggregates; valid only where answer.text is byte-identical to the control (others excluded, listed). VOID if fewer than 90 % identical in either run.
- In scope: retrieval.kept non-empty AND the item's last generate prompt carries a `Context:` block. Context = that block verbatim (what the 1.7B saw);
  response = answer.text minus the engine warning line ("Not found in this phone's offline library. From the model's memory, may be wrong:").
  Items with no kept source, and kept-source items answered without an LLM generate, are out of scope and listed separately.
  K1-screen rows identical to a K0-MAIN row in (id, context, response) are dropped as duplicates.

## Decision rule (tools/analyze.py, committed with this file)
Primary set = pooled in-scope rows (K0 MAIN + K1 screen). GO (design a refuse-when-unsupported arm next) iff
1. AUC of P(FAIL) for CE vs non-CE >= 0.70, AND
2. its bootstrap CI low >= 0.60 (item-row bootstrap, B 2000, seed 11, 2.5 / 97.5 pct), AND
3. at t* = the lowest threshold whose false alarms (flagged among judge-correct answers, correctness >= 4) are <= 10 % of the judge-correct
   answers, the gate flags >= 1/3 of CE.
Otherwise NO. Direction pre-declared (higher P(FAIL) = flag); AUC never flipped.
Also reported (not in the rule): AUC judge-wrong (corr <= 2) vs judge-correct (corr >= 4) with CI; flag tables at t* and at 0.5;
the same per set (K0 MAIN alone, K1 screen alone) and warned / unwarned; gate latency per call on the mini (prompt tokens, prefill ms);
3 caught CE and 3 false alarms.

Known limit, stated before the run: about 58 in-scope rows with roughly 9 judge-correct answers, so the 10 % false-alarm budget allows 0 false
alarms, and the CE-vs-non-CE CI is wide. Base model is Q4_K_M (card: bf16), a deviation from the card's numbers.

## Budget
calls_cap: Haiku 0 / Opus 0; paid APIs 0.
