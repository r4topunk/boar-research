// exp-40 (Sonar, dev): the Gríma false correction under different contexts. The engine's own fast-tier prompt (system text
// + "Context:" block + response-style suffix, from the and-qwen-s44 --dump-prompts run, as in Anvil's gen_oracle.mts),
// 4B Q4_K_M, app sampler, seeds 42-44. Context variants in contexts.json. Writes answers.jsonl.
import fs from "node:fs";
const dump = fs.readFileSync("<workspace>/boar-eval/runs/and-qwen-s44/and-qwen-s44.prompts.jsonl", "utf8").trim().split("\n").map((l) => JSON.parse(l));
const withCtx = dump.find((r: any) => r.messages[0].content.includes("\n\nContext:\n"));
const SYS = withCtx.messages[0].content.split("\n\nContext:\n")[0];
const qs = new Map(fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").trim().split("\n").map((l) => JSON.parse(l)).map((q: any) => [q.id, q.question]));
const wq = qs.get(withCtx.itemId) as string; const STYLE = (withCtx.messages.at(-1).content as string).slice(wq.length);
const C = JSON.parse(fs.readFileSync("contexts.json", "utf8"));
const Q = process.argv[2] ?? "Why does Gríma kill Saruman in The Lord of the Rings?";
const { getLlama, LlamaChatSession } = await import("<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js");
const model = await (await getLlama({ gpu: false })).loadModel({ modelPath: "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf", gpuLayers: 0 });
const ctx = await model.createContext({ contextSize: 4096, threads: 6 }); const seq = ctx.getSequence();
const out = fs.createWriteStream("answers.jsonl", { flags: "a" });
for (const [name, ps] of Object.entries<any[]>(C)) for (const seed of [42, 43, 44]) {
  const context = ps.map((p, i) => `[${i + 1}] ${p.label}: ${p.title.replace(/^Wikivoyage: /, "")}\n${p.text}`).join("\n\n");
  const system = ps.length ? `${SYS}\n\nContext:\n${context}` : SYS;
  await seq.clearHistory();
  const s = new LlamaChatSession({ contextSequence: seq, systemPrompt: system });
  const a = (await s.prompt(Q + STYLE, { maxTokens: 400, temperature: 0.7, topK: 40, topP: 0.95, minP: 0.05, seed } as any)).replace(/<think>[\s\S]*?<\/think>/g, "").trim();
  s.dispose({ disposeSequence: false });
  const denies = /\b(does not|doesn't|did not|didn't|never)\s+(actually\s+)?(kill|murder|stab)/i.test(a) || /\bnot killed by Gr[ií]ma\b/i.test(a);
  const why = /\b(Lotho|reveal|abus|insult|kick|beat|cruel|humiliat|mistreat|contempt)/i.test(a);
  out.write(JSON.stringify({ q: Q, ctx: name, seed, denies, why, answer: a }) + "\n");
  console.log(name, seed, denies ? "DENIES" : "ok", why ? "why" : "-", "|", a.slice(0, 150).replace(/\n/g, " "));
}
out.end();
