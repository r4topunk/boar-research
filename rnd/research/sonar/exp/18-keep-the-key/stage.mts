// Sonar exp-18b: per-item drop stage for the 6 'retrieved but dropped' items on and-qwen (kit A), by replaying the engine's
// own code @0cfd4a77 (wikiPack.searchDetailed on boar-wikivoyage-en + boar-crypto -> compressContext -> onTopic), and checking
// the replay's raw titles against the trace. Stage per key-bearing chunk: COMPRESSION (cut by compressContext: relative floor
// or budget) vs ONSUBJECT (kept by compression, rejected by onTopic) vs KEPT.
import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import fs from "node:fs";
import { WikiPack } from "./src/rag/wikiPack.ts";
import { compressContext } from "./src/rag/compress.ts";
import { onTopic } from "./src/routing/context.ts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
async function open(path: string, label: string) {
  const raw = new DatabaseSync(path, { readOnly: true });
  const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) };
  return { pack: await WikiPack.open(db as any, dec), label };
}
const packs = [await open("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", "Wikivoyage"), await open("<workspace>/shared-data/crypto/boar-crypto.sqlite", "crypto")];
const llama = await getLlama({ logLevel: "error" });
const emb = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext();
const Q = Object.fromEntries(fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => { const x = JSON.parse(l); return [x.id, x]; }));
const T = Object.fromEntries(fs.readFileSync("<workspace>/boar-eval/runs/night-2026-10-01/and-qwen-s42.traces.jsonl", "utf8").split("\n").filter(Boolean).map((l) => { const t = JSON.parse(l); return [t.itemId, t]; }));
const norm = (s: string) => s.toLowerCase().replace(/’/g, "'").replace(/\s+/g, " ");
const termHit = (t: string, x: string) => (x.startsWith("re:") ? new RegExp(x.slice(3)).test(t) : t.includes(norm(x)));
const keyHit = (text: string, g: any) => { const t = norm(text); let ok = (g.must_any ?? []).every((grp: string[]) => grp.some((x) => termHit(t, x))); if (g.must_k) ok &&= g.must_k.terms.filter((x: string) => termHit(t, x)).length >= g.must_k.k; return ok; };
const dropped = JSON.parse(fs.readFileSync("dropped.json", "utf8"));
for (const id of Object.keys(dropped)) {
  const t = T[id]; const q = Q[id]; const k = t.events.find((e: any) => e.type === "retrieve")?.k ?? 4;
  const qv = Float32Array.from((await emb.getEmbeddingFor(t.question)).vector);
  const chunks: any[] = [];
  for (const { pack, label } of packs) {
    const { hits } = await pack.searchDetailed(t.question, { k, queryVec: qv });
    for (const h of hits) chunks.push({ chunkId: `${label}:${h.chunkId}`, docId: String(h.articleId), title: label === "Wikivoyage" ? `Wikivoyage: ${h.title}` : h.title, body: h.section ? `${h.section}: ${h.text}` : h.text, score: h.score, matchType: "lexical" });
  }
  const traceRaw = t.retrieval.raw.map((s: any) => s.title);
  const ctx = t.route.reasonCodes.find((c: string) => /^context:\d+->\d+$/.test(c)); const after = ctx ? Number(ctx.split("->")[1]) : 0;
  const budget = t.route.reasonCodes.includes("task:lookup") ? 450 : 700;
  // keep the replayed chunks that the trace's raw list contains (the engine's fused top-K)
  const inRaw = chunks.filter((c) => traceRaw.includes(c.title));
  const comp = compressContext(t.question, inRaw, { tokenBudget: budget });
  console.log(`\n${id} | ${t.question.slice(0, 70)}\n  trace raw: ${traceRaw.join(", ")} | trace context ${ctx} | replay compress ${comp.tokensBefore}->${comp.tokensAfter} (budget ${budget})`);
  for (const c of inRaw) {
    const key = keyHit(c.body, q.grading); const kept = comp.chunks.find((x: any) => x.chunkId === c.chunkId);
    const stage = !kept ? "COMPRESSION" : onTopic(t.question, kept) ? (keyHit(kept.body, q.grading) ? "KEPT (key in text)" : "KEPT (key cut from text)") : "ONSUBJECT";
    console.log(`  ${key ? "KEY" : "   "} ${c.title} §${c.body.split(":")[0].slice(0, 40)} -> ${stage}`);
  }
}
