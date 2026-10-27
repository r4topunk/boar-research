// dumpart.mts <title-substring>... : chunk boundaries and text of crypto-pack articles (read-only)
import { DatabaseSync } from "node:sqlite";
import fz from "<workspace>/boar-app/node_modules/fzstd/lib/index.js";
const decompress = (fz as any).decompress;
const db = new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true });
for (const t of process.argv.slice(2)) {
  for (const a of db.prepare("SELECT * FROM articles WHERE title = ?").all(t) as any[]) {
    const blk = db.prepare("SELECT zdata FROM blocks WHERE id=?").get(a.block_id) as any;
    const text = new TextDecoder().decode(decompress(new Uint8Array(blk.zdata)).subarray(a.off, a.off + a.len));
    console.log(`#### ${a.id} ${a.title} len=${text.length}`);
    for (const c of db.prepare("SELECT id,start,end FROM chunks WHERE article_id=? ORDER BY id").all(a.id) as any[]) console.log(`--- chunk ${c.id} [${c.start},${c.end}]\n${text.slice(c.start, c.end)}`);
  }
}
