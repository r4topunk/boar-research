# SEFIX-ALL seed 43 replicate (answer screen; Haiku 5.5-low judge.v1 N4 both orders; Opus 0, paid 0, phone 0)

| set (seed 43) | arm | U | corr | CE | CE unwarned | warned | declined |
|---|---|---|---|---|---|---|---|
| all 97 | K1 control | 0.4113 | 2.562 | 25 | 10 | 42 | 0 |
| all 97 | SEFIX-ALL | 0.4323 | 2.686 | 22 | 9 | 34 | 0 |
| text-differing, real rows (61) | K1 control | 0.359 | 2.254 | 16 | 5 | 34 | 0 |
| text-differing, real rows (61) | SEFIX-ALL | 0.3928 | 2.451 | 13 | 4 | 26 | 0 |

rows: ALL {'judged': 49, 'proxy': 20, 'cache': 28}, CTL {'judged': 51, 'proxy': 20, 'cache': 26}; text differs 75/97; differing with real rows 61; unjudged differing 14; proxy items 20 (delta 0 imputed)

- dU all 97 (imputed 0 on proxies): 0.021 [-0.0008, 0.0455]; text-differing set (75, proxies imputed 0): 0.0272 [-0.0012, 0.0559]; judged-differing only (61): 0.0338 [-0.0006, 0.0703]
- by source (all items, vs control): v0.1 n57 -0.0022 [-0.0206, 0.0183]; cooking n20 0.0986 [0.0394, 0.1591]; money n20 0.0122 [-0.0454, 0.0764]
- newly delivered 23 (real rows 23): corr CTL 2.0 -> ALL 2.674; dU 0.1114 [0.0556, 0.1696] (seed 42: corr 2.0 -> 2.63)
- POOLED two seeds: vs control all 97 0.023 [0.0006, 0.0476]; changed union (n 61) 0.0385 [0.0042, 0.0737]; CE-unwarned s42 {'CTL': 12, 'ALL': 10}, s43 {'CTL': 10, 'ALL': 9}
- rule pooled: {'changed_dU_ge_0_02_ci_low_gt_minus_0_01': True, 'vs_control_all97_dU_ge_0_02_ci_low_gt_minus_0_01': True, 'CE_unwarned_not_up': True, 'LEVER_CANDIDATE': True}
- rule seed 43 alone: {'changed_dU': 0.0272, 'changed_ci': [-0.0012, 0.0559], 'all97_dU': 0.021, 'all97_ci': [-0.0008, 0.0455], 'CE_unwarned_not_up': True, 'LEVER_CANDIDATE': True}
