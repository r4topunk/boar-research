// L0 recorder (Node, on the MacBook): runs BOAR's real retrieve() (engine 0cfd4a77, g75 kit: corpus-standard + corpus-full +
// boar-crypto + boar-wikivoyage-en) on the exact (query, k) pairs the g75-matched desktop run retrieved with, and logs every
// expo-sqlite call + result and every query embedding. Output rec/rec.json feeds the Hermes replay (replay.ts).
// Setup mirrors boar-eval/adapters/desktop-node/runner/adapter.ts setupAppRetrieval (same shims, same corpus seeding).
import { registerHooks } from "node:module";
import { existsSync, mkdirSync, readFileSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { createHash } from "node:crypto";

const HERE = new URL(".", import.meta.url).pathname;
const ROOT = join(HERE, "app");
const SHARED = "<workspace>/shared-data";
const PACKS = [`${SHARED}/crypto/boar-crypto.sqlite`, `${SHARED}/packs/boar-wikivoyage-en.sqlite`];
const PACK_SHA: Record<string, string> = {
  "boar-crypto": "ae9fbd2c7a46a46a815d46d0283e7b192adb4c342b38a2adc4881e8f9d8831fb",
  "boar-wikivoyage-en": "ff8595e32f56b8b84e20464afd8bf88532d47d2d82d799e3df8489440004b66e",
};
const TRACES = "<workspace>/boar-eval/runs/g75desk/g75desk-s42.traces.jsonl";

const shim = (f: string) => new URL(`./shims/${f}`, import.meta.url).href;
const SHIMS: Record<string, string> = {
  "expo-sqlite": shim("expo-sqlite.mjs"), "expo-file-system": shim("expo-file-system.mjs"),
  "expo-file-system/legacy": shim("expo-file-system.mjs"), "llama.rn": shim("llama-rn.mjs"),
  "react-native": shim("react-native.mjs"), "ram-monitor": shim("ram-monitor.mjs"),
};
(registerHooks as any)({
  resolve: (spec: string, ctx: any, next: any) => {
    if (SHIMS[spec]) return { url: SHIMS[spec], shortCircuit: true };
    try { return next(spec, ctx); } catch (e) { if (/^[./]/.test(spec)) throw e; return next(spec, { ...ctx, parentURL: new URL("./app/package.json", import.meta.url).href }); }
  },
});

for (const p of PACKS) {
  const id = p.split("/").pop()!.replace(/\.sqlite$/, "");
  const got = createHash("sha256").update(readFileSync(p)).digest("hex");
  if (got !== PACK_SHA[id]) throw new Error(`${id}: sha ${got} != device kit ${PACK_SHA[id]}`);
}
const appDir = join(HERE, "rec", "appdir");
rmSync(appDir, { recursive: true, force: true });
process.env.BOAR_APP_DIR = appDir;
mkdirSync(join(appDir, "corpus"), { recursive: true });
const manifest: any = await import(join(ROOT, "src/models/manifest.ts"));
const catalog: any[] = [...(manifest.MODEL_CATALOG ?? []), ...(manifest.CORPUS_CATALOG ?? [])];
const link = (src: string, rel: string) => { const dst = join(appDir, rel); mkdirSync(dirname(dst), { recursive: true }); rmSync(dst, { force: true }); symlinkSync(src, dst); };
const emb = catalog.find((m) => m.kind === "embedding" && m.required);
link("<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf", emb.filename);
for (const id of ["corpus-standard", "corpus-full"]) link(join(ROOT, "assets/corpus", `${id}.json`), catalog.find((m) => m.id === id).filename);
for (const m of ["src/rag/cryptoPack.ts", "src/rag/preparedness.ts"]) if (existsSync(join(ROOT, m))) await import(join(ROOT, m));
for (const p of PACKS) { const id = p.split("/").pop()!.replace(/\.sqlite$/, ""); link(p, catalog.find((m) => m.id === id)?.filename ?? `corpus/${id}.sqlite`); }
const { embeddingEngine } = await import(join(ROOT, "src/rag/embed.ts"));
await embeddingEngine.load(emb.filename);
const { seedKnowledgeBaseIfEmpty } = await import(join(ROOT, "src/rag/seedCorpus.ts"));
await seedKnowledgeBaseIfEmpty();
const Rt: any = await import(join(ROOT, "src/rag/retrieve.ts"));
const { compressContext }: any = await import(join(ROOT, "src/rag/compress.ts"));

// record embeddings
const embeds: Record<string, number[]> = {};
const origEmbed = embeddingEngine.embed.bind(embeddingEngine);
embeddingEngine.embed = async (t: string) => { const v = await origEmbed(t); embeds[t] = Array.from(v); return v; };

const items = readFileSync(TRACES, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const work0 = items.flatMap((it: any) => it.events.filter((e: any) => e.type === "retrieve").map((e: any) => ({ id: it.itemId, q: e.query, k: e.k })));
const REC: any = (globalThis as any).__REC;
// item 0 = a warm-up ask (opens the packs: WikiPack.open, meta, fts5vocab), as on a phone that already answered once.
// Pack caches (16-block / 16-article LRUs) carry over between questions in device order, as in the app.
const work = [{ id: "_warmup", q: "What should I see in Lisbon?", k: 4 }, ...work0];
const out: any[] = [];
for (const w of work) {
  REC.calls = []; REC.sqlMs = 0; REC.on = true;
  const t0 = performance.now();
  const raw = await Rt.retrieve(w.q, w.k);
  const ms = performance.now() - t0;
  REC.on = false;
  const comp = compressContext(w.q, raw, { tokenBudget: 320 });
  out.push({ ...w, ms, sqlMs: REC.sqlMs, calls: REC.calls, nRaw: raw.length, rawIds: raw.map((c: any) => c.chunkId), compIds: comp.chunks.map((c: any) => c.chunkId), tokens: [comp.tokensBefore, comp.tokensAfter] });
}
// blobs -> base64 (node:sqlite returns Uint8Array)
const enc = (x: any): any => x instanceof Uint8Array ? { $b64: Buffer.from(x).toString("base64") } : Array.isArray(x) ? x.map(enc) : x && typeof x === "object" ? Object.fromEntries(Object.entries(x).map(([k, v]) => [k, enc(v)])) : x;
// content-addressed result store
const store: Record<string, any> = {};
for (const o of out) o.calls = o.calls.map((c: any) => { const r = JSON.stringify(enc(c.r)); const h = createHash("sha1").update(r).digest("hex").slice(0, 16); store[h] ??= JSON.parse(r); return { db: c.db, m: c.m, sql: c.sql, p: enc(c.p), h }; });
writeFileSync(join(HERE, "rec/rec.json"), JSON.stringify({ commit: "0cfd4a77", work: out, store, embeds }));
const ms = out.map((o) => o.ms).sort((a, b) => a - b);
console.log(`recorded ${out.length} retrievals; node retrieve p50 ${ms[ms.length >> 1].toFixed(0)} ms; store ${Object.keys(store).length} results; calls/q p50 ${out.map((o) => o.calls.length).sort((a, b) => a - b)[out.length >> 1]}`);
process.exit(0);
