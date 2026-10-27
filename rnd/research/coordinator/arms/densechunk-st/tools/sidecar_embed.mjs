/**
 * DENSECHUNK-ST step 0: chunk_vecs sidecar for a format-2 pack (0 LLM / 0 judge calls).
 *   sidecar_embed.mjs <pack.sqlite> --out <v3proto/<id>.sqlite> [--name <cache name>] [--threads 8]
 * 1. --out is an APFS clone (cp -c) of the published pack (the published file is never opened for writing).
 * 2. Vectors: the int8 cache shared-data/packs/work/densechunk/<name>.{i8,scales.f32,ids.i32} when present (D0 caches:
 *    crypto, wikivoyage; must cover every chunk id in order), else embedded here with the DENSECHUNK D0 code
 *    (arms/packcond/tools/densechunk_embed.mjs): text `${title}\n${section}: ${chunk text}` (section empty -> `${title}\n${text}`),
 *    the builders' embedChunks (bge-small q8_0 ec38e8…, 1,200-char cut) + quantizeInt8(384). f32 cache resumable, deleted
 *    after quantisation; the int8 cache is kept.
 * 3. Writes chunk_vecs(chunk_id INTEGER PRIMARY KEY, scale REAL, vec BLOB) into --out (one transaction), then records
 *    meta key densechunk = "bge-small-int8-v1" (the engine does not read it; provenance only).
 * Usage (MacBook): TSX=$T/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; BOAR_EMBEDDING_GGUF=… BOAR_EMBED_GPU=metal $TSX sidecar_embed.mjs …
 */
import { DatabaseSync } from "node:sqlite";
import { zstdDecompressSync } from "node:zlib";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync, rmSync, statSync, renameSync } from "node:fs";
import { join, basename } from "node:path";

const BOAR = "<workspace>";
const T = join(BOAR, "wt/packcond"); // same embedding.mjs / quantizeInt8 / sectionAt as wt/packs (diffed 2026-10-13)
const CACHE = join(BOAR, "shared-data/packs/work/densechunk");
mkdirSync(CACHE, { recursive: true });
const argv = process.argv.slice(2);
const get = (k, d) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : d);
const src = argv[0];
const out = get("--out");
const name = get("--name", basename(src).replace(/\.sqlite$/, ""));
const threads = Number(get("--threads", "8"));
const log = (m) => console.error(`[sidecar ${name} ${new Date().toISOString().slice(11, 19)}] ${m}`);
if (!src || !out || !existsSync(src)) { console.error("usage: sidecar_embed.mjs <pack.sqlite> --out <file>"); process.exit(2); }

// 1. clone
if (!existsSync(out)) {
  execFileSync("cp", ["-c", src, out + ".tmp"]);
  renameSync(out + ".tmp", out);
  log(`cloned ${src} -> ${out}`);
}
{
  const db = new DatabaseSync(out, { readOnly: true });
  const has = db.prepare("SELECT 1 FROM sqlite_master WHERE name='chunk_vecs'").get();
  const n = has ? db.prepare("SELECT count(*) AS n FROM chunk_vecs").get().n : 0;
  const nc = db.prepare("SELECT count(*) AS n FROM chunks").get().n;
  db.close();
  if (has && n === nc) { log(`chunk_vecs already complete (${n})`); process.exit(0); }
}

// 2. vectors
const ro = new DatabaseSync(src, { readOnly: true });
const rows = ro.prepare(`SELECT c.id AS cid, c.start AS s, c.end AS e, a.title AS title, a.block_id AS b, a.off AS off, a.len AS len
                         FROM chunks c JOIN articles a ON a.id = c.article_id ORDER BY c.id`).all();
