# H4b-GIDF2 (0 LLM, 0 judge, 0 Opus, 0 paid, 0 phone; MacBook, 2026-10-22; web action W92)
Patch patches/H4b-GIDF2.patch (delta over H4-MERGE, sha256 d39ca6ed…; 2 files packs.ts, wikiPack.ts), clone kiln-local/rs-H4b (rs-H4 and base untouched). `RS_MERGE=gidf2` = gidf (global idf ratio, unchanged) + one GLOBAL avgdl in BM25's length term. Tools: tools/run_h4b.sh, run_compose_h4b.sh, score_h4b.py, score_compose_h4b.py, identity_h4b.py; data h4b.json (qform, main, compose, identity), replays gitignored.
Quantities read per pack (all exact, checked on the six packs): fts_data row 1 = FTS5's averages record (nRow, tokens per column; sum = sum of fts_docsize, equal to meta.indexedChunks); fts_docsize = tokens per candidate (D, all columns, one read per search for the <= 80 pool ids). Global avgdl = sum of tokens / sum of rows over installed format-2 packs = 90.33 (locals: factbook 118.9, firstaid 109.8, medlineplus 124.5, visa 124.0, crypto 89.5, wikivoyage 88.2; wikivoyage holds 83 % of the tokens). FTS5 bm25 formula (k1 1.2, b 0.75, weighted tf, D over all columns) re-derived from fts5vocab(instance) = FTS5's score to 9e-16. Re-score: per term, one-term bm25 -> f = s / idf_local -> weighted tf = f k1 K / (k1+1-f) -> f' with K' (global avgdl) -> idf_global x f'; rebuild check (own avgdl back) <= 5e-15. Approximations: pool (top 80) and term choice stay local; prior, per-article cap unchanged.
Identity: RS_MERGE=gidf in the H4b tree = H4 gidf kept lists 432/432 (six, merged), 97/97 x3 kits, 97/97 COMPOSE N10; unset = H4 off 432/432 x2, 97/97 x3, N10 97/97 (= coverage-map stock); switch-off 20/20 (proof20 merged, proof6 six files); gidf2 on ONE pack (merged file) = control 432/432 and 20/20.
## (1) QFORM 432, six A-union files (control qform.v2-off; paired bootstrap B 2000 seed 11)
| run | hit@kept | vs control pts [item CI] | gained/lost | raw / wide12 | junk x ctl | ctx tok | wall ms/q | own-pack share |
|---|---|---|---|---|---|---|---|---|
| v2-off | 117 (27.1 %) | | | 147 / 180 | 1.00 | 288 | 224 | 54.9 % |
| gidf (H4) | 144 (33.3 %) | +6.2 [+3.9, +8.6] | 27/0 | 181 / 206 | 1.10 | 289 | 274 | 66.0 % |
| **gidf2** | **138 (31.9 %)** | +4.9 [+3.0, +7.2] (fact CI +2.5, +7.4) | 21/0 | 174 / 199 | 1.09 | 288 | 296 | 64.0 % |
gidf2 vs gidf: -1.4 pts [-2.8, -0.2], gained 1 / lost 7 (CI excludes 0, wrong sign). Per form gidf/gidf2: F0 4.2/2.1, F1 2.1/2.1, F2 20.8/16.7, F5 10.4/6.2, F6 4.2/0.0, F7 10.4/12.5, F8 4.2/4.2, F3-F4 0/0. Per pack gidf/gidf2: visa 13.9/12.5, factbook 9.7/2.8, medlineplus 6.9/8.3, firstaid 4.2/2.8, crypto 2.8/2.8, wikivoyage 0/0 (factbook alone loses 5 of the 7). Wikivoyage kept slots 331 -> 351. Merged file: 179 for off, gidf and gidf2 (identical lists).
## (2) MAIN 92 kept facts (kept = FACTPRESENT lexical OR cm oracle) and funnel ids
| kit | ctl | gidf | gidf2 | v0.1 (ctl/gidf/gidf2) | 25 S2/S3 kept ctl/gidf/gidf2 | 22 S4/S5 kept | gidf2 vs ctl |
|---|---|---|---|---|---|---|---|
| K3 | 23 | 24 | 24 | 23/24/24 | 1/2/2 | 22/22/22 | +vit-cry-001 |
| K3 + cooking + money | 29 | 30 | 30 | 23/23/23 | 1/2/2 | 22/21/21 | +money-006, +vit-cry-001, -lan-rsn-006 |
| K3 + top100k | 25 | 27 | **28** | 25/27/28 | 6/7/7 | 17/18/19 | +exp-004, +trv-003, +vit-cry-001; top100k slot share 55/55/49 % |
## (3) COMPOSE N = 10 (13 small packs; stock 29, gidf 32)
gidf2 N10 kept 32 (v0.1 28), identical kept set to gidf (0 gained / 0 lost vs gidf); vs stock +vit-cry-001, +cooking-012, +sci-001; recovery 6/25, losses 0/22; whole curve N0..10 gidf2 23/29/30/30/30/32 = gidf's; rule verdict NEITHER (v0.1 N2 22 < base 23), as for gidf; COMPOSES for stock. Wall N10 stock 678 / gidf 735 / gidf2 807 ms (noisy, N4 gidf2 run hit other load).
## Verdicts (frozen rules) and prediction
- RETRIEVE-SWEEP (94ddb631) on six files: gidf2 **NO** (+4.9 < +8; CI low +3.0, junk 1.09x pass; funnel recovery 1/25 vs 5; losses 0-1/22 ok). Same verdict as gidf, with less lift.
- COMPOSE read: N10 kept 32 = gidf, +3 over stock; the global avgdl adds nothing there.
- Prediction six files +1..+3 hits over gidf: **missed, wrong sign (-6 hits; -1.4 pts)**. Prediction N10 +0..+2 kept: result +0 (low edge); MAIN kits +0/+0/+1.
## Reading and caveats
Global length normalisation is the right model but the wrong lever here: the pooled avgdl (90) is wikivoyage's, so every small topical pack (avg 110-125 tokens, factbook records long by design) is penalised against wikivoyage; the 35-hit merged/six gap (179 vs 144) is not length norm (what remains: pool and term selection, title path). Keep gidf (idf only). Dev items, 0 LLM: hit/kept counts, not answer quality; K3W +1 is one id. gidf2 costs one extra docsize read per pack search (+8 % wall on six files over gidf; phone unpriced; one run each).
