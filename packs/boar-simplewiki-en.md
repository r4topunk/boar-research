# boar-simplewiki-en (Simple English Wikipedia)
TL;DR: the whole Simple English Wikipedia (dump 2026-10-01): 208,622 articles in full text with infobox key facts and redirect aliases, every lead embedded; 480.5 MB; built 2026-10-13 ; NOT in any kit; coverage and crowding measured 2026-10-13; self-test scored 2026-10-13 (see Quality).

## What it is
- Source: `simplewiki-20261001-pages-articles-multistream.xml.bz2` (387,919,857 B, sha1 8a12322b4c2081e31592c426f0d130d30296449a = dumps.wikimedia.org dumpstatus.json). 562,214 pages; 400,692 in namespace 0.
- Converter: `simplewiki-convert.mjs` (new; archived with the build scripts). The builder's `--wikivoyage` mode is Wikivoyage-specific (hard-codes source `enwikivoyage`, no infoboxes, no aliases), so the dump goes to the builder as JSONL instead: body = the builder's own `cleanWikivoyage` (same as WIKIFULL stage B), infoboxes = stage-B extraction → the builder's "Key facts:" line (97,569 articles have one), HTML entities (&nbsp; …) decoded, trailing boilerplate sections dropped (Related pages, Other websites, References, Notes, Sources, Further reading, Gallery, See also, External links). Dropped: 115,214 redirects, 5,474 disambiguation pages (stage-B template regex + "(disambiguation)" titles), 71,376 bodies < 200 chars; 208,628 rows out (6 more dropped by the builder: pages left with no chunk). Aliases = ns-0 redirects to the page (cap 50): 102,602 → 100,540 redirect rows.
- Licence (meta and every row): "CC BY-SA 4.0 (Simple English Wikipedia)"; url = `https://simple.wikipedia.org/wiki/<Title>`; no per-row attribution (the URL is the credit, as for the enwiki/Wikivoyage packs).
- Views: 0 on every row (no pageviews file for simplewiki in the builder; no popularity prior).
- Example citation string (engine, query "who was Marie Curie"): `Simple English Wikipedia — https://simple.wikipedia.org/wiki/Marie_Curie (CC BY-SA 4.0 (Simple English Wikipedia))`.
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da…f514. Params: leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, fullTop 1000000, embedTop 0; dfMin 2000. `articles.source` = 12 (simplewiki) on every row.
- Counts: articles 208,622 (all full text); chunks 621,682; indexed 586,279 (94.3 %, tables not indexed); lead_vecs 208,622 (all; `--embed-top` not needed); redirects 100,540; article_meta 208,622 rows (3 columns, no attribution); text 343.8 MB.
- Size: 480,534,528 B (458.3 MiB). sha256 c751768b75f91258c896a131e49743c58609cceb711c6d8fdd713671c63adabe.
- meta keys: format, formatVersion, dims, embeddingModelSha256, sources, license, manifestSha256, name, articles, chunks, indexedChunks, dfMin, params, builtAt. name "Simple English Wikipedia (2026-10-01)". meta.sources counts the manifest (208,628 documents), not the 208,622 articles.
## Kit entry and build
- Not in any kit. Kit entry would be {"id":"boar-simplewiki-en","sha256":"c751768b…"}. Label "Simple English Wikipedia" and the simple.wikipedia.org URL need the the pack workflow engine patch .
- Files: `$RUNNER_ROOT/shared-data/packs/wave2/` on the build host.
- Build (build host, Apple M4; download ≈ 2 min, convert 60 s / 453 MB RSS, build wall 928 s: text + FTS 2 min, lead embeddings ≈ 14 min at ≈ 225/s on Metal, first 5k at 218/s → projected 16 min; scripts in rnd/runner/packs/wave2-scripts/build-wave2.sh):
  ```sh
  node --max-old-space-size=6144 scripts/wave2/simplewiki-convert.mjs dl/simplewiki/simplewiki-20261001-pages-articles-multistream.xml.bz2 work/boar-simplewiki-en $RUNNER_ROOT/runner/packs/builder/scripts/lib 2026-10-01
  bash scripts/build.sh boar-simplewiki-en "Simple English Wikipedia (2026-10-01)" work/boar-simplewiki-en/manifest.json work/boar-simplewiki-en/simplewiki.000.jsonl work/boar-simplewiki-en/simplewiki.001.jsonl
  ```
