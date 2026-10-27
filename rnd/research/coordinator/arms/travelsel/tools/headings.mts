// headings.mts <title>: heading path of every chunk of a Wikivoyage article (read-only)
import { DatabaseSync } from "node:sqlite";
import fz from "<workspace>/boar-app/node_modules/fzstd/lib/index.js";
const decompress = (fz as any).decompress;
const db = new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true });
const HEADING = /^(#{1,6})\s+(.*)$/gm;
for (const a of db.prepare("SELECT * FROM articles WHERE title = ?").all(process.argv[2]) as any[]) {
  const blk = db.prepare("SELECT zdata FROM blocks WHERE id=?").get(a.block_id) as any;
  const text = new TextDecoder().decode(decompress(new Uint8Array(blk.zdata)).subarray(a.off, a.off + a.len));
  const hs = [...text.matchAll(HEADING)].map((m) => ({ at: m.index!, lvl: m[1].length, t: m[2] }));
  for (const c of db.prepare("SELECT id,start,end FROM chunks WHERE article_id=? ORDER BY id").all(a.id) as any[]) {
    const path: string[] = []; for (const h of hs) { if (h.at >= c.start) break; path.length = h.lvl - 1; path[h.lvl - 1] = h.t; }
    console.log(c.id, c.start, c.end - c.start, path.slice(1).join(" > "), "|", text.slice(c.start, c.start + 60).replace(/\n/g, " "));
  }
}
