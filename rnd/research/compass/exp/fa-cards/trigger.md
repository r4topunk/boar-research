# First-aid condition cards v0: trigger (frozen with cards.v0.json)
1. Gate (all must hold): the engine is about to show the generic no-source health card (`noHealthSourceAnswer`, from the health path or from A1's `grounding:danger-v1`), i.e. the same places A1 acts. Never replaces a sourced answer or a decline in v0.
2. Condition: `terms.regex_condition(query)` (terms.py) returns exactly one condition → that card. If it returns several (MULTI) → no specific card (generic card stays).
3. Fallback, only if terms.py returns none: bge-small query vector vs condition centroids (mean of L2-normalized prototype vectors per condition, protos.json); top cosine ≥ 0.75 and top − second ≥ 0.03 → that card.
4. Snakebite keeps its existing card and trigger (firstAidCards.ts).
5. Otherwise: the generic card, unchanged.
