// T-K6: Simple English Wikipedia pages-articles XML dump (.bz2) -> builder JSONL parts + manifest.json.
// usage: node simplewiki-convert.mjs <dump.xml.bz2> <outdir> <builder/scripts/lib dir> [snapshot=2026-10-01]
// Pass 1: ns-0 redirects (title -> target, "#section" dropped). Pass 2: ns-0 non-redirect pages -> rows.
// Body = the builder's own cleanWikivoyage (same as WIKIFULL stage B), infoboxes as stage B ({{Infobox ...}} params ->
// [{name,data}] -> the builder's infoboxText "Key facts:" line). Dropped: namespaces != 0, redirects, disambiguation
// pages (stage-B template regex + "(disambiguation)" titles), and bodies < 200 chars after dropping the trailing
// boilerplate sections (Related pages / Other websites / References / Notes / Sources / Further reading / Gallery /
// See also / External links); HTML entities (&nbsp; …) decoded. views = 0. Aliases = redirect titles to the page (cap 50).
import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { createWriteStream, mkdirSync, writeFileSync } from "node:fs";
const [dump, outdir, libdir, snapshot = "2026-10-01"] = process.argv.slice(2);
const { cleanWikivoyage, parseDumpPage } = await import(`${libdir}/wiki-pack-lib.mjs`);
mkdirSync(outdir, { recursive: true });
const LICENSE = "CC BY-SA 4.0 (Simple English Wikipedia)";
const DIS = /\{\{\s*(disambiguation|disambig|dab|hndis|geodis|surname|given name|set index article|sia)\b/i;
const BOILER = /^(related pages|other websites|references|notes|sources|further reading|gallery|see also|external links|footnotes|bibliography|other pages)$/i;

async function* pages(path) {
  const child = spawn("bzcat", [path], { stdio: ["ignore", "pipe", "inherit"] });
  child.stdout.setEncoding("utf8");
  let buf = "";
  for await (const piece of child.stdout) {
    buf += piece;
    let end;
    while ((end = buf.indexOf("</page>")) >= 0) {
      const start = buf.indexOf("<page>");
      yield parseDumpPage(buf.slice(start, end));
      buf = buf.slice(end + 7);
    }
  }
}
// stage-B infobox helpers (arms/wikifull/tools/stageB/wikifullb_convert.mjs, verbatim logic)
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
function infoboxes(wikitext) {
  const boxes = [];
  for (const t of topTemplates(wikitext)) {
    const parts = split(t); if (!/^\s*infobox/i.test(parts[0])) continue;
    const data = {};
    for (const p of parts.slice(1)) { const e = p.indexOf("="); if (e < 0) continue; const k = p.slice(0, e).trim(), v = flat(p.slice(e + 1));
      if (k && v && !/^(image|logo|caption|alt|image_size|signature|map|coordinates|module)/i.test(k)) data[k.replace(/_/g, " ")] = ents(v); }
    if (Object.keys(data).length) boxes.push({ name: parts[0].trim(), data });
  }
  return boxes;
}
/** Drops boilerplate sections (heading + body up to the next heading of the same or higher level). */
function dropBoiler(body) {
  const out = []; let skip = 0;
  for (const line of body.split("\n")) {
    const m = line.match(/^(#{2,6}) (.*)$/);
    if (m) {
      if (skip && m[1].length > skip) continue;
      skip = BOILER.test(m[2].trim()) ? m[1].length : 0;
      if (skip) continue;
    } else if (skip) continue;
    out.push(line);
  }
  return out.join("\n").replace(/\n{3,}/g, "\n\n").trim();
}
// Copies a string out of the dump buffer (V8 sliced strings would keep every buffer alive: OOM on the first run).
const own = (t) => Buffer.from(t, "utf8").toString("utf8");
// HTML entities left in wikitext after the XML decode (&nbsp; etc.); the builder's cleaner keeps them verbatim.
const ENT = { nbsp: " ", ndash: "–", mdash: "—", amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", minus: "−", times: "×", deg: "°", thinsp: " ", hellip: "…", shy: "" };
const ents = (t) => t.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (m, e) => e[0] === "#" ? String.fromCodePoint(parseInt(e[1] === "x" || e[1] === "X" ? e.slice(2) : e.slice(1), e[1] === "x" || e[1] === "X" ? 16 : 10)) : (ENT[e.toLowerCase()] ?? m));
const norm = (t) => own(t.replace(/_/g, " ").trim());
const st = { pages: 0, ns0: 0, redirects: 0, disambig: 0, short: 0, out: 0, withInfobox: 0, aliases: 0, parts: 0 };
const t0 = Date.now();
// pass 1
const redir = new Map(); // target title -> [from]
for await (const p of pages(dump)) {
  if (p.ns !== "0" || !p.redirect) continue;
  const to = norm(p.redirect.split("#")[0]);
  if (!to) continue;
  (redir.get(to) ?? redir.set(to, []).get(to)).push(own(p.title));
}
console.error(`pass1 ${((Date.now() - t0) / 1000).toFixed(0)} s, redirect targets ${redir.size}`);
// pass 2
const manifest = [];
let part = 0, partBytes = 0, out = createWriteStream(`${outdir}/simplewiki.000.jsonl`);
for await (const p of pages(dump)) {
  st.pages++;
  if (p.ns !== "0") continue;
  st.ns0++;
  if (p.redirect) { st.redirects++; continue; }
  if (DIS.test(p.text) || /\(disambiguation\)$/.test(p.title)) { st.disambig++; continue; }
  const body = ents(dropBoiler(cleanWikivoyage(p.text)));
  if (body.length < 200) { st.short++; continue; }
  const boxes = infoboxes(p.text);
  if (boxes.length) st.withInfobox++;
  const aliases = [...new Set((redir.get(p.title) ?? []).filter((a) => a !== p.title))].slice(0, 50);
  st.aliases += aliases.length;
  const url = `https://simple.wikipedia.org/wiki/${encodeURIComponent(p.title.replace(/ /g, "_"))}`;
  const rec = JSON.stringify({ page_id: p.id, title: p.title, text: `# ${p.title}\n\n${body}`, source: "simplewiki", url, license: LICENSE,
    aliases, views: 0, infoboxes: boxes.length ? JSON.stringify(boxes) : null }) + "\n";
  if (partBytes > 300e6) { out.end(); part++; partBytes = 0; out = createWriteStream(`${outdir}/simplewiki.${String(part).padStart(3, "0")}.jsonl`); }
  if (!out.write(rec)) await new Promise((r) => out.once("drain", r));
  partBytes += Buffer.byteLength(rec);
  manifest.push({ source: "simplewiki", title: own(p.title), url: own(url), license: LICENSE });
  st.out++;
}
await new Promise((r) => out.end(r));
st.parts = part + 1;
st.seconds = Math.round((Date.now() - t0) / 1000);
writeFileSync(`${outdir}/manifest.json`, JSON.stringify(manifest));
writeFileSync(`${outdir}/convert-info.json`, JSON.stringify({ format: "simplewiki-dump", dump: dump.split("/").pop(), snapshot, license: LICENSE, stats: st }, null, 1));
console.log(JSON.stringify(st));
