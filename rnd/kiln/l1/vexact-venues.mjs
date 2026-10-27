// V-exact venue scoring (RUN.md step 4): the unchanged wt/eval venues.mjs scoreFoodAnswer on the 6 vegan items of each run,
// against bench-vslice gold (OSM 2026-09-26). GPS items (vx-003..005): also whether the answer names the gold city.
// Usage: node vexact-venues.mjs <runs dir> <run base>... > venues.json   (run base = <dir>/<base>.traces.jsonl)
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { scoreFoodAnswer, normalize } from "<workspace>/wt/eval/eval/scripts/lib/venues.mjs";
const VS = "<workspace>/rnd/research/compass/exp/bounty-eval/bench-vslice";
const Q = readFileSync(join(VS, "questions.jsonl"), "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((q) => q.grading?.type === "venue-list");
const [dir, ...runs] = process.argv.slice(2);
const out = {};
for (const run of runs) {
  const T = Object.fromEntries(readFileSync(join(dir, `${run}.traces.jsonl`), "utf8").trim().split("\n").map((l) => JSON.parse(l)).map((t) => [t.itemId, t]));
  const rows = [];
  for (const q of Q) {
    const t = T[q.id]; if (!t) continue;
    const gold = JSON.parse(readFileSync(join(VS, q.grading.gold_file), "utf8"));
    const ans = t.answer?.text ?? "";
    const s = scoreFoodAnswer(ans, gold, { minRealVenues: q.grading.minRealVenues ?? 3 });
    const gps = !!q.context;
    rows.push({ id: q.id, city: gold.city, gps, pass: s.pass, verifiedDietVenues: s.verifiedDietVenues, verifiedVenues: s.verifiedVenues, deflects: s.deflects,
                namesCity: ` ${normalize(ans)} `.includes(` ${normalize(gold.city)} `), route: (t.route?.reasonCodes ?? []).filter((c) => /^(task|places|location):/.test(c)).slice(0, 4) });
  }
  out[run] = { pass: rows.filter((r) => r.pass).length, n: rows.length, gpsCity: rows.filter((r) => r.gps && r.namesCity).length, gpsN: rows.filter((r) => r.gps).length, rows };
}
console.log(JSON.stringify(out, null, 1));
