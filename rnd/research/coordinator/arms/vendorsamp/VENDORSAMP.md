# VENDORSAMP (K0, Qwen3-1.7B, 2026-10-20): stage 1 NO-GO, stage 2 not run

TL;DR: Qwen's non-thinking sampling (top_k 20, top_p 0.8, min_p 0, presence_penalty 0; T 0.7 unchanged, health T 0) fixes 1 of 23 control CEs on the screen (need 6), with 1 sentinel worse (max 1). Vendor sampling is a near no-op: 22 of 37 answers are byte-identical to the control, CE 22 vs 23. Arm ends.

## Card values used (Qwen/Qwen3-1.7B, Best Practices, fetched 2026-10-20)
"For non-thinking mode (enable_thinking=False), we suggest using Temperature=0.7, TopP=0.8, TopK=20, and MinP=0." Presence penalty: "adjust the presence_penalty parameter between 0 and 2 to reduce endless repetitions" (no single value for this mode) -> 0.
Env (quoted): BOAR_SAMPLER_JSON='{"top_k":20,"top_p":0.8,"min_p":0,"presence_penalty":0}', sha256 57ff1785...; temperature omitted on purpose (card 0.7 = engine default, keeps health at T 0).
Criterion sha256 666dc802..., committed with the env as 95e7cc4b before generation.

## Gate (verbatim)
```
screen K0: problems 27 (CE in mini control 23) | fixed 1 (need >= 6) | still CE 22 | sentinels worse 1/10 (max 1) | changed answers 15/37 -> NO-GO
  fixed st-qa-money-se-007 1.5 -> 2.0
  sentinel worse st-qa-money-se-002 corr 3.5->2.5
```
Screen deltas vs control: CE -0.027 (-0.081...0.000; count 22 vs 23), U -0.006 (-0.017...+0.004), decline 0, refusal_like 0, warned 16. Repetition (4-gram occurring >= 4 times): 0 candidate vs 0 control. generation_failed 0/37. Stage 2: not run (NO-GO).

## Examples (control -> vendor)
1. st-qa-money-se-007 (1.5 -> 2.0, the one fix): same "Not found... may be wrong" opening, credit-union regulation claim; the invented second sentence changes (assess applicants' finances -> accurate records) and is still unsupported. A judge-noise-level fix.
2. st-qa-money-se-002 sentinel (3.5 -> 2.5): control ends "You're still responsible for paying the full amount by the due date"; vendor drops it for "keep your statement up to date", losing the correct point.
3. 22 of 37 answers are byte-identical to the control (top_k/top_p tightening rarely changes the argmax path at T 0.7 with min_p 0.05 already pruning the tail).

## Run
Screen vendorsamp-K0-screen-s42 on the mini (gen slot), 15 changed answers judged, 30 Haiku calls, 0 Opus, 0 paid. Deviations: none (env quoted correctly first time).
