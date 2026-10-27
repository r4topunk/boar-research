import fs from "node:fs";
import { DatabaseSync } from "node:sqlite";
import { decompress as fz } from "<workspace>/boar-app/node_modules/fzstd/esm/index.mjs";
import { WikiPack, setPrefetch, titleCandidates } from "./src/rag/wikiPack.ts";
let n = 0;
const mk = (p: string) => { const raw = new DatabaseSync(p, { readOnly: true }); const w = (f: any) => async (s: string, a: any[] = []) => { n++; return f(s, a); };
  return { raw, db: { getAllAsync: w((s: string, a: any[]) => raw.prepare(s).all(...a)), getFirstAsync: w((s: string, a: any[]) => raw.prepare(s).get(...a) ?? null), execAsync: w((s: string) => raw.exec(s)), runAsync: w((s: string, a: any[]) => raw.prepare(s).run(...a)) } }; };
const paths = ["<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", "<workspace>/shared-data/crypto/boar-crypto.sqlite"];
const qs = "<workspace>/boar-eval/bench/v0.1/questions.public.jsonl <workspace>/boar-eval/runs/night-2026-10-01/questions-v58x.jsonl".split(" ").flatMap((f) => fs.readFileSync(f, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)));
// (A) key-level check: every prefetched (source,title) answer == the original single-row queries
let keys = 0, bad = 0;
for (const p of paths) { const m = mk(p); const wp: any = await WikiPack.open(m.db as any, fz);
  for (const it of qs) { await wp.prefetchTitles(titleCandidates(it.question ?? it.query));
    for (const [k, v] of wp.pf) { const [src, t] = [Number(k.split(":")[0]), k.slice(k.indexOf(":") + 1)]; keys++;
      let id = (m.raw.prepare("SELECT id FROM articles WHERE title = ? COLLATE NOCASE AND source = ? ORDER BY views DESC LIMIT 1").get(t, src) as any)?.id ?? null;
      if (id === null) id = (m.raw.prepare("SELECT r.article_id FROM redirects r JOIN articles a ON a.id = r.article_id WHERE r.title = ? AND a.source = ? ORDER BY a.views DESC LIMIT 1").get(t, src) as any)?.article_id ?? null;
      if (id !== v) { bad++; if (bad <= 5) console.log("MISMATCH", p.split("/").pop(), k, "prefetch", v, "orig", id); } } } }
console.log(`key-level: ${keys} (source,title) keys checked, mismatches ${bad}`);
// (B) end-to-end: identical hits and SQL call counts
async function runAll(on: boolean) { setPrefetch(on); n = 0; const out: string[] = []; const packs: any[] = []; for (const p of paths) packs.push(await WikiPack.open(mk(p).db as any, fz));
  const n0 = n; for (const it of qs) for (const wp of packs) { const { hits } = await wp.searchDetailed(it.question ?? it.query, { k: 3 }); out.push(hits.map((h: any) => `${h.chunkId}:${h.title}§${h.section}:${h.text}`).join("|")); } return { calls: n - n0, out }; }
const a = await runAll(false), b = await runAll(true);
console.log(`end-to-end: ${qs.length} questions x 2 packs | SQL calls ${a.calls} (${(a.calls / qs.length).toFixed(0)}/q) -> ${b.calls} (${(b.calls / qs.length).toFixed(0)}/q), ${(100 * (1 - b.calls / a.calls)).toFixed(0)}% fewer | result lists differing: ${a.out.filter((x, i) => x !== b.out[i]).length}/${a.out.length}`);
