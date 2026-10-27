import { DatabaseSync } from "node:sqlite"; import zlib from "node:zlib"; import fs from "node:fs";
import { WikiPack } from "./src/rag/wikiPack.ts";
export const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
export const BASE = { wv: "<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", cr: "<workspace>/shared-data/crypto/boar-crypto.sqlite" } as Record<string, string>;
export async function openPack(path: string) { const raw = new DatabaseSync(path, { readOnly: true }); const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) }; return { raw, pack: await WikiPack.open(db as any, dec) }; }
export const SLICE = JSON.parse(fs.readFileSync("../../../compass/fast-loop/l1-slices.json", "utf8")).slices["retrieval-inkit"].ids as string[];
export const Q: Record<string, any> = Object.fromEntries(fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n").filter(Boolean).map((l) => { const x = JSON.parse(l); return [x.id, x]; }));
const norm = (s: string) => s.toLowerCase().replace(/’/g, "'").replace(/\s+/g, " ");
const termHit = (t: string, x: string) => (x.startsWith("re:") ? new RegExp(x.slice(3)).test(t) : t.includes(norm(x)));
export const keyed = (id: string) => !!(Q[id]?.grading?.must_any || Q[id]?.grading?.must_k);
export const keyHit = (text: string, g: any) => { const t = norm(text); let ok = (g.must_any ?? []).every((grp: string[]) => grp.some((x) => termHit(t, x))); if (g.must_k) ok &&= g.must_k.terms.filter((x: string) => termHit(t, x)).length >= g.must_k.k; return ok; };
// engine retrieval k and the trace's question vector inputs, from the base run and-qwen-s42
export const TRACE: Record<string, any> = Object.fromEntries(fs.readFileSync("<workspace>/boar-eval/runs/night-2026-10-01/and-qwen-s42.traces.jsonl", "utf8").split("\n").filter(Boolean).map((l) => { const t = JSON.parse(l); return [t.itemId, t]; }));
export const kOf = (id: string) => TRACE[id]?.events.find((e: any) => e.type === "retrieve")?.k ?? 4;
