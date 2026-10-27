# B: the ≤ 50 GB storage budget for the post author's example classes

Sonar · 2026-10-03 · non-blind sources only (engine `be-0cfd4a77-health13`, `shared-data`, `shared-models`, Sonar/Anvil notes, public web/HF/Kiwix/archive.org APIs). Nothing > 200 MB was downloaded. All sizes are decimal GB (1 GB = 1e9 B), the unit the bounty and `manifest.ts` (`STORAGE_BUDGET_BYTES = 50 * 1000 ** 3`) use.

Helper files in this directory: `B-title-ranks.py` and `B-title-ranks.txt`. They hold the pageview ranks of 37 the post author-class Wikipedia titles, computed from the builder's own `pageviews-en-20250815.tsv`, the same method as exp-04.

## 1. TL;DR

- **Storage is not the limit; relevance gating and latency are.** BOAR's whole catalog today, with every LLM and every pack installed, is **41.0 GB**. A sensible install (4B reader + full English Wikipedia + everything else) is **≈ 24.6 GB**. The 18.4 GB English Wikipedia pack is already built and hosted. But both arms that put a big pack in the kit were **NOT ADOPTED**, because keyword hits from the big pack displaced better sources (#6 top-100k: net +3 keys, gate FAIL; #6b and #17 also failed). So the budget below spends bytes on coverage that only pays once the big-pack gate or tiering works.
- **For the post author's classes, coverage needs the top-1M tier, not the top-100k.** Of 32 class-relevant Wikipedia titles, the number in each pageview tier is: top-100k **14/32**, top-300k **25/32**, top-1M **30/32**. Examples: Mozi rank 176k, Tourism in Japan 158k, Climate of Japan 172k, Etiquette in Japan 346k, ML-KEM 235k, SPHINCS+ 774k. The existing 15-shard pack (top-1M articles in full, leads for the rest) is the right content. It should be **re-sharded by popularity** (hot top-100k shard searched by BM25 on every question, long tail through title/redirect lookup + cascade) so that latency stays bounded.
- **The cheapest high-value additions are small structured and primary packs, ≈ 1.9 GB together:**
  - PQC + crypto-research pack (FIPS 203/204/205, NIST IR 8547, RFC 8391/8554, IACR/arXiv abstracts under CC0), ~0.5 GB;
  - Stack Exchange Q&A from 8 sites (crypto, ethereum, travel, expatriates, outdoors, philosophy, vegetarianism, quantumcomputing; 487,555 posts), ~0.75 GB;
  - curated public-domain primary texts (Legge's Chinese Classics, Gutenberg canon, Wikisource Mozi), ~0.45 GB;
  - country facts + visa matrix (Wikidata CC0, Wikipedia visa tables, last World Factbook, which is public domain), ~0.05 GB;
  - GeoNames cities500 gazetteer with elevation, ~0.1 GB;
  - Overture vegan/vegetarian-dedicated venues, ~0.05 GB.
- **Ship the global places tiles (0.98 GB, 3.49 M food/drink POIs, 51,840 tagged vegan) as one optional download.** Today they are per-tile on demand. the bounty post's test is "a city I happen to be in", so the data has to be on the phone before he gets there. Overture adds venues that OSM lacks in thin-OSM cities: +10 in Edmonton, +189 in Bien Hoa and +220 in Queens (exp-12).
- **Recommended allocation (scenario S1): ≈ 24.6 GB, leaving ≈ 25 GB of headroom.** The headroom is reserved for the deep tier (Qwen3.6-35B-A3B UD-Q2_K_XL, 12.29 GB; sonar exp-16 Δ +0.060, CI +0.023…+0.096 on desktop) plus a speed hedge (Maple 5.90 GB). With both added (scenario S2), the total is ≈ 45.8 GB.

| S1 allocation | GB | status |
|---|---|---|
| APK | 0.12 | shipped (v1.0.0, 123 MB) |
| Qwen3-4B-Instruct-2507 Q4_K_M (reader) | 2.50 | shipped default |
| bge-small-en-v1.5 Q8_0 (embedder) | 0.04 | shipped, required |
| Emergency detector (mmBERT-small v3b + head) | 0.10 | in eval (exp-30) |
| English Wikipedia, 15 shards (top-1M full + leads), **re-sharded by popularity** | 18.38 | built + hosted; not adopted (gate) |
| + lead vectors extended to the top 1M | 0.21 | ESTIMATE |
| Wikivoyage EN | 0.35 | shipped |
| Crypto pack (existing) | 0.04 | shipped |
| **+ PQC / crypto-research pack** | 0.50 | new, ESTIMATE |
| Preparedness | 0.02 | shipped |
| **+ GeoNames cities500 gazetteer** (replaces the 23 MB world-places) | 0.10 | new, ESTIMATE |
| Global POI tiles (all 8,374) | 0.98 | hosted (per tile today) |
| **+ Overture veg-dedicated supplement** | 0.05 | new, ESTIMATE |
| **+ Country facts + visa matrix** | 0.05 | new, ESTIMATE |
| **+ Stack Exchange Q&A (8 sites)** | 0.75 | new, ESTIMATE |
| **+ Primary texts** | 0.45 | new, ESTIMATE |
| **Total** | **≈ 24.6** | **headroom ≈ 25.4 GB** |

## 2. Current shipped footprint (measured / declared)

Sources:
- the catalog entries in engine `be-0cfd4a77-health13`: `src/models/manifest.ts`, `src/rag/wikiEnPacks.ts`, `cryptoPack.ts`, `preparedness.ts` and `poiRegions.ts`;
- local build manifests under `<workspace>/shared-data/**.sqlite.json`;
- `du` of `shared-models`.

| Asset | Bytes on disk | Source | License (declared) | Status |
|---|---|---|---|---|
| APK v1.0.0 arm64 | ~123 MB | `review/boar.md` (sha `de9e3156…`) | app code | shipped |
| Qwen3-4B-Instruct-2507 Q4_K_M | 2,497,281,120 | manifest.ts | Apache-2.0 | default reader |
| Qwen2.5-1.5B-Instruct Q4_K_M | 986,048,768 | manifest.ts | Apache-2.0 | compact reader |
| bge-small-en-v1.5 Q8_0 | 36,806,944 | manifest.ts | MIT | required |
| Phi-3.5-mini / Qwen2.5-7B / LFM2.5-8B-A1B / Gemma 4 E4B | 2.39 / 4.68 / 5.16 / 5.15 GB | manifest.ts | MIT / Apache-2.0 / LFM Open v1.0 / Apache-2.0 | optional |
| Emergency detector (mmBERT-small v3b q8 + head) | 101 MB + 1.6 MB | `du shared-models/emergency-detector` | MIT (mmBERT) | eval only |
| Corpus standard / full (JSON) | 0.6 MB / 2.5 MB | manifest.ts | CC BY-SA 4.0 | shipped tiers |
| wiki-vital5 (format 1, 50k leads + int8 chunk vectors) | 163,647,488 | manifest.ts | CC BY-SA 4.0 | "Encyclopedia" tier |
| **English Wikipedia, 15 format-2 shards** | **18,377,299,968** (catalog sum); 18.03 GB in the local manifests | wikiEnPacks.ts; `shared-data/packs/*.json` | CC BY-SA 4.0 (+GFDL, FineWiki) | hosted on HF `r4topunk/boar-packs`, not in a tier |
| Wikivoyage EN (34,002 guides) | 351,092,736 | wikiEnPacks.ts | CC BY-SA 4.0 | shipped |
| Crypto pack (3,141 docs) | 36,093,952 | cryptoPack.ts | CC0 / CC BY-SA / MIT / BIP licenses | shipped |
| Preparedness pack (1,754 docs) | 16,490,496 | preparedness.ts | CC BY-SA 4.0 + US public domain | shipped |
| World places gazetteer (GeoNames cities15000, 34,149 places + 8,374-tile index) | 22,962,176 | poiRegions.ts | CC BY 4.0 (GeoNames) | shipped with any places pack |
| 10 city POI packs (sample) | 17.9 MB total | poiRegions.ts | ODbL 1.0 + CC BY-SA 4.0 | shipped |
| Global POI tiles (8,374 × 1°, all hosted) | 980,279,296 total; 3,490,656 POIs, 51,840 vegan | `sqlite3 world-places-tiles.sqlite "select sum(size_bytes)…"` | ODbL 1.0 (© OSM contributors) + CC BY-SA | per-tile download |
| top-100k enwiki subset (eval build) | 2.54 GB | QUEUE.md / S1 memo | CC BY-SA 4.0 | eval only, not adopted |

Totals:
- default install (APK + 4B + embedder): **2.66 GB**;
- every catalog asset: **41.0 GB** (LLMs 20.87 + corpora 19.97 + embedder + APK).

Measured format-2 pack anatomy (15 enwiki manifests, summed):
- text 21.40 GB → pack 18.03 GB = **0.84× source text**;
- the FTS5 index is 9.31 GB (52%); the zstd text blocks are 6.45 GB (36%, a 3.3:1 compression); lead vectors 0.21 GB;
- 28.44 M chunks, 6.12 M articles.

Small packs run higher because the FTS index is a larger share:

| Pack | Text | Pack | Ratio |
|---|---|---|---|
| Wikivoyage | 282 MB | 351 MB | **1.25×** |
| Crypto | 31.4 MB | 36.1 MB | **1.15×** |

**Planning factor for new packs: 0.85× plain text for Wikipedia-like corpora, 1.15–1.25× for small or listing-heavy ones.**

Against Kiwix: the Wikivoyage pack is 1.35× `wikivoyage_en_all_nopic_2026-09.zim` (260 MB). The 18 GB enwiki pack is 0.37× `wikipedia_en_all_nopic` (49 GB), because nopic ZIMs carry HTML and references. So ZIM sizes are upper bounds only.

int8 384-d bge-small vectors cost **≈ 410 B each on disk**: Wikivoyage `lead_vecs` is 13.96 MB for 34,002 rows.
- Vectors for every enwiki chunk would need 28.44 M × 410 B ≈ **11.7 GB**, so don't add them. Binary vectors (48 B/chunk, sqlite-vec) would be ≈ 1.4 GB, but need a new runtime.
- Lead vectors for the top 1M articles cost ≈ 0.41 GB (0.21 GB today).

## 3. Candidate additions

Exchange rate used for "expected gain": ≈ +0.003 judge ratio per net bench item whose answer key enters the prompt (1.5B, exp-10). Keys in prompt are the primary metric. the post author-class title ranks come from `B-title-ranks.txt`.

| # | Name | Answers (class) | Size on disk (raw → pack) | License | Build cost / time | Retrieval needs | Expected gain (evidence) |
|---|---|---|---|---|---|---|---|
| 1 | **Full EN Wikipedia, 15 shards (top-1M full + leads)**: already built | all classes; Mozi, PQC, Japan, travel | FineWiki EN 37.72 GB parquet ([HF API](https://huggingface.co/datasets/HuggingFaceFW/finewiki), 15 files) → **18.38 GB** (measured) | [CC BY-SA 4.0 + GFDL](https://huggingface.co/datasets/HuggingFaceFW/finewiki) | done: ~2.7 h on the Mac mini (`run-en-shards.log` 19:00 → 21:43), 37.7 GB streamed | FTS5 included; lead vecs 0.21 GB → 0.41 GB for the top 1M | **HIGH, conditional.** Key present in the full article on 26/39 bench items vs 11/39 in intros (exp-03); 19/21 misses are coverage (exp-06); class titles in the top 1M: 30/32. But top-100k v1 netted only +3 keys and failed the gate (QUEUE #6). Gain needs a relevance gate or tiering |
| 2 | **Popularity re-shard of #1** (tier 0 = top-100k, tier 1 = 100k–1M, tier 2 = leads) | same; latency | same bytes (≈ 2.5 / 12.7 / 3.2 GB; ESTIMATE from exp-04's curve) | same | ~3 h (rerun builder with `--full-top`/`--drop-rest` bands) | BM25 on tier 0 always; tiers 1–2 by title/redirect lookup (2 ms) or cascade | **enabler.** One ~2.1 M-chunk pack adds +85 ms p50 desktop (exp-13). All 28.4 M chunks ≈ +1.1 s desktop p50 by linear extrapolation (ESTIMATE), and more on a phone |
| 3 | Top-300k-only pack (lean alternative to #1) | same, minus the long tail | **7.25 GB** (exp-04 ESTIMATE) | CC BY-SA 4.0 | ~3 h + the 1-line `--drop-rest` builder flag | as #1 | class titles 25/32 vs 30/32 for #1 |
| 4 | **PQC + crypto-research pack** | quantum-resistant signatures, Ethereum research | <ul><li>FIPS [203](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf) / 204 / 205 PDFs: 1.25 / 3.29 / 1.06 MB (HEAD)</li><li>NIST IR 8547, SP 800-208, RFC 8391/8554 (a few MB)</li><li>IACR ePrint abstracts (~30k)</li><li>arXiv cs.CR + quant-ph abstracts (~250k of the 3,182,867-row [snapshot](https://huggingface.co/datasets/librarian-bots/arxiv-metadata-snapshot))</li><li>CC BY ePrint full texts, PQC subset</li></ul>→ **~0.5 GB** (ESTIMATE) | <ul><li>NIST: US government work ([nist.gov/oism/copyrights](https://www.nist.gov/oism/copyrights))</li><li>RFCs: [IETF Trust](https://trustee.ietf.org/documents/trust-legal-provisions/)</li><li>arXiv metadata: **CC0** ([ToU](https://info.arxiv.org/help/api/tou.html)); arXiv full text **not** redistributable by default</li><li>ePrint metadata CC0, papers per-paper ([eprint.iacr.org/rss](https://eprint.iacr.org/rss))</li></ul> | ~1 day (fetch, PDF→text, chunk); build seconds (crypto pack built in 3 s) | ~0.3 M chunks; per-chunk vecs ≈ 0.12 GB optional | **MEDIUM (ESTIMATE).** The existing crypto pack already holds the Wikipedia PQC layer: ML-KEM, SPHINCS+, Falcon, Lamport, Hash-based cryptography, Learning with errors, NIST PQC Standardization, plus EIP-8051/8052/7619 (titles queried 2026-10-03). The gap is primary parameters and research. Bench body-only crypto items: vit-cry-006/010/011 (exp-03) |
| 5 | **Stack Exchange Q&A, 8 sites** (crypto, ethereum, travel, expatriates, outdoors, philosophy, vegetarianism, quantumcomputing) | crypto "explain", visas/customs practicals, "explain X's views", vegan | 192,879 Q + 294,676 A ([SE API](https://api.stackexchange.com/2.3/info?site=travel)); 7z dumps 576 MB ([archive.org/stackexchange](https://archive.org/details/stackexchange), 2024-04) → **~0.75 GB** (ESTIMATE ~1.3 kB/post × 1.15) | [CC BY-SA 4.0](https://stackoverflow.com/help/licensing) (3.0 for pre-2018 posts) | ~0.5 day (XML → text, score filter, per-post attribution) | FTS; vectors 0.2 GB optional | **MEDIUM (ESTIMATE)**: not measured on any bench item |
| 6 | **Primary-texts pack**: Legge's *Chinese Classics* (PG [#3100](https://www.gutenberg.org/ebooks/3100), [#4094](https://www.gutenberg.org/ebooks/4094)), Wikisource *Mozi* (community translation), ~1k Gutenberg classics | Mozi/humanities "explain X's views" with quotes | ~0.4 GB text → **~0.45 GB** (ESTIMATE) | PG: US public domain ([PG license](https://www.gutenberg.org/policy/license.html)); Wikisource CC BY-SA; Mei's 1929 Mozi translation is **`pdus` (US-only PD)** per [HathiTrust](https://catalog.hathitrust.org/Record/001379764) | ~1 day (sonar card `primary-texts-pack`) | FTS + chapter titles | **LOW on the bench** (+0.006 by the exchange rate, card). Higher for the "what did Mozi actually say" style. #1 already holds Mozi (176k), Mohism (98k), Mencius (135k), Mozi (book) (792k) in full |
| 7 | **Country facts + visa matrix**: Wikidata facts per country (capital, currency, plug type/voltage, driving side, calling code, time zones, languages); visa tables parsed from the ~199 "Visa requirements for X citizens" articles; last World Factbook | "tell me about Japan", visas, customs | Factbook archive ZIM 388 MB with images ([Kiwix](https://download.kiwix.org/zim/other/)); [factbook.json](https://github.com/factbook/factbook.json) repo 69 MB → **~0.05 GB** (ESTIMATE) | [Wikidata CC0](https://www.wikidata.org/wiki/Wikidata:Licensing); Wikipedia CC BY-SA; Factbook = US gov work, **discontinued 2026-02-04** ([Wikipedia](https://en.wikipedia.org/wiki/The_World_Factbook)) so it is frozen | ~1 day (SPARQL + wikitext table parser) | structured lookup, no vectors | **MEDIUM-HIGH (ESTIMATE)**: deterministic answers to the parts of travel questions a 4B gets wrong from memory. Visa articles rank 19k (US) to 139k (Brazil) |
| 8 | **GeoNames cities500 gazetteer** (with elevation/DEM) | vegan "near me" in small towns; altitude | cities500.zip 13.9 MB vs cities15000.zip 3.36 MB today ([HEAD](https://download.geonames.org/export/dump/)) → **~0.1 GB** (ESTIMATE, scaled from 23 MB today) | [CC BY 4.0](https://www.geonames.org/export/) (already used) | hours | name index | **MEDIUM (ESTIMATE)**: towns ≥ 500 people resolve; altitude answers from the `elevation`/`dem` fields |
| 9 | **Global POI tiles, all at once** | vegan restaurants near me | **0.98 GB** (measured, 3.49 M POIs, 51,840 vegan) | [ODbL 1.0](https://www.openstreetmap.org/copyright) + CC BY-SA | done (~1.3 days wall, `geofabrik/*.log` Sep 26–28) | spatial + FTS in the tile | **HIGH for the class**. OSM-wide: diet:vegan = yes 47,850 / only 3,911 / limited 1,307 ([taginfo](https://taginfo.openstreetmap.org/keys/diet%3Avegan), 2026-10-03) |
| 10 | **Overture veg/vegan-dedicated supplement** | vegan restaurants near me (thin-OSM cities) | Overture places 11.0 GB parquet, 16 files (S3 listing, release 2026-09-23.1); veg-dedicated subset **~0.05 GB** (ESTIMATE, ~1% of restaurant rows per exp-12). A full global eat-and-drink layer would be ~3–4 GB (ESTIMATE) | CDLA-Permissive-2.0 / Apache-2.0 / CC0 per source ([attribution](https://docs.overturemaps.org/attribution/)) | ~4–6 h (card) | joins the tiles | **MEDIUM-HIGH**: +10 / +189 / +220 veg venues not in OSM (Edmonton / Bien Hoa / Queens); ~60% precision in Edmonton (exp-12) |
| 11 | PT Wikipedia (format 2) | PT questions (not the post author) | FineWiki PT 4.59 GB parquet → **~2.2–2.8 GB** (ESTIMATE, 0.48–0.6×) | CC BY-SA 4.0 + GFDL | ~1 h | as #1 | LOW for the post author; PT recall is parked (S1 memo) |
| 12 | Wikibooks EN | explanation/textbooks | Kiwix nopic 3.3 GB → **~1.3 GB** (ESTIMATE, 0.4× ZIM) | CC BY-SA | ~0.5 day (ZIM → text; libzim is GPL, build-time only) | FTS | LOW (ESTIMATE) |
| 13 | Reader/tier models | all (synthesis, reasoning) | Qwen3.6-35B-A3B UD-Q2_K_XL **12.29 GB**; Maple 20B-A1B **5.90 GB**; Gemma 4 E4B 5.15; Qwen3-4B Q5_K_M 2.89 / Q6_K 3.31 (SHELF) | Apache-2.0 / MIT / Apache-2.0 | download only; deep tier needs 1–2 weeks of engine work (Anvil) | — | deep35: Δ **+0.060** (CI +0.023…+0.096), +0.069 on out-of-kit items (sonar exp-16 `result-final-aligned.txt`, desktop). Maple: ties the 4B, CW 4 vs 7 |
| 14 | bge-reranker-v2-m3 Q4_K_M (relevance gate for big packs) | all, via precision | **0.44 GB** ([SHELF](https://huggingface.co/gpustack/bge-reranker-v2-m3-GGUF)) | Apache-2.0 | none | 182 ms/pair on M1 | AUC 0.912 vs cosine 0.773 on prompt passages (OSS scan, exp-25); the missing piece behind #1's gate failures |
| ✗ | Stanford Encyclopedia of Philosophy | Mozi/humanities | — | **No redistribution** beyond the user's own devices / ≤ 30 people ([SEP info](https://plato.stanford.edu/info.html)) | — | — | **rejected (license)** |
| ✗ | ethresear.ch | Ethereum research | — | **CC BY-NC-SA 3.0** ([ToS](https://ethresear.ch/tos)) | — | — | rejected by default (NC vs a prize bounty) |
| ✗ | the post author's blog (`vbuterin/blog`) | Ethereum/humanities | — | **no license** (GitHub API `license: null`, 2026-10-03) | — | — | rejected (link only) |
| ✗ | WorldClim climate normals | seasons | 10′ tavg 37 MB + prec 7 MB (HEAD) | **"Redistribution or commercial use is not allowed without prior permission"** ([about](https://www.worldclim.org/about.html)) | — | — | rejected (license) |
| ✗ | Wiktionary EN / Gutenberg full / Wikisource EN full | — | 8.5 GB / 206 GB / 3.6 GB ZIMs ([Kiwix](https://download.kiwix.org/zim/)) | CC BY-SA / PD / CC BY-SA | — | — | rejected (size vs gain; curated subsets are #6) |
| ✗ | passport-index visa CSV | visas | small | MIT claimed over scraped passportindex.org data; **archived, last updated 2025-01-12** ([repo](https://github.com/ilyankou/passport-index-dataset)) | — | — | cross-check only (stale, rights unclear) |

Note on a class signal outside the five: `a competitor repo`, branch `vector-search`, ships a **1.57 GB** "world-knowledge-biology" int8 vector pack (git LFS pointer, `size 1567877980`, commit 2026-09-24). Biology and longevity matter to the judge too. Wikipedia's medicine and molcell articles are inside #1; no extra pack is proposed here (UNKNOWN value).

## 4. Budget scenarios (each ≤ 50 GB)

| Item | S1: 12 GB phone, fast tier, full knowledge (recommended) | S2: 12 GB phone, max (deep tier + hedge) | S3: lean first-run (≤ 12 GB download) |
|---|---|---|---|
| APK | 0.12 | 0.12 | 0.12 |
| Reader | Qwen3-4B Q4_K_M 2.50 | Qwen3-4B 2.50 + **Maple 5.90** | Qwen3-4B 2.50 |
| Deep tier | — | **Qwen3.6-35B-A3B UD-Q2_K_XL 12.29** | — |
| Embedder + detector + reranker | 0.04 + 0.10 | 0.04 + 0.10 + **0.44** | 0.04 + 0.10 |
| English Wikipedia | 18.38 (re-sharded) + 0.21 lead vecs | 18.38 + 0.21 | **top-300k only 7.25** |
| Wikivoyage | 0.35 | 0.35 | 0.35 |
| Crypto + PQC/research | 0.04 + 0.50 | 0.04 + 0.50 | 0.04 + 0.50 |
| Preparedness | 0.02 | 0.02 | 0.02 |
| Gazetteer (cities500) | 0.10 | 0.10 | 0.10 |
| POI tiles | global 0.98 | global 0.98 | home region ~0.05 (rest on demand) |
| Overture veg | 0.05 | 0.05 | 0.05 |
| Country facts + visas | 0.05 | 0.05 | 0.05 |
| Stack Exchange Q&A | 0.75 | 0.75 | — |
| Primary texts | 0.45 | 0.45 | 0.45 |
| PT Wikipedia | — | 2.5 (ESTIMATE) | — |
| **Total** | **≈ 24.6 GB** | **≈ 45.8 GB** | **≈ 11.6 GB** |
| Headroom to 50 GB | 25.4 | 4.2 (drop PT → 6.7) | 38.4 |
| Class titles in full text (of 32) | 30 | 30 | 25 |

Reserve at least ~3 GB of headroom for runtime growth: the chat DB, logs and pack updates. Each pack downloads as its own SQLite file, so there is no unpack step and no 2× download peak (`packs.ts`).

## 5. Risks and UNKNOWN

Risks:
- **Share-alike (CC BY-SA 4.0).** Every pack built from Wikipedia, Wikivoyage, Wikibooks, Wikisource or Stack Exchange is an adaptation:
  - it must be distributed under CC BY-SA 4.0, with attribution and per-item URLs (format 2 already stores `url`/`license` per article);
  - CC BY-SA 3.0 Stack Exchange posts may be relicensed under 4.0 (a later version);
  - GFDL dual-licensing on FineWiki doesn't add duties if we use the CC side.
- **ODbL (OSM tiles).**
  - The tiles are a derivative database: they must stay ODbL, credit "© OpenStreetMap contributors", and offer the database or the method to recreate it (the public build scripts do).
  - Whether Overture records (CDLA-Permissive-2.0 / Apache / CC0) can share a tile with ODbL rows is open, as a collective work or a derivative (exp-12 card, Veil). The safe default is a separate `overture-veg` table or file with its own attribution.
- **SEP:** no redistribution, rejected. Same for the post author's blog (no license) and ethresear.ch (NC).
- **arXiv:** abstracts only (CC0), plus explicitly CC-licensed papers.
- **IACR ePrint:** per-paper license, so filter on it.
- **Gutenberg:** US public domain only, with non-US status per work UNKNOWN. The Mei 1929 Mozi is US-only PD (`pdus`), and Mei died in 1997, so it stays copyrighted in life+70 countries. Prefer Legge (d. 1897) and the Wikisource translation.
- **Stale or frozen sources:**
  - the World Factbook ended 2026-02-04;
  - the passport-index CSV was last updated 2025-01;
  - the Stack Exchange archive.org dump is from 2024-04, and SE's post-2024 dump terms are UNKNOWN;
  - FineWiki is the August 2025 snapshot.

  Answers must carry the snapshot date.
- **Download size.** S1 is ~24.6 GB: ~1.1 h at 50 Mbit/s, all from HF `r4topunk/boar-packs` (pinned commits, sha-checked). It must stay optional and tiered, with resumable per-file downloads, and it can't be part of the mandatory first-run setup (that stays 2.66 GB).
- **Build time on desktop:**
  - enwiki ~2.7 h on the mini, plus 37.7 GB streamed;
  - a popularity re-shard is ~3 h more;
  - the POI world build took ~1.3 days wall;
  - small packs take minutes to a day of curation each;
  - embedding 1M lead vectors: ≥ ~160/s observed (33k leads inside a 209 s shard build), so ≤ ~1.75 h.
- **Latency and noise from big packs (the real blocker).**
  - BM25 cost scales with chunk count: +85 ms p50 desktop per ~2.1 M chunks (exp-13). The 28.4 M-chunk pack would be roughly +1.1 s desktop if searched whole (ESTIMATE), and several seconds on a phone.
  - Three big-pack arms failed on displacement (#6, #6b, #17).
  - Mitigations: popularity tiers, title/redirect-first lookup for named entities (exactly the post author's "Mozi", "Japan", "SPHINCS+" style), and a cross-encoder gate.
- **FTS index share.** 52% of every pack is FTS5. FTS5 `detail=column`/`detail=none` could shrink it but would lose phrase queries. That saving is UNKNOWN, but it is the biggest lever if the budget ever binds.

UNKNOWN:
- Phone latency and RAM with 15+ open pack connections and tiered search (never measured on device).
- Whether the 4B turns more body text into better answers. E1(a): vital5 adds 0.000 on the 4B. The top-1M arm on Android has never been scored.
- Exact sizes for #4, #5, #6, #7, #8 and #10 (all ESTIMATE from post counts, file sizes or ratios). Measure on the first build.
- Global count and precision of Overture `vegan_restaurant` / `vegetarian_restaurant` (3 tiles measured).
- Whether FineWiki's text keeps Wikipedia's climate and visa tables. If not, #7 needs the wikitext parser (planned).
- A redistributable global climate-normals source (WorldClim rejected; NOAA 1991–2020 normals not checked).
- The Internet Encyclopedia of Philosophy's terms (not checked).
- Legal reviews (Veil): the OSM + Overture mix; NC sources under a prize bounty; SE's newer dump terms; Gutenberg outside the US.
- Pack-to-source ratio for PT/ES Wikipedia (0.48–0.6× parquet assumed).
- Whether `a competitor repo`'s biology emphasis implies a judged class BOAR should cover beyond Wikipedia.
