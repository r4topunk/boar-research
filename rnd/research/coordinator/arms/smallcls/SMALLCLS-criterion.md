# SMALLCLS criterion (frozen 2026-10-19 before any run)
Question (r4to 10-19: "usar o 1b como classificador ... metodologia de refino de busca a partir de um modelo pequeno, que entrega para um modelo grande responder"): can a small model do the two closed-label steps of emergency search refinement better than the hand rules, so a larger model answers from the right page and section?

Tasks (0 judge calls; deterministic scoring):
- A. Hazard/topic classifier: question -> one of 32 labels (safepack-tasks.json: 27 Ready.gov hazard/guidance pages + the other gold pages of the safepack set + "none"). Gold = the item's gold page; negatives = "none".
- B. Section selector: question + the gold page's section headings (## / ### lines of the page) -> one heading. Gold = the heading above the item's first verified quote (25 safepack items have one).
Sets:
- S30 = the 30 safepack items (A and B). Caveat: the SAFEROUTE hand rules were built on these 30.
- F = a FRESH set written for this arm by a separate agent before any run: >= 40 new emergency situations across the labels (not paraphrases of S30, situation-now phrasing, gold label + gold section from the same pages) + 40 non-emergency negatives (travel, crypto, general knowledge, health information that is not an emergency) with gold "none". A only, plus B where the agent gives a gold section.
Systems:
- Hand rules = SAFEROUTE hazardTerms (saferoute.patch, ptQuery.ts) mapped to labels by the hazard word (no-term -> none); for B the engine's current choice is the section E' quoted (S30 only).
- Q17 = Qwen3-1.7B (thinking off), M4 = Qwen3-4B-Instruct-2507 (upper reference), llama-server b11010 on the mini, temperature 0, max_tokens 24, one fixed prompt per task listing the options verbatim; the output is matched to an option (exact, then case/space-folded; unmatched = wrong).
Metrics: A accuracy (exact label), A emergency recall (gold != none and predicted != none), A false alarms (gold none, predicted not none); B accuracy; B on the 3 E' unsafe items (shelter-in-place chemical, gas leak, 911); prompt tokens and wall time per call.
Decision:
- Small-model refinement is ADOPTED for the next build step if Q17 on F has A accuracy >= hand rules + 0.10 with false alarms <= 4/40, AND Q17 on S30 B accuracy >= 0.80 with the 3 unsafe items correct (or each wrong one not leading to the unsafe passage).
- If only M4 passes: refinement is right but needs the 4B (cost note: one extra 4B prefill per query).
- If neither passes: hand rules stay; report the error table.
Caps: < 1 h mini after the current queue; 0 judge; 0 paid.
