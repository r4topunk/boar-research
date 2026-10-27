# HEADPASS-X2 criterion — addendum 1: variant X2b = budget-capped append (frozen 2026-10-14 14:1x, coordinator; base criterion sha 1b70f6f3… unchanged)

Trigger (X2-GATE.md, step 0 of X2): G1 PASS (fact present 113/180 ≥ 102; +41 newly present over S, 25 of them topic-pack items), G2 PASS (kit byte-identical; v0.1 + simplewiki lost-context 0, gold kept 10 → 18), G3 PASS on time and scan but **FAIL on prompt tokens: p50 1,120.5 vs the bar S + 600 = 1,100** — the dense slots fire on 165/180 and fill both slots on nearly every item (327 chunks appended), so the cost lands on the 54 items where only non-fact chunks are appended as much as on the 41 that gain the fact. Verdict for X2 as frozen: FAIL at step 0 (by 20.5 tokens of the engine's approximate count; the rule stands).

## Variant X2b (declared here; same gates, same tree, same sidecars)
The append path gets a **per-item work budget**: appended chunks (X1's neighbours first, then dense candidates in cosine order, D ≤ 2 dense) are added only while the prompt stays ≤ the item's S prompt tokens + 600 (engine approximate count, the same one the gate uses); the first chunk that would exceed the budget is dropped and the loop stops. Nothing else changes (no displacement, outside the keep step, health-strict rule, caps). Consequence: G3's prompt-token gate holds by construction; the question becomes reach under the budget.
- G1 unchanged: fact present ≥ 102/180 and ≥ X1 per family. G2/G3 unchanged (time ≤ 2× S; scan ≤ 300 ms).
- Reported in addition: appended chunks dropped by the budget (count, how many were the fact chunk), present per family, the split denominators vs S and vs X2.
- Stage 1–3 as the base criterion (generation of X2b on the 180 + v0.1 + simplewiki OFF/ON; Haiku; Opus 360 declared, runs if Haiku Δ vs S > 0).
Not a rescue of X2's number: X2b is a different mechanism (a budget rule) with the same bars; X2's step-0 result is recorded as FAIL in CLOSED (R73) with X2b/X3 as its reopen path.
