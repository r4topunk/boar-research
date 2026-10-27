// SOURCEGROUP step 3 (0 LLM): apply the engine's pure groupSources() (kiln-local/be-cut7-sourcegroup) to each
// trace's final source list + answer text, post hoc. Checks per trace: no page twice after grouping; every
// in-range [n] maps to a group n that holds the passage it cited; text identical once markers are removed
// (and byte-identical when no page repeats); group count = distinct pages.
import { readFileSync, writeFileSync } from "node:fs";
import { groupSources, pageKey } from "<workspace>/kiln-local/be-cut7-sourcegroup/src/routing/sourceGroups.ts";

const [inp, out] = process.argv.slice(2);
const rows = readFileSync(inp, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const strip = (t: string) => t.replace(/\s*\[\d+\]/g, "").replace(/\s+/g, " ").trim();
const agg: Record<string, any> = {};
const fails: any[] = [];
for (const r of rows) {
  const a = (agg[r.set] ??= { traces: 0, grouped: 0, dupAfter: 0, markerBad: 0, markerPassageBad: 0, textOtherBad: 0, identityBad: 0, textChanged: 0, before: 0, after: 0, markersIn: 0, markersOut: 0, collapsed: 0 });
  const sources = r.sources.map((s: any, i: number) => ({ chunkId: `p${i}`, docId: `p${i}`, title: s.title, body: "", score: 0, matchType: "hybrid", ...(s.source != null ? { source: s.source } : {}) }));
  const g = groupSources(r.text, sources);
  a.traces++;
  a.before += g.before;
  a.after += g.after;
  if (g.after < g.before) a.grouped++;
  const keys = g.groups.map((x) => pageKey(x));
  const bad = (k: string, extra = {}) => fails.push({ set: r.set, id: r.id, check: k, ...extra });
  if (new Set(keys).size !== keys.length || g.after !== new Set(sources.map((s: any) => pageKey(s))).size) (a.dupAfter++, bad("dupAfter"));
  // markers: original in-range [k] -> new [map[k]] whose group holds passage k
  const orig = [...r.text.matchAll(/\[(\d+)\]/g)].map((m) => Number(m[1]));
  const neu = [...g.text.matchAll(/\[(\d+)\]/g)].map((m) => Number(m[1]));
  const inRange = orig.filter((k) => k >= 1 && k <= g.before);
  a.markersIn += inRange.length;
  a.markersOut += neu.length;
  if (neu.some((n) => n >= 1 && n > g.after && !orig.includes(n))) (a.markerBad++, bad("markerOutOfGroups", { neu }));
  for (const k of inRange) if (!g.groups[g.map[k] - 1]?.passages.some((p) => p.sourceIndex === k - 1)) (a.markerPassageBad++, bad("markerPassage", { k }));
  if (g.after < g.before) {
    const expect = inRange.map((k) => g.map[k]);
    // same sequence once adjacent repeats are collapsed (the only allowed change besides renumbering)
    const collapse = (xs: number[]) => xs.filter((x, i) => i === 0 || x !== xs[i - 1]);
    const neuIn = neu.filter((n) => n >= 1 && n <= g.after);
    if (neuIn.length < expect.length) a.collapsed++;
    const same = neuIn.join() === expect.join() || (neuIn.length < expect.length && collapse(neuIn).join() === collapse(expect).join());
    if (!same) (a.markerBad++, bad("markerSeq", { expect, neuIn }));
  }
  if (strip(g.text) !== strip(r.text)) (a.textOtherBad++, bad("textOther"));
  if (g.after === g.before && g.text !== r.text) (a.identityBad++, bad("identity"));
  if (g.text !== r.text) a.textChanged++;
}
for (const a of Object.values(agg)) {
  a.meanBefore = +(a.before / a.traces).toFixed(3);
  a.meanAfter = +(a.after / a.traces).toFixed(3);
}
writeFileSync(out, JSON.stringify({ agg, fails }, null, 1));
console.log(JSON.stringify(agg, null, 0).replace(/\},"/g, '},\n"'));
console.log("fails", fails.length, JSON.stringify(fails.slice(0, 5)));
