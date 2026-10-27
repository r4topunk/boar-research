// D2Q: chunk texts + filled prompts for the target set (criterion 83b06185). usage: node extract.mjs <pack.sqlite> <targets.json> <out.jsonl>
import { DatabaseSync } from "node:sqlite";
import { zstdDecompressSync } from "node:zlib";
import { readFileSync, writeFileSync } from "node:fs";
const [packF, tf, out] = process.argv.slice(2);
const T = JSON.parse(readFileSync(tf, "utf8"));
const db = new DatabaseSync(packF, { readOnly: true });
const HEADING = /^(#{1,6})\s+(.*)$/gm;
function sectionAt(text, start) { // = wikiPack.ts sectionAt
  const path = [];
  for (const m of text.matchAll(HEADING)) {
    const at = m.index; if (at >= start) break;
    const level = m[1].length, lineEnd = at + m[0].length, titleAt = lineEnd - m[2].length;
    path.length = level - 1; path[level - 1] = (lineEnd > start ? text.slice(titleAt, start) : m[2]).trim();
  }
  return path.slice(1).filter(Boolean).join(" > ");
}
export const PROMPT = (x) => `Write 4 short questions a user might ask that this passage answers; one per line; use the passage's key terms.\n\nTitle: ${x.title}\nSection: ${x.section}\nPassage:\n${x.text}`;
const ch = db.prepare("SELECT article_id, start, end FROM chunks WHERE id=?"), ar = db.prepare("SELECT title, block_id, off, len FROM articles WHERE id=?"), bl = db.prepare("SELECT zdata FROM blocks WHERE id=?");
const blocks = new Map(), dec = new TextDecoder("utf-8"); const rows = [];
for (const [kind, ids] of [["own", T.own_chunks], ["random", T.random_chunks]]) for (const id of ids) {
  const c = ch.get(id), a = ar.get(c.article_id);
  if (!blocks.has(a.block_id)) blocks.set(a.block_id, zstdDecompressSync(bl.get(a.block_id).zdata));
  const text = dec.decode(blocks.get(a.block_id).subarray(a.off, a.off + a.len));
  const x = { chunk: id, kind, article_id: c.article_id, title: a.title, section: sectionAt(text, c.start), text: text.slice(c.start, c.end).trim() };
  x.prompt = PROMPT(x); rows.push(x);
}
writeFileSync(out, rows.map((r) => JSON.stringify(r)).join("\n") + "\n"); console.log(rows.length, "rows");
