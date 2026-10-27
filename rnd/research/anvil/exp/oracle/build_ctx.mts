// Oracle contexts (Anvil, dev): split each item's gold articles into ~120-word passages, embed with the engine's bge-small,
// and pick passages by cosine to the QUESTION (Q) or to the Opus reference ANSWER (R, the oracle), up to a word budget.
// Writes ctx-<variant>.jsonl: {id, passages: [{title, kind, text, sim}]}.  npx tsx build_ctx.mts
import fs from "node:fs";
const D = "<workspace>/rnd/research/anvil/exp/oracle";
const B = "<workspace>/boar-eval/bench/v0.1/";
const arts = fs.readFileSync(`${D}/articles.jsonl`, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const refs = new Map(fs.readFileSync(`${B}refs/refs.jsonl`, "utf8").trim().split("\n").map((l) => JSON.parse(l)).map((r: any) => [r.id, r]));
const qs = new Map(fs.readFileSync(`${B}questions.public.jsonl`, "utf8").trim().split("\n").map((l) => JSON.parse(l)).map((q: any) => [q.id, q]));
const { getLlama } = await import("<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js");
const model = await (await getLlama({ gpu: false })).loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf", gpuLayers: 0 });
const emb = await model.createEmbeddingContext({ contextSize: 512 });
const vec = async (t: string) => { const tk = model.tokenize(t) as any[]; const cut = tk.length > 500 ? model.detokenize(tk.slice(0, 500)) : t; const v = (await emb.getEmbeddingFor(cut)).vector as readonly number[]; const n = Math.hypot(...v); return v.map((x) => x / n); };
const cos = (a: number[], b: number[]) => a.reduce((s, x, i) => s + x * b[i], 0);
const words = (s: string) => s.split(/\s+/).filter(Boolean);
function passages(text: string): string[] {
  const out: string[] = []; let cur: string[] = [];
  for (const para of text.split(/\n+/).map((p) => p.trim()).filter((p) => p && !/^=+.*=+$/.test(p) && words(p).length >= 8)) {
    for (const w of words(para)) { cur.push(w); if (cur.length >= 120) { out.push(cur.join(" ")); cur = []; } }
    if (cur.length >= 60) { out.push(cur.join(" ")); cur = []; }
  }
  if (cur.length >= 20) out.push(cur.join(" "));
  return out;
}
const variants: Record<string, { by: "q" | "r"; budget: number }> = { Q450: { by: "q", budget: 340 }, R450: { by: "r", budget: 340 }, R1500: { by: "r", budget: 1150 } };
const outs: Record<string, string[]> = { Q450: [], R450: [], R1500: [] };
const ids = fs.readFileSync("<workspace>/rnd/research/anvil/exp/outofkit/v01-en-ids.txt", "utf8").trim().split(",");
for (const id of ids) {
  const cands: { title: string; kind: string; text: string; v: number[] }[] = [];
  for (const a of arts.filter((x: any) => x.id === id)) for (const p of passages(a.text).slice(0, 400)) cands.push({ title: a.title, kind: a.kind, text: p, v: await vec(p) });
  const qv = await vec((qs.get(id) as any).question), rv = await vec(((refs.get(id) as any).answer ?? ""));
  for (const [name, cfg] of Object.entries(variants)) {
    const key = cfg.by === "q" ? qv : rv;
    const ranked = cands.map((c) => ({ ...c, sim: cos(key, c.v) })).sort((a, b) => b.sim - a.sim);
    const pick: any[] = []; let n = 0;
    for (const c of ranked) { const w = words(c.text).length; if (n + w > cfg.budget && pick.length) break; pick.push({ title: c.title, kind: c.kind, text: c.text, sim: +c.sim.toFixed(3) }); n += w; }
    outs[name].push(JSON.stringify({ id, passages: pick }));
  }
  console.log(id, cands.length, "passages");
}
for (const [k, v] of Object.entries(outs)) fs.writeFileSync(`${D}/ctx-${k}.jsonl`, v.join("\n") + "\n");
