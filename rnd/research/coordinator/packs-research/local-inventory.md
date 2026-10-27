# Local inventory for the pack catalogue (2026-10-12, read-only)
Sources: `du -sh`/`ls`/`wc -l` on MacBook `shared-data/` and mini `<runner>/shared-data/`; manifests `*.sqlite.json`; `rnd/research/packs/*.md`; HF API `tree/main/<dir>`; code at `wt/packcond` (979187fa). Blind/veil not touched; no item text read.

## TL;DR
- **Zero-download builds today:** (a) Appropedia remainder: 2,903 docs fetched, only 567 kept in preparedness (`preparedness/appropedia.jsonl`, CC BY-SA 4.0); (b) any re-cut of the crypto sources (9 sparse git clones, 287 MB; ethereum.org has 8,527 files, 228 pages used); (c) Wikivoyage variants from the local dump; (d) Wikipedia subsets of **shard 07 only** (FineWiki parquet 000_00007, 2.5 GB, 436,482 rows) or of the top-100k pack (98,389 full articles, on both machines); (e) GeoNames gazetteer and the 8,374 food/drink OSM tiles (already built).
- **Needs a download:** other 14 FineWiki shards (deleted after build; 15 shard packs are on HF, 18.03 GB), any OSM category beyond food/drink (extracts were osmium-filtered), any new domain corpus (Stack Exchange, health, how-to).
- **The one missing converter:** a generic *local corpus → builder JSONL + manifest.json* script (the only converters, `fetch-crypto.mjs`/`fetch-preparedness.mjs`, are domain-specific and fetch over the network; nothing turns an existing pack/parquet + title list into JSONL either). A new domain also needs a new `source` code in two places (builder `SOURCE`, app `wikiPack.ts SOURCES`).

## 1 Sources (raw material on disk)
| Path (MacBook `shared-data/` unless noted) | Size / files | Format | Snapshot | Licence | Used by |
|---|---|---|---|---|---|
| `finewiki/000_00007.parquet` | 2.3 GB / 1 (436,482 rows, sample-build.log) | FineWiki parquet (page_id, title, text, infoboxes) | enwiki Aug 2025, HF HuggingFaceFW/finewiki @8bd13e72 (`knowledge-build/en-shard.sh`) | CC BY-SA 4.0 | shard 07 pack; other 14 shards deleted after build (`rm -f` in en-shard.sh); mini `finewiki/` empty |
| `dumps/enwiki-latest-redirect.sql.gz` | 187 MB | MySQL dump | fetched 2026-09-26 (≈13 months newer than FineWiki) | CC BY-SA 4.0 | `--redirects` (12,417,761 rows) |
| `dumps/enwiki-latest-pages-articles-multistream-index.txt.bz2` | 284 MB | id:title index | 2026-09-26 | CC BY-SA 4.0 | `--index` (with --redirects) |
| `dumps/enwikivoyage-latest-pages-articles.xml.bz2` | 131 MB | MediaWiki XML | 2026-09-26 | CC BY-SA 4.0 | `--wikivoyage`; POI Eat/Drink listings |
| `dumps/pageviews-en-20250815.tsv` | 69 MB (6,248,683 pages) | page_id TAB views, 1 day | 2025-08-15 | CC0 (Wikimedia pageviews; UNKNOWN in local files) | `--pageviews --pageview-days 1` |
| mini `<runner>/shared-data/dumps/` | 640 MB / 4 | same 4 files | same | same | mirror |
| `gate-ref/boar-wiki-en-07.sqlite` | 1.1 GB / 1 | built pack (= shard 07, sha 2455c805) | Aug 2025 | CC BY-SA 4.0 | WIKIFULL A0 |
| `preparedness/` (v1 raw) | 80 MB / 22 | JSONL shards + manifest | fetched 2026-09-26 (`fetch.log`) | CC BY-SA 4.0 (wiki, Appropedia), US PD (17 U.S.C. §105) | `appropedia.jsonl` 2,903 docs raw (31.6 MB) vs `.kept` 567 |
| `preparedness-v2/` | 50 MB / 15 | JSONL: appropedia.kept 567, army-manual 24, usgov 182, wikibooks 71, wikipedia 902, wikivoyage 8 (`wc -l`) + manifest | 2026-09-26/27 | as above; FM 21-76 (1992) PD | v3 pack (no v3 build log) |
| `preparedness-v3/` | 35 MB / 3 | built packs + `pack-manifest.json` (1,754 docs {source,title,url,license}) | 2026-09-27 | as above | published pack |
| `crypto/src/` | 287 MB / 10,916 | sparse git clones: EIPs (958 f, 2026-09-24), ERCs (618), bips (214), consensus-specs (102), execution-specs (102), execution-apis (7), portal-network-specs (32), yellowpaper (4, 2025-02-04), ethereum-org-website (8,527, 250 MB) | last commits 2026-09-14…25 (`git log -1`) | CC0 (EIPs/ERCs/specs), MIT (ethereum.org), CC BY-SA 4.0 (Yellow Paper), per-BIP (33 BIPs without licence excluded) | crypto pack |
| `crypto/build/` | 34 MB / 12 | JSONL: eips 1,208, bips 180, specs 156, ethereumorg 228, wikipedia 1,369 + manifest + relevance report | 2026-09-26 | as above | crypto pack |
| `lexicon/` | 20 MB / 20 | PT→EN title aliases (57,159 titles, langlinks) | 2026-09-27 | CC BY-SA 4.0 | PT aliases only; English-only bounty: not a pack source |
| `poi/cities15000.txt`, `countryInfo.txt`, `admin1CodesASCII.txt` | 8.1 MB | GeoNames TSV | ≈2026-09-26 | CC BY 4.0 | `build-places-pack.mjs` |
| `poi/geofabrik/work/extracts/` | 316 MB / ≈504 `*.jsonl.gz` (pipeline log: 420 extracts) | osmium-filtered **food and drink only** | OSM 2026-09-25…27 | ODbL 1.0 | world tiles |
| `poi/geofabrik/work/tiles/` | 970 MB / 8,374 tiles + json | boar-poi-pack v1 | as above | ODbL + CC BY-SA (Wikivoyage) | HF `places/tiles` |
| `poi/osm-*.json`, `q-*.overpass` | ≈ 30 MB / 12 | Overpass JSON (6 cities) | 2026-09-26 | ODbL 1.0 | city packs |
| `humansft-raw/{clapnq,dolly,hagrid}` | 29 MB / 4 JSONL | QA/SFT datasets | ≤2026-10-07 | UNKNOWN locally (no README/licence file) | fine-tune DATA line (closed); not pack material |
| mini `<runner>/knowledge-build/` | 317 MB | builder scripts copy + per-shard logs (en-00…14, voyage, prep-v2/v3, crypto-rd) | 2026-09-26/27 | — | build provenance |

