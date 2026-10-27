// Sonar exp-02: Wikivoyage keyword hits bypass the cosine gate (retrieve.ts: large-pack hits "aren't gated").
// For every (question, Wikivoyage title) shown on the iPhone in the 2026-10-01 night runs (611a4b9), compute the
// question ↔ guide-lead cosine from the pack's own lead_vecs, and compare with a hand label (on = the guide is about
// the question's subject). Read-only: shared-data/packs/boar-wikivoyage-en.sqlite, app bge-small.
import { DatabaseSync } from "node:sqlite";
import fs from "node:fs";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const D = "<workspace>/rnd/plumb/data/";
const FILES = ["d10-611a4b9-qwen1.5b-quick-kitA-o2off-o2ab82.jsonl", "d10-611a4b9-qwen1.5b-quick-kitA-o2on-o2ab82.jsonl", "q1-611a4b9-qwen1.5b-quick-kitnovital5-o2off.jsonl", "q4-611a4b9-qwen1.5b-quick-kitA-o2off-bench60-retest.jsonl", "qwen2.5-1.5b-instruct-q4km__iphone-611a4b9-o2off-bench-v0-kitB.jsonl"];
// Hand labels (Sonar, before looking at any cosine): guide titles that are the subject of the question.
const ON = new Set(["Japan","Argentina","Canada","Paris","Mount Everest","Lake Baikal","Lake Tanganyika","Lake Titicaca","Calgary","Russia","Time zones","Brazil","Indonesia","Thirty Years' War","World War I","World War II","World War II in Europe","Soviet Union","Dengue fever","Cold weather","Stay healthy","High-speed rail","South America","Peruvian Amazon","Everest Base Camp Trek","Khumbu","Central Taiwan","Eastern Taiwan","Southern Taiwan","Mars","Travelling on a low-carbohydrate diet","Africa","Altitude sickness@dng","Tanzania@never"]);
const TRAVEL = (c) => c.startsWith("travel") || c.startsWith("local");
const pairs = new Map();
for (const f of FILES) for (const l of fs.readFileSync(D + f, "utf8").split("\n").filter(Boolean)) {
  const r = JSON.parse(l);
  for (const t of r.retrievedTitles ?? []) if (t.startsWith("Wikivoyage: ")) pairs.set(`${r.queryId}|${t}`, { id: r.queryId, cat: r.category, q: r.query, title: t.slice(12) });
}
const db = new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true });
const lead = db.prepare("SELECT v.vec FROM articles a JOIN lead_vecs v ON v.article_id = a.id WHERE a.title = ? COLLATE NOCASE LIMIT 1");
const llama = await getLlama({ logLevel: "error" });
const model = await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" });
const ctx = await model.createEmbeddingContext();
const cache = new Map();
const emb = async (t) => cache.get(t) ?? (cache.set(t, Float32Array.from((await ctx.getEmbeddingFor(t)).vector)), cache.get(t));
const cos = (q, buf) => { const v = new Int8Array(buf.buffer, buf.byteOffset, buf.byteLength); let d = 0, a = 0, b = 0; for (let i = 0; i < v.length; i++) { d += q[i] * v[i]; a += q[i] * q[i]; b += v[i] * v[i]; } return d / Math.sqrt(a * b); };
const rows = [];
for (const p of pairs.values()) {
  const row = lead.get(p.title);
  const c = row ? cos(await emb(p.q), row.vec) : null;
  rows.push({ ...p, cos: c === null ? null : +c.toFixed(3), on: TRAVEL(p.cat) || ON.has(p.title), travel: TRAVEL(p.cat) });
}
rows.sort((a, b) => (b.cos ?? -1) - (a.cos ?? -1));
fs.writeFileSync("pairs.json", JSON.stringify(rows, null, 1));
const rep = [];
for (const th of [0.55, 0.6, 0.65, 0.7]) {
  const keepOn = rows.filter((r) => r.on && r.cos !== null && r.cos >= th).length, on = rows.filter((r) => r.on && r.cos !== null).length;
  const keepOff = rows.filter((r) => !r.on && r.cos !== null && r.cos >= th).length, off = rows.filter((r) => !r.on && r.cos !== null).length;
  rep.push({ threshold: th, on_kept: `${keepOn}/${on}`, noise_kept: `${keepOff}/${off}` });
}
console.table(rep);
console.log("missing lead vec:", rows.filter((r) => r.cos === null).map((r) => r.title).join(", ") || "none");
for (const r of rows) console.log(`${r.cos}\t${r.on ? "ON " : "off"}\t${r.cat}\t${r.id}\t${r.title}\t| ${r.q.slice(0, 60)}`);
await ctx.dispose(); await model.dispose();
