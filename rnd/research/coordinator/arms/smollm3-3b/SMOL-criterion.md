# SMOLLM3-3B criterion (frozen 2026-10-21 before any screen generation)

Arm: model swap Qwen3-1.7B Q4_K_M -> HuggingFaceTB/SmolLM3-3B @ a07cc9a0 (Apache-2.0) as bartowski/HuggingFaceTB_SmolLM3-3B-GGUF @ 86b3536e, Q4_K_M, sha256 519732558d5fa7420ab058e1b776dcfe73da78013c2fe59c7ca43c325ef89132, on the LITEPACKS mini tree. Everything else identical: compact tier (catalog sizeBytes kept at the 1.7B's 1107409472), prompts, declines, retrieval, seed 42, `--reasoning off`. Thinking off: with `--reasoning off` the embedded template (byte-identical to the HF chat_template.jinja) renders `Reasoning Mode: /no_think` and the empty `<think>\n\n</think>\n` generation prompt (ONBOARDING.md (1)). The engine prompt is NOT changed in this arm (citation instruction as for the 1.7B).
Gate: **GATE v2**, arms/null-cal/GATE-V2.md (sha256 34ada53f1a9ab4ae31d971b6989eba3b4b979de8e05516fa687aad238a582982) + tools/screen_gate_v2.py (sha256 fa726fc0ac0b2380b528a5447b8058aec125a39b516eaec4f91df3173275729b), rnd commit 8c175580. PARAMS: K0 net >= 10, false refusals <= 2, U_cov delta >= -0.059; K1 net >= 9, false refusals <= 4, U_cov delta >= -0.071.

## 1. Candidates (both screened; the 5-item smoke does not separate them)
| Variant | Patch | sha256 |
|---|---|---|
| V (vendor sampling: T 0.6, top_p 0.95, top_k 0, min_p 0; health T 0 kept) | smollm3-3b.patch | c623338f0301f195e710fc1a47605045778a12d8056d35e2a5f1cc011cf25fa5 |
| E (engine sampling 0.7/40/0.95/0.05, model only) | smollm3-3b-engsamp.patch | 0fae1ba0a046e9d3dbc74d269a00ed37b62ef12e7e28f4396525a4aa785bafd9 |
Arm names: `smollm3-3b` (V), `smollm3-3b-eng` (E). Output root arms/smollm3-3b/screens/ (OUT_BASE). Launcher: tools/launch_screens.sh.

## 2. Stage 1 (screen)
For each variant and K in {K0, K1}: `OUT_BASE=arms/smollm3-3b/screens SCREEN_JSON=null-cal/pool/screen2-<K>.json CRITERION=<this file> bash null-cal/tools/run_pool.sh <arm> <K> null-cal/pool/screen2-<K>.ids <patch>`.
Verdict per run = the printed screen_gate_v2.py line (GO / NO-GO), unchanged.
Reported per run (tools/extras.py, 0 LLM): gate line, CE-unwarned ctl -> cand, false refusals, U_cov delta, **citation compliance** (control answers with >= 1 citation that the candidate also cites; candidate rows carrying `compact-decline-released-uncited-with-sources` / `-all-citations-removed`), warned and declined counts, answer tokens (median/mean vs control, live items), mean totalMs vs the control trace on the same items.
Sanity (run void, repeated once if violated): traces n/n, 0 error rows, 0 generation_failed, every trace's versions["model.sha256"] = 51973255..., 0 rows with reasoningTokens > 0, 0 `<think>` / `</think>` in answer text, sampler temperature as specified (V 0.6, E 0.7; health 0).

## 3. Stage-2 entry
Stage 2 runs iff (a) a variant reads **GO on K0** under gate v2 (MAIN is the K0 pack set; K1 is reported, not gating) and (b) projected Pixel 8a decode >= 8 tok/s, where projection = 14 tok/s (midpoint of the measured 1.7B Pixel rate 12-16) x the stage-0 mini tg128 ratio SmolLM3/1.7B. Stage 0 measured ratio 0.594 (0.583, 0.605 interleaved) -> **8.3 tok/s (range 7.1-9.5)**, so (b) holds.
If both variants are GO on K0, only the one with the higher K0 net runs stage 2 (tie: V).

## 4. Stage 2 (MAIN n 97, K0)
`CRITERION=<this file> bash lp-screens/tools/run_arm.sh <smol3vmain|smol3emain> K0 main <patch>` vs the mini control lpctl-K0-main-s42 (U 0.4055); outputs moved to arms/smollm3-3b/stage2/ afterwards.
**PASS iff dU >= +0.03 and its paired bootstrap CI low > 0 and CE-unwarned rate change <= +0.02**, computed by tools/stage2_verdict.py (frozen with this file; U = agg_run.py U; CEu by null-cal/tools/labels.py; B 2000 seed 11). Default-mode U (refused := 0) reported, not gating.

## Budget
calls_cap: Haiku 700 (4 screens <= 2 x 182 = 364 + stage 2 <= 194 + onboarding smoke 20 + slack). 0 Opus, 0 paid.
