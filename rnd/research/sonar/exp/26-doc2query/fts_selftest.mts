// identity test: delete + reinsert the SAME text for 2000 chunks of the copy -> BM25 candidates for all slice questions identical
import { DatabaseSync } from "node:sqlite"; import zlib from "node:zlib"; import fs from "node:fs";
import { WikiPack } from "./src/rag/wikiPack.ts"; import { rewrite } from "./fts.mts";
const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
const [orig, copy] = process.argv.slice(2);
const Q = fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
async function cands(path: string) { const raw = new DatabaseSync(path, { readOnly: true }); const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) };
  const pack = await WikiPack.open(db as any, dec); const out: string[] = []; for (const q of Q) out.push(JSON.stringify((await pack.bm25Candidates(await pack.stems(q.question))).map((c) => [c.chunkId, c.score.toFixed(6)]))); raw.close(); return out; }
const ids = (new DatabaseSync(orig, { readOnly: true }).prepare("SELECT id FROM fts_docsize ORDER BY id LIMIT 2000 OFFSET 5000").all() as any[]).map((r) => r.id);
rewrite(copy, new Map(ids.map((i) => [i, ""])));
const a = await cands(orig), b = await cands(copy);
console.log(`identity rewrite of ${ids.length} chunks: ${a.filter((x, i) => x === b[i]).length}/${a.length} questions with identical candidates+scores`);
const ck = new DatabaseSync(copy); ck.exec("INSERT INTO fts(fts, rank) VALUES('integrity-check', 1)"); console.log("integrity-check ok");
