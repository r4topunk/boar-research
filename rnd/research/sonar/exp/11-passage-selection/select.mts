// Sonar exp-11b (pre-validation, per the replay-before-queue rule): within the articles the engine already retrieves from
// the full-text sample pack, does choosing passages by bge-small cosine (chunk embedded at query time on desktop; a
// shipped pack would store int8 chunk vectors) put the answer key in the selected text more often than the engine's
// stem-based articlePassages? Same budget: lead + 2 best sections per article (engine default), max 4 passages total.
import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import fs from "node:fs";
import { WikiPack } from "./src/rag/wikiPack.ts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
const raw = new DatabaseSync("<workspace>/shared-data/packs/boar-wiki-sample.sqlite", { readOnly: true });
const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) };
const pack = await WikiPack.open(db as any, dec);
const llama = await getLlama({ logLevel: "error" });
const bge = await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" });
const emb = await bge.createEmbeddingContext({ contextSize: 512 });
const vec = async (t: string): Promise<Float32Array> => { const toks = bge.tokenize(t).slice(0, 480); return Float32Array.from((await emb.getEmbeddingFor(toks)).vector); };
const cos = (a: Float32Array, b: Float32Array) => { let d = 0, x = 0, y = 0; for (let i = 0; i < a.length; i++) { d += a[i] * b[i]; x += a[i] * a[i]; y += b[i] * b[i]; } return d / Math.sqrt(x * y); };
const norm = (s: string) => s.toLowerCase().replace(/’/g, "'").replace(/\s+/g, " ");
const termHit = (t: string, x: string) => (x.startsWith("re:") ? new RegExp(x.slice(3)).test(t) : t.includes(norm(x)));
const keyHit = (text: string, g: any) => { const t = norm(text); let ok = (g.must_any ?? []).every((grp: string[]) => grp.some((x) => termHit(t, x))); if (g.must_k) ok &&= g.must_k.terms.filter((x: string) => termHit(t, x)).length >= g.must_k.k; return ok; };
const artText = (id: number) => { const a = raw.prepare("SELECT block_id, off, len FROM articles WHERE id = ?").get(id) as any; const z = (raw.prepare("SELECT zdata FROM blocks WHERE id = ?").get(a.block_id) as any).zdata; return Buffer.from(dec(z)).subarray(a.off, a.off + a.len).toString("utf8"); };
const res = { items: 0, reachable: 0, engine: 0, cosine: 0, blend: 0, onlyCos: [] as string[], onlyEng: [] as string[] };
let embedded = 0; const t0 = Date.now();
for (const l of fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean)) {
  const q = JSON.parse(l); if (!(q.grading.must_any || q.grading.must_k)) continue;
  res.items++;
  const qv = await vec(q.question);
  const { hits } = await pack.searchDetailed(q.question, { k: 4, queryVec: qv });
  const ids = [...new Set(hits.map((h) => h.articleId))].slice(0, 4);
  const engineText = hits.map((h) => h.text).join("\n");
  let full = "", cosText = "", blendText = "";
  for (const id of ids) {
    const text = artText(id); full += text + "\n";
    const rows = raw.prepare("SELECT start, end FROM chunks WHERE article_id = ? ORDER BY id").all(id) as any[];
    if (!rows.length) continue;
    const scored = [];
    for (const r of rows.slice(0, 80)) { const t = text.slice(r.start, r.end); scored.push({ t, c: cos(qv, await vec(t)), i: scored.length }); embedded++; }
    const lead = scored[0];
    const best = scored.slice(1).sort((a, b) => b.c - a.c).slice(0, 2);
    cosText += [lead, ...best].map((x) => x.t).join("\n") + "\n";
    // blend: engine's own passages for this article + the single best-cosine section
    blendText += hits.filter((h) => h.articleId === id).map((h) => h.text).join("\n") + "\n" + (best[0]?.t ?? "") + "\n";
  }
  const reach = keyHit(full, q.grading); if (!reach) continue;
  res.reachable++;
  const e = keyHit(engineText, q.grading), c = keyHit(cosText, q.grading), b = keyHit(blendText, q.grading);
  res.engine += +e; res.cosine += +c; res.blend += +b;
  if (c && !e) res.onlyCos.push(q.id); if (e && !c) res.onlyEng.push(q.id);
}
console.log(JSON.stringify({ ...res, embeddedChunks: embedded, seconds: Math.round((Date.now() - t0) / 1000) }, null, 1));
