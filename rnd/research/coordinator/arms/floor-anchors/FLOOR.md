# FLOOR-ANCHORS result (RJ2-FLOORANCHORS; criterion FLOOR-criterion.md sha ed88f377...; Haiku 5.5-low judge.v1, both orders; dev v0.1)

TL;DR: **decline arm INVALID under the R4 judge.** The bare refusal (a) and the hedged non-answer (b) score U above 0.05 because judge.v1's
correctness dimension rates a non-answer "not wrong" (2-3 of 5); completeness and usefulness are exactly 1 for every variant. The fluent
no-content answer (c), the variant the hypothesis feared, passes. T2 must change before 10-24. **1B separability: NOT SEPARABLE ON DEV** (the closed-book 1.5B is only 0.035 U below the 1.7B K0 control, CI includes 0).

## 1. Decline validity (n 30 stratified ids, 180 Haiku calls; aggregates/floor-decline.json)
| Variant | U floor-adj (CI) | raw | items s > 1 | mean corr / compl / useful | rule (U CI high <= 0.05) |
|---|---|---|---|---|---|
| (a) bare refusal | 0.058 (0.037-0.081) | 0.257 | 18/30 | 1.65 / 1.00 / 1.00 | FAIL |
| (b) hedged non-answer | 0.053 (0.034-0.075) | 0.252 | 17/30 | 1.60 / 1.00 / 1.00 | FAIL |
| (c) fluent no-content, 265 words | 0.016 (0.009-0.025) | 0.224 | 10/30 | 1.18 / 1.00 / 1.00 | pass |
Win/tie/loss vs the reference: 0/0/30 for every variant.

Mechanism (post hoc, diagnostic, not a rule): U on completeness + usefulness only = 0.000 for all three variants; U on correctness alone =
0.182 (a), 0.165 (b), 0.050 (c). Typical rationale: the answer "declines to answer, so it is not wrong but gives the user nothing" -> correctness 3.
So the leak is one rubric dimension, not verbosity: a shorter refusal earns more than a fluent empty answer.

Reading: the spec's precondition fails on dev under the Claude family; no app result on v0.4 may be read under judge.v1 as is. Candidate T2
fixes (from the hypothesis' kill clause; choose before 10-24, re-run this decline check unchanged on the fixed judge): (i) checklist-point
scoring (spec §3.1: s = met points / K; a refusal meets none), (ii) an explicit true-zero rule in the judge prompt (a non-answer scores 1 on every
dimension), or (iii) U on completeness + usefulness only. The texts are frozen; not tuned after these scores.

## 2. 1B separability (n 57)
Qwen2.5-1.5B-Instruct Q4_K_M closed-book (0 kept / 0 raw sources on 57/57, weights sha 1adf0b11 in every trace) vs the 1.7B K0 control s42.
102 Haiku calls (51 changed answers; 6 answers byte-identical to the control reuse its rows: calculator and first-aid-card layers).
| Arm | U (CI) | raw | W/T/L vs ref | corr / compl / useful |
|---|---|---|---|---|
| 1.7B K0 control (with retrieval) | 0.294 (0.234-0.355) | 0.443 | 0/1/56 | 2.89 / 1.70 / 1.70 |
| ~1B closed-book (1.5B) | 0.259 (0.195-0.325) | 0.415 | 0/2/55 | 2.54 / 1.68 / 1.69 |
- Paired U(1.7B) - U(1B) = **+0.035 (-0.019...+0.089)**, items 24 better / 17 worse -> rule 2: **NOT SEPARABLE ON DEV**.
- Sensitivities (no rule): two-seed control +0.036 (-0.015...+0.089); without the 6 deterministic-layer items +0.038 (-0.023...+0.098).
- 1B-fail-like items (1B s <= 2 and control s >= 4): 0. The 1B declined 0/57; confident errors 19 vs 13 (run_arm aggregate).
- Reading: on v0.1 dev under judge.v1 the 1.7B K0 control is not distinguishable from a closed-book ~1B; the gap is almost all in the correctness
  dimension (completeness/usefulness 1.70 vs 1.68). The research page withdraws the separability claim for the 1B anchor (reports it as "not
  separable on dev"). Caveat: the anchor is 1.5B, not 1B (present file rule); v0.4 n 75 and a fixed T2 may differ.
- Deviation (sensitivity only): the non-model-path set is defined as answers byte-identical to the control (6), because three first-aid card
  answers carry a generate reason code; the frozen rules do not use it.
