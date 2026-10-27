import { readFileSync, writeFileSync } from "node:fs";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const [inp, out] = process.argv.slice(2);
const llama = await getLlama({ gpu: false });
const model = await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" });
const ctx = await model.createEmbeddingContext({ contextSize: 512, threads: 4 });
const res = [];
for (const text of JSON.parse(readFileSync(inp, "utf8"))) {
  const ids = [...model.tokenize(text)]; ctx._prepareInput(ids);
  let vec = null, err = null;
  try { vec = Array.from((await ctx.getEmbeddingFor(text)).vector); } catch (e) { err = String(e.message).slice(0, 80); }
  res.push({ text, ids, vec, err });
}
writeFileSync(out, JSON.stringify(res));