## 2 Packs (built)
| id | fmt | articles / chunks (indexed %) | size B | sha256 (16) | licence | where | in shipped kit? |
|---|---|---|---|---|---|---|---|
| boar-crypto | 2 | 3,141 / 54,998 (97.6) | 36,093,952 | ae9fbd2c7a46a46a | mixed CC0/MIT/BSD/CC BY-SA, per doc `article_meta` | MB, mini, HF `topics/` | **IN** `config.kit[0]` |
| boar-wikivoyage-en | 2 | 34,002 / 548,051 (99.99) | 351,092,736 | ff8595e32f56b8b8 | CC BY-SA 4.0 | MB, mini, HF `wiki/en/` | **IN** `config.kit[1]` |
| world-places + 4 tiles (kit-vexact) / +5 (kit-vgps2) | places/poi v1 | 34,149 places, 366,144 names; 93.5k POIs | 22,962,176 + 16.0 MB (+3.65 MB) | 215ce4663b2f79db | CC BY 4.0 + ODbL + CC BY-SA | MB `poi/kit-*`, mini `poi/kit-vexact`, HF `places/` | IN via `--places` (not config.kit) |
| boar-preparedness (v3) | 2 | 1,754 / 21,691 (99.99) | 16,490,496 | 53d8bcefd8ac6564 | CC BY-SA 4.0 + US PD | MB `preparedness-v3`, mini `packs/`, HF `topics/` | no (in app catalogue) |
| wiki-vital5 | **1** | 49,832 / 115,813 | 163,647,488 | d3b87d562baba348 | CC BY-SA 4.0 | MB `packs/`, mini `packs/pinned/` (not on HF; app tier "encyclopedia") | no (VITALADD NO) |
| boar-wiki-en-top100k | 2 | 98,389 / 4,019,506 (80.5) | 2,542,215,168 | 9123b3720abd8472 | CC BY-SA 4.0 | MB + mini `packs/` (not on HF) | no (DEEPWIKI NO) |
| boar-wiki-en-00…14 | 2 | 6,124,620 total (HF README); e.g. 07: 403,973 / 1,913,583 (82.7) | 1.14–1.28 GB each, 18.03 GB total | per `packs/boar-wiki-en-NN.sqlite.json` | CC BY-SA 4.0 | **HF `wiki/en/` only** (+ 07 in `gate-ref/`); manifests on MB | no |
| boar-wiki-sample | 2 | 437,975 (shard 07 + Wikivoyage 34,002) / 2,462,151 | 1,558,347,776 | f03ee5f322fbeeec | CC BY-SA 4.0 | MB `packs/` | no (build-test artefact) |
| city POI packs (10) | poi v1 | e.g. Queens 19,963 places | 37 KB–4.3 MB | HF tree | ODbL + CC BY-SA | HF `places/cities/`, MB `poi/packs`, `poi/drawn` | no |
| old/experimental | — | crypto OLD-b309ba9, preparedness v1/v2, `-en`, `-pt.EXPERIMENT` | — | rejected by catalogue hash | — | MB, mini | do not install (READMEs) |
- Kit source: `boar-eval/adapters/desktop-node/configs/p2-iphone13-0cfd4a77.json` `.kit` = `[{id:"boar-crypto",sha256:ae9f…},{id:"boar-wikivoyage-en",sha256:ff85…}]`.
- Shared embedding model for all packs: bge-small-en-v1.5 q8_0, sha `ec38e8da…f514`, 384 dims (`packs/README.md`).
- HF dataset root: `places/`, `topics/`, `wiki/`, `README.md`; `places/tiles` returns 1,000 entries per page (index says 8,374).

