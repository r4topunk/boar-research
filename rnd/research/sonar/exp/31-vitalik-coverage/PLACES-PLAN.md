# Places coverage for the bounty kit (Sonar, 2026-10-03; EN)

TL;DR:
- **V-exact unblocked.** Lisbon and Tokyo didn't need building: the world places pipeline already produced them.
  - Tiles: t-N38W010 (Lisbon); t-N35E139 + t-N35E140 (Tokyo); Berlin is t-N52E013.
  - Same `boar-poi-pack` v1 format as the region packs; ODbL + CC BY-SA; OSM 2026-09-25/27.
  - Pinned with the shipping gazetteer (215ce466) in `shared-data/poi/kit-vexact/` (SHA256SUMS, README).
- **The v0.1 OSM gold venues are in the tiles by name:** Berlin 2,908/2,909, Lisbon 190/190, Tokyo 215/215.
- **End to end on the desktop runner** (bounty1 = health13 + travel distance, Android 4B config, `--places` = the kit):
  - food-001/002/006 list 10 real vegan-only venues each;
  - vx-003/004/005 (GPS fix) resolve the city from the location and rank by distance;
  - traces in `vexact-places/`.
- **Recommendation for the kit: ship the WHOLE WORLD places set** (8,374 tiles, 980 MB + 23 MB gazetteer, already hosted on HF r4topunk/boar-packs), not a top-N city cut.
  - It is 2% of the 50 GB budget and works wherever the judge is, including the small towns that specialized travel hits.

## Size by coverage (`places-scale.json`; tiles touched by each city ± 0.25°, cities ranked by GeoNames population as a proxy for tourism; no offline tourism ranking exists)
| Coverage | Tiles | Size |
|---|---|---|
| top 50 cities | 101 | 76 MB |
| top 100 | 186 | 96 MB |
| top 300 | 497 | 205 MB |
| top 1,000 | 1,320 | 398 MB |
| top 3,000 | 2,677 | 618 MB |
| **whole world** | **8,374** | **980 MB** |
| diet-only world (vegan/vegetarian POIs only, C-places-gps.md) | – | ~32 MB |

- The diet-only world pack is the fallback if 1 GB is too much, but it loses "ramen near me" and other cuisine questions.
- Both build from the same pipeline.

## Known quality gaps (C-places-gps.md §4; engine-side, Sonar's geo.ts lane; English)
- 2–4 of 10 results are not restaurants (gelaterias, donut shops, bars) when the question says "restaurants".
- Duplicate venues across OSM nodes (Tokyo "T's たんたん" 180 m and "T's Tantan" 2.0 km).
- Intent gaps: "near <landmark>", "plant-based / veggie", "why are there so many vegan restaurants…" (shouldn't list), "groceries", "open now".
- App side (PR to the app maintainer at the end, board rule): Android never calls `registerGeoProviders`, so the app answers "places pack not installed"; there is no places entry in the catalog UI.
