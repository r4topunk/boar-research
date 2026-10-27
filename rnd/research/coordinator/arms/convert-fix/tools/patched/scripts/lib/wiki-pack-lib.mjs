// Pure helpers for scripts/build-wiki-pack.mjs (no I/O), unit-tested in wiki-pack-lib.test.mjs.
//
// leadOf, chunkArticle, isTable, infoboxText and cleanWikivoyage are ports of
// a competitor team's scripts/build_corpus.py and scripts/wikivoyage_to_parquet.py
// ([competitor link removed] Apache-2.0, Copyright the a competitor team
// authors). Changes: JavaScript, offsets are UTF-16 code units (what the app's
// String.slice uses), and chunk sections aren't returned (the app recovers them
// from the article text, see sectionAt in src/rag/wikiPack.ts).

const HEADING = /^(#{1,6})\s+(.*)$/;
const CUT = /\n|(?<=[.!?])\s+/g;

/** Text before the first level-2 heading, cut at a paragraph boundary when longer than `leadChars`. */
export function leadOf(text, leadChars = 2500) {
  const cut = text.indexOf("\n## ");
  let lead = cut < 0 ? text : text.slice(0, cut);
  if (lead.length > leadChars) {
    const end = lead.lastIndexOf("\n\n", leadChars);
    lead = lead.slice(0, end > 0 ? end : leadChars);
  }
  return lead;
}

/** Flattens FineWiki's structured infoboxes (JSON) into one "Key facts: ..." paragraph, or "". */
export function infoboxText(raw, maxChars = 800) {
  if (!raw) return "";
  let boxes;
  try {
    boxes = JSON.parse(raw);
  } catch {
    return "";
  }
  if (!Array.isArray(boxes)) return "";
  const facts = [];
  for (const box of boxes) {
    for (const [k, v] of Object.entries(box?.data ?? {})) {
      if (typeof v === "string" && k && v && v.length < 200) facts.push(`${k}: ${v}`);
    }
  }
  const text = facts.join("; ");
  return text ? `Key facts: ${text.slice(0, maxChars)}` : "";
}

/** Splits an oversized paragraph (usually a table or list) into [start, end) spans, preferring line or sentence ends. */
function splitLong(par, limit) {
  const spans = [];
  let s = 0;
  let last = 0;
  const cuts = [...par.matchAll(CUT)].map((m) => m.index + m[0].length);
  cuts.push(par.length);
  for (const c of cuts) {
    if (c - s > limit && last > s) {
      spans.push([s, last]);
      s = last;
    }
    while (c - s > limit * 1.5) {
      spans.push([s, s + limit]);
      s += limit;
    }
    last = c;
  }
  if (s < par.length) spans.push([s, par.length]);
  return spans;
}

/**
 * [start, end) spans over `text` packed from paragraphs up to `chunkChars`;
 * chunks never cross a heading, and the heading line itself isn't part of a chunk.
 */
export function chunkArticle(text, chunkChars = 1000, maxChunkChars = 1500) {
  const out = [];
  let pos = 0;
  let curStart = null;
  let curEnd = null;
  const flush = () => {
    if (curStart !== null && text.slice(curStart, curEnd).trim()) out.push([curStart, curEnd]);
    curStart = curEnd = null;
  };
  for (let par of text.split("\n\n")) {
    let start = pos;
    const end = pos + par.length;
    pos = end + 2;
    if (!par.trim()) continue;
    const firstLine = par.split("\n", 1)[0];
    if (HEADING.test(firstLine)) {
      flush();
      const bodyOff = firstLine.length + 1;
      if (par.length <= bodyOff) continue;
      start += bodyOff;
      par = par.slice(bodyOff);
    }
    if (par.length > maxChunkChars) {
      flush();
      for (const [s, e] of splitLong(par, chunkChars)) out.push([start + s, start + e]);
      continue;
    }
    if (curStart !== null && end - curStart > chunkChars) flush();
    if (curStart === null) curStart = start;
    curEnd = end;
  }
  flush();
  return out;
}

/** A chunk that is mostly markdown table rows: kept in the text, left out of the keyword index. */
export function isTable(chunk) {
  const lines = chunk.split("\n");
  return lines.filter((l) => l.startsWith("|")).length * 2 > lines.length;
}

/** The first chunk that isn't only infobox facts: the article's prose lead. */
export function leadChunkIndex(text, spans) {
  if (spans.length > 1 && text.slice(spans[0][0], spans[0][1]).startsWith("Key facts:")) return 1;
  return 0;
}

// ---- Wikivoyage wikitext ----

const LISTINGS = new Set(["see", "do", "buy", "eat", "drink", "sleep", "listing", "go", "marker"]);
const LISTING_FIELDS = ["alt", "address", "directions", "hours", "price", "content"];

function splitTop(s, sep = "|") {
  const parts = [];
  let depth = 0;
  let cur = "";
  for (let i = 0; i < s.length; ) {
    const two = s.slice(i, i + 2);
    if (two === "{{" || two === "[[") {
      depth++;
      cur += two;
      i += 2;
    } else if (two === "}}" || two === "]]") {
      depth--;
      cur += two;
      i += 2;
    } else if (s[i] === sep && depth === 0) {
      parts.push(cur);
      cur = "";
      i++;
    } else {
      cur += s[i++];
    }
  }
  parts.push(cur);
  return parts;
}

// CONVERT-FIX (arms/convert-fix): {{convert|N|unit|...}} renders as "N unit" (first value + first unit, ranges kept) instead of "".
const CV_UNIT = { c: "°C", f: "°F", m2: "m²", km2: "km²", m3: "m³", sqft: "sq ft", sqmi: "sq mi", mi2: "sq mi", sqkm: "km²", acre: "acres" };
const CV_CONNECT = new Set(["to", "and", "or", "-", "–", "+", "&", "by", "×", "x", "to(-)", "and(-)"]);
function renderConvert(parts) {
  const pos = parts.slice(1).filter((p) => !/^\s*[A-Za-z][A-Za-z0-9_ -]{0,19}=/.test(p)).map((p) => cleanInline(p.trim()));
  if (!pos[0]) return "";
  let v = pos[0];
  let i = 0;
  while (CV_CONNECT.has(pos[i + 1]) && pos[i + 2]) {
    v += ` ${pos[i + 1]} ${pos[i + 2]}`;
    i += 2;
  }
  const u = pos[i + 1] ?? "";
  return `${v} ${CV_UNIT[u.toLowerCase()] ?? u}`.trim();
}

function renderTemplate(body) {
  const parts = splitTop(body);
  const name = parts[0].trim().toLowerCase();
  if (name === "convert" || name === "cvt") return renderConvert(parts);
  if (!LISTINGS.has(name)) return "";
  const fields = {};
  for (const p of parts.slice(1)) {
    const eq = p.indexOf("=");
    if (eq >= 0) fields[p.slice(0, eq).trim().toLowerCase()] = p.slice(eq + 1).trim();
  }
  const title = fields.name ?? "";
  if (!title || name === "marker") return "";
  const bits = LISTING_FIELDS.filter((f) => fields[f]).map((f) => cleanInline(fields[f])).filter(Boolean);
  return `- ${cleanInline(title)}: ${bits.join(". ")}`;
}

function stripTemplates(text) {
  let out = "";
  let i = 0;
  const n = text.length;
  while (i < n) {
    if (text.startsWith("{{", i)) {
      let depth = 1;
      let j = i + 2;
      while (j < n && depth) {
        if (text.startsWith("{{", j)) {
          depth++;
          j += 2;
        } else if (text.startsWith("}}", j)) {
          depth--;
          j += 2;
        } else j++;
      }
      out += renderTemplate(text.slice(i + 2, j - 2));
      i = j;
    } else {
      const next = text.indexOf("{{", i);
      const stop = next < 0 ? n : next;
      out += text.slice(i, stop);
      i = stop;
    }
  }
  return out;
}

/** Drops [[File:…]], [[Image:…]] and [[Category:…]] links, including captions that hold nested [[links]]. */
function stripMediaLinks(s) {
  const open = /\[\[(?:File|Image|Category):/gi;
  let out = "";
  let from = 0;
  for (let m = open.exec(s); m; m = open.exec(s)) {
    out += s.slice(from, m.index);
    let depth = 0;
    let i = m.index;
    while (i < s.length) {
      if (s.startsWith("[[", i)) depth++;
      else if (s.startsWith("]]", i)) depth--;
      else {
        i++;
        continue;
      }
      i += 2;
      if (depth === 0) break;
    }
    from = i;
    open.lastIndex = from;
  }
  return out + s.slice(from);
}

function cleanInline(s) {
  if (s.includes("{{")) s = stripTemplates(s);
  if (s.includes("[[")) s = stripMediaLinks(s);
  return s
    .replace(/\[\[[^\]|]*\|([^\]]*)\]\]/g, "$1")
    .replace(/\[\[([^\]]*)\]\]/g, "$1")
    .replace(/\[https?:\/\/\S+\s+([^\]]*)\]/g, "$1")
    .replace(/\[?https?:\/\/\S+\]?/g, "")
    .replace(/'{2,}/g, "")
    .replace(/<[^>]+>/g, "")
    .replace(/[ \t]+/g, " ")
    .trim();
}

