// T-K6 engine check: opens a pack with the T-K2 tree's WikiPack (wt/packs) read-only, runs queries, prints hits with
// the citation string from packHitToChunk. Run from the scratch root (see run-check.sh): PACK=… QUERIES='q1|q2' PACKID=…
import { it, vi } from "vitest";
import { DatabaseSync } from "node:sqlite";
import { decompress } from "fzstd";
vi.mock("expo-file-system/legacy", () => ({ documentDirectory: "file:///docs/" }));
vi.mock("expo-sqlite", () => ({}));
vi.mock("<workspace>/wt/packs/src/rag/embed", () => ({ embeddingEngine: {} }));
import { SOURCES, WikiPack } from "<workspace>/wt/packs/src/rag/wikiPack";
import { packHitToChunk } from "<workspace>/wt/packs/src/rag/packs";

function ro(path: string) {
  const db = new DatabaseSync(path, { readOnly: true });
  const P = (p?: unknown[]) => (p ?? []) as any[];
  return {
    async execAsync(sql: string) { db.exec(sql); },
    async getAllAsync<T>(sql: string, p?: unknown[]) { return db.prepare(sql).all(...P(p)) as T[]; },
    async getFirstAsync<T>(sql: string, p?: unknown[]) { return (db.prepare(sql).get(...P(p)) as T | undefined) ?? null; },
    async runAsync(sql: string, p?: unknown[]) { return db.prepare(sql).run(...P(p)); },
    raw: db,
  };
}

it("pack check", async () => {
  const path = process.env.PACK!, id = process.env.PACKID!;
  const db = ro(path);
  const pack = await WikiPack.open(db, decompress);
  const one = (q: string) => Object.values(db.raw.prepare(q).get() as object)[0];
  console.log(JSON.stringify({ pack: id, sources: (db.raw.prepare("SELECT source, count(*) n FROM articles GROUP BY source").all() as any[]).map((r) => `${r.source}=${SOURCES[r.source]}:${r.n}`),
    articles: one("SELECT count(*) FROM articles"), lead_vecs: one("SELECT count(*) FROM lead_vecs"), fts_docsize: one("SELECT count(*) FROM fts_docsize"),
    redirects: one("SELECT count(*) FROM redirects") }));
  for (const q of process.env.QUERIES!.split("|")) {
    const t = Date.now();
    const hits = await pack.search(q, { k: 5 });
    console.log(`\nQ: ${q}  (${hits.length} hits, ${Date.now() - t} ms)`);
    for (const h of hits.slice(0, 5)) {
      const c = packHitToChunk(id, h);
      console.log(`  - ${h.title} | ${h.section || "(lead)"} | ${h.score.toFixed(3)} | ${c.source}\n    ${h.text.slice(0, 140).replace(/\n/g, " ")}`);
    }
  }
  for (const term of (process.env.FTS ?? "").split("|").filter(Boolean))
    console.log(`FTS ${term}: ${one(`SELECT count(*) FROM fts WHERE fts MATCH '${term}'`)}`);
}, 120000);
