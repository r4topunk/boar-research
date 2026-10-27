# JUDGE-V1_1B result (second true-zero wording W3 = judge.v1_1c; criterion JUDGE-V1_1B-criterion.md sha d3bc9734...; Haiku 5.5-low, both orders, N = 4; dev only)

TL;DR: **NO-ADOPT; stop.** Dropping "A partial answer is scored on what it asserts." keeps the decline fix (a, b, c all U 0.000) but ordinary answers still
move: 5/40 CE flips (bar <= 2) and test-retest SD 0.0295 (bar 0.0206). The 1B re-score was not run (rule 5 needs ADOPT). **The ruler keeps judge.v1**, and declines
are handled by the pre-registered decline-arm subtraction (below), with its limitation stated.

## Wording
- W3 = W1 minus the 48 characters " A partial answer is scored on what it asserts." and nothing else. Lib boar-eval/scorers/vendor/eval-lib-v1_1c (boar-eval 37a2d3b).
- The pre-registered eval-lib-v1_1b (W2) was NOT used. It differs from W1 in more than that sentence: it adds an override clause, "redirects the user to other sources",
  and "Asserting nothing is not the same as being correct", and it KEEPS the partial-answer sentence. The request said to keep only the one change.
- Diff judge.v1 -> judge.v1_1c (system prompt; one line inserted before "- Do not use tools."):
      +- True zero: if an answer declines, defers, says it cannot answer, or contains no checkable claim about the question, score that answer correctness = 1, completeness = 1, usefulness = 1, regardless of tone.

## Results (v1_1/aggregates/W3.json; same ids and bars as JUDGE-V1_1)
| Check | judge.v1 | W1 (v1_1) | **W3 (v1_1c)** | Bar | W3 verdict |
|---|---|---|---|---|---|
| (a) bare refusal U (CI) | 0.058 (0.037-0.081) | 0.000 | **0.000 (0-0)** | CI high <= 0.05 | pass |
| (b) hedged U | 0.053 (0.034-0.075) | 0.000 | **0.000 (0-0)** | same | pass |
| (c) fluent no-content U | 0.016 (0.009-0.025) | 0.000 | **0.000 (0-0)** | same | pass |
| 40 controls, mean abs dn | (ref: mean of 3 v1 repeats) | 0.031 | **0.037** (correct 0.049, wrong 0.024; signed -0.004) | <= 0.05 | pass |
| 40 controls, CE flips | single v1 repeat vs majority: 2 / 0 / 3 | 7 | **5** | <= 2 | **FAIL** |
| 20 retest, mean item SD | 0.0206 (same 20 ids, v1 repeats 1-2); full-97 0.0286 | 0.0265 | **0.0295** (10/20 identical s, CE same 18/20) | <= 0.0206 | **FAIL** |
- SD reference: 0.0206 = judge.v1-low on the same 20 retest ids, repeats 1 and 2 (lp-screens control + judge-v2 rep2), computed with 0 LLM calls before JUDGE-V1_1.
  The 0.023 in the brief is judge.v2's full-97 SD (0.0229).
- All 5 flips go the same way as W1's: v1-majority CE answers with correctness 1.0-1.5 get exactly 2.0 (st-qa-cooking-se-012, -003, -007, st-qa-money-se-010,
  vit-sci-002). So the partial-answer sentence was not the only cause. Reading (post hoc, not tested): once the prompt names an explicit "1 = non-answer" anchor, the
  judge seems to reserve 1 for non-answers and puts specific-but-wrong answers at 2, right on the CE line (<= 1.5). U on the 40 hardly moves (0.281 -> 0.278).
  4 correct controls drop > 0.1 in n (lan-exp-005, lan-ref-005, st-qa-money-se-002, vit-trv-004).

## Fallback: judge.v1 + the decline-arm subtraction
- Decline floor under judge.v1 (Haiku 5.5-low, FLOOR.md): D = **0.058** (0.037-0.081) for the bare refusal; hedged 0.053, fluent no-content 0.016.
- Subtraction, using the CLAIM-DRAFT "above always-decline" form: U_net = (U - D) / (1 - D). With D 0.058: the 1.7B K0 control 0.294 -> 0.251 and the 1.5B anchor
  0.259 -> 0.213. The paired gap becomes +0.035 / 0.942 = +0.037 (-0.020...+0.094): **still LEVEL**, because subtracting a constant cannot separate them.
- Limitations to name on the card:
  - D is one judge family (Claude/Haiku) on 30 dev ids with a CI of about +/-0.02.
  - The leak depends on the wording (0.016-0.058) and on the item (s up to 1.83 on single items). One constant over-corrects fluent empty text and under-corrects terse refusals on "leaky" items.
  - It corrects totals, not items, so per-item CE and win-rate still treat a refusal as "not wrong" (correctness 2-3).
  - App refusals flagged by the trace are already zeroed by the z override (RULER-SPEC §3). The subtraction matters only for non-answers the judge does see: show-anyway answers, hedges, and the 1B and app arms.
- The research page still has no "better than a 1B" sentence: under v1 the gap is +0.035 (-0.019...+0.089), and under the rejected v1.1 it is +0.047 (-0.0005...+0.097), LEVEL both times.

## Budget and provenance
- Haiku **300 calls** (validity 180, controls 80, retest 40) of the 400 cap (+240 not used); 0 Opus, 0 paid API, 0 generation, no phone, no mini. Ledger v1_1/runs/calls-W3.ledger.
  Across both trials: 828 Haiku calls.
- Dev only (bench v0.1, selftest qa-cooking-se / qa-money-se). No v0.4, blind/ or rnd/veil file read. Stop per rule 6: no further wording under this criterion.
