// Sonar P-7b: exact builder block rule (flush after an article once blockLen >= blockKb*1024; zstd level 12)
// on all real Wikivoyage articles, stored in SQLite at several page sizes; then fzstd cost on the engine's real reads.
import fs from "node:fs";
import zlib from "node:zlib";
import { DatabaseSync } from "node:sqlite";
const SRC = "<workspace>/shared-data/crypto/boar-crypto.sqlite";
const TMP = process.env.TMPDIR_SIM;
const src = new DatabaseSync(SRC, { readOnly: true });
const arts = src.prepare("SELECT id, block_id, off, len FROM articles ORDER BY id").all();
const blockCache = new Map(); const text = (a) => { let b = blockCache.get(a.block_id); if (!b) { blockCache.clear(); b = zlib.zstdDecompressSync(Buffer.from(src.prepare("SELECT zdata FROM blocks WHERE id = ?").get(a.block_id).zdata)); blockCache.set(a.block_id, b); } return b.subarray(a.off, a.off + a.len); };
const reads = JSON.parse(fs.readFileSync("reads-cr.json", "utf8"));
const out = {};
for (const kb of (process.env.KBS ?? "64,16,8").split(",").map(Number)) {
  const blockOf = new Map(); const blobs = []; let cur = [], len = 0;
  const flush = () => { if (!len) return; blobs.push(zlib.zstdCompressSync(Buffer.concat(cur), { params: { [zlib.constants.ZSTD_c_compressionLevel]: 12 } })); cur = []; len = 0; };
  for (const a of arts) { blockOf.set(a.id, blobs.length); const t = text(a); cur.push(t); len += t.length; if (len >= kb * 1024) flush(); }
  flush();
  const zsum = blobs.reduce((n, b) => n + b.length, 0);
  const sizes = {};
  for (const ps of [4096, 8192, 16384, 65536]) {
    const f = `${TMP}/sim-${kb}-${ps}.sqlite`; try { fs.unlinkSync(f); } catch {}
    const d = new DatabaseSync(f); d.exec(`PRAGMA page_size = ${ps}; PRAGMA journal_mode = OFF; CREATE TABLE blocks (id INTEGER PRIMARY KEY, zdata BLOB NOT NULL); BEGIN`);
    const ins = d.prepare("INSERT INTO blocks VALUES (?, ?)"); blobs.forEach((b, i) => ins.run(i, b)); d.exec("COMMIT"); d.close();
    sizes[ps] = fs.statSync(f).size; fs.unlinkSync(f);
  }
  // decompressed bytes per question on the engine's real reads (cold cache per question)
  const perQ = Object.values(reads).map((ids) => { const bs = new Set(ids.map((id) => blockOf.get(id))); let raw = 0; for (const b of bs) raw += zlib.zstdDecompressSync(blobs[b]).length; return { n: bs.size, raw }; });
  const med = (v) => v.sort((x, y) => x - y)[Math.floor(v.length / 2)];
  fs.writeFileSync(`${TMP}/blobs-${kb}.json`, JSON.stringify({ q: Object.values(reads).map((ids) => [...new Set(ids.map((id) => blockOf.get(id)))]) }));
  fs.writeFileSync(`${TMP}/blobs-${kb}.bin`, Buffer.concat(blobs.map((b) => { const h = Buffer.alloc(4); h.writeUInt32LE(b.length); return Buffer.concat([h, b]); })));
  out[kb] = { blocks: blobs.length, zMB: +(zsum / 1e6).toFixed(1), tableMB: Object.fromEntries(Object.entries(sizes).map(([k, v]) => [k, +(v / 1e6).toFixed(1)])), blocksPerQ: med(perQ.map((x) => x.n)), rawMBperQ: +(med(perQ.map((x) => x.raw)) / 1e6).toFixed(2) };
  console.log(kb, JSON.stringify(out[kb]));
}
fs.writeFileSync("sim7b-cr.json", JSON.stringify(out, null, 1));
