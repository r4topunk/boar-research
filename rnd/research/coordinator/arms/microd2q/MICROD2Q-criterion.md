# MICROD2Q: does doc2query help where it matters, before generating for 1 M chunks? Gate visibility + a targeted micro-expansion on the 180 (frozen 2026-10-14 00:3x, coordinator; a parallel session)

## Tags
Tags: none

## Question
NEXT-RETRIEVAL-ARMS-2026-10-13 ranks doc2query-- below HEADPASS because (i) it only changes the index while 95/137 unreached items fail the text relevance gate (coverage ≥ 0.5, wikiPack.ts:857) and the keep step, and (ii) a full build costs ≈ 270 mini-hours. This arm answers two cheap questions first. **Q1 (code, 0 compute):** do synthetic questions indexed as an extra FTS column reach the relevance gate and onTopic, or only the BM25 ranking? **Q2 (targeted replay):** if we generate questions only for the 137 fact chunks AND every other chunk of the same articles (realistic within-article competition) plus the kit packs' top-50 competing chunks per item, does the fact chunk reach raw top-8 ≥ 90/180 and kept ≥ OFF + 15? A pass justifies one small pack (medlineplus 3k chunks) end-to-end; a fail closes doc2query for the pack line.

## Fixed inputs
- Tree: copy of cut 7 (kiln-local/be-0cfd4a77-cut7-d2q; node_modules symlinked); the h8st alternate-index setting pattern (arms/h8st/h8st.vs-cut7.patch: `fts_h8` with an extra column) reused with a `questions` column; for Q1, a declared variant X2 = the gate and onTopic also see the questions column (engine change, default off).
- Generator: Qwen3-4B-Instruct-2507 Q4_K_M on the MacBook llama-server (one server at a time), prompt from NEXT-RETRIEVAL-ARMS §2 (5 questions, everyday words, ≤ 20 words), temp 0.7, top_p 0.9, max 160 tokens, seed 42; filter: drop the lowest 30 % by bge-small cosine to the chunk, keep ≤ 3.
- Targets: the 137 unreached items' fact chunks (arms/oracle-st/tools/oracle-facts.json) + all chunks of those articles + the top-50 BM25 competitors per item from the kit and the item's pack (so expansion is applied to competitors too — no privileged treatment of the fact chunk).
- Replays: arms/h8st/tools/replay-h8.ts pattern on the 180 (kit + item's pack) and v0.1 public (60, kit only); OFF = the tk2off reference.
- Inflation flag: max token-Jaccard between each fact chunk's generated questions and its self-test question; report the distribution and the reach counts with and without the 20 % most item-similar expansions removed.

## Power
expected_delta: reach: fact chunk in raw top-8 69 → ≥ 90 of 180 (lit prior Doc2Query-- +3–16 % recall; our diagnosis says ≤ 27 + part of 21 items are addressable by vocabulary)
n: 180 (deterministic replay); 60 v0.1 no-harm
seeds: 1 (generation seed 42; replays deterministic)
mde: n/a (count gate)
slice: none
l1_futility: n/a
reopen: R6 NOTES35 new-mechanism clause (questions as index keys only, no new chunks); the H8 (b) BACKLOG row
split: pre-declared: lexical-miss items (27) vs gate-fail (21) vs article-found (56) — expected: gain on the 27, ≈ 0 on the 56 unless X2 also passes the gate

## Stages and rules
1. Q1 (0 compute): read the gate/onTopic code paths; state with file:line whether an index-only column can affect them; implement X2 only if the change is ≤ 40 lines and default-off byte-identical.
2. Generation on the MacBook for the target set (≈ 3–6k chunks, ≤ 90 min; stop if > 1.5 s/chunk or parse rate < 90 %); build the questions column on pack COPIES (shared-data/packs/d2qproto/, published files untouched, sha recorded).
3. Replays OFF / X1 (index only) / X2 (gate sees questions) on the 180 and v0.1. Gates: G1 raw top-8 ≥ 90 AND kept ≥ OFF + 15 (X1 or X2); G2 v0.1 gold-in-kept and gold-in-raw6 not lower, empty-kept not up by > 2; G3 index growth per pack projected ≤ +25 %, retrieval p50 ≤ 1.3×.
4. Verdict: PASS (→ one small pack end-to-end as the next step; 0.8 mini-hours or [usage detail removed] GPU) / FAIL (doc2query closed for the pack line; HEADPASS and the keep step are the remaining levers) / PARTIAL (G1 met only with X2 → the gate change is the real lever; report by split).

## Stop rules and budget
0 judge, 0 paid; ≤ 6k 4B generations on the MacBook; disk ≥ 8 GiB; one llama-server at a time (HEADPASS-ST step 0 is replay-only, so both arms may run concurrently); never the mini.

## Outputs and exposure
arms/microd2q/MICROD2Q.md (coordinator writes), tools/, runs/, aggregates/, d2q.vs-cut7.patch + .sha256. Public items only → no EXPOSURES row; QUEUE row per stage.
