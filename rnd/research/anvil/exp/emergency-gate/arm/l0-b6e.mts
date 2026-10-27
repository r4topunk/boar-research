// L0 parity (Anvil B6E arm): the ENGINE's routeGateMessages + routeGateVerdict, with top-20 pieces exactly as the desktop
// runner primitive returns them (runner-b4gate.patch: getChatTemplate-free Qwen chatml, detokenize([t], true)), on the dev pool +
// chat v0 + v0.1. Compares emergency/search decisions to the frozen gate-only run (emergency-gate/runs/g3-4b-B6E.jsonl).
//   npx tsx l0-b6e.mts <tree> <out.jsonl>
import fs from "node:fs";
const [tree, outPath] = process.argv.slice(2);
const G = await import(`${tree}/src/routing/routeGate.ts`);
const D = "<workspace>/rnd/research/anvil/exp";
const { getLlama, LlamaChat } = await import("<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js");
const model = await (await getLlama({ gpu: false })).loadModel({ modelPath: "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf", gpuLayers: 0 });
const ctx = await model.createContext({ contextSize: 4096, threads: 4 });
const seq = ctx.getSequence();
const load = (f: string) => fs.readFileSync(f, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const items = [
  ...JSON.parse(fs.readFileSync(`${D}/emergency-gate/pool.json`, "utf8")).map((p: any) => ({ set: "pool", id: p.id, msg: p.msg, history: p.history })),
  ...load(`${D}/chat-routing/slice.items.jsonl`).map((p: any) => ({ set: "v0", id: p.id, msg: p.msg, history: p.history ?? [], route: p.label })),
  ...load(`${D}/chat-routing/arm/v01-gate-items.jsonl`).map((p: any) => ({ set: "v01", id: p.id, msg: p.msg, history: p.history ?? [], route: p.label })),
];
const ref = new Map(load(`${D}/emergency-gate/runs/g3-4b-B6E.jsonl`).map((r: any) => [`${r.set}/${r.id}`, r]));
let prev: number[] = [];
const out: any[] = [];
let emDiff = 0, srDiff = 0, n = 0;
for (const it of items) {
  const turns = it.history.map(([role, text]: [string, string]) => ({ role, text }));
  const msgs = G.routeGateMessages(it.msg, turns.length ? { turns } : null);
  const text = msgs.map((m: any) => `<|im_start|>${m.role}\n${m.content}<|im_end|>\n`).join("") + "<|im_start|>assistant\n";
  const tokens: number[] = model.tokenize(text, true) as any;
  let k = 0; while (k < prev.length && k < tokens.length - 1 && prev[k] === tokens[k]) k++;
  if (seq.nextTokenIndex > k) await seq.eraseContextTokenRanges([{ start: k, end: seq.nextTokenIndex }]);
  const rest = tokens.slice(k);
  const o = await seq.controlledEvaluate(rest.map((t, i) => (i === rest.length - 1 ? [t, { generateNext: { probabilities: true, options: { temperature: 0 } } }] : t)) as any);
  prev = tokens;
  const probs: Map<number, number> = (o as any)[rest.length - 1].next.probabilities;
  const top = [...probs.entries()].sort((a, b) => b[1] - a[1]).slice(0, G.ROUTE_GATE_N_PROBS).map(([t, p]) => ({ token: model.detokenize([t], true), prob: p }));
  const v = G.routeGateVerdict(top);
  const r: any = ref.get(`${it.set}/${it.id}`);
  const rEm = r.pE / (r.pE + r.pS + r.pA) >= 0.5, rSr = r.pS + r.pE >= r.pA;
  n++; if (v.emergency !== rEm) emDiff++; if ((v.decision === "search") !== rSr) srDiff++;
  out.push({ set: it.set, id: it.id, route: it.route, emergency: v.emergency, em: v.emergencyScore, decision: v.decision, score: v.score, mass: v.labelMass, refEm: rEm, refSearch: rSr });
}
fs.writeFileSync(outPath, out.map((x) => JSON.stringify(x)).join("\n") + "\n");
console.log(`L0 parity: ${n} items · emergency decision diffs ${emDiff} · search decision diffs ${srDiff} · label mass < 0.9: ${out.filter((x) => x.mass < 0.9).length}`);
