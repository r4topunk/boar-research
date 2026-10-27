# HAIKU-CAL fit spec (frozen before computing; 0 LLM calls)

Purpose: a Haiku 5.5-low judge.v1 -> Opus judge.v1 calibration map from units that already carry both labels (revisit-closed-2026-10-21 "HAIKUJUDGE / JUDGE2 / CE-OPUS" retest, HAIKU-OPUS-MAP).

## Units
- Unit = (queryId, sha256(answer text)[:16], refsSha256). Text is resolved from the traces file whose sha256 equals the judgment row's tracesSha256 (all *.traces.jsonl under boar-eval/ and rnd/, never blind/ or rnd/veil/).
- A family label exists for a unit when one judgments file holds ok rows for both orders (boarA, boarB), not floor-scored. Label = per-dimension mean of the two orders' mapped.boar scores (correctness, completeness, usefulness), s = mean of the three, sref likewise. Several passes of one family on the same unit are averaged (n passes recorded).
- Haiku = judgeModel claude-haiku-5-5 (judge.v1-low); Opus = judgeModel claude-opus-5-5 (judge.v1). Gemma/Codex/other judges are ignored.
- Pool = units with both labels. Declines (null-cal labels.is_decline) are excluded from all CE/correct statistics and reported as a count.
- Source tag (priority order) = the first listed Opus pass that judged the unit: CE-OPUS (arms/ce-opus-check), CE-OPUS-RU (arms/refuse-unsupported/ce-opus-ru), WARN-OPUS (ruler/warn-opus), CV5-LADDER (ruler/cv5-ladder), CV5-PER100 (ruler/cv5-per100), GEMMA-OPUS-MAIN (ruler/gemma-opus-main); else OTHER (older Opus L2 passes, reported separately as replication). REFVAR contributes Haiku re-labels only (its refv1 rows join when refsSha256 matches).
- Features per unit from the trace: tier = runtime.model; warned = text starts with the CMP30OFF warning line (labels.W); kept = len(retrieval.kept); set = MAIN / ST-SE / ST-cand / v01-other by id.

## Labels
- CE = corr <= 1.5; correct = corr >= 4; partial otherwise (the WARNCAL/SHOWANYWAY thresholds).

## Outputs
1. Agreement: Cohen kappa on CE, on correct, and 3-class (CE/partial/correct); MAE and mean shift (Opus - Haiku) per dimension, overall, by source, by tier, by warned.
2. Calibration curve: Haiku corr on the 0.5 grid (bins 1-1.5, 2-2.5, 3-3.5, 4-5 for the headline) -> mean Opus corr, P(Opus correct), P(Opus CE), with Wilson 95 % CIs, by source and by warned.
3. Implied correction for Haiku-only numbers: (a) per-100 correct and CE implied = sum over Haiku bins x warned cells of count x P(Opus label | cell) (cells with n < 5 fall back to the bin pooled over warned); (b) U shift dS = mean(Opus s - Haiku s) per tier, with item-cluster bootstrap 95 % CI (B 2000, seed 11); (c) the differential shift between tier pairs (4B, Gemma E2B, 1.7B, 1.5B) on units of the same queryIds where available, else unpaired difference of tier means with bootstrap CI.
- Kill (from the revisit entry): if |differential shift| < 0.01 U for every tier pair, no Haiku-only U-delta verdict is reopened; only correct-count clauses stay flagged.
- No tuning: bins, thresholds, seed and B are fixed above.
