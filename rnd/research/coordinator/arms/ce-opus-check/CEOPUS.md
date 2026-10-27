# CEOPUS: Haiku 5.5-low CE label vs Opus (2026-10-20)

TL;DR: measurement only (criterion 98a826d9..., frozen before any call). 47 answers, 94 Opus calls (judge.v1, model claude-opus-5-5, both orders, N = 4 shards, 0 failures, 0 paid beyond the Opus judge).
CE agreement Haiku vs Opus 39/47 = **0.83** (kappa 0.63); rule threshold 0.80, so **no judge-sensitivity flag by the frozen rule**. But the margin is thin and the agreement is lopsided: Opus never labels CE where Haiku does not (0/47), Haiku labels CE where Opus does not on 8/47.

Set: 23 K0 screen-control CEs (Haiku label) + 24 GREEDY answers differing from the control. The full set (61 answers = 122 calls) exceeds the 100-call cap, so the 14 non-CE control answers (10 sentinels + 4 non-CE problems) were dropped: no sentinel-worse check under Opus, and the control half is selected on Haiku CE.

| Slice | n | CE agree | kappa | Haiku CE | Opus CE | Haiku-only | Opus-only |
|---|---|---|---|---|---|---|---|
| all | 47 | 39 (0.83) | 0.63 | 35 | 27 | 8 | 0 |
| control (selected on Haiku CE) | 23 | 17 (0.74) | n/a (0.0 by construction) | 23 | 17 | 6 | 0 |
| GREEDY changed | 24 | 22 (0.92) | 0.83 | 12 | 10 | 2 | 0 |
| CE-unwarned, all | 47 | 45 (0.96) | 0.87 | 11 | 9 | 2 | 0 |
| CE-unwarned, control | 23 | 22 (0.96) | 0.90 | 8 | 7 | 1 | 0 |
| CE-unwarned, GREEDY | 24 | 23 (0.96) | 0.78 | 3 | 2 | 1 | 0 |

- Correctness (orders-averaged): MAE |Haiku - Opus| = 0.277; mean (Opus - Haiku) = +0.106, i.e. on these low-scoring answers Opus is slightly more lenient (the earlier HAIKUJUDGE note had Haiku lower on average across all 57-item legs; the sets differ).
- The 6 control items that flip (Haiku CE, Opus not CE) are what cost agreement; Opus control CE = 17 of 23, so the control CE rate under Opus is 17/37 vs Haiku 23/37 on the screen if the 14 dropped answers stay non-CE.

## GREEDY fixes (frozen gate definition: control CE -> greedy not CE, over the 27 problems)
| Labels | fixed | items |
|---|---|---|
| Haiku (frozen) | 4 | vit-cry-003, vit-cry-005, vit-sci-002, vit-trv-003 |
| Opus, primary (Opus-CE control -> Opus non-CE greedy) | **2** | vit-cry-005, vit-trv-003 |
| Opus, secondary (Haiku-CE control -> Opus non-CE greedy, ignoring Opus control label) | 7 | lan-exp-007, st-qa-money-se-007, vit-cry-006 (Opus control not CE) + vit-cry-003, vit-sci-002, vit-cry-005, vit-trv-003 |

Reading: under Opus labels GREEDY fixes 2 (need 6 on the frozen rule), so the NO-GO stands either way. vit-cry-003 and vit-sci-002 are Haiku-only fixes (Opus does not call the control answer CE, or the greedy answer is still CE). The secondary count is inflated by control items Opus never called CE.

## Rule outcome
Agreement 0.83 >= 0.80 -> flag = **no** (recorded, measurement only). Caveats: n = 47, CIs not computed, the control half is Haiku-selected (its 0.74 is a lower bound for the Haiku label's false-CE share among Haiku CEs: 6/23 = 26 % of Haiku CEs are not CE under Opus), single seed. The direction (Haiku over-calls CE) makes the screens' CE counts, not their fix counts, the judge-sensitive quantity.

Files: CEOPUS-criterion.md (+ .sha256), in/ (sets, traces), out/ (Opus judgments, logs, status), ceopus.json, tools/{prep.py,run.sh,analyze.py}.
