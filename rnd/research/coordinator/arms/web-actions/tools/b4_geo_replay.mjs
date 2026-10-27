// WEB-ACTIONS-B item 4 (T10.1 / W23): replay the places router (detectGeoIntent, engine tree kiln-local/be-0cfd4a77-cut7-litepacks, read-only)
// on every public dev question (v0.1, self-tests, rivalset, slices). 0 LLM. Usage: node b4_geo_replay.mjs > ../aggregates/b4-geo-replay.json
import { readFileSync, readdirSync } from "node:fs";
const { detectGeoIntent } = await import("<workspace>/kiln-local/be-0cfd4a77-cut7-litepacks/src/routing/geo.ts");
const B = "<workspace>/boar-eval/bench";
const files = [["v0.1", `${B}/v0.1/questions.public.jsonl`], ["rivalset", `${B}/rivalset/questions.jsonl`],
  ...readdirSync(`${B}/selftest`).map((d) => [`selftest/${d}`, `${B}/selftest/${d}/questions.jsonl`]),
  ...["longsession-v1", "packread-v1", "chainwhen-v1", "mathroute-v1"].map((d) => [`slices/${d}`, `${B}/slices/${d}/questions.jsonl`])];
const CUST = /\b(tip|tips|tipping|etiquette|customs?|customary|manners|polite|rude|dress|behaviou?r|taboo|offend\w*|greet\w*|bow|shoes|gift)\b/i;
const seen = new Map(); const out = { n: 0, places: [], customs: [] };
for (const [set, f] of files) {
  for (const l of readFileSync(f, "utf8").split("\n")) {
    if (!l.trim()) continue; const q = JSON.parse(l); const t = q.question ?? q.prompt ?? ""; if (!t || seen.has(q.id + t)) continue; seen.set(q.id + t, 1); out.n++;
    const g = detectGeoIntent(t); const row = { set, id: q.id, places: !!g, near: g?.near ?? null, q: t.slice(0, 160) };
    if (g) out.places.push(row);
    if (CUST.test(t)) out.customs.push(row);
  }
}
console.log(JSON.stringify(out, null, 1));
