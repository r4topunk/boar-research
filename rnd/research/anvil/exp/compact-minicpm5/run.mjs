// Offline replay: Kiln exp-01 captured app prompts (lantern52, 40 with sources) on a compact candidate, thinking off
// (jinja enable_thinking=false, as boar-eval's adapter does), scored by the 0cfd4a77 compact citation gate port
// (../cite-exemplar/gate.mjs). Usage: node run.mjs <model.gguf> <temperature> <seed> <out.jsonl>
import fs from "node:fs";
import { createRequire } from "node:module";
import { compactGate } from "../cite-exemplar/gate.mjs";
const require = createRequire("<workspace>/boar-app/package.json");
const { getLlama, LlamaChatSession, resolveChatWrapper } = await import(require.resolve("node-llama-cpp"));
const [MODEL, tempS, seedS, out] = process.argv.slice(2);
const CAPTURE = "<workspace>/rnd/kiln/exp-01-inram-moe-reader/capture/lantern52.jsonl";
const rows = fs.readFileSync(CAPTURE, "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((r) => r.promptSources?.length);
const llama = await getLlama();
const model = await llama.loadModel({ modelPath: MODEL });
const context = await model.createContext({ contextSize: 4096 });
const tmpl = String(model.fileInfo?.metadata?.tokenizer?.chat_template ?? "");
const wrapper = resolveChatWrapper(model, /enable_thinking/.test(tmpl)
  ? { customWrapperSettings: { qwen: { thoughts: "discourage" }, jinjaTemplate: { additionalRenderParameters: { enable_thinking: false } } } } : {});
const w = fs.createWriteStream(out);
for (const r of rows) {
  const msgs = r.kilnCaptured[0].messages;
  const seq = context.getSequence();
  const session = new LlamaChatSession({ contextSequence: seq, systemPrompt: msgs.find((m) => m.role === "system").content, ...(wrapper ? { chatWrapper: wrapper } : {}) });
  const t0 = Date.now(); let firstTextMs = null;
  const raw = await session.prompt(msgs.find((m) => m.role === "user").content, { temperature: Number(tempS), seed: Number(seedS), maxTokens: 512, budgets: { thoughtTokens: 0 } });
  const ms = Date.now() - t0;
  session.dispose(); seq.dispose();
  const g = compactGate(raw, r.promptSources);
  w.write(JSON.stringify({ queryId: r.queryId, category: r.category, temp: Number(tempS), seed: Number(seedS), raw, empty: !raw.trim(), gate: g.code, rawHasCite: g.rawHasCite, declined: g.declined,
    answer: g.declined ? "The passages found don't support this answer." : g.text, ms, thinkLeak: /<think>|<\/think>/.test(raw), outTokens: model.tokenize(raw).length }) + "\n");
}
w.end(); await context.dispose(); await model.dispose();
