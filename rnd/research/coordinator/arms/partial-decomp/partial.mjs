// PARTIAL-DECOMP (0 LLM): how much of a pack block does a read need, and what would stopping early save?
// usage: node partial.mjs <article-log.jsonl> <outdir>   (log = BOAR_BLOCKLOG of a replay on the be-pd tree: "art" events = article() cache misses
// in read order with pack, block, off, len; "miss" = block-cache misses). Reuses fzstd 0.1.1 from ../zstd-bench/node_modules.
import fs from "node:fs"; import zlib from "node:zlib"; import path from "node:path";
import { createRequire } from "node:module"; import { DatabaseSync } from "node:sqlite";
const require = createRequire(new URL("../zstd-bench/", import.meta.url));
const { Decompress, decompress } = require("fzstd");
const [logFile, outDir] = process.argv.slice(2); fs.mkdirSync(outDir, { recursive: true });
const PACKDIR = "<workspace>/shared-data/packs/persona-a-union/";
const fileOf = id => `boar-${id.replace(/^local-boar-/, "")}.sqlite`;
const dbs = {}; const db = id => (dbs[id] ??= new DatabaseSync(PACKDIR + fileOf(id), { readOnly: true }));
const q = (a, p) => { const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; };
const quant = a => ({ n: a.length, p10: q(a, .1), p25: q(a, .25), p50: q(a, .5), p75: q(a, .75), p90: q(a, .9), mean: a.reduce((x, y) => x + y, 0) / a.length });

// ---- zstd frame walk: compressed end offset of each zstd block (header-aware, used to feed Decompress up to a block boundary)
function zblocks(z) {
  const fhd = z[4]; const fcsF = fhd >> 6, single = (fhd >> 5) & 1, dictF = fhd & 3;
  let p = 5 + (single ? 0 : 1) + [0, 1, 2, 4][dictF] + (fcsF === 0 ? (single ? 1 : 0) : [0, 2, 4, 8][fcsF]);
  const ends = [];
  for (;;) { const h = z[p] | (z[p + 1] << 8) | (z[p + 2] << 16); const last = h & 1, type = (h >> 1) & 3, size = h >> 3; p += 3 + (type === 1 ? 1 : size); ends.push(p); if (last) break; }
  return ends; // compressed offset after block k (checksum, if any, follows the last)
}
function outBounds(z) { const b = []; let t = 0; const d = new Decompress(c => { if (c.length) { t += c.length; b.push(t); } }); d.push(z, true); return b; } // decompressed cumulative after each zstd block

// ---- events
const ev = fs.readFileSync(logFile, "utf8").trim().split("\n").map(l => JSON.parse(l));
const arts = ev.filter(e => e.e === "art"); const searches = ev.filter(e => e.e === "search").length;
const meta = new Map(); // "pack:block" -> {len, bounds}
for (const a of arts) { const k = a.pack + ":" + a.block; if (!meta.has(k)) { const z = new Uint8Array(db(a.pack).prepare("SELECT zdata FROM blocks WHERE id=?").get(a.block).zdata); const b = outBounds(z); const ze = zblocks(z); if (ze.length !== b.length) throw new Error("zblock count mismatch " + k); meta.set(k, { len: b[b.length - 1], bounds: b, zbytes: z.length }); } }
const kOf = (m, end) => { const i = m.bounds.findIndex(x => x >= end); return i < 0 ? m.bounds.length - 1 : i; };

// ---- layout stats (whole packs)
const layout = {};
for (const id of new Set(arts.map(a => a.pack))) {
  const d = db(id); const nb = d.prepare("SELECT count(*) c FROM blocks").get().c, na = d.prepare("SELECT count(*) c FROM articles").get().c, nc = d.prepare("SELECT count(*) c FROM chunks").get().c;
  layout[id] = { blocks: nb, articles: na, chunks: nc, articles_per_block: na / nb, chunks_per_block: nc / nb, chunks_per_article: nc / na };
}
const allB = Object.values(layout).reduce((a, l) => a + l.blocks, 0), allA = Object.values(layout).reduce((a, l) => a + l.articles, 0), allC = Object.values(layout).reduce((a, l) => a + l.chunks, 0);
layout.ALL = { blocks: allB, articles: allA, chunks: allC, articles_per_block: allA / allB, chunks_per_block: allC / allB };
const zbCount = [...meta.values()].map(m => m.bounds.length); // zstd blocks per pack block, over the blocks the replay touched

