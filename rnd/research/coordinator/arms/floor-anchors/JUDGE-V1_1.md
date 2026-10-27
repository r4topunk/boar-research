# JUDGE-V1_1 result (ruler T2 true-zero fix; criterion JUDGE-V1_1-criterion.md sha e4369cf0..., addendum 1 sha b77dad9a...; Haiku 5.5-low, both orders, N = 4; dev only)

TL;DR: **NO-ADOPT by the frozen rule.** The true-zero line fixes the decline arm completely (a, b, c all U 0.000, every dimension 1.0 on 30/30), but it
moves ordinary answers: 7/40 CE flips (bar <= 2) and test-retest SD 0.0265 (bar 0.0206, v1 same 20 ids). Mean |dn| 0.031 passes (bar 0.05).
W2 not run (it was reserved for a validity failure); stop per rule 5. 1B anchor under v1.1 (addendum): 1.7B 0.318 vs 1.5B closed-book 0.272,
dU +0.047 (-0.0005...+0.097) -> **LEVEL**, not separable; 0 of the 1.7B's items went to zero.

## Diff judge.v1 -> judge.v1_1 (W1; system prompt only, one line inserted before "- Do not use tools.")
    judge.v1 bytes unchanged: boar-eval/scorers/vendor/eval-lib/judge-core.mjs (sha 521f7ad3...), harness/judge.mjs (sha bda1aeb5...)
    new: boar-eval/scorers/vendor/eval-lib-v1_1/judge-core.mjs (boar-eval f16f159), used via BOAR_EVAL_LIB
     - Declare 'tie' when the answers are of practically equal quality.
    +- True zero: if an answer declines, defers, says it cannot answer, or contains no checkable claim about the question, score that answer correctness = 1, completeness = 1, usefulness = 1, regardless of tone. A partial answer is scored on what it asserts.
     - Do not use tools. Return only the structured verdict.
Pre-registered W2 (eval-lib-v1_1b, not run): same slot, "overrides the others", adds "redirects the user to other sources" and "Asserting nothing is not the same as being correct".

## Results (aggregates/W1.json, W1-sep.json, W1-sep-sens.json under v1_1/)
| Check | judge.v1 | judge.v1_1 (W1) | Bar | Verdict |
|---|---|---|---|---|
| (a) bare refusal U (CI) | 0.058 (0.037-0.081) | 0.000 (0.000-0.000) | CI high <= 0.05 | pass |
| (b) hedged U | 0.053 (0.034-0.075) | 0.000 (0.000-0.000) | same | pass |
| (c) fluent no-content U | 0.016 (0.009-0.025) | 0.000 (0.000-0.000) | same | pass |
| 40 controls, mean abs dn (n = (s-1)/4) | ref = mean of 3 v1 repeats | 0.031 (correct 0.036, wrong 0.026; signed +0.009) | <= 0.05 | pass |
| 40 controls, CE flips vs v1 majority | v1 single repeat: 2 / 0 / 3 | **7** | <= 2 | **FAIL** |
| 20 retest, mean item SD | 0.0206 (same ids, 2 repeats); full-97 0.0286 | **0.0265** (9/20 identical s, CE same 18/20) | <= 0.0206 | **FAIL** |
- All 7 flips go the same way: v1-majority CE (wrong) answers get correctness 2.0 instead of 1.0-1.5 (vit-cry-005, vit-cry-003, vit-cry-009, vit-cry-010,
  vit-sci-002, st-qa-money-se-020, st-qa-cooking-se-003). Mean correctness on the 40: 2.69 (v1) -> 2.76. Reading (post hoc): "a partial answer is scored on
  what it asserts" lifts wrong-but-specific answers from 1 to 2, right at the CE threshold 1.5; the rule does not over-fire on content (no control moved > 0.1 in n).
- U on the 40: v1 rep1 0.281 -> v1.1 0.296.

## Addendum 1: 1B anchor re-score (v0.1 57; 228 calls)
| Judge | U 1.7B K0 control | U 1.5B closed-book | dU (CI) | Position |
|---|---|---|---|---|
| v1 (FLOOR, n 57, 6 identical-text items reuse control rows) | 0.294 | 0.259 | +0.035 (-0.019...+0.089) | LEVEL |
| v1.1 (frozen estimator, all 57 judged) | 0.318 (0.259-0.378) | 0.272 (0.209-0.332) | **+0.047 (-0.0005...+0.097)** | **LEVEL**, not SEPARABLE |
| v1.1 sensitivity: control rows reused for the 6 identical items (as FLOOR) | 0.318 | 0.270 | +0.049 (+0.001...+0.099) | (ABOVE by 0.001; not a rule) |
| v1.1 sensitivity: model-path items only (n 51) | 0.276 | 0.222 | +0.054 (-0.001...+0.107) | LEVEL |
- Items went to zero (s 1.000 under v1.1, > 1 under v1): 1.7B **0** (the control declines 0/57); 1.5B 3 (vit-hum-005, vit-hlt-003, dng-005). Items 1.7B better/worse 28/19.
- Reading: the gap widens slightly (+0.035 -> +0.047) but the CI still touches 0 under the frozen estimator. The research page cannot say "better than a 1B";
  "level with a closed-book ~1B on dev, gap +0.05 at the edge of significance" is the most it supports. Caveat: v1.1 itself was not adopted.

## Next (for the coordinator, not run)
- The validity fix works with one line; the cost is on the CE threshold. Options: keep the line and move CE to the true-zero-aware definition
  (correctness <= 2 on v1.1), or drop the "partial answer" sentence. Either is a new criterion; nothing here is re-run to rescue W1.

## Budget and provenance
- Haiku 528 calls (W1 validity 180, controls 80, retest 40, addendum 228) of the 640 cap; 0 Opus, 0 paid API, 0 generation, no phone, no mini. Ledger v1_1/runs/calls.ledger.
- Timing: addendum 1 arrived after the W1 validity run and was frozen before any of its calls and before the controls/retest.
- Dev only: bench v0.1 + selftest qa-cooking-se / qa-money-se. No v0.4, blind/ or rnd/veil file read.
