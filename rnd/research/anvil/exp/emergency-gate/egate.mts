// Emergency label gate, gate-only replay (Anvil). Same machinery as B6 gate-eval.mts: cached static prefix, KV erase after the
// common prefix, one forward, p(POS first token)/(p(POS)+p(NEG)). env: S, MODEL=4b|15b, P=E1|E2|CMP, OUT
import fs from "node:fs";
const D = process.env.S!, P = process.env.P!, M = process.env.MODEL ?? "4b";
const sys = fs.readFileSync(`${D}/prompts/${P}.txt`, "utf8").trim();
const [POS, NEG] = P === "CMP" ? ["yes", "no"] : ["EMERGENCY", "OTHER"];
const { getLlama } = await import("<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js");
const file = M === "4b" ? "Qwen3-4B-Instruct-2507-Q4_K_M.gguf" : "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf";
const model = await (await getLlama({ gpu: false })).loadModel({ modelPath: `<workspace>/shared-models/${file}`, gpuLayers: 0 });
const ctx = await model.createContext({ contextSize: 4096, threads: 4 });
const seq = ctx.getSequence();
const posT = (model.tokenize(POS) as number[])[0], negT = (model.tokenize(NEG) as number[])[0];
console.error(`labels ${POS}->${posT} '${model.detokenize([posT])}' ${NEG}->${negT} '${model.detokenize([negT])}'`);
const clip = (t: string) => (t.length > 280 ? t.slice(0, 279) + "…" : t);
const userMsg = (msg: string, hist: [string, string][]) => {
  const turns = hist.slice(-6);
  const body = turns.length ? `Conversation so far:\n${turns.map(([r, t]) => `${r}: ${clip(t)}`).join("\n")}\n\nLast message: ${msg}` : msg;
  return P === "CMP" ? `Message: ${body}` : body;
};
const prefixTok = (model.tokenize(`<|im_start|>system\n${sys}<|im_end|>\n<|im_start|>user\n`, true) as number[]).length;
let prev: number[] = [];
const pool = JSON.parse(fs.readFileSync(`${D}/pool.json`, "utf8"));
const out: any[] = [];
for (const p of pool) {
  const tokens: number[] = model.tokenize(`<|im_start|>system\n${sys}<|im_end|>\n<|im_start|>user\n${userMsg(p.msg, p.history)}<|im_end|>\n<|im_start|>assistant\n`, true) as any;
  let k = 0; while (k < prev.length && k < tokens.length - 1 && prev[k] === tokens[k]) k++;
  if (seq.nextTokenIndex > k) await seq.eraseContextTokenRanges([{ start: k, end: seq.nextTokenIndex }]);
  const rest = tokens.slice(k);
  const t0 = performance.now();
  const o = await seq.controlledEvaluate(rest.map((t, i) => (i === rest.length - 1 ? [t, { generateNext: { probabilities: true, options: { temperature: 0 } } }] : t)) as any);
  const ms = performance.now() - t0;
  prev = tokens;
  const probs: Map<number, number> = (o as any)[rest.length - 1].next.probabilities;
  const pP = probs.get(posT) ?? 0, pN = probs.get(negT) ?? 0, mass = pP + pN;
  out.push({ id: p.id, score: mass > 0 ? pP / mass : null, mass, newTok: tokens.length - prefixTok, ms: Math.round(ms) });
}
fs.writeFileSync(process.env.OUT!, out.map((x) => JSON.stringify(x)).join("\n") + "\n");
console.error(`done ${out.length} prefix ${prefixTok} tok`);
