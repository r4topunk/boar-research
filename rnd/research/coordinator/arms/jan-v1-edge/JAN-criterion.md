# JAN-V1-EDGE criterion (frozen 2026-10-21 before any screen generation)

Arm: model swap Qwen3-1.7B Q4_K_M -> janhq/Jan-v1-edge (janhq/Jan-v1-edge-gguf @ e2c9bc87, Jan-v1-edge-Q4_K_M.gguf, sha256 bdde4346...0c59, Apache-2.0; Qwen3-1.7B base, SFT from Jan-v1-4B + RLVR) on the LITEPACKS mini tree; everything else identical (compact tier, prompts, declines, retrieval, seed 42, `--reasoning off` -> the template's empty `<think>\n\n</think>\n\n` prefill, as for the 1.7B). See ONBOARDING.md.
Known before the screen (onboarding smoke): thinking cannot be fully switched off. With the empty-think prefill the model still reasons in the visible answer on 3/5 smoke items per sampler and emits `</think>` there (runaways up to the 768-token cap). This is the deployable path, so it is screened as is; thought markers are reported, not a void condition.
Gate: **GATE v2**, arms/null-cal/GATE-V2.md (sha256 34ada53f1a9ab4ae31d971b6989eba3b4b979de8e05516fa687aad238a582982) + tools/screen_gate_v2.py (sha256 fa726fc0ac0b2380b528a5447b8058aec125a39b516eaec4f91df3173275729b), rnd commit 8c175580. PARAMS: K0 net >= 10, false refusals <= 2, U_cov delta >= -0.059; K1 net >= 9, false refusals <= 4, U_cov delta >= -0.071.

## 1. Candidates (both screened; the smoke did not separate them: Haiku CE 4/5 both, median answer 233 vs 133 tokens, both leak 3/5)
| Variant | Patch | sha256 |
|---|---|---|
| V (card sampling: T 0.6, top_p 0.95, top_k 20, min_p 0; health T 0 kept) | jan-v1-edge.patch | see jan-v1-edge.patch.sha256 |
| E (engine sampling 0.7/40/0.95/0.05, model only) | jan-v1-edge-engsamp.patch | see jan-v1-edge-engsamp.patch.sha256 |
Arm names: `jan-v1-edge` (V), `jan-v1-edge-eng` (E). Output root arms/jan-v1-edge/screens/ (OUT_BASE). Launcher: tools/launch_screens.sh.
The thinking-on probe (jan-v1-edge-think256.patch, `--reasoning on`, fast-tier budget 256) was a size measurement only and is not screened.

## 2. Stage 1 (screen)
For each variant and K in {K0, K1}: `OUT_BASE=arms/jan-v1-edge/screens SCREEN_JSON=null-cal/pool/screen2-<K>.json CRITERION=<this file> bash null-cal/tools/run_pool.sh <arm> <K> null-cal/pool/screen2-<K>.ids <patch>`.
Verdict per run = the printed screen_gate_v2.py line (GO / NO-GO), unchanged. Reported per run: gate line, CE-unwarned count (cand vs ctl), false refusals, U_cov delta, `[n]` citation compliance (share of live answers with >= 1 `[n]` on items where the control cites), mean output tokens and mean totalMs vs the control trace, answers containing `<think>`/`</think>`.
Sanity (run void, repeated once if violated): traces n/n, 0 error rows, 0 generation_failed, every trace's versions["model.sha256"] = bdde4346....

## 3. Stage-2 entry
Stage 2 runs iff a variant reads **GO on K0** under gate v2 (K1 reported, not gating). Speed: same architecture and the same file size as the 1.7B (1,107,409,440 vs 1,107,409,472 B), so per-token decode equals the 1.7B; no stage-0 bench. If both are GO on K0, only the higher K0 net runs stage 2 (tie: V).

## 4. Stage 2 (MAIN n 97, K0)
`CRITERION=<this file> bash lp-screens/tools/run_arm.sh <arm> K0 main <patch>` vs the mini control lpctl-K0-main-s42 (U 0.4055).
**PASS iff dU >= +0.03 and its paired bootstrap CI low > 0 and CE-unwarned rate change <= +0.02**, computed by tools/stage2_verdict.py (frozen with this file; U = agg_run.py U; CEu by null-cal/tools/labels.py; B 2000 seed 11). Default-mode U (refused := 0) reported, not gating.

## Budget
calls_cap: Haiku 700 (4 screens <= 2 x 182 = 364 + stage 2 <= 194 + slack). Spent before this freeze: onboarding smokes 30 (V 10, E 10, think256 10). 0 Opus, 0 paid.
