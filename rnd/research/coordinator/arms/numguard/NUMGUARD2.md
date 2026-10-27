# NUMGUARD-2: with the numeric guard ON, does skipping retrieval on guard-fired turns that no calculator answered remove the fake citations with 0 harm? **PASS**

Criterion `NUMGUARD2-criterion.md` sha256 **209c103cb172c9981588d0c91e1a93328b5aff9b7d35ae5c615f3a9b1932a3f2**, frozen before any run (Ruleset 30, Precheck filled; deterministic-gate arm).
Patch `tools/numguard2.patch` sha256 **b182609c062391aefb0837a7fcf5cdb9959f52ac0cba5af543b5b081f00cb408** = numguard.patch (byte-identical hunks) + 6 lines in answer.ts after planAnswer: `if (numguard && NUMGUARD_NORETRIEVE === "1") { plan.retrieve = false; reasonCodes += "numguard:noretrieve" }`. Reaching planAnswer already means no calculator / arithmetic / travel / FACTS shortcut answered. NUMGUARD unset is the same as cut 7, and NUMGUARD=1 alone is the same as numguard.patch. Tree `kiln-local/be-0cfd4a77-cut7-numguard` patched in place (answer.ts cecf61e9…; runner `tools/run_ng2.sh` pins it; `run_ng.sh` now refuses this tree by design). `tsc --noEmit` clean and routing vitest 592/592 on a scratch copy of wt/cut7 with numguard2.patch applied (resulting answer.ts sha matches the kiln tree).
Seed 42, llama-server b11010 CPU --threads 4, claim kit, mmbert detector :8094 (untouched). **Judge calls: 0** (paid 0). Generation wall 832 s (smoke 32 + slice 152 + v0.1 648), replay 7 s.

## Result
| measurement | result |
|---|---|
| Smoke (5 guard-fired slice items, both flags) | rc 0, 5/5 correct; `numguard:noretrieve` on mr-u07 and mr-a02 (retrieval.raw 0); vit-sci-003, mr-a07 (calculator-rate-time), mr-a04 (calculator-battery) unchanged |
| Slice 26 (score_mr.py), A / NG / NG2 | correct 23 / 26 / **26**; cited 4 / 6 / **4**; retrieved 15 / 14 / 12; headline 18 / 21 / 20; extra (> 2 sentences) 5 / 5 / 7; p50 model-only 7.0 / 7.0 / 8.6 s |
| Slice per item NG → NG2 | only mr-u07 and mr-a02 change (24/26 byte-identical); 0 correct→wrong; both lose the [1] (cited 2 → **0** on guard-fired model-answered items). The 4 remaining cited items (mr-u04, mr-u08, mr-t01, mr-t06) are not guard-fired and are the same as A |
| v0.1 60 NG2 vs NG ON (v01-ng-on-s42) | answers changed **0/60**, reason codes changed 0/60, kept lists changed 0/60; same_answer 60/60 (42/42 LLM with the same prompt length). Only numeric guard fire: vit-sci-003, answered by the calculator, so noretrieve does not apply |
| Route replay (0 LLM, `runs/route-replay2.*`; detector p equals the NUMGUARD replay on 306/306) | changed turns: **180 self-tests 0**; slice 2 (mr-u07, mr-a02, the same ids as generation); v0.1 0. Info only (outside the 180): st-qa-cooking-se-005 and st-qa-money-se-004 would go closed-book |

## The 2 changed items (NG → NG2)
| item | NG (retrieval on) | NG2 (closed-book) |
|---|---|---|
| mr-u07 2.2 bar → psi | "≈ 32 psi … (2.2 × 14.7 ≈ 32.34 psi) [1]" ✓ cited | "2.2 bar is approximately 32 psi." + 2 sentences of tyre advice ✓ no citation |
| mr-a02 bus 9:40 + 2 h 35 | "The bus arrives at 12:15 [1]." ✓ cited | "Add 2 hours 35 minutes to 9:40 … It arrives at 12:15." ✓ no citation |

## Worst 3 (quoted briefly)
1. mr-u07 NG2 adds advice nobody asked for ("Most car manufacturers recommend between 30–35 psi…"). Slice extra goes 5 → 7, and the closed-book 4B pads its answers. Not harm under the rule, but it is a length cost.
2. mr-a02 NG2 no longer leads with the answer (headline 21 → 20). The number is correct and comes in the last sentence.
3. Reason codes keep `retrieve:yes` from planAnswer next to `numguard:noretrieve` (as in MATHROUTE's override). This is cosmetic, and a PR version should set retrieve inside planAnswer. Also, st-qa-money-se-004 (a PayPal [usage detail removed] scam question, outside the 180) would lose retrieval under NG2, which is a likely downside for numeric-looking non-math questions the guard admits.

## Verdict (frozen rule)
**PASS.** Slice 26/26 with 0 correct→wrong vs NG, 0 citations on the guard-fired model-answered items (2 → 0), 0 changed answers on v0.1 (all 60, including the non-numeric ones), 0 changed turns on the 180 self-tests. Product/credibility arm, not a bar lever. Caveat for the PR: currency-only numeric intent (the money-se-004 pattern) should probably keep retrieval.

## Files
tools/ (numguard2.patch + .sha256, run_ng2.sh, route_replay2.mts), runs/ (ng2-smoke-s42.*, ng2-A-s42.*, v01-ng2-on-s42.*, v01-compare-ng-vs-ng2.json, v01-same_answer-ng-vs-ng2.txt, route-replay2.jsonl/.txt, gen_ng2.log), aggregates/ (numguard2.json, score_slice2.json).
Exposure: dev + public sets only; blind/ and rnd/veil/ not read.
