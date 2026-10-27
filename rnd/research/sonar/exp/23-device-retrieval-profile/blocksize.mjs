import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import { decompress } from "<workspace>/boar-app/node_modules/fzstd/esm/index.mjs";
const db = new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true });
// real article texts, in pack order, from 120 consecutive blocks (≈ 7.5 MB raw)
const blocks = db.prepare("SELECT id, zdata FROM blocks WHERE id BETWEEN 1000 AND 1119").all();
const texts = []; for (const b of blocks) { const raw = zlib.zstdDecompressSync(Buffer.from(b.zdata)); for (const a of db.prepare("SELECT off, len FROM articles WHERE block_id = ? ORDER BY off").all(b.id)) texts.push(raw.subarray(a.off, a.off + a.len)); }
const rawTotal = texts.reduce((n, t) => n + t.length, 0);
function build(kb) { const out = []; let cur = [], size = 0; const idx = [];
  const flush = () => { if (!cur.length) return; const z = zlib.zstdCompressSync(Buffer.concat(cur), { params: { [zlib.constants.ZSTD_c_compressionLevel]: 12 } }); out.push(new Uint8Array(z)); cur = []; size = 0; };
  texts.forEach((t, i) => { if (size && size + t.length > kb * 1024) flush(); idx[i] = out.length; cur.push(t); size += t.length; }); flush(); return { out, idx }; }
const pick = Array.from({ length: 60 }, (_, i) => (i * 7919) % texts.length);
for (const kb of [64, 32, 16, 8]) {
  const { out, idx } = build(kb); const z = out.reduce((n, b) => n + b.length, 0);
  const need = [...new Set(pick.map((i) => idx[i]))]; let bytes = 0; const t = performance.now(); for (const bi of need) bytes += decompress(out[bi]).length; const ms = performance.now() - t;
  console.log(`${process.execArgv.join(" ") || "jit"} block ${String(kb).padStart(2)} KB: ratio ${(z / rawTotal).toFixed(3)} (size x${(z / rawTotal / 1).toFixed(3)}) | 60 article reads -> ${need.length} blocks, ${(bytes / 1e6).toFixed(2)} MB, fzstd ${ms.toFixed(0)} ms`);
}
