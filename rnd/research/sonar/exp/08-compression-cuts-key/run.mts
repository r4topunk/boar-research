// Sonar exp-08: does compressContext (src/rag/compress.ts @0cfd4a77, copied verbatim) cut the answer sentence out of
// the passages the model is shown? Replays compression on reconstructed raw chunks of Kiln's ios-main-v5-t0 traces
// (kit A + vital5, temp 0), with the work budget the trace itself reports (`context:X->Y`), then checks the item's
// answer key in (a) the uncompressed chunks of the shown sources and (b) their compressed text.
// Chunk reconstruction (approximate, declared): vital5 = its top-n chunks by cosine to the question (n = copies in raw);
// bundled corpus = article body; Wikivoyage/crypto = consecutive 1,000-char windows of the article (format-2 chunkChars 1000).
import { DatabaseSync } from "node:sqlite";
import fs from "node:fs";
import { execFileSync } from "node:child_process";
import zlib from "node:zlib";
import { compressContext } from "./compress.0cfd4a77.ts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const R = "<workspace>/boar-eval/runs/night-2026-10-01/ios-main-v5-t0.traces.jsonl";
const Q = Object.fromEntries(fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => { const x = JSON.parse(l); return [x.id, x]; }));
const v5 = new DatabaseSync("<workspace>/shared-data/packs/wiki-vital5.sqlite", { readOnly: true });
const f2 = [new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true }), new DatabaseSync("<workspace>/shared-data/crypto/boar-crypto.sqlite", { readOnly: true })];
const corpus = Object.fromEntries(JSON.parse(execFileSync("git", ["-C", "<workspace>/boar-app", "show", "0cfd4a77:assets/corpus/corpus.json"], { maxBuffer: 1 << 28 }).toString()).map((d: any) => [d.title.toLowerCase(), d.body]));
const llama = await getLlama({ logLevel: "error" });
const emb = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext();
const cos = (q: Float32Array, buf: Uint8Array) => { const v = new Int8Array(buf.buffer, buf.byteOffset, buf.byteLength); let d = 0, a = 0, b = 0; for (let i = 0; i < v.length; i++) { d += q[i] * v[i]; a += q[i] * q[i]; b += v[i] * v[i]; } return d / Math.sqrt(a * b); };
const norm = (s: string) => s.toLowerCase().replace(/’/g, "'").replace(/\s+/g, " ");
const termHit = (t: string, x: string) => (x.startsWith("re:") ? new RegExp(x.slice(3)).test(t) : t.includes(norm(x)));
const keyHit = (text: string, g: any) => { const t = norm(text); let ok = (g.must_any ?? []).every((grp: string[]) => grp.some((x) => termHit(t, x))); if (g.must_k) ok &&= g.must_k.terms.filter((x: string) => termHit(t, x)).length >= g.must_k.k; return ok; };
async function chunksFor(title: string, n: number, qv: Float32Array): Promise<string[]> {
  const rows = v5.prepare("SELECT body, vec FROM chunks WHERE title = ? COLLATE NOCASE").all(title) as any[];
  if (rows.length) return rows.map((r) => [cos(qv, r.vec), r.body] as [number, string]).sort((a, b) => b[0] - a[0]).slice(0, n).map((x) => x[1]);
  if (corpus[title.toLowerCase()]) return [corpus[title.toLowerCase()]];
  const t2 = title.includes(": ") ? title.split(": ").slice(1).join(": ") : title;
  for (const db of f2) for (const t of [title, t2]) {
    const a = db.prepare("SELECT block_id, off, len FROM articles WHERE title = ? COLLATE NOCASE ORDER BY views DESC LIMIT 1").get(t) as any;
    if (a) { const z = (db.prepare("SELECT zdata FROM blocks WHERE id = ?").get(a.block_id) as any).zdata; const txt = zlib.zstdDecompressSync(Buffer.from(z)).subarray(a.off, a.off + a.len).toString("utf8"); return Array.from({ length: n }, (_, i) => txt.slice(i * 1000, (i + 1) * 1000)).filter(Boolean); }
  }
  return [];
}
const rows: any[] = [];
for (const l of fs.readFileSync(R, "utf8").split("\n").filter(Boolean)) {
  const t = JSON.parse(l); const q = Q[t.itemId]; if (!q || !(q.grading.must_any || q.grading.must_k)) continue;
  const ev = t.events.filter((e: any) => e.type === "sources"); const shown = new Set((ev.at(-1)?.sources ?? []).map((s: any) => s.title)); if (!shown.size) continue;
  const ctxCode = t.route.reasonCodes.find((c: string) => /^context:\d+->\d+$/.test(c)); const after = ctxCode ? Number(ctxCode.split("->")[1]) : 450;
  const qv = Float32Array.from((await emb.getEmbeddingFor(t.question)).vector);
  const count = new Map<string, number>(); for (const s of t.retrieval.raw) count.set(s.title, (count.get(s.title) ?? 0) + 1);
  const chunks: any[] = [];
  for (const [title, n] of count) for (const [i, body] of (await chunksFor(title, n, qv)).entries()) chunks.push({ chunkId: `${title}#${i}`, docId: title, title, body, score: 1, matchType: "hybrid" });
  // budget: the trace's own tokensAfter is <= budget; the engine's budget is dynamic, so replay with FAST lookup/other and with the trace's value
  const task = t.route.reasonCodes.find((c: string) => c.startsWith("task:"))?.slice(5);
  const budget = task === "lookup" ? 450 : 700;
  const comp = compressContext(t.question, chunks, { tokenBudget: budget });
  const shownFull = chunks.filter((c) => shown.has(c.title)).map((c) => c.body).join("\n");
  const shownComp = comp.chunks.filter((c: any) => shown.has(c.title)).map((c: any) => `${c.title}\n${c.body}`).join("\n");
  const fullHit = keyHit(shownFull, q.grading), compHit = keyHit(shownComp, q.grading);
  rows.push({ id: t.itemId, cat: q.category, task, budget, traceAfter: after, replayAfter: comp.tokensAfter, declined: t.answer.declined, fullHit, compHit });
}
fs.writeFileSync("rows.json", JSON.stringify(rows, null, 1));
const full = rows.filter((r) => r.fullHit), cut = full.filter((r) => !r.compHit);
console.log(`items with shown sources and a key: ${rows.length}; key in the shown chunks (uncompressed): ${full.length}; key CUT by compression: ${cut.length}; replay tokensAfter vs trace (median): ${rows.map((r) => r.replayAfter).sort((a, b) => a - b)[rows.length >> 1]} vs ${rows.map((r) => r.traceAfter).sort((a, b) => a - b)[rows.length >> 1]}`);
console.log(`declined among key-in-full: ${full.filter((r) => r.declined).length}/${full.length}; among key-cut: ${cut.filter((r) => r.declined).length}/${cut.length}; among key-kept: ${full.filter((r) => r.compHit && r.declined).length}/${full.filter((r) => r.compHit).length}`);
for (const r of cut) console.log(`  CUT ${r.id} (${r.cat}, ${r.task}, budget ${r.budget}, trace ${r.traceAfter}) declined=${r.declined}`);
