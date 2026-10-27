// MICROD2Q generation on Metal (declared build change, coordinator 2026-10-14): node-llama-cpp 3.21.1 (wt/eval/eval/node_modules,
// prebuilt @node-llama-cpp/mac-arm64-metal), same GGUF (Qwen3-4B-Instruct-2507-Q4_K_M, sha 3605803b...), all layers on GPU,
// one context with 4 sequences (= -np 4), 4 prompts in flight. Prompt = gen.mjs prompt() rendered with the GGUF's own chat
// template for one user message (no system): "<|im_start|>user\n{p}<|im_end|>\n<|im_start|>assistant\n"; LlamaCompletion,
// temperature 0.7, topP 0.9, maxTokens 160, seed 42 (+ topK 40, minP 0.05 = the llama-server defaults the CPU run inherited);
// the prompt is tokenized with special tokens on. Output lines = gen.mjs format. Resumable.
// usage: node gen_metal.mjs <list.json> <out.jsonl>
import { readFileSync, existsSync, appendFileSync } from "node:fs";
import { chunkInfo, prompt } from "./gen.mjs";
const ROOT = "<workspace>";
const { getLlama, LlamaCompletion } = await import(`${ROOT}/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js`);
const [listF, out] = process.argv.slice(2);
const list = JSON.parse(readFileSync(listF, "utf8"));
const done = new Set(existsSync(out) ? readFileSync(out, "utf8").split("\n").filter(Boolean).map((l) => { const o = JSON.parse(l); return `${o.pack}:${o.chunk}`; }) : []);
const todo = list.filter((t) => !done.has(`${t.pack}:${t.chunk}`));
const llama = await getLlama({ gpu: "metal" });
const model = await llama.loadModel({ modelPath: `${ROOT}/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf`, gpuLayers: "max" });
const context = await model.createContext({ sequences: Number(process.env.D2Q_SEQ ?? 4), contextSize: 8192, batchSize: 2048 });
console.error(`gpu ${llama.gpu} layers ${model.gpuLayers} todo ${todo.length} of ${list.length}`);
let next = 0, n = 0, ptok = 0, ctok = 0; const t0 = Date.now();
async function worker() {
  const seq = context.getSequence();
  const comp = new LlamaCompletion({ contextSequence: seq });
  while (next < todo.length) {
    const t = todo[next++]; const x = chunkInfo(t.pack, t.chunk); const ts = Date.now();
    const text = `<|im_start|>user\n${prompt(x)}<|im_end|>\n<|im_start|>assistant\n`;
    let raw = null, err = null, finish = null, usage = null;
    try {
      await seq.clearHistory();
      const r = await comp.generateCompletionWithMeta(model.tokenize(text, true), { temperature: 0.7, topP: 0.9, topK: 40, minP: 0.05, maxTokens: 160, seed: 42 });
      raw = r.response.replace(/<\|im_end\|>\s*$/, "").trim(); finish = r.metadata?.stopReason === "maxTokens" ? "length" : "stop";
      const pt = model.tokenize(text, true).length, ct = model.tokenize(r.response).length; ptok += pt; ctok += ct;
      usage = { prompt_tokens: pt, completion_tokens: ct };
    } catch (e) { err = String(e); }
    appendFileSync(out, JSON.stringify({ pack: t.pack, chunk: t.chunk, article_id: x.article_id, title: x.title, section: x.section, chars: x.text.length,
      raw, finish, usage, ms: Date.now() - ts, err, backend: "node-llama-cpp-3.21.1-metal" }) + "\n");
    n++; if (n % 100 === 0) console.error(`${new Date().toISOString().slice(11, 19)} ${n}/${todo.length} ${((Date.now() - t0) / 1000 / n).toFixed(2)} s/chunk`);
  }
}
await Promise.all(Array.from({ length: Number(process.env.D2Q_SEQ ?? 4) }, worker));
const s = (Date.now() - t0) / 1000;
console.error(`DONE ${n} in ${s.toFixed(0)} s = ${(s / Math.max(n, 1)).toFixed(3)} s/chunk; mean prompt ${(ptok / Math.max(n, 1)).toFixed(0)} tok, completion ${(ctok / Math.max(n, 1)).toFixed(0)} tok`);
await context.dispose(); await model.dispose(); await llama.dispose();
