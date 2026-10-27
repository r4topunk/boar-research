// Oracle reader runs (Anvil, dev): the engine's OWN fast-tier prompt (system text + "Context:" block + user message with the
// response-style suffix, taken byte-for-byte from the and-qwen-s44 --dump-prompts run, main 0cfd4a77) with the Context block
// replaced by the oracle passages of ctx-<variant>.jsonl. 4B Q4_K_M, node-llama-cpp CPU, app sampler (0.7/40/0.95/0.05, seed 42),
// nPredict 512. Writes EvalTrace for harness/judge.mjs.   npx tsx gen_oracle.mts <variant> [--gguf path --name id --no-think]
import fs from "node:fs";
const D = "<workspace>/rnd/research/anvil/exp/oracle";
const a = process.argv.slice(2), variant = a[0], get = (k: string, d: string) => (a.includes(k) ? a[a.indexOf(k) + 1] : d);
const gguf = get("--gguf", "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf"), name = get("--name", "qwen3-4b");
const noThink = a.includes("--no-think");
const dump = fs.readFileSync("<workspace>/boar-eval/runs/and-qwen-s44/and-qwen-s44.prompts.jsonl", "utf8").trim().split("\n").map((l) => JSON.parse(l));
const withCtx = dump.find((r: any) => r.messages[0].content.includes("\n\nContext:\n"));
const SYS_PREFIX = withCtx.messages[0].content.split("\n\nContext:\n")[0];
const qs = new Map(fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").trim().split("\n").map((l) => JSON.parse(l)).map((q: any) => [q.id, q]));
const wq = (qs.get(withCtx.itemId) as any).question; const userMsg = withCtx.messages.at(-1).content as string;
if (!userMsg.startsWith(wq)) throw new Error("unexpected user message shape");
const STYLE = userMsg.slice(wq.length); // "\n\n(Response style: …)"
const ctxs = fs.readFileSync(`${D}/ctx-${variant}.jsonl`, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const out = `${D}/runs/${name}-${variant}.traces.jsonl`; fs.mkdirSync(`${D}/runs`, { recursive: true });
const done = new Set(fs.existsSync(out) ? fs.readFileSync(out, "utf8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l).itemId) : []);
const { getLlama, LlamaChatSession, resolveChatWrapper } = await import("<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js");
const model = await (await getLlama({ gpu: false })).loadModel({ modelPath: gguf, gpuLayers: 0 });
const ctx = await model.createContext({ contextSize: 4096, threads: 4 });
const seq = ctx.getSequence();
const wrapper = noThink ? resolveChatWrapper(model, { customWrapperSettings: { qwen: { thoughts: "discourage" }, jinjaTemplate: { additionalRenderParameters: { enable_thinking: false } } } } as any) : undefined;
for (const c of ctxs) {
  if (done.has(c.id)) continue;
  const q: any = qs.get(c.id);
  const context = c.passages.map((p: any, i: number) => `[${i + 1}] ${p.kind === "wiki" ? "Wikipedia" : "Web"}: ${p.title}\n${p.text}`).join("\n\n");
  const system = c.passages.length ? `${SYS_PREFIX}\n\nContext:\n${context}` : SYS_PREFIX;
  await seq.clearHistory();
  const session = new LlamaChatSession({ contextSequence: seq, systemPrompt: system, ...(wrapper ? { chatWrapper: wrapper } : {}) });
  const t0 = performance.now();
  const raw = await session.prompt(q.question + STYLE, { maxTokens: 512, temperature: 0.7, topK: 40, topP: 0.95, minP: 0.05, seed: 42, ...(noThink ? { budgets: { thoughtTokens: 0 } } : {}) } as any);
  session.dispose({ disposeSequence: false });
  const text = raw.replace(/<think>[\s\S]*?<\/think>/g, "").trim();
  const trace = { protocol: "1.0.0", runId: `oracle-${name}-${variant}`, itemId: c.id, question: q.question,
    engine: { commit: "0cfd4a77-prompt", arm: `oracle-${variant}-${name}`, dirty: false },
    runtime: { adapter: "oracle-reader", host: "MacBook CPU x4 (node-llama-cpp 3.21.1)", model: name, sampler: { temperature: 0.7, top_k: 40, top_p: 0.95, min_p: 0.05, seed: 42 }, versions: { prompt: "engine fast-tier prompt from and-qwen-s44 dump", ctx: `ctx-${variant}.jsonl` } },
    config: { commit: "0cfd4a77", arm: `oracle-${variant}-${name}`, modelId: name, settings: {}, kit: [], device: null },
    route: { task: null, tier: "fast", outcome: "answered", reasonCodes: [`oracle:${variant}`, `oracle:passages-${c.passages.length}`] },
    retrieval: { raw: [], kept: c.passages.map((p: any) => ({ title: p.title, sim: p.sim })), dropped: [] },
    answer: { text, cited: [], shown: [], declined: false, weakSources: false, warnings: [] },
    timing: { ttftMs: null, totalMs: Math.round(performance.now() - t0), retrievalMs: null, prefillMs: null, decodeTokPerSec: null, promptTokens: null, outputTokens: null },
    resources: null, events: [], error: text ? null : "empty-answer", createdAt: new Date().toISOString() };
  fs.appendFileSync(out, JSON.stringify(trace) + "\n");
  console.log(c.id, c.passages.length, ((performance.now() - t0) / 1000).toFixed(1) + "s", text.slice(0, 70).replace(/\n/g, " "));
}
