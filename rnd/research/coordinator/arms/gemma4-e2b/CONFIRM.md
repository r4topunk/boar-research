# GEMMA4-E2B confirm (Q7a2, 2026-10-21): seed 43 K0 dU +0.030 [+0.007, +0.052]; pooled two-seed K0 dU +0.029 [+0.009, +0.048]; stage-2 FAIL stands; K1 MAIN dU +0.017 [-0.008, +0.040]

TL;DR: measurement only. Criterion = arms/gemma4-e2b-confirm/CONFIRM-criterion.md (sha256 42ca5c6d..., frozen 2026-10-20 23:48 before any generation; hash re-checked). It has **no pass/fail clause**: its reading rule says the numbers are reported as measured and the GEMMA4-E2B stage-2 verdict (FAIL, dU +0.0281 < +0.03, stage2/verdict.json) stays. Applying the +0.03 bar to M1 or the pooled estimate would need a new, separate pre-registration, and none was made. So this file gives **no new verdict**. For information only: both the seed-43 point (+0.0298) and the pooled point (+0.0290) sit just under +0.03, and both CIs exclude 0.

Judge: Haiku 5.5-low (judge.v1-low, both orders, N = 4 shards). Dev set MAIN 97 (lp-screens/main-97.ids). Engine-sampler variant E. 0 Opus, 0 paid.

## Numbers (gemma4-e2b-confirm/tools/confirm_report.py definitions, B 2000, seed 11, items resampled)
| Measure | 1.7B control | Gemma E2B | delta [95 % CI] |
|---|---|---|---|
| **M1 seed 43, K0: U** | 0.4024 | 0.4323 | **+0.0298 [+0.0073, +0.0520]** |
| M1 CE-unwarned rate (count) | 0.072 (7) | 0.062 (6) | -0.010 |
| M1 CE any (count) | 19 | 16 | |
| M1 declined / warned / refused R | 7 / 39 / 46 | 9 / 32 / 40 | |
| M1 default-mode U (R := 0) | 0.251 | 0.289 | +0.038 [+0.010, +0.066] |
| M1 U on covered (51) | 0.471 | 0.483 | +0.012 [-0.027, +0.050] |
| ref seed 42, K0: U (recomputed; = stage2/verdict.json) | 0.4055 | 0.4336 | +0.0281 [+0.0061, +0.0519] |
| ref seed 42 CE-unwarned (count) | 0.072 (7) | 0.021 (2) | -0.052 |
| **Pooled K0, 2 seeds x 97 (cluster bootstrap over items): U** | 0.4039 | 0.4329 | **+0.0290 [+0.0089, +0.0479]** |
| Pooled CE-unwarned rate (count / 194) | 0.072 (14) | 0.041 (8) | -0.031 [-0.083, +0.021] |
| Pooled refused R | 92 | 81 | |
| Mean of the per-seed dU | | | +0.0290 |

Reading: the U gain replicates across seeds (+0.028, +0.030). The CE-unwarned drop does not replicate at the same size: 7 -> 2 at seed 42, 7 -> 6 at seed 43, pooled -0.031 with a CI that includes 0. Covered-item U is flat at both seeds, so the U gain comes mostly from fewer refusals (R 46 -> 40/41) rather than better answers on the items the control shows.

## Frozen rule (stage 2, GEMMA4-criterion.md §4, unchanged)
PASS iff dU >= +0.03 and its paired bootstrap CI low > 0 and CE-unwarned rate change <= +0.02 (seed 42 only). Verdict: FAIL (dU +0.0281). This confirm run does not reopen it.

## Sanity (criterion clauses)
- c43: 97/97 traces, 0 errors, model.sha256 b139949c on 97/97, 70 answers differ from lpctl-K0-main-s42 (>= 10: the seed patch acted).
- g43: 97/97 traces, 0 errors, model.sha256 740185b2 on 97/97, 0 thought markers, 73 answers differ from the stage-2 Gemma run (>= 10).

## M2 (K1 MAIN, seed 42): done 2026-10-21 01:56 (full frozen confirm_report.py -> gemma4-e2b-confirm/confirm-report.json)
| M2 vs | U ctl | U Gemma+K1 | dU [95 % CI] | CE-unwarned (count) | refused R | default-mode dU [CI] | covered dU [CI] |
|---|---|---|---|---|---|---|---|
| K1 control lpctl-K1-main-s42 | 0.4102 | 0.4275 | +0.0173 [-0.0075, +0.0396] | 7 -> 9 (+0.021) | 53 -> 34 | +0.080 [+0.044, +0.117] | +0.002 [-0.038, +0.035] (44) |
| K0 control lpctl-K0-main-s42 (cross pack set) | 0.4055 | 0.4275 | +0.0221 [-0.0016, +0.0453] | 7 -> 9 (+0.021) | 46 -> 34 | +0.056 [+0.010, +0.100] | -0.049 [-0.108, +0.000] (51) |
On K1, Gemma refuses much less (R 53 -> 34). The default-mode U gain is large, but agg_run U is flat (CI includes 0) and CE-unwarned rises by 2. Sanity: 97/97 traces, model.sha256 740185b2 on 97/97, 0 thought markers, 75 answers changed vs the K1 control. Run: lp-screens/tools/run_arm.sh gemma4-e2b-confirm-gk1 K1 main gemma4-e2b-confirm/patches/g42.patch (relaunched 01:32 because generation never ran in the dead session), 150 Haiku calls.

## Tooling note
The final numbers (M1, pooled, M2) are from the frozen confirm_report.py (sha256 9749e229..., unchanged) -> gemma4-e2b-confirm/confirm-report.json; M1/pooled match the earlier interim run, made while gk1 was missing, from gemma4-e2b-confirm/tools/confirm_report_m1only.py: the same file with only the two K1 paths and the two M2 calls removed (diff = 4 lines, no metric change). It reproduces stage2/verdict.json exactly on the seed-42 pair. Output: gemma4-e2b-confirm/confirm-M1-pooled.json.

## Calls and paths
Haiku 5.5-low: c43 140 (00:06-00:08) + g43 150 (01:33-01:35, resumed after the rate-limit STOP; STOP file removed) + gk1 150 = **440** of the 600 cap. GEMMA4 arm total 534 + 440 = 974 across the two criteria.
Runs: gemma4-e2b-confirm/runs/{c43,g43,gk1} (symlinks arms/gemma4-e2b-confirm-{c43,g43,gk1}); aggregates gemma4-e2b-confirm/runs/{c43,g43}/aggregates/*.json. The Gemma GGUF stays on the mini (line open; N3 GEMMA-PACKS is waiting on this row).
