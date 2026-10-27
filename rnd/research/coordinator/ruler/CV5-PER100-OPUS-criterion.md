# CV5-PER100-OPUS criterion (round 3, hypotheses-round3-2026-10-21.json; frozen 2026-10-21 before any call of this pass)

## Question (verbatim statement)
The refuse-by-default per-100 table (HON6-TIER-PER100, MAIN 97 K0, 1.7B / Gemma / 4B; about 16 correct-shown and 2-4 CE-shown per 100 for each
tier) survives an Opus re-judge of the shown answers. Prediction from the WARN-OPUS pattern: CE-shown stays within +-2 per 100 per tier, and
correct-shown rises by 3 or more per 100. The tier tie on correct-shown and the CE ordering (4B <= 1.7B) are unchanged.

## Population (0 calls; ruler/tools/cv5_per100_prep.py + cv5_per100_common.py, committed with this file; in/set.json)
- Rows = hon67.py's desktop primary rows D, exec'd unchanged (hon67.py sha 9718fe37...): MAIN 97 (v0.1 57 + qa-cooking-se 20 + qa-money-se 20)
  K0 s42, 4B = vs4b, Gemma E2B = stage2 eng, 1.7B = lpctl control (mini frame). Hidden / warning flags deterministic, unchanged.
- (a) Census of every answer SHOWN under refuse-by-default: 4B 31, Gemma 37, 1.7B 32 rows.
- (b) Hidden sample: per tier, the hidden rows that carry text (hidden and not an engine decline), stratified by the Haiku label (CE corr <= 1.5,
  correct corr >= 4, partial), 20 per tier, proportional allocation (largest remainder, >= 1 per non-empty stratum), seeded per tier x stratum.
- Unit = unique (item, answer text): identical text across tiers is judged once. Reuse: any existing Opus judge.v1 row pair (ok, both orders,
  seed 7, that bench unit's refsSha256 / questionsSha256) on the identical unit, indexed by cv5_opus_pool.py, including the CV5-LADDER-OPUS rows
  (the 1.7B and Gemma s42 v0.1 texts are the same traces). Dev sets; no blind/, rnd/veil, v0.4.
- **130 unique units: 88 reused (CV5-LADDER-OPUS, WARN-OPUS and other identical-frame Opus passes), 42 new = 84 Opus calls.** Hidden strata (rows with
  text): 4B CE 14 / correct 10 / partial 35; Gemma 11 / 7 / 33; 1.7B 19 / 7 / 32.

## Judge
judge.v1 bytes, Opus via arms/deepthink/tools/shard_judge.sh model opus, both orders, seed 7, --gap-ms 0, N = 4, one pass per tier x bench unit
(ruler/tools/cv5_per100_run.sh). **calls_cap: Opus 310** (planned 84). Haiku 0, paid 0, generation 0, phone 0, mini 0. A stopped shard is
fixed and rerun, never skipped; every unit needs both orders.

## Analysis (ruler/tools/cv5_per100.py, committed with this file)
- hon67.py's per100 / pboot / table / decide exec'd unchanged. Opus rows: hon67's row() rebuilt with Opus corr, s, sref (CE = corr <= 1.5,
  correct = corr >= 4). Haiku columns = the same functions on hon67's own rows (= HON6 desktop_primary). Paired CIs: hon67's item bootstrap
  B 2000 seed 11.
- Primary output = the refuse-by-default columns (correct-shown, CE-shown, partial, hidden per 100) for both judges side by side, all 97 ids,
  plus divergent / deterministic splits. Refuse-mode U / floor-adj U under Opus are secondary: their denominators need sref on unjudged hidden
  rows, imputed as the item's mean Opus sref over any Opus row of this study, else Haiku sref + the mean Opus - Haiku sref offset (declared).
- Hidden: per tier, correct-hidden and CE-hidden per 100 under Opus = stratified expansion of the 20-row sample (bootstrap within strata,
  B 2000, seed 11) vs the Haiku census; show-all under Opus = shown census + that estimate (an estimate, not a census).
- Agreement on shown rows: CE and correct agreement, Haiku-only / Opus-only CE ids, mean corr shift.

## Decision (Opus, all 97 ids; kill rules verbatim from the hypothesis)
- **Kill** if any tier's CE-shown moves more than 2 per 100 (Opus - Haiku), OR the CE ordering 1.7B vs 4B reverses with CI excluding 0
  (Opus 4B - 1.7B dCE > 0 with CI low > 0), OR correct-shown differs between any two tiers by 5 or more per 100 (the tie breaks).
  On a kill the page quotes only the Opus per-100 table, rewrites the 'tiers level under refuse-by-default' sentence, and NOTE-2 carries the Opus numbers.
- **Supported** if no kill and correct-shown rises by >= 3 per 100 on every tier; **holds, prediction partial** if no kill and the rise is < 3
  somewhere (the table survives; the WARN-OPUS-based prediction does not fully).
- Every per-100 number printed names its judge family, the mode, and "dev questions, one run".

## Known limits (stated before the run)
One seed per tier; n 97 dev; hidden side is a 20-per-tier sample (wide CI); the judge sees the warning line in warned texts; mini-frame traces.
