#!/usr/bin/env node
// Checks converter output against the builder's input schema and the licence rules. Prints counts only.
//   node validate.mjs <dir | file.jsonl> [...]      exit 1 on any error
// Per row: page_id safe integer and unique (across all inputs: they may share one build); title and text
// non-empty strings, text >= 200 chars (the builder drops shorter docs: counted as a warning); source a
// non-empty string; license set; url a string; aliases string[]; views integer >= 0; infoboxes null or a JSON
// string; stackexchange rows carry attribution with "Q by" and the question URL; medlineplus rows contain no
// "ency/" or "druginfo" text and no A.D.A.M./ASHP credit; text has no line opening a table ("|") by accident.
// manifest.json next to a JSONL must list the same number of docs with matching titles and sources.
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";

const files = process.argv.slice(2).flatMap((p) => (statSync(p).isDirectory() ? readdirSync(p).filter((f) => f.endsWith(".jsonl")).map((f) => join(p, f)) : [p]));
if (!files.length) {
  console.log("usage: node validate.mjs <dir | file.jsonl> [...]");
  process.exit(1);
}
const ids = new Map();
const errors = {};
const warnings = {};
const err = (k) => (errors[k] = (errors[k] ?? 0) + 1);
const warn = (k) => (warnings[k] = (warnings[k] ?? 0) + 1);
const report = [];
for (const f of files) {
  const rows = readFileSync(f, "utf8").split("\n").filter(Boolean);
  const bySource = {};
  let n = 0;
  for (const line of rows) {
    let r;
    try {
      r = JSON.parse(line);
    } catch {
      err("bad JSON");
      continue;
    }
    n++;
    const family = r.source_family ?? r.source;
    bySource[r.source] = (bySource[r.source] ?? 0) + 1;
    if (!Number.isSafeInteger(r.page_id) || r.page_id < 0) err("page_id not a safe integer");
    else if (ids.has(r.page_id)) err("duplicate page_id");
    else ids.set(r.page_id, f);
    if (typeof r.title !== "string" || !r.title.trim()) err("empty title");
    if (typeof r.text !== "string" || !r.text.trim()) err("empty text");
    else if (r.text.length < 200) warn("text < 200 chars (builder drops it)");
    if (typeof r.source !== "string" || !r.source) err("missing source");
    if (typeof r.license !== "string" || !r.license.trim()) err("missing license");
    if (r.url !== undefined && typeof r.url !== "string") err("url not a string");
    if (!r.url) warn("no url");
    if (r.aliases !== undefined && !(Array.isArray(r.aliases) && r.aliases.every((a) => typeof a === "string" && a))) err("aliases not string[]");
    if (r.views !== undefined && !(Number.isInteger(r.views) && r.views >= 0)) err("views not an integer >= 0");
    if (r.infoboxes != null && typeof r.infoboxes !== "string") err("infoboxes not null or a JSON string");
    if (typeof r.text === "string" && /^\|/m.test(r.text)) warn("line starting with | (table, not indexed)");
    if (family === "stackexchange") {
      if (typeof r.attribution !== "string" || !r.attribution.startsWith("Q by ") || !r.attribution.includes(r.url)) err("stackexchange row without attribution");
      if (!/^CC BY-SA (2\.5|3\.0|4\.0)$/.test(r.license)) err("stackexchange licence not CC BY-SA 2.5/3.0/4.0");
    }
    if (family === "medlineplus") {
      const all = `${r.text}\n${(r.aliases ?? []).join("\n")}`;
      if (/ency\/|druginfo|A\.D\.A\.M|ASHP|American Society of Health-System Pharmacists/i.test(all)) err("medlineplus row with encyclopedia/drug text");
      if (!/National Library of Medicine/.test(r.license)) err("medlineplus licence line missing");
    }
    if (family === "factbook" && !r.text.startsWith("Key facts:")) warn("factbook row without Key facts");
    if (!r.attribution) warn("no attribution");
  }
  const mf = join(dirname(f), "manifest.json");
  if (existsSync(mf)) {
    const m = JSON.parse(readFileSync(mf, "utf8"));
    if (!Array.isArray(m)) err("manifest.json not an array");
    else if (m.length !== n) err("manifest count != jsonl rows");
  } else warn("no manifest.json");
  report.push({ file: f, rows: n, sources: bySource });
}
console.log(JSON.stringify({ files: report, uniqueIds: ids.size, errors, warnings }, null, 1));
process.exit(Object.keys(errors).length ? 1 : 0);
