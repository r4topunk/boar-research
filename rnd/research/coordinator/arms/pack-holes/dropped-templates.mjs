// Re-runs the builder's wikitext cleaner (boar-app/scripts/lib/wiki-pack-lib.mjs cleanWikivoyage, same md5 as the mini's
// builder copy) with a sentinel in place of every dropped template, and emits one JSONL line per dropped template:
//   {t: template name, l: left context (same line, <=80 chars), r: right context (<=60), p: page title}
// usage: node dropped-templates.mjs <dump.xml.bz2> <libdir> <pageMod> [maxPages] > out.jsonl
// Functions below are verbatim copies of wiki-pack-lib.mjs:148-163 (renderTemplate/stripTemplates), 192-202 (cleanInline),
// 232-251 (cleanWikivoyage) except renderTemplate returns SENT(name) for non-listing templates and stripTemplates is
// also used on infobox-free text only (infobox templates are reported under their own name "infobox*").
import { spawn } from "node:child_process";
const [dump, libdir, mod = "1", maxPages = "0"] = process.argv.slice(2);
const { parseDumpPage } = await import(`${libdir}/wiki-pack-lib.mjs`);
const LISTINGS = new Set(["see", "do", "buy", "eat", "drink", "sleep", "listing", "go", "marker"]);
const LISTING_FIELDS = ["alt", "address", "directions", "hours", "price", "content"];
const S0 = "", S1 = "";
function splitTop(s, sep = "|") {
  const parts = []; let depth = 0, cur = "";
  for (let i = 0; i < s.length; ) {
    const two = s.slice(i, i + 2);
    if (two === "{{" || two === "[[") { depth++; cur += two; i += 2; }
    else if (two === "}}" || two === "]]") { depth--; cur += two; i += 2; }
    else if (s[i] === sep && depth === 0) { parts.push(cur); cur = ""; i++; }
    else cur += s[i++];
  }
  parts.push(cur); return parts;
}
function renderTemplate(body) {
  const parts = splitTop(body);
  const name = parts[0].trim().toLowerCase();
  if (!LISTINGS.has(name)) return `${S0}${name.replace(/[\n]/g, " ").slice(0, 40)}${S1}`;
  const fields = {};
  for (const p of parts.slice(1)) { const eq = p.indexOf("="); if (eq >= 0) fields[p.slice(0, eq).trim().toLowerCase()] = p.slice(eq + 1).trim(); }
  const title = fields.name ?? "";
  if (!title || name === "marker") return "";
  const bits = LISTING_FIELDS.filter((f) => fields[f]).map((f) => cleanInline(fields[f])).filter(Boolean);
  return `- ${cleanInline(title)}: ${bits.join(". ")}`;
}
function stripTemplates(text) {
  let out = "", i = 0; const n = text.length;
  while (i < n) {
    if (text.startsWith("{{", i)) {
      let depth = 1, j = i + 2;
      while (j < n && depth) { if (text.startsWith("{{", j)) { depth++; j += 2; } else if (text.startsWith("}}", j)) { depth--; j += 2; } else j++; }
      out += renderTemplate(text.slice(i + 2, j - 2)); i = j;
    } else { const next = text.indexOf("{{", i); const stop = next < 0 ? n : next; out += text.slice(i, stop); i = stop; }
  }
  return out;
}
function stripMediaLinks(s) {
  const open = /\[\[(?:File|Image|Category):/gi; let out = "", from = 0;
  for (let m = open.exec(s); m; m = open.exec(s)) {
    out += s.slice(from, m.index); let depth = 0, i = m.index;
    while (i < s.length) { if (s.startsWith("[[", i)) depth++; else if (s.startsWith("]]", i)) depth--; else { i++; continue; } i += 2; if (depth === 0) break; }
    from = i; open.lastIndex = from;
  }
  return out + s.slice(from);
}
function cleanInline(s) {
  if (s.includes("{{")) s = stripTemplates(s);
  if (s.includes("[[")) s = stripMediaLinks(s);
  return s.replace(/\[\[[^\]|]*\|([^\]]*)\]\]/g, "$1").replace(/\[\[([^\]]*)\]\]/g, "$1").replace(/\[https?:\/\/\S+\s+([^\]]*)\]/g, "$1")
    .replace(/\[?https?:\/\/\S+\]?/g, "").replace(/'{2,}/g, "").replace(/<[^>]+>/g, "").replace(/[ \t]+/g, " ").trim();
}
function cleanSent(wikitext) {
  let t = wikitext.replace(/<!--[\s\S]*?-->/g, "").replace(/<ref[^>]*?\/>|<ref[^>]*>[\s\S]*?<\/ref>/g, "")
    .replace(/<gallery[\s\S]*?<\/gallery>/g, "").replace(/^\{\|[\s\S]*?^\|\}/gm, "");
  t = stripTemplates(t);
  if (t.includes("[[")) t = stripMediaLinks(t);
  const lines = [];
  for (const raw of t.split("\n")) {
    const m = raw.match(/^(={2,6})\s*(.*?)\s*=+\s*$/);
    if (m) { lines.push("", `${"#".repeat(m[1].length)} ${cleanInline(m[2])}`, ""); continue; }
    lines.push(cleanInline(raw.replace(/^[*#]+\s*/, "- ").replace(/^[:;]+\s*/, "")));
  }
  return lines.join("\n").replace(/^- - /gm, "- ").replace(/\n{3,}/g, "\n\n").trim();
}
async function* pages(path) {
  const child = spawn("bzcat", [path], { stdio: ["ignore", "pipe", "inherit"] });
  child.stdout.setEncoding("utf8"); let buf = "";
  for await (const piece of child.stdout) {
    buf += piece; let end;
    while ((end = buf.indexOf("</page>")) >= 0) { const start = buf.indexOf("<page>"); yield parseDumpPage(buf.slice(start, end)); buf = buf.slice(end + 7); }
  }
}
const M = Number(mod), MAXP = Number(maxPages);
let n = 0, seen = 0;
const re = new RegExp(`${S0}([^${S1}]*)${S1}`, "g");
const rm = new RegExp(`[${S0}${S1}]`, "g");
for await (const p of pages(dump)) {
  if (p.ns !== "0" || p.redirect) continue;
  if (p.id % M !== 0) continue;
  seen++; if (MAXP && seen > MAXP) break;
  const s = cleanSent(p.text);
  for (const m of s.matchAll(re)) {
    const ls = s.lastIndexOf("\n", m.index) + 1;
    const le = s.indexOf("\n", m.index); const lineEnd = le < 0 ? s.length : le;
    const l = s.slice(Math.max(ls, m.index - 80), m.index).replace(rm, "");
    const r = s.slice(m.index + m[0].length, Math.min(lineEnd, m.index + m[0].length + 60)).replace(/[^]*/, "").replace(rm, "");
    process.stdout.write(JSON.stringify({ t: m[1], l, r, p: p.title }) + "\n");
    n++;
  }
}
console.error(`pages ${seen}, dropped templates ${n}`);
