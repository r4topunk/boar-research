// dumpsec.mts <title>: whole article text with chunk boundary markers (read-only)
import { DatabaseSync } from "node:sqlite";
import fz from "<workspace>/boar-app/node_modules/fzstd/lib/index.js";
const decompress = (fz as any).decompress;
const db = new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true });
for (const a of db.prepare("SELECT * FROM articles WHERE title = ?").all(process.argv[2]) as any[]) {
  const blk = db.prepare("SELECT zdata FROM blocks WHERE id=?").get(a.block_id) as any;
  const text = new TextDecoder().decode(decompress(new Uint8Array(blk.zdata)).subarray(a.off, a.off + a.len));
  console.log(`#### ${a.id} ${a.title} len=${text.length}`);
  const cs = db.prepare("SELECT id,start,end FROM chunks WHERE article_id=? ORDER BY id").all(a.id) as any[];
  let out = ""; let pos = 0;
  for (const c of cs) { out += text.slice(pos, c.start) + `\n<<<CHUNK ${c.id} [${c.start},${c.end}]>>>\n` ; pos = c.start; }
  console.log(cs.length, "chunks");
  for (const c of cs) console.log(`--- chunk ${c.id} [${c.start},${c.end}]\n${text.slice(c.start, c.end)}`);
}
