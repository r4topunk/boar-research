/**
 * PACKCOND DENSECHUNK D0 — chunk-level bge-small vectors for a format-2 pack (0 LLM, 0 judge calls).
 * Embedding text rule (declared once): `${articles.title}\n${section}: ${chunk text}` (section = wikiPack.ts sectionAt(article
 * text, chunk.start); when empty, just `${title}\n${chunk text}`). Same as packHitToChunk's body under the plain article title
 * the lead vectors were built with (build-wiki-pack.mjs leadBatches), through the builders' own embedChunks (title + "\n" + body,
 * 1,200-char cut, halving until it fits 512 tokens) and quantizeInt8 (384 dims).
 *
 * Modes:
 *   --bench N        : embed the first N chunks (chunk-id order) into a throwaway cache, print chunks/s.
 *   --full           : embed every chunk of the pack (resumable: float32 cache appended in chunk-id order), then write
 *                      <out>/<name>.i8 (int8, chunks x 384), <name>.scales.f32, <name>.ids.i32 (chunk ids, cache order),
 *                      <name>.meta.tsv (chunk_id, article_id, section heading).
 *   --ids-file F     : (with --full) restrict to the chunk ids listed in F (one per line; sampled run). Not used when the
 *                      full set fits the compute cap.
 *   --query-jsonl F --query-out G : embed the engine search query (`query` field) of each line of F (blind file; never printed)
 *                      with the replay shim's call (model.createEmbeddingContext({contextSize: 512}).getEmbeddingFor(query),
 *                      no prefix) and write G = float32 rows + G.ids (item ids). Prints counts only.
 *
 * Usage (MacBook; GPU = Metal like the replay shim):
 *   T=<workspace>; TSX=$T/boar-eval/adapters/desktop-node/node_modules/.bin/tsx
 *   export BOAR_EMBEDDING_GGUF=$T/shared-models/bge-small-en-v1.5-q8_0.gguf BOAR_EMBED_GPU=metal
 *   $TSX tools/densechunk_embed.mjs --pack $T/shared-data/packs/boar-wikivoyage-en.sqlite --name wikivoyage --bench 2000
 *   $TSX tools/densechunk_embed.mjs --pack $T/shared-data/crypto/boar-crypto.sqlite --name crypto --full
 *   $TSX tools/densechunk_embed.mjs --pack $T/shared-data/packs/boar-wikivoyage-en.sqlite --name wikivoyage --full
 *   $TSX tools/densechunk_embed.mjs --query-jsonl $T/blind/bench-v02/runs-packcond/p4b-v02.jsonl --query-out <work>/q-v02.f32
 * Output dir: <workspace>/shared-data/packs/work/densechunk/ (not in git).
 */
import { DatabaseSync } from "node:sqlite";
import { zstdDecompressSync } from "node:zlib";
import { existsSync, mkdirSync, readFileSync, writeFileSync, rmSync, statSync } from "node:fs";
import { join } from "node:path";

const BOAR = "<workspace>";
const T = join(BOAR, "wt/packcond");
const OUT = join(BOAR, "shared-data/packs/work/densechunk");
mkdirSync(OUT, { recursive: true });
const { embedChunks, ensureEmbeddingModel, EMBEDDING_MODEL } = await import(join(T, "scripts/lib/embedding.mjs"));
const { quantizeInt8 } = await import(join(T, "scripts/lib/knowledge-pack-lib.mjs"));
const { sectionAt } = await import(join(T, "src/rag/wikiPack.ts"));

const argv = process.argv.slice(2);
const get = (k, d) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : d);
const threads = Number(get("--threads", "8"));
const log = (m) => console.error(`[densechunk ${new Date().toISOString().slice(11, 19)}] ${m}`);

