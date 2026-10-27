# REVEAL-CENSUS (2026-10-21): the 1.7B's hidden MAIN answers under Opus are 11 correct : 16 confidently wrong (0.69); non-health 0.56 (CI 0.22-1.35). Show-anyway stays behind a second confirmation, never for health

- Criterion: REVEAL-CENSUS-criterion.md (sha in REVEAL-CENSUS-criterion.sha256; rnd 6bffe115, committed before any call).
- Tools: tools/reveal_census_prep.py, tools/reveal_census_run.sh, tools/reveal_census.py (sha cdee7e44...). Output REVEAL-CENSUS-2026-10-21.json (sha 5f83ea15...); new Opus rows in reveal-census/out/.
- Cost: **72 Opus judge.v1 calls** (cap 192), 72 ok, 0 missing, 0 reruns; 60 units reused from existing Opus passes. 0 Haiku, 0 generation, 0 paid, 0 phone, 0 mini. Dev sets only.
- Rows: the 1.7B K0 control (lp-screens / null-cal, mini frame, s42), hidden = declined / warned / no kept source, with text. Unit = item x answer-text hash x refs.

## TL;DR
- **Why the two Opus numbers conflicted: sampling, not judges.** All 58 MAIN hidden answers already had Opus labels (CV5-LADDER L1, GEMMA-OPUS-MAIN ctl42, CE-OPUS ctl, WARN-OPUS K0, CV5-PER100). The census gives **11 correct / 16 CE / 31 partial**. CV5-PER100's 20-row expansion (about 19 correct vs 11 CE per 100 questions, ratio about 1.7) overstated the correct side and understated the CE side; per 100 questions the census is 11.3 correct-hidden and 16.5 CE-hidden.
- **MAIN (the number claim v5 and NOTE-2 quote):** correct:CE **0.69** (Clopper-Pearson 0.29-1.58); per 100 reveals 19 correct / 28 CE. **Non-health 0.56 (0.22-1.35)**, 17 / 30 per 100. Haiku on the same rows: 0.37 / 0.32.
- **Rule 2: NOT met** (non-health point 0.56 < 1.0, CI low 0.22 <= 0.7). The recommendation stays: **show-anyway behind a second confirmation with "unverified, often wrong" copy, non-health only; never for health.** D3b liability stands, now quoted with census numbers.
- **Self-tests (upper bound, stratified 38 of 132):** weighted correct:CE **2.06** (stratified bootstrap 1.04-5.87; unweighted 15:7, exact 0.82-6.2); non-health 1.28 (boot 0.50-3.96; exact 0.43-4.1). Under Haiku the same sample is 0.35 (census 0.29). The self-test reveals are much better than MAIN's because ST-cand (pack-topic questions, 50 % Opus-correct) and health dominate; ST-SE non-health is 3 : 6, like MAIN.
- **Health:** MAIN 4 health reveals: 2 correct, 0 CE (Opus); ST health sample 8: 6 correct, 0 CE. **Rule 3 still holds** on prior Opus evidence: WARN-OPUS judged the ice-on-burns memory answer (st-qa-health-se-019, LP K0/K1) corr 1.0, and that item is in this ST population (Haiku CE; not drawn in the 38). The health path keeps the card or refusal.
- **HAIKU-CAL check:** the calibrated map predicted MAIN 0.62 / non-health 0.55; the census gives 0.69 / 0.56. The map transfers.

## MAIN 97 K0, census of the 58 hidden answers with text (Opus judge.v1; Haiku 5.5-low alongside)
| subset | n | Opus correct / CE / partial | Opus per 100 reveals: correct / CE | **Opus correct:CE (exact 95 %)** | Haiku correct / CE | Haiku ratio |
|---|---|---|---|---|---|---|
| all | 58 | 11 / 16 / 31 | 19.0 / 27.6 | **0.69 (0.29-1.58)** | 7 / 19 | 0.37 |
| **non-health** | 54 | 9 / 16 / 29 | 16.7 / 29.6 | **0.56 (0.22-1.35)** | 6 / 19 | 0.32 |
| health (WARNSPEC) | 4 | 2 / 0 / 2 | 50 / 0 | n/a (CI low 0.19) | 1 / 0 | n/a |
| warned | 39 | 8 / 12 / 19 | 20.5 / 30.8 | 0.67 (0.24-1.77) | 3 / 16 | 0.19 |
| unwarned, no kept source (banner) | 19 | 3 / 4 / 12 | 15.8 / 21.1 | 0.75 (0.11-4.4) | 4 / 3 | 1.33 |

