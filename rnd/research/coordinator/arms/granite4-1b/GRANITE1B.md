# GRANITE4-1B (2026-10-21): stage 1 GO on both K0 screens, NO-GO on both K1 screens; stage 2 FAIL (dU +0.000)

TL;DR: ibm-granite/granite-4.0-1b Q4_K_M as a straight swap for Qwen3-1.7B passes GATE v2 on K0 with both samplers (net 14, bar 10; 1/20 false refusals) and fails on K1 (false refusals 5-7/20 vs max 4, U_cov below the floor). Every false refusal on every screen is a citation drop: the model omits the [n] marker on 29-53 % of answers the 1.7B cited, and the engine shows those behind the warning line. Per criterion §3 the K0 nets tie (14 = 14) -> E (engine sampler) ran stage 2 on MAIN 97 K0: **dU +0.0003 (CI -0.019...+0.020), CE-unwarned 7.2 -> 8.2 % -> FAIL** (needs dU >= +0.03). Granite 1B is equal to the 1.7B on MAIN, not better. Final verdict: NO on every arm; GGUF deleted (class A).
Criterion GRANITE1B-criterion.md (sha ed62c89a..., committed d53b9795 before any screen generation); gate v2 = null-cal/GATE-V2.md + screen_gate_v2.py (shas in the criterion). Judge Haiku 5.5-low, N 4, both orders.

