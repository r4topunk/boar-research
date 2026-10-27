#!/usr/bin/env node
// PK-5 MERGED-PACK: merge several format-2 BOAR knowledge packs into one format-2 sqlite (0 LLM). Node >= 23.8.
//   node merge-packs.mjs <out.sqlite> <pack1.sqlite> [pack2.sqlite ...]
// Copies each pack's blocks / articles / chunks / redirects / article_meta / lead_vecs with id offsets (source codes,
// zstd blocks, offsets and int8 lead vectors unchanged), then re-indexes the contentless FTS5 table from the article
// text exactly as boar-app scripts/build-wiki-pack.mjs does (title, heading path "A > B", chunk text; UTF-16 offsets;
// only the chunk ids the source pack had indexed, read from its fts_docsize), runs 'optimize', and rebuilds df
// (terms with doc >= dfMin) from the merged index. meta: format 2, same embedding sha/dims, summed counts,
// indexedChunks = merged fts_docsize count, sources merged, mergedFrom = [{file, sha256, name}].
import { DatabaseSync } from "node:sqlite";
import { zstdDecompressSync } from "node:zlib";
import { createHash } from "node:crypto";
import { readFileSync, rmSync } from "node:fs";
import { basename } from "node:path";

const [out, ...packs] = process.argv.slice(2);
if (!out || !packs.length) { console.error("usage: merge-packs.mjs <out.sqlite> <pack.sqlite>..."); process.exit(2); }
const DF_MIN = 2000;