log(`${rows.length} chunks`);
let data, scales;
const i8 = join(CACHE, `${name}.i8`);
const t0 = Date.now();
let embedded = 0;
if (existsSync(i8)) {
  const ids = new Int32Array(readFileSync(join(CACHE, `${name}.ids.i32`)).buffer.slice(0));
  if (ids.length !== rows.length || rows.some((r, i) => r.cid !== ids[i])) { log("FATAL cache ids != pack chunk ids"); process.exit(1); }
  data = new Int8Array(readFileSync(i8).buffer.slice(0));
  scales = new Float32Array(readFileSync(join(CACHE, `${name}.scales.f32`)).buffer.slice(0));
  log(`int8 cache reused (${data.length / 384} vectors)`);
} else {
  const { embedChunks, ensureEmbeddingModel } = await import(join(T, "scripts/lib/embedding.mjs"));
  const { quantizeInt8 } = await import(join(T, "scripts/lib/knowledge-pack-lib.mjs"));
  const { sectionAt } = await import(join(T, "src/rag/wikiPack.ts"));
  await ensureEmbeddingModel();
  const blockStmt = ro.prepare("SELECT zdata FROM blocks WHERE id = ?");
  let bId = -1, bBuf = null, aKey = "", aText = "";
  const chunkAt = (i) => {
    const r = rows[i];
    if (r.b !== bId) { bBuf = zstdDecompressSync(blockStmt.get(r.b).zdata); bId = r.b; }
    const key = `${r.b}:${r.off}`;
    if (key !== aKey) { aText = bBuf.subarray(r.off, r.off + r.len).toString("utf8"); aKey = key; }
    const sec = sectionAt(aText, r.s);
    const text = aText.slice(r.s, r.e);
    return { title: r.title, body: sec ? `${sec}: ${text}` : text };
  };
  const lazy = { length: rows.length, slice: (a, b) => { const o = []; for (let i = a; i < Math.min(b, rows.length); i++) o.push(chunkAt(i)); return o; } };
  const f32 = join(CACHE, `${name}.f32`);
  const have0 = existsSync(f32) ? Math.floor(statSync(f32).size / 1536) : 0;
  const vecs = await embedChunks(lazy, f32, threads);
  embedded = rows.length - have0;
  ({ data, scales } = quantizeInt8(vecs, 384));
  writeFileSync(i8, Buffer.from(data.buffer, data.byteOffset, data.byteLength));
  writeFileSync(join(CACHE, `${name}.scales.f32`), Buffer.from(scales.buffer));
  writeFileSync(join(CACHE, `${name}.ids.i32`), Buffer.from(Int32Array.from(rows.map((r) => r.cid)).buffer));
  rmSync(f32);
  log(`embedded ${embedded} in ${((Date.now() - t0) / 1000).toFixed(0)} s; int8 cache written, f32 deleted`);
}
ro.close();

// 3. sidecar table
const db = new DatabaseSync(out);
db.exec("DROP TABLE IF EXISTS chunk_vecs; CREATE TABLE chunk_vecs (chunk_id INTEGER PRIMARY KEY, scale REAL NOT NULL, vec BLOB NOT NULL)");
const ins = db.prepare("INSERT INTO chunk_vecs (chunk_id, scale, vec) VALUES (?, ?, ?)");
db.exec("BEGIN");
for (let i = 0; i < rows.length; i++) ins.run(rows[i].cid, scales[i], new Uint8Array(data.buffer, data.byteOffset + i * 384, 384));
db.exec("INSERT OR REPLACE INTO meta (key, value) VALUES ('densechunk', 'bge-small-int8-v1')");
db.exec("COMMIT");
db.close();
const stats = { pack: name, src, out, chunks: rows.length, embedded, seconds: +((Date.now() - t0) / 1000).toFixed(1),
  sidecar_bytes: rows.length * (384 + 4), src_bytes: statSync(src).size, out_bytes: statSync(out).size };
writeFileSync(join(CACHE, `${name}.sidecar.json`), JSON.stringify(stats));
log(`chunk_vecs written: ${JSON.stringify(stats)}`);
