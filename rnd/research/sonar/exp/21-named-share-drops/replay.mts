import fs from "node:fs";
import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import { WikiPack, setSoleName, properNameRuns } from "./src/rag/wikiPack.ts";
const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
const mk = (p: string) => { const raw = new DatabaseSync(p, { readOnly: true }); return { getAllAsync: async (s: string, a: any[]) => raw.prepare(s).all(...a), getFirstAsync: async (s: string, a: any[]) => raw.prepare(s).get(...a) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, a: any[]) => raw.prepare(s).run(...a) }; };
const P: any = { wv: await WikiPack.open(mk("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite") as any, dec), cr: await WikiPack.open(mk("<workspace>/shared-data/crypto/boar-crypto.sqlite") as any, dec) };
const norm = (s: string) => s.toLowerCase().replace(/’/g, "'").replace(/\s+/g, " ");
const termHit = (t: string, x: string) => (x.startsWith("re:") ? new RegExp(x.slice(3)).test(t) : t.includes(norm(x)));
const keyHit = (text: string, g: any) => { if (!g || !(g.must_any || g.must_k)) return false; const t = norm(text); let ok = (g.must_any ?? []).every((grp: string[]) => grp.some((x) => termHit(t, x))); if (g.must_k) ok &&= g.must_k.terms.filter((x: string) => termHit(t, x)).length >= g.must_k.k; return ok; };
const files = ["<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "<workspace>/boar-eval/runs/night-2026-10-01/questions-v58x.jsonl"];
let changed = 0, n = 0;
for (const f of files) for (const it of fs.readFileSync(f, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l))) {
  const q = it.question ?? it.query; n++;
  for (const k of ["wv", "cr"]) {
    setSoleName(false); const a = (await P[k].searchDetailed(q, { k: 3 })).hits;
    setSoleName(true); const b = (await P[k].searchDetailed(q, { k: 3 })).hits;
    const sig = (h: any[]) => h.map((x) => `${x.title} §${x.section}`).join(" | ");
    if (sig(a) !== sig(b)) { changed++;
      console.log(`\n${it.id} [${k}] runs=${JSON.stringify(properNameRuns(q))} ${q.slice(0, 100)}`);
      console.log(`  before (key ${a.some((h: any) => keyHit(h.text, it.grading))}): ${sig(a)}`);
      console.log(`  after  (key ${b.some((h: any) => keyHit(h.text, it.grading))}): ${sig(b)}`);
      for (const h of b) if (keyHit(h.text, it.grading)) console.log(`     KEY in ${h.title} §${h.section}: ${h.text.slice(0, 200).replace(/\n/g, " ")}`);
    }
  }
}
console.log(`\nquestions ${n}; pack result lists changed ${changed}`);