## Onboarding (onboarding/)
- GGUF official ibm-granite/granite-4.0-1b-GGUF Q4_K_M, sha 22ec0f9c...d7f1, Apache-2.0, arch `granite` (40 attention layers, no Mamba); llama.cpp b11010 loads it.
- Template: GGUF-embedded == HF chat template (template_check.out, all kwargs modes); no thinking mode (no `<think>`); engine prompt unchanged, sources stay inside the user message (the template's `documents` slot is not used, so the IBM documents system message never renders).
- Speed (mini llama-bench, 2 interleaved rounds): tg128 62.8 / 59.1 vs 1.7B 61.1 / 59.9 tok/s -> ratio 1.007 -> projected Pixel 8a decode 14.1 tok/s (12.1-16.1); pp512 228.9 / 228.2 vs 265.4 / 256.3 (0.88x prefill).
- Smoke: 5 K0 items, E judged (10 Haiku calls); the G smoke judge failed with 0 ok rows (preflight/session, <= 8 calls attempted); both smokes generated cleanly.

## Stage 1 (gate v2 lines, verbatim)
```
E K0  screen2 K0: problems 30 | fixed_u 15 (by refusal 8) | new CEu 1 | net 14 (bar 10) | false refusals 1/20 (max 2) | sentinels worse 7 (report only) | U_cov -0.0567 [-0.1004, -0.0166] (min -0.059) | changed 50 | dead changed 0 -> GO
E K1  screen2 K1: problems 21 | fixed_u 13 (by refusal 4) | new CEu 2 | net 11 (bar 9) | false refusals 7/20 (max 4) | sentinels worse 3 (report only) | U_cov -0.1310 [-0.2258, -0.0437] (min -0.071) | changed 41 | dead changed 0 -> NO-GO
G K0  screen2 K0: problems 30 | fixed_u 14 (by refusal 6) | new CEu 0 | net 14 (bar 10) | false refusals 1/20 (max 2) | sentinels worse 4 (report only) | U_cov -0.0298 [-0.0729, 0.0081] (min -0.059) | changed 50 | dead changed 0 -> GO
G K1  screen2 K1: problems 21 | fixed_u 9 (by refusal 0) | new CEu 1 | net 8 (bar 9) | false refusals 5/20 (max 4) | sentinels worse 6 (report only) | U_cov -0.0786 [-0.1542, -0.0104] (min -0.071) | changed 41 | dead changed 0 -> NO-GO
```
E K0 passes U_cov by 0.002 (-0.0567 vs -0.059).

## Diagnostics (tools/citations.py, 0 LLM; screens/*/aggregates/*.cite.json)
| Run | CEu ctl -> cand | answers with sources | cited ctl -> cand | ctl-cited lost (= cite drops = warned) | false refusals that are cite drops | out tokens mean (med) cand vs ctl | wall ratio | Haiku |
|---|---|---|---|---|---|---|---|---|
| E K0 | 30 -> 16 | 17 | 17 -> 8 (47 %) | 9 | 1/1 | 37.5 (35.5) vs 41.2 (41.5) | 0.93 | 100 |
| E K1 | 21 -> 10 | 28 | 28 -> 17 (61 %) | 11 | 7/7 | 37.1 (37) vs 44.0 (44) | 0.98 | 82 |
| G K0 | 30 -> 16 | 17 | 17 -> 10 (59 %) | 7 | 1/1 | 39.3 (38.5) vs 41.2 (41.5) | 0.94 | 100 |
| G K1 | 21 -> 13 | 28 | 28 -> 23 (82 %) | 5 | 5/5 | 38.7 (38) vs 44.0 (44) | 0.98 | 82 |
- Sanity (criterion §2): all runs n/n, 0 errors, 0 generation_failed, model.sha256 22ec0f9c on every trace, 0 reasoning tokens, 0 role/think token leaks; temperature 0.7 on every E item (no health-routed items in these screens), 0 on every G item. No run void.
- Warned share = cite drops only (0 declines either side): E 9/50 and 11/41, G 7/50 and 5/41 (control 0).
- Part of the K0 net comes from those warnings (fixed by refusal 8 E / 6 G of 15 / 14): the citation drops land on wrong answers more often than on right ones, but on K1 they hit 5-7 right answers.
- Same failure family as MINISTRAL-3-3B and FOTAPOL (dropped [n] -> warning), milder; greedy keeps more citations than the engine sampler.
- Wall equal to the 1.7B (0.93-0.98x; answers ~10 % shorter).

## Stage 2 (MAIN n 97, K0, E = engine sampler)
Entry (criterion §3): both variants GO on K0, nets tie 14 = 14 -> E. Launched 02:21 (lp-screens/tools/run_arm.sh granite4-1b-eng K0 main granite4-1b-engsamp.patch, CRITERION=this criterion; log screens/logs/stage2-main.log; outputs arms/granite4-1b-eng/ moved to stage2/).
Generation 02:27-02:31 (after 6 min in the slot queue), judged 02:31-02:34.
| Metric | 1.7B control | Granite 1B (E) | delta [95 % CI] |
|---|---|---|---|
| U (agg_run) | 0.4055 | 0.4058 | **+0.0003 [-0.0194, +0.0203]** (need >= +0.03 and CI low > 0) |
| CE-unwarned rate | 0.072 | 0.082 | **+0.010** (need <= +0.02; passes) |
| CE (any) count | 27 | 28 | +0.010 [-0.072, +0.093] |
| default-mode U (refused := 0), info | 0.257 | 0.261 | +0.004 [-0.024, +0.033] |
| refused (declined or warned) | 46 | 46 | |
**Verdict: FAIL** (stage2/verdict.json; dU and CI clauses fail, CEu clause passes). 75/97 answers changed, 150 Haiku calls.
Diagnostics (stage2/aggregates/*.cite.json): sanity clean (97/97, 0 errors, model sha on every trace, 0 reasoning, 0 leaks; 0.7 on live items, 22 items not generated by either arm); cited answers 17 -> 17 of 32 with sources (6 control citations lost, 6 gained), warned 39 -> 39; out tokens 38.5 (med 36) vs 45.5 (47); wall 0.97x.

## Reading
- Granite 4.0 1B is a speed-neutral, quality-neutral swap for Qwen3-1.7B on MAIN: same U, same CE count, same refusals, ~15 % shorter answers. The K0 screen GO came from the screen's problem-rich items (fixed by refusal 6-8 of 14-15) and did not carry to MAIN.
- Its main defect is [n] citation compliance on dense multi-source contexts (K1: 18-39 % of control citations lost, all false refusals are citation drops); on MAIN it is a wash.
- The GGUF is only 0.08 GB smaller than the 1.7B Q4_K_M (1.02 vs 1.11 GB) and decode is equal, so it offers no footprint or speed lever either. Not tested: documents-slot prompting (criterion kept the engine prompt), phone speed.

## Spend and disk
Haiku 5.5-low calls: smoke 10 (+ <= 8 attempted, 0 ok) + screens 364 + stage 2 150 = **524** (cap 700). 0 Opus, 0 paid.
Disk (criterion §5, DISK-POLICY class A): granite-4.0-1b-Q4_K_M.gguf (1.02 GB, sha verified) deleted from the mini at 02:36 with its lite/SHA256SUMS line after the MODELS.md recipe row and a DISK-LOG line; free 29 -> 30 GiB. Mini job dirs for the 5 granite runs keep traces only (trees removed by run_arm/run_pool).
