# RETRIEVE-SWEEP stage 1 (0 LLM): arms x metrics

QFORM n 432 (hit@kept, paired vs B0; CI = item bootstrap B 2000 seed 11; fact-cluster CI beside it). Junk set = 206 items whose gold is not in B0's wide-12. MAIN 97 = K1 kit + K1 settings; recovery = of the funnel's 25 S2/S3 ids, fact PRESENT in the arm's kept list and not in the switch-off replay; losses = of the 22 S4/S5 ids, PRESENT in the switch-off replay and not in the arm.

| arm | hit@kept | Δ vs B0 pts [CI item] | [CI fact] | gained/lost | QFORM dropped-25 kept | recovery /25 | losses /22 | junk-kept (B0 ×) | mean kept | ctx tok after compr. | kept tok | wall ms/q (mean) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B0 stock (QFORM replay) | 41.4 (179) | +0.0 [+0.0, +0.0] | [+0.0, +0.0] | 0/0 | 0/25 | 0 | 0 | 1.53 (1.00) | 1.83 | 276 | 191 | 88 | - |
| B1 K1 settings (head pass a2 + dense append-budget) | 45.4 (196) | +3.9 [+2.1, +5.8] | [+2.1, +6.0] | 17/0 | 7/25 | - | - | 3.02 (1.97) | 3.25 | 276 | 438 | 92 | - |
| A78 GROUND-DENSE tau 0.78 | 43.1 (186) | +1.6 [+0.7, +3.0] | [+0.5, +3.0] | 7/0 | 7/25 | 0 | 0 | 1.55 (1.01) | 1.88 | 276 | 196 | 93 | no |
| A74 GROUND-DENSE tau 0.74 | 44.0 (190) | +2.5 [+1.2, +4.2] | [+1.2, +4.2] | 11/0 | 11/25 | 0 | 0 | 1.63 (1.06) | 1.95 | 276 | 205 | 138 | no |
| B KEYQ | 42.4 (183) | +0.9 [-0.7, +2.5] | [-0.5, +2.3] | 8/4 | 0/25 | 2 | 1 | 1.60 (1.04) | 1.86 | 287 | 192 | 134 | no |
| C SIBLING (on K1 settings) | 49.3 (213) | +7.9 [+5.3, +10.6] | [+5.6, +10.4] | 34/0 | 9/25 | 1 | 0 | 3.67 (2.40) | 4.15 | 274 | 583 | 2630 | no |
| D DIVERSITY | 41.2 (178) | -0.2 [-0.7, +0.0] | [-0.7, +0.0] | 0/1 | 0/25 | 0 | 0 | 1.52 (0.99) | 1.83 | 276 | 192 | 86 | no |
| E MINSIM 0.62 (dense) | 39.8 (172) | -1.6 [-2.8, -0.5] | [-3.0, -0.5] | 0/7 | 0/25 | 0 | 2 | 1.36 (0.89) | 1.64 | 251 | 170 | 87 | no |
| F COMBO exploratory = A74 + B (no arm passed) | 45.1 (195) | +3.7 [+1.6, +6.0] | [+1.6, +6.0] | 20/4 | 11/25 | 2 | 1 | 1.68 (1.10) | 1.99 | 287 | 207 | 448 | no |

## hit@kept % per form

| arm | F0 | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 |
|---|---|---|---|---|---|---|---|---|---|
| B0 | 50 | 10 | 62 | 25 | 42 | 83 | 50 | 42 | 8 |
| B1 | 54 | 21 | 62 | 27 | 46 | 83 | 60 | 46 | 8 |
| A78 | 50 | 10 | 62 | 27 | 44 | 83 | 58 | 44 | 8 |
| A74 | 50 | 15 | 65 | 27 | 44 | 83 | 60 | 44 | 8 |
| B | 50 | 8 | 62 | 27 | 44 | 83 | 54 | 44 | 8 |
| C | 60 | 23 | 67 | 35 | 48 | 85 | 62 | 54 | 8 |
| D | 48 | 10 | 62 | 25 | 42 | 83 | 50 | 42 | 8 |
| E | 50 | 10 | 54 | 25 | 40 | 83 | 48 | 42 | 6 |
| F | 50 | 12 | 65 | 29 | 46 | 83 | 65 | 48 | 8 |

MAIN switch-off replay vs the funnel labels: S2/S3 fact present 0/25 (funnel: 0), S4/S5 present 22/22 (funnel: 22).