function sectionsAt(text, spans) { // verbatim from build-wiki-pack.mjs
  const heads = [...text.matchAll(/^(#{1,6})\s+(.*)$/gm)].map((m) => ({ at: m.index, level: m[1].length, name: m[2].trim() }));
  const res = []; let h = 0; const path = [];
  for (const [s] of spans) {
    while (h < heads.length && heads[h].at < s) { const { level, name } = heads[h++]; path.length = Math.max(0, level - 1); path[level - 1] = name; }
    res.push(path.slice(1).filter(Boolean).join(" > "));
  }
  return res;
}

rmSync(out, { force: true });
const db = new DatabaseSync(out);
db.exec(`PRAGMA journal_mode = OFF; PRAGMA synchronous = OFF; PRAGMA page_size = 8192; PRAGMA cache_size = -1000000;
  CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
  CREATE TABLE blocks (id INTEGER PRIMARY KEY, zdata BLOB NOT NULL);
  CREATE TABLE articles (id INTEGER PRIMARY KEY, source INTEGER NOT NULL, page_id INTEGER NOT NULL, title TEXT NOT NULL,
                         views INTEGER NOT NULL, block_id INTEGER NOT NULL, off INTEGER NOT NULL, len INTEGER NOT NULL);
  CREATE TABLE chunks (id INTEGER PRIMARY KEY, article_id INTEGER NOT NULL, start INTEGER NOT NULL, end INTEGER NOT NULL);
  CREATE VIRTUAL TABLE fts USING fts5(title, section, body, content='', detail=full, tokenize='porter unicode61 remove_diacritics 2');
  CREATE TABLE article_meta (article_id INTEGER PRIMARY KEY, url TEXT, license TEXT, attribution TEXT);
  CREATE TABLE redirects (title TEXT NOT NULL COLLATE NOCASE, article_id INTEGER NOT NULL, PRIMARY KEY (title, article_id)) WITHOUT ROWID;
  CREATE TABLE lead_vecs (article_id INTEGER PRIMARY KEY, scale REAL NOT NULL, vec BLOB NOT NULL);`);
const insFts = db.prepare("INSERT INTO fts (rowid, title, section, body) VALUES (?, ?, ?, ?)");
let aOff = 0, cOff = 0, bOff = 0;
const metas = [], from = [];
let nArticles = 0, nChunks = 0, nIndexed = 0;
const sources = {};
const dec = new TextDecoder();
for (const p of packs) {
  const sha = createHash("sha256").update(readFileSync(p)).digest("hex");
  db.exec(`ATTACH DATABASE '${p.replace(/'/g, "''")}' AS s`);
  const m = Object.fromEntries(db.prepare("SELECT key, value FROM s.meta").all().map((r) => [r.key, r.value]));
  if (m.format !== "boar-knowledge-pack" || m.formatVersion !== "2") throw new Error(`${p}: not format 2`);
  metas.push(m); from.push({ file: basename(p), sha256: sha, name: m.name });
  try { Object.assign(sources, JSON.parse(m.sources || "{}")); } catch {}
  const has = (t) => !!db.prepare("SELECT 1 FROM s.sqlite_master WHERE name = ?").get(t);
  db.exec("BEGIN");
  db.exec(`INSERT INTO blocks SELECT id + ${bOff}, zdata FROM s.blocks;
    INSERT INTO articles SELECT id + ${aOff}, source, page_id, title, views, block_id + ${bOff}, off, len FROM s.articles;
    INSERT INTO chunks SELECT id + ${cOff}, article_id + ${aOff}, start, end FROM s.chunks;
    INSERT INTO lead_vecs SELECT article_id + ${aOff}, scale, vec FROM s.lead_vecs;`);
  if (has("redirects")) db.exec(`INSERT OR IGNORE INTO redirects SELECT title, article_id + ${aOff} FROM s.redirects`);
  if (has("article_meta")) {
    const cols = db.prepare("SELECT name FROM pragma_table_info('article_meta', 's')").all().map((r) => r.name);
    db.exec(`INSERT INTO article_meta SELECT article_id + ${aOff}, url, license, ${cols.includes("attribution") ? "attribution" : "NULL"} FROM s.article_meta`);
  }
  // Re-index: per article, the indexed chunks (rowids present in the source fts_docsize).
  const indexed = new Set(db.prepare("SELECT id FROM s.fts_docsize").all().map((r) => r.id));
  const blockCache = new Map();
  const arts = db.prepare("SELECT id, title, block_id, off, len FROM s.articles ORDER BY id").all();
  const chunksOf = db.prepare("SELECT id, start, end FROM s.chunks WHERE article_id = ? ORDER BY id");
  const blk = db.prepare("SELECT zdata FROM s.blocks WHERE id = ?");
  let n = 0;
  for (const a of arts) {
    let buf = blockCache.get(a.block_id);
    if (!buf) { blockCache.clear(); buf = zstdDecompressSync(blk.get(a.block_id).zdata); blockCache.set(a.block_id, buf); }
    const text = dec.decode(buf.subarray(a.off, a.off + a.len));
    const ch = chunksOf.all(a.id);
    const secs = sectionsAt(text, ch.map((c) => [c.start, c.end]));
    ch.forEach((c, i) => { if (indexed.has(c.id)) { insFts.run(c.id + cOff, a.title, secs[i], text.slice(c.start, c.end)); n++; } });
  }
  db.exec("COMMIT");
  const cnt = (t) => db.prepare(`SELECT COUNT(*) AS n, COALESCE(MAX(id), 0) AS mx FROM s.${t}`).get();
  const A = cnt("articles"), C = cnt("chunks"), B = cnt("blocks");
  if (n !== indexed.size) throw new Error(`${p}: re-indexed ${n} != source indexed ${indexed.size}`);
  console.error(`${basename(p)}: articles ${A.n}, chunks ${C.n}, indexed ${n}, blocks ${B.n}`);
  nArticles += A.n; nChunks += C.n; nIndexed += n;
  aOff += A.mx; cOff += C.mx; bOff += B.mx;
  db.exec("DETACH DATABASE s");
}
db.exec("INSERT INTO fts (fts) VALUES ('optimize')");
db.exec(`CREATE INDEX articles_title ON articles (title COLLATE NOCASE); CREATE INDEX chunks_article ON chunks (article_id);
  CREATE VIRTUAL TABLE temp.fts_v USING fts5vocab(main, 'fts', 'row');
  CREATE TABLE df (term TEXT PRIMARY KEY, doc INTEGER NOT NULL) WITHOUT ROWID;
  INSERT INTO df SELECT term, doc FROM temp.fts_v WHERE doc >= ${DF_MIN};`);
const docsize = db.prepare("SELECT COUNT(*) AS n FROM fts_docsize").get().n;
if (docsize !== nIndexed) throw new Error(`fts_docsize ${docsize} != ${nIndexed}`);
const m0 = metas[0];
const meta = { format: "boar-knowledge-pack", formatVersion: "2", dims: m0.dims, embeddingModelSha256: m0.embeddingModelSha256,
  sources: JSON.stringify(sources), license: metas.map((m) => m.license).join(" | "), name: "BOAR A-union merged (" + from.map((f) => f.file.replace(/\.sqlite$/, "")).join(", ") + ")",
  articles: String(nArticles), chunks: String(nChunks), indexedChunks: String(docsize), dfMin: String(DF_MIN), params: m0.params,
  builtAt: new Date().toISOString(), mergedFrom: JSON.stringify(from) };
for (const m of metas) if (m.embeddingModelSha256 !== m0.embeddingModelSha256 || m.dims !== m0.dims) throw new Error("embedding mismatch");
const ins = db.prepare("INSERT INTO meta VALUES (?, ?)");
for (const [k, v] of Object.entries(meta)) ins.run(k, v);
db.exec("VACUUM");
db.close();
console.error(`merged: articles ${nArticles}, chunks ${nChunks}, indexed ${docsize} -> ${out}`);