## 3 Builders (`wt/packcond/scripts/`, Node ≥ 23.8 for zstd; MB v25.9.0, mini v25.8.1)
| Script | Input | Key flags / modes | Output | Measured runtime |
|---|---|---|---|---|
| `build-wiki-pack.mjs` (642 l.) | `--shards`: FineWiki parquet **or** `.jsonl` (whole file read into RAM); URLs auto-downloaded | `--pageviews --pageview-days --full-top N` (rest kept as `--lead-chars` 2500 lead); `--redirects`+`--index` together; `--wikivoyage XML.BZ2`; `--manifest` (topic packs); `--no-embed`, `--embed-only`, `--embed-top N`, `--embed-threads`; `--limit`, `--delete-shards`, `--work-dir`, `--min-free-gb`, `--wait-for-shards`; `--chunk-chars` 1000 (max ×1.5), `--block-kb` 64, `--zlevel` 12, `--no-optimize`, `--name` | format 2 SQLite + `<out>.json` summary (size, sha256, counts, table bytes, buildSeconds) | enwiki shard: text ≈ 194–294 s (`boar-wiki-en-NN.sqlite.json`), ≈ 8–18 min/shard with 33,334-lead embed (`run-en-shards.log`); Wikivoyage 111 s; preparedness v2 21 s; crypto text step seconds (`build.log`); top100k embed at 100k OOMed twice at 6 GB heap → 50k |
| `build-knowledge-pack.mjs` (254 l.) | MediaWiki API (online): Vital level 4/5 or `--titles file` | cached steps in `build/knowledge-pack/<id>/` | **format 1** (`chunks(id,title,body,source,scale,vec)` + `chunks_fts`); intro only | ~2–3 h for 50k (KNOWLEDGE_PACKS.md) |
| `build-places-pack.mjs` (65 l.) | `cities15000.txt countryInfo.txt out.sqlite [tiles/index.json]` | — | boar-places-pack v1 (meta, places, names, tiles) | — |
| `build-poi-pack.mjs` (69 l.) | `--osm` Overpass/osmium JSON, `--bbox`, `--tz`, `--voyage` + `--voyage-title`, `--places`, `--diet-check` | one region | boar-poi-pack v1 (grid + FTS on names/cuisine) | — |
| `build-poi-world.mjs` | Geofabrik `leaves.json`; osmium + curl | `extract` (food/drink only) → `tiles` → `index` | 1° tiles + `index.json` | 420 extracts, 2026-09-27/28 (`geofabrik/pipeline.log`) |
| `push-knowledge-pack.mjs` (46 l.) | a `.sqlite` named `[a-z0-9-]+.sqlite` | `--serial` | adb copy to `files/corpus/` of a debuggable build, sha check | — |
| converters | `fetch-crypto.mjs` (git clones + MediaWiki), `fetch-preparedness.mjs` (MediaWiki, Appropedia, ready.gov, NPS, archive.org), `filter-relevance.mjs` (jev yes/no per doc, cut 0.5, cost-capped) | — | JSONL shards + `manifest.json` | — |

