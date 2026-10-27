# RV1-DECLINE-CU: U from completeness + usefulness only (U_CU) -- NO-ADOPT (2026-10-21)

- Criterion: RV1-HON8-criterion.md (sha256 03027cfb..., rnd b1220d1e, committed before computing).
- Script: tools/rv1_cu.py (sha256 8d53109d7e76...), python3 -I tools/rv1_cu.py RV1-DECLINE-CU-2026-10-21.json. Output sha256 a5c8655cf0b6...
- Cost: 0 LLM, 0 judge, 0 generation, 0 paid. Existing Haiku 5.5-low judge.v1 rows (both orders) + Opus rows of CE-OPUS-RU. Dev only.

## TL;DR
- **U_CU fixes the decline arm (a, b, c all U 0.000, CI 0-0), is quieter on retest (SD 0.0177 vs 0.0206) and keeps item order (Spearman >= 0.895), but fails the frozen kill clause on gap moves:** 4B - 1.5B moves -0.039 (CI -0.062...-0.015) and Gemma - 1.5B moves -0.036 on the v0.1 51 (bar < 0.03). The consistency bar also fails (mean |dn| 0.083 vs 0.05), mostly a scale compression (signed -0.080). **Verdict NO-ADOPT; U_CU is never quoted.**
- **Why it moves the 1.5B gaps:** the closed-book 1.5B differs from the others mainly in correctness. Dropping that dimension shrinks 1.7B - 1.5B from +0.040 to **+0.011**. So the 1.7B's small edge over a closed-book 1.5B lives entirely in correctness.
- **U_Z (zero correctness only on an engine decline) NO-ADOPT:** the decline variants carry no engine decline signal (0/30 flagged), so U_Z = U_full there (a 0.058, b 0.053: FAIL). On real traces it only touches the 3 engine-declined MAIN items per arm, which the spec's z override already zeroes.
- **Fallback (kill clause verbatim; v1.1c already failed JUDGE-V1_1B):** R1 = **judge.v1 + decline subtraction**, U' = (U - 0.058)/0.942, with U_dec 0.058 (0.037-0.081) printed in every row, and the decline arm marked "invalid as a floor, used as an offset".
- **No rank flips and no separability verdict changes** under U_CU, on the ladder or on MAIN 97.

## 1. Decline validity (30 ids; bar: U CI high <= 0.05)
| variant | U_full | U_CU | U_Z (engine flag) | U_Z' (labels.is_decline) | U' subtraction |
|---|---|---|---|---|---|
| (a) bare refusal | 0.058 (0.037-0.081) FAIL | **0.000 (0-0)** | 0.058 FAIL (0/30 flagged) | 0.000 (30/30 flagged) | 0.000 (-0.022...+0.024) |
| (b) hedged | 0.053 (0.034-0.075) FAIL | **0.000 (0-0)** | 0.053 FAIL | 0.053 FAIL (0/30) | -0.005 (-0.026...+0.018) |
| (c) fluent no-content | 0.016 (0.009-0.025) | **0.000 (0-0)** | 0.016 | 0.016 | -0.044 (-0.052...-0.035) |
- U' passes by construction on (a) and over-corrects (c) to -0.044: the subtraction's known limit (one constant for a wording-dependent leak).

## 2. Consistency 40 (v1 repeats 1-3; bars from JUDGE-V1_1: mean |dn| <= 0.05, CE flips <= 2)
| | value | bar | |
|---|---|---|---|
| mean abs dn (n_CU vs n_full) | **0.083** (correct 0.146, wrong 0.020); signed -0.080 | <= 0.05 | **FAIL** |
| CE-label flips | **0** (by construction) | <= 2 | pass |
| U on the 40 (rep 1) | full 0.281 -> CU 0.189 | | |
- CE definition under U_CU: CE = correctness (mean of both orders) <= 1.5 from the same judge.v1 rows, unchanged; correctness stays in the judge output and feeds CE only. Script asserts 0 flips.
- Reading: the dn gap is a level shift, not noise. Correct answers drop from n 0.49 to 0.35 because the judge gives correctness higher marks than completeness/usefulness on right answers. A CU-only proxy (mean(compl, useful) <= 1.5) agrees with CE on 111/120 rows (8 proxy-only, 1 CE-only), so U_CU still sees errors through usefulness.

