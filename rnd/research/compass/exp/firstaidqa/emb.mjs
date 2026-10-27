import { createRequire } from "module"; import fs from "fs";
const require = createRequire("<workspace>/boar-app/package.json");
const { getLlama } = await import(require.resolve("node-llama-cpp"));
const llama = await getLlama({ gpu: false });
const ctx = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext({ contextSize: 512 });
const S = JSON.parse(fs.readFileSync("sample400.json", "utf8")); const out = {};
for (const t of S) out[t] = Array.from((await ctx.getEmbeddingFor(t)).vector);
fs.writeFileSync("emb.json", JSON.stringify(out)); console.log("ok", S.length);
