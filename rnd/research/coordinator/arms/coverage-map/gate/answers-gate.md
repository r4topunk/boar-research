# PRECISION-GATE answer screen (MAIN 97, 1.7B, 13-pack kit, RS_MERGE=gidf, seed 42, Haiku 5.5-low judge.v1 N 4 both orders) - EXPLORATORY

Criterion arms/coverage-map/PRECISION-GATE-criterion.md (sha a350a88b), tau 0.4842 (calibration.md). Control for the gate = ARM-G (compose/screen traces + judge rows); K3 control = null-cal/control/pool-K1.json. Aggregator tools/agg_gate.py; judged rows judge/P1, judge/P2 (38 Haiku calls, CALLS.md); unchanged answers reuse ARM-G / control / P1 rows.

| arm | U | corr | CE | CE unwarned (text line) | CE unwarned (+UI weak flag) | warned (text) | weak flag | no-source model answers | mean totalMs |
|---|---|---|---|---|---|---|---|---|---|
| control (K3 kit, stock) | 0.4102 | 2.536 | 29 | 12 | 12 | 46 | 0 | 14 | 4449 |
| ARM-G (13 packs, gidf) | 0.4167 | 2.582 | 24 | 14 | 14 | 40 | 40 | 1 | 5594 |
| P1 SCORE-GATE | 0.4194 | 2.577 | 24 | 14 | 12 | 37 | 44 | 17 | 4934 |
| P2 SELECT-GATE | 0.4176 | 2.572 | 28 | 16 | 13 | 40 | 46 | 19 | 6637 |

Paired dU (item bootstrap B 2000 seed 11):
- P1 vs ARM-G, changed items n 16: **+0.0163 [-0.0468, +0.0756]** (dcorr -0.031); all 97: +0.0026 [-0.0070, +0.0121]; vs K3 control all 97: **+0.0092 [-0.0129, +0.0313]** (ARM-G itself vs control +0.0065 [-0.0155, +0.0287])
- P2 vs ARM-G, changed items n 18: **+0.0041 [-0.0372, +0.0492]** (dcorr -0.056); all 97: +0.0008 [-0.0070, +0.0097]; vs K3 control all 97: **+0.0074 [-0.0145, +0.0283]** (ARM-G itself vs control +0.0065 [-0.0155, +0.0287])

Fact present / absent (flag = N10 gidf replay stage K; 32 / 60 / 5 unkeyed). Gated = sources withheld by the gate:
| arm | class | n | gated | ARM-G U -> arm U | dU vs ARM-G [CI] | answers changed |
|---|---|---|---|---|---|---|
| P1 | fact_present | 32 | 3 | 0.4247 -> 0.4242 | -0.0005 [-0.0275, +0.0195] | 3 |
| P1 | fact_absent | 60 | 13 | 0.4045 -> 0.4091 | +0.0046 [-0.0051, +0.0159] | 13 |
| P1 | unkeyed | 5 | 0 | 0.5069 -> 0.5069 | +0.0000 [+0.0000, +0.0000] | 0 |
| P2 | fact_present | 32 | 3 | 0.4247 -> 0.4273 | +0.0026 [-0.0032, +0.0104] | 3 |
| P2 | fact_absent | 60 | 15 | 0.4045 -> 0.4044 | -0.0001 [-0.0119, +0.0122] | 15 |
| P2 | unkeyed | 5 | 0 | 0.5069 -> 0.5069 | +0.0000 [+0.0000, +0.0000] | 0 |

False closed-book on fact-present items: P1 3/32 (9.4 %): vit-cry-008, vit-sci-001, lan-rsn-004; P2 3/32 (9.4 %): lan-hlt-003, vit-cry-001, vit-sci-001

Gated items, ARM-G corr -> arm corr (class):
- P1: vit-hum-001 A 2.5->2.0, vit-cry-007 A 1.0->1.0, vit-cry-008 P 3.0->1.0, vit-sci-001 P 2.5->3.0, vit-sci-002 A 1.0->1.0, lan-rsn-004 P 1.0->2.0, lan-rsn-005 A 3.0->2.0, st-qa-money-se-002 A 1.5->3.5, st-qa-money-se-005 A 2.0->1.5, st-qa-money-se-006 A 1.0->2.0, st-qa-money-se-008 A 2.0->3.5, st-qa-money-se-010 A 1.5->1.0, st-qa-money-se-012 A 3.0->1.5, st-qa-money-se-014 A 2.0->2.5, st-qa-money-se-015 A 2.5->2.0, st-qa-money-se-019 A 3.0->2.5
- P2: vit-hum-001 A 2.5->2.0, lan-hlt-003 P 3.0->3.5, vit-cry-001 P 2.0->1.0, vit-cry-005 A 2.0->1.0, vit-cry-007 A 1.0->1.0, vit-sci-001 P 2.5->3.0, st-qa-cooking-se-006 A 2.5->3.0, st-qa-cooking-se-010 A 2.5->1.5, st-qa-cooking-se-020 A 2.5->1.5, st-qa-money-se-002 A 1.5->3.5, st-qa-money-se-005 A 2.0->1.5, st-qa-money-se-006 A 1.0->2.0, st-qa-money-se-008 A 2.0->3.5, st-qa-money-se-012 A 3.0->1.5, st-qa-money-se-015 A 2.5->2.0, st-qa-money-se-016 A 2.0->2.0, st-qa-money-se-017 A 2.0->2.0, st-qa-money-se-020 A 1.0->1.0

Sanity (97/97, 0 errors, 0 empty, 0 loops, deterministic items identical to ARM-G in both arms): {"P1": {"rows": 97, "det_items": 24, "text_identical_to_G": 81, "closed_book": 17, "mean_totalMs": 4934.0, "kill": false}, "P2": {"rows": 97, "det_items": 24, "text_identical_to_G": 79, "closed_book": 19, "mean_totalMs": 6637.0, "select_calls": 72, "select_ms_mean": 3373.0, "no_evidence": 18, "unmapped": 0, "no_sentences": 0, "kill": false}}

Rule verdicts (frozen): P1: NO (dU>=+0.02 & CI low>-0.01: False, CE-unwarned not up: True, false closed<=10%: True, vs-control rule: False); P2: NO (dU>=+0.02 & CI low>-0.01: False, CE-unwarned not up: False, false closed<=10%: True, vs-control rule: False)
