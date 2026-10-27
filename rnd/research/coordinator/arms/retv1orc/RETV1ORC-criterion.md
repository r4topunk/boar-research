# RETV1ORC criterion (frozen 2026-10-20, before any generation)

Arm: the 1.7B LITEPACKS system (cut7-headpass-x2+litepacks, Qwen3-1.7B Q4_K_M, LITEDECLINE_OFF=5, --reasoning off, seed 42, mini) on pack set K1,
with the RETFLOOR **V1orC** append gate: an X2b pending append (X1 neighbour or dense pick) is kept only if it passes onSubject OR its cosine to the question is >= 0.70
(arms/retfloor/RETFLOOR.md; health questions keep the onHealthTopic rule as in RETFLOOR).
Candidate = `retv1orc.patch` (unified, -p1 on the tree root; = tools/apply_retfloor.py output with the env default switched from "base" to "V1orC", so no env file is needed).
Patch sha256 `93b9be73ab192d063b394c201d06ddf8d9cb4de32f71d4e83dad6f335398e288`. Dry-run applies to kiln-local/be-0cfd4a77-cut7-litepacks (answer.ts 0d1ac07d).

## Stage 1 (screen): GATE v2, K1
- Gate spec: arms/null-cal/GATE-V2.md sha256 `34ada53f1a9ab4ae31d971b6989eba3b4b979de8e05516fa687aad238a582982`; tool null-cal/tools/screen_gate_v2.py (PARAMS K1), unchanged.
- Screen: null-cal/pool/screen2-K1.ids (sha256 2d45ca83…, 21 problems + 20 sentinels); control = null-cal/control/pool-K1.json (mini K1 control).
- Run: `OUT_BASE=arms SCREEN_JSON=null-cal/pool/screen2-K1.json CRITERION=<this file> bash null-cal/tools/run_pool.sh retv1orc K1 null-cal/pool/screen2-K1.ids retv1orc/retv1orc.patch`.
- Judge: Haiku 5.5-low, judge.v1-low, N = 4, both orders; only answers whose text differs from the control are judged. Cap 100 calls for stage 1.
- **GO iff net >= 9 AND false refusals <= 4/20 AND U_cov delta >= -0.071** (the gate v2 K1 rule, verbatim from the tool). Otherwise NO-GO: stop, no stage 2.
- Reported, not gated: CE-unwarned count control -> arm on the 41 screen items; fixed_u (by refusal), new CEu; sentinels worse; coverage (items with >= 1 `retrieval.kept` source)
  control -> arm on the screen items; mean `timing.promptTokens` control -> arm (live items); changed answers; dead changed (must be 0).
- Sanity (invalidate, not NO-GO): traces n/n, 0 error rows, `retfloor:variant:V1orC` reason code present on every item that had pending appends, dead items unchanged.

## Stage 2 (only on GO): MAIN n 97, K1
- Run: `CRITERION=<this file> bash lp-screens/tools/run_arm.sh retv1orc K1 main retv1orc/retv1orc.patch` (main-97.ids sha256 9664d81f…). Cap 200 calls.
- Metrics on the 97 items with labels.py (default-mode product): U_d = sum(0 if R else s) / sum sref; CEu rate = CEu / 97. Paired item bootstrap B 2000 seed 11, 95 % percentile CI.
- **Primary: vs the mini K0 MAIN control** (lp-screens/control/aggregates/lpctl-K0-main-s42.json). **PASS iff U_d change >= +0.03 AND its CI low > 0 AND CEu-rate change <= +0.02.**
- Secondary (reported, same thresholds stated as PASS/NO): vs the mini K1 MAIN control (lpctl-K1-main-s42.json).
- Also reported: agg_run U (declined-only) deltas, coverage change on MAIN, prompt tokens.

## Notes
- A stage-1 GO authorises stage 2 only; stage 2 PASS is a candidate result, not an adoption.
- Haiku only, 0 Opus, 0 paid. Generation only on the Mac mini via the gen1/gen2 slot lock.

## Budget
calls_cap: Haiku 300 / Opus 0
opus_clause: none