if (get("--query-jsonl")) {
  // Engine query embedding: the replay shim's exact call (runner/app-shims/llama-rn.mjs).
  const lines = readFileSync(get("--query-jsonl"), "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
  const { getLlama } = await import(join(T, "node_modules/node-llama-cpp/dist/index.js"));
  const llama = await getLlama({ gpu: "auto" });
  const model = await llama.loadModel({ modelPath: EMBEDDING_MODEL.path });
  const ctx = await model.createEmbeddingContext({ contextSize: 512 });
  const ids = [], bufs = [];
  for (const r of lines) {
    if (typeof r.query !== "string" || !r.query) continue;
    const v = (await ctx.getEmbeddingFor(r.query)).vector;
    ids.push(r.id); bufs.push(Buffer.from(Float32Array.from(v).buffer));
  }
  writeFileSync(get("--query-out"), Buffer.concat(bufs));
  writeFileSync(get("--query-out") + ".ids", ids.join("\n") + "\n");
  log(`queries embedded: ${ids.length}/${lines.length}`);
  await ctx.dispose(); await model.dispose();
  process.exit(0);
}

const packPath = get("--pack");
const name = get("--name");
await ensureEmbeddingModel();
const db = new DatabaseSync(packPath, { readOnly: true });
let rows = db.prepare(`SELECT c.id AS cid, c.article_id AS aid, c.start AS s, c.end AS e, a.title AS title, a.block_id AS b, a.off AS off, a.len AS len
                       FROM chunks c JOIN articles a ON a.id = c.article_id ORDER BY c.id`).all();
if (get("--ids-file")) {
  const keep = new Set(readFileSync(get("--ids-file"), "utf8").split("\n").filter(Boolean).map(Number));
  rows = rows.filter((r) => keep.has(r.cid));
}
const bench = get("--bench") ? Number(get("--bench")) : 0;
if (bench) rows = rows.slice(0, bench);
log(`${name}: ${rows.length} chunks`);

// Lazy chunk list: embedChunks only calls .length and .slice(a, b) in order; bodies are built per slice.
const blockStmt = db.prepare("SELECT zdata FROM blocks WHERE id = ?");
let bId = -1, bBuf = null, aKey = "", aText = "";
const sections = new Array(rows.length);
function chunkAt(i) {
  const r = rows[i];
  if (r.b !== bId) { bBuf = zstdDecompressSync(blockStmt.get(r.b).zdata); bId = r.b; }
  const key = `${r.b}:${r.off}`;
  if (key !== aKey) { aText = bBuf.subarray(r.off, r.off + r.len).toString("utf8"); aKey = key; }
  const sec = sectionAt(aText, r.s);
  sections[i] = sec;
  const text = aText.slice(r.s, r.e);
  return { title: r.title, body: sec ? `${sec}: ${text}` : text };
}
const lazy = { length: rows.length, slice: (a, b) => { const o = []; for (let i = a; i < Math.min(b, rows.length); i++) o.push(chunkAt(i)); return o; } };

const cache = join(OUT, bench ? `${name}.bench${bench}.f32` : `${name}.f32`);
if (bench && existsSync(cache)) rmSync(cache);
const t0 = Date.now();
const have0 = existsSync(cache) ? Math.floor(statSync(cache).size / 1536) : 0;
const vecs = await embedChunks(lazy, cache, threads);
const secs = (Date.now() - t0) / 1000;
const rate = (rows.length - have0) / secs;
log(`embedded ${rows.length - have0} in ${secs.toFixed(1)} s = ${rate.toFixed(1)} chunks/s (threads ${threads}, gpu ${process.env.BOAR_EMBED_GPU || "cpu"})`);
if (bench) {
  console.log(JSON.stringify({ pack: name, bench: rows.length, seconds: +secs.toFixed(1), chunks_per_s: +rate.toFixed(1), threads, gpu: process.env.BOAR_EMBED_GPU || "cpu" }));
  rmSync(cache);
  process.exit(0);
}
// Sections for chunks that were cached by an earlier (interrupted) run.
for (let i = 0; i < rows.length; i++) if (sections[i] === undefined) chunkAt(i);
const { data, scales } = quantizeInt8(vecs, 384);
writeFileSync(join(OUT, `${name}.i8`), Buffer.from(data.buffer, data.byteOffset, data.byteLength));
writeFileSync(join(OUT, `${name}.scales.f32`), Buffer.from(scales.buffer));
writeFileSync(join(OUT, `${name}.ids.i32`), Buffer.from(Int32Array.from(rows.map((r) => r.cid)).buffer));
writeFileSync(join(OUT, `${name}.meta.tsv`), rows.map((r, i) => `${r.cid}\t${r.aid}\t${String(sections[i]).replace(/[\t\n]/g, " ")}`).join("\n") + "\n");
writeFileSync(join(OUT, `${name}.stats.json`), JSON.stringify({ pack: packPath, chunks: rows.length, new_embedded: rows.length - have0, seconds: +secs.toFixed(1), chunks_per_s: +rate.toFixed(1), threads, gpu: process.env.BOAR_EMBED_GPU || "cpu", int8_bytes: data.byteLength, scale_bytes: scales.byteLength }));
log(`wrote ${name}.i8 (${data.byteLength} B) + scales/ids/meta`);
