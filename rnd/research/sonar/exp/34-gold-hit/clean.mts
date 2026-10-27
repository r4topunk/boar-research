// exp-34 CLEAN L0 (Sonar, dev; coordinator's "Q450-like path"): article candidates = named titles (share >= 0.25) +
// dense bge lead-vector search over top100k + the BM25 top articles; passages = ~45-60-word sentence windows of each
// candidate's best chunks, chosen jointly with kit A's non-Wikipedia passages by bge cosine to the question; only a
// cosine floor 0.5 drops "clearly off-topic" windows (0/0.5/0.6 gave the same gold hits); budgets 130 (≈ what the engine places), 240, 340 (Q450's) words. Writes clean-<budget>.prompts.jsonl.
//   tsx clean.mts <top100k.sqlite> <engine tree> <kitA replay traces>
import fs from "node:fs"; import zlib from "node:zlib"; import { DatabaseSync } from "node:sqlite";
const [packPath, tree, kitA, variant = "full"] = process.argv.slice(2);
// variants: full (named + dense 6 + bm25 4, cap 12; lead + 3 chunks); lite (named + dense 4 + bm25 2, cap 8; lead + 1 chunk); nodense; nonamed
const V = { full: { d: 6, b: 4, cap: 12, ch: 3, named: true }, lite: { d: 4, b: 2, cap: 8, ch: 1, named: true }, nodense: { d: 0, b: 4, cap: 12, ch: 3, named: true }, nonamed: { d: 6, b: 4, cap: 12, ch: 3, named: false }, min: { d: 0, b: 4, cap: 8, ch: 1, named: true } }[variant]!;
const { WikiPack } = await import(`${tree}/src/rag/wikiPack.ts`);
const { cosineSimilarityInt8 } = await import(`${tree}/src/rag/pure.ts`);
const db = new DatabaseSync(packPath, { readOnly: true });
const sql = {
  getAllAsync: async (s: string, p: any[] = []) => db.prepare(s).all(...p),
  getFirstAsync: async (s: string, p: any[] = []) => db.prepare(s).get(...p) ?? null,
  execAsync: async (s: string) => { db.exec(s); },
  runAsync: async (s: string, p: any[] = []) => db.prepare(s).run(...p),
};
const pack = await WikiPack.open(sql as any, (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(d)));
const leads = db.prepare("SELECT article_id, vec FROM lead_vecs").all() as any[];
const { getLlama } = await import("<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js");
const model = await (await getLlama({ gpu: false })).loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf", gpuLayers: 0 });
const emb = await model.createEmbeddingContext({ contextSize: 512, threads: 4 });
const vec = async (t: string) => { const tk = model.tokenize(t) as any[]; const c = tk.length > 500 ? model.detokenize(tk.slice(0, 500)) : t; const v = (await emb.getEmbeddingFor(c)).vector as readonly number[]; const n = Math.hypot(...v); return Float32Array.from(v.map((x) => x / n)); };
const dot = (a: Float32Array, b: Float32Array) => { let s = 0; for (let i = 0; i < a.length; i++) s += a[i] * b[i]; return s; };
const words = (s: string) => s.split(/\s+/).filter(Boolean);
// kit A's non-Wikipedia passages (Wikivoyage, crypto) as placed by the engine: they compete in the same ranking.
const nonwiki = new Map<string, { label: string; title: string; text: string }[]>();
for (const l of fs.readFileSync(kitA, "utf8").trim().split("\n")) {
  const r = JSON.parse(l);
  const ev = (r.events ?? []).filter((e: any) => e.type === "sources" && (e.sources ?? []).some((x: any) => x.text));
  nonwiki.set(r.itemId, (ev.at(-1)?.sources ?? []).map((x: any) => ({ label: (x.source ?? "?").split(" ")[0], title: x.title, text: x.text ?? "" })));
}
const ids = fs.readFileSync("<workspace>/rnd/research/anvil/exp/outofkit/v01-en-ids.txt", "utf8").trim().split(",");
const qs = new Map(fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").trim().split("\n").map((l) => JSON.parse(l)).map((q: any) => [q.id, q.question]));
const FLOORS = [0.5];
const BUDGETS = [130, 240, 340];
const out: Record<string, string[]> = Object.fromEntries(BUDGETS.map((b) => [String(b), []]));
const stats: any[] = [];
for (const id of ids) {
  const q = qs.get(id) as string; const qv = await vec(q);
  const stems = await pack.stems(q);
  const named = (await pack.titlesInQuestion(q, stems)).filter((t: any) => t.share >= 0.25).map((t: any) => t.id);
  const dense = leads.map((r) => ({ id: r.article_id, s: cosineSimilarityInt8(qv, new Uint8Array(r.vec)) })).sort((a, b) => b.s - a.s).slice(0, V.d).map((x) => x.id);
  const bm = [...new Set((await pack.bm25Candidates(stems)).map((c: any) => c.articleId))].slice(0, V.b);
  const arts = [...new Set([...(V.named ? named : []), ...dense, ...bm])].slice(0, V.cap);
  const wins: { label: string; title: string; text: string; v?: Float32Array }[] = [];
  for (const a of arts) {
    const art = await pack.article(a);
    // device-sized candidate set: the lead + the article's 3 best chunks by the question's stems
    const ps = await pack.articlePassages(a, stems, V.ch);
    const lead = art.text.slice(0, 1200);
    for (const t of [lead, ...ps.map((p: any) => p.text)]) {
      let cur: string[] = [];
      for (const s of t.replace(/\s+/g, " ").split(/(?<=[.!?])\s+/)) { cur.push(s); if (words(cur.join(" ")).length >= 45) { wins.push({ label: "Wikipedia", title: art.title, text: cur.join(" ") }); cur = []; } }
      if (words(cur.join(" ")).length >= 12) wins.push({ label: "Wikipedia", title: art.title, text: cur.join(" ") });
    }
  }
  const seen = new Set<string>(); const cands = [...wins, ...(nonwiki.get(id) ?? [])].filter((w) => !seen.has(w.text) && (seen.add(w.text), true));
  for (const c of cands) c.v = await vec(c.text);
  const ranked = cands.map((c) => ({ ...c, s: dot(qv, c.v!) })).sort((a, b) => b.s - a.s);
  for (const b of BUDGETS) { const f = FLOORS[0];
    const parts: string[] = []; let n = 0;
    for (const c of ranked) { if (c.s < f) break; const w = words(c.text).length; if (n + w > b && n > 0) break; parts.push(`${c.label}: ${c.title}\n${c.text}`); n += w; }
    out[String(b)].push(JSON.stringify({ itemId: id, messages: [{ content: "SYS\n\nContext:\n" + parts.map((p, i) => `[${i + 1}] ${p}`).join("\n\n") }] }));
  }
  stats.push({ id, named: named.length, arts: arts.length, cands: cands.length });
  process.stderr.write(`${id} named ${named.length} arts ${arts.length} cands ${cands.length}\n`);
}
for (const [k, v] of Object.entries(out)) fs.writeFileSync(`clean${variant === "full" ? "" : "-" + variant}-${k}.prompts.jsonl`, v.join("\n") + "\n");
console.log("mean candidate windows", (stats.reduce((s, x) => s + x.cands, 0) / stats.length).toFixed(1));
