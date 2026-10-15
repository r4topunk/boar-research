# boar-wiki-en-07 (English Wikipedia shard 07 of 15)
TL;DR: one 1.2 GB shard of the full-enwiki split (403,973 articles); a reference gate pack, not shipped; weaker retrieval than top-100k.

## What it is
- Source: HuggingFaceFW/finewiki enwiki Enterprise HTML dumps (Aug 2025), part 07 of 15; redirects + pageviews 20250815. Built 2026-09-26 (builtAt 2026-09-26T23:01Z). Licence CC BY-SA 4.0 (Wikipedia, Wikivoyage).
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da...f514. Params: leadChars 2500, chunkChars 1000, embedTop 33334 (lead_vecs 33,634 of 403,973 articles). Contentless FTS5 yes. Chunks 1,913,583; indexed 1,581,704 (82.7 %; 17.3 % unindexed tables/numbers).
- Size 1,213,472,768 B (1.13 GiB). sha256 2455c805270ac04ecb921176f9110227aa5f1c05fbe7e14830ce13d57a68385b. Manifest: shared-data/packs/boar-wiki-en-07.sqlite.json (records the mini path); the copy in gate-ref/ has no .json beside it.
## Kit entry and build
- Not in any shipped kit; entry would be {"id":"boar-wiki-en-07","sha256":"2455c805..."}. Build: boar-app/scripts/build-wiki-pack.mjs via shared-data/packs/run-en-shards.sh (15 shards, shards 00-14 manifests exist; buildSeconds 199).
## Measured coverage (PACKCOND P2)
- F0: V-para 0/51 (1 loose), v0.2 24/110 (9 new). Retrieval on covered v0.2 items: raw 9/24 (38 %), kept 5/24 (21 %), pool20 11. Pack takes 46 % of kept slots (25 of 54), 3 base-kit collisions.
## Measured quality effects
- None measured at the answer level (coverage and replay only).
## Known gaps
- One of 15 shards, not topic-curated (shard assignment is not by topic), so coverage is incidental (24/110); retrieval and grounding lose 62-79 % of covered items before reading.
## Community curation notes
- Card fields: id, name, domain, source + snapshot date, licence line per source (meta `sources`/`license`), counts, sha256, build command, kit entry `{id, sha256}`, known gaps.
- Self-test set (PACKCOND O4, P5, needs the maintainer): 20 public questions written by a curator (not Claude) whose answers are in the pack; scored by the same pipeline (F0 gate, then judge.v1 ratio); ship the per-pack number on the card.
- Licence: keep the per-source licence map from meta and a one-line attribution; CC BY-SA 4.0 and ODbL 1.0 are share-alike (card must say so).
