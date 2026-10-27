| seed | set | arm | U | corr | CE | CE unwarned | warned | declined |
|---|---|---|---|---|---|---|---|---|
| 42 | all 97 | K3 control | 0.4102 | 2.536 | 29 | 12 | 46 | 0 |
| 42 | all 97 | SEFIX-ALL | 0.4352 | 2.696 | 22 | 10 | 38 | 0 |
| 42 | all 97 | COMBINED | 0.4339 | 2.655 | 20 | 12 | 42 | 0 |
| 42 | changed vs SEFIX-ALL (37) | SEFIX-ALL | 0.3816 | 2.324 | 9 | 1 | 23 | 0 |
| 42 | changed vs SEFIX-ALL (37) | COMBINED | 0.3782 | 2.216 | 7 | 3 | 27 | 0 |
| 43 | all 97 | K3 control | 0.4126 | 2.582 | 24 | 10 | 44 | 0 |
| 43 | all 97 | SEFIX-ALL | 0.4334 | 2.67 | 22 | 10 | 31 | 0 |
| 43 | all 97 | COMBINED | 0.4337 | 2.649 | 21 | 10 | 36 | 0 |
| 43 | changed vs SEFIX-ALL (37) | SEFIX-ALL | 0.3837 | 2.338 | 9 | 2 | 18 | 0 |
| 43 | changed vs SEFIX-ALL (37) | COMBINED | 0.3847 | 2.284 | 8 | 2 | 23 | 0 |

```json
{
 "rule": {
  "pooled_dU_vs_K3_all97_ge_0_03": false,
  "pooled_dU_vs_K3_ci_low_gt_0": true,
  "dU_vs_SEFIXALL_changed_ge_0": false,
  "CE_unwarned_not_above_SEFIXALL": false,
  "CE_unwarned_not_above_SEFIXALL_each_seed": false,
  "PASS": false
 },
 "pooled": {
  "vs_K_all97": {
   "n": 97,
   "d": 0.0224,
   "ci": [
    0.0005,
    0.0466
   ],
   "dcorr": 0.0928,
   "dcorr_ci": [
    -0.0722,
    0.2706
   ]
  },
  "vs_F_all97": {
   "n": 97,
   "d": -0.0004,
   "ci": [
    -0.011,
    0.0109
   ],
   "dcorr": -0.0309,
   "dcorr_ci": [
    -0.1211,
    0.0644
   ]
  },
  "vs_F_changed_union": {
   "n_union": 37,
   "n": 37,
   "d": -0.0012,
   "ci": [
    -0.029,
    0.0269
   ],
   "dcorr": -0.0811,
   "dcorr_ci": [
    -0.3176,
    0.1419
   ]
  },
  "F_vs_K_all97": {
   "n": 97,
   "d": 0.0229,
   "ci": [
    -0.0007,
    0.048
   ],
   "dcorr": 0.1237,
   "dcorr_ci": [
    -0.0464,
    0.3015
   ]
  },
  "U": {
   "K": 0.4114,
   "F": 0.4343,
   "C": 0.4338
  },
  "CE_unwarned": {
   "K": {
    "per_seed": {
     "42": 12,
     "43": 10
    },
    "sum": 22
   },
   "F": {
    "per_seed": {
     "42": 10,
     "43": 10
    },
    "sum": 20
   },
   "C": {
    "per_seed": {
     "42": 12,
     "43": 10
    },
    "sum": 22
   }
  },
  "CE": {
   "K": {
    "42": 29,
    "43": 24
   },
   "F": {
    "42": 22,
    "43": 22
   },
   "C": {
    "42": 20,
    "43": 21
   }
  }
 }
}
```
