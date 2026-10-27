// exp-29 task 3: every instant:final answer in boar-eval/runs + rnd traces (skipping v1-fresh, blind, veil, and v1-* ids).
// Per unique (question, answer): source title, crypto-pack source flag, bge-m3 relevance of (question, answer text).
import fs from "node:fs"; import { execSync } from "node:child_process";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const files = execSync(`grep -rl --include='*.traces.jsonl' 'instant:final' <workspace>/boar-eval/runs <workspace>/rnd 2>/dev/null || true`).toString().split("\n").filter((f) => f && !/v1-fresh|\/blind\/|\/veil\//.test(f));
const CRYPTO = /^(Ethereum EIPs\/ERCs|Ethereum specs|ethereum\.org|Bitcoin BIPs):|^(Ethereum|Bitcoin|Tornado Cash)\b/;
const uniq = new Map<string, any>(); let total = 0;
for (const f of files) for (const l of fs.readFileSync(f, "utf8").split("\n").filter(Boolean)) {
  let t: any; try { t = JSON.parse(l); } catch { continue; }
  if (/^(v1-|v02-)/.test(t.itemId) || !t.route?.reasonCodes?.includes("instant:final")) continue;
  total++;
  const src = (t.answer.shown ?? [])[(t.answer.cited?.[0] ?? 1) - 1] ?? (t.answer.shown ?? [])[0];
  const title = typeof src === "string" ? src : src?.title ?? "";
  const k = `${t.question}\u0000${t.answer.text}`;
  const u = uniq.get(k) ?? { item: t.itemId, question: t.question, answer: t.answer.text, title, runs: [] as string[], health: t.route.reasonCodes.some((c: string) => c.startsWith("grounding:health")), pt: t.route.reasonCodes.includes("retrieve:pt-en-terms") };
  u.runs.push(f.split("/runs/")[1] ?? f); uniq.set(k, u);
}
const llama = await getLlama({ logLevel: "error" });
const rr = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-reranker-v2-m3-q4km.gguf" })).createRankingContext({ contextSize: 1024, threads: 4 });
const rows = [...uniq.values()];
for (const r of rows) { r.score = +(await rr.rank(r.question, `${r.title}\n${r.answer}`.slice(0, 2400))).toFixed(3); r.crypto = CRYPTO.test(r.title); }
rows.sort((a, b) => a.score - b.score);
fs.writeFileSync("scan.json", JSON.stringify(rows, null, 1));
console.log(`files ${files.length}; instant:final traces ${total}; unique (question, answer) ${rows.length}; score<0.10 ${rows.filter((r) => r.score < 0.1).length}; <0.30 ${rows.filter((r) => r.score < 0.3).length}; crypto source ${rows.filter((r) => r.crypto).length}`);
for (const r of rows.filter((r) => r.score < 0.3)) console.log(`${r.score.toFixed(3)} ${r.item} [${r.runs.length} runs] Q: ${r.question.slice(0, 90)} || SRC: ${r.title.slice(0, 50)} || A: ${r.answer.replace(/\s+/g, " ").slice(0, 140)}`);
