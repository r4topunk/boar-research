# PACKSHAPE-FIRSTAID criterion (frozen 2026-10-23 before any shaped build or replay; never edited after)

Question: does the PACKSHAPE recipe (structure only) help boar-firstaid-en, the second-worst pack in PACKPROOF (correct-any
ON 0.35)? Health pack: AI-reviewed, not clinically reviewed. **No medical wording is changed**: no word is edited, reordered or
removed; the only additions are the topic name (already in the article title) and repeated section heading lines.

## Variant boar-firstaid-en-shaped (tools/shape_firstaid.py; sha in FIRSTAID-FROZEN.sha256)
- Same source: the text of v3proto boar-firstaid-en (0a7dffa6) read-only; 1,842 articles, same page_id, source, url, licence,
  attribution. Pipeline check done before this file: the unshaped text through the same builder reproduces the v3proto chunks
  22,500/22,500, articles and article_meta exactly.
- F1 topic = the last '/' segment of the article title.
- F2 prose paragraphs -> sentences; each list item = one unit; a unit without the topic gets "<topic>: " in front (after the
  list marker). Headings, 'Key facts:' lines, table lines and the title line stay byte-identical.
- F3 one chunk per section step block: within each heading section, units are packed in order into blocks of <= 120 words and
  <= 950 chars; each extra block repeats the section heading line verbatim (same section path). F4 a unit over the cap is never cut.
- Wording check (tools/check_words_fa.py, must pass or the build is invalid): removing the inserted "<topic>: " prefixes and the
  repeated heading lines gives the original token sequence for every article (whitespace aside); every number and word of the
  shaped text exists in the source.
- Build as PACKSHAPE (mini builder 885d7913 + wt/packcond libs, default params, lead_vecs, then the chunk_vecs sidecar); file
  kiln-local/shape-packs/fa-shaped/boar-firstaid-en.sqlite (same file name and pack id). Not in shared-data, never published.

## Arms, sets, metrics (as PACKSHAPE-criterion.md)
- BASE = K13 (the PACKSHAPE BASE replays, reused: st.BASE.on-k13, main.BASE). FASHAPED = K13 with v3proto boar-firstaid-en
  replaced by the shaped file (factbook stays the ORIGINAL v3proto file).
- ST20 = the 20 firstaid self-tests (on-k13 group); the other 120 on-k13 self-tests replayed too.
- Own fact chunk kept (primary): a normalised in_pack_facts quote is a substring of one kept own-article chunk body after the
  inserted "<topic>: " prefixes are removed (BASE: same rule, nothing to remove). Secondary: the loose 80 % token rule.
- MAIN 97 chunk-level (BASE 42), kept-set changes, firstaid share of kept slots, MAIN health losses; self-test health losses.

## Gate (0 LLM) - all must hold
(a) ST20 own fact chunk kept FASHAPED - BASE >= +5 of 20 (BASE 5 by the PACKSHAPE diagnosis rule); (b) MAIN chunk-level >= 41;
(c) 0 health losses on MAIN and on the 140 self-tests (a self-test or MAIN health item losing a kept health-pack doc).

## Stage 2 (only if the gate passes; Haiku <= 20, Opus 0, paid 0, phone 0)
20 firstaid items, FASHAPED kit, 1.7B Succinct seed 42 on the mini (PACKSHAPE run_mini recipe); Haiku 5.5-low call A, PACKPROOF
prompt. LEVER-CANDIDATE if correct-any >= BASE + 5 (0.35 -> >= 0.60) and read-right-when-delivered >= 0.6; else DELIVERY-ONLY.
Health answers keep the caveat; no wording decision is taken here.

## Predictions
- P1 fact chunk kept 5 -> 6 (gate (a) FAILS): firstaid's misses are mostly the health path keeping nothing (11/20 kept 0 chunks)
  and the chunks are already prose of ~104 words, so shaping has little to fix.
- P2 MAIN 42 -> 42, 0 health losses.
- P3 pack size +10 to +40 % (more chunks, prefixes).
