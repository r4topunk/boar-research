# boar-firstaid-en (First aid and emergency preparedness (v4))
TL;DR: reproducible rebuild of boar-preparedness (v3: the same 1,754 docs) plus the 88 sections of ATP 4-02.11 (US Army casualty care / first aid, March 2026); 1,842 articles, 21 MB; built 2026-10-12 (T-K3) with a recorded command; NOT in any kit; coverage/crowding pending T-K4; self-test scored 2026-10-13.

## What it is
- Sources (articles per `articles.source`): enwiki 902, enwikivoyage 8, enwikibooks 71, appropedia 567, usgov 294 (FM 21-76 24 + US federal works 182 + ATP 4-02.11 sections 88).
- Inputs: `shared-data/preparedness-v2/{appropedia.kept,army-manual,usgov,wikibooks,wikipedia,wikivoyage}.jsonl` (the v3 doc set, see boar-preparedness.md) + `shared-data/packs/work/atp-4-02-11/atp-4-02-11.jsonl` (convert.mjs pdf, T-K1; PDF archive.org, 12,665,561 B, sha256 a4a0650f…6542). Manifest = preparedness-v2/manifest.json (1,754) + atp manifest (88) concatenated.
- Licences (article_meta): CC BY-SA 4.0 1,548; "Public domain (US Army FM 21-76, 1992)" 24; "Public domain (US federal government work, 17 U.S.C. §105)" 182; "US government work (17 U.S.C. §105), public release" 88 (ATP). CC BY-SA rows are share-alike.
- Attribution column present; filled on the 88 ATP rows ("Army Techniques Publication for Casualty Response, Tactical Combat Casualty Care, and First Aid, ATP 4-02.11, 2026-03-23; <archive.org url>"), empty on the v3 rows (their url + licence already credit them).
- Example citation (engine, query "how to treat a snake bite", 2nd hit): `US government — https://archive.org/details/army-techniques-publication-for-casualty-response-tactical-combat-casualty-care- (US government work (17 U.S.C. §105), public release) — Army Techniques Publication for Casualty Response, …, ATP 4-02.11, 2026-03-23; <same url>` (section "First Aid For A Snakebite").
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da…f514. Params: leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, fullTop 1000000, embedTop 0.
- Counts: articles 1,842; chunks 22,500; indexed 22,497 (99.99 %); lead_vecs 1,842; redirects 0; views 0.
- Size: 20,987,904 B (20.0 MiB). sha256 8cfab0b47ec8c5cb32840b24df1054c4df1a08d600d063c95c022c58eb5bf558.
- meta keys: format, formatVersion, dims, embeddingModelSha256, sources, license, manifestSha256, name, articles, chunks, indexedChunks, dfMin, params, builtAt.
## Kit entry and build
- Not in any kit. Kit entry would be {"id":"boar-firstaid-en","sha256":"8cfab0b4…"}. Supersedes boar-preparedness (v3, sha 53d8bcef…) as the reproducible build; v3's PT aliases (meta aliases_pt 729, add-langlink-aliases step) are NOT in v4 (English only, by the task's scope).
- Build (build host, Apple M4, wall 10 s; scripts in rnd/runner/packs/wave1-scripts/):
  ```sh
  P=$RUNNER_ROOT/runner/packs/work/preparedness-v2
  bash scripts/build.sh boar-firstaid-en "First aid and emergency preparedness (v4)" work/boar-firstaid-en/manifest.json \
    $P/appropedia.kept.jsonl $P/army-manual.jsonl $P/usgov.jsonl $P/wikibooks.jsonl $P/wikipedia.jsonl $P/wikivoyage.jsonl work/atp-4-02-11/atp-4-02-11.jsonl
  ```
## Measured coverage
- V-para 34 absent items: verified 0/34, >=0.7 0, >=0.6 0 (coverage probe 2026-10-12: jev fact-in-text over 20 candidate chunks per item, deep-tier run s42).
- pending T-K4 (v3 measured: V-para 0/51, v0.2 8/110; ATP adds clinical first-aid steps).
## Crowding
- T-K4a (2026-10-12, arms/packs/T-K4a.md): share v0.2 0.101 / v0.1 0.060, mostly health/danger items, gold unchanged → **default-eligible**; retrieval p50 +133 ms (v0.2) / +77 ms (v0.1).
## Quality
- Self-test score (2026-10-13; the 20 public self-test questions written from this pack's text; Haiku 5.5-low L1 judge, both answer orders; 4B claim build; dev): with pack raw **0.47** (0.41–0.53), above_min 0.32 / without pack raw **0.47** (0.42–0.52), above_min 0.32; paired Δ +0.004 raw (95 % CI -0.027…+0.036), +0.006 above_min; items better/worse with the pack 8/9; win/tie/loss vs the gold answer 0/0/20. Pack passages kept on 3/20 items (3/16 kept passages); the fact's source article kept on 0/20. Gold answers are agent-written from the same text: a development check, not comparable with benchmark numbers.
- Self-test, deep tier (Qwen3.6-35B-A3B + thinking 512, desktop, Haiku 5.5-low N=4 both orders, 2026-10-13): with pack 0.479 vs without 0.466, Δ +0.013 (−0.028…+0.051); deep with pack vs 4B with pack +0.007 (−0.022…+0.039); pack passages kept on 3/20 items; win 0/20. Dev numbers, agent-written gold; first-aid items take the health-strict path (no deep prompt), so this is not a deep-tier measurement.
## Category gaps
- Still no MedlinePlus first-aid topics, ready.gov/FEMA refresh, USGS/NOAA or FM 21-76 re-split from the catalogue row (wave 1 kept the v3 doc set + ATP only); Wikipedia half (902) is general background; no non-English content.
## Curation notes
- ATP sections are PDF-split (heuristic; tables as " · "-joined lines, hyphenated line ends not rejoined); all ATP rows share one URL (the archive.org item).
- Safety content keeps the "AI-reviewed, not clinically reviewed" caveat; TCCC material is written for military medics — a self-test should check that lay steps are retrieved first.

## Published
- 2026-10-13 00:01: https://huggingface.co/datasets/r4topunk/boar-packs/tree/main/topics/boar-firstaid-en (sqlite + .sqlite.json + README + LICENSE + selftest.jsonl; root README "Wave 1" section, commit 103f7bfa).
