// REPACK16 (0 LLM): rewrite a format-2 pack's zstd blocks at N KB with build-wiki-pack.mjs's exact rule
// (articles appended in id order, block closed once blockLen >= N*1024, zstd level 12), every other table untouched.
// usage: node repack.mjs <in.sqlite> <out.sqlite> <N KB> [zlevel=12]   -> prints one JSON line (blocks, bytes, sha, wall).
import fs from "node:fs"; import crypto from "node:crypto"; import { DatabaseSync } from "node:sqlite";
import { constants as zc, zstdCompressSync, zstdDecompressSync } from "node:zlib";
const [inp, out, nkb, lvl = "12"] = process.argv.slice(2); const LIM = Number(nkb) * 1024; const LEVEL = Number(lvl);
if (!inp || !out || !LIM) { console.error("usage: repack.mjs in out N"); process.exit(2); }
if (fs.existsSync(out)) { console.error("refusing to overwrite", out); process.exit(2); }
const t0 = Date.now();
const src = new DatabaseSync(inp, { readOnly: true });
src.exec(`VACUUM INTO '${out}.tmp'`); src.close();
const db = new DatabaseSync(out + ".tmp");
const arts = db.prepare("SELECT id, block_id, off, len FROM articles ORDER BY id").all();
const getB = db.prepare("SELECT zdata FROM blocks WHERE id = ?");
let cid = -1, cbuf = null; const text = id => { return cbuf; };
const blocks = []; let cur = []; let curLen = 0; let bid = 1; const upd = [];
const flush = () => { if (!curLen) return; blocks.push([bid++, zstdCompressSync(Buffer.concat(cur), { params: { [zc.ZSTD_c_compressionLevel]: LEVEL } })]); cur = []; curLen = 0; };
for (const a of arts) {
  if (a.block_id !== cid) { cid = a.block_id; cbuf = zstdDecompressSync(getB.get(cid).zdata); }
  const data = cbuf.subarray(a.off, a.off + a.len);
  upd.push([bid, curLen, a.id]); cur.push(data); curLen += data.length;
  if (curLen >= LIM) flush();
}
flush();
db.exec("BEGIN");
db.exec("DELETE FROM blocks");
const ins = db.prepare("INSERT INTO blocks VALUES (?, ?)"); for (const [i, z] of blocks) ins.run(i, z);
const up = db.prepare("UPDATE articles SET block_id = ?, off = ? WHERE id = ?"); for (const u of upd) up.run(...u);
// record the layout in meta.params (blockKb) so the file says what it is
const p = db.prepare("SELECT value FROM meta WHERE key = 'params'").get();
if (p) { const j = JSON.parse(p.value); j.blockKb = Number(nkb); db.prepare("UPDATE meta SET value = ? WHERE key = 'params'").run(JSON.stringify(j)); }
db.exec("COMMIT");
db.exec(`VACUUM INTO '${out}'`); db.close(); fs.unlinkSync(out + ".tmp");
const sha = crypto.createHash("sha256").update(fs.readFileSync(out)).digest("hex");
const zbytes = blocks.reduce((s, [, z]) => s + z.length, 0);
console.log(JSON.stringify({ in: inp, out, block_kb: Number(nkb), articles: arts.length, blocks: blocks.length, zdata_bytes: zbytes,
  file_bytes: fs.statSync(out).size, in_file_bytes: fs.statSync(inp).size, sha256: sha, wall_s: (Date.now() - t0) / 1000 }));
