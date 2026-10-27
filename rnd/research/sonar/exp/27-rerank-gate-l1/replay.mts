// exp-27 local proxy (NOT the L1): replay and-qwen-s44's dumped prompts for the items the gate changes, base vs gated
// messages, same 4B, temperature 0.7 / top-k 40 / top-p 0.95 / min-p 0.05 / seed 44 (adapter defaults), no engine post-processing.
import fs from "node:fs";
import { gate } from "./rrgate.ts";
const { getLlama, LlamaChatSession } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const dry = JSON.parse(fs.readFileSync("dryrun-tau0.05.json", "utf8")) as any[];
const ids = new Set(dry.filter((r) => r.scored.some((s: any) => !s.kept)).map((r) => r.id));
const llama = await getLlama({ logLevel: "error" });
const rr = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-reranker-v2-m3-q4km.gguf" })).createRankingContext({ contextSize: 1024, threads: 4 });
const m = await llama.loadModel({ modelPath: "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf" });
const gen = async (msgs: any[], nPredict: number) => { const ctx = await m.createContext({ contextSize: 4096, seed: 44 });
  const s = new LlamaChatSession({ contextSequence: ctx.getSequence(), systemPrompt: msgs[0].content });
  const t = await s.prompt(msgs[msgs.length - 1].content, { temperature: 0.7, topK: 40, topP: 0.95, minP: 0.05, seed: 44, maxTokens: nPredict ?? 512 });
  await ctx.dispose(); return t; };
const out: any[] = [];
for (const l of fs.readFileSync("<workspace>/boar-eval/runs/and-qwen-s44/and-qwen-s44.prompts.jsonl", "utf8").split("\n").filter(Boolean)) {
  const x = JSON.parse(l); if (!ids.has(x.itemId)) continue; ids.delete(x.itemId);
  const { messages, info } = await gate(x.messages, (q, d) => rr.rank(q, d), 0.05);
  const base = await gen(x.messages, x.nPredict), arm = await gen(messages, x.nPredict);
  out.push({ id: x.itemId, question: info?.question, dropped: info?.dropped, base, arm });
  console.log(`\n=== ${x.itemId} dropped ${JSON.stringify(info?.dropped)}\nQ: ${info?.question}\nBASE: ${base}\nARM:  ${arm}`);
}
fs.writeFileSync("replay-proxy.json", JSON.stringify(out, null, 1));
