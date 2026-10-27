// Anvil copy of Sonar exp-11 run-k.mts (read-only import of Sonar's engine copy); adds passage size and fixes the per-K output name.
// Sonar exp-11: right article, wrong passage? Replays WikiPack.searchDetailed @0cfd4a77 (engine code, exp-09 copy) on
// boar-wikivoyage-en and boar-crypto for the 52 keyed bench-v0.1 items, and compares the answer key in (a) the passages
// the pack returns vs (b) the whole text of the same articles. Matters for the full-article enwiki pack (long articles).
import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import fs from "node:fs";
import { WikiPack } from "<workspace>/rnd/research/sonar/exp/11-passage-selection/src/rag/wikiPack.ts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
async function open(path: string) {
  const raw = new DatabaseSync(path, { readOnly: true });
  const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) };
  return { pack: await WikiPack.open(db as any, dec), raw };
}
const packs = [await open("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite"), await open("<workspace>/shared-data/crypto/boar-crypto.sqlite")];
const llama = await getLlama({ logLevel: "error" });
const emb = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext();
const norm = (s: string) => s.toLowerCase().replace(/’/g, "'").replace(/\s+/g, " ");
const termHit = (t: string, x: string) => (x.startsWith("re:") ? new RegExp(x.slice(3)).test(t) : t.includes(norm(x)));
const keyHit = (text: string, g: any) => { const t = norm(text); let ok = (g.must_any ?? []).every((grp: string[]) => grp.some((x) => termHit(t, x))); if (g.must_k) ok &&= g.must_k.terms.filter((x: string) => termHit(t, x)).length >= g.must_k.k; return ok; };
const article = (raw: DatabaseSync, id: number) => { const a = raw.prepare("SELECT block_id, off, len FROM articles WHERE id = ?").get(id) as any; const z = (raw.prepare("SELECT zdata FROM blocks WHERE id = ?").get(a.block_id) as any).zdata; return Buffer.from(dec(z)).subarray(a.off, a.off + a.len).toString("utf8"); };
const out: any[] = [];
for (const l of fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean)) {
  const q = JSON.parse(l); if (!(q.grading.must_any || q.grading.must_k)) continue;
  const qv = Float32Array.from((await emb.getEmbeddingFor(q.question)).vector);
  let passages = "", articles = "", titles: string[] = [];
  for (const { pack, raw } of packs) {
    const { hits } = await pack.searchDetailed(q.question, { k: Number(process.env.K ?? 4), queryVec: qv });
    passages += hits.map((h) => `${h.section}: ${h.text}`).join("\n");
    const ids = [...new Set(hits.map((h) => h.articleId))];
    articles += ids.map((id) => article(raw, id)).join("\n");
    titles.push(...hits.map((h) => `${h.title}§${h.section || "lead"}`));
  }
  out.push({ id: q.id, passages: keyHit(passages, q.grading), articles: keyHit(articles, q.grading), titles, passageChars: passages.length });
}
fs.writeFileSync(`rows-k${process.env.K}.json`, JSON.stringify(out, null, 1));
const ch = out.map((r) => r.passageChars).sort((a, b) => a - b); console.log(`K=${process.env.K} passage chars median ${ch[Math.floor(ch.length / 2)]} (~${Math.round(ch[Math.floor(ch.length / 2)] / 4)} tokens)`);
const wrongPassage = out.filter((r) => r.articles && !r.passages);
console.log(`keyed items ${out.length}; key in returned passages ${out.filter((r) => r.passages).length}; key in the same articles' full text ${out.filter((r) => r.articles).length}; right article / wrong passage ${wrongPassage.length}`);
for (const r of wrongPassage) console.log(`  ${r.id}: ${r.titles.slice(0, 5).join(" | ")}`);
