# B-HONEST (K0, Qwen3-1.7B, 2026-10-20): stage 1 NO-GO, stage 2 not run

TL;DR: the D4 honest strings ported to the 1.7B path (succinct persona + honest CONTEXT_INSTRUCTION) fix 4 of 23 control CEs on the screen (need 6), with 1 sentinel worse (max 1). NO-GO; arm ends.

| Item | Value |
|---|---|
| Patch | b-honest.patch sha256 799c8823...; personalities.ts succinct systemPrompt += honest/facts-only/capability sentences (= S3 string); pure.ts CONTEXT_INSTRUCTION = honest variant; nothing else |
| Criterion | B-HONEST-criterion.md sha256 3ac3efca...; committed with the patch and tools/verdict.py as 22f4674a before generation |
| Screen run | b-honest-K0-screen-s42, mini, 37 items, 26 changed answers, 52 Haiku calls, 0 Opus, 0 paid |
| Screen deltas vs mini control (n 37) | U +0.012 (-0.015...+0.043), CE -0.054 (-0.189...+0.081), decline 0; CE count 21 vs 23; warned 17 vs 16; refusal_like 0 |
| Stage 2 | not run: NO-GO |

## Gate output (verbatim)
```
screen K0: problems 27 (CE in mini control 23) | fixed 4 (need >= 6) | still CE 21 | sentinels worse 1/10 (max 1) | changed answers 26/37 -> NO-GO
  fixed lan-cmp-005 1.0 -> 3.5
  fixed st-qa-money-se-009 1.0 -> 2.5
  fixed vit-cry-003 1.5 -> 2.0
  fixed vit-cry-005 1.0 -> 2.0
  sentinel worse st-qa-money-se-002 corr 3.5->2.5
```
Judge-noise caveat (SCREENS.md): ~5 % of changed CE items flip by noise alone; 4 fixes is consistent with that. Two of the four "fixed" items only move to 2.0 (vit-cry-003, vit-cry-005), still wrong.

## Examples of "fixed" CE (verbatim; control -> candidate)
1. lan-cmp-005 (corr 1.0 -> 3.5). Control: "The Nile crocodile is larger than the saltwater crocodile [1]." Candidate: "Not found in this phone's offline library. From the model's memory, may be wrong:\nThe saltwater crocodile grows bigger than the Nile crocodile." (the released path now warns and gets it right; this reads as a sampling/route shift, not caution).
2. st-qa-money-se-009 (1.0 -> 2.5). Control: "A regular brokerage account is generally better for 401(k) withdrawals because they are taxed as ordinary income, not capital gains. ..." Candidate: "A regular brokerage account is not generally the better deal for 401(k) withdrawals due to taxation as ordinary income. The capital-gains rate is typically lower than ordinary income tax rates." (flips the claim, still off-target).
3. vit-cry-005 (1.0 -> 2.0). Control and candidate both start with the warning line and both give an invented Privacy Pools description; the candidate is only slightly less wrong.

New refusals: none (declined 0, refusal_like 0 on all 37). The one worse sentinel is a correctness drop (st-qa-money-se-002 3.5 -> 2.5), not a refusal.

Reading: the honest sentences did not make the 1.7B abstain or hedge ("I don't know" never appeared); it keeps answering confidently, so CE is barely moved. Files: aggregates/b-honest-K0-screen-s42.{json,gate.txt,gate.json}, traces/, judgments/, runs/logs/.
