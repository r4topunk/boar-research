import { createRequire } from "module"; import fs from "fs";
const require = createRequire("<workspace>/boar-app/package.json");
const { getLlama } = await import(require.resolve("node-llama-cpp"));
const llama = await getLlama({ gpu: false });
const emb = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext({ contextSize: 512 });
const vec = async (t) => { const v = (await emb.getEmbeddingFor(t.slice(0, 1500))).vector; const n = Math.hypot(...v); return Array.from(v, (x) => x / n); };
const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0);
const D = JSON.parse(fs.readFileSync("drafts.json", "utf8"));
for (const d of D) {
  const dv = await vec(d.draft.replace(/\[\d+\]/g, "").trim()); let best = 0;
  for (const s of d.sources) for (let i = 0; i < s.text.length; i += 1000) best = Math.max(best, dot(dv, await vec(`${s.title}\n${s.text.slice(i, i + 1000)}`)));
  d.cos = best; delete d.sources;
}
fs.writeFileSync("scored.json", JSON.stringify(D)); console.log("ok", D.length);
