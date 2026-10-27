# VENDORSAMP criterion (frozen 2026-10-20 before any candidate generation)

## Question
Does Qwen's own recommended sampling for Qwen3 in NON-thinking mode make Qwen3-1.7B (LITEPACKS system, pack set K0 claim kit, compact declines released behind the warning line) produce fewer confident errors (CE) than the engine's current sampling?

## Vendor card text used (Qwen/Qwen3-1.7B, Hugging Face, Best Practices, fetched 2026-10-20)
- "For non-thinking mode (`enable_thinking=False`), we suggest using `Temperature=0.7`, `TopP=0.8`, `TopK=20`, and `MinP=0`."
- "you can adjust the `presence_penalty` parameter between 0 and 2 to reduce endless repetitions" (higher values "may occasionally result in language mixing and a slight decrease in model performance"). The card gives no single presence_penalty for non-thinking mode (the 1.5 note is for significant endless repetitions), so presence_penalty = 0 is used.

## Current sampling (mini tree be-0cfd4a77-cut7-litepacks, be/server.ts samplerFor): temperature 0.7 (health items 0), top_k 40, top_p 0.95, min_p 0.05, seed 42.

## Candidate V (arms/vendorsamp/vendorsamp.env, sha256 in vendorsamp.env.sha256)
BOAR_SAMPLER_JSON='{"top_k":20,"top_p":0.8,"min_p":0,"presence_penalty":0}' (quoted; samplerOverride spreads last). Temperature is deliberately NOT in the override: the card's 0.7 equals the engine default for non-health items, and omitting it keeps the engine's health-item temperature 0 (as GREEDY found, the override would otherwise win over per-item temperature). Effective: non-health T 0.7 / top_k 20 / top_p 0.8 / min_p 0 / presence_penalty 0; health T 0. Everything else identical.
Control = the MINI controls of arms/lp-screens/control (lpctl-K0-screen-s42, lpctl-K0-main-s42).

## Sets (dev only)
- Stage 1 = arms/lp-screens/screen-K0.ids (27 problems + 10 sentinels).
- Stage 2 = arms/lp-screens/main-97.ids (MAIN n 97).

## Judge
Haiku 5.5-low judge.v1-low, N = 4 shards, both orders, via tools/run_arm.sh (identical answers reuse control judgments). 0 Opus, 0 paid.

## Budget
calls_cap: Haiku 500

## Decision rule (stated before running)
- Stage 1: the gate printed by tools/screen_gate.py: GO iff fixed >= 6 AND sentinels worse <= 1 (worse = correctness drop >= 1.0, newly declined / refusal-like, or newly CE). NO-GO ends the arm.
- Stage 2 (only on GO; MAIN n 97 vs the cached mini K0 MAIN control; paired item bootstrap B 2000 seed 11; arms/vendorsamp/tools/verdict.py, copy of greedy's):
  PASS iff (1) CE rate change <= -0.05 with paired CI high < 0 (CE rate = CE count / non-declined answers), AND (2) decline + refusal-like rate change <= +0.03, AND (3) U change >= -0.01 (point estimate). Otherwise NO.
- Also reported on the screen: CE change with CI, U change, repetition (answers with a repeated n-gram loop: any 4-gram of words occurring >= 4 times) candidate vs control. Judge-noise caveat per SCREENS.md; no re-run to rescue a NO.
