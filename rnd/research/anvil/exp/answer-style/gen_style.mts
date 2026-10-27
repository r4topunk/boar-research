// Answer-style replay (Anvil, pre-registered PREREG.md): the engine's real fast-tier prompts (and-qwen-s44 dump) with only the
// two style strings substituted per variants.json. 4B, node-llama-cpp CPU, app sampler, nPredict 512. EvalTrace out.
//   npx tsx gen_style.mts <variant> <seed>
import fs from "node:fs";
const D = "<workspace>/rnd/research/anvil/exp/answer-style";
const [variant, seedS] = process.argv.slice(2); const seed = Number(seedS);
const V = JSON.parse(fs.readFileSync(`${D}/variants.json`, "utf8")); const v = V.variants[variant];
const ids = new Set(fs.readFileSync("<workspace>/rnd/research/anvil/exp/outofkit/v01-en-ids.txt", "utf8").trim().split(","));
const dump = fs.readFileSync("<workspace>/boar-eval/runs/and-qwen-s44/and-qwen-s44.prompts.jsonl", "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((r: any) => ids.has(r.itemId));
const out = `${D}/runs/${variant}-s${seed}.traces.jsonl`;
const done = new Set(fs.existsSync(out) ? fs.readFileSync(out, "utf8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l).itemId) : []);
const { getLlama, LlamaChatSession } = await import("<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js");
const model = await (await getLlama({ gpu: false })).loadModel({ modelPath: "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf", gpuLayers: 0 });
const ctx = await model.createContext({ contextSize: 4096, threads: 4 });
const seq = ctx.getSequence();
let subs = 0;
for (const r of dump) {
  if (done.has(r.itemId)) continue;
  let system: string = r.messages[0].content, user: string = r.messages.at(-1).content;
  if (v.sys) { if (!system.includes(V.replace_sys)) throw new Error(`sys string missing ${r.itemId}`); system = system.replace(V.replace_sys, v.sys); subs++; }
  if (v.user) { if (!user.includes(V.replace_user)) throw new Error(`user string missing ${r.itemId}`); user = user.replace(V.replace_user, v.user); }
  await seq.clearHistory();
  const session = new LlamaChatSession({ contextSequence: seq, systemPrompt: system });
  const t0 = performance.now(); let n = 0;
  const text = (await session.prompt(user, { maxTokens: 512, temperature: 0.7, topK: 40, topP: 0.95, minP: 0.05, seed, onToken: (t: any) => { n += t.length; } } as any)).trim();
  session.dispose({ disposeSequence: false });
  const outTok = (model.tokenize(text) as any).length;
  fs.appendFileSync(out, JSON.stringify({ protocol: "1.0.0", runId: `style-${variant}-s${seed}`, itemId: r.itemId, question: user.split("\n\n(Response style")[0],
    engine: { commit: "0cfd4a77-prompt", arm: `style-${variant}`, dirty: false }, runtime: { adapter: "style-replay", host: "MacBook CPU x4", model: "qwen3-4b", sampler: { temperature: 0.7, top_k: 40, top_p: 0.95, min_p: 0.05, seed }, versions: { variants: "variants.json" } },
    config: { commit: "0cfd4a77", arm: `style-${variant}`, modelId: "qwen3-4b", settings: {}, kit: [], device: null }, route: { task: null, tier: "fast", outcome: "answered", reasonCodes: [`style:${variant}`] },
    retrieval: { raw: [], kept: [], dropped: [] }, answer: { text, cited: [], shown: [], declined: false, weakSources: false, warnings: [] },
    timing: { ttftMs: null, totalMs: Math.round(performance.now() - t0), retrievalMs: null, prefillMs: null, decodeTokPerSec: null, promptTokens: null, outputTokens: outTok },
    resources: null, events: [], error: text ? null : "empty-answer", createdAt: new Date().toISOString() }) + "\n");
}
console.log(variant, seed, "done; sys substitutions", subs);
