# SEFIX F1b answer screen (MAIN 97, 13-pack kit with v3 cooking/money, RS_MERGE=gidf, packHeadPass a2 + packDense2 extra, K1 tree, seed 42, Qwen3-1.7B, Haiku 5.5-low judge.v1 N 4 both orders) - EXPLORATORY

Criterion SEFIX-criterion.md (sha 07ea2b5e), LEVER-CANDIDATE clause. Controls reused, not regenerated: ARM-G (compose/screen traces + judge rows), K3 control (null-cal/control/pool-K1.json). Aggregator ans-tools/agg_f1b.py; data answers-f1b.json; judge rows ans-judge/F1B (+F1B2); ledger CALLS.md (132 Haiku of 300).
Divergence-first: changed = kept (title, section, source) differs AND text differs vs ARM-G = 64 items (v0.1 33, cooking 13, money 18); the other 33 reuse ARM-G rows (31 text-identical; 2 text-only changes, lan-exp-004/005, have the same kept titles but other chunk ids, prompt 667->584 / 741->597 tokens; judged as a sensitivity).
Sanity: 97/97 rows, 0 errors, 0 empty, 0 loops, 24/24 deterministic items byte-identical to ARM-G; kept-list identity vs the F1b replay 94/97 = 96.9 % (ARM-G vs its replay 88/97); the 3 misses (cooking-009, cooking-014, money-018) are live traces with one more chunk than the replay (live headpass/repack), never fewer.

| set | arm | U | corr | use | CE | CE unwarned | warned | out tok | totalMs |
|---|---|---|---|---|---|---|---|---|---|
| all 97 | K3 control | 0.4102 | 2.536 | 1.613 | 29 | 12 | 46 | 36.43 | 4449 |
| all 97 | ARM-G | 0.4167 | 2.582 | 1.634 | 24 | 14 | 40 | 34.54 | 5594 |
| all 97 | **F1b** | 0.4009 | 2.443 | 1.593 | 32 | **18** | 36 | 32.32 | 3748 |
| changed 64 | K3 control | 0.3648 | 2.273 | 1.453 | 22 | 7 | 38 | 47.44 | 5903 |
| changed 64 | ARM-G | 0.3846 | 2.430 | 1.508 | 14 | 5 | 34 | 45.44 | 7431 |
| changed 64 | **F1b** | 0.3584 | 2.219 | 1.430 | 23 | 10 | 31 | 42.62 | 4918 |
totalMs is not comparable across arms (ARM-G ran two jobs in parallel on the mini, F1b alone); declined 0 everywhere.

Paired dU (item bootstrap B 2000 seed 11):
- F1b vs ARM-G, changed 64: **-0.0262 [-0.0510, -0.0019]** (dcorr -0.211 [-0.414, -0.031]); 66 incl. the 2 text-only: -0.0232 [-0.0475, +0.0013]; all 97: -0.0158 [-0.0340, +0.0015]
- F1b vs K3 control, all 97: **-0.0093 [-0.0329, +0.0125]** (dcorr -0.093 [-0.278, +0.077]); ARM-G itself +0.0065 [-0.0155, +0.0287]
By source, changed vs ARM-G: v0.1 n 33 -0.0606 [-0.0983, -0.0269] (corr 2.697 -> 2.333, CE 6 -> 11); cooking n 13 -0.0013 [-0.0525, +0.0563]; money n 18 +0.0219 [-0.0113, +0.0612]. All items vs K3 control: v0.1 -0.021 [-0.052, +0.007], cooking +0.024 [-0.020, +0.072], money -0.008 [-0.057, +0.048].
2x2 fact present (G flag x F1b flag, changed items, live kept = replay kept needed): A/A 20: corr 1.95 -> 1.70, dU -0.028; **A->P 14: corr 2.25 -> 2.25, dU 0.000**; P->A 2 (lan-hlt-002, vit-trv-003: lost by the extra mode): -0.089; P/P 20: -0.020; no flag 8: 2.81 -> 1.88.
The 14 newly delivered cm facts (13 confirmed fact-present in the live kept text): corr K3 control 2.107 -> ARM-G (fact absent) 2.286 -> F1b (fact present) 2.250; dU vs ARM-G +0.0014 [-0.051, +0.053]. Up >= 1: money-003, money-017; down >= 1: cooking-010. 9 of the 14 answers still carry the "Not found in this phone's offline library" line (ARM-G also 9): the engine's grounding gate does not trust the delivered chunk, so delivery does not turn into answers.
CE: F1b all-97 CE-unwarned 18 vs ARM-G 14 vs control 12 = **up**. On changed items 11 CE new vs 2 fixed vs ARM-G; unwarned new: lan-hlt-003, lan-cmp-003, trv-004, cooking-016, money-012 (3 are v0.1/non-cm items). Fewer warnings (36 vs 40) are part of the rise: wrong answers lose the warning line when more sources are kept.
Attribution caveat: no live v2+extra arm was run, so the v0.1 loss (-0.061 on 33 items) cannot be split between the extra mode and the sidecars (replay: v0.1 kept 28 -> 27 for both).

Rule (frozen): vs ARM-G changed dU >= +0.02 & CI low > -0.01: NO (-0.026, CI low -0.051); vs K3 control all 97 dU >= +0.02 & CI low > -0.01: NO (-0.009, CI low -0.033); CE-unwarned not up: NO (18 > 14, > 12). **Verdict: NO (not a LEVER-CANDIDATE).** Prediction was +0.03...+0.06 on changed items (flagged optimistic: the cm questions were written from the threads); measured -0.026.
