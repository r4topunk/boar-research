// exp-26 helper: rewrite chunks' FTS rows in a pack COPY (contentless FTS5 'delete' with the exact original values,
// then insert body + appended text). Original values rebuilt as the builder made them (title, heading path, span text).
import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
export function sectionsAt(text: string, spans: number[][]) {
  const heads = [...text.matchAll(/^(#{1,6})\s+(.*)$/gm)].map((m) => ({ at: m.index!, level: m[1].length, name: m[2].trim() }));
  const out: string[] = []; let h = 0; const path: string[] = [];
  for (const [s] of spans) { while (h < heads.length && heads[h].at < s) { const { level, name } = heads[h++]; path.length = Math.max(0, level - 1); path[level - 1] = name; } out.push(path.slice(1).filter(Boolean).join(" > ")); }
  return out;
}
export function original(db: DatabaseSync, chunkId: number) {
  const c = db.prepare("SELECT article_id, start, end FROM chunks WHERE id = ?").get(chunkId) as any;
  const a = db.prepare("SELECT title, block_id, off, len FROM articles WHERE id = ?").get(c.article_id) as any;
  const text = zlib.zstdDecompressSync((db.prepare("SELECT zdata FROM blocks WHERE id = ?").get(a.block_id) as any).zdata).subarray(a.off, a.off + a.len).toString("utf8");
  const rows = db.prepare("SELECT id, start, end FROM chunks WHERE article_id = ? ORDER BY id").all(c.article_id) as any[];
  const secs = sectionsAt(text, rows.map((r) => [r.start, r.end]));
  const i = rows.findIndex((r) => r.id === chunkId);
  return { articleId: c.article_id, title: a.title as string, section: secs[i], body: text.slice(c.start, c.end) };
}
export function rewrite(path: string, extra: Map<number, string>) {
  const db = new DatabaseSync(path);
  db.exec("BEGIN");
  const del = db.prepare("INSERT INTO fts (fts, rowid, title, section, body) VALUES ('delete', ?, ?, ?, ?)");
  const ins = db.prepare("INSERT INTO fts (rowid, title, section, body) VALUES (?, ?, ?, ?)");
  for (const [id, add] of extra) {
    if (!db.prepare("SELECT 1 FROM fts_docsize WHERE id = ?").get(id)) continue;
    const o = original(db, id);
    del.run(id, o.title, o.section, o.body);
    ins.run(id, o.title, o.section, add ? `${o.body}\n${add}` : o.body);
  }
  db.exec("COMMIT");
  db.close();
}
