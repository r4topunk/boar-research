# EVALFIX (T6, 2026-10-12): wins+ties rescore, CI sensitivity, v0.3 power. 0 judge calls; tools/winsties.py, tools/robust_ci.py; aggregates/{winsties,robust_ci,power}.json
TL;DR: no verdict changes. The judge essentially never emits `tie`, so wins+ties = wins; the robust intervals agree with the bootstrap within 0.01 on all five delta rows.

## 1. Wins / ties / losses vs the Opus reference (Wilson 95 %; mapped.winner values seen: ref 1051, boar 1, tie 0 of 1052 rows)
| run | n | wins | ties same-order | ties order-disagree | losses | win rate (CI) | wins+ties (CI) |
|---|---|---|---|---|---|---|---|
| H V-para s42 / s43 | 51 / 51 | 0 / 0 | 0 / 0 | 0 / 0 | 51 / 51 | 0 (0-0.070) | 0 (0-0.070) |
| K V-para s42 / s43 | 51 / 51 | 0 / 0 | 0 / 0 | 0 / 0 | 51 / 51 | 0 (0-0.070) | 0 (0-0.070) |
| Q V-para s42 / s43 | 51 / 51 | 0 / 0 | 0 / 0 | 0 / 0 | 51 / 51 | 0 (0-0.070) | 0 (0-0.070) |
| H V-para pooled (102 item-runs) | 102 | 0 | 0 | 0 | 102 | 0 (0-0.036) | 0 (0-0.036) |
| H v0.2 s42 | 110 | 0 | 0 | 1 | 109 | 0 (0-0.034) | 0.009 (0.002-0.050) |
| K v0.2 s42 | 110 | 0 | 0 | 0 | 110 | 0 (0-0.034) | 0 (0-0.034) |
The one tie is an order disagreement (one order said boar, the other ref). Score-parity check (order-summed rubric mean boar >= ref): 0 items in every run.

## 2. Three intervals side by side (raw ratio scale; n items; 2-seed rows average seeds per item)
| row | n | point | (a) cited bootstrap | (b) logit-t | (c) paired t (delta method) | max end gap |
|---|---|---|---|---|---|---|
| DT512 H-T V-para, 2 seeds | 51 | +0.011 | -0.010...+0.031 | -0.002...+0.024 | -0.002...+0.024 | 0.008 |
| DEEPTHINK T-D V-para, 2 seeds | 51 | +0.075 | +0.040...+0.110 | +0.044...+0.113 | +0.042...+0.107 | 0.006 |
| QUANTCEIL Q-H V-para, 2 seeds | 51 | +0.004 | -0.024...+0.033 | -0.020...+0.031 | -0.020...+0.028 | 0.005 |
| QUANTCEIL Q-H v0.2, s42 | 110 | +0.008 | -0.011...+0.028 | -0.010...+0.036 | -0.011...+0.028 | 0.008 |
| SEEDVAR H 3-seed mean ratio V-para | 51 | 0.550 | per-seed 0.500-0.607; seed-level t 0.500...0.600 | 0.521...0.582 | 0.520...0.579 | 0.021 |
Sources of (a): arms/dt512/aggregates/paired_gap-HvsT-2seed.json, arms/deepthink/aggregates/L2-TvsD-2seed.paired_gap.json, arms/quantceil/aggregates/paired_gap-QvsH-{2,1}seed.json, arms/seedvar/aggregates/seedvar-H-3seed.opus.json.
Disagreement > 0.01: only SEEDVAR, and only because (a) there is a seed-level t (k = 3, df 2, ignores item sampling, +-0.050) while (b)/(c) are item-level (+-0.030) and treat the 3-seed average as fixed; the per-seed bootstrap CIs (+-0.03) agree with (b)/(c). (b) is for the mean of per-item ratios (0.549), (c) for the ratio of sums (0.550). Bonett 2006 not applied (plain paired t).

## 3. Reading
Judge.v1 allows ties but Opus never uses them as such (1 of 1052 rows is a tie, from an order disagreement), so the GDPval-style wins+ties framing adds nothing: V-para 0/51 per seed for H, K and Q (upper bounds 0.07), v0.2 0-1/110. Even a score-parity tie proxy gives 0 items, so the gap to the reference is not a tie-handling artefact. The robust intervals match the bootstrap within 0.008 at every end on the delta rows: DT512 H-T stays CHEAPER-PARITY (CI low > -0.03, includes 0), DEEPTHINK T-D stays detected (low +0.04), Q-H stays NO on both sets. (b)/(c) are slightly narrower than the two-level bootstrap on 2-seed rows because they average seeds; the cited bootstrap remains the conservative figure. v0.3 sizing is in boar-eval/bench/v0.3/plan/power-statement.md (point estimate needed for mean > 0.50 at n 110: 0.53, 0.545 with sigma_run 0.020).

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file by design (measurement / descriptive / tooling); nothing to freeze.
