// exp-29: the health-extractive "no steps → What the source says" fallback, all non-blind traces: unique (question, quote), bge-m3 relevance.
import fs from "node:fs"; import { execSync } from "node:child_process";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const files = execSync(`grep -rlE --include='*.traces.jsonl' "What the source says|O que a fonte diz" <workspace>/boar-eval/runs <workspace>/rnd 2>/dev/null || true`).toString().split("\n").filter((f) => f && !/v1-fresh|\/blind\/|\/veil\//.test(f));
const U = new Map<string, any>(); let n = 0;
for (const f of files) for (const l of fs.readFileSync(f, "utf8").split("\n").filter(Boolean)) {
  let t: any; try { t = JSON.parse(l); } catch { continue; } if (/^(v1-|v02-)/.test(t.itemId)) continue;
  const m = (t.answer?.text ?? "").split(/What the source says[^:]*:|O que a fonte diz[^:]*:/)[1]; if (!m) continue; n++;
  const quote = m.trim().split("\n\n")[0]; const k = `${t.question}\u0000${quote}`;
  const u = U.get(k) ?? { item: t.itemId, q: t.question, quote, runs: 0, file: f.includes("/exp/29-") ? "exp29" : "runs" }; u.runs++; U.set(k, u);
}
const rr = await (await (await getLlama({ logLevel: "error" })).loadModel({ modelPath: "<workspace>/shared-models/bge-reranker-v2-m3-q4km.gguf" })).createRankingContext({ contextSize: 1024, threads: 4 });
const rows = [...U.values()]; for (const r of rows) r.s = +(await rr.rank(r.q, r.quote.slice(0, 2400))).toFixed(3);
rows.sort((a, b) => a.s - b.s);
const ext = rows.filter((r) => r.file === "runs");
console.log(`fallback answers in eval runs (not my exp-29 runs): ${ext.reduce((s, r) => s + r.runs, 0)} traces, ${ext.length} unique; off-topic (<0.10) ${ext.filter((r) => r.s < 0.1).length}`);
for (const r of ext) console.log(`${r.s.toFixed(3)} ${r.item} [${r.runs}] Q: ${r.q.slice(0, 70)} || ${r.quote.replace(/\s+/g, " ").slice(0, 100)}`);
fs.writeFileSync("fallback.json", JSON.stringify(rows, null, 1));
