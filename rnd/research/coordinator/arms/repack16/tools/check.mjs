// REPACK16 tool check: layout of <orig> vs <repack64> identical; every article's text identical in <orig> vs each other file.
// usage: node check.mjs <orig.sqlite> <repack64.sqlite> [other repacks...]
import crypto from "node:crypto"; import { DatabaseSync } from "node:sqlite"; import { zstdDecompressSync } from "node:zlib";
const [orig, r64, ...rest] = process.argv.slice(2);
const lay = f => { const d = new DatabaseSync(f, { readOnly: true }); const r = d.prepare("SELECT id, block_id, off, len FROM articles ORDER BY id").all(); d.close(); return r; };
const A = lay(orig), B = lay(r64); let same = 0; for (let i = 0; i < A.length; i++) if (A[i].block_id === B[i].block_id && A[i].off === B[i].off && A[i].len === B[i].len) same++;
const texts = f => { const d = new DatabaseSync(f, { readOnly: true }); const g = d.prepare("SELECT zdata FROM blocks WHERE id = ?"); let cid = -1, buf; const h = [];
  for (const a of d.prepare("SELECT id, block_id, off, len FROM articles ORDER BY id").all()) { if (a.block_id !== cid) { cid = a.block_id; buf = zstdDecompressSync(g.get(cid).zdata); } h.push(crypto.createHash("sha1").update(buf.subarray(a.off, a.off + a.len)).digest("hex")); }
  d.close(); return h; };
const T0 = texts(orig); const res = { articles: A.length, layout64_identical: same, text_identical: {} };
for (const f of [r64, ...rest]) { const T = texts(f); let s = 0; for (let i = 0; i < T0.length; i++) if (T[i] === T0[i]) s++; res.text_identical[f.split("/").slice(-2).join("/")] = s; }
console.log(JSON.stringify(res));
