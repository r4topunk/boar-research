# boar-wiki-en-top100k (English Wikipedia, top 100k by views, full text)
TL;DR: 2.54 GB format-2 pack with full text of the 98,389 most-viewed enwiki articles; rejected for the 4B, closed for the deep tier (DEEPWIKI -0.034) because it takes 98 % of kept slots; the largest raw coverage gain (+27 v0.2 items).

## What it is
- Source: HuggingFaceFW/finewiki (enwiki, Enterprise HTML dumps of August 2025), 15 FineWiki EN shards @8bd13e72; redirects enwiki-latest-redirect.sql.gz; pageviews-en-20250815 (1 day). Built 2026-10-02 (builtAt 2026-10-02T06:03Z; manifest file dated Oct 10), buildSeconds 56 for the packaging step.
- Licence (meta): CC BY-SA 4.0 (Wikipedia, Wikivoyage).
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da...f514. Params: fullTop 100000, leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, embedTop 50000 (EMBED-NOTE: two OOMs at 100000, coordinator decision 2026-10-02; lead_vecs 50,081 cover ids 1..50081 in storage order, not top-50k by views; relabel fix 2026-10-02 05:25, pre-fix sha aff5fd11...). Contentless FTS5 yes.
- Counts: articles 98,389; chunks 4,019,506; indexed 3,235,902 (80.5 %: 19.5 % of chunks, mostly tables/numbers, are NOT in FTS; tables-in-FTS caveat).
- Size: 2,542,215,168 B (2.37 GiB). sha256 9123b3720abd847291e2502d7529419ca86c1fc4cf111e9b449a2be06fc694e7.
## Kit entry and build
- Kit entry used by DEEPWIKI/P2: {"id":"boar-wiki-en-top100k","sha256":"9123b372..."}. Not in the shipped kit; on the build hosts.
- Build: scripts/build-wiki-pack.mjs @ upstream/main 0cfd4a77 + --drop-rest (wt/enwiki-droprest); args --full-top 100000 --drop-rest --pageview-days 1 --redirects --index (by runner agent; see boar-wiki-en-top100k.sqlite.json).
## Measured coverage (PACKCOND P2, arm H s42)
- F0: V-para 4/51 (3 new), v0.2 47/110 (27 new beyond the installed kit; 59 total with kit). By category the union adds on v0.2: comparison 7, explanation 11, reasoning 10, honesty-refusal 8, danger 7, synthesis 4, crypto 3.
- Retrieval on covered items: V-para raw 3/4, kept 3/4; v0.2 raw 28/47 (60 %), kept 23/47 (49 %), pool20 31.
- Crowding: pack takes 98 % of kept slots on the covered v0.2 items (100 of 102; 32 base-kit collisions by title) = DEEPWIKI 62 % share.
## Measured quality effects
- DEEPWIKI (deep thinking tier, V-para slice 20, Haiku): -0.034 (-0.082...+0.003), h2h 4/8/8, NO; pack took 26 of 28 kept slots, retrieval 2.6x slower. Earlier rejected for the 4B. WIKISECTION: only 2/13 (V-para) and 4/30 (v0.2) absent-knowledge items had the fact in the full article body.
## Known gaps
- No quota against the curated packs; Wikipedia body text rarely holds the rubric facts of V-para; 19.5 % unindexed chunks lose table facts.
## Community curation notes
- Card fields: id, name, domain, source + snapshot date, licence line per source (meta `sources`/`license`), counts, sha256, build command, kit entry `{id, sha256}`, known gaps.
- Self-test set (PACKCOND O4, P5, needs the maintainer): 20 public questions written by a curator (not Claude) whose answers are in the pack; scored by the same pipeline (F0 gate, then judge.v1 ratio); ship the per-pack number on the card.
- Licence: keep the per-source licence map from meta and a one-line attribution; CC BY-SA 4.0 and ODbL 1.0 are share-alike (card must say so).
- Curators should ship a share cap (per-pack quota, PACKCOND O2) with this pack; 2.5 GB is a device-storage decision.
