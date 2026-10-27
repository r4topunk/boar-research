# NULLCAL criterion (frozen 2026-10-20 before any candidate generation)

## Question
How many "fixes" does the K0 stage-1 screen record when the lever is a null (no change in meaning)? The screen's target and noise floor were never measured:
MAINT audit findings M2, M3, RT-3, N1, M4 (research-2026-10-20/model-usage/measurement.md, refute-1.md, refute-2.md) put the null at about 3 fixes per arm against a bar of 6.
This arm is MEASUREMENT ONLY. It decides nothing about any lever; it calibrates GATE v2 (arms/null-cal/GATE-V2.md, written after the numbers, committed before it is cited).

## Arms (K0 screen = arms/lp-screens/screen-K0.ids, 27 problems + 10 sentinels, sha256 b6ff7da7...; Qwen3-1.7B, LITEPACKS system, LITEDECLINE_OFF=5, mini)
- null-ws: arms/null-cal/null-ws.patch (sha256 in null-ws.patch.sha256). Whitespace-only change of the succinct persona text in src/constants/personalities.ts (double spaces after 7 commas/periods/words). Changes the prompt bytes (persona.sha256 must differ from the control's 5e0de1c7 in the traces) and the tokens; no change in meaning. Seed 42.
- null-s43: arms/null-cal/null-s43.patch (sha256 in null-s43.patch.sha256). be/server.ts samplerFor sends `seed: 43` instead of the request seed (42). The unchanged system otherwise (BOAR_SAMPLER_JSON does not allow `seed`, hence a one-token patch; env quoting lesson of arms/greedy does not apply, no env file).
- Control = the mini control arms/lp-screens/control (lpctl-K0-screen-s42, deterministic: 37/37 byte-identical across runs).
- Both via arms/lp-screens/tools/run_arm.sh <arm> K0 screen <patch> (Haiku 5.5-low judge.v1-low, N = 4, both orders; identical answers reuse control judgments), outputs under arms/null-cal/<arm>/ (arm dirs are symlinked during the run and removed after; recorded paths in aggregates still read arms/<arm>/).

## Measured and reported for each null (tools/null_report.py, frozen with this file; 0 LLM)
- v1 gate verbatim (tools/screen_gate.py output): fixed, sentinels worse, verdict.
- live(i) = control trace generated tokens > 0; the 4 K0 problems and 4 K0 sentinels answered by routing/deterministic layers are dead.
- CE = not declined and correctness <= 1.5 (agg_run.py); CEu = CE and not warned (the product default refuses warned memory answers).
- fixed_v1 (23 control CEs), fixed_reach (live control CEs, 19), fixed_u (live problems that are CEu in the control and not in the candidate), new_CEu (live items not CEu in the control and CEu in the candidate), CEu count control vs candidate, sentinels worse over all 10 and over the live ones, changed answers (live and dead; dead changed must be 0).
- Also reported: U, Q, CE, decline deltas from agg_run.py.

## Decision rule
None (measurement). Not a lever test: no GO/NO-GO is drawn from either null. The two counts are inputs to GATE v2 together with the judge test-retest numbers already in arms/lp-screens/SCREENS.md (identical texts re-judged: equal CE on 35/37; equal correctness on 24/37).
Sanity conditions (the run is void and repeated once if violated): traces 37/37, 0 error rows, 0 changed answers on dead items, null-ws persona.sha256 differs from the control's on 37/37, null-s43 text differs from the control on at least 10 live items.

## Budget
calls_cap: Haiku 300 (both arms together; the expected spend is <= 2 x 74)
