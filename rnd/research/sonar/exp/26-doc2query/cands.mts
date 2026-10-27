// Sonar exp-26 step 1: the expansion set for an L0 Doc2Query-- test. For each v0.1 public question: the articles of its
// BM25 candidate pool (pool 300, wider than the engine's 80, so near-miss competitors are expanded too), the articles it
// names, and the articles of its searchDetailed hits, in the Wikivoyage and crypto packs (kit A). Output: per pack, the
// indexed chunks of those articles with the exact (title, section, body) the builder put in FTS.
import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import fs from "node:fs";
import { WikiPack } from "./src/rag/wikiPack.ts";
const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
const PACKS = { wv: "<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", cr: "<workspace>/shared-data/crypto/boar-crypto.sqlite" };
const SLICE = new Set(JSON.parse(fs.readFileSync("../../../compass/fast-loop/l1-slices.json", "utf8")).slices["retrieval-inkit"].ids as string[]);
const Q = fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
// builder's sectionsAt (scripts/build-wiki-pack.mjs): heading path at each span start, without the "# Title" level
function sectionsAt(text: string, spans: number[][]) {
  const heads = [...text.matchAll(/^(#{1,6})\s+(.*)$/gm)].map((m) => ({ at: m.index!, level: m[1].length, name: m[2].trim() }));
  const out: string[] = []; let h = 0; const path: string[] = [];
  for (const [s] of spans) { while (h < heads.length && heads[h].at < s) { const { level, name } = heads[h++]; path.length = Math.max(0, level - 1); path[level - 1] = name; } out.push(path.slice(1).filter(Boolean).join(" > ")); }
  return out;
}
const out: any = { slice: [...SLICE], packs: {} };
for (const [key, path] of Object.entries(PACKS)) {
  const raw = new DatabaseSync(path, { readOnly: true });
  const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) };
  const pack = await WikiPack.open(db as any, dec);
  const bySlice = new Set<number>(), byAll = new Set<number>();
  for (const q of Q) {
    const stems = await pack.stems(q.question);
    const ids = new Set<number>();
    for (const c of await pack.bm25Candidates(stems, 300, pack.tuning.prior, 1000)) ids.add(c.articleId);
    for (const t of await pack.titlesInQuestion(q.question, stems)) ids.add(t.id);
    for (const h of (await pack.searchDetailed(q.question, { k: 6 })).hits) ids.add(h.articleId);
    for (const id of ids) { byAll.add(id); if (SLICE.has(q.id)) bySlice.add(id); }
  }
  const chunks: any[] = [];
  for (const aid of byAll) {
    const a = await (pack as any).article(aid);
    const rows = raw.prepare("SELECT id, start, end FROM chunks WHERE article_id = ? ORDER BY id").all(aid) as any[];
    const secs = sectionsAt(a.text, rows.map((r) => [r.start, r.end]));
    rows.forEach((r, i) => {
      if (!raw.prepare("SELECT 1 FROM fts_docsize WHERE id = ?").get(r.id)) return; // tables are not indexed
      chunks.push({ id: r.id, articleId: aid, slice: bySlice.has(aid), title: a.title, section: secs[i], body: a.text.slice(r.start, r.end) });
    });
  }
  out.packs[key] = { articlesAll: byAll.size, articlesSlice: bySlice.size, chunks };
  console.log(`${key}: articles all-60 ${byAll.size}, slice-24 ${bySlice.size}; indexed chunks all ${chunks.length}, slice ${chunks.filter((c) => c.slice).length}; body chars ${chunks.reduce((s, c) => s + c.body.length, 0)}`);
}
fs.writeFileSync("cands.json", JSON.stringify(out));
