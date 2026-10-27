// H8-ST step 0: alternate lexical index on a COPY of a format-2 pack (0 LLM). The pack's fts(title, section, body) already
// carries the article title (every chunk) and the heading path (builder sectionsAt, path minus "# Title"); this adds what
// is missing: fts_h8(title, section, body, lead) where title/section/body are rebuilt exactly as the builder does
// (same indexed rowids = fts_docsize, title = articles.title, section = sectionsAt over the article's chunk spans,
// body = text.slice(start, end)) and lead = the article's first sentence (lead chunk as WikiPack.articlePassages picks it:
// the second chunk when the first starts with "Key facts:"; "#" heading lines dropped; first [.!?] after >= 20 chars, cap 300).
// Usage: node build_h8.mjs <src.sqlite> <dst.sqlite> [--peek N]
import { DatabaseSync } from "node:sqlite";
import { zstdDecompressSync } from "node:zlib";
import { copyFileSync, existsSync, statSync } from "node:fs";
const [src, dst] = process.argv.slice(2);
const peek = process.argv.includes("--peek") ? Number(process.argv[process.argv.indexOf("--peek") + 1]) : 0;
if (!peek) { if (existsSync(dst)) throw new Error(`${dst} exists`); copyFileSync(src, dst); }
const db = new DatabaseSync(peek ? src : dst, peek ? { readOnly: true } : {});
function sectionsAt(text, spans) { // verbatim logic of build-wiki-pack.mjs sectionsAt
  const heads = [...text.matchAll(/^(#{1,6})\s+(.*)$/gm)].map((m) => ({ at: m.index, level: m[1].length, name: m[2].trim() }));
  const out = []; let h = 0; const path = [];
  for (const [s] of spans) {
    while (h < heads.length && heads[h].at < s) { const { level, name } = heads[h++]; path.length = Math.max(0, level - 1); path[level - 1] = name; }
    out.push(path.slice(1).filter(Boolean).join(" > "));
  }
  return out;
}
function firstSentence(t) {
  const s = t.split("\n").filter((l) => !/^#{1,6}\s/.test(l)).join(" ").replace(/\s+/g, " ").trim();
  const m = /^(.{20,300}?[.!?])(?=\s|$)/s.exec(s);
  if (m) return m[1];
  const c = s.slice(0, 300); const i = c.lastIndexOf(" ");
  return s.length <= 300 ? s : c.slice(0, i > 100 ? i : 300);
}
const indexed = new Set(db.prepare("SELECT id FROM fts_docsize").all().map((r) => r.id));
const arts = db.prepare("SELECT id, title, block_id, off, len FROM articles ORDER BY id").all();
const chunksOf = db.prepare("SELECT id, start, end FROM chunks WHERE article_id = ? ORDER BY id");
const blk = db.prepare("SELECT zdata FROM blocks WHERE id = ?");
const dec = new TextDecoder();
let curB = -1, curData = null, n = 0, nl = 0, leadChars = 0;
if (!peek) {
  db.exec(`CREATE VIRTUAL TABLE fts_h8 USING fts5(title, section, body, lead, content='', detail=full, tokenize='porter unicode61 remove_diacritics 2'); BEGIN`);
}
const ins = peek ? null : db.prepare("INSERT INTO fts_h8 (rowid, title, section, body, lead) VALUES (?, ?, ?, ?, ?)");
let done = 0;
for (const a of arts) {
  if (a.block_id !== curB) { curB = a.block_id; curData = zstdDecompressSync(blk.get(curB).zdata); }
  const text = dec.decode(curData.subarray(a.off, a.off + a.len));
  const rows = chunksOf.all(a.id); if (!rows.length) continue;
  const secs = sectionsAt(text, rows.map((r) => [r.start, r.end]));
  const lead = text.startsWith("Key facts:", rows[0].start) && rows.length > 1 ? rows[1] : rows[0];
  const fs = firstSentence(text.slice(lead.start, lead.end)); nl++; leadChars += fs.length;
  if (peek && done < peek) { console.log(JSON.stringify({ title: a.title, sec: secs.slice(0, 4), lead: fs })); done++; if (done >= peek) break; continue; }
  rows.forEach((r, i) => { if (indexed.has(r.id)) { ins.run(r.id, a.title, secs[i], text.slice(r.start, r.end), fs); n++; } });
  if (n % 20000 < rows.length) { db.exec("COMMIT; BEGIN"); }
}
if (!peek) {
  db.exec("COMMIT");
  db.exec("INSERT INTO fts_h8 (fts_h8) VALUES ('optimize')");
  // fidelity: the first three per-column token counts must equal the original index's for every indexed row
  const a1 = db.prepare("SELECT id, sz FROM fts_docsize ORDER BY id").all(), a2 = db.prepare("SELECT id, sz FROM fts_h8_docsize ORDER BY id").all();
  let same = 0, diff = 0, ex = [];
  for (let i = 0; i < a1.length; i++) { const x = Buffer.from(a1[i].sz), y = Buffer.from(a2[i]?.sz ?? []); if (a2[i]?.id === a1[i].id && y.subarray(0, x.length).equals(x)) same++; else { diff++; if (ex.length < 3) ex.push(a1[i].id); } }
  db.close();
  console.log(JSON.stringify({ src, dst, indexedRows: n, origRows: indexed.size, articles: nl, leadAvgChars: +(leadChars / nl).toFixed(1), docsize3_same: same, docsize3_diff: diff, diffEx: ex, srcBytes: statSync(src).size, dstBytes: statSync(dst).size }));
}
