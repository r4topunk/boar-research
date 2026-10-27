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
  for (const ti of traceRaw) if (corpus[ti] && !pool.some((c) => c.title === ti)) pool.push({ chunkId: `corpus:${ti}`, docId: ti, title: ti, body: corpus[ti], score: 1, matchType: "hybrid" });
  // the engine's raw: take pool chunks in trace order, consuming duplicates
  const used = new Set<string>(); const chunks: any[] = [];
  for (const ti of traceRaw) { const c = pool.find((x) => x.title === ti && !used.has(x.chunkId)); if (c) { used.add(c.chunkId); chunks.push(c); } }
  items.push({ id: t.itemId, q: t.question, budget: t.route.reasonCodes.includes("task:lookup") ? 450 : 700, after: Number(ctx.split("->")[1]), chunks, complete: chunks.length === traceRaw.length, health: isHealthQuestion(t.question) });
}

const lv = { wv: new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true }), cr: new DatabaseSync("<workspace>/shared-data/crypto/boar-crypto.sqlite", { readOnly: true }) };
const cosI8 = (q: Float32Array, buf: Uint8Array) => { const v = new Int8Array(buf.buffer, buf.byteOffset, buf.byteLength); let d = 0, a = 0, b = 0; for (let i = 0; i < v.length; i++) { d += q[i] * v[i]; a += q[i] * q[i]; b += v[i] * v[i]; } return d / Math.sqrt(a * b); };
function lead(title: string): Uint8Array | null {
  const wv = title.startsWith("Wikivoyage: "); const t2 = wv ? title.slice(12) : title.replace(/^(ethereum\.org|Ethereum EIPs\/ERCs|Ethereum specs|Bitcoin BIPs): /, "");
  const db = wv ? lv.wv : lv.cr; const r = db.prepare("SELECT l.vec FROM articles a JOIN lead_vecs l ON l.article_id = a.id WHERE a.title = ? LIMIT 1").get(t2) as any; return r ? r.vec : null;
}
setFloor(0.5);
const rows: any[] = [];
for (const it of items) {
  if (!(it.complete && !it.health)) continue;
  const comp = compressContext(it.q, it.chunks, { tokenBudget: it.budget });
  if (comp.tokensAfter !== it.after) continue;
  const qv = Float32Array.from((await emb.getEmbeddingFor(it.q)).vector);
  const g = Q[it.id]?.grading ?? {};
  for (const c of comp.chunks) {
    if (onTopic(it.q, c)) continue;
    const v = lead(c.title); const cos = v ? cosI8(qv, v) : null;
    rows.push({ id: it.id, title: c.title, cos, key: (g.must_any || g.must_k) ? keyHit(c.body, g) : false });
  }
}
fs.writeFileSync("dropped-chunks.json", JSON.stringify(rows, null, 1));
console.log(`chunks dropped by onTopic after compression: ${rows.length} (key-bearing ${rows.filter((r) => r.key).length})`);
for (const tau of [0.6, 0.65, 0.7, 0.75]) {
  const resc = rows.filter((r) => r.cos !== null && r.cos >= tau);
  console.log(`rescue if leadSim >= ${tau}: rescued ${resc.length}; key-bearing ${resc.filter((r) => r.key).length}/${rows.filter((r) => r.key).length}; non-key ${resc.filter((r) => !r.key).length}`);
}
for (const r of rows.filter((r) => r.key || (r.cos ?? 0) >= 0.65)) console.log(`  ${r.key ? "KEY" : "   "} ${(r.cos ?? NaN).toFixed(3)} ${r.id} ${r.title}`);
