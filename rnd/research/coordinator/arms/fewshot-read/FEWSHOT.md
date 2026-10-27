# FEWSHOT-READ: two worked examples in the 1.7B lite prompt, stage-1 pool screen (2026-10-21)

TL;DR: **NO-GO.** dU **-0.001 (-0.015 ... +0.014)** on the 87 stage1-pool ids (K0, seed 42, mini) vs the mini K0 control. Bar was dU >= +0.03 with CI low > 0. The CI excludes +0.03, so this is a clean null at screen resolution, not an underpowered miss. Stage 2 does not run.
Criterion FEWSHOT-criterion.md (sha256 86bc3115... at freeze, commit 081c410c before generation; Budget block added before judging, 3ee18ec4..., b3e43fd1). Judge Haiku 5.5-low judge.v1-low, N = 4, both orders, changed answers only: 82 calls (cap 150). 0 Opus, 0 paid.

| metric (87 ids) | control (K0 s42) | FEWSHOT-READ |
|---|---|---|
| U | 0.396 | 0.395 (dU -0.001, CI -0.015 ... +0.014) |
| CE (agg_run) | 29 | 28 |
| CE-unwarned (labels.py) | 11 | 10 (fixed 3, new 2) |
| refusals R (decline or warned) | 39 | 36 (5 lifted, 2 new) |
| declines | 2 | 2 |
| shown LLM answers with a [n] | 18/44 | 21/47 |
| answers changed | - | 41 (16 up, 18 down) |
| prompt tokens where the patch fired (40 items) | p50 +287 tokens per call (sum +11 480) | |
| generated tokens (sum) | 3 594 | 3 382 |
| per-item totalMs p50 (mini) | 2 107 ms | 2 229 ms (+6 %) |
| RD-1 conversion (FACTPRESENT K0 present, corr >= 4) | 3/7 | 2/7 |

Reading
- The demonstrations change the format a little (3 more cited answers, 3 fewer warned) but not the reading: 41 answers move, up and down about equally (16 vs 18), and U is flat.
- This matches the closed instruction-only arms (LITE17, QUOTEFIRST, HONESTPROMPT <= 0.02): demonstrations are no better than instructions for the 1.7B. The prompt lever for lite reading stays closed.
- Cost if it had worked: about +287 prompt tokens (about +70 % of a typical 1.7B answer prompt) on every sourced answer.
- RD-1 conversion on the 7 pool items with the fact present in K0: 3/7 -> 2/7 (n tiny; per item control -> arm: lan-exp-002 4.5 -> 4.0, lan-exp-004 2.5 -> 2.0, lan-exp-005 4.0 -> 3.0, lan-exp-007 1.5 -> 1.0, lan-rsn-006 4.5 -> 4.0, vit-cry-003 2.0 -> 2.0, vit-cry-006 1.0 -> 1.0). The few-shot block does not raise the use of a present fact.
- Largest moves: lan-cmp-005 corr 1.0 -> 4.0 (CE fixed), st-qa-ethereum-se-017 1.0 -> 3.0; lan-cmp-003 4.0 -> 1.5 (warned both), st-boar-factbook-006 2.0 -> 1.0.

Limits
- One seed. The 1.7B seed-to-seed r is 0.66 on MAIN (DIVERGENCE-MAP), and no null exists on this pool, so the CI is the paired item bootstrap only. That does not change the verdict: the point estimate sits at 0.
- K0 has kept context on only 40 of the 87 ids, so the patch fires on 40. The other 47 are byte-identical to the control.
- Haiku-low labels only.

Files: fewshot-read.patch (sha256 e2fb3306...), traces/, judgments/, aggregates/fewshot-read-K0-stage1-pool-s42.json, aggregates/fewshot-read.report.json (sample2-gate/tools/report.py), runs/logs/.
