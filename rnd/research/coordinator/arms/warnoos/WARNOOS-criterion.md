# WARN-OOS criterion (H-B, META 2026-10-16 13:xx; frozen before the run; 0 LLM / 0 judge / 0 paid)
Question: does the WARN question-side health signal (WARN_LEX from warnspec.py f2d1849a-line v3 + the engine's isSafetyQuery, healthgap tree) hold on a set the lexicon author never read?
Set: bench v0.2 110 (blind, script-only, scoped exception 10-16 13:xx; never read when WARN_LEX was written). Labels = the set's own fields, no reading: P = category health (8); D = danger True (10, reported apart); N = every other item (92).
Signal S(q) = WARN_LEX(NFC q) OR isSafetyQuery(q). The detector p and health-pack sources are not available question-side (claim kit has no health pack) and are not used.
Gate: recall on P >= 7/8 AND false-positive rate on N <= 0.10 -> PASS (default-on blocker narrowed to the detector line); recall <= 6/8 -> FAIL (lexicon over-fitted); FP > 0.10 -> FAIL-NOISY (banner fatigue risk).
Output: counts only, ids of P misses only (no text). One EXPOSURES row.