By reason code (Opus; Haiku correct / CE in brackets):
| bucket | n | correct / CE | ratio (exact) |
|---|---|---|---|
| W: no-source | 24 | 5 / 7 [1 / 8] | 0.71 (0.18-2.6) |
| U: no kept source (banner only) | 19 | 3 / 4 [4 / 3] | 0.75 (0.11-4.4) |
| W: uncited-with-sources | 8 | 2 / 2 [2 / 3] | 1.0 (0.07-13.8) |
| W: all-citations-removed | 7 | 1 / 3 [0 / 5] | 0.33 (0.01-4.2) |
- No cell is selectable (rule 4); every cell CI spans 1.
- The 16 Opus CEs are all non-health: vit-hum-004, vit-hum-005, vit-trv-003, vit-cry-002, vit-cry-005, vit-cry-007, cooking-se-007/008/009/012, money-se-001/005/009/010/013/020. 13 of them are Haiku CEs too.
- Per 100 MAIN questions (97): 11.3 correct-hidden, 16.5 CE-hidden under Opus (Haiku 7.2 / 19.6). Show-all under Opus = shown census (CV5-PER100: 18.6 correct / 2.1 CE) + hidden census = **29.9 correct / 18.6 CE per 100 questions** (now a census, not an estimate).

## Self-tests (ST-SE 100 + ST-cand 80): stratified 38 of 132 hidden answers with text (upper bound)
| stratum (pop) | n | Opus correct / CE / partial | ratio (exact) |
|---|---|---|---|
| ST-SE non-health (64) | 18 | 3 / 6 / 9 | 0.50 (0.08-2.3) |
| ST-SE health (14) | 4 | 3 / 0 / 1 | n/a |
| ST-cand non-health (42) | 12 | 6 / 1 / 5 | 6.0 (0.73-276) |
| ST-cand health (12) | 4 | 3 / 0 / 1 | n/a |
| **weighted, all (132)** | 38 | est. 51.2 / 24.8 rows | **2.06** (boot 1.04-5.87); per 100: 38.8 / 18.8 |
| weighted, non-health (106) | 30 | est. 31.7 / 24.8 rows | 1.28 (boot 0.50-3.96); per 100: 29.9 / 23.4 |
| Haiku census, all / non-health / health | 132 / 106 / 26 | 14/49, 7/46, 7/3 | 0.29 / 0.15 / 2.33 |
- By reason code (unweighted sample): banner 6 / 3, all-citations-removed 5 / 4, W: no-source 3 / 0, W: uncited 1 / 0.
- Haiku vs Opus on the same 38: Haiku 4 correct / 11 CE, Opus 15 / 7. The warned-answer under-call (HAIKU-CAL kappa(correct) 0.22 on warned) explains most of the gap.

## Rules (frozen)
1. **Quoted number = MAIN**: "Under an Opus judge, the 1.7B's hidden answers on 97 dev questions are about 1 correct per 1.5 confidently wrong (11 vs 16 of 58; non-health 9 vs 16, correct:CE 0.56, CI 0.22-1.35). On pack self-tests the hidden answers are better (about 2 correct per confident error, a stratified 38-answer sample; upper bound). 1.7B, Opus judge.v1, dev questions, one run."
2. **Show-anyway: no change.** Non-health MAIN 0.56 < 1.0 and CI low 0.22 <= 0.7. NOTE-2 keeps: second confirmation, "unverified, often wrong", non-health only.
3. **Health: no show-anyway.** 0 Opus CEs among the 12 health reveals judged here, but the ice-on-burns memory answer (Opus 1.0 in WARN-OPUS) sits in this population.
4. No reason-code rule.

## What changes in the text
- Replace "about 20 correct and 38 confidently wrong per 100 reveals (WARN-OPUS, 0.54)" with the MAIN census: **19 correct / 28 CE per 100 reveals (0.69); non-health 17 / 30 (0.56)**. WARN-OPUS stays as the LITEPACKS-pool figure.
- Withdraw the CV5-PER100 NOTE-2 sentence "the case for a show-anyway button is stronger under Opus" for the 1.7B: the census CE-hidden is 16.5 per 100 questions, not 11.2 (the 4B/Gemma hidden estimates are still 20-row samples).

## Limits
One seed, one Opus pass per unit (60 reused from five earlier passes on identical texts and refs), mini-frame traces, the judge sees the warning line (no strip condition here; the revisit's condition B is still open), ST is a 38-row sample with wide CIs, health tag lexical (AI-reviewed, not clinically reviewed).
