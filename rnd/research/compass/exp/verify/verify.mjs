// Verifier candidates on declined compact drafts: bge-small cosine (draft vs best source chunk) and a resident-LLM yes/no.
import { createRequire } from "module"; import fs from "fs";
const require = createRequire("<workspace>/boar-app/package.json");
const { getLlama, LlamaChatSession } = await import(require.resolve("node-llama-cpp"));
const llama = await getLlama();
const M = "<workspace>/shared-models/";
const emb = await (await llama.loadModel({ modelPath: M + "bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext({ contextSize: 512 });
const vec = async (t) => { const v = (await emb.getEmbeddingFor(t.slice(0, 1500))).vector; const n = Math.hypot(...v); return Array.from(v, (x) => x / n); };
const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0);
const D = JSON.parse(fs.readFileSync("drafts.json", "utf8"));
for (const d of D) {
  const clean = d.draft.replace(/\[\d+\]/g, "").trim(); const dv = await vec(clean);
  const chunks = [];
  for (const s of d.sources) for (let i = 0; i < s.text.length; i += 1000) chunks.push({ title: s.title, text: s.text.slice(i, i + 1000) });
  for (const c of chunks) c.sim = dot(dv, await vec(`${c.title}\n${c.text}`));
  chunks.sort((a, b) => b.sim - a.sim);
  d.cos = chunks[0]?.sim ?? 0; d.passages = chunks.slice(0, 2);
}
const SYS = fs.readFileSync("verify-prompt.txt", "utf8").trim();
const grammar = await llama.createGrammar({ grammar: 'root ::= "yes" | "no"' });
for (const name of ["Qwen2.5-1.5B-Instruct-Q4_K_M.gguf", "Qwen3-4B-Instruct-2507-Q4_K_M.gguf"]) {
  const ctx = await (await llama.loadModel({ modelPath: M + name })).createContext({ contextSize: 2048 }); const seq = ctx.getSequence(); let ms = 0;
  for (const d of D) {
    const src = d.passages.map((p, i) => `[${i + 1}] ${p.title}: ${p.text}`).join("\n\n");
    const s = new LlamaChatSession({ contextSequence: seq, systemPrompt: SYS }); const t = Date.now();
    d[name.startsWith("Qwen3") ? "v4b" : "v15"] = d.passages.length ? (await s.prompt(`Sources:\n${src}\n\nQuestion: ${d.question}\nAnswer: ${d.draft.replace(/\[\d+\]/g, "").trim()}\n\nDo the sources state the answer's main claim?`, { grammar, temperature: 0, maxTokens: 2 })).trim() : "no";
    ms += Date.now() - t; s.dispose({ disposeSequence: false }); await seq.clearHistory();
  }
  console.log(name, "avg ms", Math.round(ms / D.length)); await ctx.dispose();
}
fs.writeFileSync("verified.json", JSON.stringify(D.map(({ sources, ...d }) => d), null, 0));
