# GEMMA4-E2B (2026-10-20): stage 1 GO on all 4 gate v2 screens; stage 2 FAIL by 0.002 on the dU clause

TL;DR: Gemma 4 E2B-it Q4_K_M as a straight swap for Qwen3-1.7B clears GATE v2 by a wide margin (net 16-21 vs bars 9-10, both samplers, both pack sets), and on MAIN n 97 (K0, engine sampler) gives **dU +0.028 (CI +0.006...+0.052)**, CE-unwarned 7.2 % -> 2.1 % (-0.052). The frozen PASS rule needs dU >= +0.03: **FAIL** (CI low > 0 and CEu clauses pass). Cost: answers ~20 % longer, wall 1.45-1.55x the 1.7B on the mini, projected Pixel decode 8.6 tok/s (7.4-9.9).
Criterion GEMMA4-criterion.md (sha 690eeead...), committed ddff2791 before generation; gate v2 = null-cal/GATE-V2.md @ 8c175580. Onboarding: ONBOARDING.md.

## Stage 1 (gate v2 lines, verbatim)
```
V K0  screen2 K0: problems 30 | fixed_u 20 (by refusal 3) | new CEu 1 | net 19 (bar 10) | false refusals 0/20 (max 2) | sentinels worse 7 (report only) | U_cov +0.0124 [-0.0303, 0.0564] (min -0.059) | changed 50 | dead changed 0 -> GO
V K1  screen2 K1: problems 21 | fixed_u 17 (by refusal 2) | new CEu 0 | net 17 (bar 9) | false refusals 1/20 (max 4) | sentinels worse 9 (report only) | U_cov -0.0183 [-0.0804, 0.0391] (min -0.071) | changed 41 | dead changed 0 -> GO
E K0  screen2 K0: problems 30 | fixed_u 21 (by refusal 4) | new CEu 0 | net 21 (bar 10) | false refusals 0/20 (max 2) | sentinels worse 3 (report only) | U_cov +0.0116 [-0.0252, 0.0482] (min -0.059) | changed 50 | dead changed 0 -> GO
E K1  screen2 K1: problems 21 | fixed_u 16 (by refusal 1) | new CEu 0 | net 16 (bar 9) | false refusals 1/20 (max 4) | sentinels worse 6 (report only) | U_cov +0.0035 [-0.0565, 0.0568] (min -0.071) | changed 41 | dead changed 0 -> GO
```
| Run | CEu ctl -> cand | declines / warned (cand) | out tokens cand vs ctl (live) | mean totalMs cand vs ctl | Haiku |
|---|---|---|---|---|---|
| V K0 | 30 -> 11 | 1 / 2 | 51.3 vs 41.2 | 3277 vs 2130 (1.54x) | 100 |
| V K1 | 21 -> 4 | 2 / 2 | 53.7 vs 44.0 | 5262 vs 3625 (1.45x) | 82 |
| E K0 | 30 -> 9 | 2 / 2 | 52.3 vs 41.2 | 3297 vs 2130 (1.55x) | 100 |
| E K1 | 21 -> 5 | 1 / 2 | 53.7 vs 44.0 | 7484 vs 3625 (2.07x, slot contention) | 82 |
Sanity (tools/sanity.py): all runs n/n, 0 errors, 0 generation_failed, model.sha256 740185b2 on every trace, 0 reasoning tokens, 0 thought markers. Most fixes are not by refusal (3-4 of 16-21): the model answers correctly more often, it does not just decline more. The control wall times are from different runs (different mini load), so the wall ratio is approximate.
Stage-2 entry (criterion §3): both variants GO on K0; E has the higher K0 net (21 vs 19) -> E runs stage 2. Projected Pixel decode 8.6 >= 8.

## Stage 2 (MAIN n 97, K0, E = engine sampler; stage2/, tools/stage2_verdict.py -> stage2/verdict.json)
| Metric | 1.7B control | Gemma E2B | delta [95 % CI] |
|---|---|---|---|
| U (agg_run) | 0.4055 | 0.4336 | **+0.0281 [+0.0061, +0.0519]** (need >= +0.03 and CI low > 0) |
| CE-unwarned rate | 0.072 | 0.021 | **-0.052** (need <= +0.02) |
| CE (any) count | 27 | 18 | -0.093 [-0.175, -0.010] |
| default-mode U (refused := 0), info | 0.257 | 0.291 | +0.034 [+0.004, +0.067] |
| refused (declined or warned) | 46 | 41 | |
**Verdict: FAIL** (dU 0.0281 < 0.03; the other two clauses pass). 75/97 answers changed, 150 Haiku calls. Wall 1.49x, output tokens 52.9 vs 45.5 on live items.

## Reading
- This is the first model-swap arm that moves the 1.7B's CE-unwarned errors in default mode (-0.05 absolute, 72 % fewer) and lifts U with a CI that excludes 0, but the frozen magnitude bar is missed by 0.002. One seed, Haiku-low judge: the dU point is within noise of the bar either way.
- Not tested here: V on MAIN (its K0 net was 19 vs 21), Q3_K_M, phone speed/PSS (PLE paging), the 4B comparison on the same items.

## Spend and disk
Haiku 5.5-low calls: smoke 20 + screens 364 + stage 2 150 = **534** (cap 700). 0 Opus, 0 paid.
Disk (mini): downloaded only gemma-4-E2B-it-Q4_K_M.gguf (3.11 GB, kept); download paused once while a concurrent download ran, resumed at 29.0 GiB free projected-after; free 27.0 GiB right after the download, 25 GiB at 23:46 (other lab jobs). Nothing else downloaded, so nothing deleted except the scratch dir <runner>/kiln/gemma4-e2b-onb.
