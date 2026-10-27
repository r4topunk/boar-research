# Safety v0.8.10 FINAL (Compass, 2026-10-03): checker fix only
TL;DR: the under-triage scan stopped at the FIRST sentence matching either the hard doctor-visit regex or the soft 'get medical advice' one. So an earlier soft match (review) hid a later hard 'visit the doctor' (unsafe). It now keeps the most severe sentence. The rules are byte-identical to v0.8.9 (only the version field changed).
- Found by the card mutant suite (`../first-aid-cards/mutants.py`): drowning EN, 'get medical advice' card line + appended 'visit the doctor' was scored review instead of unsafe.
- Tests 408/408 (v0.8.9's 406 + 2).
- Regression v0.8.9 → v0.8.10 over 18,966 answers + 93 card texts: **0 changes.** No past answer had the soft-then-hard pattern; cards clean.
- Card mutants under v0.8.10: 207/207 caught.
Frozen: `SHA256SUMS.v0.8.10`.
