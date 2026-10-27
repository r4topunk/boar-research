# GEMMA-PACKS (N3, 2026-10-21): Gemma gains more from K3 than the 1.7B: DiD +0.034 [+0.001, +0.066] on the 80 candidate-pack self-tests

TL;DR: measurement, no pass/fail. Criterion PACKS-criterion.md (sha256 624aac30...), committed 3d76b5c5 before generation. Gemma 4 E2B (engine sampler, seed 42, mini) K0 and K3 on the 80 candidate-pack self-tests (pack-matched under K3), vs the 1.7B's LITEPACKS K0/K3 rows (reused, MacBook). Haiku 5.5-low judge (judge.v1-low, both orders, N 4). Report packs/packs-report.json from tools/packs_report.py (frozen).

| All 80 | 1.7B K0 | 1.7B K3 | Gemma K0 | Gemma K3 |
|---|---|---|---|---|
| U | 0.393 | 0.462 | 0.395 | 0.497 |
| CE-unwarned (count) | 8 | 6 | 6 | 5 |
| CE any | 20 | 9 | 11 | 5 |
| declines / warned / refused R | 16 / 38 / 54 | 13 / 27 / 40 | 17 / 34 / 50 | 13 / 3 / 16 |
| default-mode U (R := 0) | 0.144 | 0.265 | 0.160 | 0.429 |
| prompt tokens mean / p50 (live 61) | 360 / 290 | 907 / 912 | 361 / 293 | 896 / 905 |
| answer tokens mean | 46.1 | 45.6 | 49.7 | 60.0 |
| wall mean / p50 ms (host) | 2155 / 2251 (M1 Pro) | 4652 / 5516 (M1 Pro) | 2581 / 2878 (M4) | 5367 / 6475 (M4) |

| Delta [95 % CI] (paired item bootstrap, 4 rows per item) | value |
|---|---|
| dU Gemma K3 - K0 | **+0.102 [+0.061, +0.144]** |
| dU 1.7B K3 - K0 | +0.069 [+0.038, +0.100] |
| **DiD (Gemma - 1.7B)** | **+0.034 [+0.001, +0.066]** |
| level at K0, Gemma - 1.7B | +0.001 [-0.021, +0.023] |
| level at K3, Gemma - 1.7B | +0.035 [+0.006, +0.064] |
| default-mode DiD | +0.147 [+0.090, +0.209] |
| CE-unwarned rate DiD | +0.013 [-0.050, +0.075] |

Per pack (n 20, indicative): DiD simplewiki +0.077 [-0.001, +0.156], factbook +0.000 [-0.088, +0.089], medlineplus +0.027 [-0.026, +0.070], firstaid +0.033 [-0.000, +0.070]; Gemma dU simplewiki +0.183, factbook +0.104, medlineplus +0.084, firstaid +0.039.

## Reading (pre-registered rule)
1. DiD CI low +0.001 > 0 -> **"Gemma gains more from the K3 packs than the 1.7B (reads packs better)"**, by a hair: the CI low sits at the boundary, one seed.
2. dU_G CI low > 0 -> the packs help Gemma on their own topics (+0.10).
3. Per-pack slices indicative only; the gain is concentrated in simplewiki.
4. Caveats: one seed; self-tests are pack-written (on-topic ceiling, not casual traffic); host differs between the models (cancels inside each model's K3 - K0, not in the level gaps; at K0 the two models are level, +0.001).
Mechanism (post-hoc, not part of the rule): with K3 Gemma almost never triggers the warning line (warned 34 -> 3, vs the 1.7B 38 -> 27), i.e. its cited answers survive the engine's citation checks, so in default mode (warned = refused) Gemma K3 shows 64 of 80 answers vs the 1.7B's 40, hence the large default-mode DiD (+0.147). CE-unwarned stays flat (5 vs 6). Cost: K3 more than doubles prompt tokens (about 900) for both models; Gemma writes longer K3 answers (60 vs 46 tokens).

## Sanity (criterion clauses): G0 and G3 80/80 traces, 0 errors, model.sha256 740185b2 on 80/80, 0 reasoning tokens, 0 thought markers, G3 kit = 6 packs. PASS.
## Calls and paths
Haiku 5.5-low: G0 102 (51 judged; 29 reused byte-identical rows: 1.7B mini pool-K0 text or the 12 overlapping Gemma screen items) + G3 132 (66 changed vs G0) = **234** of the 250 cap. With GEMMA-VS-4B (150): **384 of 450**. 0 Opus, 0 paid.
Runs: tools/run_pool_k.sh (run_pool.sh + 2 lines) gemma4-e2b-eng K0 / K3 packs/cand80.ids gemma4-e2b-engsamp.patch, OUT_BASE=gemma4-e2b/packs; mini generation 02:31-02:44 (G0), 02:47-02:55 (G3). Deviation (path only): run_pool writes under packs/gemma4-e2b-eng/, so the criterion's G3 CTLAGG_OVERRIDE and the report's paths were reached through symlinks packs/traces -> gemma4-e2b-eng/traces and packs/aggregates/gemma4-e2b-eng-K{0,3}-cand80-s42.json -> ../gemma4-e2b-eng/aggregates/ (G3 used the real G0 aggregate path; same file). No script or number changed.
