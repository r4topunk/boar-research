// Sonar exp-19: cheap relevance signals for each (question, prompt passage) pair of and-qwen-s44 (exact prompt text).
import { DatabaseSync } from "node:sqlite";
import fs from "node:fs";
import { scoreSentences } from "./src/rag/compress.ts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const pairs = JSON.parse(fs.readFileSync("pairs.json", "utf8"));
const Q = Object.fromEntries(fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => { const x = JSON.parse(l); return [x.id, x]; }));
const llama = await getLlama({ logLevel: "error" });
const bge = await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" });
const emb = await bge.createEmbeddingContext();
const vec = async (t: string) => Float32Array.from((await emb.getEmbeddingFor(bge.tokenize(t).slice(0, 480))).vector);
const cos = (a: Float32Array, b: Float32Array) => { let d = 0, x = 0, y = 0; for (let i = 0; i < a.length; i++) { d += a[i] * b[i]; x += a[i] * a[i]; y += b[i] * b[i]; } return d / Math.sqrt(x * y); };
const cosI8 = (q: Float32Array, buf: Uint8Array) => { const v = new Int8Array(buf.buffer, buf.byteOffset, buf.byteLength); let d = 0, a = 0, b = 0; for (let i = 0; i < v.length; i++) { d += q[i] * v[i]; a += q[i] * q[i]; b += v[i] * v[i]; } return d / Math.sqrt(a * b); };
const lv = { wv: new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true }), cr: new DatabaseSync("<workspace>/shared-data/crypto/boar-crypto.sqlite", { readOnly: true }) };
const lead = (q: Float32Array, title: string) => { const wv = title.startsWith("Wikivoyage: "); const t2 = wv ? title.slice(12) : title.replace(/^(ethereum\.org|Ethereum EIPs\/ERCs|Ethereum specs|Bitcoin BIPs): /, ""); const r = (wv ? lv.wv : lv.cr).prepare("SELECT l.vec FROM articles a JOIN lead_vecs l ON l.article_id = a.id WHERE a.title = ? LIMIT 1").get(t2) as any; return r ? cosI8(q, r.vec) : null; };
const norm = (s: string) => s.toLowerCase().replace(/’/g, "'").replace(/\s+/g, " ");
const termHit = (t: string, x: string) => (x.startsWith("re:") ? new RegExp(x.slice(3)).test(t) : t.includes(norm(x)));
const keyHit = (text: string, g: any) => { if (!g || !(g.must_any || g.must_k)) return null; const t = norm(text); let ok = (g.must_any ?? []).every((grp: string[]) => grp.some((x) => termHit(t, x))); if (g.must_k) ok &&= g.must_k.terms.filter((x: string) => termHit(t, x)).length >= g.must_k.k; return ok; };
const out = [];
for (const p of pairs) {
  const qv = await vec(p.question);
  const section = (p.passage.match(/^([^:\n]{2,80}):\s/) ?? [])[1] ?? "";
  const ss = scoreSentences(p.question, [{ chunkId: "x", docId: "x", title: p.title, body: p.passage, score: 1, matchType: "lexical" } as any]);
  out.push({ ...p, passage: undefined, passCos: +cos(qv, await vec(p.passage)).toFixed(3), titleCos: +cos(qv, await vec(`${p.title}${section ? " > " + section : ""}`)).toFixed(3), leadCos: (() => { const l = lead(qv, p.title); return l === null ? null : +l.toFixed(3); })(), bestSent: +Math.max(0, ...ss.map((s: any) => s.score)).toFixed(3), key: keyHit(p.passage, Q[p.item]?.grading) });
}
fs.writeFileSync("signals.json", JSON.stringify(out, null, 1));
console.log(`signals for ${out.length} pairs; key-bearing passages: ${out.filter((o) => o.key).length}`);
