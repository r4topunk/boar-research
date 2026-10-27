import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import { WikiPack } from "./src/rag/wikiPack.ts";
import { compressContext, scoreSentences } from "./src/rag/compress.ts";
import { onTopic } from "./src/routing/context.ts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const raw = new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true });
const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) };
const pack = await WikiPack.open(db as any, (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d))));
const llama = await getLlama({ logLevel: "error" });
const emb = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext();
const Q = "I'm at 4,000 m in the Andes with a headache and nausea. What should I do?";
const { hits } = await pack.searchDetailed(Q, { k: 4, queryVec: Float32Array.from((await emb.getEmbeddingFor(Q)).vector) });
const chunks = hits.map((h) => ({ chunkId: String(h.chunkId), docId: String(h.articleId), title: `Wikivoyage: ${h.title}`, body: h.section ? `${h.section}: ${h.text}` : h.text, score: h.score, matchType: "lexical" as const }));
for (const q of [Q, "I'm at 4,000 m with a headache and nausea. What should I do?"]) {
  const comp = compressContext(q, chunks as any, { tokenBudget: 700 });
  console.log(`\nquery: ${q}\n  compress ${comp.tokensBefore}->${comp.tokensAfter} kept ${comp.keptIndices.map((i: number) => chunks[i].title + "§" + hits[i].section).join(" | ")}`);
  console.log("  onTopic per chunk:", chunks.map((c) => `${c.title}§${hits[chunks.indexOf(c)].section}=${onTopic(q, c as any)}`).join("; "));
  const sc = scoreSentences(q, chunks as any); const best = chunks.map((_, ci) => Math.max(0, ...sc.filter((s: any) => s.chunkIndex === ci).map((s: any) => s.score)));
  console.log("  best sentence score per chunk:", best.map((b) => b.toFixed(2)).join(", "));
  const top = sc.sort((a: any, b: any) => b.score - a.score)[0]; console.log(`  top sentence (chunk ${top.chunkIndex}): ${top.text.slice(0, 160)}`);
}
