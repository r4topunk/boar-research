// exp-27 L0 dry run: the gate on and-qwen-s44's dumped prompts (exact engine prompts) for the retrieval-inkit and
// outofkit-quality L1 slices. Reports passages dropped, key-bearing passages dropped, items whose context changes, ms/pair.
import fs from "node:fs";
import { gate, splitContext, doc } from "./rrgate.ts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const TAU = Number(process.env.TAU ?? 0.05);
const S = JSON.parse(fs.readFileSync("../../../compass/fast-loop/l1-slices.json", "utf8")).slices;
const ids = new Set<string>([...S["retrieval-inkit"].ids, ...S["outofkit-quality"].ids]);
const Q: Record<string, any> = Object.fromEntries(fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => { const x = JSON.parse(l); return [x.id, x]; }));
const norm = (s: string) => s.toLowerCase().replace(/’/g, "'").replace(/\s+/g, " ");
const termHit = (t: string, x: string) => (x.startsWith("re:") ? new RegExp(x.slice(3)).test(t) : t.includes(norm(x)));
const keyHit = (text: string, g: any) => { if (!g || !(g.must_any || g.must_k)) return false; const t = norm(text); let ok = (g.must_any ?? []).every((grp: string[]) => grp.some((x) => termHit(t, x))); if (g.must_k) ok &&= g.must_k.terms.filter((x: string) => termHit(t, x)).length >= g.must_k.k; return ok; };
const llama = await getLlama({ logLevel: "error" });
const rr = await (await llama.loadModel({ modelPath: process.argv[2] })).createRankingContext({ contextSize: 1024, threads: 4 });
let pairs = 0, ms = 0, dropped = 0, keyDropped = 0, changed: string[] = [], keyCtxLost: string[] = [], seen = 0;
const rank = async (q: string, d: string) => { const t = performance.now(); const s = await rr.rank(q, d); ms += performance.now() - t; pairs++; return s; };
const rows: any[] = [];
for (const l of fs.readFileSync("<workspace>/boar-eval/runs/and-qwen-s44/and-qwen-s44.prompts.jsonl", "utf8").split("\n").filter(Boolean)) {
  const x = JSON.parse(l); if (!ids.has(x.itemId)) continue; seen++;
  const { messages, info } = await gate(x.messages, rank, TAU); if (!info) continue;
  const before = splitContext(x.messages[0].content)!.passages, after = splitContext(messages[0].content)!.passages;
  const g = Q[x.itemId]?.grading;
  for (const p of before) if (!after.includes(p) && !after.some((a) => a.n === p.n)) { dropped++; if (keyHit(doc(p), g)) keyDropped++; }
  if (info.dropped.length) changed.push(x.itemId);
  if (keyHit(before.map(doc).join("\n"), g) && !keyHit(after.map(doc).join("\n"), g)) keyCtxLost.push(x.itemId);
  rows.push({ id: x.itemId, scored: info.scored, titles: before.map((p) => p.text.split("\n")[0].slice(0, 70)) });
}
for (const r of rows) console.log(r.id.padEnd(12), JSON.stringify(r.scored.map((s: any) => [s.n, s.score, s.kept ? "keep" : "DROP"])), JSON.stringify(r.titles));
console.log(`tau ${TAU}: slice prompts ${seen} (s44 dump), with >=2 passages ${rows.length}; pairs ${pairs} (${(ms / pairs).toFixed(0)} ms/pair, this MacBook under load); passages dropped ${dropped}; key-bearing passages dropped ${keyDropped}; items whose context loses the key ${keyCtxLost.length} ${JSON.stringify(keyCtxLost)}; items changed ${changed.length} ${JSON.stringify(changed)}`);
fs.writeFileSync(`dryrun-tau${TAU}.json`, JSON.stringify(rows, null, 1));
