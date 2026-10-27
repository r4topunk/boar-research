// exp-26 L0 ceiling: "perfect Doc2Query" = the test question itself appended to the best key chunk's FTS row
// (one chunk per item per pack). If the key still doesn't reach searchDetailed's hits, generated questions can't either.
import fs from "node:fs";
import { BASE, openPack, SLICE, Q, keyed, keyHit, kOf } from "./lib.mts";
import { original, rewrite } from "./fts.mts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const emb = await (await (await getLlama({ logLevel: "error" })).loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext();
const ceil = JSON.parse(fs.readFileSync("ceiling.json", "utf8"));
const [wvCopy, crCopy] = process.argv.slice(2); const COPY: Record<string, string> = { wv: wvCopy, cr: crCopy };
const items = SLICE.filter(keyed);
const qv: Record<string, Float32Array> = {}; for (const id of items) qv[id] = Float32Array.from((await emb.getEmbeddingFor(Q[id].question)).vector);
// pick per item/pack the key chunk with the best BM25 rank (pool 2000), else the key chunk whose text has most question stems
const pick: Record<string, Record<string, number>> = {};
for (const key of ["wv", "cr"]) {
  const { raw, pack } = await openPack(BASE[key]); const extra = new Map<number, string>();
  for (const id of items) {
    if (!ceil[id]?.[key]?.nKeyChunks) continue;
    const stems = await pack.stems(Q[id].question);
    const cands = await pack.bm25Candidates(stems, 2000, pack.tuning.prior, 100000);
    const keyChunk = (cid: number) => { const o = original(raw, cid); return keyHit(`${o.title}\n${o.body}`, Q[id].grading); };
    let best = cands.find((c) => keyChunk(c.chunkId))?.chunkId;
    if (best === undefined) {
      // not in the BM25 pool at all: scan the articles that contain the most question stems via FTS title/body (OR over stems, wide)
      const rows = raw.prepare(`SELECT rowid id FROM fts WHERE fts MATCH ? LIMIT 20000`).all(pack.queryTerms(stems).map((t: string) => `"${t.replace(/\*$/, "")}"${t.endsWith("*") ? "*" : ""}`).join(" OR ")) as any[];
      best = rows.map((r) => r.id).find((cid: number) => keyChunk(cid));
    }
    if (best === undefined) continue;
    (pick[id] ??= {})[key] = best; extra.set(best, `${extra.get(best) ?? ""}\n${Q[id].question}`.trim());
  }
  raw.close(); rewrite(COPY[key], extra);
}
const run = async (paths: Record<string, string>) => { const out: Record<string, any> = {};
  for (const key of ["wv", "cr"]) { const { raw, pack } = await openPack(paths[key]);
    for (const id of items) { const { hits } = await pack.searchDetailed(Q[id].question, { k: kOf(id), queryVec: qv[id] }); const stems = await pack.stems(Q[id].question);
      const cands = await pack.bm25Candidates(stems); const p = pick[id]?.[key];
      (out[id] ??= {})[key] = { keyInHits: hits.some((h) => keyHit(`${h.title}\n${h.section}: ${h.text}`, Q[id].grading)), pickInHits: p !== undefined && hits.some((h) => h.chunkId === p), pickRank80: p === undefined ? null : cands.findIndex((c) => c.chunkId === p), hits: hits.map((h) => `${h.title}§${h.section}`.slice(0, 50)) }; }
    raw.close(); }
  return out; };
const b = await run(BASE), o = await run(COPY);
let gained = 0, lost = 0;
for (const id of items) for (const key of ["wv", "cr"]) { if (pick[id]?.[key] === undefined) continue;
  const x = b[id][key], y = o[id][key]; if (y.keyInHits && !x.keyInHits) gained++; if (x.keyInHits && !y.keyInHits) lost++;
  console.log(`${id.padEnd(12)} ${key} pickRank(pool80) ${x.pickRank80} -> ${y.pickRank80} | pick in hits ${x.pickInHits} -> ${y.pickInHits} | key in hits ${x.keyInHits} -> ${y.keyInHits}${JSON.stringify(x.hits) !== JSON.stringify(y.hits) ? `\n      base ${JSON.stringify(x.hits)}\n      orac ${JSON.stringify(y.hits)}` : ""}`); }
console.log(`ORACLE: items keyed ${items.length}; (item,pack) with a key chunk ${Object.values(pick).reduce((s, v) => s + Object.keys(v).length, 0)}; key-in-hits gained ${gained}, lost ${lost}`);
fs.writeFileSync("oracle.json", JSON.stringify({ pick, base: b, oracle: o }, null, 1));
