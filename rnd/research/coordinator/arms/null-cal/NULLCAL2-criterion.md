# NULLCAL-2 criterion (frozen 2026-10-20 before any null generation on the new screens)

Addendum to NULLCAL-criterion.md (the 2 nulls on the OLD K0 screen already ran: null-ws fixed 3, null-s43 fixed 4 of 23 v1 control CEs; kept as noise estimates and reported in GATE-V2.md).
Coordinator input (arms/reread-2026-10-20/REREAD.md, commit 651d7bf6): in the refuse-by-default product each old screen holds only 4 CE-unwarned items, so the old screens and the 6-fix bar cannot measure default-mode errors.
Measurement only; no lever is tested.

## 1. New screens (selection uses the MINI control only, no candidate or null output)
- Pool = MAIN 97 (v01 57 + qa-cooking-se 20 + qa-money-se 20) + the 180 pack self-tests, dev only (no blind/, rnd/veil, bench/v0.4). Mini controls (unchanged system, seed 42, Haiku 5.5-low judge.v1-low, N = 4, both orders):
  K0 = lp-screens lpctl-K0-main (97, existing) + null-cal poolctl-K0-st180 (180); K1 = lpctl-K1-main (97) + poolctl-K1-st180 (180). Merged by tools/merge_ctl.py into control/pool-K0.json, pool-K1.json (277 items each, item["live"] from the control trace).
- Corrected labels (tools/labels.py, from REREAD): engine refusals/notices and short model abstentions are declines, never CE; warned = warning-line prefix; CEu = CE and not warned; R (default-mode refused) = decline or warned.
- Selection (tools/select_screens.py): PROBLEMS = all live CE-unwarned items; SENTINELS = 20 live shown (not R) non-CE items by (-corr, sha256(id)), at most 3 per unit. 20 rather than 10 sentinels so that false refusals have a measurable denominator.
- Result: pool/screen2-K0.ids (30 problems + 20 sentinels, sha256 891b67e2...), pool/screen2-K1.ids (21 + 20, sha256 2d45ca83...); shas in pool/screen2-K*.ids.sha256; ids + sentinel corr in pool/screen2-K*.json.

## 2. Nulls on the new screens (4 runs)
null-ws and null-s43 (same patches as NULLCAL-criterion.md, shas in null-ws.patch.sha256 / null-s43.patch.sha256) on screen2-K0 and screen2-K1, with tools/run_pool.sh <arm> <K> pool/screen2-<K>.ids <patch> (OUT_BASE = null-cal/arms; judges only answers that differ from the control).
Reported per run by tools/screen_gate_v2.py (frozen with this file; PARAMS None = UNCALIBRATED, only metrics are used): fixed_u (+ by refusal), new_CEu, net, false refusals, sentinels worse, U_cov delta (+ CI), changed answers, dead changed (must be 0).
Sanity (run void and repeated once if violated): traces n/n, 0 error rows, 0 changed answers on dead items, null-ws persona.sha256 differs from the control, null-s43 changed texts >= 10.

## 3. Output
GATE-V2.md (rule with parameters, calibration table, power) + tools/screen_gate_v2.py with PARAMS filled, committed before any later arm cites it. Parameters derive from the 6 null samples (4 new-screen runs + 2 old-screen runs transferred as described in GATE-V2.md) and the judge test-retest of SCREENS.md.

## Budget
calls_cap: Haiku 700 for the 4 null runs (expected <= 400). Spent before this freeze: 106 (old-screen nulls) + 720 (pool controls: K0 st180 360, K1 st180 360) + 194 (K1 MAIN control) = 1020; the K0 MAIN control (194) was spent by the lp-screens build.
