import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import fs from "node:fs";
import { WikiPack } from "./src/rag/wikiPack.ts";
const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
const PACKS = { wv: "<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", cr: "<workspace>/shared-data/crypto/boar-crypto.sqlite" };
const SLICE = new Set(JSON.parse(fs.readFileSync("../../../compass/fast-loop/l1-slices.json", "utf8")).slices["retrieval-inkit"].ids as string[]);
const Q = fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)).filter((q) => SLICE.has(q.id));
for (const [key, path] of Object.entries(PACKS)) {
  const raw = new DatabaseSync(path, { readOnly: true });
  const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) };
  const pack = await WikiPack.open(db as any, dec);
  for (const pool of [80, 150, 300]) {
    const ch = new Set<number>(), named = new Set<number>(), hitArt = new Set<number>();
    for (const q of Q) {
      const stems = await pack.stems(q.question);
      for (const c of await pack.bm25Candidates(stems, pool, pack.tuning.prior, 1000)) ch.add(c.chunkId);
      for (const t of await pack.titlesInQuestion(q.question, stems)) named.add(t.id);
      for (const h of (await pack.searchDetailed(q.question, { k: 6 })).hits) hitArt.add(h.articleId);
    }
    const nNamed = [...named].reduce((s, a) => s + (raw.prepare("SELECT count(*) n FROM chunks WHERE article_id=?").get(a) as any).n, 0);
    const nHit = [...hitArt].reduce((s, a) => s + (raw.prepare("SELECT count(*) n FROM chunks WHERE article_id=?").get(a) as any).n, 0);
    console.log(`${key} pool ${pool}: pool chunks ${ch.size}; named articles ${named.size} (${nNamed} chunks); hit articles ${hitArt.size} (${nHit} chunks)`);
  }
}