**Format 2 tables** (builder header l.13–22): `meta(key,value)`, `blocks(id,zdata)` zstd text, `articles(id,source,page_id,title,views,block_id,off,len)`, `chunks(id,article_id,start,end)`, contentless FTS5 `fts(title,section,body)` porter+unicode61, `redirects(title,article_id)`, `df(term,doc)` (terms in ≥ 2,000 chunks), `lead_vecs(article_id,scale,vec int8)`, optional `article_meta(article_id,url,license)`. **Meta keys:** format=`boar-knowledge-pack`, formatVersion=2, dims=384, embeddingModelSha256, sources (JSON; per-source docs + licence counts when `--manifest`), license, manifestSha256, name, articles, chunks, indexedChunks, dfMin, params (fullTop, leadChars, chunkChars, blockKb, zlevel, limit, embedTop), builtAt.
**Limits:** chunks where > 50 % of lines start with `|` are stored but **not indexed** (`isTable`, wiki-pack-lib l.106): 19.5 % of top100k chunks, 17.3 % of shard 07, 2.4 % crypto; only lead vectors (no chunk vectors: DENSECHUNK); docs with text < 200 chars dropped; dedup by `page_id` across all shards of one build.

**Builder input JSONL (one doc per line; build-wiki-pack l.265–286):**
| field | type | req. | meaning |
|---|---|---|---|
| `page_id` | integer | yes | unique within the pack (dedup key). Convention: per-source ranges, e.g. EIPs 5,000,000,001…, BIPs 8,000,000,002…, usgov 4,0xx,xxx,xxx, FM 21-76 4,500,000,000 |
| `title` | string | yes | display title; a `# Title` heading is prepended |
| `text` | string | yes | ≥ 200 chars; Markdown-ish, `#`-headings become the FTS `section` path; paragraphs split on blank lines |
| `source` | string | no (default enwiki) | must be one of `enwiki, enwikivoyage, enwikibooks, appropedia, usgov, eips, ethspecs, ethereumorg, bips`, else the build throws |
| `url`, `license` | string | no | written to `article_meta` (shown next to answers) |
| `aliases` | string[] | no | extra titles into `redirects` (e.g. "ERC-20") |
| `views` | integer | no | used when no `--pageviews`; ranks lead embeddings with `--embed-top` |
| `infoboxes` | JSON string | no | FineWiki infobox array → "Key facts" lines (≤ 800 chars) |
Companion `manifest.json` for `--manifest`: array of `{source, title, url, license}` (+ `chars` in practice). A new domain: write JSONL + manifest, then `node scripts/build-wiki-pack.mjs --out <id>.sqlite --shards <dir>/*.jsonl --manifest <dir>/manifest.json --name "…"` (no pageviews ⇒ every doc full text, every lead embedded). New `source` names need edits in builder `SOURCE` and `src/rag/wikiPack.ts SOURCES` (unknown codes fall back to "enwiki" in the app, l.513; `LAY_SOURCES` changes ranking).

