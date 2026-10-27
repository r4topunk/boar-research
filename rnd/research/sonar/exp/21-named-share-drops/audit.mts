import fs from "node:fs";
import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import { WikiPack } from "./src/rag/wikiPack.ts";
const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
const mk = (p: string) => { const raw = new DatabaseSync(p, { readOnly: true }); return { raw, db: { getAllAsync: async (s: string, a: any[]) => raw.prepare(s).all(...a), getFirstAsync: async (s: string, a: any[]) => raw.prepare(s).get(...a) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, a: any[]) => raw.prepare(s).run(...a) } }; };
const packs = [["wv", "<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite"], ["cr", "<workspace>/shared-data/crypto/boar-crypto.sqlite"]] as const;
const P: any = {}; for (const [k, p] of packs) { const m = mk(p); P[k] = { raw: m.raw, pack: await WikiPack.open(m.db as any, dec) }; }
const norm = (s: string) => s.toLowerCase().replace(/’/g, "'").replace(/\s+/g, " ");
const termHit = (t: string, x: string) => (x.startsWith("re:") ? new RegExp(x.slice(3)).test(t) : t.includes(norm(x)));
const keyHit = (text: string, g: any) => { if (!g || !(g.must_any || g.must_k)) return null; const t = norm(text); let ok = (g.must_any ?? []).every((grp: string[]) => grp.some((x) => termHit(t, x))); if (g.must_k) ok &&= g.must_k.terms.filter((x: string) => termHit(t, x)).length >= g.must_k.k; return ok; };
const qs = fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
for (const it of qs) for (const k of ["wv", "cr"]) {
  const { pack, raw } = P[k]; const stems = await pack.stems(it.question); const named = await pack.titlesInQuestion(it.question, stems);
  const min = pack.tuning.namedMinShare;
  for (const n of named) if (n.share < min) {
    const a = raw.prepare("SELECT title FROM articles WHERE id = ?").get(n.id) as any;
    const text = (await pack.article(n.id)).text;
    console.log(`${it.id} [${k}] dropped named "${a.title}" share ${n.share.toFixed(3)} | key in article: ${text ? keyHit(text, it.grading) : "?"} | ${it.question.slice(0, 90)}`);
  }
}
