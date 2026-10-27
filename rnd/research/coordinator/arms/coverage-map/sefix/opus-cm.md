# SEFIX-ALL Opus read, cooking/money units (judge.v1, claude-opus-5-5, N 4, both orders, seed 7; seed 42; control = K1 cm traces)

Judged set = 22 differing-text units of the 40 (20 of the 21 newly delivered cm facts whose text differs + 2 by id order); left unjudged for the 60-call cap: 16 differing units (cooking-004, cooking-008, cooking-009, cooking-011, cooking-012, cooking-014, cooking-020, money-001, money-005, money-008, money-009, money-011, money-014, money-015, money-017, money-018). Rows (new/pool): ctl 8/14, ALL 22/0.

| set | n | U ctl | U ALL | dU (CI) | win/tie/loss | dcorr | correct/100 ctl>ALL | CE/100 ctl>ALL | CE-unwarned ctl>ALL | decl/100 ctl>ALL |
|---|---|---|---|---|---|---|---|---|---|---|
| judged (22) | 22 | 0.1565 [0.0954, 0.2159] | 0.3295 [0.2624, 0.3973] | +0.1730 [0.082, 0.2659] | 15/3/4 | +0.909 | 13.6 > 50.0 | 22.7 > 13.6 | 2 > 1 | 22.7 > 0.0 |
| newly delivered, judged | 20 | 0.1555 [0.0953, 0.2203] | 0.3396 [0.2674, 0.4042] | +0.1842 [0.0865, 0.2795] | 14/2/4 | +0.975 | 10.0 > 50.0 | 20.0 > 10.0 | 2 > 1 | 25.0 > 0.0 |
| other judged | 2 | 0.1667 [0.0, 0.3333] | 0.2292 [0.0417, 0.4167] | +0.0625 [0.0417, 0.0833] | 1/1/0 | +0.250 | 50.0 > 50.0 | 50.0 > 50.0 | 0 > 0 | 0.0 > 0.0 |
| newly delivered, all 21 (incl. identical cooking-002) | 21 | 0.1486 [0.0884, 0.2097] | 0.3246 [0.2445, 0.3936] | +0.1761 [0.0779, 0.2683] | 14/3/4 | +0.929 | 9.5 > 47.6 | 19.0 > 9.5 | 2 > 1 | 28.6 > 4.8 |

Haiku read on the same ids (answer-screen rows):
- judged22 (n 22): U ctl 0.1486 ALL 0.2762 dU +0.1276 [0.0468, 0.2119]; corr 2.0 > 2.659
- new_delivered_judged (n 20): U ctl 0.1604 ALL 0.3 dU +0.1396 [0.0479, 0.2331]; corr 2.05 > 2.75
- other_judged (n 2): U ctl 0.0426 ALL 0.0638 dU +0.0213 [0.0, 0.0435]; corr 1.5 > 1.75
- new_delivered_all21 (n 21): U ctl 0.1535 ALL 0.287 dU +0.1335 [0.0422, 0.2201]; corr 2.0 > 2.667
- all_cm40 (n 40): U ctl 0.1653 ALL 0.2155 dU +0.0502 [-0.0131, 0.112]; corr 2.062 > 2.337

Sensitivity, answer-screen U definition (decline = 0, sum s / sum sref), Opus judged 22: {"U_ctl": 0.2622, "U_all": 0.4642, "dU": 0.202, "dU_ci": [0.1104, 0.2942]}
Haiku on the 16 differing units left unjudged: {"n": 16, "U_ctl": 0.2082, "U_all": 0.1584, "dU": -0.0499, "dU_ci": [-0.1195, 0.0149], "corr_ctl": 2.281, "corr_all": 2.062}

Verdict: LEVER on the covered domain
