#!/usr/bin/env node
// vbuterin/blog posts/*.md -> builder JSONL (one doc per English post). Keeps numbers, names, math and code verbatim;
// only removes link targets, image embeds, HTML tags, and the 4 "[key]: <> (...)" metadata lines (read for date/title).
// usage: node vitalik-convert.mjs <blog-repo-dir> <out-dir> <snapshot>
import { readFileSync, readdirSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { join } from "node:path";
import { createHash } from "node:crypto";
import { decodeEntities, hash32 } from "<runner>/kiln/packs/convert/lib/common.mjs";

const [repo, out, snapshot] = process.argv.slice(2);
const LICENSE = "WTFPL (blog text and author-made images, per the repository README)";
const TRANSLATION = /_(DE|IT|Polish|Portuguese|ES|FR|RU|ZH|KO|JA|TR|PT|PL|ID|AR|VI|UA)\.md$/i;
const files = readdirSync(join(repo, "posts")).filter((f) => f.endsWith(".md") && !TRANSLATION.test(f)).sort();
// site/ has the published path (date + slug) -> canonical URL
const urlOf = new Map();
const walk = (d) => { for (const e of readdirSync(d, { withFileTypes: true })) { const p = join(d, e.name); if (e.isDirectory()) walk(p); else if (/general\/\d{4}\/\d\d\/\d\d\/[^/]+\.html$/.test(p)) urlOf.set(e.name.replace(/\.html$/, ""), p.split("site/")[1]); } };
walk(join(repo, "site/general").replace(/general$/, "")); 
const docs = []; const skipped = [];
for (const f of files) {
  const slug = f.replace(/\.md$/, "");
  let raw = readFileSync(join(repo, "posts", f), "utf8");
  const meta = {};
  raw = raw.replace(/^\[(\w+)\]: <> \((.*)\)\s*$/gm, (_, k, v) => { meta[k] = v; return ""; });
  if (!meta.title || !meta.date) { skipped.push([f, "no title/date"]); continue; }
  let t = raw.replace(/\r/g, "");
  t = t.replace(/```[\w+-]*\n([\s\S]*?)```/g, (_, c) => c.replace(/^(#+\s)/gm, "​$1").replace(/^\|/gm, "¦").replace(/^/gm, "    ").replace(/\n+$/, "\n"));
  t = t.replace(/!\[([^\]]*)\]\([^)]*\)/g, (_, a) => (a.trim() ? `[image: ${a.trim()}]` : ""));
  t = t.replace(/<img\b[^>]*>/gi, "").replace(/<!--[\s\S]*?-->/g, "");
  t = t.replace(/\[([^\]]+)\]\((?:[^()]|\([^)]*\))*\)/g, "$1"); // links -> text
  t = t.replace(/^\[\d+\]: .*$/gm, ""); // reference-style link defs
  t = t.replace(/<\/?(?:center|div|span|small|sup|sub|br|p|em|strong|b|i|u|a|iframe|video|details|summary)\b[^>]*>/gi, " ");
  t = decodeEntities(t);
  t = t.replace(/^(\s*)\|(.*)\|\s*$/gm, (_, ws, row) => /^[\s:|-]+$/.test(row) ? "" : ws + row.split("|").map((c) => c.trim()).join("; ")); // table rows keep every cell
  t = t.replace(/^# +/gm, "## ").replace(/^(#{4,}) /gm, "### ");
  t = t.replace(/^(\s*)\|/gm, "$1¦").replace(/[ \t]+$/gm, "").replace(/\n{3,}/g, "\n\n").trim();
  if (t.length < 200) { skipped.push([f, `short ${t.length}`]); continue; }
  const date = meta.date.replace(/\//g, "-");
  const pub = urlOf.get(slug);
  const url = pub ? `https://vitalik.eth.limo/${pub}` : `https://github.com/vbuterin/blog/blob/main/posts/${f}`;
  docs.push({
    page_id: 14e9 + hash32(slug) % 1e8, title: meta.title, text: `Published: ${date}\n\n${t}`,
    source: "vitalikblog", url, license: LICENSE,
    attribution: `Vitalik Buterin, "${meta.title}" (${date}), ${url}; WTFPL; repo vbuterin/blog ${snapshot}`,
    aliases: [slug], views: 0, infoboxes: null,
  });
}
const ids = new Set(docs.map((d) => d.page_id)); if (ids.size !== docs.length) throw new Error("page_id collision");
mkdirSync(out, { recursive: true });
const jl = join(out, "vitalik-blog.jsonl");
writeFileSync(jl, docs.map((d) => JSON.stringify(d)).join("\n") + "\n");
writeFileSync(join(out, "manifest.json"), JSON.stringify(docs.map((d) => ({ source: d.source, title: d.title, url: d.url, license: d.license, chars: d.text.length })), null, 1));
const dates = docs.map((d) => d.text.slice(11, 21)).sort();
const info = { count: docs.length, skipped, snapshot, dateRange: [dates[0], dates.at(-1)], withSiteUrl: docs.filter((d) => d.url.includes("eth.limo")).length, chars: docs.reduce((s, d) => s + d.text.length, 0), jsonlSha256: createHash("sha256").update(readFileSync(jl)).digest("hex") };
writeFileSync(join(out, "convert-info.json"), JSON.stringify(info, null, 2));
console.log(JSON.stringify(info, null, 1));
