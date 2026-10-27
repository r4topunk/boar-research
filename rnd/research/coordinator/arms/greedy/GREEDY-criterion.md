# GREEDY criterion (frozen 2026-10-20 before any candidate generation)

## Question
On Qwen3-1.7B with the compact declines released behind the warning line (LITEPACKS system, pack set K0 claim kit), does greedy decoding make the model produce fewer confident errors (CE) than the engine's current sampling?
(GRILL-2026-10-20 Q6, Q13.)

## Current sampling (mini tree be-0cfd4a77-cut7-litepacks, be/server.ts samplerFor, server backend): temperature 0.7 (health items 0), top_k 40, top_p 0.95, min_p 0.05, seed 42.

## Candidate (arms/greedy/greedy.env, sha256 in greedy.env.sha256)
Env override, no source change: BOAR_SAMPLER_JSON={"temperature":0,"top_k":1} (be/server.ts samplerOverride, spread last, so it wins over the per-item temperature). Result on the 1.7B fast/compact path: temperature 0, top_k 1 (top_p 0.95 and min_p 0.05 stay, inert under top_k 1), seed 42. Everything else identical (prompts, retrieval, packs, warning line, release logic).
Control = the MINI controls of arms/lp-screens/control (lpctl-K0-screen-s42, lpctl-K0-main-s42).

## Sets (dev only)
- Stage 1 = arms/lp-screens/screen-K0.ids (27 problems + 10 sentinels).
- Stage 2 = arms/lp-screens/main-97.ids (MAIN n 97).

## Judge
Haiku 5.5-low judge.v1-low, N = 4 shards, both orders, via tools/run_arm.sh (identical answers reuse control judgments). 0 Opus, 0 paid.

## Budget
calls_cap: Haiku 500

## Decision rule (stated before running)
- Stage 1: the frozen gate printed by tools/screen_gate.py: GO iff fixed >= 6 AND sentinels worse <= 1 (worse = correctness drop >= 1.0, newly declined / refusal-like, or newly CE). NO-GO ends the arm.
- Stage 2 (only on GO; MAIN n 97 vs the cached mini K0 MAIN control; paired item bootstrap B 2000 seed 11; arms/greedy/tools/verdict.py):
  PASS iff (1) CE rate change <= -0.05 with paired CI high < 0 (CE rate = CE count / non-declined answers), AND (2) decline + refusal-like rate change <= +0.03, AND (3) U change >= -0.01 (point estimate). Otherwise NO.
- Also reported: Q, warned rate, CE split warned/unwarned. Judge-noise caveat per SCREENS.md; no re-run to rescue a NO.
