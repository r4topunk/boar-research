// L0 parity (Anvil, B4 arm): the arm's routeGate.ts (prompt, fold, verdict) + the runner's ChatML/controlledEvaluate path
// must reproduce runs-slice-q4b-b4.jsonl decisions on Compass chat-slice v0.  npx tsx l0-parity.mts <engineTree> <gguf> <out.jsonl>
import fs from "node:fs";
const [tree, gguf, outPath] = process.argv.slice(2);
const G = await import(`${tree}/src/routing/routeGate.ts`);
const { getLlama } = await import("<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js");
const llama = await getLlama({ gpu: false });
const model = await llama.loadModel({ modelPath: gguf, gpuLayers: 0 });
const ref = new Map(fs.readFileSync(new URL("../runs-slice-q4b-b4.jsonl", import.meta.url), "utf8").trim().split("\n").map((l) => JSON.parse(l)).map((r) => [r.id, r]));
const items = fs.readFileSync(process.env.ITEMS ?? new URL("../slice.items.jsonl", import.meta.url), "utf8").trim().split("\n").map((l) => JSON.parse(l));
const out = fs.createWriteStream(outPath);
let same = 0, n = 0;
for (const it of items) {
  const turns = (it.history ?? []).map(([role, text]: [string, string]) => ({ role, text }));
  const messages = G.routeGateMessages(it.msg, turns.length ? { turns } : null);
  const text = messages.map((m: any) => `<|im_start|>${m.role}\n${m.content}<|im_end|>\n`).join("") + "<|im_start|>assistant\n";
  const tokens = model.tokenize(text, true);
  const ctx = await model.createContext({ contextSize: Math.max(2048, tokens.length + 16), threads: 4 });
  const t0 = performance.now();
  const o = await ctx.getSequence().controlledEvaluate(tokens.map((t: any, i: number) => (i === tokens.length - 1 ? [t, { generateNext: { probabilities: true, token: true, options: { temperature: 0 } } }] : t)) as any);
  const ms = performance.now() - t0;
  await ctx.dispose();
  const probs: Map<number, number> = (o as any)[tokens.length - 1].next.probabilities;
  const top = [...probs.entries()].sort((a, b) => b[1] - a[1]).slice(0, G.ROUTE_GATE_N_PROBS).map(([t, p]) => ({ token: model.detokenize([t], true), prob: p }));
  const v = G.routeGateVerdict(top);
  const r = ref.get(it.id) ?? { B: { decision: "SEARCH", score: null, promptTokens: null } };
  const refDecision = r.B.decision === "SEARCH" ? "search" : "answer";
  n++; if (v.decision === refDecision) same++;
  out.write(JSON.stringify({ id: it.id, label: it.label, decision: v.decision, score: v.score, labelMass: v.labelMass, ref: refDecision, refScore: r.B.score, promptTokens: tokens.length, refPromptTokens: r.B.promptTokens, ms: Math.round(ms) }) + "\n");
  console.log(it.id, v.decision, v.score?.toFixed(3), refDecision, r.B.score, tokens.length, r.B.promptTokens);
}
out.end();
console.log(`PARITY ${same}/${n}`);
