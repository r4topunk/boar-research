// Sonar exp-05: sources the lexical topic filter (onSubject/onTopic, answer.ts @0cfd4a77) drops vs keeps, with the
// question↔source cosine the engine could use to rescue them. Traces: Kiln's ios-main-v5-t0 (deterministic) and
// ios-main-s42 (no vital5). Cosine: vital5 = best chunk of the title (int8 vecs), Wikivoyage/crypto = pack lead vector.
// "key" = the source's article contains the item's answer key (tools/key_in_context.py logic), a proxy for "right source".
import { DatabaseSync } from "node:sqlite";
import fs from "node:fs";
import { execFileSync } from "node:child_process";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const R = "<workspace>/boar-eval/runs/night-2026-10-01/";
const Q = Object.fromEntries(fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => { const x = JSON.parse(l); return [x.id, x]; }));
const v5 = new DatabaseSync("<workspace>/shared-data/packs/wiki-vital5.sqlite", { readOnly: true });
const f2 = { wv: new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true }), cr: new DatabaseSync("<workspace>/shared-data/crypto/boar-crypto.sqlite", { readOnly: true }) };
const llama = await getLlama({ logLevel: "error" });
const model = await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" });
const ctx = await model.createEmbeddingContext();
const cache = new Map();
const emb = async (t) => cache.get(t) ?? (cache.set(t, Float32Array.from((await ctx.getEmbeddingFor(t)).vector)), cache.get(t));
const cos = (q, buf) => { const v = new Int8Array(buf.buffer, buf.byteOffset, buf.byteLength); let d = 0, a = 0, b = 0; for (let i = 0; i < v.length; i++) { d += q[i] * v[i]; a += q[i] * q[i]; b += v[i] * v[i]; } return d / Math.sqrt(a * b); };
function sim(q, title) {
  const vs = v5.prepare("SELECT vec FROM chunks WHERE title = ? COLLATE NOCASE").all(title);
  if (vs.length) return Math.max(...vs.map((r) => cos(q, r.vec)));
  const t2 = title.includes(": ") ? title.split(": ").slice(1).join(": ") : title;
  for (const db of [f2.wv, f2.cr]) for (const t of [title, t2]) {
    const r = db.prepare("SELECT v.vec FROM articles a JOIN lead_vecs v ON v.article_id = a.id WHERE a.title = ? COLLATE NOCASE ORDER BY a.views DESC LIMIT 1").get(t);
    if (r) return cos(q, r.vec);
  }
  return null;
}
// key per (item,title) from the python tool (article mode)
const keyed = JSON.parse(execFileSync("python3", ["keys.py"], { encoding: "utf8", maxBuffer: 1 << 26 }));
const out = [];
for (const run of ["ios-main-v5-t0", "ios-main-s42"]) {
  for (const l of fs.readFileSync(R + run + ".traces.jsonl", "utf8").split("\n").filter(Boolean)) {
    const t = JSON.parse(l); const q = Q[t.itemId]; if (!q) continue;
    const ev = t.events.filter((e) => e.type === "sources"); const pre = new Set((ev.at(-1)?.sources ?? []).map((s) => s.title));
    const dropTopic = t.route.reasonCodes.some((c) => c.startsWith("grounding:off-topic-dropped"));
    const qv = await emb(t.question);
    const seen = new Set();
    for (const s of t.retrieval.raw) {
      if (seen.has(s.title)) continue; seen.add(s.title);
      out.push({ run, id: t.itemId, cat: q.category, title: s.title, kept: pre.has(s.title), topicDropRun: dropTopic, cos: sim(qv, s.title), key: keyed[`${t.itemId}|${s.title}`] ?? null });
    }
  }
}
fs.writeFileSync("sources.json", JSON.stringify(out, null, 1));
const dropped = out.filter((r) => !r.kept && r.topicDropRun && r.cos !== null);
console.log(`sources ${out.length}; dropped in runs with off-topic drops (with cosine): ${dropped.length} (key-bearing ${dropped.filter((r) => r.key).length})`);
for (const th of [0.7, 0.75, 0.78, 0.8, 0.82, 0.85]) {
  const resc = dropped.filter((r) => r.cos >= th);
  console.log(`rescue if cos >= ${th}: ${resc.length} rescued; key-bearing ${resc.filter((r) => r.key).length}/${dropped.filter((r) => r.key).length}; non-key ${resc.filter((r) => !r.key).length}/${dropped.filter((r) => !r.key).length}`);
}
console.log("\ndropped sources, by cosine:");
for (const r of dropped.sort((a, b) => b.cos - a.cos)) console.log(`${r.cos.toFixed(3)} ${r.key ? "KEY" : "   "} ${r.run.padEnd(15)} ${r.id.padEnd(12)} ${r.cat.padEnd(16)} ${r.title}`);
await ctx.dispose(); await model.dispose();
