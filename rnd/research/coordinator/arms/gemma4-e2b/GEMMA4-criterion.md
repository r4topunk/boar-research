# GEMMA4-E2B criterion (frozen 2026-10-20 before any screen generation)

Arm: model swap Qwen3-1.7B Q4_K_M -> google/gemma-4-E2B-it (unsloth/gemma-4-E2B-it-GGUF @ 0314792d, Q4_K_M, sha256 740185b2...4b8b, Apache-2.0) on the LITEPACKS mini tree; everything else identical (compact tier, prompts, declines, retrieval, seed 42, --reasoning off, thinking off: no `<|think|>` in any render, see ONBOARDING.md).
Gate: **GATE v2**, arms/null-cal/GATE-V2.md (sha256 34ada53f1a9ab4ae31d971b6989eba3b4b979de8e05516fa687aad238a582982) + tools/screen_gate_v2.py (sha256 fa726fc0ac0b2380b528a5447b8058aec125a39b516eaec4f91df3173275729b), rnd commit 8c175580. PARAMS: K0 net >= 10, false refusals <= 2, U_cov delta >= -0.059; K1 net >= 9, false refusals <= 4, U_cov delta >= -0.071.

## 1. Candidates (both screened; the smoke did not separate them: CE 2/5 vs 3/5, median answer 36 vs 39 tokens)
| Variant | Patch | sha256 |
|---|---|---|
| V (vendor sampling: T 1.0, top_p 0.95, top_k 64, min_p 0; health T 0 kept) | gemma4-e2b.patch | 9917f1b7663fe55784b112cf14ee44c30c3f11b709dcbc05c0b8b58a521e64ce |
| E (engine sampling 0.7/40/0.95/0.05, model only) | gemma4-e2b-engsamp.patch | 095ca9d71b6f8814bf8e77e796531936cfe9f8f85559bdde5d8ba26b4fc2b248 |
Arm names: `gemma4-e2b` (V), `gemma4-e2b-eng` (E). Output root arms/gemma4-e2b/screens/ (OUT_BASE).

## 2. Stage 1 (screen)
For each variant and K in {K0, K1}: `OUT_BASE=arms/gemma4-e2b/screens SCREEN_JSON=null-cal/pool/screen2-<K>.json CRITERION=<this file> bash null-cal/tools/run_pool.sh <arm> <K> null-cal/pool/screen2-<K>.ids <patch>`.
Verdict per run = the printed screen_gate_v2.py line (GO / NO-GO), unchanged. Reported per run: gate line, CE-unwarned count (ceu_cand vs ceu_ctl), false refusals, U_cov delta, mean output tokens and mean totalMs vs the control trace on the same items.
Sanity (run void, repeated once if violated): traces n/n, 0 error rows, 0 generation_failed, every trace's versions["model.sha256"] = 740185b2..., 0 thought markers (`<|channel>`, `<channel|>`, `<|think|>`) in answer text.

## 3. Stage-2 entry
Stage 2 runs iff (a) a variant reads **GO on K0** under gate v2 (MAIN is the K0 pack set; K1 is reported, not gating) and (b) projected Pixel 8a decode >= 8 tok/s, where projection = 14 tok/s (midpoint of the measured 1.7B Pixel rate 12-16) x the stage-0 mini tg128 ratio Gemma/1.7B. Stage 0 measured ratio 0.616 (0.625, 0.608 interleaved) -> **8.6 tok/s (range 7.4-9.9)**, so (b) holds.
If both variants are GO on K0, only the one with the higher K0 net runs stage 2 (tie: V).

## 4. Stage 2 (MAIN n 97, K0)
`CRITERION=<this file> bash lp-screens/tools/run_arm.sh <arm> K0 main <patch>` vs the mini control lpctl-K0-main-s42 (U 0.4055).
**PASS iff dU >= +0.03 and its paired bootstrap CI low > 0 and CE-unwarned rate change <= +0.02**, computed by tools/stage2_verdict.py (frozen with this file; U = agg_run.py U; CEu by null-cal/tools/labels.py; B 2000 seed 11). Default-mode U (refused := 0) reported, not gating.

## Budget
calls_cap: Haiku 700 (4 screens <= 2 x 182 = 364 + stage 2 <= 194 + slack). Spent before this freeze: onboarding smoke 20. 0 Opus, 0 paid.
