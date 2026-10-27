import fs from "node:fs";
import { DatabaseSync } from "node:sqlite";
import { decompress as fz } from "<workspace>/boar-app/node_modules/fzstd/esm/index.mjs";
import { WikiPack } from "./src/rag/wikiPack.ts";
(globalThis as any).__onArticle = (pack: any, id: number) => { if (!pack.meta?.name?.includes("Wikivoyage")) (READS[CUR] ??= []).push(id); };
const READS: Record<string, number[]> = {}; let CUR = ""; let dT = 0, dB = 0, dN = 0, sqlT = 0, sqlN = 0;
const dec = (d: Uint8Array) => { const t = performance.now(); const o = fz(d); dT += performance.now() - t; dB += o.length; dN++; return o; };
const mk = (p: string) => { const raw = new DatabaseSync(p, { readOnly: true }); const w = (f: any) => async (s: string, a: any[] = []) => { const t = performance.now(); const r = f(s, a); sqlT += performance.now() - t; sqlN++; return r; };
  return { getAllAsync: w((s: string, a: any[]) => raw.prepare(s).all(...a)), getFirstAsync: w((s: string, a: any[]) => raw.prepare(s).get(...a) ?? null), execAsync: w((s: string) => raw.exec(s)), runAsync: w((s: string, a: any[]) => raw.prepare(s).run(...a)) }; };
const packs = [await WikiPack.open(mk("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite") as any, dec), await WikiPack.open(mk("<workspace>/shared-data/crypto/boar-crypto.sqlite") as any, dec)];
const qs = fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const rows = [];
for (const it of qs) {
  for (const p of packs as any[]) { p.blocks?.clear?.(); p.articles?.clear?.(); }   // cold caches per question, as on a first ask
  CUR = it.id; dT = dB = dN = sqlT = sqlN = 0; const t0 = performance.now();
  for (const p of packs) await p.searchDetailed(it.question, { k: 3 });
  const tot = performance.now() - t0; rows.push({ id: it.id, tot, dT, dB, dN, sqlT, sqlN });
}
const q = (k: string, p = 0.5) => { const v = rows.map((r: any) => r[k]).sort((a, b) => a - b); return +v[Math.floor(p * (v.length - 1))].toFixed(1); };
console.log(`questions ${rows.length} (cold block cache per question, fzstd JS)`);
for (const k of ["tot", "dT", "sqlT", "dB", "dN", "sqlN"]) console.log(`  ${k.padEnd(5)} p50 ${q(k)}  p90 ${q(k, 0.9)}`);
const share = rows.map((r) => r.dT / r.tot).sort((a, b) => a - b); console.log(`  decompress share of pack search: p50 ${share[Math.floor(share.length / 2)].toFixed(2)}`);
fs.writeFileSync("prof.json", JSON.stringify(rows)); fs.writeFileSync("reads-cr.json", JSON.stringify(READS)); console.log("questions with wv reads", Object.keys(READS).length, "reads", Object.values(READS).flat().length);
