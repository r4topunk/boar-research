import fs from "node:fs";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const D = "<scratch>";
const pairs = JSON.parse(fs.readFileSync("../19-offtopic-passages/pairs.json", "utf8"));
const labels = JSON.parse(fs.readFileSync("../19-offtopic-passages/labels.json", "utf8"));
const sig = Object.fromEntries(JSON.parse(fs.readFileSync("../19-offtopic-passages/signals.json", "utf8")).map((s) => [s.pid, s]));
const auc = (pos, neg) => { let w = 0; for (const p of pos) for (const n of neg) w += p > n ? 1 : p === n ? 0.5 : 0; return w / (pos.length * neg.length); };
const llama = await getLlama({ logLevel: "error", gpu: process.env.GPU === "1" ? "auto" : false });
for (const [name, file] of [["jina-reranker-v1-tiny-en (33M, fp16)", "jina-tiny-q8.gguf"], ["bge-reranker-v2-m3 (568M, Q4_K_M)", "bge-m3-q4km.gguf"]]) {
  const model = await llama.loadModel({ modelPath: `${D}/${file}` });
  const ctx = await model.createRankingContext({ contextSize: 1024, threads: 4 });
  const scores = {}; const t = performance.now();
  for (const p of pairs) { const doc = `${p.title}\n${p.passage}`.slice(0, 2400); scores[p.pid] = await ctx.rank(p.question, doc); }
  const ms = (performance.now() - t) / pairs.length;
  const H = pairs.filter((p) => labels[p.pid].label === "helpful"), U = pairs.filter((p) => labels[p.pid].label !== "helpful");
  const a = auc(H.map((p) => scores[p.pid]), U.map((p) => scores[p.pid]));
  // never-empty drop rule at the threshold that keeps all helpful passages
  const minH = Math.min(...H.map((p) => scores[p.pid]));
  const byItem = {}; for (const p of pairs) (byItem[p.item] ??= []).push(p);
  let du = 0, dk = 0; for (const ps of Object.values(byItem)) { const best = ps.reduce((x, y) => (scores[y.pid] > scores[x.pid] ? y : x)); for (const p of ps) if (p !== best && scores[p.pid] < minH) { if (labels[p.pid].label !== "helpful") du++; if (sig[p.pid]?.key) dk++; } }
  console.log(`${name}: AUC helpful>unhelpful ${a.toFixed(3)} (bge-small cosine baseline 0.773) | drop below min-helpful score, never empty: ${du}/${U.length} unhelpful dropped, 0 helpful, ${dk} key-bearing dropped | ${ms.toFixed(0)} ms/pair (M1 CPU, 4 threads)`);
  fs.writeFileSync(`scores-${file.split("-")[0]}.json`, JSON.stringify(scores));
  await ctx.dispose(); await model.dispose();
}
