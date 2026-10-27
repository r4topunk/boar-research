# CHAINWHEN criterion (frozen 2026-10-19 before any generation)

Question: is there a right moment to chain one extra 4B call (the G3 source pick) before the answer, and does routing on its output improve judged answers on 8 GB?

Exploratory basis (0 LLM, RELGATE x PACKREAD M4-D4, n 54): ratio 0.752 when the fact chunk is source [1], 0.662 when it sits further back, 0.602 with no fact; G3 = 0 is right on 21/26 no-fact contexts; with n_src <= 2 the fact is never further back.

Set: the 150 RELGATE contexts (arms/relgate/data/contexts.jsonl; public pack self-tests, X2b engine prompts). No blind/ or veil/ reads.
Model: Qwen3-4B-Instruct-2507 (same GGUF and llama-server b11010 settings as PACKREAD M4), prompt D4 exactly as PACKREAD, max_tokens 1024, seed 42, one generation per item per arm.

Arms:
- OFF: the context as is.
- ON (trigger rule, fixed): skip G3 when the pack is boar-firstaid-en, boar-medlineplus-en or qa-health-se (health/danger never gated) or when n_src <= 2; ON = OFF for those items. Otherwise use the G3 argmax already recorded in arms/relgate/runs/m4.jsonl (same prompt, deterministic):
  - pick = 1: unchanged.
  - pick > 1: move that source to position [1] and renumber the others in order (citations follow the new numbers).
  - pick = 0: append to the user turn one line: "Note: the offline sources above may not contain the answer. If they do not, say so plainly and give only what you are sure of."

Judge: Haiku 5.5-low, judge.v1-low, N = 4 shards, both orders, uncapped, refs of the self-tests. Score = PACKREAD agg (mean of 3 dims, ratio Q = sum s / sum s_ref, bootstrap B 2000).

Decision (paired ON - OFF over the triggered items, i.e. items where ON != OFF):
- ADOPT-CANDIDATE: delta >= +0.02 and paired 95 % CI low > 0, and no harm on the pick=1-or-untriggered rest (identical by construction) and on the pick>1 subset with fact@1 (delta >= -0.05, report n).
- Separate readouts (no rule): pick>1 subset delta; pick=0 subset delta and correctness mean; overall delta on all 150; trigger rate; phone cost = +0.57 s per triggered item if prefix KV reuse works, +18 s otherwise.
- NO otherwise. A NO means the chain step does not pay on self-tests at this n; it does not test V-para-style casual questions.
Next on ADOPT-CANDIDATE: Opus confirmation on the triggered items, then a device prefix-KV check before any engine patch.
