import fs from "node:fs";
import { decompress } from "<workspace>/boar-app/node_modules/fzstd/esm/index.mjs";
const S = process.env.S;
const load = (dir, kb) => { const buf = fs.readFileSync(`${dir}/blobs-${kb}.bin`); const blobs = []; for (let o = 0; o < buf.length; ) { const n = buf.readUInt32LE(o); blobs.push(new Uint8Array(buf.subarray(o + 4, o + 4 + n))); o += 4 + n; } return { blobs, q: JSON.parse(fs.readFileSync(`${dir}/blobs-${kb}.json`, "utf8")).q }; };
for (const kb of [64, 32, 16, 8]) {
  const wv = load(S, kb), cr = load(`${S}/cr`, kb); const per = [];
  for (let i = 0; i < wv.q.length; i++) { const t = performance.now(); for (const b of wv.q[i]) decompress(wv.blobs[b]); for (const b of cr.q[i] ?? []) decompress(cr.blobs[b]); per.push(performance.now() - t); }
  per.sort((a, b) => a - b); console.log(`${process.execArgv.join(" ") || "jit"} ${String(kb).padStart(2)} KB: fzstd per question p50 ${per[per.length >> 1].toFixed(0)} ms, p90 ${per[Math.floor(per.length * 0.9)].toFixed(0)} ms`);
}
