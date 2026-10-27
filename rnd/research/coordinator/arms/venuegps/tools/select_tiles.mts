// VENUEGPS-2: tile selection by coordinates only. For each venue item, the tile whose bounds contain its user_location
// (engine's own tileIdOf + tileBbox, wt/cut7 src/rag/poiRegions.ts), looked up in the app's tile catalog
// (world-places.sqlite `tiles`, the shipping gazetteer in kit-vexact). Prints ids, coordinates, tile ids, catalog rows.
// Usage: tsx select_tiles.mts > tiles.json
import { readFileSync } from "node:fs";
import { DatabaseSync } from "node:sqlite";
import { tileIdOf, tileBbox } from "<workspace>/wt/cut7/src/rag/poiRegions.ts";
const locs: { id: string; lat: number; lon: number }[] = JSON.parse(readFileSync("<private held-out dir>", "utf8"));
const db = new DatabaseSync("<workspace>/shared-data/poi/kit-vexact/world-places.sqlite", { readOnly: true });
const q = db.prepare("select id, size_bytes, sha256, pois, vegan, osm_date, url from tiles where id = ?");
const rows = locs.map((l) => {
  const tile = tileIdOf(l.lat, l.lon);
  const [a, b, c, d] = tileBbox(tile)!;
  const inside = l.lat >= a && l.lat < c && l.lon >= b && l.lon < d;
  return { id: l.id, lat: l.lat, lon: l.lon, tile, inside, catalog: (q.get(tile) as any) ?? null };
});
console.log(JSON.stringify(rows, null, 1));
