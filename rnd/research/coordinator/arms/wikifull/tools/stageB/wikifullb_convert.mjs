// WIKIFULL stage B: raw.jsonl {page_id,title,wikitext} -> builder JSONL {page_id,title,text,infoboxes,source:"enwiki"}.
// Body: the builder's own cleanWikivoyage (wikitext -> plain markdown-ish; non-listing templates, tables, refs dropped).
// Infoboxes: top-level {{Infobox ...}} params flattened to FineWiki's [{data:{k:v}}] shape (nested templates -> their
// positional args) so the builder's infoboxText adds its "Key facts:" line as for FineWiki rows.
// Drops disambiguation pages (FineWiki has none either way: they carry no facts) and bodies < 200 chars after cleaning.
import { createReadStream, writeFileSync, createWriteStream } from "node:fs";
import { createInterface } from "node:readline";
import { cleanWikivoyage } from "./lib/wiki-pack-lib.mjs";
const [inp, outp] = process.argv.slice(2);
let part = 0, partBytes = 0, out = createWriteStream(`${outp}.000.jsonl`);  // parts <= 300 MB (builder reads each JSONL whole)
const st = { in: 0, out: 0, disambig: 0, short: 0, withInfobox: 0 };
function topTemplates(s) {
  const res = []; let i = 0;
  while ((i = s.indexOf("{{", i)) >= 0) {
    let d = 1, j = i + 2;
    while (j < s.length && d) { if (s.startsWith("{{", j)) { d++; j += 2; } else if (s.startsWith("}}", j)) { d--; j += 2; } else j++; }
    res.push(s.slice(i + 2, j - 2)); i = j;
  }
  return res;
}
function split(s) { const p = []; let d = 0, c = ""; for (let i = 0; i < s.length;) { const t = s.slice(i, i + 2);
  if (t === "{{" || t === "[[") { d++; c += t; i += 2; } else if (t === "}}" || t === "]]") { d--; c += t; i += 2; } else if (s[i] === "|" && d === 0) { p.push(c); c = ""; i++; } else c += s[i++]; }
  p.push(c); return p; }
function flat(v) {
  v = v.replace(/<!--[\s\S]*?-->/g, "").replace(/<ref[^>]*?\/>|<ref[^>]*>[\s\S]*?<\/ref>/g, "");
  for (let k = 0; k < 4 && v.includes("{{"); k++)
    v = v.replace(/\{\{([^{}]*)\}\}/g, (_, b) => split(b).slice(1).filter((x) => !x.includes("=")).map((x) => x.trim()).filter(Boolean).join(" "));
  return v.replace(/\[\[[^\]|]*\|([^\]]*)\]\]/g, "$1").replace(/\[\[([^\]]*)\]\]/g, "$1").replace(/\[https?:\/\/\S+\s+([^\]]*)\]/g, "$1")
    .replace(/\[?https?:\/\/\S+\]?/g, "").replace(/'{2,}/g, "").replace(/<br\s*\/?>/gi, ", ").replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
}
const DIS = /\{\{\s*(disambiguation|disambig|dab|hndis|geodis|surname|given name|set index article|sia)\b/i;
// split on "\n" only (readline also splits on other line terminators found inside wikitext)
async function* lines(path) { let buf = ""; for await (const piece of createReadStream(path, "utf8")) { buf += piece; let i;
  while ((i = buf.indexOf("\n")) >= 0) { yield buf.slice(0, i); buf = buf.slice(i + 1); } } if (buf) yield buf; }
for await (const line of lines(inp)) {
  if (!line) continue; st.in++;
  const r = JSON.parse(line);
  if (DIS.test(r.wikitext) || /\(disambiguation\)$/.test(r.title)) { st.disambig++; continue; }
  const boxes = [];
  for (const t of topTemplates(r.wikitext)) {
    const parts = split(t); if (!/^\s*infobox/i.test(parts[0])) continue;
    const data = {};
    for (const p of parts.slice(1)) { const e = p.indexOf("="); if (e < 0) continue; const k = p.slice(0, e).trim(), v = flat(p.slice(e + 1));
      if (k && v && !/^(image|logo|caption|alt|image_size|signature|map|coordinates|module)/i.test(k)) data[k.replace(/_/g, " ")] = v; }
    if (Object.keys(data).length) boxes.push({ name: parts[0].trim(), data });
  }
  const body = cleanWikivoyage(r.wikitext);
  if (body.length < 200) { st.short++; continue; }
  if (boxes.length) st.withInfobox++;
  if (partBytes > 300e6) { out.end(); part++; partBytes = 0; out = createWriteStream(`${outp}.${String(part).padStart(3, "0")}.jsonl`); }
  const rec = JSON.stringify({ page_id: r.page_id, title: r.title, text: `# ${r.title}\n\n${body}`, infoboxes: boxes.length ? JSON.stringify(boxes) : null, source: "enwiki" }) + "\n";
  out.write(rec); partBytes += Buffer.byteLength(rec);
  st.out++;
}
st.parts = part + 1; await new Promise((r) => out.end(r)); console.log(JSON.stringify(st)); writeFileSync(outp + ".stats.json", JSON.stringify(st, null, 1));
