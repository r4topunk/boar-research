# boar-preparedness (Emergency and preparedness)
TL;DR: curated format-2 pack of Appropedia, US-government, Wikibooks and Wikipedia documents on emergency preparedness; NOT in the shipped kit; strongest on v0.2 danger items.

## What it is
- Source: appropedia 567, usgov 206 (US Army FM 21-76 24 + US federal works 182), enwikibooks 71, enwiki 902, enwikivoyage 8 (1,754 articles). Built 2026-09-27 (builtAt 2026-09-27T05:22Z). meta aliases_pt 729 (PT aliases).
- Licence (meta): CC BY-SA 4.0; Public domain (US Army FM 21-76, 1992); Public domain (US federal government work, 17 U.S.C. 105).
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da...f514. Params: leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, embedTop 0 (lead_vecs 1,754). Contentless FTS5 yes. Counts: chunks 21,691; indexed 21,688 (99.99 %).
- Size: 16,490,496 B (15.7 MiB). sha256 53d8bcefd8ac65648eb959da2f0761cfb9efcb668822c4030f188312b764865e. Sibling boar-preparedness-en.sqlite (20,193,280 B, sha 2d7640d7...8c0, EN-only variant) is not the measured one.
- Per-document licence/URL list: shared-data/preparedness-v3/pack-manifest.json (294 KB).
## Kit entry and build
- Not in any measured kit. A kit entry would be {"id":"boar-preparedness","sha256":"53d8bcef..."}. 
- Build: build-wiki-pack.mjs family; builder log/script for preparedness-v3 not found. METADATA MISSING: shared-data/packs/README-preparedness.md and shared-data/packs/boar-preparedness.sqlite do not exist (P2 also notes the packs/ path is absent); no .sqlite.json manifest next to either file.
## Measured coverage (PACKCOND P2, arm H s42, dev data)
- V-para: 0/51 F0. v0.2: 8/110 (3 new beyond the installed kit); danger 6 of the added items (danger 10 items in total; kit alone covers 5, union 7).
- Replay F1/F2 not run (not top-2 by added coverage).
## Measured quality effects
- None measured. Added v0.2 items sit above average ratio anyway (P2 added-items mean 0.66 vs 0.61).
## Known gaps
- Zero V-para coverage; health 1/8 only; no non-English content apart from aliases; coverage is a safety niche, not a general lift.
## Community curation notes
- Card fields: id, name, domain, source + snapshot date, licence line per source (meta `sources`/`license`), counts, sha256, build command, kit entry `{id, sha256}`, known gaps.
- Self-test set (PACKCOND O4, P5, needs r4to): 20 public questions written by a curator (not Claude) whose answers are in the pack; scored by the same pipeline (F0 gate, then judge.v1 ratio); ship the per-pack number on the card.
- Licence: keep the per-source licence map from meta and a one-line attribution; CC BY-SA 4.0 and ODbL 1.0 are share-alike (card must say so).
- Self-test: 20 survival/first-aid/water questions with a source URL from pack-manifest.json. Safety content keeps the "AI-reviewed, not clinically reviewed" caveat.
