# Model-usage audit, measurement dimension (2026-10-20 ~20:50)

TL;DR: the arithmetic of all 7 screen gates reproduces exactly from raw traces + judgments (independent script).
None of today's NOs comes from a wrong calculation, and the judgment-reuse and selection biases make the screen *lenient*, not strict.
But the screen's target is mis-measured in three ways that matter for the direction of the research:
(1) the CE label counts refusals and "pack not installed" notices as confident errors, so abstention-type levers (B-HONEST, OCC-RAG) can never score;
(2) 4 of the 23/21 control CEs and 4-5 of the 10 sentinels never reach the LLM, so no prompt/sampler/model arm can move them, and the frozen "need 6" rests on a denominator of 27 instead of the reachable 19/17 (under a reachable denominator SHORTCTX and QUOTEFIRST would read GO);
(3) the null "fix" rate from re-sampling alone is about 3 per arm, so the four arms at 4 fixes are indistinguishable from null, and GREEDY's "CI excludes 0" is regression to the mean.
Read-only; 0 model calls, 0 judge calls, 0 paid. Scripts: `measurement-tools/` (regate.py, null.py, refscan.py), run with `python3 -I`.

## Findings

### M1 (high): CE label counts refusals and notices as confident errors; refusal_like regex misses the engine's own refusal strings
- `arms/lp-screens/tools/agg_run.py:30`: `CE=(not d and j["corr"] <= 1.5)`, where `d` = trace `answer.declined`. A refusal that the engine does not flag as declined, or one the model writes itself, is CE whenever Haiku gives correctness <= 1.5.
- `agg_run.py:9` RX matches "i don't have (enough |reliable )?information", not the engine's health refusal "I don't have a reliable offline source on this, so I won't give health advice from memory..." nor "The offline places pack is not installed...". So `refusal_like` = 0 in every aggregate today, including B-HONEST.
- Measured, mini K0 MAIN control (lpctl-K0-main-s42): 7 answers are engine refusal/notice texts. Haiku corr 1.0, 2.5, 1.0, 1.0, 2.0, 3.0, 1.0, so **4 of the 7 are counted CE** = 4 of the 27 MAIN CEs (15 %).
  On both screens all 4 such items are "problems" and CE: st-qa-cooking-se-002 (places notice), -013, -015, st-qa-money-se-004 (health refusal).
