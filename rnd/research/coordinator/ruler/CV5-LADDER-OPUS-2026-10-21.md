# CV5-LADDER-OPUS (2026-10-21): the 4B gap holds under Opus; the "1.7B level with a closed-book 1.5B" sentence is KILLED (separable under Opus, not under Haiku)

Criterion CV5-LADDER-OPUS-criterion.md (sha 3870ac70..., rnd b551a774) frozen before any call. 324 new Opus judge.v1 calls (cap 360) + 24 reused units, 0 generation, 0 paid, 0 Haiku.
v0.1 dev, RV2 primary 51 ids, one seed per rung (deviation stated in the criterion: two seeds would need 476 calls). Output CV5-LADDER-OPUS-2026-10-21.json (sha a3c6fcb3b2d1...), tools/cv5_ladder.py.

## TL;DR
- **Verdict: KILLED (level sentence only).** Separability of the 4B survives; the "level" sentence does not.
- Under Opus, **4B − 1.7B = +0.109 (+0.063…+0.160)** and **4B − Gemma = +0.098 (+0.054…+0.146)**: both SEPARABLE. Kill-sep not met.
- Under Opus, **1.7B − 1.5B = +0.090 (+0.009…+0.170)**: CI low > 0, so **kill-level fires**. Under Haiku on the same frame it is +0.038 (−0.023…+0.098).
- Haiku and Opus rank items alike: Spearman 0.89 to 0.94 per rung, so the Haiku rows stay on the page.
- But Opus lifts the closed-book 1.5B less than the three RAG rungs. The Opus − Haiku offset is +0.052 for the 1.5B vs +0.084 to +0.104 for the others (spread 0.052).
- The Haiku L1 judge compressed the 1.7B's lead over the floor.

## Levels (U floor-adj, n 51, item-cluster bootstrap B 2000 seed 11)
| rung | Opus U (CI) | Haiku U, same frame | Opus − Haiku (CI) | Spearman s | CE agree / correct agree (of 51) |
|---|---|---|---|---|---|
| L0 Qwen2.5-1.5B closed-book | 0.261 (0.189–0.342) | 0.209 | +0.052 (+0.026…+0.080) | 0.94 | 48 / 48 |
| L1 1.7B K0 s42 | 0.351 (0.279–0.437) | 0.248 | +0.104 (+0.066…+0.142) | 0.90 | 46 / 44 |
| L2 Gemma E2B s42 | 0.362 (0.290–0.444) | 0.266 | +0.096 (+0.061…+0.132) | 0.91 | 45 / 39 |
| L3 4B cut 7 Pixel 8a | 0.460 (0.387–0.537) | 0.376 | +0.084 (+0.044…+0.122) | 0.89 | 49 / 42 |

## Pairs (SEPARABLE iff dU >= 0.05 and CI low > 0)
| pair | Opus dU (CI) | better/worse | verdict | Haiku same frame | Haiku RV2 two-seed |
|---|---|---|---|---|---|
| 1.7B − 1.5B | **+0.090 (+0.009…+0.170)** | 25/13 | **SEPARABLE** | +0.038 (−0.023…+0.098), not | +0.040 (−0.019…+0.096), not |
| Gemma − 1.7B | +0.011 (−0.033…+0.056) | 22/15 | not | +0.018, not | +0.010, not |
| 4B − Gemma | **+0.098 (+0.054…+0.146)** | 27/10 | SEPARABLE | +0.111 (+0.070…+0.155) | +0.117 (+0.074…+0.162) |
| Gemma − 1.5B | +0.101 (+0.027…+0.179) | 32/11 | SEPARABLE | +0.057 (+0.001…+0.113) | +0.051 (−0.008…+0.108) |
| 4B − 1.7B | **+0.109 (+0.063…+0.160)** | 29/7 | SEPARABLE | +0.129 (+0.085…+0.177) | +0.127 (+0.086…+0.172) |
| 4B − 1.5B | +0.199 (+0.132…+0.270) | 38/6 | SEPARABLE | +0.167 (+0.117…+0.219) | +0.167 (+0.117…+0.219) |

MDE at n 75 under Opus: 0.093 for 1.7B − 1.5B, 0.055 for 4B − 1.7B.

Reading:
- Under Opus the ladder has three levels: {1.5B closed-book} < {1.7B ≈ Gemma} < {4B}.
- Under Haiku it has two: {1.5B, 1.7B, Gemma} < {4B}.
- The 1.7B − 1.5B CI low is +0.009, just above 0. One seed, so this is not a robust margin.

## Sentences the page may print (mechanical, from the criterion flags)
- **S1a (stands, both judges):** "The ruler separates the 4B from the 1.7B and Gemma tier: +0.11 and +0.10 U under Opus (CI low ≥ +0.05), +0.13 and +0.11 under Haiku (v0.1 dev, 51 items, one run)."
- **S1b (replaces 'the 1.7B is level with a closed-book 1.5B'):** "Whether the 1.7B beats a closed-book Qwen2.5-1.5B depends on the judge. It is separable under Opus (+0.09 U, CI +0.01…+0.17) and not under Haiku (+0.04, CI −0.02…+0.10), on 51 dev items, one run."
- **Caveat line:** "Opus scores every rung higher than Haiku (+0.05 to +0.10 U), and it lifts the closed-book baseline least. Item rankings agree (Spearman 0.89–0.94)."
- Do NOT print: "the 1.7B sits within noise of a closed-book 1.5B" without naming Haiku; "decline < 1B < app" as a two-judge result; any ladder ratio without its judge family.

## Limits
- One seed per rung, and the 1.7B − 1.5B CI low is +0.009.
- The 4B rung is cut 7 + kit on the phone, vs the K0 engine for the others (RV2 confound).
- 1.5B, not 1B; dev ids. Reused units came from 5 earlier Opus passes on the identical (item, text, frame).

## Files
- ruler/cv5-ladder/in/set.json (units, reuse), cv5-ladder/out/*.judgments.jsonl
- tools/cv5_opus_pool.py, cv5_ladder_prep.py, cv5_ladder_run.sh, cv5_ladder.py
