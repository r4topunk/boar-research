#!/usr/bin/env node
// exp-05: embed each question with the app's embedding GGUF (node-llama-cpp), twice: raw (as the app does today,
// src/rag/retrieve.ts:166 / passages.ts:33) and with BGE's query instruction prefix. Adapted from boar-app
// eval/retrieval/embed-queries.mjs (c87234a9), which produced the published baseline vectors.
//   BOAR_EMBEDDING_GGUF=/path/bge-small-en-v1.5-q8_0.gguf node embed_queries.mjs questions.jsonl out.json
import { createHash } from "node:crypto";
import { createReadStream, readFileSync, writeFileSync } from "node:fs";
import { getLlama } from "node-llama-cpp";

export const BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: ";
const EXPECTED_SHA256 = "ec38e8da142596baa913124ae50550de284b6916bf59577ef2f0cb9660c2f514"; // manifest.ts bge-small-en-v1.5-q8 = packs' embeddingModelSha256
const [input, output] = process.argv.slice(2);
const model = process.env.BOAR_EMBEDDING_GGUF;
if (!input || !output || !model) throw new Error("usage: BOAR_EMBEDDING_GGUF=... embed_queries.mjs questions.jsonl out.json");
const h = createHash("sha256");
for await (const c of createReadStream(model)) h.update(c);
const sha = h.digest("hex");
if (sha !== EXPECTED_SHA256) throw new Error(`embedding GGUF sha256 ${sha} != ${EXPECTED_SHA256}`);
const qs = readFileSync(input, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const llama = await getLlama({ gpu: false });
const ctx = await (await llama.loadModel({ modelPath: model })).createEmbeddingContext({ contextSize: 512, threads: 4 });
const out = { modelSha256: sha, prefix: BGE_QUERY_PREFIX, raw: {}, prefixed: {} };
for (const q of qs) {
  const text = q.query ?? q.question;
  out.raw[q.id] = Array.from((await ctx.getEmbeddingFor(text)).vector);
  out.prefixed[q.id] = Array.from((await ctx.getEmbeddingFor(BGE_QUERY_PREFIX + text)).vector);
}
writeFileSync(output, JSON.stringify(out));
console.log(`embedded ${qs.length} questions x2 (raw, prefixed); model sha256 ${sha}`);
