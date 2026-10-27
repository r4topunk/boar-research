# STACK criterion (FROZEN 2026-10-22 23:4x, before any replay): lexical fixes + dense re-rank + chunk vectors together

Configuration: 13-pack kit with the v3 cooking/money files (chunk vectors), RS_MERGE=gidf, SEFIX F1 + F2 + F4 (F3 withdrawn), RS_RERANK=mix (R1), settings packHeadPass a2 + packDense2 extra (as F1b), K1 tree clone with the H4-MERGE + SEFIX-F1/F2/F4 + R1-RERANK patches.
Reads (0 LLM): MAIN 97 replay, chunk-level delivery (tools/chunklevel.py) on MAIN 92 / cm 40 / v0.1 52 vs SEFIX-124 (F1+F2+F4, v2 files) and SEFIX-ALL (47) and R1 mix (42); losses among the facts SEFIX-124 delivers; junk-kept (mean kept chunks on items with no fact kept) vs SEFIX-124; kept tokens; switch-off identity 20/20 vs the F1b replay.
Rule: STACK DELIVERS iff chunk-level kept on MAIN 92 ≥ max(SEFIX-124, 47) + 5 AND losses ≤ 2 AND junk ≤ 1.15× SEFIX-124 AND v0.1 chunk-level ≥ SEFIX-124's − 1. Then the Haiku answer screen (1.7B on the mini, seeds 42 and 43, divergence-first vs the K3 control of the same seed, judge.v1 N 4 both orders, cap 200): LEVER-CANDIDATE iff pooled ΔU vs K3 over 97 ≥ +0.03 with CI low > 0 AND CE-unwarned ≤ the control's.
Prediction: chunk-level kept 54…58 (cm 24…28, v0.1 27…29), junk ≤ 1.1×; answer screen +0.03…+0.05 pooled (cooking/money optimistic), v0.1 0.
Caps: 0 LLM for the replay; Haiku ≤ 200; Opus only after PASS; paid 0; phone 0.
