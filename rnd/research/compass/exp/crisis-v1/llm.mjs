import { createRequire } from "module"; import fs from "fs";
const require = createRequire("<workspace>/boar-app/package.json");
const { getLlama, LlamaChatSession } = await import(require.resolve("node-llama-cpp"));
const llama = await getLlama();
const model = await llama.loadModel({ modelPath: `<workspace>/shared-models/${process.argv[2]}` });
const ctx = await model.createContext({ contextSize: 1024 }); const seq = ctx.getSequence();
const grammar = await llama.createGrammar({ grammar: 'root ::= "yes" | "no"' });
const SYS = fs.readFileSync(process.argv[4] ?? "prompt.txt", "utf8").trim();
const rows = JSON.parse(fs.readFileSync("rows.json", "utf8")); const out = {}; let ms = 0;
for (const r of rows) {
  const s = new LlamaChatSession({ contextSequence: seq, systemPrompt: SYS }); const t = Date.now();
  out[r.id] = (await s.prompt(`Message: ${r.q}`, { grammar, temperature: 0, maxTokens: 2 })).trim();
  ms += Date.now() - t; s.dispose({ disposeSequence: false }); await seq.clearHistory();
}
fs.writeFileSync(process.argv[3], JSON.stringify(out)); console.log("ok", rows.length, "avg ms", Math.round(ms / rows.length));
