// PARTIAL-DECOMP pack-build alternative (0 LLM): same article read sequence, packs repacked into smaller blocks (articles never split).
// usage: node repack.mjs <article-log.jsonl> <outdir>. Compressed size = node:zlib zstd level 12 (control: same tool at 64 KB).
import fs from "node:fs"; import zlib from "node:zlib"; import path from "node:path"; import { createRequire } from "node:module"; import { DatabaseSync } from "node:sqlite";
const require = createRequire(new URL("../zstd-bench/", import.meta.url)); const { decompress } = require("fzstd");
const [logFile, outDir] = process.argv.slice(2); const PACKDIR = "<workspace>/shared-data/packs/persona-a-union/";
const arts = fs.readFileSync(logFile, "utf8").trim().split("\n").map(l => JSON.parse(l)).filter(e => e.e === "art");
const packs = [...new Set(arts.map(a => a.pack))]; const SIZES = [16, 32, 64]; // KB targets
const zc = b => zlib.zstdCompressSync(b, { params: { [zlib.constants.ZSTD_c_compressionLevel]: 12 } }).length;
const layout = {}; // pack -> { N -> { blockOfArticle: Map(artId-> {nb, off, len}), blocks:[len], comp } }
for (const p of packs) {
  const db = new DatabaseSync(PACKDIR + `boar-${p.replace(/^local-boar-/, "")}.sqlite`, { readOnly: true });
  const rows = db.prepare("SELECT id, block_id, off, len FROM articles ORDER BY block_id, off").all();
  const zb = new Map(); for (const r of db.prepare("SELECT id, zdata FROM blocks").all()) zb.set(r.id, decompress(new Uint8Array(r.zdata)));
  const origComp = db.prepare("SELECT sum(length(zdata)) s FROM blocks").get().s;
  layout[p] = { origComp, orig: db.prepare("SELECT count(*) c FROM blocks").get().c, N: {} };
  for (const N of SIZES) {
    const lim = N * 1024; const byKey = new Map(); const blocks = []; let cur = null;
    for (const r of rows) {
      const a = zb.get(r.block_id).subarray(r.off, r.off + r.len);
      if (!cur || (cur.len > 0 && cur.len + a.length > lim)) { cur = { len: 0, parts: [] }; blocks.push(cur); }
      byKey.set(r.block_id + ":" + r.off, { nb: blocks.length - 1, end: cur.len + a.length }); cur.len += a.length; cur.parts.push(a);
    }
    let comp = 0; for (const b of blocks) comp += zc(Buffer.concat(b.parts));
    layout[p].N[N] = { byKey, lens: blocks.map(b => b.len), comp };
    console.error(p, N, "KB", blocks.length, "blocks", comp);
  }
}
function run(N, C) { // C = slots per pack at the 64 KB baseline; scaled by 64/N so cached bytes stay equal
  const slots = Math.round(C * 64 / N); const st = {}; let miss = 0, dec = 0;
  for (const a of arts) {
    const L = layout[a.pack].N[N]; const k = L.byKey.get(a.block + ":" + a.off); const c = (st[a.pack] ??= new Map());
    if (!c.has(k.nb)) { miss++; dec += L.lens[k.nb]; c.set(k.nb, 1); if (c.size > slots) c.delete(c.keys().next().value); }
  }
  return { slots_per_pack: slots, misses: miss, decoded_MB: dec / 1e6 };
}
const out = { sizes_KB: SIZES, per_pack: {}, total: {}, sim: {} };
for (const N of SIZES) {
  const comp = packs.reduce((s, p) => s + layout[p].N[N].comp, 0); out.total[N] = { compressed_bytes: comp, vs_64KB_control_pct: 0, blocks: packs.reduce((s, p) => s + layout[p].N[N].lens.length, 0) };
  for (const p of packs) (out.per_pack[p] ??= {})[N] = { blocks: layout[p].N[N].lens.length, compressed_bytes: layout[p].N[N].comp };
}
for (const N of SIZES) out.total[N].vs_64KB_control_pct = 100 * (out.total[N].compressed_bytes / out.total[64].compressed_bytes - 1);
out.total.shipped_zdata_bytes = packs.reduce((s, p) => s + layout[p].origComp, 0);
for (const C of [16, 64]) for (const N of SIZES) (out.sim[C] ??= {})[N] = run(N, C);
for (const C of [16, 64]) for (const N of SIZES) out.sim[C][N].decoded_vs_64KB_pct = 100 * (out.sim[C][N].decoded_MB / out.sim[C][64].decoded_MB - 1);
fs.writeFileSync(path.join(outDir, "repack-sim.json"), JSON.stringify(out, null, 1));
console.log(JSON.stringify({ total: out.total, sim: out.sim }, null, 1));
