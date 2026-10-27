# FACTS r2 judge result (2026-10-06): ADOPT by the frozen criterion (research-only after the cut 6 freeze; PR-phase candidate)
Criterion FACTS-judge-criterion.md b38e33cc… · patch facts-r2.vs-cut6.patch d8f8142d… (wt/facts 24cd66ef) · 16 judge calls (judge.v1-med, both orders) · control = speedpack-l1/spctl-v01-s44 (one named source run).
| item | ctl | FACTS r2 | Δ | corr ctl→arm | winner ctl→arm |
|---|---|---|---|---|---|
| lan-cmp-001 Brazil vs Russia population | 3.50 | 4.33 | +0.83 | 4.0→5.0 | ref→ref |
| lan-rsn-002 Burj Khalifa in Lake Baikal | 3.00 | 5.00 | +2.00 | 3.0→5.0 | ref→**tie** |
| lan-ref-001 2017 Literature Nobel | 3.33 | 5.00 | +1.67 | 3.0→5.0 | ref→**tie** |
| lan-ref-004 Iceland area | 4.67 | 4.67 | 0 | 5.0→5.0 | tie→tie |
| lan-exp-006 Kilimanjaro | 2.67 | 3.33 | +0.67 | 3.5→5.0 | ref→ref |
| lan-rsn-007 Berlin Wall years | 4.33 | 4.33 | 0 | 5.0→5.0 | ref→ref |
| lan-ref-005 2016 Olympics host | 4.00 | 4.33 | +0.33 | 4.5→5.0 | **boar→boar** |
| trv-002 plug type | 1.67 | 3.67 | +2.00 | 2.0→5.0 | ref→ref |
Pooled Δ +0.94 rubric points per item over 8; drops ≥ 1.0: none; correctness ≤ 2: 1 → 0; correctness 5.0 on all 8; unsafe n/a (no danger items). Gates: pooled Δ ≥ 0 PASS · no drop PASS · cw not up PASS → **ADOPT**.
Projected effect on the v0.1 EN ratio (57 items, same judge): +7.5 rubric points over ≈ 279 reference points ≈ **+0.027**, above the ≈ 0.025 MDE and the largest single-arm gain since cut 3 (VG+AR +0.029). Deterministic answers (no seed noise; judge noise only).
Caveats: dev-motivated item selection (the 8 were chosen because the table covers them); held-out coverage UNKNOWN (v0.2 is blind; its composition is explanation/reasoning-heavy); trigger recall on fresh phrasings unmeasured (the CF killer) → FACTS-RECALL L0 next; completeness still 2–3 on multi-part items (the table answers one fact; Kilimanjaro lost "highest in Africa"); 60 Hz field empty; cut 6 is frozen, so this is research-only until r4to decides.