## 3. Test-retest (20 ids, v1 repeats 1-2; bar <= 0.0206)
- SD n_CU **0.0177** (pass) vs n_full 0.0206; identical s on 16/20 (full 12/20). Without deterministic ids (n 14): 0.0221 vs 0.0231. All 97, 3 repeats: 0.0247 vs 0.0286.

## 4. Gaps and ranks (bar: every |move| < 0.03, no rank flip)
v0.1 51 (rv2_ladder rungs; item-cluster bootstrap B 2000, seed 11; move CI = paired bootstrap of dU_CU - dU_full)
| pair | dU_full | dU_CU | move (CI) | separable full / CU |
|---|---|---|---|---|
| 1.7B - 1.5B | +0.040 (-0.019...+0.096) | +0.011 (-0.034...+0.054) | -0.029 (-0.049...-0.009) | no / no |
| Gemma - 1.7B | +0.010 | +0.003 | -0.007 | no / no |
| 4B - Gemma | +0.117 (+0.074...+0.162) | +0.115 (+0.077...+0.154) | -0.002 | yes / yes |
| Gemma - 1.5B | +0.051 (-0.008...+0.108) | +0.014 | **-0.036** (-0.061...-0.012) | no / no |
| 4B - 1.7B | +0.127 | +0.118 | -0.010 | yes / yes |
| 4B - 1.5B | +0.167 (+0.117...+0.219) | +0.129 (+0.084...+0.173) | **-0.039** (-0.062...-0.015) | yes / yes |
- Levels U_full -> U_CU: 1.5B 0.209 -> 0.134, 1.7B 0.249 -> 0.145, Gemma 0.260 -> 0.148, 4B 0.376 -> 0.263. Order identical.

MAIN 97 K0 s42
| pair | dU_full | dU_CU | move |
|---|---|---|---|
| 4B - 1.7B | +0.097 (+0.064...+0.130) | +0.102 (+0.077...+0.129) | +0.005 |
| Gemma - 1.7B | +0.036 (+0.008...+0.065) | +0.026 (+0.002...+0.050) | -0.010 |
| 4B - Gemma | +0.061 (+0.028...+0.097) | +0.076 (+0.048...+0.106) | +0.015 |
- Sensitivity without deterministic ids (n 75): moves +0.007 / -0.013 / +0.019. All 57: 4B - 1.5B -0.035, Gemma - 1.5B -0.033.
- Max |move| 0.0385 -> **FAIL**. Ranks identical in every block; no separability verdict changes.

## 5. Item Spearman (bar >= 0.85): min **0.895** (1.5B); 1.7B 0.922, Gemma 0.948, 4B 0.913; MAIN 0.901 / 0.939 / 0.940 -> pass.

## 6. Opus family check (CE-OPUS-RU 38, no rule)
- U_full 0.411 (0.325-0.494) -> U_CU 0.301 (0.230-0.369); Spearman 0.942. Opus CE 7, all 7 also CU-proxy <= 1.5 (proxy flags 12). Same shape as Haiku: CU compresses, keeps order.

## Verdict and what R1 takes
| check | U_CU | U_Z |
|---|---|---|
| decline a/b/c | pass | **FAIL** (a, b) |
| consistency 40 | **FAIL** (0.083) | n/a |
| retest | pass | n/a |
| gaps / ranks | **FAIL** (4B-1.5B -0.039, Gemma-1.5B -0.036) | pass |
| Spearman | pass | n/a |
| verdict | **NO-ADOPT** | **NO-ADOPT** |
- R1: judge.v1 + decline subtraction (U_dec 0.058, CI 0.037-0.081, in every row; decline arm "invalid as a floor, used as an offset"). U_CU is not quoted on the page or in the spec.
- Side finding for RV2 / the page (no rule): the 1.7B vs closed-book 1.5B edge (+0.04) is a correctness-only difference; on completeness + usefulness the two are level (+0.011). That supports "level with a closed-book 1.5B".
- UNKNOWN: whether a bar on gap moves of 0.03 is right for a metric that rescales the whole axis (U_CU compresses U by about 30 %); the frozen rule does not rescale, and it was applied as written.

## Files
RV1-DECLINE-CU-2026-10-21.json (+ .sha256), tools/rv1_cu.py, RV1-HON8-criterion.md (+ .sha256).
