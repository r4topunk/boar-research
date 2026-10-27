# WIKISECTION (H5) — are the deep tier's missing facts in a body section of the article it already kept? 0-call jev gate (2026-10-12; BACKLOG §1 row 1 gate: PASS if ≥ 40 % of the on-topic absent-knowledge items have the fact in a body chunk at p ≥ 0.7)

**Verdict: FAIL on both sets — the facts are not in the kept article at all.** On-topic absent items: V-para 2/13 (15 %) have the fact in a body chunk, v0.2 4/30 (13 %); the lead (1/13, 1/30) and the wiki-vital5 intro (1/6, 0/20) are as low. Off-topic-but-kept groups: 0/1 and 1/14. Where the fact does appear (6 items), 5 times it is in the body only.

| set / group | n | title → pack article | body chunk ≥ 0.7 | lead ≥ 0.7 | vital intro ≥ 0.7 |
|---|---|---|---|---|---|
| V-para, absent + on-topic | 13 | 10 | **2 (15 %)** | 1 | 1 of 6 |
| V-para, absent + off-topic, kept > 0 | 1 | 1 | 0 | 0 | 0 of 1 |
| v0.2, absent + on-topic | 30 | 23 | **4 (13 %)** | 1 | 0 of 20 |
| v0.2, absent + off-topic, kept > 0 | 14 | 7 | 1 (7 %) | 0 | 0 of 5 |
Method: `tools/section_gate.py`: for each item, both Opus rationales (judge.v1, s42) + each body chunk (≤ 60 per article, pack chunk boundaries) of the enwiki top-100k full-text pack article matching the kept title (redirects honoured; "Wikivoyage: X" resolved to the Wikipedia article X when it exists) → jev boolean "does the text state the specific missing fact"; max over chunks; lead chunk and the wiki-vital5 intro as controls. 3,251 gateway requests, [usage detail removed], 0 Claude calls; caches under the blind runs dirs; rnd holds ids, titles, probabilities. Caveats: items whose title did not resolve count as non-passing (3 + 7); jev reads literally, so a fact phrased very differently could be missed (the LOSSMAP calibration suggests the error is small, not 3×).

Reading: the rubric's missing facts on the deep tier's absent-knowledge items are not in Wikipedia's article on the kept subject (intro or body), and not in the model (it did not emit them with thinking). They are the kind of specific, question-shaped content a reference written with web access holds (LENGTHSHARE: ≈ 83 % substance). No section-level, intro-level or quota-based packing of Wikipedia can supply them; H5 closed at step 0, QNOTES (B6: notes from the 35B's own knowledge) loses its last support. Direction check (LOOP-PROGRAM §5.6) is now evidenced at the fact level: the floor-adjusted V-para target is not reachable with any kit-content or model lever measurable on ≤ 12 GB.

## Addendum H5b (2026-10-12) — is the fact ANYWHERE in the enwiki top-100k pack? (`tools/anywhere_gate.py`: BM25 FTS over the rationales' content terms + kept title, top 20 × 2 queries, ≤ 40 chunks per item, jev `has_fact`; 1,981 requests [usage detail removed], 0 Claude calls)
| set / group | n | fact somewhere in the pack (p ≥ 0.7) | in another article only | in the kept article |
|---|---|---|---|---|
| V-para, absent + on-topic | 13 | **1 (8 %)** (one other article) | 1 | 0 |
| V-para, absent + off-topic, kept > 0 | 1 | 0 | 0 | 0 |
| v0.2, absent + on-topic | 30 | 13 (43 %, marginal vs the 40 % bar; unverified) | 8 | 5 |
| v0.2, absent + off-topic, kept > 0 | 14 | 7 (50 %) | 6 | 1 |
Reading: on the bounty-style set the facts are not in Wikipedia at all (1/13): no retrieval or query lever over Wikipedia can reach V-para's absent-knowledge loss. On v0.2 the 43 % is a marginal, unverified upper bound (BM25 + jev false positives are visible in the hit titles: tangential articles for inflation and city items); it stays a dev-set curiosity, not an arm: a verified re-judge would cost nothing in Claude budget but cannot change the V-para reading. Wikipedia is closed as a source for the bounty bar.

## Correction 2026-10-12 (scope; see DEEP-RESEARCH-2026-10-12 §1 and deepresearch-2026-10-12/verify/wikisection_scope.md)
Both gates opened only the top-100k pack (indexed text; tables excluded by the builder) and only absent items with a kept source. "The facts are not in Wikipedia" is withdrawn; the result is "not in the top-100k pack's indexed text for the gated subset (1/13 at p ≥ 0.7; 4/13 at p ≥ 0.6)". The no-kept absent items, the full shards and a fresh snapshot are tested by WIKIFULL (T2).

Ledger note (2026-10-13, LEDGER-FIXES §5): WIKISECTION: no criterion file; the gate was pre-stated in BACKLOG §1 row 1 — nothing to freeze (a sha now would fake a pre-registration). WIKISECTION-H5b: no criterion file by design (measurement / descriptive / tooling); nothing to freeze.
