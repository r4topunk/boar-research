# FOLLOWQ-G criterion (frozen 2026-10-06, after the FOLLOWQ diagnostic; post-hoc arm, declared)

FOLLOWQ (cb314c6): history-aware query Q1 gave sources to 10/21 rule-flagged follow-ups (plausibly on-topic titles: Lisbon, Dengue fever, Guernica, Canberra, Machu Picchu, Curitiba…), but changed retrieval on 11 non-flagged messages. Arm = cut 5 + Q1 (previous user turn + current) ONLY when FOLLOWQ's deterministic follow-up rule fires (rule copied verbatim from arms/followq/tools, no retuning); otherwise Q0 as today.
Gates:
G1 build: patch vs 0cfd4a77 applies to a fresh archive, tsc clean, all tests pass, new tests for the rule + query.
G2 identity: v0.1 EN s44 text/tier/passages identical 60/60 vs same-day cut 5 (single-turn → rule must never fire); on the 192 dev chat messages retrieval unchanged on every non-flagged message (0 diffs).
G3 quality (dev chat follow-ups whose answer text changed): Opus A/B judge (claude -p, both orders; prompt: given the conversation, which reply better answers the last user message — accurate, on-topic, uses the conversation; tie allowed), position-swapped. ADOPT iff arm wins ≥ 60% of non-tie decisions summed over both orders AND no answer judged unsafe/harmful that was not before.
G4 latency: retrieval wall time on the flagged messages ≤ 1.3× control (desktop).
Dev only (chat slices v0–v2); never chat-v3, blind/, rnd/veil/.
