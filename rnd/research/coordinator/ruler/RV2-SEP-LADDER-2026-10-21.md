# RV2-SEP-LADDER: the ruler separates the 4B from the small tier; the 1.7B is level with a closed-book 1.5B (2026-10-21)

TL;DR (0 LLM, 0 judge, 0 generation; existing Haiku 5.5-low judge.v1 rows; v0.1 dev 57 minus FLOOR's 6 deterministic items = **n 51**; criterion RV24-criterion.md sha 53f75edc… committed 69430af4 before computing):
- Ladder U (floor-adj): **1.5B closed-book 0.209 · 1.7B K0 0.249 · Gemma E2B 0.260 · 4B (phone cut 7) 0.376**.
- **4B − 1.5B = +0.167 (+0.117…+0.219)**, 39/6 items: H-a holds (>= 0.08, CI low > 0.03). Kill-1 not triggered: the ruler has tier resolution at n ≈ 50.
- **1.7B − 1.5B = +0.040 (−0.019…+0.096)**: H-b holds (< 0.05), NOT SEPARABLE. **Coverage DiD = −0.007 (−0.136…+0.114)**: kill-2 triggered → drop the "coverage explains the level" sentence.
- Page sentence (mechanical, criterion rule): **"The ruler separates the 4B from the 1.7B and Gemma tier (+0.12 to +0.13 U, CI low ≥ +0.07); the 1.7B sits within noise of a closed-book 1.5B on this set (+0.04, CI −0.02…+0.10), under both judge.v1 and v1.1."**

## 1. Levels (n 51; U = Σ(s−1)/Σ(r−1); U_net = (U − 0.058)/0.942; item-cluster bootstrap B 2000 seed 11)
| rung | U (CI) | U_net |
|---|---|---|
| L0 Qwen2.5-1.5B closed-book (FLOOR) | 0.209 (0.154–0.272) | 0.161 |
| L1 1.7B K0 desktop, s42+c43 | 0.249 (0.198–0.308) | 0.203 |
| L2 Gemma 4 E2B desktop, s42+g43 | 0.260 (0.207–0.320) | 0.214 |
| L3 Qwen3-4B cut 7, Pixel 8a | 0.376 (0.323–0.432) | 0.338 |

## 2. Adjacent pairs (rule: SEPARABLE iff dU >= 0.05 and CI low > 0; identical verdicts on the U_net scale)
| pair | dU (CI) | dU_net | better/worse | verdict | MDE at n 75 |
|---|---|---|---|---|---|
| 1.7B − 1.5B | +0.040 (−0.019…+0.096) | +0.043 | 28/17 | not separable | 0.066 |
| Gemma − 1.7B | +0.010 (−0.027…+0.050) | +0.011 | 21/18 | not separable | 0.045 |
| 4B − Gemma | **+0.117 (+0.074…+0.162)** | +0.124 | 34/12 | **SEPARABLE** | 0.052 |
| Gemma − 1.5B | +0.051 (−0.008…+0.108) | +0.054 | 30/17 | not separable (CI touches 0) | 0.068 |
| 4B − 1.7B | **+0.127 (+0.086…+0.172)** | +0.135 | 37/7 | **SEPARABLE** | 0.051 |
| 4B − 1.5B | **+0.167 (+0.117…+0.219)** | +0.178 | 39/6 | **SEPARABLE** | 0.060 |
Order of points is 1.5B < 1.7B < Gemma < 4B, but only the step to the 4B is resolved. The ladder is two levels, {1.5B, 1.7B, Gemma} and {4B}.

## 3. Sensitivities (no rule)
| set | 1.7B−1.5B | Gemma−1.7B | 4B−Gemma | 4B−1.5B |
|---|---|---|---|---|
| all 57 | +0.036 (−0.015…+0.089) | +0.009 | +0.106 (+0.066…+0.148) | +0.151 (+0.104…+0.200) |
| 42 (minus the 15 phone-deterministic ids, deterministic-v01.ids ∩ 57) | +0.013 (−0.040…+0.064) | +0.013 | +0.144 (+0.094…+0.196) | +0.169 (+0.115…+0.219) |
| n 51, phone Gemma for L2 | | +0.015 (−0.025…+0.057) | +0.112 (+0.063…+0.166) | |
| n 51, desktop 4B cut 7 s42 for L3 | | | | +0.163 (+0.108…+0.217) |
| n 51, 1.7B s42 only | +0.038 (−0.023…+0.098) (= FLOOR sens) | | | |
- judge.v1.1 (JUDGE-V1_1.md addendum, quoted, all 57): 1.7B − 1.5B +0.047 (−0.0005…+0.097), LEVEL. Both judges agree.
- U_CU (RV1) not computed: RV1 has no result yet.

## 4. Coverage DiD (H-c; covered = the 1.7B s42 trace kept >= 1 source)
| subset | n | 1.7B − 1.5B |
|---|---|---|
| covered | 31 | +0.038 (−0.028…+0.097) |
| uncovered | 20 | +0.045 (−0.058…+0.157) |
| DiD | | **−0.007 (−0.136…+0.114)** |
Kill-2 fires (covered gap <= 0.05 and DiD CI includes 0): the 1.7B's small edge over the 1.5B is not located on items where it kept a source. Report: "level with a closed-book 1.5B on dev, both judges".

## 5. What the R2 spec / page take from this
1. Spec §8 separability stays a **gate on the 4B tier only**. "decline < 1B < app" is not printed for the 1.7B. Each R4 row prints its MDE: about 0.05–0.07 at n 75 for these pairs (0.066 for 1.7B vs 1.5B).
2. The "1B row is a level anchor; separability is a coverage property" framing is **withdrawn**: the coverage half fails (DiD ≈ 0).
3. Confound: the 4B rung is cut 7 + claim kit on the phone; the lower three are the K0 litepacks engine. The weight-only swap on MAIN 97 (VS4B: 4B − 1.7B +0.076, +0.050…+0.101) shows the model step alone is also separable. So the 4B gap is mostly the model, with some engine/kit difference on top.
4. Caveats: Haiku L1 judge (compresses gaps), v0.1 dev ids, one phone run for the 4B, 1.5B not 1B.

## Files
- RV2-SEP-LADDER-2026-10-21.json (all numbers), tools/rv2_ladder.py (`python3 -I tools/rv2_ladder.py RV2-SEP-LADDER-2026-10-21.json`), RV24-criterion.md + .sha256.
