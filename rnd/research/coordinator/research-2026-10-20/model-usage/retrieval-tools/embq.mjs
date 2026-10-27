// embeds questions (jsonl of {id,question}) raw and with the BGE v1.5 query instruction; writes JSON {id:{raw:[..],inst:[..]}}
import { readFileSync, writeFileSync } from "node:fs";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const [inp, out] = process.argv.slice(2);
const INST = "Represent this sentence for searching relevant passages: ";
const llama = await getLlama({ gpu: false });
const model = await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" });
const ctx = await model.createEmbeddingContext({ contextSize: 512, threads: 4 });
const res = {};
const toks = {};
for (const line of readFileSync(inp, "utf8").split("\n").filter(Boolean)) {
  const { id, question } = JSON.parse(line);
  res[id] = { raw: Array.from((await ctx.getEmbeddingFor(question)).vector), inst: Array.from((await ctx.getEmbeddingFor(INST + question)).vector) };
}
const t = model.tokenize("What is the capital of Kyrgyzstan?");
const pre = [...t]; ctx._prepareInput ? ctx._prepareInput(pre) : null;
console.log("tokens(no specials)", JSON.stringify(t), "with specials", JSON.stringify(pre), "bos", model.tokens.bos, "sep", model.tokens.sep);
writeFileSync(out, JSON.stringify(res));
await ctx.dispose(); await model.dispose();
