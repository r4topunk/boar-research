import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import { WikiPack, titleCandidates, isTravelQuestion } from "./src/rag/wikiPack.ts";
const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
const raw = new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true });
const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) };
const pack: any = await WikiPack.open(db as any, dec);
const q = "How do I get from Chiang Mai to Pai, and what should I know about the road?";
const stems = await pack.stems(q);
console.log("isTravelQuestion:", isTravelQuestion(q));
console.log("titleCandidates:", titleCandidates(q).slice(0, 12));
const named = await pack.titlesInQuestion(q, stems);
for (const n of named) { const a = raw.prepare("SELECT title FROM articles WHERE id = ?").get(n.id) as any; console.log(`  named: ${a.title} share ${n.share.toFixed(3)} (namedMinShare ${pack.tuning.namedMinShare})`); }
console.log("stems:", stems.map((s: any) => `${s.stem}:${s.idf.toFixed(2)}`).join(" "));
const { hits } = await pack.searchDetailed(q, { k: 4 });
console.log("hits:", hits.map((h: any) => `${h.title} §${h.section} via=${h.via}`));
