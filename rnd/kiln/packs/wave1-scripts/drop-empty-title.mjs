// usage: node drop-empty-title.mjs <workdir>: drops rows whose title is empty (deleted/blank questions) from the
// JSONL and manifest.json (originals kept as *.raw), writes dropped page_ids to drop-info.json.
import { readdirSync, readFileSync, renameSync, writeFileSync } from "node:fs";
const dir = process.argv[2];
const jf = readdirSync(dir).find((f) => f.endsWith(".jsonl"));
const lines = readFileSync(`${dir}/${jf}`, "utf8").split("\n").filter(Boolean);
const keep = [], dropped = [];
for (const l of lines) { const d = JSON.parse(l); (d.title && d.title.trim() ? keep : dropped).push(d.title && d.title.trim() ? l : { page_id: d.page_id, url: d.url }); }
const man = JSON.parse(readFileSync(`${dir}/manifest.json`, "utf8"));
const man2 = man.filter((m) => m.title && m.title.trim());
renameSync(`${dir}/${jf}`, `${dir}/${jf}.raw`); renameSync(`${dir}/manifest.json`, `${dir}/manifest.json.raw`);
writeFileSync(`${dir}/${jf}`, keep.join("\n") + "\n");
writeFileSync(`${dir}/manifest.json`, JSON.stringify(man2, null, 1));
writeFileSync(`${dir}/drop-info.json`, JSON.stringify({ rule: "empty title", dropped }, null, 1));
console.log(dir, "kept", keep.length, "dropped", dropped.length, "manifest", man.length, "->", man2.length);
