# FOLLOWQ diagnostic criterion (frozen 2026-10-06, before any run). Diagnostic only: no adopt decision.

Finding: cut 5 retrieval is history-blind: `answer.ts:962` searchQuery = req.query (or its EN translation); earlier turns are not used. CHATGATE: 39/69 expected-search dev chat messages ended with no sources (mostly kit coverage).
Question: how many of those 69 are follow-ups whose topic lives in the history, and would a history-aware query find on-topic passages in the SAME kit?
Set: CHATGATE's 69 expected-search messages (dev chat slices v0–v2), same kit and retriever as CHATGATE. Dev only.
Variants (retrieval only, no generation): Q0 bare (as today); Q1 previous user turn + current; Q2 current + named entities/nouns carried from the last 2 user turns (deterministic, no LLM).
Measures per variant: messages with ≥1 passage over the engine's own relevance cutoff; follow-up flag (current turn has a pronoun/ellipsis and no named entity — deterministic rule, stated); on-topic proxy = a coordinator-blind Opus labeller is NOT used; instead report passage titles per item for a later read.
Decision for the coordinator (not automatic): build a FOLLOWQ arm only if Q1 or Q2 adds sources on ≥ 8 follow-up messages AND changes retrieval on ≤ 2 non-follow-up messages among the 192.
