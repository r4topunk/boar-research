# VENUEGPS-2: device location + the user's area tile (2026-10-07, criterion baf48960…; 0 judge calls)
TL;DR: **P5 7/7 on s42 and 7/7 on s43** (cut 7, config (b) + location option ON + one area tile per item, no engine change).
Every item returns 10 POIs, 10 matched to OSM gold diet venues; tier instant, 5–192 ms per item. Verdict branch ≥ 5/7.
## Tile selection (tools/select_tiles.mts → tiles.json; coordinates only, gold venue lists not consulted)
Engine tileIdOf/tileBbox (wt/cut7 src/rag/poiRegions.ts) on venue-locations.json; all 7 inside their tile; all 5 tiles in the catalog.
| items | tile | bytes | catalog sha256 (12) |
|---|---|---|---|
| vpara-016, 017 | t-N50E019 | 1,040,384 | bea75d9be0c8 |
| vpara-018, 019 | t-N41E044 | 585,728 | a492031adcdc |
| vpara-020 | t-N46E014 | 724,992 | 269ea2889ea3 |
| vpara-049 | t-N39W001 | 1,093,632 | 63400daccad2 |
| vpara-050 | t-S14W072 | 208,896 | b6f769d6fc65 |
Kit shared-data/poi/kit-vgps2 = kit-vexact (hard links) + these 5, fetched read-only from the catalog URLs in world-places.sqlite
(HF r4topunk/boar-packs @44c3375c), sha = catalog sha 5/5, 10 s. SHA256SUMS sha **94821014…**. Delta **+3.65 MB** (3,653,632 B). Tile unavailable: 0 items.
## Result (scorer rnd/kiln/l1/cut6-claim-b-venues.mjs, unchanged)
| id | route codes (s42 = s43) | venues returned | OSM gold matches | pass / near | ms s42/s43 |
|---|---|---|---|---|---|
| vpara-016 | places:10, coverage-full, region-t-N50E019, near-city | 10 | 10 | yes / yes | 192 / 186 |
| vpara-017 | same, t-N50E019 | 10 | 10 | yes / yes | 18 / 18 |
| vpara-018 | same, t-N41E044 | 10 | 10 | yes / yes | 76 / 75 |
| vpara-019 | same, t-N41E044 | 10 | 10 | yes / yes | 5 / 5 |
| vpara-020 | same, t-N46E014 | 10 | 10 | yes / yes | 5 / 5 |
| vpara-049 | same, t-N39W001 (filter item: pass_filter yes) | 10 | 10 | yes / yes | 47 / 46 |
| vpara-050 | places:10, **coverage-partial**, region-t-S14W072, near-city | 10 | 10 | yes / yes | 5 / 5 |
s43 = s42 byte-identical (names and answer text 7/7; the places path is LLM-free). Process setup ≈ 60 s per run (wall 70 s / 12 s cached).
Engine venue names (all 70: engine-venues.json), e.g. 016 No Bones, Veganic, Zielony Talerz, … Hard Rock Cafe; 018 Living Vino, Brinji, Black Cup, …;
020 Veganika, Gaudi&Naan, Bistro Maha, …; 049 Khambú, Jardín Urbano, La Lluna, …; 050 Vrinda Vegetariana, Green Point Vegan Food, Tulasi Restaurante Vegetariano, ….
## Gate (5 non-venue controls vpara-001…005, location ON + new kit vs VENUEGPS same-machine run)
Retrieval raw+kept 5/5, prompt tokens 5/5, answer text 5/5, route 5/5 identical; item-location events 0 (no entry for those ids).
## Verdict (criterion rule, read once)
7/7 ≥ 5/7 → the places path works under "GPS fix + the user's area tile downloaded"; claim text states venue results as "with
device location and the user's area tile", and the 12 GB config lists the tile download. Not a claim number (V-para burnt).
## Deviations / caveats
1. The VENUEGPS option-on run had no non-venue items; the gate reference is the VENUEGPS same-machine OFF run (vg-offnv-s42); option ON is a no-op for ids absent from venue-locations.json (0 events), so that is the same reference.
2. tools/cause.mjs regex fixed (coverage-full/partial had been counted as no-hit); VENUEGPS numbers unchanged (all coverage-none).
3. Gold and engine both come from OSM diet tags, so a pass shows the plumbing works. It does not check whether the venues are any good.
## Exposure
Scripts read blind/V-para/venue-locations.json, items.jsonl and gold files (scorer only). Outputs: blind/.../runs-venuegps/
vg2-{on-s42,on-s43,nv-s42}.*, venues-vg2-s4{2,3}.json. Left blind/: ids, coordinates, tile ids, counts, booleans, engine venue names.
UNKNOWN: whether the app installs the area tile without a user action (download UX); results for cities with no catalog tile.
