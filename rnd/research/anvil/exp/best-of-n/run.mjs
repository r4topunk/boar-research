// Best-of-n on Qwen3-4B (desktop quality proxy): Kiln exp-01 captured prompts (lantern52, 40 with sources), n samples
// at temp 0.7 (seeds 1..n), app sampler otherwise. Writes all samples; selection is done in select.py.
import fs from "node:fs";
import { createRequire } from "node:module";
const require = createRequire("<workspace>/boar-app/package.json");
const { getLlama, LlamaChatSession } = await import(require.resolve("node-llama-cpp"));
const N = Number(process.argv[2] ?? 4), out = process.argv[3];
const rows = fs.readFileSync("<workspace>/rnd/kiln/exp-01-inram-moe-reader/capture/lantern52.jsonl", "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((r) => r.promptSources?.length);
const llama = await getLlama();
const model = await llama.loadModel({ modelPath: "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf" });
const context = await model.createContext({ contextSize: 4096 });
const w = fs.createWriteStream(out);
for (const r of rows) {
  const msgs = r.kilnCaptured[0].messages;
  const samples = [];
  for (let s = 1; s <= N; s++) {
    const seq = context.getSequence();
    const session = new LlamaChatSession({ contextSequence: seq, systemPrompt: msgs.find((m) => m.role === "system").content });
    const t = await session.prompt(msgs.find((m) => m.role === "user").content, { temperature: 0.7, topK: 40, topP: 0.95, minP: 0.05, seed: s, maxTokens: 512 });
    session.dispose(); seq.dispose();
    samples.push(t.trim());
  }
  w.write(JSON.stringify({ queryId: r.queryId, category: r.category, sources: r.promptSources, samples }) + "\n");
}
w.end(); await context.dispose(); await model.dispose();
