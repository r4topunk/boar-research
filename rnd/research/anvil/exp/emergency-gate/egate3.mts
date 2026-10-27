// Merged 3-label gate (B6 + EMERGENCY), one forward: p(EM), p(SEARCH), p(ANS) from the first tokens. env: S, MODEL, OUT
import fs from "node:fs";
const D = process.env.S!, M = process.env.MODEL ?? "4b", P = process.env.P ?? "B6E";
const sys = fs.readFileSync(`${D}/prompts/${P}.txt`, "utf8").trim();
const { getLlama } = await import("<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js");
const file = M === "4b" ? "Qwen3-4B-Instruct-2507-Q4_K_M.gguf" : "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf";
const model = await (await getLlama({ gpu: false })).loadModel({ modelPath: `<workspace>/shared-models/${file}`, gpuLayers: 0 });
const ctx = await model.createContext({ contextSize: 4096, threads: 4 });
const seq = ctx.getSequence();
const [eT, sT, aT] = ["EMERGENCY", "SEARCH", "ANSWER"].map((w) => (model.tokenize(w) as number[])[0]);
console.error("tokens", [eT, sT, aT].map((t) => model.detokenize([t])));
const clip = (t: string) => (t.length > 280 ? t.slice(0, 279) + "…" : t);
const userMsg = (msg: string, hist: [string, string][]) => {
  const turns = hist.slice(-6);
  return turns.length ? `Conversation so far:\n${turns.map(([r, t]) => `${r}: ${clip(t)}`).join("\n")}\n\nLast message: ${msg}` : msg;
};
const load = (f: string) => fs.readFileSync(f, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const items = [
  ...JSON.parse(fs.readFileSync(`${D}/pool.json`, "utf8")).map((p: any) => ({ set: "pool", ...p })),
  ...load(`${process.env.A}/slice.items.jsonl`).map((p: any) => ({ set: "v0", id: p.id, msg: p.msg, history: p.history ?? [], route: p.label })),
  ...load(`${process.env.A}/arm/v01-gate-items.jsonl`).map((p: any) => ({ set: "v01", id: p.id, msg: p.msg, history: p.history ?? [], route: p.label })),
];
let prev: number[] = [];
const out: any[] = [];
for (const p of items) {
  const tokens: number[] = model.tokenize(`<|im_start|>system\n${sys}<|im_end|>\n<|im_start|>user\n${userMsg(p.msg, p.history)}<|im_end|>\n<|im_start|>assistant\n`, true) as any;
  let k = 0; while (k < prev.length && k < tokens.length - 1 && prev[k] === tokens[k]) k++;
  if (seq.nextTokenIndex > k) await seq.eraseContextTokenRanges([{ start: k, end: seq.nextTokenIndex }]);
  const rest = tokens.slice(k);
  const o = await seq.controlledEvaluate(rest.map((t, i) => (i === rest.length - 1 ? [t, { generateNext: { probabilities: true, options: { temperature: 0 } } }] : t)) as any);
  prev = tokens;
  const pr: Map<number, number> = (o as any)[rest.length - 1].next.probabilities;
  const [pE, pS, pA] = [eT, sT, aT].map((t) => pr.get(t) ?? 0);
  out.push({ set: p.set, id: p.id, route: p.route, pE, pS, pA });
}
fs.writeFileSync(process.env.OUT!, out.map((x) => JSON.stringify(x)).join("\n") + "\n");
console.error("done", out.length);