/** Wikivoyage page wikitext → markdown-ish text: listings kept as list items, other templates, tables and refs dropped. */
export function cleanWikivoyage(wikitext) {
  let t = wikitext
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/<ref[^>]*?\/>|<ref[^>]*>[\s\S]*?<\/ref>/g, "")
    .replace(/<gallery[\s\S]*?<\/gallery>/g, "")
    .replace(/^\{\|[\s\S]*?^\|\}/gm, "");
  t = stripTemplates(t);
  // Before splitting into lines: an image caption can span several.
  if (t.includes("[[")) t = stripMediaLinks(t);
  const lines = [];
  for (const raw of t.split("\n")) {
    const m = raw.match(/^(={2,6})\s*(.*?)\s*=+\s*$/);
    if (m) {
      lines.push("", `${"#".repeat(m[1].length)} ${cleanInline(m[2])}`, "");
      continue;
    }
    lines.push(cleanInline(raw.replace(/^[*#]+\s*/, "- ").replace(/^[:;]+\s*/, "")));
  }
  // "* {{see|...}}" renders as "- - name": one bullet is enough
  return lines.join("\n").replace(/^- - /gm, "- ").replace(/\n{3,}/g, "\n\n").trim();
}

/** XML entity decoding for dump <title>/<text> contents. */
export function decodeXml(s) {
  return s
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#039;|&apos;/g, "'")
    .replace(/&amp;/g, "&");
}

/** One <page> of a MediaWiki XML dump → {id, ns, title, redirect, text}. */
export function parseDumpPage(xml) {
  const tag = (name) => {
    const m = xml.match(new RegExp(`<${name}(?:\\s[^>]*)?>([\\s\\S]*?)</${name}>`));
    return m ? decodeXml(m[1]) : null;
  };
  const redirect = xml.match(/<redirect\s+title="([^"]*)"/);
  return {
    id: Number(tag("id")),
    ns: tag("ns"),
    title: tag("title") ?? "",
    redirect: redirect ? decodeXml(redirect[1]) : null,
    text: tag("text") ?? "",
  };
}

// ---- Wikimedia SQL dumps ----

// rows look like (10,0,'Computer_accessibility','',''); only the first three fields are needed
const REDIRECT_ROW = /\((\d+),(-?\d+),'((?:[^'\\]|\\.)*)',/g;

