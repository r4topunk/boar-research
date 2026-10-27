import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import { decompress } from "<workspace>/boar-app/node_modules/fzstd/esm/index.mjs";
const db = new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true });
const rows = db.prepare("SELECT zdata FROM blocks WHERE id % 59 = 0 LIMIT 60").all().map((r) => new Uint8Array(r.zdata));
let out = 0; const t = performance.now(); for (const z of rows) out += decompress(z).length; const ms = performance.now() - t;
const t2 = performance.now(); for (const z of rows) zlib.zstdDecompressSync(Buffer.from(z)); const nat = performance.now() - t2;
console.log(`${process.execArgv.join(" ") || "jit"}: 60 blocks, ${(out / 1e6).toFixed(1)} MB out | fzstd ${ms.toFixed(0)} ms (${(out / 1e6 / (ms / 1000)).toFixed(1)} MB/s) | native zstd ${nat.toFixed(0)} ms`);
