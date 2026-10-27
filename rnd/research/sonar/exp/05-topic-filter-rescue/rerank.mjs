// Sonar exp-05b: does a 33M cross-encoder (jina-reranker-v1-tiny-en Q8_0, sha 0defc1f8…) separate answer-bearing
// sources from the rest where bge-small cosine can't? Same sources as exp-05 (sources.json, all raw sources of
// ios-main-v5-t0 + ios-main-s42). Passage text: vital5 = its best-cosine chunk; Wikivoyage/crypto = first 1,500 chars
// of the article. Metric: within-item pairwise AUC (key-bearing vs non-key source), cosine vs reranker.
import { DatabaseSync } from "node:sqlite";
import fs from "node:fs";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const zstdDec = (b) => new Promise((ok, ko) => import("node:zlib").then((z) => z.zstdDecompress(b, (e, r) => (e ? ko(e) : ok(r)))));
const v5 = new DatabaseSync("<workspace>/shared-data/packs/wiki-vital5.sqlite", { readOnly: true });
const f2 = [new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true }), new DatabaseSync("<workspace>/shared-data/crypto/boar-crypto.sqlite", { readOnly: true })];
const llama = await getLlama({ logLevel: "error" });
const emb = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext();
const rr = await (await llama.loadModel({ modelPath: process.env.RR ?? "models/jina-reranker-v1-tiny-en-Q8_0.gguf" })).createRankingContext();
const cos = (q, buf) => { const v = new Int8Array(buf.buffer, buf.byteOffset, buf.byteLength); let d = 0, a = 0, b = 0; for (let i = 0; i < v.length; i++) { d += q[i] * v[i]; a += q[i] * q[i]; b += v[i] * v[i]; } return d / Math.sqrt(a * b); };
async function passage(title, qv) {
  const rows = v5.prepare("SELECT body, vec FROM chunks WHERE title = ? COLLATE NOCASE").all(title);
  if (rows.length) return rows.map((r) => [cos(qv, r.vec), r.body]).sort((a, b) => b[0] - a[0])[0][1];
  const t2 = title.includes(": ") ? title.split(": ").slice(1).join(": ") : title;
  for (const db of f2) for (const t of [title, t2]) {
    const a = db.prepare("SELECT block_id, off, len FROM articles WHERE title = ? COLLATE NOCASE ORDER BY views DESC LIMIT 1").get(t);
    if (a) { const z = db.prepare("SELECT zdata FROM blocks WHERE id = ?").get(a.block_id).zdata; const buf = await zstdDec(Buffer.from(z)); return buf.subarray(a.off, a.off + a.len).toString("utf8").slice(0, 1500); }
  }
  return null;
}
const src = JSON.parse(fs.readFileSync("sources.json", "utf8"));
const questions = Object.fromEntries(fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => { const x = JSON.parse(l); return [x.id, x.question]; }));
const byItem = new Map();
for (const s of src) if (s.key !== null && s.cos !== null) { const k = `${s.run}|${s.id}`; byItem.set(k, [...(byItem.get(k) ?? []), s]); }
let t0 = Date.now(), nDocs = 0, tokens = 0;
const pairs = { cos: [0, 0], rr: [0, 0] }; const items = [];
for (const [k, ss] of byItem) {
  if (!ss.some((s) => s.key) || !ss.some((s) => !s.key)) continue;
  const q = questions[ss[0].id]; const qv = Float32Array.from((await emb.getEmbeddingFor(q)).vector);
  const docs = []; for (const s of ss) docs.push((await passage(s.title, qv)) ?? s.title);
  const t1 = Date.now(); const scores = await rr.rankAll(q, docs.map((d) => d.slice(0, 1200))); nDocs += docs.length; tokens += docs.reduce((n, d) => n + d.slice(0, 1200).length / 4, 0);
  ss.forEach((s, i) => (s.rr = scores[i]));
  for (const a of ss.filter((s) => s.key)) for (const b of ss.filter((s) => !s.key)) {
    pairs.cos[0] += a.cos > b.cos ? 1 : a.cos === b.cos ? 0.5 : 0; pairs.cos[1]++;
    pairs.rr[0] += a.rr > b.rr ? 1 : a.rr === b.rr ? 0.5 : 0; pairs.rr[1]++;
  }
  const top = (f) => [...ss].sort((x, y) => y[f] - x[f])[0];
  items.push({ k, q: q.slice(0, 70), topCos: `${top("cos").title}${top("cos").key ? " (KEY)" : ""}`, topRR: `${top("rr").title}${top("rr").key ? " (KEY)" : ""}`, srcs: ss.map((s) => `${s.key ? "*" : ""}${s.title} cos=${s.cos.toFixed(2)} rr=${s.rr.toFixed(2)}${s.kept ? " [kept]" : ""}`) });
}
const elapsed = Date.now() - t0;
console.log(`items with key and non-key sources: ${items.length}; pairs ${pairs.cos[1]}`);
console.log(`within-item AUC  cosine ${(pairs.cos[0] / pairs.cos[1]).toFixed(3)}  |  reranker ${(pairs.rr[0] / pairs.rr[1]).toFixed(3)}`);
console.log(`top-1 is key-bearing: cosine ${items.filter((i) => i.topCos.endsWith("(KEY)")).length}/${items.length}  reranker ${items.filter((i) => i.topRR.endsWith("(KEY)")).length}/${items.length}`);
console.log(`reranker throughput (M-series CPU/Metal, desktop): ${nDocs} docs, ~${Math.round(tokens)} tokens in ~${elapsed} ms incl. embedding+IO`);
for (const i of items) console.log(`\n${i.k} | ${i.q}\n  top cos: ${i.topCos}\n  top rr : ${i.topRR}\n  ${i.srcs.join("\n  ")}`);
fs.writeFileSync(process.env.OUT ?? "rerank.json", JSON.stringify(items, null, 1));
