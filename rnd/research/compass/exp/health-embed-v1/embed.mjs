// Embeds prototypes + eval questions with the exact bge-small q8_0 GGUF BOAR ships, via node-llama-cpp
// (same path as boar-eval's llama-rn shim). No query prefix (symmetric classification).
import { createRequire } from "module";
import fs from "fs";
const require = createRequire("<workspace>/boar-app/package.json");
const { getLlama } = await import(require.resolve("node-llama-cpp"));
const llama = await getLlama({ gpu: false });
const model = await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" });
const ctx = await model.createEmbeddingContext({ contextSize: 512 });
const P = JSON.parse(fs.readFileSync("prototypes.json", "utf8"));
const E = fs.readFileSync("../health-embed/eval.jsonl", "utf8").trim().split("\n").map(JSON.parse);
const emb = async (t) => Array.from((await ctx.getEmbeddingFor(t)).vector);
const out = { pos: [], neg: [], eval: [] };
for (const t of P.pos) out.pos.push(await emb(t));
for (const t of P.neg) out.neg.push(await emb(t));
for (const e of E) out.eval.push(await emb(e.q));
fs.writeFileSync("emb.json", JSON.stringify(out));
console.log("ok", out.pos.length, out.neg.length, out.eval.length, out.eval[0].length);
