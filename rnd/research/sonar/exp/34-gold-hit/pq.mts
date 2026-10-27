// exp-34 PQ L0 (Sonar, dev): re-select Wikipedia passages within the articles the g1plus engine already retrieved, by
// bge-small cosine to the question (no query prefix, as the engine). Candidates = the pack's own chunks (top100k,
// chunkChars 1000). Context = the engine's non-Wikipedia passages + PQ passages up to a word budget:
//   "same" = the engine's own context words for that item; "340" = Q450's budget.
// Writes pq-<budget>.prompts.jsonl in the --dump-prompts shape for goldhit.py.
//   node pq.mts <sub.sqlite>
import fs from "node:fs"; import zlib from "node:zlib"; import { DatabaseSync } from "node:sqlite";
const [sub, tag = ""] = process.argv.slice(2);
const items = JSON.parse(fs.readFileSync(`pq-items${tag}.json`, "utf8"));
const db = new DatabaseSync(sub, { readOnly: true });
const blocks = new Map<number, Buffer>();
const block = (id: number) => { if (!blocks.has(id)) blocks.set(id, zlib.zstdDecompressSync((db.prepare("SELECT zdata FROM blocks WHERE id=?").get(id) as any).zdata)); return blocks.get(id)!; };
// Articles by title, on demand (the full pack has ~98k articles).
const art = { get(t: string) {
  const a = db.prepare("SELECT id,block_id,off,len FROM articles WHERE title = ? COLLATE NOCASE").get(t) as any;
  return a ? { id: a.id, text: block(a.block_id).subarray(a.off, a.off + a.len).toString("utf8") } : undefined;
} };
const { getLlama } = await import("<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js");
const model = await (await getLlama({ gpu: false })).loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf", gpuLayers: 0 });
const emb = await model.createEmbeddingContext({ contextSize: 512, threads: 4 });
const vec = async (t: string) => { const tk = model.tokenize(t) as any[]; const c = tk.length > 500 ? model.detokenize(tk.slice(0, 500)) : t; const v = (await emb.getEmbeddingFor(c)).vector as readonly number[]; const n = Math.hypot(...v); return v.map((x) => x / n); };
const words = (s: string) => s.split(/\s+/).filter(Boolean);
const tr = JSON.parse(fs.readFileSync(`pq-engine-ctx${tag}.json`, "utf8")); // {id: {nonwiki: [{label,title,text}]}}
const out: Record<string, string[]> = { same: [], "240": [], "340": [] };
let nChunks = 0;
for (const [id, it] of Object.entries<any>(items)) {
  const cands: { title: string; text: string; v: number[] }[] = [];
  for (const t of it.wiki_titles) {
    const a = art.get(t.toLowerCase()); if (!a) continue;
    for (const c of db.prepare("SELECT start,end FROM chunks WHERE article_id=? ORDER BY start").all(a.id) as any[]) {
      const text = a.text.slice(c.start, c.end).replace(/\s+/g, " ").trim();
      if (words(text).length >= 8) cands.push({ title: t, text, v: [] });
    }
  }
  const qv = await vec(it.q);
  for (const c of cands) c.v = await vec(c.text);
  nChunks += cands.length;
  const cos = (v: number[]) => v.reduce((s, x, i) => s + x * qv[i], 0);
  // v2: the top 40 chunks, split into ~60-word sentence windows, re-ranked (closer to the engine's sentence compression).
  const top = cands.map((c) => ({ ...c, sim: cos(c.v) })).sort((a, b) => b.sim - a.sim).slice(0, 40);
  const wins: { title: string; text: string; v: number[] }[] = [];
  for (const c of top) {
    const ss = c.text.split(/(?<=[.!?])\s+/); let cur: string[] = [];
    for (const s of ss) { cur.push(s); if (words(cur.join(" ")).length >= 45) { wins.push({ title: c.title, text: cur.join(" "), v: [] }); cur = []; } }
    if (words(cur.join(" ")).length >= 12) wins.push({ title: c.title, text: cur.join(" "), v: [] });
  }
  for (const w of wins) w.v = await vec(w.text);
  const ranked = wins.map((c) => ({ ...c, sim: cos(c.v) })).sort((a, b) => b.sim - a.sim);
  const nonwiki = (tr[id]?.nonwiki ?? []) as any[];
  for (const [name, budget] of [["same", Math.max(it.ctx_words, 60)], ["240", 240], ["340", 340]] as const) {
    const parts = nonwiki.map((x) => `${x.label}: ${x.title}\n${x.text}`);
    let n = nonwiki.reduce((s, x) => s + words(x.text).length, 0);
    for (const c of ranked) { const w = words(c.text).length; if (n + w > budget && n > 0) break; parts.push(`Wikipedia: ${c.title}\n${c.text}`); n += w; }
    const ctx = parts.map((p, i) => `[${i + 1}] ${p}`).join("\n\n");
    out[name].push(JSON.stringify({ itemId: id, messages: [{ content: "SYS\n\nContext:\n" + ctx }] }));
  }
  process.stderr.write(`${id} ${cands.length}\n`);
}
for (const [k, v] of Object.entries(out)) fs.writeFileSync(`pq${tag}-${k}.prompts.jsonl`, v.join("\n") + "\n");
console.log("items", Object.keys(items).length, "chunks embedded", nChunks);
