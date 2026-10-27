# SAMPLE2-GATE: best-of-2 seeds picked by the GATE17 groundedness gate, stage-1 pool screen (2026-10-21)

TL;DR: **NO-GO.** dU **+0.003 (-0.007 ... +0.014)** on the 87 stage1-pool ids (K0) vs the seed-42 control. Bar was dU >= +0.03 with CI low > 0. The CI excludes +0.03. Stage 2 does not run.
The gate does pick the better answer more often than the worse one (10 up, 5 down, 4 equal among its 19 swaps; CE 29 -> 26), but only 38 of the 87 items can be gated and half of those keep seed 42, so the pool-level gain is about 0.003 U.
Criterion SAMPLE2-criterion.md (sha256 5e59c13c... at freeze, commit 081c410c before generation; Budget block 39d39511..., b3e43fd1). Judge Haiku 5.5-low judge.v1-low, N = 4, both orders, only the 19 seed-43 picks: 38 calls (cap 150). 0 Opus, 0 paid.

| metric (87 ids) | control (seed 42) | best-of-2 by gate |
|---|---|---|
| U | 0.396 | 0.399 (dU +0.003, CI -0.007 ... +0.014) |
| CE (agg_run) | 29 | 26 (rate -0.034, CI -0.081 ... +0.012) |
| CE-unwarned (labels.py) | 11 | 10 (fixed 1, new 0) |
| refusals R (decline or warned) | 39 | 37 (2 lifted, 0 new) |
| shown LLM answers with a [n] | 18/44 | 20/46 |
| seed-43 text differs from seed 42 | - | 76/87 |
| eligible for the gate (differ, both LLM, no decline, kept parity, context) | - | 38 (kept parity 87/87; context present 40) |
| seed 43 picked | - | 19/38 (0 ties) |
| RD-1 conversion (FACTPRESENT K0 present, corr >= 4) | 3/7 | 4/7 (lan-exp-004 2.5 -> 4.0) |

Cost (mini M4 CPU, -t 4)
- Decode: x2 nominal. Generated tokens 3 594 (s42) + 3 641 (s43). Generation wall 188 s + 201 s for the 87 (sum of per-item totalMs).
- Gate: 2 calls per eligible item (76 calls). Gate prompt p50 383 / p90 530 tokens, prefill p50 1.8 s / p90 2.6 s per call (sum 145 s), so about 3.8 s per gated item on the mini on top of the second generation. On a phone this is a second full answer plus two prefills of about 400 tokens.

Reading
- Per-item selection works in the expected direction: the gate's picks gain on 10 items and lose on 5. The ceiling is set by scope, though. In K0 only 40 of the 87 pool items have kept context, and the gate cannot score memory answers (the 37 warned ones).
- Seeds differ on 76/87 items. Best-of-2 by an oracle would be larger (DEEPBO2 found +0.038 for the deep tier), but the gate is a weak proxy for correctness (GATE17: AUC about 0.5 for CE).
- Not a null run: the seed-43 sample alone is judged only where it was picked. A full s43 judgment (about +114 calls) would give the pool's first null and the oracle best-of-2 ceiling.

Limits: one pair of seeds, Haiku-low labels, K0 only (with K1/K3 more items have context, so the gate would have more scope; untested).
Files: tools/ (gen_dump.sh, s2g.py, run_gate.sh, judge_agg.sh, report.py), gate/ (s2g.inputs.jsonl, s2g.outputs.jsonl, items.json, selection.json), traces/ (s43 dump traces + prompts, composite traces), judgments/, aggregates/ (sample2-gate-K0-stage1-pool-s42s43.json, sample2-gate.report.json).
