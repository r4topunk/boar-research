# TRAVELSEL (Wikivoyage practical-section selection) on cut 3 — frozen 2026-10-05 by the coordinator before any code

Evidence (KNOWLEDGE-PACK-SIZING.md): trv-004, vit-trv-003 (and the Brazil 110/220 V fact) have the needed text IN the shipped Wikivoyage pack but selection drops it (+0.016 ceiling to Q450). Travel = 8 V-para items (travel-practical 5, travel-local 3).
Mechanism: for questions that already retrieve a Wikivoyage destination article and ask a practical slot (getting there/around, transport, safety/dangers, electricity/plugs/voltage, money/costs, visas, health/water), prefer chunks from the matching section ("Get in", "Get around", "Stay safe", "Stay healthy", "Electricity", "Buy"/"Money", "Cope") of the named destination, within the same work budget. Everything else untouched; never on health/danger card paths.

## L0 (deterministic stub-LLM replay, no judge)
- Gold fact in context (in-pack gold facts pre-registered in arms/travelsel/gold-facts.json BEFORE the first replay) on the 2–3 target items: ≥ 2 gain it, 0 lose it;
- other v0.1 + V-exact contexts byte-identical except travel-routed items; 0 travel-routed item loses its gold sentence; venues 6/6 and GPS city 3/3 unchanged; retrieval p50 ≤ 1.2× cut 3.
## L1 (v0.1 EN s44 + s45, same-day cut 3 control, judge changed items only, judge.v1-med)
PASS iff: target items' mean rubric up ≥ +0.5; no changed item down ≥ 1.0; unsafe 0; cw not up; paired Δ ≥ 0.
Stop rule: one revision after an L0 FAIL (gold facts may not be edited after the first replay); none after L1.
