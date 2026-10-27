// Byte-identity, JS side: the app's fzstd 0.1.1 over every block of a pack, same output format as native_hashes.c.
import { DatabaseSync } from "node:sqlite";
import { createHash } from "node:crypto";
import { decompress } from "<workspace>/boar-app/node_modules/fzstd/esm/index.mjs";
const db = new DatabaseSync(process.argv[2], { readOnly: true });
const out = [];
for (const r of db.prepare("SELECT id, zdata FROM blocks ORDER BY id").iterate()) {
  const o = decompress(new Uint8Array(r.zdata));
  out.push(`${r.id} ${o.length} ${createHash("sha256").update(o).digest("hex")}`);
}
process.stdout.write(out.join("\n") + "\n");
