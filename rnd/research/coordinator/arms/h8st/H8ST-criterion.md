# H8-ST step 0: build-time contextual chunk headers for format-2 packs — does the fact chunk reach the raw list without any LLM? (frozen 2026-10-13 23:2x, coordinator; a parallel session)

## Tags
Tags: none

## Question
ORACLE-ST (RETRIEVAL-HEADROOM, +0.095 Opus from one injected fact chunk; the gain sits on the 137/180 items whose fact chunk the engine does not reach) makes retrieval reach the first bottleneck on pack-matched items. H8 (BACKLOG META 10-13) names two build-time expansions: (a) contextual chunk headers — the chunk's indexed text carries its article title and section path (Anthropic "contextual retrieval" −49 % failed retrievals; Doc2Query-- +3–16 % BM25 recall); (b) doc2query synthetic questions (≈ 14 h of 4B generation per 55k chunks). This step 0 measures (a) alone, with 0 LLM calls: a sidecar/alternate lexical index whose per-chunk text = `title — section path — chunk text` (and, declared variant X2, + the article's first sentence), on COPIES of the published packs; the engine reads the alternate index under a setting (default off, byte-identical off). It decides whether (a) is worth a judged re-score and whether (b) is needed.

## Fixed inputs
- Packs: copies of the 9 published wave-1/2 packs under shared-data/packs/h8proto/ (published files untouched; sha256 of each copy recorded). Builder: the pack builder's lexical index path (find it: boar-app scripts/build-wiki-pack.mjs and the engine's WikiPack FTS/keyword search) — X = the same index built over header-augmented chunk text; X2 = X + article first sentence. The engine change lives in a copy tree (never wt/packs, wt/groundst, the claim tree, cut7-oracle/-stack/-tk2*): a setting that opens the alternate index when present.
- Reference: the OFF replay on the same tree (replay-crowd / replay-p4b / tk2-replay pattern: engine retrieval + keep step, no LLM) on the 180 public self-test items with kit + the item's pack. Reach definitions = packroute step0.py / tk2-replay compare_tk2.py (fact chunk in raw top-6/top-8, fact article kept, fact chunk kept, empty-kept).
- v0.1 public (60, kit only) no-harm replay: the kit packs get the alternate index too (crypto, Wikivoyage), so G2 is meaningful.

## Power
expected_delta: reach: fact chunk in raw top-8 55–67 → ≥ 90 of 180 (BACKLOG H8-ST gate; lit prior +3–16 % recall); quality (not measured here): ≤ +0.095 × share of items newly reached × keep-through rate
n: 180 (reach counts, deterministic); 60 v0.1 (no-harm)
seeds: n/a (replay, deterministic)
mde: n/a (counts; gate below)
slice: none (0-LLM replay over all 180)
l1_futility: n/a
reopen: none (H8 was proposed, never run; PACKDENSE R44 and DENSECHUNK R46 were dense levers — this is lexical, build-time)
split: pre-declared: SE packs (question-shaped titles) vs topic packs (factbook, medlineplus, simplewiki, firstaid) — expected: the gain on topic packs, ≈ 0 on SE

## Stages and rules
0. Build the alternate indexes (X, X2) for the 9 packs + 2 kit packs; byte-identical OFF check on 3 items (prompt/kept/raw equal to the tk2-replay OFF cell on the same tree, or to a fresh OFF replay).
1. Replays OFF / X / X2 on the 180 (kit + item's pack) and on v0.1 (kit only). Gates (X or X2 may pass):
   - **G1 reach:** fact chunk in raw top-8 ≥ 90/180 (OFF reference measured on the same tree, expected 55–67) AND fact chunk kept ≥ OFF + 15.
   - **G2 no-harm:** v0.1 gold-in-kept and gold-in-raw6 not lower than OFF; empty-kept not up by more than 2; kit lost-context 0.
   - **G3 cost:** retrieval p50 ≤ 1.3× OFF; index size growth per pack reported (≤ +25 % of the pack file).
2. Verdict: **PASS** (all gates for X or X2) → the loop schedules the judged re-score (Haiku L1 on the 180, Opus if Δ ≥ +0.02) and H8-ST (b) doc2query only for the packs where (a) leaves the fact chunk unreached; **FAIL** → (a) closed at step 0, (b) doc2query becomes the H8-ST step 0 (needs mini time; after the SFT4B stage 1); **PARTIAL** (G1 reach met on topic packs only) → report by split, the loop decides.

## Stop rules and budget
0 LLM, 0 judge, 0 paid. MacBook disk ≥ 8 GiB (index copies ≈ pack size; delete X2 if X fails G3); no llama-server needed; never touch the mini. Deadline: report by 2026-10-14 00:50 BRT or at a stage boundary.

## Outputs and exposure
arms/h8st/H8ST.md (coordinator writes), aggregates/, tools/ (index builder, replay driver, compare), runs/; the patch as h8st.vs-cut7.patch + sha256. Public items only → no EXPOSURES row; QUEUE row per stage.
