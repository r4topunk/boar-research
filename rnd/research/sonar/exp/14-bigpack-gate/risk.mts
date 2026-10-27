// exp-14e: whole-set risk of G1+ on Kiln's ios-enwiki-s42-kic (v1, 72 items). For each keyed item whose answer key is in
// the pre-answer passages (exact text), find the key-bearing source(s); classify each raw candidate as verified (vital5/corpus
// chunk with similarity >= 0.70, or a large-pack hit with question<->lead cos >= 0.70, or named [N]) vs unverified.
// Risk = key-bearing source is unverified AND the raw list holds >= k verified candidates (it could be displaced).
import { DatabaseSync } from "node:sqlite";
import fs from "node:fs";
import { titleCandidates } from "./src/rag/wikiPack.ts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const R = "<workspace>/boar-eval/runs/night-2026-10-01/";
const Q = Object.fromEntries(fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => { const x = JSON.parse(l); return [x.id, x]; }));
const dbs = { crypto: new DatabaseSync("<workspace>/shared-data/crypto/boar-crypto.sqlite", { readOnly: true }), wv: new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true }), big: new DatabaseSync("../../data/leadvecs-top100k.fixed.sqlite", { readOnly: true }) };
const llama = await getLlama({ logLevel: "error" });
const emb = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext();
const cos = (q: Float32Array, buf: Uint8Array) => { const v = new Int8Array(buf.buffer, buf.byteOffset, buf.byteLength); let d = 0, a = 0, b = 0; for (let i = 0; i < v.length; i++) { d += q[i] * v[i]; a += q[i] * q[i]; b += v[i] * v[i]; } return d / Math.sqrt(a * b); };
const norm = (s: string) => s.toLowerCase().replace(/’/g, "'").replace(/\s+/g, " ");
const termHit = (t: string, x: string) => (x.startsWith("re:") ? new RegExp(x.slice(3)).test(t) : t.includes(norm(x)));
const keyHit = (text: string, g: any) => { const t = norm(text); let ok = (g.must_any ?? []).every((grp: string[]) => grp.some((x) => termHit(t, x))); if (g.must_k) ok &&= g.must_k.terms.filter((x: string) => termHit(t, x)).length >= g.must_k.k; return ok; };
function leadCos(qv: Float32Array, s: any): number | null {
  const src = s.source ?? ""; let pack = "", title = s.title;
  if (/wikivoyage/i.test(src)) { pack = "wv"; title = title.replace(/^Wikivoyage: /, ""); }
  else if (/ethereum|eips|ercs|bips|bitcoin/i.test(src) || /^(ethereum\.org|Ethereum EIPs\/ERCs|Ethereum specs|Bitcoin BIPs): /.test(title)) { pack = "crypto"; title = title.replace(/^(ethereum\.org|Ethereum EIPs\/ERCs|Ethereum specs|Bitcoin BIPs): /, ""); }
  else if (src.startsWith("Wikipedia —") && s.similarity == null) pack = "big"; else return null;
  const r = (dbs as any)[pack].prepare("SELECT l.vec FROM articles a JOIN lead_vecs l ON l.article_id = a.id WHERE a.title = ? LIMIT 1").get(title) as any;
  return r ? cos(qv, r.vec) : null;
}
let keyedPre = 0, keyUnverified = 0, atRisk: string[] = [], keyVerified = 0;
for (const l of fs.readFileSync(R + "ios-enwiki-s42-kic.traces.jsonl", "utf8").split("\n").filter(Boolean)) {
  const t = JSON.parse(l); const q = Q[t.itemId]; if (!q || !(q.grading.must_any || q.grading.must_k)) continue;
  const ev = t.events.filter((e: any) => e.type === "sources"); const pre = ev.at(-1)?.sources ?? [];
  if (!keyHit(pre.map((s: any) => s.text ?? "").join("\n"), q.grading)) continue;
  keyedPre++;
  const qv = Float32Array.from((await emb.getEmbeddingFor(t.question)).vector);
  const cands = new Set(titleCandidates(t.question).map((c: string) => c.toLowerCase()));
  const verified = (s: any) => (s.similarity != null && s.similarity >= 0.7) || cands.has(s.title.toLowerCase()) || (leadCos(qv, s) ?? 0) >= 0.7;
  const keySrc = pre.filter((s: any) => keyHit(s.text ?? "", q.grading));
  const anyVerifiedKey = keySrc.some(verified);
  const nVerifiedRaw = new Set(t.retrieval.raw.filter(verified).map((s: any) => s.title + "|" + (s.section ?? ""))).size;
  const k = t.events.find((e: any) => e.type === "retrieve")?.k ?? 4;
  if (anyVerifiedKey) keyVerified++; else { keyUnverified++; if (nVerifiedRaw >= k) atRisk.push(`${t.itemId}(${keySrc.map((s: any) => s.title).join("+") || "split"}; verified raw ${nVerifiedRaw}/k ${k})`); }
}
console.log(`keyed items with the key in pre (v1, s42): ${keyedPre}; key in a G1+-verified source: ${keyVerified}; key only in unverified sources: ${keyUnverified}; of those, at displacement risk (>= k verified candidates in raw): ${atRisk.length}`);
console.log(atRisk.join("\n"));
