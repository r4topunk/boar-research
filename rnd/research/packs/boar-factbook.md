# boar-factbook (CIA World Factbook, CC0 archive)
TL;DR: all 261 entries of the CIA World Factbook CC0 JSON archive (countries, territories, EU, oceans, World), one doc per entry with a one-chunk "Key facts:" block; 11.6 MB; built 2026-10-13 ; NOT in any kit; coverage and crowding measured 2026-10-13; self-test scored 2026-10-13 (see Quality).

## What it is
- Source: github.com/factbook/factbook.json, shallow clone of commit 144d6977b2b01ac1cbd220de754c0a005616760b (2026-09-11 15:19 +02:00), 261 `<region>/<code>.json` files (`meta/categories.json` not read). The CIA stopped publishing the Factbook on 2026-02-04 (VERIFIED.md), so this is a frozen snapshot. Most figures are "2024 est." / "2025 est."; the JSON has no per-field date.
- Licence: repo `LICENSE.md` = CC0 1.0 Universal (sha256 36ffd9dc…f39673, checked 2026-10-13). Meta and every row: "CC0 (CIA World Factbook archive, data as of 2026-09-11 (repo commit 144d6977))". Attribution on every row: "CIA World Factbook (US government work), via the factbook/factbook.json CC0 archive, snapshot 2026-09-11 (repo commit 144d6977)".
- Converter: `convert.mjs factbook` with these changes: (1) a `Time zone` key fact (from Government > Capital > time difference, "UTC+3"; 238/261 have one); (2) display-title overrides for 11 entries whose archive short form is unusable (DRC → Democratic Republic of the Congo, "The Dominican" → Dominican Republic, EE → European Union, "Gaza, Gaza Strip" → Gaza Strip, Svalbard's parenthetical, the US Pacific refuges list, and the oceans OO/XO/XQ/ZH/ZN → Southern/Indian/Arctic/Atlantic/Pacific Ocean); the old short form is kept as an alias unless it is a 2-letter code; (3) aliases with brackets dropped ("DRC (", "DROC)"). 15/15 converter unit tests pass.
- Doc shape: `Key facts:` (official name, capital, time zone, location, area, population, languages, religions, ethnic groups, government type, independence, currency, GDP, GDP per capita, life expectancy, climate, internet code; ≤ 1,348 chars, one chunk) + `## Background` + one `## <Category>` section per Factbook category (Geography, People and Society, Environment, Government, Economy, Energy, Communications, Transportation, Military and Security, Space, Terrorism, Transnational Issues), each field flattened as `Field (sub): text`.
- No telephone calling codes: this archive no longer carries the "Telecommunication systems" field (only internet country code).
- Example citation string (engine, query "what is the capital and population of Kenya"): `CIA World Factbook (archive) — https://github.com/factbook/factbook.json/blob/master/africa/ke.json (CC0 (CIA World Factbook archive, data as of 2026-09-11 (repo commit 144d6977))) — CIA World Factbook (US government work), via the factbook/factbook.json CC0 archive, snapshot 2026-09-11 (repo commit 144d6977)`.
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da…f514. Params: leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, fullTop 1000000, embedTop 0; dfMin 2000. `articles.source` = 11 (factbook) on every row.
- Counts: articles 261; chunks 10,543; indexed 10,543 (100 %); lead_vecs 261; redirects 774 (aliases: long/local/former names, abbreviations); article_meta 261 rows with attribution; views 0 (no popularity prior).
- Size: 11,624,448 B (11.1 MiB). sha256 c585435354a413d04790882c4e2263f725b1024c067febad3f2a99783e663447.
- meta keys: format, formatVersion, dims, embeddingModelSha256, sources, license, manifestSha256, name, articles, chunks, indexedChunks, dfMin, params, builtAt. name "CIA World Factbook (CC0 archive, data as of 2026-09-11)".
## Kit entry and build
- Not in any kit. Kit entry would be {"id":"boar-factbook","sha256":"c5854353…"}. Label "CIA World Factbook (archive)" needs the engine patch that adds the new source labels.
- Files: mini `<runner>/shared-data/packs/wave2/`; MacBook `shared-data/packs/wave2/`.
- Build (mini M4; convert 1 s, build wall 2 s; scripts in rnd/kiln/packs/wave2-scripts/):
  ```sh
  git clone --depth 1 https://github.com/factbook/factbook.json.git dl/factbook-src/factbook.json     # commit 144d6977
  node convert/convert.mjs factbook dl/factbook-src/factbook.json --out work/boar-factbook --snapshot "2026-09-11 (repo commit 144d6977)"
  bash scripts/build.sh boar-factbook "CIA World Factbook (CC0 archive, data as of 2026-09-11)" work/boar-factbook/manifest.json work/boar-factbook/factbook.jsonl
  ```
## Engine check (patched engine tree, WikiPack.search k 5, lexical only, 2026-10-13)
- "what is the capital and population of Kenya": Kenya Background / Government / Key facts (lead, "Capital: Nairobi") / Geography (population distribution); 5th hit Haiti.
- "compare the land area of Brazil and Australia": Brazil and Australia Background + Government; the Area lines (Key facts / Geography) are not in the top 5.
- "which currency does Japan use": Japan Background, Military, Key facts (lead, carries "Currency: yen (JPY)" lower in the block), South Korea Key facts.
- FTS: nairobi 7 chunks, yen 6, kinshasa 5. Source ids 11:261.
## Measured coverage
- V-para 34 absent items: verified 1/34 (one explanation item, Japan entry), >=0.7 1, >=0.6 3; all in the on-topic-kept group, 0 on the 20 no-kept items (coverage probe 2026-10-13: jev fact-in-text over 20 candidate chunks per item, deep-tier run s42). With the other wave-1/wave-2 packs and the installed kit: 6/34.
## Crowding
- crowding probe 2026-10-13: share of kept slots 0.107 (v0.2) / 0.200 (v0.1), on 11 / 10 items, spread over explanation, comparison and reasoning items, 0 on crypto (replay on 110 + 60 dev items); kit gold counted over all slots goes up (country entries share titles with the gold), but counted over kit slots only it drops on 1 / 3 items (v0.1 16/14 to 12/10) → passes the share rule, borderline on gold: **user-selected only** until a quality check; retrieval p50 +32 ms (v0.2) / -6 ms (v0.1).
## Quality
- Self-test score (2026-10-13; the 20 public self-test questions written from this pack's text; Haiku 5.5-low L1 judge, both answer orders; 4B claim build; dev): with pack raw **0.44** (0.38–0.50), above_min 0.29 / without pack raw **0.46** (0.39–0.52), above_min 0.31; paired Δ -0.018 raw (95 % CI -0.079…+0.026), -0.022 above_min; items better/worse with the pack 8/8; win/tie/loss vs the gold answer 0/0/20. Pack passages kept on 5/20 items (7/35 kept passages); the fact's source article kept on 5/20. Gold answers are agent-written from the same text: a development check, not comparable with benchmark numbers.
- Self-test, deep tier (Qwen3.6-35B-A3B + thinking 512, desktop, Haiku 5.5-low N=4 both orders, 2026-10-13): with pack 0.554 vs without 0.550, Δ +0.004 (−0.015…+0.023); deep with pack vs 4B with pack +0.116 (+0.045…+0.192); pack passages kept on 9/20 items; win 0/20. Dev numbers, agent-written gold; the deep tier gains nothing measurable from this pack.
## Category gaps
- Country-level facts only (no cities beyond capitals, no history detail beyond "Background"). Figures frozen at 2024/2025 estimates; no calling codes; no flags/maps.
## Curation notes
- Lexical ranking favours the long Background/Government sections over the Key facts block for "capital/currency/area" questions; the Key facts chunk is the lead, so a semantic re-rank (queryVec) should lift it. Worth checking in the pack workflow crowding.
- Alias "Congo" points to the DRC (from its former names); the Republic of the Congo's title is "Congo (Brazzaville)".

## Published
- 2026-10-13 02:30: https://huggingface.co/datasets/r4topunk/boar-packs/tree/main/topics/boar-factbook (sqlite + .sqlite.json + README + LICENSE + selftest.jsonl; root README "Wave 2" section, commit de2c38f5). Flag: user-selected only.
