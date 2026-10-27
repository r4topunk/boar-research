import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import fs from "node:fs";
import { WikiPack } from "./src/rag/wikiPack.ts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
const raw = new DatabaseSync("<workspace>/shared-data/packs/boar-wiki-sample.sqlite", { readOnly: true });
const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) };
const pack: any = await WikiPack.open(db as any, dec);
const llama = await getLlama({ logLevel: "error" });
const emb = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext();
const norm = (s: string) => s.toLowerCase().replace(/’/g, "'").replace(/\s+/g, " ");
const termHit = (t: string, x: string) => (x.startsWith("re:") ? new RegExp(x.slice(3)).test(t) : t.includes(norm(x)));
const keyHit = (text: string, g: any) => { const t = norm(text); let ok = (g.must_any ?? []).every((grp: string[]) => grp.some((x) => termHit(t, x))); if (g.must_k) ok &&= g.must_k.terms.filter((x: string) => termHit(t, x)).length >= g.must_k.k; return ok; };
let full = 0, titles = 0, both = 0, n = 0;
for (const l of fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean)) {
  const q = JSON.parse(l); if (!(q.grading.must_any || q.grading.must_k)) continue; n++;
  const qv = Float32Array.from((await emb.getEmbeddingFor(q.question)).vector);
  const f = keyHit((await pack.searchDetailed(q.question, { k: 4, queryVec: qv })).hits.map((h: any) => h.text).join("\n"), q.grading);
  const stems = await pack.stems(q.question);
  const named = (await pack.titlesInQuestion(q.question, stems)).filter((x: any) => x.share >= pack.tuning.namedMinShare);
  const t = keyHit((await pack.titleHits(named.map((x: any) => x.id), stems, 5)).map((h: any) => h.text).join("\n"), q.grading);
  full += +f; titles += +t; both += +(f && t);
}
console.log(`keyed ${n}: key in full search passages ${full}; in named-title passages only ${titles}; both ${both}`);
