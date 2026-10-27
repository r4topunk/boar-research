// Gate-only replay (Anvil, B6 dev loop). npx tsx gate-eval.mts <tree> [SYS=<prompt.txt>] ; sets: v0 (chat-slice v0), v01 (v0.1 72, all SEARCH), probe
// Reuses the cached static prefix across items (KV erase after the common prefix) — scores match a fresh context to ~1e-4.
import fs from "node:fs";
const [tree] = process.argv.slice(2);
const G = await import(`${tree}/src/routing/routeGate.ts`);
const sys: string = process.env.SYS ? fs.readFileSync(process.env.SYS, "utf8") : G.ROUTE_GATE_SYSTEM;
const { getLlama } = await import("<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js");
const model = await (await getLlama({ gpu: false })).loadModel({ modelPath: "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf", gpuLayers: 0 });
const ctx = await model.createContext({ contextSize: 4096, threads: 4 });
const seq = ctx.getSequence();
let prev: number[] = [];
async function score(it: any) {
  const turns = (it.history ?? []).map(([role, text]: [string, string]) => ({ role, text }));
  const user = G.routeGateMessages(it.msg, turns.length ? { turns } : null)[1].content;
  const tokens: number[] = model.tokenize(`<|im_start|>system\n${sys}<|im_end|>\n<|im_start|>user\n${user}<|im_end|>\n<|im_start|>assistant\n`, true) as any;
  let k = 0; while (k < prev.length && k < tokens.length - 1 && prev[k] === tokens[k]) k++;
  if (seq.nextTokenIndex > k) await seq.eraseContextTokenRanges([{ start: k, end: seq.nextTokenIndex }]);
  const rest = tokens.slice(k);
  const o = await seq.controlledEvaluate(rest.map((t, i) => (i === rest.length - 1 ? [t, { generateNext: { probabilities: true, options: { temperature: 0 } } }] : t)) as any);
  prev = tokens.slice(0, tokens.length);
  const probs: Map<number, number> = (o as any)[rest.length - 1].next.probabilities;
  const top = [...probs.entries()].sort((a, b) => b[1] - a[1]).slice(0, 20).map(([t, p]) => ({ token: model.detokenize([t], true), prob: p }));
  return G.routeGateVerdict(top);
}
const load = (f: string) => fs.readFileSync(f, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const sets: Record<string, any[]> = { v0: load("../slice.items.jsonl"), v01: load("v01-gate-items.jsonl"), probe: load("probe-lookups.jsonl") };
const out: any[] = [];
for (const [name, items] of Object.entries(sets)) {
  const wrong: string[] = []; let fs_ = 0, ms = 0, ok = 0, n = 0;
  for (const it of items) {
    const v = await score(it);
    out.push({ set: name, id: it.id, label: it.label, decision: v.decision, score: v.score });
    if (it.label === "EITHER") continue;
    n++;
    const right = (it.label === "SEARCH") === (v.decision === "search");
    if (right) ok++; else { wrong.push(`${it.id}:${v.score?.toFixed(3)}`); if (it.label === "SEARCH") ms++; else fs_++; }
  }
  console.log(`${name.padEnd(5)} ${ok}/${n}  false-search ${fs_}  missed ${ms}  wrong: ${wrong.join(" ")}`);
}
if (process.env.OUT) fs.writeFileSync(process.env.OUT, out.map((x) => JSON.stringify(x)).join("\n") + "\n");
