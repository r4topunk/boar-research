// Addendum diagnostic (0 LLM): global top-10 by cosine over ALL wiki-vital5 chunk vectors (what a full dense scan of the
// format-1 pack would return), vs the engine's format-1 path (cosine re-rank of the bm25 top-400 pool only).
import { DatabaseSync } from "node:sqlite";
import { writeFileSync } from "node:fs";
const B = "<workspace>";
const pure: any = await import(`${B}/kiln-local/be-0cfd4a77-cut7-litepacks/src/rag/pure.ts`);
const { getLlama } = await import(`${B}/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js`);
const llama = await getLlama({ gpu: false });
const model = await llama.loadModel({ modelPath: `${B}/shared-models/bge-small-en-v1.5-q8_0.gguf` });
const ec = await model.createEmbeddingContext({ contextSize: 512 });
const db = new DatabaseSync(`${B}/shared-data/packs/wiki-vital5.sqlite`, { readOnly: true });
const rows = db.prepare("SELECT id, title, vec FROM chunks").all() as any[];
const qs: [string, string][] = [
  ["b13", "How mosquitoes spread disease, and why HIV isn't one of them"],
  ["b15", "Kyoto's role in Japanese history and culture"],
  ["b19", "Travelling in Brazil: plugs, voltage and emergency numbers"],
  ["b20", "Japan and Germany compared: population density and an aging society"],
];
const out: any = {};
for (const [id, q] of qs) {
  const qv = Float32Array.from((await ec.getEmbeddingFor(q)).vector);
  const t0 = performance.now();
  const s = rows.map((r) => ({ id: r.id, title: r.title, sim: pure.cosineSimilarityInt8(qv, new Uint8Array(r.vec)) })).sort((a, b) => b.sim - a.sim).slice(0, 10);
  out[id] = { ms: Math.round(performance.now() - t0), top: s.map((x) => ({ ...x, sim: +x.sim.toFixed(4) })) };
  console.log(id, `${out[id].ms} ms`, s.map((x) => `${x.title}#${x.id}:${x.sim.toFixed(3)}`).join(" | "));
}
writeFileSync(process.argv[2], JSON.stringify(out, null, 1));
process.exit(0);
