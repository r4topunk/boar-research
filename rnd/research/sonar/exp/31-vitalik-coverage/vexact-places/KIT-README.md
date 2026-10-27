# V-exact places kit (Sonar, 2026-10-03)
Places data for the 6 vegan V-exact items (food-001/002/006 Berlin, Lisbon, Tokyo; vx-003/004/005 the same cities with a GPS fix).
- `world-places.sqlite` = the shipping world gazetteer (sha 215ce466…, identical to `hf-stage-gaz/places/world-places.sqlite`, HF r4topunk/boar-packs @0d75f30; 34,149 places, GeoNames ≥ 15k, with the 8,374-tile index). Not the older `poi/world-places.sqlite` (fdb302aa…, no tile index).
- City tiles: 1° tiles from the world places pipeline (`shared-data/poi/geofabrik`, format boar-poi-pack v1, the same format as the region packs): t-N52E013 (Berlin), t-N38W010 (Lisbon), t-N35E139 + t-N35E140 (Tokyo, with the east of the metro area).
- Licence: ODbL 1.0 (© OpenStreetMap contributors) + CC BY-SA 4.0 (Wikivoyage listings); OSM snapshots 2026-09-25 (Berlin, Tokyo west) and 2026-09-27 (Lisbon, Tokyo east), Geofabrik regional extracts.
- **Gold check:** the v0.1 OSM gold venues (snapshot 2026-09-26) are present by name: Berlin 2,908/2,909, Lisbon 190/190, Tokyo 215/215.
- Runner: `--places <this dir>/world-places.sqlite,<this dir>/t-N52E013.sqlite,<this dir>/t-N38W010.sqlite,<this dir>/t-N35E139.sqlite,<this dir>/t-N35E140.sqlite` (the runner links each file into poi/ by basename).
