// Sonar exp-13: where does retrieval time go? Desktop (M-series, CPU+Metal) per-component timing over the 72 bench-v0.1
// questions, engine code @0cfd4a77: query embedding (bge-small), format-2 WikiPack.searchDetailed (Wikivoyage, crypto),
// format-1 pack search as in packs.ts (FTS 400 candidates + int8 cosine on all + term coverage) on wiki-vital5.
import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import fs from "node:fs";
import { WikiPack } from "./src/rag/wikiPack.ts";
import { buildLexicalQuery, filterByTermCoverage, cosineSimilarityInt8 } from "./src/rag/pure.ts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
async function open(path: string) {
  const raw = new DatabaseSync(path, { readOnly: true });
  const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) };
  return await WikiPack.open(db as any, dec);
}
const wv = await open("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite");
const cr = await open("<workspace>/shared-data/crypto/boar-crypto.sqlite");
const v5 = new DatabaseSync("<workspace>/shared-data/packs/wiki-vital5.sqlite", { readOnly: true });
const llama = await getLlama({ logLevel: "error", gpu: false });
const emb = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf", gpuLayers: 0 })).createEmbeddingContext({ threads: 4 });
const qs = fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l).question);
const t: Record<string, number[]> = { embed: [], wikivoyage: [], crypto: [], vital5_fts: [], vital5_cosine: [] };
const now = () => performance.now();
for (const q of qs) {
  let a = now(); const qv = Float32Array.from((await emb.getEmbeddingFor(q)).vector); t.embed.push(now() - a);
  a = now(); await wv.searchDetailed(q, { k: 4, queryVec: qv }); t.wikivoyage.push(now() - a);
  a = now(); await cr.searchDetailed(q, { k: 4, queryVec: qv }); t.crypto.push(now() - a);
  const lq = buildLexicalQuery(q); if (!lq) continue;
  a = now(); const rows = v5.prepare("SELECT c.id, c.title, c.body, c.vec, bm25(chunks_fts) AS rank FROM chunks_fts f JOIN chunks c ON c.id = f.rowid WHERE chunks_fts MATCH ? ORDER BY rank LIMIT 400").all(lq.match) as any[]; t.vital5_fts.push(now() - a);
  a = now(); rows.map((r) => cosineSimilarityInt8(qv, r.vec)); filterByTermCoverage(rows, lq.terms); t.vital5_cosine.push(now() - a);
}
const med = (x: number[]) => [...x].sort((p, q) => p - q)[x.length >> 1], p90 = (x: number[]) => [...x].sort((p, q) => p - q)[Math.floor(x.length * 0.9)];
const tot = Object.values(t).reduce((s, x) => s + med(x), 0);
for (const [k, v] of Object.entries(t)) console.log(`${k.padEnd(14)} p50 ${med(v).toFixed(1)} ms  p90 ${p90(v).toFixed(1)} ms  share ${(100 * med(v) / tot).toFixed(0)}%`);
console.log(`sum of p50s ${tot.toFixed(1)} ms (CPU only, 4 threads)`);
