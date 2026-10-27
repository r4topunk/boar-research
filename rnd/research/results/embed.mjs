import { createRequire } from "module"; import fs from "fs";
const require = createRequire("<workspace>/boar-app/package.json");
const { getLlama } = await import(require.resolve("node-llama-cpp"));
const llama = await getLlama({ gpu: false });
const model = await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" });
const ctx = await model.createEmbeddingContext({ contextSize: 512 });
const rows = [];
for (const f of process.argv.slice(2)) for (const l of fs.readFileSync(f, "utf8").trim().split("\n")) { const d = JSON.parse(l); rows.push({ set: f.split("/").pop(), id: d.id, q: d.question, danger: d.danger === true || /^(dng|saf)-/.test(d.id), v: Array.from((await ctx.getEmbeddingFor(d.question)).vector) }); }
fs.writeFileSync("emb.json", JSON.stringify(rows)); console.log("ok", rows.length);
