// CPU-only (gpu:false, 4 threads) decode throughput of Qwen3-4B Q4_K_M with N parallel sequences on one context
// (node-llama-cpp batches the sequences' decode steps together). Same prompt in every sequence; 64 new tokens each.
import { createRequire } from "node:module";
const require = createRequire("<workspace>/boar-app/package.json");
const { getLlama, LlamaCompletion } = await import(require.resolve("node-llama-cpp"));
const llama = await getLlama({ gpu: false });
const model = await llama.loadModel({ modelPath: "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf" });
const prompt = "Explain in a short paragraph why the Roman Empire split into eastern and western halves, and what each half became.";
for (const n of [1, 2, 4]) {
  const ctx = await model.createContext({ contextSize: 512 * n, sequences: n, threads: 4 });
  const seqs = Array.from({ length: n }, () => ctx.getSequence());
  const t0 = performance.now();
  const outs = await Promise.all(seqs.map((s, i) => new LlamaCompletion({ contextSequence: s })
    .generateCompletion(prompt, { maxTokens: 64, temperature: 0.7, seed: 42 + i, customStopTriggers: [] })));
  const ms = performance.now() - t0;
  const toks = outs.reduce((a, o) => a + model.tokenize(o).length, 0);
  console.log(JSON.stringify({ n, wallS: +(ms / 1000).toFixed(2), totalTokens: toks, aggTokPerS: +(toks / (ms / 1000)).toFixed(1), perSeqTokPerS: +(toks / n / (ms / 1000)).toFixed(1) }));
  await ctx.dispose();
}
await model.dispose();