/** Main-namespace redirects in one line of enwiki-*-redirect.sql: [[fromPageId, targetTitle]]. */
export function parseRedirectRows(line) {
  if (!line.startsWith("INSERT INTO") && !line.startsWith("(")) return [];
  const out = [];
  for (const m of line.matchAll(REDIRECT_ROW)) {
    if (m[2] !== "0") continue;
    out.push([Number(m[1]), m[3].replace(/\\(.)/g, "$1").replace(/_/g, " ")]);
  }
  return out;
}

/** One line of pages-articles-multistream-index.txt ("offset:pageId:title") → [pageId, title]. */
export function parseIndexLine(line) {
  const a = line.indexOf(":");
  const b = line.indexOf(":", a + 1);
  if (a < 0 || b < 0) return null;
  return [Number(line.slice(a + 1, b)), line.slice(b + 1)];
}

/**
 * A page URL safe to store in a pack: spaces become underscores on wiki paths and %20 elsewhere, other unencoded
 * characters are encoded, already-encoded URLs stay as they are. Same rule as normalizeUrl in src/rag/packs.ts.
 */
export function normalizeUrl(url) {
  const spaced = /\/wiki\//.test(url) ? url.replace(/ /g, "_") : url.replace(/ /g, "%20");
  try {
    return encodeURI(decodeURI(spaced));
  } catch {
    return spaced;
  }
}
