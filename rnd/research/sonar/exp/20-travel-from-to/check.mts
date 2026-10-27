import fs from "node:fs";
import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import { WikiPack, isTravelQuestion } from "./src/rag/wikiPack.ts";
const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
const raw = new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true });
const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) };
const pack: any = await WikiPack.open(db as any, dec);
const q = "How do I get from Chiang Mai to Pai, and what should I know about the road?";
console.log("patched isTravelQuestion:", isTravelQuestion(q));
const { hits } = await pack.searchDetailed(q, { k: 3 });
console.log("k=3 hits:", hits.map((h: any) => `${h.title} §${h.section} via=${h.via}`));
const pai = hits.filter((h: any) => h.title === "Pai").map((h: any) => h.text).join(" ");
console.log("Pai passage mentions route/1095/bus/minibus/drive:", /1095|minibus|minivan|\bbus\b|route|drive|motorbike/i.test(pai), "|", pai.slice(0, 300));
// false-fire scan: which public bench questions does the new pattern newly mark as travel?
const re = /\b(get|go|travel|getting|going) from \p{Lu}[\p{L}.' -]*? to \p{Lu}/u;
const qs = fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
console.log("public v0.1 questions matching the new pattern:", qs.filter((x) => re.test(x.question)).map((x) => `${x.id}: ${x.question}`));
