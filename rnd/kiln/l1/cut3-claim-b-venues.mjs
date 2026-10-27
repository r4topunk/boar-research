// V-para venue scoring per blind/V-para/RUN-MAPPING.md (sha 7ba30030…): unchanged venues.mjs scoreFoodAnswer; adapter only reshapes gold.
// Prints ONLY ids, booleans, counts. Usage: node cut3-claim-b-venues.mjs <dir> <run base>...
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { scoreFoodAnswer, normalize } from "<workspace>/wt/eval/eval/scripts/lib/venues.mjs";
const V = "<private held-out dir>";
const Q = readFileSync(join(V, "items.jsonl"), "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((q) => q.grading?.type === "venue-list" || q.grading?.scorer === "venue-list");
const [dir, ...runs] = process.argv.slice(2);
const vtag = (v) => v["diet:vegan"] ?? v.vegan ?? v.tags?.["diet:vegan"];
const toVenue = (v) => ({ name: v.name, nameEn: v["name:en"] ?? v.nameEn ?? v.tags?.["name:en"], osm: v.osm, vegan: vtag(v) });
const shape = (g, pred = () => true) => ({ diet: g.diet, osm: { venues: g.venues.filter(pred).map(toVenue) } });
const out = {};
for (const run of runs) {
  const T = Object.fromEntries(readFileSync(join(dir, `${run}.traces.jsonl`), "utf8").trim().split("\n").map((l) => JSON.parse(l)).map((t) => [t.itemId, t]));
  const rows = [];
  for (const q of Q) {
    const t = T[q.id]; if (!t) continue;
    const g = JSON.parse(readFileSync(join(V, q.grading.gold_file), "utf8"));
    const ans = t.answer?.text ?? "";
    const city = g.city ?? q.grading.city;
    const s = scoreFoodAnswer(ans, shape(g), { minRealVenues: 3 });
    const itemMin = q.grading.minRealVenues ?? 3;
    const near = scoreFoodAnswer(ans, shape(g, (v) => v.within_radius === true), { minRealVenues: itemMin });
    const hasFilter = g.venues.some((v) => v.matches_filter !== undefined);
    const filt = hasFilter ? scoreFoodAnswer(ans, shape(g, (v) => v.within_radius === true && v.matches_filter === true), { minRealVenues: itemMin }) : null;
    rows.push({ id: q.id, pass: s.pass, verifiedDietVenues: s.verifiedDietVenues, pass_item_min: s.verifiedDietVenues >= itemMin, pass_near: near.pass, pass_filter: filt ? filt.pass : null,
                deflects: s.deflects, names_city: city ? ` ${normalize(ans)} `.includes(` ${normalize(city)} `) : null,
                route: (t.route?.reasonCodes ?? []).filter((c) => /^(task|places|location):/.test(c)).slice(0, 4) });
  }
  out[run] = { pass: rows.filter((r) => r.pass).length, n: rows.length, rows };
}
console.log(JSON.stringify(out, null, 1));
