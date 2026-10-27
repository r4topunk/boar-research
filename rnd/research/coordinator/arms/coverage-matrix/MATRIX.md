# COVERAGE-MATRIX (2026-10-21): packs help every tier on their own topics; A-union = K3 minus the simplewiki slice; no MAIN harm on U, CE-unwarned 7 -> 12

TL;DR: measurement, no pass/fail. Criterion MATRIX-criterion.md (frozen sha dfc84677..., rnd ea5f8290, before generation; amendment 1 = "## Budget" heading for the preflight, cap unchanged, sha 897e46e0..., before any judge call). Seed 42, mini generation (6 new cells), Haiku 5.5-low judge (judge.v1-low, both orders, N 4), **652 of 700 calls**, 0 Opus, 0 paid. Report matrix-report.json from tools/matrix_report.py (frozen). Self-tests are pack-written: every in-pack number is an upper bound.

## Matrix: U [95 % CI] on the 80 candidate-pack self-tests
| tier | K0 (claim kit) | K3 (+simplewiki, factbook, medlineplus, firstaid) | KA (A-union: + visa, factbook, medlineplus, firstaid) |
|---|---|---|---|
| Qwen3-1.7B | 0.381 [0.350, 0.412] mini (MacBook 0.393) | 0.462 [0.427, 0.495] MacBook | 0.435 [0.401, 0.471] |
| Gemma 4 E2B | 0.395 [0.365, 0.424] | 0.497 [0.459, 0.535] | 0.450 [0.414, 0.489] |
| Qwen3-4B Q4_K_M (lite tier swap) | 0.461 [0.427, 0.496] | 0.545 [0.503, 0.586] | 0.513 [0.477, 0.550] |

| dU (paired bootstrap) | K3 - K0 | KA - K0 | KA - K3 | KA - K3 on60 (like-for-like) | KA - K3 simplewiki20 |
|---|---|---|---|---|---|
| 1.7B | +0.069 [+0.038, +0.100] (MacBook pair) | +0.054 [+0.022, +0.088] (mini pair) | -0.027 [-0.063, +0.008] (cross-host) | +0.009 [-0.028, +0.049] | -0.136 [-0.200, -0.075] |
| Gemma | +0.102 [+0.061, +0.144] | +0.055 [+0.015, +0.096] | **-0.047 [-0.089, -0.006]** | +0.006 [-0.033, +0.048] | -0.211 [-0.281, -0.137] |
| 4B | +0.084 [+0.047, +0.120] | +0.052 [+0.024, +0.083] | **-0.032 [-0.062, -0.000]** | -0.005 [-0.035, +0.026] | -0.112 [-0.188, -0.040] |

| per cell (all 80) | CE-unwarned | CE | declines / warned / refused R | prompt tok mean (p50, live 61) | answer tok | wall mean / p50 ms (host) |
|---|---|---|---|---|---|---|
| 1.7B K0 mini | 7 | 20 | 16 / 39 / 55 | 360 (290) | 44.8 | 1766 / 1947 (M4) |
| 1.7B K3 MacBook | 6 | 9 | 13 / 27 / 40 | 907 (912) | 45.6 | 4652 / 5516 (M1 Pro) |
| 1.7B KA | 6 | 15 | 12 / 30 / 42 | 773 (814) | 46.7 | 3375 / 3975 (M4) |
| Gemma K0 | 6 | 11 | 17 / 34 / 50 | 361 (293) | 49.7 | 2581 / 2878 |
| Gemma K3 | 5 | 5 | 13 / 3 / 16 | 896 (905) | 60.0 | 5367 / 6475 |
| Gemma KA | 6 | 8 | 14 / 16 / 28 | 766 (800) | 55.6 | 4922 / 6045 |
| 4B K0 | 6 | 12 | 16 / 40 / 56 | 356 (286) | 67.0 | 4978 / 5518 |
| 4B K3 | 5 | 8 | 13 / 16 / 29 | 903 (908) | 75.5 | 9978 / 12094 |
| 4B KA | 5 | 10 | 12 / 25 / 37 | 769 (810) | 72.6 | 8923 / 10733 |
dCEu rate vs K0: every cell within -0.025..0.000, all CIs straddle 0. Thermal: no sensor on the mini path; wall (mini, generation serialized by the slot guard, see Deviations) is the only latency/heat proxy. KA costs about 15 % fewer prompt tokens than K3 (visa adds few kept chunks vs simplewiki).

Tier gaps (all 80): 4B - 1.7B +0.080 [+0.054, +0.106] at K0, +0.083 at K3 (cross-host), +0.078 [+0.052, +0.106] at KA; Gemma - 1.7B +0.014 (CI straddles) at K0 and KA, +0.035 at K3; 4B - Gemma +0.066 / +0.048 / +0.063. Pack-gain DiD vs the 1.7B: K3 Gemma +0.034 [+0.001, +0.066] (= GEMMA-PACKS), K3 4B +0.015 (straddles), KA Gemma +0.001, KA 4B -0.002 (straddle).

## MAIN 97 no-harm (1.7B KA vs K0, same host)
U 0.406 -> 0.398, **dU -0.007 [-0.026, +0.012] -> "no harm shown"** (rule: CI low >= -0.03). CE-unwarned 7 -> 12, dCEu rate +0.052 [-0.010, +0.113] (above the LITEPACKS +0.02 CE clause, quoted, not a gate); refused R 46 -> 47; prompt tokens 384 -> 681; wall p50 2.0 -> 3.7 s.

## Reading (pre-registered rules)
1. Every pack set helps every tier on the pack-matched self-tests (all six dU CI lows > 0; upper bounds). 2. KA vs K3: K3 beats KA for Gemma and the 4B (CI highs < 0, 4B at the boundary), no measurable difference for the 1.7B (cross-host); the whole gap is the simplewiki20 slice, which is off-pack under KA (-0.11 to -0.21); on the like-for-like on60 slice KA = K3 for all tiers (|d| <= 0.009), so dropping simplewiki causes no crowding gain and no loss on the shared packs, and visa is unmeasured here (no visa self-tests in the 80). 3. MAIN: no harm shown on U; the CE-unwarned rise (5 more confident unwarned errors of 97, CI straddles 0) is the one cost signal and needs a look before KA becomes a default. 4. One seed; tier gaps under 0.05 (Gemma vs 1.7B) are not robust; Haiku-low compresses gaps. Coverage x quality: pack gain is about +0.05 (KA) to +0.07-0.10 (K3) at every tier, model gain about +0.08 (4B over 1.7B) at every pack set; they add, with no measurable interaction except Gemma's K3 DiD.

## Deviations and paths
- KA uses the v3proto factbook/medlineplus/firstaid files K3 uses (the persona-a-union MANIFEST pins the wave1/wave2 files; same content, no chunk_vecs sidecar); visa from wave4 via kadirs.patch (wave4 appended last to PACK_DIRS). No area tiles.
- merge_reuse.py fixed at 03:4x to copy full rows (agg_run --control needed CE); no effect on which items were judged (same text match). Cell 1 judged early (03:46) by hand in priority order; the driver then skipped it.
- The mini slot guard counts the adapter's node processes (their argv names llama-server), so only one generation ran at a time; wall columns carry no 2-slot contention.
- Calls: 1.7B KA 110, MAIN KA 114, Gemma KA 90, 4B K0 122, 4B K3 120, 4B KA 90 = 652 (reuse of byte-identical answers from tools/reuse_pool.txt and the matrix's own aggregates). Traces/judgments/aggregates under q17/, gemma/, q4b/; logs/; resume commands PLAN.md.
