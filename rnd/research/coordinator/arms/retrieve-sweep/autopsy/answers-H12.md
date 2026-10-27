# H1+H2 answer screen (H12 = H1 HP-SLATE + H2 HEALTH-TOPIC-FALLBACK, MAIN 97, K1 v2 kit, seed 42, Qwen3-1.7B, Haiku 5.5-low judge.v1 N 4 both orders) - EXPLORATORY

Control = mini baseline (arms/litepacks/traces/mini lp-K1-{cm,v01}-s42, not regenerated), judged rows from null-cal/control/pool-K1.json. Arm = traces/h12-K1-main-s42 (patches/H12-H1plusH2.patch sha d53288e6, env RS_HP_SLATE=1 RS_HEALTH_TOPIC_FB=1).
Divergence-first: 75 of 97 items have a different kept list AND a different answer text; the other 22 are byte-identical (20 deterministic-path + 2 live) and keep the control row. 150 Haiku calls (75 ids x 2 orders), Opus 0, paid 0, phone 0.

| set | arm | U | corr | CE | CE unwarned | warned | out tok | totalMs |
|---|---|---|---|---|---|---|---|---|
| all 97 | control | 0.4102 | 2.536 | 29 | 12 | 46 | 36.43 | 4449 |
| all 97 | H12 | 0.3924 | 2.381 | 32 | 9 | 53 | 36.23 | 4227 |
| changed 75 | control | 0.3798 | 2.373 | 22 | 7 | 44 | 45.72 | 5544 |
| changed 75 | H12 | 0.3570 | 2.173 | 25 | 4 | 51 | 45.45 | 5296 |

Paired dU (item bootstrap B 2000 seed 11): changed 75 = **-0.0228 [-0.0521, +0.0056]**; all 97 = -0.0178 [-0.0427, +0.0051]. Mean correctness change on the changed items -0.200 [-0.420, +0.007]; usefulness (changed, n 75) 1.513 -> 1.433.
Correctness up >= 1 point on 12 items, down >= 1 on 19. CE new 13, fixed 10; unwarned CE new ['lan-exp-007'], fixed ['lan-cmp-005', 'st-qa-cooking-se-007', 'st-qa-money-se-012'].
Sensitivity (changed set): excluding lan-exp-007 and st-qa-money-se-005 (pool control text differs from the mini baseline) -0.0205 [-0.0521, +0.0094]; excluding the two H2 targets -0.0176 [-0.0477, +0.0121]; excluding all four -0.0151 [-0.0469, +0.0137]. By source: v0.1 items (43) -0.0033, cooking-se (14) -0.0554, money-se (18) -0.0455.

## 7 target ids (correctness before -> after; s = judge mean of 3 dims)
| id | fix | corr | s | warned | note |
|---|---|---|---|---|---|
| lan-rsn-005 | H1 | 3.0 -> 4.0 | 2.333 -> 2.667 | True -> False | answer changed |
| lan-cmp-004 | H1 | 1.0 -> 1.0 | 1.0 -> 1.0 | True -> True | answer changed |
| vit-hum-003 | H1 | 2.0 -> 2.0 | 1.333 -> 1.333 | True -> True | answer changed |
| vit-sci-001 | H1 | 3.0 -> 3.5 | 2.0 -> 2.167 | True -> True | answer changed |
| st-qa-money-se-012 | H1 | 1.5 -> 2.0 | 1.5 -> 2.0 | False -> True | answer changed |
| vit-hlt-001 | H2 | 3.0 -> 2.0 | 3.0 -> 2.0 | False -> False | answer changed |
| vit-hlt-002 | H2 | 4.5 -> 3.5 | 3.5 -> 2.5 | False -> False | answer changed |

## Gold-kept 2x2 on the changed items (FACTPRESENT lexical rule; control flag = B0.main replay, arm flag = H1/H2 replay with the same kept titles; 13 items have no flag)
| ctl fact -> arm fact | n | mean corr ctl -> arm | dU |
|---|---|---|---|
| ctl_A__arm_A | 39 | 2.205 -> 1.795 | -0.0536 |
| ctl_A__arm_P | 4 | 2.25 -> 2.25 | -0.0410 |
| ctl_P__arm_A | 1 | 1.0 -> 2.0 | +0.1667 |
| ctl_P__arm_P | 18 | 2.75 -> 2.833 | +0.0307 |
| no-flag | 13 | 2.5 -> 2.385 | -0.0181 |

Answer screen (frozen in the brief: dU >= +0.02 with CI low > -0.01 on the changed items, CE-unwarned not up): dU clause FAILS (-0.023, CI low -0.052); CE-unwarned 7 -> 4 on changed (12 -> 9 on 97) clause holds. Verdict: NO (exploratory).
