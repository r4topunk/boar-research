# RETRIEVE-SWEEP stage 1 (0 LLM): arms x metrics

QFORM n 432 (hit@kept, paired vs B0; CI = item bootstrap B 2000 seed 11; fact-cluster CI beside it). Junk set = 206 items whose gold is not in B0's wide-12. MAIN 97 = K1 kit + K1 settings; recovery = of the funnel's 25 S2/S3 ids, fact PRESENT in the arm's kept list and not in the switch-off replay; losses = of the 22 S4/S5 ids, PRESENT in the switch-off replay and not in the arm.

| arm | hit@kept | Δ vs B0 pts [CI item] | [CI fact] | gained/lost | QFORM dropped-25 kept | recovery /25 | losses /22 | junk-kept (B0 ×) | mean kept | ctx tok after compr. | kept tok | wall ms/q (mean) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B0 stock (QFORM replay) | 41.4 (179) | +0.0 [+0.0, +0.0] | [+0.0, +0.0] | 0/0 | 0/25 | 0 | 0 | 1.53 (1.00) | 1.83 | 276 | 191 | 88 | - |
| H3 COMPRESS-KEEP-HEAD (RS_COMPRESS_HEAD=1, TOK 160) | 41.4 (179) | +0.0 [+0.0, +0.0] | [+0.0, +0.0] | 0/0 | 0/25 | 0 | 0 | 1.66 (1.08) | 2.02 | 327 | 212 | 315 | no |

## hit@kept % per form

| arm | F0 | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 |
|---|---|---|---|---|---|---|---|---|---|
| B0 | 50 | 10 | 62 | 25 | 42 | 83 | 50 | 42 | 8 |
| H3 | 50 | 10 | 62 | 25 | 42 | 83 | 50 | 42 | 8 |

MAIN switch-off replay vs the funnel labels: S2/S3 fact present 0/25 (funnel: 0), S4/S5 present 22/22 (funnel: 22).
