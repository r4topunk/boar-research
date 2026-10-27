// exp-27b L0: the cross-encoder as a COVERAGE signal (not a filter). For every s44 prompt with context: max bge-m3 score over
// the first <= 3 passages. Against the judge: does a low max flag the confident-wrong answers (s44 judge correctness <= 2,
// not declined) better than the engine's own weakSources flag?
import fs from "node:fs";
import { splitContext, questionOf, doc } from "./rrgate.ts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const B = "<workspace>/boar-eval/runs/and-qwen-s44/and-qwen-s44";
const load = (p: string) => fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const tr = Object.fromEntries(load(B + ".traces.jsonl").map((t) => [t.itemId, t]));
const corr: Record<string, number[]> = {}; for (const j of load(B + ".judgments.jsonl")) if (j.ok && j.mapped) (corr[j.queryId] ??= []).push(j.mapped.boar.correctness);
const llama = await getLlama({ logLevel: "error" });
const rr = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-reranker-v2-m3-q4km.gguf" })).createRankingContext({ contextSize: 1024, threads: 4 });
const rows: any[] = []; const seen = new Set<string>();
for (const x of load(B + ".prompts.jsonl")) {
  if (seen.has(x.itemId)) continue; const sp = splitContext(x.messages[0].content); if (!sp) continue; seen.add(x.itemId);
  const q = questionOf(x.messages[x.messages.length - 1].content);
  const sc: number[] = []; for (const p of sp.passages.slice(0, 3)) sc.push(await rr.rank(q, doc(p)));
  const c = corr[x.itemId]; const t = tr[x.itemId];
  rows.push({ id: x.itemId, max: Math.max(...sc), s1: sc[0], n: sp.passages.length, correctness: c ? c.reduce((a, b) => a + b, 0) / c.length : null, declined: t?.answer.declined, weak: t?.answer.weakSources });
}
rows.sort((a, b) => a.max - b.max);
for (const r of rows) console.log(r.id.padEnd(12), `max ${r.max.toFixed(3)} s1 ${r.s1.toFixed(3)} n ${r.n} corr ${r.correctness ?? "-"} weak ${r.weak} declined ${r.declined}`);
const judged = rows.filter((r) => r.correctness !== null && !r.declined); const cw = (r: any) => r.correctness <= 2;
const auc = (f: (r: any) => number) => { const P = judged.filter(cw), N = judged.filter((r) => !cw(r)); let s = 0; for (const p of P) for (const n of N) s += f(p) < f(n) ? 1 : f(p) === f(n) ? 0.5 : 0; return s / (P.length * N.length); };
console.log(`prompts with context ${rows.length}; judged non-declined ${judged.length}; CW (corr<=2) ${judged.filter(cw).length}`);
console.log(`AUC(low max-score -> CW) ${auc((r) => r.max).toFixed(3)}; AUC(low passage-1 score -> CW) ${auc((r) => r.s1).toFixed(3)}; weakSources flag: CW ${judged.filter((r) => cw(r) && r.weak).length}/${judged.filter(cw).length}, non-CW ${judged.filter((r) => !cw(r) && r.weak).length}/${judged.filter((r) => !cw(r)).length}`);
for (const tau of [0.05, 0.1, 0.2, 0.3]) console.log(`max < ${tau}: CW ${judged.filter((r) => cw(r) && r.max < tau).length}/${judged.filter(cw).length}, non-CW ${judged.filter((r) => !cw(r) && r.max < tau).length}/${judged.filter((r) => !cw(r)).length}`);
fs.writeFileSync("coverage-l0.json", JSON.stringify(rows, null, 1));
