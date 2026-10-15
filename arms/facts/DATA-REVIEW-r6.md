# FACTS r6 data review (criterion C): new rows only

Reviewer: the r6 agent (Opus), row by row against its own knowledge; no web, no LLM call, no judge.
Tool: `tools/sample_new_rows.py <r5 asset> <candidate> <seed> 60` (entities not in the r5 asset, sorted by QID, `random.Random(seed).sample`).
Flag types: wrong unit, wrong magnitude, stale year, wrong entity type, duplicate/ambiguous label.

## Round 1: seed 46 on the first candidate (4,383 entities, 3,347 new): `data-review-r6-sample.txt`
**4/60 flagged (bar ≤ 2): FAIL → one rebuild with gates.**
| # | row | flag | class |
|---|---|---|---|
| 08 | Gwangju (Q42069), city in Gyeonggi, 397,269 | ambiguous label: "Gwangju" is first the 1.4 M metropolitan city (not in the table), so "population of Gwangju" would answer the wrong city | label of a more prominent item |
| 22 | Dykh-Tau, ctry = Russia, **Russian Empire, Soviet Union** | stale: dissolved states printed as the mountain's country (P17 without end date) | stale country list |
| 23 | Toyota (Q201117), city, 422,106 | ambiguous label: the car maker is the dominant sense ("How big is Toyota?" → city area) | label of a more prominent item |
| 47 | The One (Q30766256), Brisbane skyscraper, 263 m | ambiguous label: generic phrase / song titles; "how tall is the one" resolved lowercase | label of a more prominent item |
Not flagged but uncertain: 02 Sirajganj 450,000 (2020) and 36 Junagadh 465,000 (2020) look high vs 2011 census city figures (estimates, not provably wrong);
13/14/51 Indonesian regencies typed as "city" (the description says "regency", so the answer is honest); 05 Hulun Lake alias is a nature-reserve name.
All other 52 rows: values within ~5 % of common figures (elevations, heights, lengths, populations dated 2020–2026).

## Gates added (tools/build_asset.py, r6; raw evidence in data/raw/homonym_r6_*.{rq,json})
- (a) **stale country list**: `ctry` keeps only labels of current table countries when at least one is present (129 entities, incl. 35 r5 entities:
  Cairo, Kabul, Athens, Stockholm …; no G2 target reads it). Unmatched lists (Greenland, "Netherlands") are kept as is.
- (b) **label of a more prominent item**: a new (non-r5) entity is dropped when another Wikidata item (not a disambiguation/category page) has
  the exact same English label and more sitelinks (`tools/fetch_homonyms_r6.py`, 5 WDQS queries). 150 dropped (city 65, mountain 54, building 13,
  river 13, lake 5): Toyota, Gwangju, The One, London (Ontario), Amsterdam (municipality), Armenia (Colombia), Hyderabad (Pakistan),
  Santiago (commune), Montevideo (building), Batman, Snøhetta, Mount Olympus ×2, Colorado River ×2 … r5 entities are never dropped.
- (c) (after round 2) **water tower height**: a structure whose label ends in "water tower" loses a height > 200 m (1 value: Migdal Haemek).

## Round 2: seed 47 on the rebuilt asset (4,233 entities, 3,197 new): `data-review-r6-sample-seed47.txt`
**1/60 flagged (bar ≤ 2): PASS.**
| # | row | flag |
|---|---|---|
| 02 | Migdal Haemek water tower, height 297 m | wrong magnitude (a water tower; ~300 m is the site's elevation, not a height) → gate (c), value dropped in the final asset |
Not flagged: 46 Umboi Island (a volcanic island kept as "mountain"; its 1,548 m summit elevation is right); 17 Lachlan River 1,339 km
(sources 1,339–1,448); 33 Subansiri Lower 130 m (116 m above riverbed); 07 Pointe-Noire has a garbage alias "CapitaThe Economic" (harmless).

Final asset: 4,233 entities, 760,970 bytes, sha256 92d64c02f7cdf2dc5c61b9d73377d0aec45a8187defa3d911d50d39b79d61598 (gate log `build-r6.gates.log`).
UNKNOWN: precision of one reviewer's memory on obscure peaks (Picó Bernat, Mount Paris, Kanjiroba); populations were not checked against census tables.
