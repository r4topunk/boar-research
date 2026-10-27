// VENUEGPS step 1: deterministic cause classification of the 7 V-para venue items from existing traces.
// Reads blind/ (script-only). Prints ONLY ids, class, route codes (task/near/location/places), counts.
// Usage: node cause.mjs <traces.jsonl>...
import { readFileSync } from "node:fs";
const V = "<private held-out dir>";
const ids = readFileSync(`${V}/items.jsonl`, "utf8").trim().split("\n").map((l) => JSON.parse(l))
  .filter((q) => q.grading?.type === "venue-list").map((q) => q.id);
const classify = (t) => {
  const rc = t.route?.reasonCodes ?? [];
  if (t.route?.task !== "places" && !rc.includes("task:places")) return "other";
  if (rc.some((c) => /^location:(unavailable|denied|timeout|stale|prompt|stopped)$/.test(c)) || rc.includes("places:no-pack")) return "no-location";
  const pe = (t.events ?? []).filter((e) => e.kind === "places");
  const n = pe.reduce((a, e) => Math.max(a, Array.isArray(e.places) ? e.places.length : 0), 0);
  if (n === 0 || rc.some((c) => /^places:(coverage-none|no-match|search-failed)/.test(c))) return "no-places-hit";
  return "places-hit-but-answer-ignores";
};
const all = {};
for (const f of process.argv.slice(2)) {
  const T = Object.fromEntries(readFileSync(f, "utf8").trim().split("\n").map((l) => JSON.parse(l)).map((t) => [t.itemId, t]));
  const rows = ids.map((id) => {
    const t = T[id];
    if (!t) return { id, cls: "missing" };
    const pe = (t.events ?? []).filter((e) => e.kind === "places");
    return { id, cls: classify(t), tier: t.route?.tier, places: pe.reduce((a, e) => Math.max(a, Array.isArray(e.places) ? e.places.length : 0), 0),
             codes: (t.route?.reasonCodes ?? []).filter((c) => /^(task|near|location|places):/.test(c)) };
  });
  const counts = {}; for (const r of rows) counts[r.cls] = (counts[r.cls] ?? 0) + 1;
  all[f.split("/").pop()] = { counts, rows };
}
console.log(JSON.stringify(all, null, 1));
