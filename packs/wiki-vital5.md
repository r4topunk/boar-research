# wiki-vital5 (Wikipedia Vital Articles level 5, introductions)
TL;DR: format-1 pack of 49,832 Wikipedia article introductions (115,813 chunks); not in the shipped kit; tested as a peer and as an additive quota, no detectable gain.

## What it is
- Source: Wikipedia Vital Articles level 5, article introductions via the MediaWiki API. Built 2026-09-24 (builtAt 2026-09-24T20:29Z). Licence CC BY-SA 4.0 (Wikipedia).
## Format
- formatVersion 1 (older, simpler): single table chunks(id,title,body,source,scale,vec int8) with an FTS5 external-content table chunks_fts(title,body); every chunk carries its own embedding (dims 384, bge-small q8_0, embeddingModelSha256 ec38e8da...f514). id meta = wiki-vital5. Chunking via chunkIntro in boar-app/scripts/lib/knowledge-pack-lib.mjs. No tables-in-FTS issue (intros are prose). FTS yes.
- Counts: articles 49,832; chunks 115,813. Size 163,647,488 B (156 MiB). sha256 d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666 (QUEUE shows "d3b87d..." on the mini).
## Kit entry and build
- Not in the claim kit. VITALPACK/VITALADD used it as an extra kit entry {"id":"wiki-vital5","sha256":"d3b87d56..."}. 
- Build: node boar-app/scripts/build-knowledge-pack.mjs [--level 5|--titles file.txt] (docs/KNOWLEDGE_PACKS.md); steps are cached under build/knowledge-pack/<id>/.
## Measured coverage (PACKCOND P2 + VITALPACK)
- F0: V-para 1/51 (1 new beyond the installed kit), v0.2 20/110 (7 new). Added to the kit, vital5 fills 13/28 V-para and 23/47 v0.2 empty-kept items (VITALPACK replay).
- Crowding as a peer pack (share of kept slots): v0.1 36 %, V-para 33 %, v0.2 61 % (gate fail); additive quota q=1: 19-31 %.
## Measured quality effects
- VITALPACK-DEEP closed at step 0 (crowding gate). VITALADD (q=1 intro appended after grounding): NO, Opus slice -0.011 (-0.039...+0.018), Haiku full v0.2 +0.011 (-0.007...+0.029), not detected at MDE 0.025 although the mechanism fired (vital intro appended on 60/110 v0.2, 22/51 V-para). WIKISECTION: the missing rubric facts are mostly not in intro text either (vital-intro controls 1/6 V-para, 0/20 v0.2).
## Known gaps
- Intros only: no body facts, numbers, tables. V-para categories explanation/comparison/reasoning/synthesis: 0-1 F0 each.
## Community curation notes
- Card fields: id, name, domain, source + snapshot date, licence line per source (meta `sources`/`license`), counts, sha256, build command, kit entry `{id, sha256}`, known gaps.
- Self-test set (PACKCOND O4, P5, needs the maintainer): 20 public questions written by a curator (not Claude) whose answers are in the pack; scored by the same pipeline (F0 gate, then judge.v1 ratio); ship the per-pack number on the card.
- Licence: keep the per-source licence map from meta and a one-line attribution; CC BY-SA 4.0 and ODbL 1.0 are share-alike (card must say so).
- Format 1 packs should be rebuilt as format 2 before shipping (no lead_vecs/df; per-chunk vectors cost 115k x 384 B).
