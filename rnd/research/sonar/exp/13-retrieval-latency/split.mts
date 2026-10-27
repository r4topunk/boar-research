import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import fs from "node:fs";
import { WikiPack } from "./src/rag/wikiPack.ts";
const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
const raw = new DatabaseSync("<workspace>/shared-data/packs/boar-wiki-sample.sqlite", { readOnly: true });
const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) };
const pack: any = await WikiPack.open(db as any, dec);
const qs = fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l).question);
const t: Record<string, number[]> = { stems: [], titles: [], bm25: [] };
let titleOnlyEnough = 0;
for (const q of qs) {
  let a = performance.now(); const stems = await pack.stems(q); t.stems.push(performance.now() - a);
  a = performance.now(); const named = (await pack.titlesInQuestion(q, stems)).filter((x: any) => x.share >= pack.tuning.namedMinShare); const th = await pack.titleHits(named.map((x: any) => x.id), stems, 5); t.titles.push(performance.now() - a);
  if (th.length >= 4) titleOnlyEnough++;
  a = performance.now(); await pack.bm25Candidates(stems); t.bm25.push(performance.now() - a);
}
const med = (x: number[]) => [...x].sort((p, q) => p - q)[x.length >> 1], p90 = (x: number[]) => [...x].sort((p, q) => p - q)[Math.floor(x.length * 0.9)];
for (const [k, v] of Object.entries(t)) console.log(`${k.padEnd(7)} p50 ${med(v).toFixed(1)} ms  p90 ${p90(v).toFixed(1)} ms`);
console.log(`questions where named-title hits alone fill k=4: ${titleOnlyEnough}/${qs.length}`);
