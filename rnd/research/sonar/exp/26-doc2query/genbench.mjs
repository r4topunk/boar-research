const { getLlama, LlamaChatSession } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
import fs from "node:fs";
const model = process.argv[2], N = Number(process.argv[3] ?? 8);
const c = JSON.parse(fs.readFileSync("cands.json", "utf8")).packs.wv.chunks.slice(0, N);
const llama = await getLlama({ logLevel: "error" });
const m = await llama.loadModel({ modelPath: model });
const ctx = await m.createContext({ contextSize: 768 * N, sequences: N, batchSize: 2048 });
const t0 = Date.now(); let toks = 0;
const outs = await Promise.all(c.map(async (ch, i) => {
  const s = new LlamaChatSession({ contextSequence: ctx.getSequence(), systemPrompt: "You write search questions." });
  const p = `Passage from "${ch.title}"${ch.section ? ` (section: ${ch.section})` : ""}:\n${ch.body.slice(0, 1200)}\n\nWrite 5 different short questions a traveller or student might type that this passage answers. Use words a person would use, not only the passage's words. One per line, no numbering.`;
  const a = await s.prompt(p, { temperature: 0, maxTokens: 160 });
  toks += m.tokenize(a).length; return a;
}));
console.log(`${model.split("/").pop()} N=${N}: ${((Date.now() - t0) / 1000).toFixed(1)} s, ${toks} out tok, ${(toks / ((Date.now() - t0) / 1000)).toFixed(0)} tok/s`);
console.log(outs[0]); console.log(outs[1]);
