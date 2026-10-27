// Sonar exp-18c: full-set replay (72 items, and-qwen-s42 = Android 4B, kit A) of context assembly (compressContext + onTopic)
// on exactly reconstructed raw chunks (Wikivoyage/crypto passages via WikiPack.searchDetailed; bundled corpus docs = 1 chunk),
// fidelity-checked against each trace's `context:X->Y` code. Variants of compress.ts RELATIVE_RELEVANCE_FLOOR: 0.5 (engine), 0.3, 0.0.
// Output per variant: exact key-in-pre on keyed items (fidelity-ok, non-health), gained/lost vs 0.5, items emptied, prompt tokens.
import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import fs from "node:fs";
import { execFileSync } from "node:child_process";
import { WikiPack } from "./src/rag/wikiPack.ts";
import { compressContext, setFloor } from "./compress-floor.ts";
import { onTopic, isHealthQuestion } from "./src/routing/context.ts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
async function open(path: string, label: string) {
  const raw = new DatabaseSync(path, { readOnly: true });
  const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) };
  return { pack: await WikiPack.open(db as any, dec), label };
}
const packs = [await open("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", "Wikivoyage"), await open("<workspace>/shared-data/crypto/boar-crypto.sqlite", "crypto")];
const v5 = new DatabaseSync("<workspace>/shared-data/packs/wiki-vital5.sqlite", { readOnly: true });
const cosI8 = (q: Float32Array, buf: Uint8Array) => { const v = new Int8Array(buf.buffer, buf.byteOffset, buf.byteLength); let d = 0, a = 0, b = 0; for (let i = 0; i < v.length; i++) { d += q[i] * v[i]; a += q[i] * q[i]; b += v[i] * v[i]; } return d / Math.sqrt(a * b); };
const corpus = Object.fromEntries(JSON.parse(execFileSync("git", ["-C", "<workspace>/boar-app", "show", "upstream/main:assets/corpus/corpus.json"], { maxBuffer: 1 << 28 }).toString()).map((d: any) => [d.title, d.body]));
const llama = await getLlama({ logLevel: "error" });
const emb = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext();
const Q = Object.fromEntries(fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => { const x = JSON.parse(l); return [x.id, x]; }));
const norm = (s: string) => s.toLowerCase().replace(/’/g, "'").replace(/\s+/g, " ");
const termHit = (t: string, x: string) => (x.startsWith("re:") ? new RegExp(x.slice(3)).test(t) : t.includes(norm(x)));
const keyHit = (text: string, g: any) => { const t = norm(text); let ok = (g.must_any ?? []).every((grp: string[]) => grp.some((x) => termHit(t, x))); if (g.must_k) ok &&= g.must_k.terms.filter((x: string) => termHit(t, x)).length >= g.must_k.k; return ok; };
const approx = (s: string) => Math.ceil(s.length / 4);
const items: any[] = [];
for (const l of fs.readFileSync("<workspace>/boar-eval/runs/night-2026-10-01/and-qwen-s42.traces.jsonl", "utf8").split("\n").filter(Boolean)) {
  const t = JSON.parse(l); const ctx = t.route.reasonCodes.find((c: string) => /^context:\d+->\d+$/.test(c)); if (!ctx) continue;
  const k = t.events.find((e: any) => e.type === "retrieve")?.k ?? 4; const traceRaw: string[] = t.retrieval.raw.map((s: any) => s.title);
  const qv = Float32Array.from((await emb.getEmbeddingFor(t.question)).vector);
  const pool: any[] = [];
  for (const { pack, label } of packs) for (const h of (await pack.searchDetailed(t.question, { k, queryVec: qv })).hits) pool.push({ chunkId: `${label}:${h.chunkId}`, docId: String(h.articleId), title: label === "Wikivoyage" ? `Wikivoyage: ${h.title}` : (h.source === "enwiki" ? h.title : `${({ ethereumorg: "ethereum.org", eips: "Ethereum EIPs/ERCs", ethspecs: "Ethereum specs", bips: "Bitcoin BIPs" } as any)[h.source] ?? ""}: ${h.title}`), body: h.section ? `${h.section}: ${h.text}` : h.text, score: 1, matchType: "lexical" });
  for (const ti of new Set(traceRaw)) {
    if (pool.some((c) => c.title === ti)) continue;
    const rows = v5.prepare("SELECT id, body, vec FROM chunks WHERE title = ?").all(ti) as any[];
    if (rows.length) { rows.map((r) => ({ r, c: cosI8(qv, r.vec) })).sort((a, b) => b.c - a.c).forEach(({ r }) => pool.push({ chunkId: `v5:${r.id}`, docId: ti, title: ti, body: r.body, score: 1, matchType: "hybrid" })); continue; }
    if (corpus[ti]) pool.push({ chunkId: `corpus:${ti}`, docId: ti, title: ti, body: corpus[ti], score: 1, matchType: "hybrid" });
  }
  // the engine's raw: take pool chunks in trace order, consuming duplicates
  const used = new Set<string>(); const chunks: any[] = [];
  for (const ti of traceRaw) { const c = pool.find((x) => x.title === ti && !used.has(x.chunkId)); if (c) { used.add(c.chunkId); chunks.push(c); } }
  items.push({ id: t.itemId, q: t.question, budget: t.route.reasonCodes.includes("task:lookup") ? 450 : 700, after: Number(ctx.split("->")[1]), chunks, complete: chunks.length === traceRaw.length, health: isHealthQuestion(t.question) });
}
const lvdb = { wv: new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true }), cr: new DatabaseSync("<workspace>/shared-data/crypto/boar-crypto.sqlite", { readOnly: true }) };
const qvs = new Map<string, Float32Array>(); for (const it of items) qvs.set(it.id, Float32Array.from((await emb.getEmbeddingFor(it.q)).vector));
function leadSim(it: any, title: string): number { const wv = title.startsWith("Wikivoyage: "); const t2 = wv ? title.slice(12) : title.replace(/^(ethereum\.org|Ethereum EIPs\/ERCs|Ethereum specs|Bitcoin BIPs): /, ""); const r = (wv ? lvdb.wv : lvdb.cr).prepare("SELECT l.vec FROM articles a JOIN lead_vecs l ON l.article_id = a.id WHERE a.title = ? LIMIT 1").get(t2) as any; return r ? cosI8(qvs.get(it.id)!, r.vec) : -1; }
let RESCUE = false;
const run = (floor: number, per = 4) => { setFloor(floor); const out: Record<string, any> = {};
  for (const it of items) { const comp = compressContext(it.q, it.chunks, { tokenBudget: it.budget, maxSentencesPerChunk: per }); const kept = comp.chunks.filter((c: any) => onTopic(it.q, c) || (RESCUE && leadSim(it, c.title) >= 0.7));
    out[it.id] = { after: comp.tokensAfter, text: kept.map((c: any) => `${c.title}\n${c.body}`).join("\n"), n: kept.length, tok: kept.reduce((s: number, c: any) => s + approx(`${c.title}\n${c.body}`), 0) }; }
  return out; };
const base = run(0.5);
const ok = items.filter((it) => it.complete && base[it.id].after === it.after && !it.health);
console.log(`items with context code ${items.length}; complete raw reconstruction ${items.filter((i) => i.complete).length}; replay matches trace context code ${items.filter((i) => base[i.id].after === i.after).length}; usable (complete+match, non-health) ${ok.length}`);
const keyed = ok.filter((it) => Q[it.id] && (Q[it.id].grading.must_any || Q[it.id].grading.must_k));

for (const per of [4, 6]) { setFloor(0.5);
  const it = items.find((x) => x.id === "vit-cry-010"); const comp = compressContext(it.q, it.chunks, { tokenBudget: it.budget, maxSentencesPerChunk: per });
  const kept = comp.chunks.filter((c: any) => onTopic(it.q, c));
  console.log(`perChunk ${per}: tokensAfter ${comp.tokensAfter}`);
  for (const c of kept) console.log(`   ${keyHit(c.body, Q[it.id].grading) ? "KEY" : "   "} ${c.title} | ${c.body.slice(0, 160).replace(/\n/g, " ")}`);
}
console.log("grading:", JSON.stringify(Q["vit-cry-010"].grading).slice(0, 300));