- The same refusal text gets correctness 1.0 to 3.0, so the judge has no stable reading of an abstention.
- Consequence: a lever whose mechanism is "abstain when unsure" (B-HONEST's "If you don't know, say so"; OCC-RAG UNANSWERABLE) is scored CE about half the time even when it works. The gate has no outcome "CE turned into an honest refusal".
- Counterfactual on OCCRAG (sidecar routes, 0 calls): if OCC's UNANSWERABLE were kept as a decline instead of falling back to Qwen, the frozen gate reads
  K0 fixed **8** (need 6), sentinels newly declined 0 -> GO; K1 fixed **13**, 1 sentinel newly declined (max 1) -> GO.
  The abstention precision on these CE-enriched screens is 16 of 22 (6/7 K0, 10/15 K1; the K1 false abstentions include lan-cmp-003 at corr 5.0 and four items at 3.0).
  OCC would still fail the stage-2 latency clause (2.0x wall on eligible items) and the +0.03 refusal cap is untested, so this is a re-scope signal, not a reversal.

### M2 (medium): screen denominator includes items no arm can move; sentinels half dead
- `arms/lp-screens/tools/screen_gate.py:24`: `need = math.ceil(0.22 * len(P))` with len(P) = 27 (MacBook-selected problems).
- But in the mini control only 23 (K0) / 21 (K1) of the 27 are CE, and **4 of those never reach the LLM** (sampler temperature absent in the trace, outputTokens 0): st-qa-cooking-se-002 (route places, "places:no-pack"), st-qa-cooking-se-013, -015, st-qa-money-se-004 (route `instant:preview` + `grounding:health-no-source`, detector p 1.000 / 0.953). None of the 7 arms changed any of them (checked: 0 no-LLM item changed in b-honest, greedy, shortctx, quotefirst).
- Reachable CEs = 19 (K0) / 17 (K1). The design intent "22 % of problems fixed" gives need 5 (K0) / **4 (K1)** on reachable CEs. Under that reading SHORTCTX (4 fixed, 0 sentinels worse) and QUOTEFIRST (4 fixed, 0 worse) are GO; B-HONEST and GREEDY (4 of 19) stay NO.
- Sentinels: 4/10 (K0) and 5/10 (K1) are deterministic-layer answers (facts-depth, facts-dates, calculator, detector) and cannot get worse; of the live ones, the cm sentinels sit at corr 2.0-3.5 in the mini control (st-qa-money-se-019 2.0, -005 2.0, -013 1.5 = already CE). st-qa-money-se-002 (3.5 -> 2.5) is the "worse" sentinel in 3 of 3 K0 arms that changed it, i.e. one noisy item uses the whole sentinel allowance.

### M3 (medium): null fix rate is about 3 per arm; "fixed 4" = null; GREEDY's significant CE delta is regression to the mean
- Null estimate (null.py, 0 calls): the unchanged system re-run on the mini vs the MacBook selection run. Of the 27 MacBook-CE problems, text changed on 21 (K0) / 19 (K1); of those changed, 3 / 6 are not CE on the mini (pooled 9/40 = 22 %). Unchanged texts re-judged: 1/14 flips (judge alone).
- Today's arms changed 14-18 of the control-CE problems (B-HONEST 18, GREEDY 16, QUOTEFIRST 16, SHORTCTX 14, VENDORSAMP 11, OCC 3/5) -> expected null fixes about 2.5-4 (lower for doubly-selected items). Observed 4, 4, 4, 4, 1, 2, 3.
- vit-cry-005 is "fixed" in 4 arms and vit-cry-003 in 3, almost always 1.0/1.5 -> 2.0; correctness 2 still means "a wrong claim that matters" (judge-core.mjs RUBRIC). 45 of the control's low items sit exactly at the 1.5/2.0 boundary (pairs (1,2) 22, (2,2) 23), so one order moving one point decides "fixed".
- GREEDY screen CE -0.108 (CI -0.216..-0.027) is bootstrapped over items of a CE-enriched sample; the null alone predicts about -0.08. The CI excluding 0 is not evidence of an effect (QUEUE 19:47 already hedges this).
- Direction: the selection biases (MacBook-selected problems, control judgments reused only for identical text, re-judge only changed text) all push toward spurious fixes, i.e. toward GO. They cannot have produced today's NOs.

### M4 (medium): the screens measure CE in a product mode the 20:24 decision retired
- All screens run LITEDECLINE_OFF=5 (mini_gen.sh:31) = every compact decline released behind the warning line. In the K0 screen control **15 of 23 CEs are warned** answers (B-HONEST 14/21, GREEDY 11/19, OCC 13/21 warned).
- r4to's 20:24 decision (QUEUE) makes "no source -> refuse by default, show-anyway button" the product. In default mode those 15 warned answers become declines; the default-mode CE on the K0 screen is 8 unwarned (B-HONEST 7, GREEDY 8, OCC 8). The levers were judged on the CE the user will no longer see by default.
- Not a bug in a NO, but the next screens should report CE-unwarned (default mode) and CE-warned (show-anyway mode) separately, as the ruler spec does for U-ref / U-noref.

### M5 (medium): Haiku-low CE label never validated against Opus at the 1.7B's CE rate
- HAIKUJUDGE (arms/haikujudge) validated winner agreement (54/57) and documented gap compression (paired delta x0.25). Recomputed from its files: on the two 57-item legs Opus has 2 and 4 CE, Haiku 3 and 3, agreement 2+2 both, 1+1 Haiku-only, 0+2 Opus-only; Haiku correctness is 0.14-0.36 lower on average.
- With 6 Opus CEs in the calibration set, the CE <= 1.5 label (the only stage-1 metric) is unvalidated for a system at 23-28 % CE. L1-PROTOCOL's near-miss rule (Opus re-check within 0.01 of a threshold) has no CE analogue.

### M6 (low): mini job reports DONE on 29/37 generation_failed rows
- `arms/lp-screens/tools/mini_gen.sh:37` writes DONE when rc = 0 and row count matches; errored rows are not checked. The GREEDY first attempt (`greedy/failed-quoting-attempt/*.status`: "end rc=0 rows=37 / DONE") had 29 rows with `generation_failed: Expected property name or '}' in JSON at position 1` and still went to the judge stage. It failed closed later (judge drops errored traces, agg_run.py exits MISSING), so no number was produced, but nothing stops a partial failure earlier.
- Cause verified: `set -a; . $J/env` sources the file in bash, so unquoted `{"temperature":0,...}` loses its quotes; the quoted re-run recorded `sampler.override` = `{"temperature":0,"top_k":1}` on 37/37 traces (and VENDORSAMP `{"top_k":20,"top_p":0.8,"min_p":0,"presence_penalty":0}` on 37/37).

### Cross-dimension leads seen while auditing (not measurement; for the routing/detector auditors)
- Emergency detector fires on non-health questions and forces the health refusal: st-qa-cooking-se-013 "rescue a cast iron pot with burnt-on food" detector p = 1.000, st-qa-cooking-se-015 "thighs juicy, white meat dry" p 0.263 yet `detector:fire` (fires below 0.5; vit-sci-003 also fires at p 0.291), st-qa-money-se-004 "PayPal stranger offer" p 0.953 (reasonCodes `detector:fire`, `grounding:health-no-source`).
- st-qa-cooking-se-002 (botulism in vegetables in oil) is routed to `task:places` ("places pack is not installed").
- These 4 items are 15 % of the MAIN CE count and no answer-model arm can touch them.

## Recomputed gates (regate.py, independent of agg_run.py / screen_gate.py; same result on all 7)
| Run | ctl CE on problems | fixed | sentinels worse | changed / 37 | verdict |
|---|---|---|---|---|---|
| b-honest K0 | 23 | 4 (lan-cmp-005, st-qa-money-se-009, vit-cry-003, vit-cry-005) | 1 (st-qa-money-se-002) | 26 | NO-GO |
| greedy K0 | 23 | 4 (vit-cry-003, vit-cry-005, vit-sci-002, vit-trv-003) | 1 (st-qa-money-se-002) | 24 | NO-GO |
| vendorsamp K0 | 23 | 1 (st-qa-money-se-007) | 1 (st-qa-money-se-002) | 15 | NO-GO |
| occrag K0 | 23 | 2 | 0 | 3 | NO-GO |
| shortctx K1 | 21 | 4 (lan-rsn-003, st-qa-cooking-se-020, trv-004, vit-cry-005) | 0 | 22 | NO-GO |
| quotefirst K1 | 21 | 4 (st-qa-cooking-se-008, -020, trv-004, vit-cry-005) | 0 | 24 | NO-GO |
| occrag K1 | 21 | 3 | 0 | 7 | NO-GO |

## Checked and OK
- Gate arithmetic: all 7 gate.txt outputs reproduced from traces + judgments.
- Judge provenance: 584 rows across control + 6 arms, all ok, judgeModel claude-haiku-5-5, judgeVersion judge.v1-low; every judged id has exactly one row per order (boarA, boarB).
- Order effect: |A - B| correctness = 0 on 117/171, 1 on 53, 2 on 1 (control).
- Judgment reuse: only byte-identical texts reuse control rows (agg_run.py:27; run_arm.sh judges only changed ids); the mini is deterministic (37/37 identical across runs per SCREENS.md, 97/97 in LOGPROB).
- Sampler overrides reached the server: `sampler.override` in versions on 37/37 traces for GREEDY and VENDORSAMP; samplerFor() (be/server.ts:27) spreads the override after the defaults; trace temperature 0 on the 29 LLM items for GREEDY.
- B-HONEST patch reached the model: persona sha 28cf39aa vs control 5e0de1c7 on all 37 traces (but `engine.patch.sha256` stays 0fba26b8 for every arm: it does not identify the candidate patch; run_arm's status line carries the patch sha instead).
- LOGPROB: headline AUC (all 97) includes 22 unflagged no-LLM items; on the 75 generated items AUC is 0.45, so the inclusion did not hide a signal (verdict NO holds).
- References: v0.1 refs median 262 words vs control answers 40 (x6.5); self-test gold 78-82 words (x1.7-1.9). Same for every arm, so not a cause of a paired NO; the length gap matters for completeness/U, not for the correctness-based CE.
- judge-core blind() strips citations/links only; the CMP30OFF warning line reaches the judge unchanged in both arms of every pair (no asymmetry).

## Cheapest tests
1. CE redefinition, 0 calls: re-run screen_gate.py with CE = not declined AND not refusal_like AND corr <= 1.5, with RX extended to the engine strings ("reliable offline source", "pack is not installed", "Not enough information", "I didn't find this"), and need computed on reachable mini-control CEs. Report both verdicts beside the frozen one (no rescue of a frozen NO; label as re-analysis).
2. Null arm, about 50 Haiku calls: run a comment-only or whitespace-in-persona patch through run_arm.sh K0 screen (changes the sample, not the meaning) to measure the real null "fixed" count; calibrate the stage-1 bar as null + margin.
3. OCC abstain-as-decline, 0 generation: the OCC sidecar already holds the abstentions; score a variant where `occ-abstain-fallback-qwen` = declined, report CE, decline rate and U on the screens; only if it looks useful, a stage-2 MAIN run (latency clause stays).
4. Haiku vs Opus CE label, about 80 Opus calls: re-judge the 23 K0 control CEs + the 16 GREEDY changed problem answers with Opus judge.v1, both orders; report CE agreement.
5. SHORTCTX / QUOTEFIRST stage 2 (MAIN 97) if the coordinator accepts the reachable-denominator reading: about 150 Haiku calls each (changed answers only).

UNKNOWN: whether Haiku scores a model-written "I don't know" differently from the engine's fixed refusal text (no model-written refusal exists in today's judged traces: refscan.py found 0 outside the warning/notice texts).
