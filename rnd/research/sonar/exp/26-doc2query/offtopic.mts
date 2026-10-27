// exp-26 L0 off-topic rate: every pack hit (Wikivoyage + crypto, engine k, query vector) for the 24 retrieval-inkit items,
// base vs oracle packs, scored by bge-reranker-v2-m3 (exp-25: AUC 0.912 vs Opus labels). unhelpful < 0.46 (helpful p25), off < 0.10.
import fs from "node:fs";
import { BASE, openPack, SLICE, Q, kOf } from "./lib.mts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const llama = await getLlama({ logLevel: "error" });
const emb = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext();
const rr = await (await llama.loadModel({ modelPath: process.argv[2] })).createRankingContext({ contextSize: 1024, threads: 4 });
const ARM: Record<string, Record<string, string>> = { base: BASE, oracle: { wv: process.argv[3], cr: process.argv[4] } };
const cache = new Map<string, number>(); const res: any = {};
for (const [arm, paths] of Object.entries(ARM)) {
  let n = 0, un = 0, off = 0;
  for (const key of ["wv", "cr"]) { const { raw, pack } = await openPack(paths[key]);
    for (const id of SLICE) { const qv = Float32Array.from((await emb.getEmbeddingFor(Q[id].question)).vector);
      for (const h of (await pack.searchDetailed(Q[id].question, { k: kOf(id), queryVec: qv })).hits) {
        const ck = `${id}|${key}|${h.chunkId}`; if (!cache.has(ck)) cache.set(ck, await rr.rank(Q[id].question, `${h.title}\n${h.section ? h.section + ": " : ""}${h.text}`.slice(0, 2400)));
        const s = cache.get(ck)!; n++; if (s < 0.46) un++; if (s < 0.1) off++; ((res[arm] ??= {})[id] ??= []).push([key, h.title, h.section, +s.toFixed(3)]); } }
    raw.close(); }
  console.log(`${arm}: pack hits ${n}; unhelpful (<0.46) ${un} (${(100 * un / n).toFixed(1)}%); off-topic (<0.10) ${off} (${(100 * off / n).toFixed(1)}%)`);
}
fs.writeFileSync("offtopic.json", JSON.stringify(res, null, 1));
