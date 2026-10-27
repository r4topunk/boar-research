# WIKIVOYAGE-REBUILD criterion (frozen 2026-10-21 before any candidate build)

## Question
Does a Wikivoyage-specific template whitelist in `renderTemplate` (about 40 templates; patch to a COPY of `wiki-pack-lib.mjs`, never boar-app) produce a candidate `boar-wikivoyage-en` pack with far fewer template holes, the same size class and the same retrieval behaviour except where a hole was fixed? Candidate only: it is NOT swapped into any kit or control by this arm.

## Inputs (all existing; nothing downloaded)
- Source dump on the mini: `<runner>/shared-data/dumps/enwikivoyage-latest-pages-articles.xml.bz2` (130,838,743 B, the file the current pack was built from; current pack builtAt 2026-09-27, sha256 ff8595e32f56b8b84e20464afd8bf88532d47d2d82d799e3df8489440004b66e, 548,051 chunks, 34,002 articles, 351,092,736 B).
- Builder: the mini's `<runner>/kiln/packs/builder/scripts` (wiki-pack-lib.mjs md5 04776e535a12674fc7b35e16afd306a5 = boar-app's); candidate builder tree = a copy of that `scripts/` dir with `node_modules` and `package.json` linked, only `lib/wiki-pack-lib.mjs` patched.
- Build recipe = `<runner>/knowledge-build/voyage.sh` (pass 1 `--no-embed`, pass 2 `--embed-only --embed-threads 2` with `BOAR_EMBEDDING_GGUF=bge-small-en-v1.5-q8_0.gguf BOAR_EMBED_GPU=metal`), `--name "English Wikivoyage"`, same defaults (leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12).
- Hole scanner: `arms/pack-holes/holes.py` UNCHANGED (sha256 `shasum -a 256` recorded in the report; python 3.14), full scan (`--articles-mod 1`), same pattern set. Definitions: STRONG = every pattern except space_punct/double_space; FACT = prep_punct, unit_no_number, between_and, paren_dash_only, born_died_empty, orphan_modifier; COSMETIC-class = empty_paren, paren_lead_punct, lang_label_empty.
- Output: `<runner>/shared-data/packs/candidates/boar-wikivoyage-en-v2/boar-wikivoyage-en.sqlite` (+ `.json`).

## Preconditions (a failed precondition makes the verdict INVALID, not FAIL)
- P1 scanner reproduces the existing numbers on the current pack: chunks_with_strong_hole 15,312 and chunks_with_fact_hole 7,451 of 548,051 (arms/pack-holes/out/boar-wikivoyage-en.json).
- P2 pipeline reproduces the pack: an UNPATCHED control build (pass 1 only, same builder copy) gives exactly 548,051 chunks and 34,002 articles. Control file is deleted afterwards.

## Gates (all must hold for PASS; each measured on the candidate)
- G1 fact holes: chunks_with_fact_hole / chunks_total <= 0.008.
- G2 total holes (strict reading of "cosmetic"): chunks_with_strong_hole / chunks_total <= 0.016 (strong = cosmetic-class + fact + line_lead_punct; the COSMETIC-class-only share is also reported, informational).
- G3 size: chunks_total within +-5 % of 548,051, i.e. 520,648 .. 575,454; articles_total exactly 34,002.
- G4 retrieval replay on the LITEPACKS K1 requests (280 items = lp-K1-v01 60 + lp-K1-cm 40 + lp-K1-st 180, seed 42), 0 LLM. Tool: `boar-eval/adapters/desktop-node/tools/replay-retrieval.sh --tree kiln-local/be-0cfd4a77-cut7-litepacks --tasks-from <the K1 traces> --verify-sha`, packs K1 = boar-crypto (ae9fbd2c) + wikivoyage + boar-simplewiki-en (v3proto 99bcec30). Run A = current wikivoyage, run B = candidate wikivoyage; everything else identical. Compared object = the engine's `raw` retrieve() list per item (ordered (source, title) pairs). Default replay settings (no packHeadPass/X2b; those act after retrieve()). Rule: every item whose raw list differs between A and B must contain, in A or B, at least one Wikivoyage article whose cleaned article text differs between the two packs (the "explained" set: a fix touched it); every item whose A and B lists contain NO such article must be identical in both. Unexplained items must be 0. Also reported (not gated): identical-item count, ordered-differs vs set-differs, items where a kept A chunk carried a hole (holes.py hole_chunk_ids on A) and whether B changed.
- G5 format and integrity: meta formatVersion 2, dims 384, embeddingModelSha256 ec38e8da142596baa913124ae50550de284b6916bf59577ef2f0cb9660c2f514, rows in lead_vecs == articles, contentless FTS5 present, `PRAGMA integrity_check` = ok, indexed >= 99.9 % of chunks, replay run B loads the candidate with no error.

## Not gated, reported
Pack bytes, chunk delta, text bytes, build seconds, sha256, per-pattern shares before/after, 6 before/after sentences, template-hit counts of the whitelist (top 15), articles whose text changed, tests of the patch (`tools/wikivoyage-whitelist.test.mjs`).

## Verdict rule
PASS = P1, P2 hold and G1..G5 hold. Otherwise FAIL naming the gate (or INVALID for a precondition). Budget: 0 judge calls, 0 paid API. No kit, control, or boar-app file is modified; the current pack is read-only.
