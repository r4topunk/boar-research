# QWEN35-2B (Qwen3.5-2B Q4_K_M in the 1.7B slot, LITEPACKS, 2026-10-20/21): stage 1 NO-GO on all 4 screens (GATE v2), stage 2 not run

TL;DR: MC-1 is closed for this checkpoint and quant. Qwen3.5-2B at native Q4_K_M, with vendor sampling (V) or with engine sampling (E), fails GATE v2 on both K0 and K1. Its CE-unwarned "fixes" are mostly the engine putting the warning line on answers. That happens because the 2B drops or mangles the [n] citations: cited answers on the K0 screen fall from 17 to 5 (V) and 7 (E). The 2B therefore loses usefulness on covered items (U_cov -0.10 to -0.20) and refuses correct sentinels. Answers are about 1.8x longer. Wall time is 1.24-2.01x the 1.7B under uneven mini load.

| Screen | gate line (verbatim, screen_gate_v2.py, GATE v2 commit 8c175580) |
|---|---|
| V K0 | `problems 30 \| fixed_u 16 (by refusal 10) \| new CEu 6 \| net 10 (bar 10) \| false refusals 2/20 (max 2) \| sentinels worse 16 (report only) \| U_cov -0.1447 [-0.1917, -0.0989] (min -0.059) \| changed 50 \| dead changed 0 -> NO-GO` |
| V K1 | `problems 21 \| fixed_u 12 (by refusal 6) \| new CEu 1 \| net 11 (bar 9) \| false refusals 8/20 (max 4) \| sentinels worse 9 (report only) \| U_cov -0.2017 [-0.2838, -0.1184] (min -0.071) \| changed 41 \| dead changed 0 -> NO-GO` |
| E K0 | `problems 30 \| fixed_u 12 (by refusal 7) \| new CEu 3 \| net 9 (bar 10) \| false refusals 3/20 (max 2) \| sentinels worse 14 (report only) \| U_cov -0.0982 [-0.1536, -0.0445] (min -0.059) \| changed 50 \| dead changed 0 -> NO-GO` |
| E K1 | `problems 21 \| fixed_u 7 (by refusal 2) \| new CEu 2 \| net 5 (bar 9) \| false refusals 2/20 (max 4) \| sentinels worse 12 (report only) \| U_cov -0.0716 [-0.1318, -0.0148] (min -0.071) \| changed 41 \| dead changed 0 -> NO-GO` |

| Screen | CE-unwarned ctl -> cand | declines | warned ctl -> cand | cited answers ctl -> cand | answer tokens mean (max) cand vs ctl | wall ratio (sum totalMs, live) | mini load cand vs ctl |
|---|---|---|---|---|---|---|---|
| V K0 | 30 -> 20 | 0 -> 0 | 0 -> 12 | 17 -> 5 | 81.8 (133) vs 41.2 | 1.56 | 5.65 vs 4.46 |
| V K1 | 21 -> 10 | 0 -> 0 | 0 -> 14 | 28 -> 14 | 75.5 (116) vs 44.0 | 1.29 | 5.98 vs 4.61 |
| E K0 | 30 -> 21 | 0 -> 0 | 0 -> 10 | 17 -> 7 | 75.5 (247) vs 41.2 | 2.01 | 7.57 vs 4.46 |
| E K1 | 21 -> 16 | 0 -> 0 | 0 -> 4 | 28 -> 24 | 73.8 (108) vs 44.0 | 1.24 | 4.22 vs 4.61 |
All runs: 0 errors, 0 reasoning tokens, 0 think-tag leaks, 0 dead items changed. Wall per arm: tools/wall.py -> screens/<arm>/aggregates/*.wall.json.

## Reading
- Mechanism: every new warned answer carries `compact-decline-released-uncited-with-sources` and/or `...-all-citations-removed`. The 2B follows the "[n]" citation instruction less well than the 1.7B, which fits the vendor IFEval of 61.2 vs 73.7. In the refuse-by-default product the engine then refuses those answers. That removes some confident errors ("fixed by refusal" 2-10 per screen), and it also removes correct answers (false refusals up to 8/20, U_cov far below the null floor).
- Excluding the refusals, the 2B's own correctness gain is small: fixes not by refusal are 6 / 6 / 5 / 5, against null fixes of 9-10 (K0) and 6-7 (K1) per GATE-V2 §3.
- The sampler is not the cause. E (engine sampling) is also NO-GO and has lower U_cov loss but fewer net fixes. V's T 1.0 + presence 2.0 raises citation loss on K1 (14 vs 4 warned).
- Stage 2 (MAIN n 97) was not run: no K0 GO, and the V K0 wall ratio is 1.56 > 1.5.

## Spend and deviations
- Haiku calls: screens 364 (100 + 82 + 100 + 82) + onboarding smoke 20 = 384 (cap 800). 0 Opus, 0 paid.
- V K0 judging first failed at the preflight (the criterion had `## Judge and budget` instead of a `## Budget` block). A format-only amendment was committed (42ebab1a) before any judge call, and V K0 was resumed from cached generation (screens/q35v-K0-resume.log).
- E (model swap only) was added to the coordinator's spec as a secondary candidate after the smoke showed long answers with vendor sampling. It was frozen in the criterion before generation.
- The mini was shared with 4-6 other lab jobs (slot starvation of about 50 min; free disk was 25 GiB at the V K0 start). Wall ratios are therefore load-confounded (see the load column).
- Not tested: Q8_0 or UD-Q4_K_XL of the 2B, and a citation-format prompt adapted to the 2B. Either would be a new arm with its own criterion.
