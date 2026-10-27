# SHORTCTX (K1): stage 1 NO-GO

TL;DR: capping the 1.7B's context at 2 chunks / ~350 tokens on pack set K1 fixed 4 of 27 confident-error problems (need 6); sentinels intact. Stage 2 not run.

| Item | Value |
|---|---|
| Candidate | shortctx.patch sha256 `3b9cac98c098...b259` (answer.ts only, -p1; no env override exists for k/budget) |
| Criterion | SHORTCTX-criterion.md sha256 `865cb4f5f2b6...6a18`, committed 7eb25db5 before generation |
| Screen (37 items vs mini K1 control) | U 0.3626 vs control, delta -0.0175 (-0.047..+0.010); CE 20 vs 22 |
| Prompt tokens (28 items with timing) | mean 754 -> 502, p50 761 -> 529 |
| Haiku calls | 44 (cap 160) |

Gate output (verbatim):
```
screen K1: problems 27 (CE in mini control 21) | fixed 4 (need >= 6) | still CE 19 | sentinels worse 0/10 (max 1) | changed answers 22/37 -> NO-GO
  fixed lan-rsn-003 1.0 -> 2.0 / st-qa-cooking-se-020 1.5 -> 2.5 / trv-004 1.5 -> 2.0 / vit-cry-005 1.5 -> 2.0
```
Fixed items moved only 0.5-1.0 points and stay near the CE line (about 5 % judge noise per item applies). 19 problems remain CE.

## Examples
- lan-rsn-003 (pronghorn): control = warning + memory answer; candidate cites source [2] with the same fact, 1.0 -> 2.0, still CE.
- vit-cry-005: both answers are the not-found warning + memory text; the wording shifts, 1.5 -> 2.0 by noise.
- st-qa-cooking-se-003: both warned memory answers; the candidate is shorter, still CE.

Reading: a shorter context cuts prompt tokens by a third but does not make the 1.7B use the Simple Wikipedia chunks; most problem items answer from memory behind the warning in both arms.
Verdict: NO-GO, stage 2 not run, no K1 MAIN control generated.
