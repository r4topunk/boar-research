# B1-LAYER-SPLICE criterion (round 7, ruler/hypotheses-round7-2026-10-21.json; frozen 2026-10-21 before any spliced number was computed)

## Statement (verbatim)
Splicing our cut-7 deterministic-layer answers into the RC1 shipped rows on the 8 CV5 layer ids raises RC1's Opus U floor-adj from 0.143 to >= 0.183
(dU >= +0.04, item-bootstrap CI low > 0) and lowers CE per 100 by >= 8. Ids: lan-cmp-001, lan-exp-006, lan-ref-001, lan-ref-004, lan-ref-005,
lan-rsn-002, lan-rsn-007, trv-002.

## Inputs (all existing; 0 LLM, 0 judge calls, 0 phone)
- Base: RC1 Opus judge.v1 rows arms/rc1-pixel/a1/judgments/rc1-shipped.opus.judgments.jsonl (sha bf6bab00...), rows.jsonl df26ed79....
- Layer answers: CV5 rung L3_4B_phone_cut7 traces (boar-eval/runs/device-pixel8a/final-cut7-v01/traces.jsonl). An id counts as a
  deterministic layer iff timing.outputTokens == 0 and route.reasonCodes has an 'answer:' code. Ids that fail are dropped from the splice
  (kept at their RC1 score) and the n is reported.
- Layer judgments reused: the Opus judge.v1 rows in ruler/cv5-ladder/out/L3_4B_phone_cut7.judgments.jsonl for those ids (both orders, seed 7),
  loaded exactly as a1_analyze.py does (same text key via cv5_opus_pool). No new judge call.

## Analysis (tools/b1_splice.py)
- RC1' = RC1 item vector with the layer ids' (s, r, corr, wins, decline flag) replaced by the L3 values. U floor-adj, raw, U_D2S, per 100
  (correct/CE/decline), win/tie/loss as A1. dU = RC1' - RC1, paired item-cluster bootstrap B 2000, numpy default_rng(11), 2.5/97.5 pct.
- Sensitivity: same splice on the L0 1.5B closed-book desktop rung (L0' - L0).

## Decision (frozen)
- SUPPORTED iff n_layer >= 5 and dU >= +0.04 and dU CI low > 0 and d CE per 100 <= -8. KILL iff n_layer < 5 or dU < +0.02
  (NOTE-1 section 3 drops the 'largest measured lever' sentence for the shipped app; port moves behind NOTE-1/NOTE-5). Else MIXED.
- Label everywhere: a 0-call counterfactual projection (assumes the app routes the same items to the same layer texts), not a measurement.
