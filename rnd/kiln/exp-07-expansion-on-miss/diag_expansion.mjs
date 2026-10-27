// exp-07 diagnostic: the raw expansion line each model writes (same system prompt, temp 0, 48 tokens) for the fired ids.
import { getLlama, LlamaChatSession } from "node-llama-cpp";
import { readFileSync } from "node:fs";
const SYSTEM = "You help an offline encyclopedia search. Reply with ONE line only: 4 to 6 search terms separated by commas, " +
  "for the user's question. Use synonyms, words the answering article would use, and the names of specific " +
  "candidate entities (for 'tallest animal': giraffe; for 'largest country': Russia). No explanations, no numbering.";
const ids = process.argv[3].split(",");
const qs = readFileSync("kiln/questions.vitalik58.jsonl", "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)).filter((q) => ids.includes(q.id));
const llama = await getLlama({ gpu: false });
const model = await llama.loadModel({ modelPath: process.argv[2] });
for (const q of qs) {
  const ctx = await model.createContext({ contextSize: 2048, threads: 4, seed: 42 });
  const s = new LlamaChatSession({ contextSequence: ctx.getSequence(), systemPrompt: SYSTEM });
  const out = await s.prompt(q.question, { maxTokens: 48, temperature: 0 });
  console.log(JSON.stringify({ id: q.id, q: q.question, raw: out }));
  await ctx.dispose();
}
