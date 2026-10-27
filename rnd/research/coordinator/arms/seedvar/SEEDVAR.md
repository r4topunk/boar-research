# SEEDVAR result (coordinator-run, 2026-10-10 12:33–13:2x). Criterion SEEDVAR-criterion.md sha256 f7196323ac5f28e119a08cc609be1ed2032706059abf8f8ea75a7c8be3b0feb4 (not edited); measurement only, no verdict
**Finding: the recommended deep configuration (cut 6 + Qwen3.6-35B + thinking 512, DT512 arm H) scores raw 0.533 / 0.572 / 0.544 on V-para across seeds 42 / 43 / 44 (Opus judge.v1, 51 ids): mean 0.550, SD 0.020 (floor-adjusted 0.412 / 0.460 / 0.425, mean 0.432, SD 0.025). Seed 43 is the high point; s42 vs s44 differ by −0.011 (−0.049…+0.023). A one-seed deep number on V-para carries ≈ ±0.02 (1 SD, ratio) and ±0.025 floor-adjusted; the two-seed claim rows (0.436 floor-adj) sit 0.004 above the three-seed mean. On v0.2 the same tier is stable across seeds (0.613 / 0.612, per-item r 0.90), so the instability is set-specific (51 bounty-style items, frontier reference).**

## Identity
| item | value |
|---|---|
| run | `dh-H-vpara-s44` on the dt512 tree (cut 6 824e0b35… + deepthink eb3f464b… + dt512 f9a1979b…), requests = H s42 with seed 44 (sha a062f940…), 58/58 rc 0, 0 errors, 51 deep-thinking, reasoning 522 on 51/51 (budget 512 bound on 48), answer tokens median 97, p50 80.4 s (p90 98.1), ttft 69.9 s, mini 70 min |
| judge | Opus judge.v1 N = 4, 51 ids (102 calls, 0 failures), `--system dt512-H-opus`, refs 952e2c44 |
| script | `seedvar.mjs` (judge-core conventions as paired.mjs): per-seed ratio/floor/win, pairwise paired Δ, SD, per-item Pearson r |

## V-para (51 ids, Opus), per-seed and pairwise
| arm | s42 | s43 | s44 | mean | SD | pairwise Δ (CI) | per-item r |
|---|---|---|---|---|---|---|---|
| **H** deep + think 512 | 0.533 (0.500–0.563) | 0.572 (0.538–0.607) | 0.544 (0.509–0.579) | **0.550** | **0.020** | 42−43 −0.039 (−0.072…−0.011); 42−44 −0.011 (−0.049…+0.023); 43−44 +0.028 (+0.002…+0.057) | 0.60 / 0.48 / 0.68 |
| T deep + think 1024 | 0.518 | 0.566 | — | 0.542 | 0.034 | −0.048 (−0.083…−0.017) | 0.53 (shares H's first 512 thinking tokens per seed: not independent) |
| D deep, no thinking | 0.460 | 0.474 | — | 0.467 | 0.011 | −0.015 (−0.050…+0.019) | 0.50 |
| K 4B claim (cut 6) | 0.413 | 0.413 | — | 0.413 | 0.000 | 0.000 (−0.023…+0.023) | **0.81** |
Win-rate 0 for every seed and arm. Floor-adjusted H: 0.412 / 0.460 / 0.425 (mean 0.432, SD 0.025).

## v0.2 (110 ids, Opus, two seeds; existing rows)
| arm | s42 | s43 | Δ (CI) | per-item r |
|---|---|---|---|---|
| TV deep + think 1024 | 0.613 | 0.612 | +0.001 (−0.015…+0.016) | 0.90 |
| D deep, no thinking | 0.564 | 0.571 | −0.006 (−0.030…+0.018) | 0.80 |
| K 4B claim | 0.519 | 0.506 | +0.014 (−0.002…+0.032) | 0.90 |

## Reading and rules of thumb
- The thinking tier's answers on V-para are a per-item lottery across seeds (r ≈ 0.5–0.7; the 4B's 0.81): long reasoning chains diverge, and the frontier reference punishes the wrong branch. The set-level mean is nevertheless stable to ≈ ±0.02.
- For decisions: a one-seed deep-tier Δ on V-para below ≈ 0.03 is within seed noise (two independent one-seed runs differ by SD·√2 ≈ 0.03); paired designs on the same seed share the sampling seed but not the trajectory, so they do not cancel this noise. Today's THINK4B (+0.026, one seed) and the DT512-vs-T comparisons (+0.011) are inside that band; the claim-scale deep numbers (two seeds) carry ≈ ±0.014.
- L1-PROTOCOL: add "V-para deep-tier one-seed numbers: ±0.02 raw / ±0.025 floor-adj (SEEDVAR); v0.2: ±0.01". DT512.md: the three-seed H mean 0.550 raw / 0.432 floor-adj is a note beside the frozen two-seed result, not a replacement.

## Exposures (script-only)
V-para: 1 full generation (58, seed 44) + Opus 51 ids (102 calls); other seeds' rows re-read. Outputs: `blind/V-para/runs-dt512/dh-H-vpara-s44.*`, aggregates here (`seedvar-H-3seed.opus.json`, `think-H-s44.json`). Cost: Opus 102, Haiku 0, mini 70 min.
