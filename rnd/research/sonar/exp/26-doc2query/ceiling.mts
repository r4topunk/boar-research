// exp-26 step 0: where do slice items' key chunks sit? Per keyed retrieval-inkit item and pack: chunks whose own text
// (title + section + body) satisfies the precheck key; best rank of such a chunk in the BM25 candidate list (pool 2000);
// whether it is in a named article; whether today's searchDetailed hits (k=6) already carry the key.
import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import fs from "node:fs";
import { WikiPack } from "./src/rag/wikiPack.ts";
const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
const PACKS = { wv: "<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", cr: "<workspace>/shared-data/crypto/boar-crypto.sqlite" };
const SLICE = new Set(JSON.parse(fs.readFileSync("../../../compass/fast-loop/l1-slices.json", "utf8")).slices["retrieval-inkit"].ids as string[]);
const Q = fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)).filter((q) => SLICE.has(q.id) && (q.grading.must_any || q.grading.must_k));
const norm = (s: string) => s.toLowerCase().replace(/’/g, "'").replace(/\s+/g, " ");
const termHit = (t: string, x: string) => (x.startsWith("re:") ? new RegExp(x.slice(3)).test(t) : t.includes(norm(x)));
const keyHit = (text: string, g: any) => { const t = norm(text); let ok = (g.must_any ?? []).every((grp: string[]) => grp.some((x) => termHit(t, x))); if (g.must_k) ok &&= g.must_k.terms.filter((x: string) => termHit(t, x)).length >= g.must_k.k; return ok; };
const res: any = {};
for (const [key, path] of Object.entries(PACKS)) {
  const raw = new DatabaseSync(path, { readOnly: true });
  const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) };
  const pack = await WikiPack.open(db as any, dec);
  // scan every chunk once
  const keyChunks: Record<string, Set<number>> = Object.fromEntries(Q.map((q) => [q.id, new Set<number>()]));
  const arts = raw.prepare("SELECT id, title, block_id, off, len FROM articles ORDER BY block_id").all() as any[];
  let blk = -1, buf: Buffer = Buffer.alloc(0);
  const chq = raw.prepare("SELECT id, start, end FROM chunks WHERE article_id = ?");
  for (const a of arts) {
    if (a.block_id !== blk) { blk = a.block_id; buf = zlib.zstdDecompressSync((raw.prepare("SELECT zdata FROM blocks WHERE id=?").get(blk) as any).zdata); }
    const text = buf.subarray(a.off, a.off + a.len).toString("utf8");
    for (const c of chq.all(a.id) as any[]) { const t = `${a.title}\n${text.slice(c.start, c.end)}`; for (const q of Q) if (keyHit(t, q.grading)) keyChunks[q.id].add(c.id); }
  }
  for (const q of Q) {
    const stems = await pack.stems(q.question);
    const cands = await pack.bm25Candidates(stems, 2000, pack.tuning.prior, 100000);
    const rank = cands.findIndex((c) => keyChunks[q.id].has(c.chunkId));
    const named = (await pack.titlesInQuestion(q.question, stems)).filter((t) => t.share >= pack.tuning.namedMinShare).map((t) => t.id);
    const keyArts = new Set([...keyChunks[q.id]].map((id) => (raw.prepare("SELECT article_id a FROM chunks WHERE id=?").get(id) as any).a));
    const hits = (await pack.searchDetailed(q.question, { k: 6 })).hits;
    (res[q.id] ??= {})[key] = { nKeyChunks: keyChunks[q.id].size, nKeyArticles: keyArts.size, bestPoolRank: rank, namedHasKey: named.some((n) => keyArts.has(n)), hitsHaveKey: hits.some((h) => keyChunks[q.id].has(h.chunkId)) };
  }
}
for (const q of Q) console.log(q.id.padEnd(12), JSON.stringify(res[q.id]));
fs.writeFileSync("ceiling.json", JSON.stringify(res, null, 1));