## 4 Catalogue and card format
- **Cards** (`rnd/research/packs/README.md` + 7 cards): index columns id, domain, articles/chunks, size, format, licence, built, v0.2 F0 (of 110), V-para F0 (of 51), kit status. Card sections: TL;DR; What it is (source + snapshot, licence from meta); Format (formatVersion, dims, model sha, params, counts, indexed %, size, sha256); Kit entry and build (`{id, sha256}`, command); Measured coverage; Measured quality effects; Known gaps; Community curation notes (card fields, 20-question curator self-test, share-alike licence line, per-pack share cap).
- **App catalogue:** `CatalogModel` (`src/models/manifest.ts` l.27): id, kind=`corpus`, format `json | sqlite-pack | poi-pack`, label, displayName, filename `corpus/<id>.sqlite`, sizeBytes, sha256, sourceUrl (HF pinned `resolve/<commit>/<path>`), license, description, required. `CORPUS_CATALOG` itself holds only corpus-standard, corpus-full, wiki-vital5 (3 entries); crypto, preparedness, wiki-en shards, Wikivoyage register through `registerAssetProvider` (`src/rag/cryptoPack.ts`, `preparedness.ts`, `wikiEnPacks.ts`) with per-source attribution lists. `TIERS` (minimum/standard/full/encyclopedia) pick `corpusPackIds`.
- **Checks on open** (`src/rag/packs.ts` l.95–125): catalogue packs must match `sizeBytes` exactly; meta.format must be `boar-knowledge-pack` and embeddingModelSha256 equal the app's (or empty for format 2); import matches by size then sha256 (`ModelManager.ts`). Any valid `*.sqlite` in `corpus/` is used as `local-<name>` with no size/sha check (pack:push path).
- **Community authoring** (`docs/KNOWLEDGE_PACKS.md`, 90 l.): build (`npm run pack:build`, format 1 only), push over USB, or upload publicly + add a `CORPUS_CATALOG` entry + tier id. Stale: does not describe format-2/`build-wiki-pack` topic packs or the asset-provider path.

## 5 Constraints from measured results
| Result | Line | Source |
|---|---|---|
| DEEPWIKI | top100k as peer: Δ −0.034 (−0.082…+0.003); pack fills 26/28 kept slots; retrieval ×2.6 → large packs need a quota | CLOSED.md #29; arms/deepwiki/DEEPWIKI.md |
| VITALPACK / VITALADD | vital5 as peer fails crowding gate (share 0.61 > 0.40); additive q=1: mechanism fires (60/110, 22/51) but NO at slice, not detected at MDE 0.025 | CLOSED.md #34; arms/vitalpack/VITALADD.md |
| DEEPNORAG | removing the curated kit −0.045 (−0.083…−0.011): packs add ≈ +0.045 | CLOSED.md #33 |
| PACKCOND P1 | in-pack floor-adj 0.55 (H, n=32) vs 0.39 uncovered; K 0.41 vs 0.29; selection, not causal | arms/packcond/PACKCOND-P1.md |
| PACKCOND P2 | union of all packs: V-para 10/51, v0.2 62/110 (27 from top100k) | arms/packcond/PACKCOND-P2.md |
| PACKDENSE | lead-level dense router: 5/15 misses reached; projected 21/32 < 22 → FAIL step 0 | arms/packcond/PACKDENSE.md, CLOSED.md #44 |
| DENSECHUNK | chunk vectors reach the fact chunk on 23/32 (cos ≥ 0.55), fused sim 22/32 = bar, fails resolvable-gold rule; cost +212.6 MB Wikivoyage (+61 %), +21.3 MB crypto; needs new engine path | arms/packcond/DENSECHUNK.md |
| SECTIONHIT | article kept 12/32, fact section kept 7/32; no passage-selection headroom (loss is article-level retrieval) | arms/packcond/SECTIONHIT.md |
| WIKISECTION | fact in enwiki body 2/13 V-para, 4/30 v0.2 (bar 40 %) | CLOSED.md #39 |
| WIKIFULL A0 | shard 07: V-para 1/34 (0 verified), v0.2 11/78 (9 verified); 1/15 shards, not a verdict; A/B need 16.9 + 25.8 GB download | arms/wikifull/A0-shard07.md; BACKLOG.md l.44, l.68 |

## 6 Gaps / UNKNOWN
- UNKNOWN: licence files for `humansft-raw/*` and the pageviews TSV (none on disk).
- UNKNOWN: preparedness v3 build command/log (card: "not found"); `crypto/boar-crypto.sqlite.json` was regenerated 2026-10-12 (old one kept `.stale-9ac8ad1c`).
- Snapshot skew: FineWiki text Aug 2025 vs redirects/index/Wikivoyage 2026-09-26.
- No offline title-filter for parquet or pack→JSONL extractor: Wikipedia topic subsets currently need the MediaWiki API (online) or a new script.
- OSM extracts keep food/drink only; health/water/shelter POIs need a new Geofabrik run (download, ODbL).
- Only shard 07 parquet survives locally; full-Wikipedia work needs HF packs (18 GB) or re-download of 14 parquet shards.
- No pack has chunk-level vectors in format 2; table chunks unindexed.
- No per-pack self-test sets exist yet (cards: needs r4to, non-Claude author).
