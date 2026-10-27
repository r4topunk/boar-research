// Closed-book local-model anchors (Anvil out-of-kit front): the harness anchor recipe (boar-eval harness/anchors.mjs: system
// prompt anchor.v1 = reference.v1 minus web lines, user = bare question, no tools) with a local GGUF via node-llama-cpp
// (desktop CPU, the GGUF's own chat template, app sampler temp 0.7 seed 42, max 450 tokens). Writes EvalTrace v1 so
// harness/judge.mjs judges it like any run. Proxy for "what this model answers from memory" on out-of-kit items.
//   npx tsx local-anchors.mts --gguf <path> --name <id> --ids a,b,... --out <traces.jsonl> [--threads 4]
import fs from "node:fs"; import crypto from "node:crypto";
const a = process.argv.slice(2), get = (k: string, d?: string) => (a.includes(k) ? a[a.indexOf(k) + 1] : d);
const gguf = get("--gguf")!, name = get("--name")!, out = get("--out")!, ids = new Set(get("--ids")!.split(","));
const B = "<workspace>/boar-eval";
const src = fs.readFileSync(`${B}/harness/anchors.mjs`, "utf8");
const ANCHOR_SYSTEM = src.match(/export const ANCHOR_SYSTEM = `([\s\S]*?)`;/)![1];
const promptSha = crypto.createHash("sha256").update(ANCHOR_SYSTEM).digest("hex");
const qs = fs.readFileSync(`${B}/bench/v0.1/questions.public.jsonl`, "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((q: any) => ids.has(q.id));
const done = new Set(fs.existsSync(out) ? fs.readFileSync(out, "utf8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l).itemId) : []);
const { getLlama, LlamaChatSession, resolveChatWrapper } = await import("<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js");
const llama = await getLlama({ gpu: false });
const model = await llama.loadModel({ modelPath: gguf, gpuLayers: 0 });
const ctx = await model.createContext({ contextSize: 2048, threads: Number(get("--threads", "4")) });
const noThink = a.includes("--no-think");
const wrapper = noThink ? resolveChatWrapper(model, { customWrapperSettings: { qwen: { thoughts: "discourage" }, jinjaTemplate: { additionalRenderParameters: { enable_thinking: false } } } } as any) : undefined;
const seq = ctx.getSequence();
console.log(`${name}: ${qs.length} items (${done.size} done), anchor.v1 sha ${promptSha.slice(0, 8)}`);
for (const q of qs) {
  if (done.has(q.id)) continue;
  await seq.clearHistory();
  const session = new LlamaChatSession({ contextSequence: seq, systemPrompt: ANCHOR_SYSTEM, ...(wrapper ? { chatWrapper: wrapper } : {}) });
  const t0 = performance.now(); let first: number | null = null; let n = 0;
  const raw = await session.prompt(q.question, { maxTokens: 450, temperature: Number(get("--temp", "0.7")), seed: 42, ...(noThink ? { budgets: { thoughtTokens: 0 } } : {}), onTextChunk: () => { n++; if (first === null) first = performance.now(); } } as any);
  const thinking = /<think>/.test(raw); const text = raw.replace(/<think>[\s\S]*?<\/think>/g, "");
  const totalMs = performance.now() - t0;
  session.dispose({ disposeSequence: false });
  const trace = {
    protocol: "1.0.0", runId: `outofkit-local-${name}`, itemId: q.id, question: q.question,
    engine: { commit: "n/a-anchor", arm: `anchor-local-${name}`, dirty: false },
    runtime: { adapter: "local-anchor", host: "MacBook CPU x4 (node-llama-cpp 3.21.1)", model: name, sampler: { temperature: 0.7, seed: 42 }, versions: { prompt: "anchor.v1", promptSha256: promptSha, gguf } },
    config: { commit: "n/a-anchor", arm: `anchor-local-${name}`, modelId: name, settings: { promptVersion: "anchor.v1", tools: [], web: false, thinking: !noThink }, kit: [], device: null },
    route: { task: null, tier: null, outcome: "answered", reasonCodes: [] },
    retrieval: { raw: [], kept: [], dropped: [] },
    answer: { text: text.trim(), cited: [], shown: [], declined: false, weakSources: false, warnings: thinking ? ["thinking-present"] : [] },
    timing: { ttftMs: first === null ? null : Math.round(first - t0), totalMs: Math.round(totalMs), retrievalMs: null, prefillMs: null, decodeTokPerSec: null, promptTokens: null, outputTokens: n },
    resources: null, events: [], error: text.trim() ? null : "empty-answer", createdAt: new Date().toISOString(),
  };
  fs.appendFileSync(out, JSON.stringify(trace) + "\n");
  console.log(`${q.id} ${(totalMs / 1000).toFixed(1)}s ${text.trim().slice(0, 60).replace(/\n/g, " ")}`);
}
