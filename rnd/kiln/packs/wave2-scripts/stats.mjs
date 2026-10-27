// usage: node stats.mjs pack.sqlite  -> JSON with counts/meta keys
import { DatabaseSync } from "node:sqlite";
const db = new DatabaseSync(process.argv[2], { readOnly: true });
const one = (q) => Object.values(db.prepare(q).get())[0];
const cols = db.prepare("PRAGMA table_info(article_meta)").all().map((c) => c.name);
const meta = Object.fromEntries(db.prepare("SELECT key, value FROM meta").all().map((r) => [r.key, r.value]));
const out = {
  articles: one("SELECT count(*) FROM articles"),
  chunks: one("SELECT count(*) FROM chunks"),
  fts_rows: one("SELECT count(*) FROM fts_docsize"),
  redirects: one("SELECT count(*) FROM redirects"),
  lead_vecs: one("SELECT count(*) FROM lead_vecs"),
  sources: db.prepare("SELECT source, count(*) n FROM articles GROUP BY source").all().map((r) => `${r.source}:${r.n}`).join(" "),
  meta_cols: cols.join(","),
  meta_rows: one("SELECT count(*) FROM article_meta"),
  attribution_rows: cols.includes("attribution") ? one("SELECT count(*) FROM article_meta WHERE attribution IS NOT NULL AND attribution != ''") : 0,
  views_gt0: one("SELECT count(*) FROM articles WHERE views > 0"),
  licenses: cols.length ? db.prepare("SELECT license, count(*) n FROM article_meta GROUP BY license").all().map((r) => `${r.license}=${r.n}`) : [],
  meta_keys: Object.keys(meta),
  meta_name: meta.name, meta_license: meta.license,
};
console.log(JSON.stringify(out, null, 1));
