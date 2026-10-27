// Sonar exp-09 (QUEUE #10): replay the engine's own code @0cfd4a77 (wikiPack search → compressContext → onTopic) on the
// Wikivoyage pack for the 6 "on-topic gold dropped" items of ios-main-s42, to find which stage drops the gold guide.
import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import { WikiPack } from "./src/rag/wikiPack.ts";
import { compressContext } from "./src/rag/compress.ts";
import { onTopic, isHealthQuestion } from "./src/routing/context.ts";
import { canonicalHealthTerms } from "./src/routing/ptQuery.ts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const raw = new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true });
const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) };
const pack = await WikiPack.open(db as any, (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d))));
const llama = await getLlama({ logLevel: "error" });
const emb = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext();
const ITEMS: Record<string, [string, string]> = {
  "vit-hlt-002": ["I'm at 4,000 m in the Andes with a headache and nausea. What should I do?", "Altitude sickness"],
  "lan-exp-002": ["What are the key facts about Montenegro: capital, currency, coastline and how it became independent?", "Montenegro"],
  "lan-exp-004": ["What is Kyoto known for, and why was it historically important?", "Kyoto"],
  "lan-exp-006": ["What is Kilimanjaro, how high is it, and is it a volcano?", "Mount Kilimanjaro"],
  "lan-rsn-007": ["In which year was the Berlin Wall built, and in which year did it come down?", "Berlin Wall"],
  "lan-exp-007": ["Describe Greenland: who governs it, its capital, roughly how many people live there, and how much of it is covered by ice?", "Greenland"],
};
for (const [id, [q, gold]] of Object.entries(ITEMS)) {
  const qv = Float32Array.from((await emb.getEmbeddingFor(q)).vector);
  const { hits } = await pack.searchDetailed(q, { k: 4, queryVec: qv });
  const chunks = hits.map((h) => ({ chunkId: String(h.chunkId), docId: String(h.articleId), title: `Wikivoyage: ${h.title}`, body: h.section ? `${h.section}: ${h.text}` : h.text, score: h.score, matchType: "lexical" as const, action: h.action }));
  const health = isHealthQuestion(q);
  const matchQuery = (health ? canonicalHealthTerms(q) : null) ?? q;
  const comp = compressContext(matchQuery, chunks, { tokenBudget: 700 });
  console.log(`\n${id} | health=${health} matchQuery="${String(matchQuery).slice(0, 80)}"`);
  console.log(`  compress ${comp.tokensBefore} -> ${comp.tokensAfter}; kept idx ${comp.keptIndices.join(",")}`);
  for (const [i, c] of chunks.entries()) {
    const k = comp.chunks.find((x: any) => x.chunkId === c.chunkId);
    console.log(`  [${i}] ${c.title} §${hits[i].section || "lead"} via=${hits[i].via} | compressed:${k ? "kept" : "CUT"} | onTopic(raw):${onTopic(matchQuery, c as any)} onTopic(compressed):${k ? onTopic(matchQuery, k as any) : "-"}${c.title.endsWith(gold) ? "  <= GOLD" : ""}`);
    if (k && c.title.endsWith(gold)) console.log(`      compressed body: ${k.body.slice(0, 220)}`);
  }
}