## Engine check (patched engine tree, WikiPack.search k 5, lexical only, 2026-10-13)
- "why is the sky blue": WRONG article: the title rule matches "Sky blue" (the colour) and "Light blue"; no scattering passage in the top 5 (FTS `rayleigh` = 30 chunks exist).
- "who was Marie Curie": Marie Curie lead / Death / Personal life, then Curie Institute (Paris).
- "how do vaccines work": Vaccine lead / Effectiveness / Types of vaccines, COVID-19 vaccine, RNA vaccine "How mRNA vaccines work".
- FTS: rayleigh 30, curie 139, vaccine 546. Source ids 12:208,622.
## Measured coverage
- V-para 34 absent items: verified 0/34, >=0.7 1 (unverified), >=0.6 2; 0 on the 20 no-kept items (coverage probe 2026-10-13: jev fact-in-text over 20 candidate chunks per item, deep-tier run s42).
## Crowding
- crowding probe 2026-10-13: share of kept slots 0.829 (v0.2) / 0.714 (v0.1), on 75 / 38 items, in every category including crypto and refusal items (replay on 110 + 60 dev items); kit gold over kit slots drops 18/15 to 10/8 (v0.2) and 16/14 to 5/3 (v0.1), on 9 / 13 items; empty kept lists fall 50 to 24 / 15 to 8 → **user-selected only** (a general pack crowds the kit, as the earlier large-Wikipedia test did); retrieval p50 +6 / +7 ms.
## Quality
- Self-test score (2026-10-13; the 20 public self-test questions written from this pack's text; Haiku 5.5-low L1 judge, both answer orders; 4B claim build; dev): with pack raw **0.57** (0.48–0.64), above_min 0.45 / without pack raw **0.47** (0.39–0.54), above_min 0.31; paired Δ +0.102 raw (95 % CI +0.054…+0.157), +0.133 above_min; items better/worse with the pack 15/2; win/tie/loss vs the gold answer 0/0/20. Pack passages kept on 15/20 items (38/43 kept passages); the fact's source article kept on 12/20. Gold answers are agent-written from the same text: a development check, not comparable with benchmark numbers.
- Self-test, deep tier (Qwen3.6-35B-A3B + thinking 512, desktop, Haiku 5.5-low N=4 both orders, 2026-10-13): with pack 0.599 vs without 0.567, Δ +0.032 (−0.020…+0.090); deep with pack vs 4B with pack +0.032 (−0.023…+0.100); pack passages kept on 16/20 items; win 0/20. Dev numbers, agent-written gold; the pack's effect on the deep tier is not decided (CI through 0).
## Category gaps
- Simple English: short articles (≈ 3 chunks per article, 1.6 kB of text on average) with simplified wording and fewer numbers than enwiki; weak on recent events and niche topics. No pageview prior, so lexical ties are not broken by popularity.
## Curation notes
- The "Sky blue" miss is the title-in-question rule (`titlesInQuestion`, share ≥ 0.5) picking a colour article; a semantic re-rank (queryVec) or the pack's ranking params should be checked in the pack workflow.
- Leftovers of template stripping: empty brackets "( )" where pronunciation/date templates were (e.g. the Marie Curie lead), a stray ",which" where a ref-cited clause was cut.
- Rebuild from a newer dump: same command; the dump date goes into the name and this card.

## Published
- 2026-10-13 02:30: https://huggingface.co/datasets/r4topunk/boar-packs/tree/main/topics/boar-simplewiki-en (sqlite + .sqlite.json + README + LICENSE + selftest.jsonl; root README "Wave 2" section, commit de2c38f5). Flag: user-selected only.