// ---- cache simulation: engine Lru = FIFO by insertion (Map.get does not refresh), one per pack
function sim(C, mode) {
  const st = {}; let decoded = 0, miss = 0, upgrades = 0; const resid = [];
  const fin = r => resid.push(r);
  for (const a of arts) {
    const m = meta.get(a.pack + ":" + a.block); const end = a.off + a.len; const k = kOf(m, end);
    const c = (st[a.pack] ??= new Map()); const h = c.get(a.block);
    if (!h) {
      miss++;
      decoded += mode === "full" ? m.len : mode.startsWith("exact") ? end : m.bounds[k];
      c.set(a.block, { k, end, dec: end, first: end, len: m.len, zb: m.bounds[k] });
      if (c.size > C) { const o = c.keys().next().value; fin(c.get(o)); c.delete(o); }
    } else {
      if (end > h.end) h.end = end;
      if (mode === "restart" && k > h.k) { decoded += m.bounds[k]; h.k = k; h.zb = m.bounds[k]; upgrades++; }
      else if (mode === "exact_resume" && end > h.dec) { decoded += end - h.dec; h.dec = end; upgrades++; }
      else if (mode === "exact_restart" && end > h.dec) { decoded += end; h.dec = end; upgrades++; }
      else if (mode === "resume" && k > h.k) { decoded += m.bounds[k] - m.bounds[h.k]; h.k = k; h.zb = m.bounds[k]; upgrades++; }
    }
  }
  for (const c of Object.values(st)) for (const h of c.values()) fin(h);
  return { C, mode, misses: miss, upgrades, decoded_bytes: decoded, resid };
}
const out = { searches, article_reads: arts.length, distinct_blocks: meta.size, layout, zstd_blocks_per_pack_block: quant(zbCount), zstd_block_count_hist: Object.fromEntries([...new Set(zbCount)].sort((a, b) => a - b).map(n => [n, zbCount.filter(x => x === n).length])), sim: {}, fractions: {} };
for (const C of [16, 64]) {
  const base = sim(C, "full");
  const f = { misses: base.misses, decoded_MB_full: base.decoded_bytes / 1e6 };
  const modes = {};
  for (const mode of ["exact_resume", "exact_restart", "stream_stop_restart", "stream_stop_resume"]) {
    const r = sim(C, mode.startsWith("exact") ? mode : mode === "stream_stop_restart" ? "restart" : "resume");
    modes[mode] = { misses: r.misses, upgrades: r.upgrades, decoded_MB: r.decoded_bytes / 1e6, saved_vs_full_pct: 100 * (1 - r.decoded_bytes / base.decoded_bytes) };
  }
  // fraction distributions per decompression (residency = from miss to eviction/end): needed end / decompressed length
  const exactFirst = [], exactResid = [], zFirst = [], zResid = [];
  for (const h of base.resid) { exactFirst.push(h.first / h.len); exactResid.push(h.end / h.len); }
  // zstd-granular fractions need the block meta: recompute from stored end
  f.exact_end_over_len_first_read = quant(exactFirst); f.exact_end_over_len_residency_max = quant(exactResid);
  out.sim[C] = { baseline: f, modes };
}
// zstd-granular stop fraction (residency max) per decompression at C=16/64: separate pass so the fields above stay simple
for (const C of [16, 64]) {
  const bres = sim(C, "full").resid; const base_resid_end = bres.reduce((a, h) => a + h.end, 0), base_resid_len = bres.reduce((a, h) => a + h.len, 0);
  const st = {}; const fr = [], frFirst = []; const fin = h => { fr.push(h.zbEnd / h.len); frFirst.push(h.zbFirst / h.len); };
  for (const a of arts) {
    const m = meta.get(a.pack + ":" + a.block); const end = a.off + a.len; const k = kOf(m, end); const c = (st[a.pack] ??= new Map()); const h = c.get(a.block);
    if (!h) { c.set(a.block, { zbEnd: m.bounds[k], zbFirst: m.bounds[k], len: m.len }); if (c.size > C) { fin(c.get(c.keys().next().value)); c.delete(c.keys().next().value); } }
    else if (m.bounds[k] > h.zbEnd) h.zbEnd = m.bounds[k];
  }
  for (const c of Object.values(st)) for (const h of c.values()) fin(h);
  out.sim[C].baseline.zstd_stop_over_len_first_read = quant(frFirst); out.sim[C].baseline.zstd_stop_over_len_residency_max = quant(fr);
  out.sim[C].baseline.exact_residency_max_byte_weighted_saved_pct = 100 * (1 - base_resid_end / base_resid_len);
  out.sim[C].baseline.share_decompressions_stopping_before_last_zstd_block_residency = fr.filter(x => x < 0.999999).length / fr.length;
}
// per-article-read view (cache-independent): end/len of every article read
out.read_end_over_len = quant(arts.map(a => (a.off + a.len) / meta.get(a.pack + ":" + a.block).len));
out.article_len_bytes = quant(arts.map(a => a.len)); out.block_len_bytes = quant([...meta.values()].map(m => m.len));
fs.writeFileSync(path.join(outDir, "replay-sim.json"), JSON.stringify(out, null, 1));
console.log("sim written", out.article_reads, "reads", meta.size, "blocks; misses@16 base", out.sim[16].baseline.misses, "@64", out.sim[64].baseline.misses);
