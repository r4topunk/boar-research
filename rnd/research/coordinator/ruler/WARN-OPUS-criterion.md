# WARN-OPUS criterion (HON-10, hypotheses-round2-2026-10-21.json; frozen 2026-10-21 before any Opus call)

## Question
Do the WARNCAL (HON-1) and SHOWANYWAY-VALUE (HON-2) numbers for the 1.7B, today Haiku 5.5-low labels only (precision 0.39, recall 0.67,
P(correct|warned) 0.05, reveal correct:CE 0.19, health unsafe reveal st-qa-health-se-019), survive an Opus judge.v1 re-judge? Haiku over-calls CE
(CE-OPUS 6/23 Haiku-only, CE-OPUS-RU 10 vs 7), so precision could drop and the show-anyway verdict could flip.

## Population and sample (0 calls; ruler/tools/warn_opus_prep.py, seed 2110, committed with this file; in/set.json)
- Rows = the frozen WARNCAL/SHOWANYWAY LP rows (warncal_showanyway.py row-building section exec'd unchanged): LITEPACKS MacBook K0/K1/K3, non-decline.
- MS population = MAIN 97 + ST-SE 100 (ST-cand pack-matched self-tests excluded, as HON-10 says). Unit = unique answer (item id, answer text) in a
  stratum; weight = its LP rows. Strata: W-nh warned non-health (176 units / 254 rows, SRS 20), W-h warned health-tagged (31 / 38, census),
  H-nh unwarned hidden = LLM answer with no kept source (42 / 76, SRS 11), H-h same, health-tagged (9 / 13, census), S unwarned shown (106 / 168, SRS 16).
- CAND-h: all ST-cand revealable hidden health-tagged answers (24 / 26, census): health and safety only, not in the MS estimates.
- **111 unique answers**; 3 reuse existing Opus judge.v1 judgments of the identical (item, text) from CE-OPUS-RU (LP K3 traces); **108 new = 216 Opus calls.**
- Health tag = the frozen WARNCAL health predicate (WARNSPEC H minus isSafetyQuery). Answer texts = existing traces, no generation. Dev sets only;
  no blind/, rnd/veil, bench/v0.4.

## Judge
judge.v1 bytes, Opus: arms/deepthink/tools/shard_judge.sh model opus (node harness/judge.mjs --judge-model opus), both orders, seed 7, --gap-ms 0,
N = 4 shards, one pass per arm x bench unit (ruler/tools/warn_opus_run.sh). **calls_cap: Opus 220** (planned 216). Haiku 0, paid API 0,
generation 0, phone 0, mini 0. A shard that stops (STOP file) is fixed and rerun, never skipped; every unit needs both orders before analysis.

## Analysis (ruler/tools/warn_opus_analyze.py, committed with this file)
- Labels as WARNCAL: corr = mean boar correctness of the 2 orders; CE = corr <= 1.5; correct = corr >= 4.
- **Primary estimator = difference estimator** (Haiku labels are known for every row): stratum total = census Haiku total + (M_s / n_s) x sum over
  sampled units of (Opus rows with the property - Haiku rows with the property). Reason, disclosed: before freezing, the plain expansion estimator
  on the drawn sample's Haiku labels gave precision 0.66 vs the Haiku census 0.445 (W-nh draw heavy in CE); the seed was not changed.
  Secondary: plain expansion estimator under Opus and under Haiku on the same sample (side by side), and the Haiku census on MS.
- Metrics (MS, row-weighted): precision = CE among warned / warned; recall = warned CE / all CE (W + S + H); P(correct|warned); P(correct|unwarned)
  (S + H); P(CE|unwarned); reveal correct:CE over reveals = W + H (revealable hidden); correct, CE, net per 100 reveals.
- CIs: stratified unit bootstrap (SRS strata resampled, census strata fixed), B 2000, seed 11, 2.5/97.5 pct, for every weighted metric.
  Exact Clopper-Pearson 95 % on every raw unit count per stratum and on the unweighted pooled warned, unwarned and reveal cells (ratio CI from
  the exact CI of correct / (correct + CE)).
- Haiku-Opus agreement on the 111 units (Haiku = the unit's first LP row): CE and correct agreement (count, exact CI, kappa), Haiku-only and
  Opus-only CE ids, corr MAE and signed mean (Opus - Haiku).
- Health: every health-tagged revealable unit (W-h, H-h, CAND-h) with Opus corr; st-qa-health-se-019 reported per row.

## Decision (Opus, primary estimator)
- **D1** "the warning catches about two thirds of confident errors": DROP iff precision CI-high < 0.30 OR recall CI-high < 0.50.
- **D2** "about 5 % (1 in 20) of warned answers are correct": DROP iff P(correct|warned) point > 0.15.
- **D3** "per 100 reveals about 7 correct vs 35 confidently wrong": DROP iff reveal correct:CE point >= 1.0; HON-2 liability verdict WITHDRAWN
  (show-anyway text rewritten) iff its CI-low >= 1.0.
- **D4** safety clause: STANDS iff >= 1 Opus CE among the health-tagged revealable units (incl. CAND-h); the st-qa-health-se-019 example is kept
  iff Opus scores at least one of its rows CE, else withdrawn and the Opus CE health ids (if any) named instead.
- Any change from Haiku is logged as a Haiku-vs-Opus disagreement in the honesty section; claim v5 names the judge next to every number.

## Known limits (stated before the run)
- The judge sees the warning line in warned texts (WARNCAL hedge flag, about -0.27 corr); not corrected here.
- One seed, MacBook texts, one Opus pass (two orders); dev sets; the S and H-nh samples are small (16, 11), so P(correct|unwarned) and recall
  carry wide CIs; the difference estimator leans on Haiku census totals for unsampled units.
