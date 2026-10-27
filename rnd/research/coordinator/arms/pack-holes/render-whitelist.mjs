// PROTOTYPE (not a rebuild): same cleaner as the builder but with a whitelist renderer for the templates that
// leave holes. Emits {p, base, wl} per page (base = builder output, wl = whitelist output) for holes-eval.py.
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

const MONTHS = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const CUR = { eur: "€", usd: "$", gbp: "£", jpy: "¥", cny: "¥", rub: "₽", inr: "₹", php: "₱", egp: "E£", krw: "₩", thb: "฿", aud: "A$", cad: "C$", nzd: "NZ$", chf: "CHF ", idr: "Rp ", sek: "SEK ", nok: "NOK ", dkk: "DKK ", huf: "HUF ", mxn: "MX$", brl: "R$", zar: "R ", try: "₺", czk: "CZK ", pln: "PLN " };
const UNITS = { km: "km", m: "m", mi: "mi", ft: "ft", kg: "kg", lb: "lb", km2: "km²", mi2: "sq mi", m2: "m²", ha: "ha", acre: "acres", kmh: "km/h", mph: "mph", mm: "mm", cm: "cm", metre: "m", meter: "m", mile: "mi", feet: "ft", c: "°C", f: "°F", celsius: "°C", fahrenheit: "°F", kmph: "km/h" };
const isNamed = (p) => /^\s*[A-Za-z0-9_ -]{1,20}=/.test(p);
const CONNECT = new Set(["to", "and", "or", "-", "–", "+", "&", "by", "×", "x"]);
function renderWL(name, parts, fields) {
  const pos = parts.slice(1).filter((p) => !isNamed(p)).map((p) => cleanInline(p.trim()));
  const first = pos[0] ?? "";
  if (name === "convert" || name === "cvt") {
    let i = 0, v = pos[0]; if (!v) return "";
    while (CONNECT.has(pos[i + 1]) && pos[i + 2]) { v += ` ${pos[i + 1]} ${pos[i + 2]}`; i += 2; }
    let u = pos[i + 1] ?? ""; u = { c: "°C", f: "°F", m2: "m²", km2: "km²", mi2: "sq mi" }[u.toLowerCase()] ?? u;
    return `${v} ${u}`.trim();
  }
  if (UNITS[name] !== undefined) {
    if (!first) return "";
    const unit = UNITS[name];
    return pos.length > 1 && CONNECT.has(pos[1]) && pos[2] ? `${first} ${pos[1]} ${pos[2]} ${unit}` : `${first} ${unit}`.replace(/ °/, " °").replace(/^(-?[\d.,]+) (°[CF])$/, "$1 $2");
  }
  if (CUR[name] !== undefined) return first ? `${CUR[name]}${first}` : "";
  if (name === "lang" || name === "langx") return pos[1] ?? "";
  if (/^lang-[a-z-]+$/.test(name)) return first;
  if (/^(transl|translit|tlit|zh|nihongo|korean|script)$/.test(name) && name !== "nihongo") return pos[pos.length - 1] ?? "";
  if (name === "nihongo") { const nonEmpty = [pos[1], pos[2]].filter(Boolean).join(", "); return nonEmpty ? `${first || pos[2] || ""} (${nonEmpty})` : first; }
  if (/^ipac?(-[a-z]+)?$/.test(name)) return /^ipac/.test(name) ? `/${pos.filter((x) => x && !/^(lang|en|us|uk)$/.test(x)).join("")}/` : (pos[pos.length - 1] ?? "");
  if (name === "ill" || name === "interlanguage link") return first;
  if (/^(iata|icao|faa lid|faa_lid|phone|tel|station|rint|aur)$/.test(name)) return first;
  if (name === "isbn") return first ? `ISBN ${first}` : "";
  if (/^(nowrap|nobr|small|big|it|chem2|nbsp)$/.test(name)) return name === "nbsp" ? " " : first;
  if (/^(birth date( and age)?|death date( and age)?|start date( and age)?|end date|birth-date)$/.test(name)) {
    const [y, mo, d] = pos.map((x) => Number(x)); if (!y) return first;
    return [d || "", MONTHS[mo] || "", y].filter((x) => x !== "").join(" ");
  }
  if (name === "val") return first + (fields.u ? " " + fields.u : "");
  if (name === "unesco") return "UNESCO World Heritage Site";
  return null; // not whitelisted -> dropped as in the builder
}
function renderTemplate(body) {
  const parts = splitTop(body);
  const name = parts[0].trim().toLowerCase();
  if (!LISTINGS.has(name)) {
    const fields = {};
    for (const p of parts.slice(1)) { const eq = p.indexOf("="); if (eq >= 0) fields[p.slice(0, eq).trim().toLowerCase()] = p.slice(eq + 1).trim(); }
    const r = WL ? renderWL(name, parts, fields) : null;
    return r ?? "";
  }
  const fields = {};
  for (const p of parts.slice(1)) { const eq = p.indexOf("="); if (eq >= 0) fields[p.slice(0, eq).trim().toLowerCase()] = p.slice(eq + 1).trim(); }
  const title = fields.name ?? "";
  if (!title || name === "marker") return "";
  const bits = LISTING_FIELDS.filter((f) => fields[f]).map((f) => cleanInline(fields[f])).filter(Boolean);
  return `- ${cleanInline(title)}: ${bits.join(". ")}`;
}
let WL = false;
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
function clean(wikitext) {
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
const tidy = (s) => s.replace(/\(\s*[;,]\s*/g, "(").replace(/\s*\(\s*\)/g, "").replace(/\(\s*[;,\s]*\)/g, "");
let seen = 0;
for await (const p of pages(dump)) {
  if (p.ns !== "0" || p.redirect) continue;
  if (p.id % M !== 0) continue;
  seen++; if (MAXP && seen > MAXP) break;
  WL = false; const base = clean(p.text);
  WL = true; const wl = tidy(clean(p.text));
  process.stdout.write(JSON.stringify({ p: p.title, base, wl }) + "\n");
}
console.error(`pages ${seen}`);
