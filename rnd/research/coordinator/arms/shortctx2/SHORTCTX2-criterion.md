# SHORTCTX2 criterion (frozen 2026-10-20, before any generation)

Arm: the 1.7B LITEPACKS system (cut7-headpass-x2+litepacks, Qwen3-1.7B Q4_K_M, LITEDECLINE_OFF=5, --reasoning off, seed 42, mini) on pack set K1 with the SHORTCTX context cap:
at most 2 sources, ~350 context tokens, sentence-boundary cut, health and multi-pass untouched.
Candidate = `arms/shortctx/shortctx.patch` (unchanged, -p1 on the tree root; sha256 `3b9cac98c09837e097c1b6eb60f5d27ab39bf2a095c24ebe57a4bd7e6323b259`).
Why again: SHORTCTX stage 1 ran on the old v1 screen (fixed 4 of 27, NO-GO); REREAD-2026-10-20 reads it as -1 CE-unwarned in default mode with 0 new errors. This re-screens it on the GATE v2 K1 screen, whose bar is measurement-derived.

## Stage 1 (screen): GATE v2, K1
- Gate spec: arms/null-cal/GATE-V2.md sha256 `34ada53f1a9ab4ae31d971b6989eba3b4b979de8e05516fa687aad238a582982`; tool null-cal/tools/screen_gate_v2.py (PARAMS K1), unchanged.
- Screen: null-cal/pool/screen2-K1.ids (sha256 2d45ca83..., 21 problems + 20 sentinels); control = null-cal/control/pool-K1.json (mini K1 control).
- Run: `OUT_BASE=arms SCREEN_JSON=null-cal/pool/screen2-K1.json CRITERION=<this file> bash null-cal/tools/run_pool.sh shortctx2 K1 null-cal/pool/screen2-K1.ids shortctx/shortctx.patch`.
- Judge: Haiku 5.5-low, judge.v1-low, N = 4, both orders; only answers whose text differs from the control are judged. Cap 100 calls for stage 1.
- **GO iff net >= 9 AND false refusals <= 4/20 AND U_cov delta >= -0.071** (gate v2 K1 rule, verbatim from the tool). Otherwise NO-GO: stop, no stage 2.
- Reported, not gated: CE-unwarned count control -> arm on the 41 screen items; fixed_u (by refusal), new CEu; sentinels worse; coverage; mean timing.promptTokens control -> arm; changed answers; dead changed (must be 0).
- Sanity (invalidate, not NO-GO): traces n/n, 0 error rows, dead items unchanged.

## Stage 2 (only on GO): MAIN n 97, K1
- Run: `CRITERION=<this file> bash lp-screens/tools/run_arm.sh shortctx2 K1 main shortctx/shortctx.patch` (main-97.ids sha256 9664d81f...). Cap 200 calls.
- Metrics on the 97 items with labels.py (default-mode product): U_d = sum(0 if R else s) / sum sref; CEu rate = CEu / 97. Paired item bootstrap B 2000 seed 11, 95 % percentile CI.
- **Primary: vs the mini K0 MAIN control** (lp-screens/control/aggregates/lpctl-K0-main-s42.json). **PASS iff U_d change >= +0.03 AND CI low > 0 AND CEu-rate change <= +0.02.**
- Secondary (reported): vs the mini K1 MAIN control (lpctl-K1-main-s42.json), same thresholds as PASS/NO.

## Notes
- A stage-1 GO authorises stage 2 only; PASS is a candidate result, not an adoption.
- Haiku only, 0 Opus, 0 paid. Generation only on the Mac mini via the gen1/gen2 slot lock. Dev sets only.

## Budget
calls_cap: Haiku 300 / Opus 0
opus_clause: none
