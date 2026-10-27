// PARTIAL-DECOMP bench (MacBook, 0 LLM): full decode vs fzstd streaming stop at the needed offset, on the 200 real blocks of ../zstd-bench.
// usage: node bench.mjs <outdir>. Node v25, fzstd 0.1.1 (the version pinned in bench-app). Per (block, article) pair: needed end = off+len of a seeded-random article of that block.
import fs from "node:fs"; import path from "node:path"; import { createRequire } from "node:module"; import { DatabaseSync } from "node:sqlite";
const require = createRequire(new URL("../zstd-bench/", import.meta.url)); const { Decompress, decompress } = require("fzstd");
const outDir = process.argv[2]; const ZB = new URL("../zstd-bench/blocks/", import.meta.url).pathname;
const idx = JSON.parse(fs.readFileSync(ZB + "index.json")); const bin = fs.readFileSync(ZB + "blocks.bin");
const PACKDIR = "<workspace>/shared-data/packs/persona-a-union/"; const dbs = {};
let seed = 7; const rnd = () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 2 ** 32;
function zends(z) { const fhd = z[4]; const fcsF = fhd >> 6, single = (fhd >> 5) & 1; let p = 5 + (single ? 0 : 1) + [0, 1, 2, 4][fhd & 3] + (fcsF === 0 ? (single ? 1 : 0) : [0, 2, 4, 8][fcsF]); const e = []; for (;;) { const h = z[p] | (z[p + 1] << 8) | (z[p + 2] << 16); p += 3 + (((h >> 1) & 3) === 1 ? 1 : h >> 3); e.push(p); if (h & 1) break; } return e; }
function streamAll(z) { let t = 0; const d = new Decompress(c => { t += c.length; }); d.push(z, true); return t; }
function streamStop(z, ze, ob, end) { const k = ob.findIndex(x => x >= end); const kk = k < 0 ? ob.length - 1 : k; let t = 0; const d = new Decompress(c => { t += c.length; }); d.push(z.subarray(0, ze[kk]), kk === ob.length - 1); return t; }
let off = 0; const rows = [];
for (const b of idx) {
  const z = new Uint8Array(bin.subarray(off, off + b.n)); off += b.n;
  const db = (dbs[b.pack] ??= new DatabaseSync(PACKDIR + b.pack, { readOnly: true }));
  const arts = db.prepare("SELECT off, len FROM articles WHERE block_id=?").all(b.id);
  const ob = []; { let t = 0; new Decompress(c => { if (c.length) { t += c.length; ob.push(t); } }).push(z, true); }
  const ze = zends(z); if (ze.length !== ob.length) throw new Error("zblock mismatch");
  for (let i = 0; i < 3; i++) { const a = arts[Math.floor(rnd() * arts.length)]; rows.push({ pack: b.pack, id: b.id, z, ze, ob, len: ob[ob.length - 1], end: a.off + a.len, nz: ob.length }); }
}
const time = f => { const t = process.hrtime.bigint(); f(); return Number(process.hrtime.bigint() - t) / 1e6; };
const REPS = 7; for (const r of rows.slice(0, 20)) { decompress(r.z); streamAll(r.z); } // warm
const res = rows.map(r => {
  const F = [], A = [], S = [];
  for (let k = 0; k < REPS; k++) { F.push(time(() => decompress(r.z))); A.push(time(() => streamAll(r.z))); S.push(time(() => streamStop(r.z, r.ze, r.ob, r.end))); }
  const med = a => [...a].sort((x, y) => x - y)[a.length >> 1];
  const outBytes = streamStop(r.z, r.ze, r.ob, r.end);
  return { pack: r.pack, id: r.id, nz: r.nz, len: r.len, end_over_len: r.end / r.len, stop_over_len: outBytes / r.len, full_ms: med(F), stream_all_ms: med(A), stream_stop_ms: med(S) };
});
const med = a => [...a].sort((x, y) => x - y)[a.length >> 1]; const sum = (a, f) => a.reduce((x, y) => x + f(y), 0);
const summ = rs => ({ pairs: rs.length, median_full_ms: med(rs.map(r => r.full_ms)), median_stream_all_ms: med(rs.map(r => r.stream_all_ms)), median_stream_stop_ms: med(rs.map(r => r.stream_stop_ms)), median_end_over_len: med(rs.map(r => r.end_over_len)), median_stop_over_len: med(rs.map(r => r.stop_over_len)), total_stop_over_full_time: sum(rs, r => r.stream_stop_ms) / sum(rs, r => r.full_ms), total_stop_over_streamall_time: sum(rs, r => r.stream_stop_ms) / sum(rs, r => r.stream_all_ms), ms_per_decoded_MB_full: sum(rs, r => r.full_ms) / (sum(rs, r => r.len) / 1e6) });
const out = { node: process.version, fzstd: "0.1.1", reps: REPS, pairs: res.length, blocks: idx.length, all: summ(res), single_zstd_block: summ(res.filter(r => r.nz === 1)), multi_zstd_block: summ(res.filter(r => r.nz > 1)), rows: res };
fs.writeFileSync(path.join(outDir, "bench-stop.json"), JSON.stringify(out, null, 1));
console.log(JSON.stringify({ all: out.all, single: out.single_zstd_block, multi: out.multi_zstd_block }, null, 1));
