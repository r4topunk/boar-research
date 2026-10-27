# SEFIX-ALL Opus confirm (judge.v1, claude-opus-5-5, N 4, both orders, seed 7), CV5 51 subset n 42

Set: 42 of the CV5 51 (cap fit, outcome-blind; dropped trv-004, lan-exp-005, lan-exp-002, vit-cry-003, vit-hum-006, vit-hlt-003; excluded identical-text ids without an Opus row vit-hum-004, vit-cry-009, lan-rsn-004). Control = MINI-BASELINE K1 mini traces. Rows: pool (identical unit) / new: ctl 20/22, ALL 13/29. Opus calls 102 of 110.

| set | n | U ctl | U ALL | dU (CI) | win/tie/loss | dcorr | correct/100 ctl>ALL | CE/100 ctl>ALL | CE-unwarned ctl>ALL | decl/100 ctl>ALL |
|---|---|---|---|---|---|---|---|---|---|---|
| S (42) | 42 | 0.4043 [0.3161, 0.498] | 0.402 [0.3151, 0.492] | -0.0022 [-0.0623, 0.0605] | 10/21/11 | +0.012 | 40.5 > 38.1 | 19.0 > 9.5 | 2 > 2 | 0.0 > 0.0 |
| text differs (30) | 30 | 0.3011 [0.2272, 0.3773] | 0.2977 [0.2326, 0.3629] | -0.0034 [-0.0862, 0.0781] | 10/9/11 | +0.017 | 26.7 > 23.3 | 23.3 > 10.0 | 1 > 1 | 0.0 > 0.0 |
| SEFIX-changed vs ARM-G (6) | 6 | 0.2391 [0.1429, 0.3551] | 0.25 [0.1268, 0.4286] | +0.0109 [-0.1631, 0.2572] | 2/1/3 | -0.083 | 16.7 > 16.7 | 33.3 > 0.0 | 1 > 0 | 0.0 > 0.0 |

Haiku read, same ids (answer screen rows):
- S42: U ctl 0.2957 ALL 0.3141 dU +0.0184 [-0.0363, 0.0734]
- differing30: U ctl 0.2254 ALL 0.2515 dU +0.0261 [-0.0479, 0.1004]
- sefix_changed6: U ctl 0.1628 ALL 0.2362 dU +0.0734 [-0.1364, 0.2804]

Verdict: not decided at n 42 (dU -0.002, CI -0.062..+0.061)
