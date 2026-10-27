// B6 ablation on a v0 subset (dev set): VARIANT drops/rewrites prompt lines; prints decisions. npx tsx ablate.mts <tree> <gguf> <ids,…>
import fs from "node:fs";
const [tree, gguf, idsArg] = process.argv.slice(2);
const G = await import(`${tree}/src/routing/routeGate.ts`);
const { getLlama } = await import("<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js");
const model = await (await getLlama({ gpu: false })).loadModel({ modelPath: gguf, gpuLayers: 0 });
const ids = new Set(idsArg.split(","));
const items = fs.readFileSync(new URL("../slice.items.jsonl", import.meta.url), "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((x) => ids.has(x.id));
const base: string = G.ROUTE_GATE_SYSTEM;
const about = base.split("\n").find((l) => l.startsWith("About BOAR:"))!;
const shortAbout = "About BOAR: an offline app on this phone; a small local AI model answers from a downloaded library (Wikipedia, Wikivoyage, crypto, OpenStreetMap) and shows its sources; text only, no internet.";
const variants: Record<string, string> = {
  B6: base,
  mixedRule: base.replace("getting somewhere) is SEARCH.", "getting somewhere) is SEARCH. A greeting followed by a question is judged by the question."),
  shortAbout: base.replace(about, shortAbout),
  aboutLast: base.replace("\n" + about + "\n", "").replace("\n\nReply with", "\n\n" + about + "\n\nReply with"),
};
variants["mixed+short"] = variants.mixedRule.replace(about, shortAbout);
for (const [name, sys] of Object.entries(variants)) {
  const row: string[] = [];
  for (const it of items) {
    const turns = (it.history ?? []).map(([role, text]: [string, string]) => ({ role, text }));
    const user = G.routeGateMessages(it.msg, turns.length ? { turns } : null)[1].content;
    const text = `<|im_start|>system\n${sys}<|im_end|>\n<|im_start|>user\n${user}<|im_end|>\n<|im_start|>assistant\n`;
    const tokens = model.tokenize(text, true);
    const ctx = await model.createContext({ contextSize: 2048, threads: 4 });
    const o = await ctx.getSequence().controlledEvaluate(tokens.map((t: any, i: number) => (i === tokens.length - 1 ? [t, { generateNext: { probabilities: true, options: { temperature: 0 } } }] : t)) as any);
    await ctx.dispose();
    const probs: Map<number, number> = (o as any)[tokens.length - 1].next.probabilities;
    const top = [...probs.entries()].sort((a, b) => b[1] - a[1]).slice(0, 20).map(([t, p]) => ({ token: model.detokenize([t], true), prob: p }));
    const v = G.routeGateVerdict(top);
    const ok = it.label === "EITHER" ? "~" : (it.label === "SEARCH") === (v.decision === "search") ? "ok" : "XX";
    row.push(`${it.id}:${v.decision[0]}${v.score?.toFixed(2)}${ok}`);
  }
  console.log(name.padEnd(12), row.join(" "));
}
