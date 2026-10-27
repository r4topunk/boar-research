#!/usr/bin/env node
// Title-lookup tier shard: a copy of a format-2 pack without the body full-text index (Sonar exp-33, TIER-PLAN.md).
// Keeps blocks/chunks/articles/redirects/df/lead_vecs; drops the fts virtual table (and its shadow tables); meta.tier=named.
// usage: node slim-wiki-pack.mjs <in.sqlite> <out.sqlite>   (Node ≥ 22, node:sqlite)
import { DatabaseSync } from "node:sqlite";
import { copyFileSync, statSync } from "node:fs";
const [inp, out] = process.argv.slice(2);
if (!inp || !out) { console.error("usage: slim-wiki-pack.mjs <in> <out>"); process.exit(2); }
copyFileSync(inp, out);
const db = new DatabaseSync(out);
const count = (t) => db.prepare(`SELECT count(*) AS n FROM ${t}`).get().n;
const before = { articles: count("articles"), chunks: count("chunks"), redirects: count("redirects") };
db.exec("DROP TABLE IF EXISTS fts");
for (const t of ["fts_data", "fts_idx", "fts_docsize", "fts_config", "fts_content"]) db.exec(`DROP TABLE IF EXISTS ${t}`);
db.prepare("INSERT OR REPLACE INTO meta (key, value) VALUES ('tier', 'named')").run();
db.exec("VACUUM");
const after = { articles: count("articles"), chunks: count("chunks"), redirects: count("redirects") };
if (JSON.stringify(before) !== JSON.stringify(after)) { console.error("count mismatch", before, after); process.exit(1); }
console.log(JSON.stringify({ in: inp, out, inBytes: statSync(inp).size, outBytes: statSync(out).size, ...after }));
