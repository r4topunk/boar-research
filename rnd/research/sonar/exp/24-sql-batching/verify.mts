import fs from "node:fs";
import { DatabaseSync } from "node:sqlite";
import { decompress as fz } from "<workspace>/boar-app/node_modules/fzstd/esm/index.mjs";
const { WikiPack: Base } = await import("./hb/src/rag/wikiPack.ts");
const { WikiPack: P8 } = await import("./h/src/rag/wikiPack.ts");
let n = 0;
const mk = (p: string) => { const raw = new DatabaseSync(p, { readOnly: true }); const w = (f: any) => async (s: string, a: any[] = []) => { n++; return f(s, a); };
  return { getAllAsync: w((s: string, a: any[]) => raw.prepare(s).all(...a)), getFirstAsync: w((s: string, a: any[]) => raw.prepare(s).get(...a) ?? null), execAsync: w((s: string) => raw.exec(s)), runAsync: w((s: string, a: any[]) => raw.prepare(s).run(...a)) }; };
const paths = ["<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", "<workspace>/shared-data/crypto/boar-crypto.sqlite"];
const qs = "<workspace>/boar-eval/bench/v0.1/questions.public.jsonl <workspace>/boar-eval/runs/night-2026-10-01/questions-v58x.jsonl".split(" ").flatMap((f) => fs.readFileSync(f, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)));
async function run(C: any, opts: any) { n = 0; const packs: any[] = []; for (const p of paths) packs.push(await C.open(mk(p) as any, fz)); const n0 = n; const out: string[] = [];
  for (const it of qs) for (const wp of packs) { const { hits } = await wp.searchDetailed(it.question ?? it.query, opts); out.push(JSON.stringify(hits)); } return { calls: n - n0, out }; }
for (const opts of [{ k: 3 }, { k: 6 }]) {
  const a = await run(Base, opts), b = await run(P8, opts);
  console.log(`k=${opts.k}: ${qs.length} q x 2 packs | calls ${a.calls} -> ${b.calls} (${(100 * (1 - b.calls / a.calls)).toFixed(0)}% fewer, ${(a.calls / qs.length).toFixed(0)} -> ${(b.calls / qs.length).toFixed(0)}/q) | full hit objects differing: ${a.out.filter((x, i) => x !== b.out[i]).length}/${a.out.length}`);
}
