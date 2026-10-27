// Sonar exp-07: crypto-pack (format 2) keyword hits shown/retrieved on NON-crypto questions, with the question <-> article
// lead cosine from the pack's own lead_vecs (same gate idea as wikivoyage-lead-gate). Traces: Kiln's night runs
// (ios-main-v5-t0, ios-main-s42) raw + pre sources. Crypto = the item's category is crypto, or the question names
// a crypto term. Read-only.
import { DatabaseSync } from "node:sqlite";
import fs from "node:fs";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const R = "<workspace>/boar-eval/runs/night-2026-10-01/";
const db = new DatabaseSync("<workspace>/shared-data/crypto/boar-crypto.sqlite", { readOnly: true });
const llama = await getLlama({ logLevel: "error" });
const ctx = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext();
const cos = (q, buf) => { const v = new Int8Array(buf.buffer, buf.byteOffset, buf.byteLength); let d = 0, a = 0, b = 0; for (let i = 0; i < v.length; i++) { d += q[i] * v[i]; a += q[i] * q[i]; b += v[i] * v[i]; } return d / Math.sqrt(a * b); };
const CRYPTO = /\b(crypto|bitcoin|btc|ethereum|eth|eip|erc|bip|blockchain|stak|validator|wallet|token|defi|dao|zk|zero[- ]knowledge|rollup|quadratic funding|tornado|privacy pools?|d\/acc|halving|stablecoin|terra|luna|ust|quantum)/i;
const Q = Object.fromEntries(fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => { const x = JSON.parse(l); return [x.id, x]; }));
const isCryptoSrc = (s) => /ethereum\.org|eips\.ethereum|ercs\.ethereum|bips|github\.com\/bitcoin|ethereum specs/i.test(s.source ?? "") || /^(ethereum\.org|Ethereum EIPs\/ERCs|Ethereum specs|Bitcoin BIPs):/.test(s.title) || (s.source ?? "").includes("CC BY-SA 4.0") && !(s.source ?? "").includes("wikivoyage");
const lead = (title) => {
  const t2 = title.includes(": ") ? title.split(": ").slice(1).join(": ") : title;
  for (const t of [title, t2]) { const r = db.prepare("SELECT v.vec FROM articles a JOIN lead_vecs v ON v.article_id = a.id WHERE a.title = ? COLLATE NOCASE LIMIT 1").get(t); if (r) return r.vec; }
  return null;
};
const rows = new Map();
for (const run of ["ios-main-v5-t0", "ios-main-s42"]) for (const l of fs.readFileSync(R + run + ".traces.jsonl", "utf8").split("\n").filter(Boolean)) {
  const t = JSON.parse(l); const q = Q[t.itemId]; if (!q) continue;
  const crypto = q.category === "crypto" || CRYPTO.test(q.question);
  const ev = t.events.filter((e) => e.type === "sources"); const pre = new Set((ev.at(-1)?.sources ?? []).map((s) => s.title));
  for (const s of t.retrieval.raw) {
    const v = lead(s.title); if (!v) continue;           // only sources that resolve to a crypto-pack article
    const key = `${t.itemId}|${s.title}`; if (rows.has(key)) { rows.get(key).shown ||= pre.has(s.title); continue; }
    const qv = Float32Array.from((await ctx.getEmbeddingFor(t.question)).vector);
    rows.set(key, { id: t.itemId, cat: q.category, crypto, title: s.title, shown: pre.has(s.title), cos: +cos(qv, v).toFixed(3) });
  }
}
const all = [...rows.values()];
fs.writeFileSync("pairs.json", JSON.stringify(all, null, 1));
const off = all.filter((r) => !r.crypto), on = all.filter((r) => r.crypto);
console.log(`crypto-pack sources in raw: ${all.length} (on crypto questions ${on.length}, on NON-crypto questions ${off.length}, of which shown before the answer ${off.filter((r) => r.shown).length})`);
for (const th of [0.55, 0.6]) console.log(`gate cos>=${th} on non-crypto questions: keeps ${off.filter((r) => r.cos >= th).length}/${off.length}; on crypto questions it would keep ${on.filter((r) => r.cos >= th).length}/${on.length} (gate not applied there)`);
for (const r of off.sort((a, b) => b.cos - a.cos)) console.log(`${r.cos}\t${r.shown ? "SHOWN" : "     "}\t${r.cat}\t${r.id}\t${r.title}`);
