# PACKDENSE (PACKCOND P4b) step 0 gate: **FAIL at step 0 by projection** (2026-10-12 21:03; 0 LLM, 0 judge calls)

Criterion: PACKDENSE-criterion.md (sha256 e2815dd8…). D0: P4B-DIAG.md (tools/replay-p4b.ts, tools/p4b_diag.py, aggregates/p4b-diag.json; OFF raw lists identical to pg-off-H32 32/32, pg-off-R20 20/20, H traces 110/110).

| gate | bar | declared variant (M 2 per pack, floor 0.60, 1 passage) | verdict |
|---|---|---|---|
| G1 F0 article in raw top-6 | ≥ 22/32 (baseline 17) | **21/32 projected** (enters crypto-A06, danger-B01, honesty-refusal-A02, travel-local-A01; leaves 0); lossless ceiling M = 5: 22; M = 3: 21 | FAIL |
| G2 F0 in kept | ≥ 14/32 (11) | not projectable (dedupe, compression, grounding, health filter ignored; danger-B01 is health-strict) | — |
| G3 gold not lower | v0.2 ≥ 19, v0.1 ≥ 15 | 24 / 19 as scored, but the gain is the scorer's bare-title rule ("Wikivoyage: X" = Wikipedia gold "X"); genuine +1/−1 (v0.2), 0/−1 (v0.1) | pass (weak) |
| G3 churn | R20 kept changed ≤ 10/20 (reported) | raw lists changed 15/20; 95/107 v0.2, 45/54 v0.1 (the floor 0.60 sits below the noise p50 0.69, so the rule adds two guides to nearly every question) | reported |
| G4 cost | p50 ≤ 2×; scan ≤ 150 ms | scan p50 75 ms (34k vectors), max 155 ms cold; engine p50 156 ms | pass |

Why the gate replay was not run: the simulation reproduces the OFF baseline exactly and bounds every grid cell (M 1–5 × floor 0.50–0.70 × P 1–2) at ≤ 22 with gold not lower; the declared cell projects 21. The engine functions that the simulation ignores (dedupeArticleCopies, compression, grounding) can only remove passages, so the engine count cannot exceed the projection. Building the packDense engine patch to confirm a FAIL would spend an agent-hour on a known result; the patch is not built and the tree is unchanged.

Where the 15 misses are (D0 per-article table, best F0 target per item): term coverage of the fact article vs the question < 0.40 on 11/15 (the question's words are not in the article); lead cosine rank > 10 on 9/15 (bge-small leads of travel guides sit at a noise p50 of 0.69, the targets at p50 0.62); named by the question on 5/15 but with share 0.08–0.28 (side mentions under the 0.5 rule); 4/15 are danger items on the health-strict path with an empty raw list on 3 (regional guides' Stay-safe facts: Washington (state), Pacific Northwest, Western Java, Cold weather — the health search query may drop the place; see BACKLOG HEALTHQ). Filter-side relaxations (named share ≥ 0.1, BM25 pool 400 with coverage ≥ 0.3, dense top-3 ≥ 0.6) make at most 10/15 *eligible* before the k = 6 competition, at NAMEDSLOT-class churn (CLOSED R3: 15/60 raw lists moved); they are not declared.

Consequence: no 0-LLM retrieval-side lever on the installed packs reaches the gate on the v0.2 in-pack subset. The pack-conditional loss that remains is (a) questions whose words and meaning (under bge-small) do not reach the fact's article, and (b) the health-strict path. The line continues through pack-matched v0.3 items (boar-eval bench/v0.3/plan/pack-matched.md, PM7: ≥ 40 % non-lead facts, written with the article in hand) and, if r4to wants a retrieval lever measured on them, an LLM query writer (low prior: query2doc gains scale with model size).
