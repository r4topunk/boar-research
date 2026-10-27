# boar-wikivoyage-en (English Wikivoyage)
TL;DR: full English Wikivoyage as a format-2 pack; in the shipped kit (config.kit[1]); covers the travel categories and a few comparison/danger/honesty items.

## What it is
- Source: enwikivoyage-latest-pages-articles dump, 34,002 articles. Built 2026-09-27 (builtAt 2026-09-27T00:08Z), 111 s.
- Licence (meta): CC BY-SA 4.0 (Wikipedia, Wikivoyage). Share-alike attribution needed.
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da...f514. Params: leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, embedTop 0 (lead_vecs 34,002, int8 for all articles). Tables: articles, articles_title, chunks, chunks_article, blocks, redirects, df, lead_vecs, contentless FTS5. FTS yes.
- Counts: chunks 548,051; indexed 548,005 (99.99 %; listings are prose-like so the tables-in-FTS caveat barely applies).
- Size: 351,092,736 B (335 MiB). sha256 ff8595e32f56b8b84e20464afd8bf88532d47d2d82d799e3df8489440004b66e.
## Kit entry and build
- config.kit: {"id":"boar-wikivoyage-en","sha256":"ff8595e3..."} (same config as crypto). 
- Build: boar-app/scripts/build-wiki-pack.mjs (voyage mode; manifest boar-wikivoyage-en.sqlite.json records the mini path <runner>/shared-data/packs/).
## Measured coverage (PACKCOND P1, F0 verified)
- V-para: F0 2 (H) / 3 (K) of 51. v0.2: F0 27 (H) / 17 (K) of 110 (the largest F0 source in the installed kit).
- Wikivoyage F0 items include comparison, danger, honesty-refusal and explanation items (Wikivoyage articles double as city/country overviews), not only travel: P1 F0 any-pack by category v0.2 H: comparison 5/13, danger 5/10, honesty-refusal 5/12, travel-practical 3/4, travel-local 1/2.
## Measured quality effects
- With crypto in the curated kit: +0.045 (DEEPNORAG, deep tier). VENUEGPS-2 (7/7 venues) used places tiles, not this pack.
- P1 conditional (kit packs together): H v0.2 floor-adj 0.55 on F0 (n=32) vs 0.39 uncovered; K 0.41 (n=20) vs 0.29. Part selection (easier items), not an intervention effect.
## Known gaps
- V-para travel-local 0/3 and travel-practical 1/5 covered: the rubric facts there are venue/time-specific and not in guide prose. Not a venue list (see kit-vexact places).
## Community curation notes
- Card fields: id, name, domain, source + snapshot date, licence line per source (meta `sources`/`license`), counts, sha256, build command, kit entry `{id, sha256}`, known gaps.
- Self-test set (PACKCOND O4, P5, needs r4to): 20 public questions written by a curator (not Claude) whose answers are in the pack; scored by the same pipeline (F0 gate, then judge.v1 ratio); ship the per-pack number on the card.
- Licence: keep the per-source licence map from meta and a one-line attribution; CC BY-SA 4.0 and ODbL 1.0 are share-alike (card must say so).
- Self-test candidates: visa/transport/safety facts for named cities.

## Converter-fix rebuild (2026-10-21, not published, not swapped)
- Rebuilt on the mini with the CONVERT-FIX lib (`{{convert}}`/`{{cvt}}` only; builder-cf, lib md5 cd17fa24): 351,133,696 B (+41 kB), sha256 34130f664c2c87e518ca6b61a465b9a8233d9200b130a478eb7b4882d40aa321; 34,002 articles, 548,035 chunks (-16 vs this pack; the post-09-27 stripMediaLinks fix also applies), format 2, integrity ok, lead_vecs 34,002. Candidate path: shared-data/packs/candidates/boar-wikivoyage-en-convfix/ (mini + MacBook).
- Artefact chunks (CONVERT-FIX regex): 877 -> 801 (-9 %); broad regex 2,180 -> 2,024. Wikivoyage mostly uses unit templates (`{{km}}`, `{{c}}`, `{{m}}`...), which the convert-only patch does not render; the WIKIVOYAGE-REBUILD v2 whitelist candidate (080408a9) covers them (fact holes 1.36 % -> 0.79 %).
- Retrieval parity (0 LLM, K3 kit, 280 dev questions): raw and kept identical 280/280; 900 articles changed text.
- Not published: this pack has no self-test file, coverage or crowding probe (PACK-CATALOGUE D-K3 b-d) and no folder on r4topunk/boar-packs; it is pinned (ff8595e3) in the shipped and device-day kits. Details: coordinator/arms/convert-fix/CONVERT-FIX-SHIP.md.
