# SAFEPACK addendum 1 (frozen 2026-10-19 after the engine run E, before any model generation or audit; parent 601b2897)

Observation that forces it (no answer quality read, routes and retrieval only): the engine with the pack installed called the model on 1/30 items (15 REFUSE "I don't have a reliable offline source", 11 raw extracts, 3 cards); the gold Ready.gov/FM page was in raw retrieval on 5/30, raw retrieval empty on 10/30. The prompt dump therefore has 1 context, so "restyle on the engine's contexts" cannot run.

Change: the restyled arms use an ORACLE context instead: for each item, one context passage = the gold source document's text window of 2,000 characters starting 300 characters before the first in_pack_facts quote (clipped to the document), formatted as the engine does ("Context:\n[1] <title>\n<passage>"), inside the app chat-path system message (arm sys + context instruction + the engine identity text). Arms: M4, LF, Q17 x D0, D4 (6 arms x 30 = 180 generations; D5 dropped to fit the day). This measures reading/safety given the right page; E measures the current system end to end.
Retrieval diagnosis is reported separately (gold page in raw / kept, raw empty, route kind) and is the main product finding if E fails the safety rule.
Metrics, decision rules and caps otherwise unchanged; E is audited with the same blind safety audit.
