# REVEAL-CENSUS criterion (WARN-REVEAL census; frozen 2026-10-21 before any call of this pass)

## Question
The two Opus show-anyway numbers conflict: WARN-OPUS (HON-10) reveal correct:CE 0.54 (0.32-0.83) on LITEPACKS K0/K1/K3 warned rows incl. self-tests
(difference estimator), and CV5-PER100-OPUS about 19.0 correct-hidden vs 11.2 CE-hidden per 100 (ratio about 1.7) on a 20-row sample of the 1.7B
MAIN 97 K0 hidden rows. They come from different populations. This pass measures each population directly under Opus.

## Populations (0 calls; tools/reveal_census_prep.py, committed with this file; reveal-census/in/set.json)
- Rows = tools/warncal_showanyway.py data section exec'd unchanged (sha 8e162cea...), source MINI, arm K0 = the 1.7B lp-screens / null-cal control,
  mini frame, seed 42, Haiku 5.5-low labels as stored. Hidden = declined OR warned OR an LLM answer with no kept source (RU definition);
  "with text" = hidden and not a decline (null-cal labels.is_decline).
- **MAIN** = MAIN 97 (v0.1 57 + qa-cooking-se 20 + qa-money-se 20), hidden with text: **58 rows = census** (54 non-health, 4 health by the
  WARNSPEC health predicate). This is the CV5-PER100 1.7B hidden-with-text population.
- **ST** = the 180 self-tests (ST-SE 100 + ST-cand 80), hidden with text: 132 rows. Stratified sample of 38: strata set x health
  (ST-SE nh 64 / h 14, ST-cand nh 42 / h 12), allocation ST-SE nh 18, ST-SE h 4, ST-cand nh 12, ST-cand h 4 (proportional, largest remainder,
  >= 4 per stratum), random.Random("reveal-census-<stratum>").
- Unit = (item, sha16 of answer text, refs sha of the frame). Existing Opus judge.v1 both-order pairs on the identical unit are reused (any
  file under boar-eval/ or rnd/, never blind/ or rnd/veil/); several pairs are averaged.
- **Prep result: 96 units; 60 reused (all 58 MAIN units: CV5-LADDER L1, GEMMA-OPUS-MAIN ctl42, CE-OPUS ctl, WARN-OPUS K0, CV5-PER100 1.7B;
  2 ST units from WARN-OPUS K0), 36 new ST units = 72 Opus calls.** Dev sets only; no blind/, rnd/veil, v0.4.

## Judge
judge.v1 bytes, Opus via arms/deepthink/tools/shard_judge.sh model opus, both orders, seed 7, --gap-ms 0, N = 4, one pass per bench unit on
arms/null-cal/control/traces/poolctl-K0-st180-s42.traces.jsonl (tools/reveal_census_run.sh). Ids files list divergent-st180 ids first.
**calls_cap: Opus 192** (planned 72). Haiku 0, paid 0, generation 0, phone 0, mini 0. A stopped shard is fixed and rerun, never skipped; every
unit needs both orders.

## Analysis (tools/reveal_census.py, committed after the run but implementing only what is written here)
- Opus label per unit = mean over orders (and over reused pairs) of mapped boar correctness; CE = corr <= 1.5, correct = corr >= 4, partial otherwise.
- Per population: correct, CE, partial per 100 reveals; **correct:CE = k_correct / k_CE with exact CI = Clopper-Pearson 95 % on
  p = k_correct / (k_correct + k_CE), mapped to p / (1 - p)**. MAIN = census (exact counts; the CI expresses item sampling).
  ST = stratified expansion (weights stratum size / n) for the per-100 point estimates; correct:CE CI = Clopper-Pearson on the unweighted sample
  counts, plus stratified bootstrap (B 2000, seed 11) of the weighted ratio.
- Splits: non-health vs health (WARNSPEC predicate, AI-reviewed, not clinically reviewed); by reason code (bucket: W:no-source,
  W:all-citations-removed, W:uncited-with-sources, U:no-kept(banner)); Haiku census on the same rows side by side; HAIKU-CAL implied value
  (MAIN 0.62) as a check.

## Rules (fixed now)
1. **Quoted number:** the number claim v5 and NOTE-2 quote for show-anyway = the MAIN population (non-health and all, Opus, census), with the
   self-test (ST) number reported as an upper bound / secondary figure, both naming the judge family, "1.7B, dev questions, one run".
2. **Show-anyway recommendation** stays "behind a second confirmation, never for health" UNLESS MAIN non-health correct:CE >= 1.0 AND its
   Clopper-Pearson CI low > 0.7. If met: NOTE-2 wording may offer show-anyway for non-health with "unverified" copy (wording only; no default
   change, health unchanged). Otherwise the D3b liability verdict stands and is quoted with the census numbers.
3. **Health:** any Opus CE among health reveals keeps the safety clause (count rule, unchanged from SHOWANYWAY D4).
4. Nothing is selected post hoc: reason-code cells are reported, never promoted to a rule in this pass.

## Prior (stated before the run)
HAIKU-CAL implied MAIN correct:CE about 0.62 (non-health 0.55); CV5-PER100's sample implied about 1.7. P(MAIN non-health >= 1.0 with CI low > 0.7) about 0.2.

## Known limits
One seed, one Opus pass per unit, mini-frame traces, n 58 / 38, the judge sees the warning line in warned texts (no strip condition in this pass).
