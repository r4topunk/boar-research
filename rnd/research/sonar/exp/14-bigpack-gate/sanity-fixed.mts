import { DatabaseSync } from "node:sqlite";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const ex = new DatabaseSync("../../data/leadvecs-top100k.fixed.sqlite", { readOnly: true });
const sm = new DatabaseSync("<workspace>/shared-data/packs/boar-wiki-sample.sqlite", { readOnly: true });
const llama = await getLlama({ logLevel: "error" });
const emb = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext();
const i8 = (b: Uint8Array) => new Int8Array(b.buffer, b.byteOffset, b.byteLength);
const cos = (a: ArrayLike<number>, b: ArrayLike<number>) => { let d = 0, x = 0, y = 0; for (let i = 0; i < a.length; i++) { d += a[i] * b[i]; x += a[i] * a[i]; y += b[i] * b[i]; } return d / Math.sqrt(x * y); };
// titles present in both
const common = sm.prepare("SELECT a.title, l.vec FROM articles a JOIN lead_vecs l ON l.article_id = a.id ORDER BY a.views DESC LIMIT 400").all() as any[];
let n = 0, sims: number[] = [];
for (const r of common) {
  const e = ex.prepare("SELECT l.vec FROM articles a JOIN lead_vecs l ON l.article_id = a.id WHERE a.title = ?").get(r.title) as any;
  if (!e) continue; n++; sims.push(cos(i8(r.vec), i8(e.vec)));
  if (n <= 5) console.log(r.title, "sample-vs-export lead cos", cos(i8(r.vec), i8(e.vec)).toFixed(3));
  if (n >= 40) break;
}
sims.sort((a, b) => a - b); console.log(`common titles ${n}: sample-vs-export median ${sims[sims.length >> 1].toFixed(3)} min ${sims[0].toFixed(3)}`);
for (const t of ["Dengue fever", "Burn", "Iceland", "BitTorrent"]) {
  const q = Float32Array.from((await emb.getEmbeddingFor(t)).vector);
  const e = ex.prepare("SELECT l.vec, a.id FROM articles a JOIN lead_vecs l ON l.article_id = a.id WHERE a.title = ?").get(t) as any;
  const s = sm.prepare("SELECT l.vec FROM articles a JOIN lead_vecs l ON l.article_id = a.id WHERE a.title = ?").get(t) as any;
  console.log(`"${t}" title-embedding vs export lead ${e ? cos(q, i8(e.vec)).toFixed(3) : "-"} | vs sample lead ${s ? cos(q, i8(s.vec)).toFixed(3) : "-"}`);
}
console.log(ex.prepare("SELECT count(*) n, min(article_id) mn, max(article_id) mx FROM lead_vecs").get(), ex.prepare("SELECT count(*) n, min(id) mn, max(id) mx FROM articles").get());
// own-title check over common titles: title embedding vs fixed lead
const rows2 = ex.prepare("SELECT a.title, l.vec FROM articles a JOIN lead_vecs l ON l.article_id = a.id").all() as any[];
const common2 = rows2.filter((r) => sm.prepare("SELECT 1 FROM articles WHERE title = ?").get(r.title)).slice(0, 40);
const own: number[] = [];
for (const r of common2) own.push(cos(Float32Array.from((await emb.getEmbeddingFor(r.title)).vector), i8(r.vec)));
own.sort((a, b) => a - b);
console.log(`own-title cos (title embedding vs fixed lead) over ${own.length} common titles: median ${own[own.length >> 1].toFixed(3)}, p10 ${own[Math.floor(own.length * 0.1)].toFixed(3)}, min ${own[0].toFixed(3)}`);
