# GRANITE4-1B criterion (frozen 2026-10-21 before any screen generation)

Arm: model swap Qwen3-1.7B Q4_K_M -> ibm-granite/granite-4.0-1b (official ibm-granite/granite-4.0-1b-GGUF @ b27c2fe3, Q4_K_M, sha256 22ec0f9c...d7f1, Apache-2.0; GGUF arch `granite`, 40 attention layers, no Mamba) on the LITEPACKS mini tree; everything else identical (compact tier with catalog sizeBytes kept at 1107409472, engine prompt unchanged with sources inside the user message (the template's `documents` slot is not used), declines, retrieval, seed 42, --reasoning off; the template has no thinking mode, see ONBOARDING.md).
Gate: **GATE v2**, arms/null-cal/GATE-V2.md (sha256 34ada53f1a9ab4ae31d971b6989eba3b4b979de8e05516fa687aad238a582982) + tools/screen_gate_v2.py (sha256 fa726fc0ac0b2380b528a5447b8058aec125a39b516eaec4f91df3173275729b). PARAMS: K0 net >= 10, false refusals <= 2, U_cov delta >= -0.059; K1 net >= 9, false refusals <= 4, U_cov delta >= -0.071.

## 1. Candidates (both screened; the 5-item smoke does not separate them)
| Variant | Patch | sha256 |
|---|---|---|
| E (engine sampling 0.7/40/0.95/0.05, health T 0; model only) | granite4-1b-engsamp.patch | see granite4-1b-engsamp.patch.sha256 |
| G (greedy: BOAR_SAMPLER_JSON {"temperature":0,"top_k":1}; the card names no sampler and its examples use the default generation_config = greedy) | granite4-1b-greedy.patch | see granite4-1b-greedy.patch.sha256 |
Arm names: `granite4-1b-eng` (E), `granite4-1b-grd` (G). Output root arms/granite4-1b/screens/ (OUT_BASE).

## 2. Stage 1 (screen)
For each variant and K in {K0, K1}: `OUT_BASE=arms/granite4-1b/screens SCREEN_JSON=null-cal/pool/screen2-<K>.json CRITERION=<this file> bash null-cal/tools/run_pool.sh <arm> <K> null-cal/pool/screen2-<K>.ids <patch>`.
Verdict per run = the printed screen_gate_v2.py line (GO / NO-GO), unchanged. Reported per run (tools/citations.py, 0 LLM): CE-unwarned ctl -> cand, false refusals, U_cov delta, **citation compliance** (answers with sources shown that carry `cited` / an `[n]` marker, cand vs control; control-cited answers that lose their citation; route codes compact-decline-released-uncited-with-sources / -all-citations-removed), mean/median output tokens, wall ratio vs the control traces on the same items.
Sanity (run void, repeated once if violated): traces n/n, 0 error rows, 0 generation_failed, every trace's versions["model.sha256"] = 22ec0f9c..., 0 reasoning tokens, 0 role/think tokens (`<|start_of_role|>`, `<|end_of_role|>`, `<|end_of_text|>`, `<think>`, `<tool_call>`) in answer text; temperature 0 on every G item, 0.7 (or 0 health) on E.

## 3. Stage-2 entry
Stage 2 runs iff a variant reads **GO on K0** under gate v2 (MAIN is the K0 pack set; K1 is reported, not gating). Speed is not a blocker here: stage 0 mini tg128 ratio Granite/1.7B = 1.007 (1.028, 0.987 interleaved) -> projected Pixel 8a decode 14 x 1.007 = 14.1 tok/s (12.1-16.1).
If both variants are GO on K0, only the one with the higher K0 net runs stage 2 (tie: E).

## 4. Stage 2 (MAIN n 97, K0)
`CRITERION=<this file> bash lp-screens/tools/run_arm.sh <arm> K0 main <patch>` vs the mini control lpctl-K0-main-s42 (U 0.4055).
**PASS iff dU >= +0.03 and its paired bootstrap CI low > 0 and CE-unwarned rate change <= +0.02**, computed by tools/stage2_verdict.py (frozen with this file; identical logic to gemma4-e2b/tools/stage2_verdict.py; U = agg_run.py U; CEu by null-cal/tools/labels.py; B 2000 seed 11). Default-mode U (refused := 0) reported, not gating.

## 5. After a NO
Delete granite-4.0-1b-Q4_K_M.gguf on the mini after logging its recipe line in rnd/kiln/MODELS.md and the deletion in rnd/kiln/DISK-LOG.md.

## Budget
calls_cap: Haiku 700 (4 screens <= 2 x 182 = 364 + stage 2 <= 194 + slack). Spent before this freeze: onboarding smoke <= 20. 0 Opus, 0 paid.
