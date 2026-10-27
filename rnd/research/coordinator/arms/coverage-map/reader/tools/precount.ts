// RD2 0-LLM pre-count: apply groundUncited to the F1b answer texts with the replay's keptFull sources. usage: tsx precount.ts [bar]
import { readFileSync, writeFileSync } from "node:fs";
import { groundUncited } from "<workspace>/kiln-local/rs-RD2/src/routing/citations";
const C = "<workspace>/rnd/research/coordinator/arms/coverage-map";
const bar = Number(process.argv[2] ?? 0.6);
const W = "Not found in this phone's offline library. From the model's memory, may be wrong:";
const rd = (f: string) => readFileSync(f, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const T = new Map(rd(C + "/sefix/ans-traces/f1b-main-s42.traces.jsonl").map((t: any) => [t.itemId, t]));
const R = new Map(rd(C + "/sefix/replays/main.v3-extra.jsonl").map((r: any) => [r.id, r]));
const out: any[] = [];
for (const [id, t] of T) {
  const rp: any = R.get(id); const raw: string = t.answer.text ?? "";
  if (!rp || t.answer.declined) continue;
  const warned = raw.startsWith(W);
  const body = warned ? raw.slice(W.length).replace(/^\n/, "") : raw;
  if (/\[\d+\]/.test(body)) continue;
  const rc: string[] = t.route.reasonCodes;
  // not reached by the hook: instant:final returns the extractive excerpt before post-processing; health answers are cards/excerpts
  if (rc.includes("instant:final") || rc.some((x) => /health|^grounding:fa-card/.test(x))) continue;
  const sources = (rp.keptFull ?? []).map((c: any) => ({ chunkId: c.chunkId, docId: c.docId, title: c.title, body: c.body, score: 1, matchType: "lexical" }));
  const g = groundUncited(body, sources, t.question ?? rp.query, bar);
  out.push({ id, warned, nSources: sources.length, added: g.added, flips: g.added.length > 0, text: body, grounded: g.added.length ? g.text : null, reasonCodes: rc.filter((x) => /grounding|multipass|health/.test(x)) });
}
writeFileSync(C + `/reader/precount.bar${bar}.json`, JSON.stringify(out, null, 1));
const f = out.filter((o) => o.flips);
console.log(`bar ${bar}: uncited non-declined ${out.length} (warned ${out.filter((o) => o.warned).length}); flips ${f.length}: warned->cited ${f.filter((o) => o.warned).length}`);
for (const o of f) console.log(`FLIP ${o.id} warned=${o.warned} added=${o.added.join(",")}\n  ${o.grounded.replace(/\n/g, " | ").slice(0, 500)}`);
