# COMPOSE answer screen (MAIN 97, K1 tree, seed 42, Qwen3-1.7B, Haiku 5.5-low judge.v1 N 4 both orders) - EXPLORATORY

Control = mini baseline K1 kit (3 packs). ARM-S = 13-pack kit (K3 + 10 small packs, N10), stock merge; ARM-G = same kit + rs-H4 patch (RS_MERGE=gidf). Judged rows: null-cal/control/pool-K1.json (control), screen/judge/{G,S} (arms). Aggregator screen/tools/agg_cmp.py.

| set | arm | U | corr | CE | CE unwarned | warned | declined | out tok | totalMs |
|---|---|---|---|---|---|---|---|---|---|
| all 97  | control | 0.4102 | 2.536 | 29 | 12 | 46 | 0 | 36.43 | 4449 |
| all 97  | ARM-S | 0.4083 | 2.567 | 28 | 12 | 45 | 0 | 35.36 | 5513 |
| all 97  | control | 0.4102 | 2.536 | 29 | 12 | 46 | 0 | 36.43 | 4449 |
| all 97  | ARM-G | 0.4167 | 2.582 | 24 | 14 | 40 | 0 | 34.54 | 5594 |
| changed 67 | control | 0.3815 | 2.381 | 20 | 4 | 42 | 0 | 45.79 | 5526 |
| changed 67 | ARM-S | 0.3790 | 2.425 | 19 | 4 | 41 | 0 | 44.24 | 6900 |
| changed 69 | control | 0.3780 | 2.370 | 20 | 4 | 43 | 0 | 46.28 | 5549 |
| changed 69 | ARM-G | 0.3872 | 2.435 | 15 | 6 | 37 | 0 | 43.61 | 7048 |

Paired dU vs control (item bootstrap B 2000 seed 11):
- ARM-S: changed 67 = **-0.0026 [-0.0370, +0.0297]**; all 97 = -0.0019 [-0.0252, +0.0208]; dcorr +0.0448 [-0.2164, +0.2985]; excluding the two pool-text-mismatch items -0.0019 [-0.0359, +0.0322]
- ARM-G: changed 69 = **+0.0093 [-0.0223, +0.0387]**; all 97 = +0.0065 [-0.0155, +0.0287]; dcorr +0.0652 [-0.1667, +0.2971]; excluding the two pool-text-mismatch items +0.0101 [-0.0239, +0.0422]
- ARM-G - ARM-S on the 66 items changed in both: +0.0070 [-0.0117, +0.0260] (U_S 0.3806, U_G 0.3876, control 0.3824; answer text identical on 34 of them); union 70: +0.0115 [-0.0080, +0.0305]; all 97: +0.0084 [-0.0056, +0.0225]

By source (changed items; ctl U -> arm U, dU [CI]):
- ARM-S v0.1 (n 34): 0.3969 -> 0.4274, dU +0.0305 [-0.0195, +0.0822], corr 2.574 -> 2.853, CE new 3 / fixed 7
- ARM-S cooking (n 14): 0.3703 -> 0.3622, dU -0.0080 [-0.0775, +0.0596], corr 2.214 -> 2.214, CE new 2 / fixed 3
- ARM-S money (n 19): 0.3613 -> 0.3013, dU -0.0600 [-0.1052, -0.0086], corr 2.158 -> 1.816, CE new 6 / fixed 2
- ARM-G v0.1 (n 36): 0.3893 -> 0.4078, dU +0.0185 [-0.0288, +0.0658], corr 2.542 -> 2.639, CE new 5 / fixed 8
- ARM-G cooking (n 14): 0.3703 -> 0.4051, dU +0.0348 [-0.0216, +0.0944], corr 2.214 -> 2.429, CE new 0 / fixed 2
- ARM-G money (n 19): 0.3613 -> 0.3327, dU -0.0286 [-0.0739, +0.0150], corr 2.158 -> 2.053, CE new 3 / fixed 3

Gold-kept 2x2 on the changed items (FACTPRESENT lexical rule on kept text; ctl flag = B0.main replay, arm flag = N10 replay of the arm when its kept titles equal the run's):

| arm | cell | n | corr ctl -> arm | dU |
|---|---|---|---|---|
| ARM-S | ctl_A__arm_A | 37 | 2.284 -> 2.027 | -0.0413 |
| ARM-S | ctl_A__arm_P | 5 | 1.8 -> 3.1 | +0.1583 |
| ARM-S | ctl_P__arm_P | 14 | 2.893 -> 3.286 | +0.0435 |
| ARM-S | no-flag | 11 | 2.318 -> 2.364 | -0.0087 |
| ARM-G | ctl_A__arm_A | 35 | 2.3 -> 2.186 | -0.0117 |
| ARM-G | ctl_A__arm_P | 7 | 1.857 -> 2.357 | +0.0651 |
| ARM-G | ctl_P__arm_P | 16 | 2.781 -> 2.875 | +0.0314 |
| ARM-G | no-flag | 11 | 2.318 -> 2.636 | +0.0069 |

Newly kept facts (compose.json N10 kept list minus N0.stock; all changed in the live runs):
- ARM-S (7 facts, mean dcorr +1.143): lan-cmp-004 1.0->2.5, lan-hlt-002 3.5->4.5, st-qa-cooking-se-004 3.0->4.0, st-qa-cooking-se-008 1.5->1.0, st-qa-cooking-se-009 3.0->3.5, vit-hlt-003 2.0->4.0, vit-hum-005 1.0->3.5
- ARM-G (10 facts, mean dcorr +0.550): lan-cmp-004 1.0->2.5, lan-hlt-002 3.5->4.5, st-qa-cooking-se-004 3.0->4.0, st-qa-cooking-se-008 1.5->1.0, st-qa-cooking-se-009 3.0->4.0, st-qa-cooking-se-012 1.0->1.5, vit-cry-001 2.0->2.0, vit-hlt-003 2.0->1.0, vit-hum-005 1.0->3.5, vit-sci-001 3.0->2.5

CE: ARM-S new 11 ['lan-cmp-002', 'vit-sci-002', 'dng-005', 'st-qa-cooking-se-010', 'st-qa-cooking-se-019', 'st-qa-money-se-001', 'st-qa-money-se-002', 'st-qa-money-se-006', 'st-qa-money-se-007', 'st-qa-money-se-009', 'st-qa-money-se-015'] fixed 12; unwarned new ['lan-cmp-002', 'dng-005'] fixed ['st-qa-cooking-se-007', 'st-qa-money-se-013']; ARM-G new 8 ['lan-cmp-002', 'vit-sci-002', 'vit-hlt-003', 'lan-exp-005', 'dng-005', 'st-qa-money-se-002', 'st-qa-money-se-006', 'st-qa-money-se-007'] fixed 13; unwarned new ['lan-cmp-002', 'vit-hlt-003', 'lan-exp-005', 'dng-005'] fixed ['st-qa-cooking-se-007', 'st-qa-money-se-012', 'st-qa-money-se-013']
