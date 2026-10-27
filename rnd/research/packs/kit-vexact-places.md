# kit-vexact places (world-places + OSM city tiles)
TL;DR: places gazetteer (GeoNames >= 15k, 34,149 places, 8,374-tile index) plus four 1-degree OSM POI tiles (Berlin, Lisbon, Tokyo x2); format boar-places-pack / boar-poi-pack, not a text Knowledge Pack; powers the venue path (VENUEGPS-2 7/7).

## What it is
- world-places.sqlite: GeoNames cities15000, licence CC BY 4.0 (GeoNames), built 2026-09-28. Tiles: t-N52E013 (Berlin, 17,157 POIs), t-N38W010 (Lisbon, 9,884), t-N35E139 (Tokyo west, 62,475), t-N35E140 (Tokyo east, 4,011). Licence ODbL 1.0 (c) OpenStreetMap contributors + CC BY-SA 4.0 (Wikivoyage listings). OSM snapshots 2026-09-25 (Berlin, Tokyo W) and 2026-09-27 (Lisbon, Tokyo E).
## Format
- world-places: format boar-places-pack v1, tables meta, names, places, tiles. Tiles: boar-poi-pack v1 (same family as regional POI packs; Geofabrik extracts). No embeddings, no FTS5 text index of prose; lookup by name/coordinates.
- Sizes: world-places 22,962,176 B; t-N35E139 9,900,032; t-N35E140 663,552; t-N38W010 1,781,760; t-N52E013 3,706,880 (total 38.99 MB).
- sha256 (SHA256SUMS in the dir): world-places 215ce4663b2f79dbf25e9cacab90cd8aa0a8711721663a733cb53bc49d972892; N52E013 0accffdf...; N38W010 45b508b5...; N35E139 8fcd37b7...; N35E140 2cb90347... (full values in SHA256SUMS).
## Kit entry and build
- Runner option `--places <dir>/world-places.sqlite,<dir>/t-*.sqlite` (not config.kit text packs). Extended kit-vgps2 = kit-vexact + 5 tiles (+3.65 MB, SHA256SUMS 94821014...), picked by user location.
- Build: boar-app/scripts/build-places-pack.mjs (cities15000.txt countryInfo.txt out.sqlite [tiles index]); tiles via build-poi-pack.mjs / build-poi-world.mjs (docs/POI_PACKS.md).
## Measured coverage
- PACKCOND P1 skipped it: judged items on v0.2/V-para are not venue lists and judge.v1 does not score them. Coverage was measured on the v0.1 OSM gold: Berlin 2,908/2,909, Lisbon 190/190, Tokyo 215/215 venue names present.
## Measured quality effects
- VENUEGPS: with kit-vexact only, 7/7 venue items fail (location unavailable, then coverage-none). VENUEGPS-2 (location in runner + the user's area tile): P5 7/7 on both seeds, 10/10 OSM-gold matches per item, 5-192 ms. Venues and gold are both OSM diet tags, so this proves the path, not venue quality. Claim text: "with device location and the user's area tile".
## Known gaps
- Only 4 cities (plus 5 catalog tiles in kit-vgps2); anywhere else returns coverage-none. Prose questions (travel-local/practical) are not helped by it.
## Community curation notes
- Card fields: id, name, domain, source + snapshot date, licence line per source (meta `sources`/`license`), counts, sha256, build command, kit entry `{id, sha256}`, known gaps.
- Self-test set (PACKCOND O4, P5, needs r4to): 20 public questions written by a curator (not Claude) whose answers are in the pack; scored by the same pipeline (F0 gate, then judge.v1 ratio); ship the per-pack number on the card.
- Licence: keep the per-source licence map from meta and a one-line attribution; CC BY-SA 4.0 and ODbL 1.0 are share-alike (card must say so).
- Self-test: 20 "near me" venue queries with a known OSM-gold answer per tile; licence line must carry ODbL attribution.
