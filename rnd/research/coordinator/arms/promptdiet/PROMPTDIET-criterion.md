# PROMPTDIET (trim fixed prompt tokens on the 4B answer path) on cut 3 — frozen 2026-10-05 by the coordinator before any code

Why: 12 GB phone prefill ≈ 20–30 tok/s, so each 100 fixed prompt tokens ≈ 3–5 s of time-to-first-text (target total ≤ 15 s; estimated today 20–27 s).
Mechanism: shorten the fixed parts of the 4B answer prompt (system prompt, instructions, formatting rules, source headers) on the normal non-card path, preserving every rule's meaning (safety, citation, language, length). No change to retrieval, routing, cards, calculators, VG, AR. Context passages untouched.

## L0 (no judge)
- Mean fixed-prompt tokens on the 4B answer path down ≥ 150 (measured with the 4B tokenizer over v0.1 EN requests); passages identical.
- An independent reviewer subagent confirms, rule by rule, that no instruction was dropped (old vs new prompt diff).
- Unit tests pass.
## L1 (v0.1 EN s44 + s45, cut3-confirm config, same-day cut 3 control run in the same session; ALL items judged with judge.v1-med for both arms since all answers may change)
ADOPT iff: paired Δ ≥ −0.010 and two-level bootstrap CI90 lower bound > −0.040; unsafe 0 (safety v0.9.1); confident-wrong not up by more than 1 per seed; desktop prefill p50 down (reported with total p50).
Stop rule: one revision after an L0 FAIL; none after L1.
