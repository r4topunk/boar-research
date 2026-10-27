# WARN-OOS (H-B, META 2026-10-16 13:xx): out-of-sample check of the WARN question-side signal on v0.2: FAIL (recall 3/8)
Criterion WARNOOS-criterion.md sha 66f73c41… (frozen before the run). 0 LLM / 0 judge / 0 paid. Script-only on blind (v0.2 110, scoped exception 10-16 13:xx; WARN_LEX was written 10-16 from public sets only, so v0.2 is unseen). Tool gate_warnoos.py, output gate.json.

| group (set labels, no reading) | n | S = WARN_LEX or isSafetyQuery | WARN_LEX | isSafetyQuery | isHealthQuestion |
|---|---|---|---|---|---|
| P: category health | 8 | **3** | 3 | 1 | 1 |
| D: danger True | 10 | 6 | 3 | 6 | 4 |
| N: all other | 92 | 2 (FP 0.022) | 1 | 1 | 0 |
Misses (ids only): v02-health-A02, A04, B01, B03, B04. The engine's own health routing is also weak here: grounding:health-* fires on 1/8 health items in the kit replay.

**Verdict:** FAIL by rule (recall 3/8 <= 6/8): in-sample 15/15 does not transfer; FP side is fine (2.2 %). Not tested: the detector p >= 0.05 line and health-pack sources (no detector in the search-gate replay; kit has no health pack), which may carry the misses. Consequence: deps.warn stays off by default; before default-on, run the mmbert detector on these 8 + 10 questions (0 LLM, the :8094 detector) and only then decide whether to widen the lexicon (any widening must be checked on a set it was not fitted on: v0.3).
