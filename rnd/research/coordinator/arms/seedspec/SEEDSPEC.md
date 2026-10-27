# SEEDSPEC (T7): seed-specificity of the deep tier's wrong claims
Arm H (deep + think 512), V-para, seeds s42/s43/s44, Opus judge.v1 both orders; jev typesafe-ai/jev, threshold 0.6, 51 requests (one per item, 3 seeds in state). Script: tools/seedspec.py; data: aggregates/seedspec-H-vpara.json (ids/labels/probs only); cache blind/V-para/runs-dt512/seedspec-cache/. Cost: [usage detail removed] (gateway marketCost).

Set A = 26 items wrong_fact on s42 (LOSSMAP); set B = all 51 judged.
| | A (26) | B (51) |
|---|---|---|
| wrong per seed s42/s43/s44 | 24/15/17 | 24/20/26 |
| wrong in 1 / 2 / 3 seeds | 6 / 10 / 10 | 12 / 14 / 10 |
| any seed wrong | 26 | 36 |
| same_wrong_fact among multi-seed-wrong | 12/20 = 60 % | 12/24 = 50 % |
| any_seed_correct_on_it among wrong | 14/26 = 54 % | 21/36 = 58 % |
| pattern stable_wrong / seed_specific / mixed / not_wrong | 17 / 1 / 8 / 0 | 22 / 5 / 9 / 15 |
| seed_specific share of wrong items | 4 % | 14 % |
| seed_specific + mixed share | 35 % | 39 % |

Correctness range across seeds (mean of both orders per seed): A <1: 7, 1-<2: 10, >=2: 9; B <1: 19, 1-<2: 21, >=2: 11. Items with a range >= 2 points: 9/26 (A), 11/51 (B).

Reading against T7 (seed-specific >= 50 % of wrong items): strict pattern = 4 % (A) / 14 % (B); even counting mixed as seed-specific = 35 % / 39 %. Single-seed-wrong items are 23 % (A) / 33 % (B). Caveat: any_seed_correct (54 %) is higher than the pattern label implies, so part of "stable_wrong" is one wrong claim recurring while another claim varies; jev is a gut-check labeller (no human audit). Even the generous reading is below 50 %.
VERDICT: T7 FAILS. Wrong facts are mostly stable across seeds (model knowledge); O-6 Integrative Decoding k = 2-4 stays closed, no T9 ID arm.

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file; the gate was pre-stated in DEEP-RESEARCH-2026-10-12 l.180 (SEEDSPEC/T7) — nothing to freeze (a sha now would fake a pre-registration).
