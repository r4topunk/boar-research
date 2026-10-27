# GEMMA-VS-4B (2026-10-21): 4B - 1.7B +0.076 [+0.050, +0.101]; 4B - Gemma +0.048 [+0.021, +0.075]; Gemma captures F 0.38 [0.13, 0.68] of the 4B gain (pooled seeds)

TL;DR: measurement, no pass/fail. Criterion VS4B-criterion.md (sha256 4212369b...), committed 3d76b5c5 before generation. Qwen3-4B-Instruct-2507 Q4_K_M as a weight-only swap at the lite (compact) tier, MAIN 97 K0, seed 42, Haiku 5.5-low judge (judge.v1-low, both orders, N 4). Report: vs4b/vs4b-report.json from tools/vs4b_report.py (frozen).

| Pair (cand - ctl) | U ctl | U cand | dU [95 % CI] | CE-unwarned (count) | refused R | default-mode dU [CI] | U on both-shown (n) dU [CI] |
|---|---|---|---|---|---|---|---|
| 4B - 1.7B s42 | 0.4055 | 0.4814 | **+0.076 [+0.050, +0.101]** | 7 -> 5 (dCEu CI -0.083...+0.041) | 46 -> 47 | +0.029 [+0.001, +0.059] | +0.057 [+0.019, +0.098] (47) |
| 4B - Gemma s42 | 0.4336 | 0.4814 | **+0.048 [+0.021, +0.075]** | 2 -> 5 (CI -0.021...+0.083) | 41 -> 47 | -0.005 [-0.040, +0.029] | +0.043 [+0.007, +0.081] (48) |
| 4B s42 - Gemma s43 (cross seed) | 0.4323 | 0.4814 | +0.049 [+0.022, +0.080] | 6 -> 5 | 40 -> 47 | -0.003 [-0.038, +0.031] | +0.059 [+0.023, +0.100] (49) |
| Gemma - 1.7B s42 (ref = stage 2) | 0.4055 | 0.4336 | +0.028 [+0.006, +0.052] | 7 -> 2 | 46 -> 41 | +0.034 [+0.004, +0.067] | +0.023 [-0.011, +0.058] (47) |

Fraction of the 4B gain Gemma captures: **F42 0.37 [0.09, 0.65]**, **Fpool 0.38 [0.13, 0.68]** (Gemma and 1.7B pooled over seeds 42 + 43 vs the 4B seed 42; 0 % of resamples with denominator <= 0).

| Cost (mini M4, live LLM items 75/97) | 1.7B | Gemma E2B | 4B |
|---|---|---|---|
| answer tokens (mean) | 45.5 | 52.9 | 68.4 |
| prompt tokens (mean) | 384 | 384 | 380 |
| wall per item mean / p50 (ms, slot contention included) | 1863 / 2028 | 2784 / 3011 | 4963 / 5308 |

## Reading (pre-registered rule)
1. The 4B is measurably better than the 1.7B on MAIN K0 (CI low +0.050 > 0).
2. 4B vs Gemma: 4B better than Gemma at both Gemma seeds (CI low +0.021 / +0.022 > 0).
3. F: point < 0.5 -> **Gemma captures less than half of the 4B gain** (about 38 %; CI 0.13-0.68 is wide).
4. One 4B seed: the 4B - Gemma delta (+0.048) is below the 0.05 one-seed noise rule, so the ordering is not robust on one seed, though its CI excludes 0 at both Gemma seeds.
Where the 4B gain comes from: unlike Gemma, it does not refuse less (R 46 -> 47); it answers better on the items it shows (both-shown dU +0.057 vs Gemma's +0.023). In default mode (warned = refused) the 4B and Gemma are level (-0.005). The 4B costs about 1.8x Gemma's wall and 2.7x the 1.7B's on the mini, with longer answers.

## Sanity (criterion clauses): 97/97 traces, 0 errors, model.sha256 3605803b on 97/97, 0 reasoning tokens, 75 answers differ from lpctl-K0-main-s42. PASS.
## Calls and paths
Haiku 5.5-low: 150 (v01 84, cooking 28, money 38; 22 answers byte-identical to the control reused its rows) of the 200 cap. 0 Opus, 0 paid.
Run: CRITERION=VS4B-criterion.md lp-screens/tools/run_arm.sh gemma4-e2b-vs4b K0 main gemma4-e2b/vs4b-engsamp.patch (sha256 485fecea...); outputs gemma4-e2b/vs4b/{traces,judgments,aggregates,runs} (arms/gemma4-e2b-vs4b = symlink); mini generation 02:31-02:40, judged 02:40-02:44.
Not measured: the 4B on its own product tier (non-compact prompts/declines), phone speed.
