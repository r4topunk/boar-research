# HFU-FIX2 criterion (frozen 2026-10-06; re-test of the SAME frozen patch on fresh templates; post-hoc scope, declared)

HFU-FIX (rnd cde7325) failed as frozen: G3 58.1% (bar 90%, control 23.4%) because 23/58 EN probes (water ws-*, dng-005) have no card condition, so no follow-up rule can recover one; 121/133 = 91.0% on the rest (descriptive). G5b 4/20 non-health pairs routed health in BOTH arms ("What are the symptoms?" fires isHealthQuestion alone) — pre-existing, not rule-introduced. Patch 673ecf17… stays frozen (no code change).
Post-hoc changes, declared: (1) G3 scope = probes whose standalone question carries a card condition (the rule's stated domain); (2) G5b counts only health routes the arm adds over control. To avoid scoring on templates already seen, NEW templates frozen here:
T2 ∈ {"How long does it last?", "Is it dangerous?", "What causes it?", "How can I avoid it?", "What do I do now?"}.
G3' among EN dev probes with a card condition whose standalone form of T2 routes to health: ≥ 90% of follow-up forms get the same route class (arm), and arm ≥ control + 30 points.
G5b' 20 non-health pairs (same 20 as HFU-FIX) with T2: 0 health routes added by the arm vs control.
G2/G5a reuse HFU-FIX build numbers (unchanged patch). ADOPT → cut 6 = cut 5 + HFU-FIX (device-day candidate). If G3' fails again → closed, no further rescue.
