import fs from "node:fs";
import { DatabaseSync } from "node:sqlite";
import { decompress as fz } from "<workspace>/boar-app/node_modules/fzstd/esm/index.mjs";
import { WikiPack, setSkipAbsent } from "./src/rag/wikiPack.ts";
let n = 0; const ST = new Map<string, number>();
const mk = (p: string) => { const raw = new DatabaseSync(p, { readOnly: true }); const w = (f: any) => async (s: string, a: any[] = []) => { n++; const k = s.replace(/\s+/g, " ").slice(0, 60); ST.set(k, (ST.get(k) ?? 0) + 1); return f(s, a); };
  return { raw, db: { getAllAsync: w((s: string, a: any[]) => raw.prepare(s).all(...a)), getFirstAsync: w((s: string, a: any[]) => raw.prepare(s).get(...a) ?? null), execAsync: w((s: string) => raw.exec(s)), runAsync: w((s: string, a: any[]) => raw.prepare(s).run(...a)) } }; };
const paths = ["<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", "<workspace>/shared-data/crypto/boar-crypto.sqlite"];
const qs = [..."<workspace>/boar-eval/bench/v0.1/questions.public.jsonl <workspace>/boar-eval/runs/night-2026-10-01/questions-v58x.jsonl".split(" ").flatMap((f) => fs.readFileSync(f, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)))];
async function runAll(skip: boolean) {
  setSkipAbsent(skip); n = 0; ST.clear(); const out: string[] = [];
  const packs: any[] = []; for (const p of paths) { const m = mk(p); const wp: any = await WikiPack.open(m.db as any, fz);
    (globalThis as any).__present ??= new Map(); (globalThis as any).__present.set(wp, new Set((m.raw.prepare("SELECT DISTINCT source FROM articles").all() as any[]).map((r) => r.source))); packs.push(wp); }
  const n0 = n; const t0 = performance.now();
  for (const it of qs) for (const wp of packs) { const { hits } = await wp.searchDetailed(it.question ?? it.query, { k: 3 }); out.push(hits.map((h: any) => `${h.chunkId}:${h.title}§${h.section}:${h.text.length}`).join("|")); }
  return { calls: n - n0, ms: performance.now() - t0, out, top: [...ST.entries()].sort((a, b) => b[1] - a[1]).slice(0, 4) };
}
const a = await runAll(false), b = await runAll(true);
const diff = a.out.filter((x, i) => x !== b.out[i]).length;
console.log(`questions ${qs.length} x 2 packs | SQL calls base ${a.calls} (${(a.calls / qs.length).toFixed(0)}/q) -> skip-absent ${b.calls} (${(b.calls / qs.length).toFixed(0)}/q), ${(100 * (1 - b.calls / a.calls)).toFixed(0)}% fewer | result lists differing: ${diff}/${a.out.length}`);
console.log("top base:", a.top); console.log("top skip:", b.top);
console.log("cold article() reads by caller (both runs):", [...((globalThis as any).__AC ?? new Map()).entries()].sort((x: any, y: any) => y[1] - x[1]).slice(0, 8));
