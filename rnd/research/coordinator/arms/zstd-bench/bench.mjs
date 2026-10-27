// usage: node bench.mjs <lib> ; prints JSON. One lib per process.
import fs from "node:fs"; import crypto from "node:crypto"; import zlib from "node:zlib";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const lib = process.argv[2];
const idx = JSON.parse(fs.readFileSync("blocks/index.json")); const bin = fs.readFileSync("blocks/blocks.bin");
let off = 0; const blocks = idx.map(b => { const s = new Uint8Array(bin.subarray(off, off + b.n)); off += b.n; return s; });
let dec;
if (lib === "fzstd") { const { decompress } = require("fzstd"); dec = z => decompress(z); }
else if (lib === "node-zlib-zstd") { dec = z => new Uint8Array(zlib.zstdDecompressSync(z)); }
else if (lib === "bokuweb-wasm") { const m = await import("@bokuweb/zstd-wasm"); await m.init(); dec = z => m.decompress(z); }
else if (lib === "oneidentity-wasm") { const m = require("@oneidentity/zstd-js/wasm/decompress/index.cjs.js"); const { ZstdSimple: S } = await m.ZstdInit(); dec = z => S.decompress(z); }
else if (lib === "oneidentity-asm") { const m = require("@oneidentity/zstd-js/asm/decompress/index.cjs.js"); const { ZstdSimple: S } = await m.ZstdInit(); dec = z => S.decompress(z); }
else if (lib === "zstddec") { const { ZSTDDecoder } = await import("zstddec"); const d = new ZSTDDecoder(); await d.init(); const refLen = JSON.parse(fs.readFileSync("aggregates/ref-lens.json")); let bi = 0; dec = z => d.decode(z, refLen[bi++ % refLen.length]); /* zstddec needs the exact output size (not in the pack format; the zstd frame header has it but zstddec does not read it) */ }
const td = new TextDecoder();
const sha = u => crypto.createHash("sha256").update(u).digest("hex");
const hashes = blocks.map(z => sha(dec(z)));
const REPS = 5, mode = {};
for (const m of ["decompress", "decompress+utf8"]) {
  const per = [];
  dec(blocks[0]); // warm
  for (let r = 0; r < REPS; r++) {
    const ms = [];
    for (const z of blocks) { const t = process.hrtime.bigint(); const u = dec(z); if (m !== "decompress") td.decode(u); ms.push(Number(process.hrtime.bigint() - t) / 1e6); }
    per.push(ms);
  }
  const pooled = per.flat().sort((a, b) => a - b); const q = p => pooled[Math.min(pooled.length - 1, Math.floor(p * pooled.length))];
  const repMed = per.map(a => [...a].sort((x, y) => x - y)[a.length >> 1]);
  mode[m] = { median_ms: q(0.5), p90_ms: q(0.9), mean_ms: pooled.reduce((a, b) => a + b, 0) / pooled.length, rep_medians_ms: repMed };
}
const ref = process.env.REFHASH ? JSON.parse(fs.readFileSync(process.env.REFHASH)) : null;
const out = { lib, node: process.version, n_blocks: blocks.length, reps: REPS, ...mode, hashes_sha: sha(hashes.join()), identical_vs_fzstd: ref ? hashes.every((h, i) => h === ref[i]) : null };
if (lib === "fzstd") fs.writeFileSync("aggregates/ref-lens.json", JSON.stringify(blocks.map(z => dec(z).length)));
if (lib === "fzstd") fs.writeFileSync("aggregates/ref-hashes.json", JSON.stringify(hashes));
fs.writeFileSync(`aggregates/bench-${lib}.json`, JSON.stringify(out, null, 1));
console.log(lib, JSON.stringify({ d: mode.decompress.median_ms, d90: mode.decompress.p90_ms, u: mode["decompress+utf8"].median_ms, u90: mode["decompress+utf8"].p90_ms, same: out.identical_vs_fzstd }));
