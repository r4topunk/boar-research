// Shared helpers for the pack converters: entity decoding, HTML fragment → text,
// stable ids, licence rules and the output writer (builder JSONL + manifest + convert-info).
// No dependencies; Node >= 22.
import { createHash } from "node:crypto";
import { createReadStream, mkdirSync, statSync, writeFileSync } from "node:fs";
import { basename, join } from "node:path";

// Named entities seen in the inputs (HTML 4 Latin-1 set + common punctuation).
const LATIN1 =
  "nbsp iexcl cent pound curren yen brvbar sect uml copy ordf laquo not shy reg macr deg plusmn sup2 sup3 acute micro para middot cedil sup1 ordm raquo frac14 frac12 frac34 iquest Agrave Aacute Acirc Atilde Auml Aring AElig Ccedil Egrave Eacute Ecirc Euml Igrave Iacute Icirc Iuml ETH Ntilde Ograve Oacute Ocirc Otilde Ouml times Oslash Ugrave Uacute Ucirc Uuml Yacute THORN szlig agrave aacute acirc atilde auml aring aelig ccedil egrave eacute ecirc euml igrave iacute icirc iuml eth ntilde ograve oacute ocirc otilde ouml divide oslash ugrave uacute ucirc uuml yacute thorn yuml".split(" ");
const ENTITIES = Object.fromEntries(LATIN1.map((n, i) => [n, String.fromCodePoint(160 + i)]));
Object.assign(ENTITIES, {
  amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", ndash: "–", mdash: "—", lsquo: "‘", rsquo: "’", sbquo: "‚",
  ldquo: "“", rdquo: "”", bdquo: "„", hellip: "…", bull: "•", prime: "′", Prime: "″", trade: "™", euro: "€",
  larr: "←", rarr: "→", uarr: "↑", darr: "↓", harr: "↔", le: "≤", ge: "≥", ne: "≠", asymp: "≈", minus: "−",
  infin: "∞", alpha: "α", beta: "β", gamma: "γ", delta: "δ", mu: "μ", pi: "π", sigma: "σ", omega: "ω",
  Scaron: "Š", scaron: "š", OElig: "Œ", oelig: "œ", thinsp: " ", ensp: " ", emsp: " ", zwnj: "", zwj: "",
  lrm: "", rlm: "", dagger: "†", Dagger: "‡", permil: "‰", lsaquo: "‹", rsaquo: "›",
});

/** Decodes named (incl. Latin-1) and numeric character references; unknown names stay as they are. */
export function decodeEntities(s) {
  return s.replace(/&(#[xX][0-9a-fA-F]+|#\d+|[A-Za-z][A-Za-z0-9]*);/g, (m, e) => {
    if (e[0] === "#") {
      const cp = e[1] === "x" || e[1] === "X" ? parseInt(e.slice(2), 16) : Number(e.slice(1));
      return cp > 0 && cp <= 0x10ffff ? String.fromCodePoint(cp) : m;
    }
    return ENTITIES[e] ?? ENTITIES[e.toLowerCase()] ?? m;
  });
}

/** XML attributes of one start tag: {name: decodedValue}. */
export function xmlAttrs(tag) {
  const out = {};
  for (const m of tag.matchAll(/([A-Za-z_][\w.:-]*)="([^"]*)"/g)) out[m[1]] = decodeEntities(m[2]);
  return out;
}

/**
 * An HTML fragment (a Stack Exchange post body, a MedlinePlus summary, a Factbook field) as plain text:
 * paragraphs blank-line separated, list items as "- " / "1. " lines (nested lists indented), <pre> code kept
 * verbatim, inline <code> in backticks, headings as plain lines (they must not open builder sections),
 * links reduced to their text, images dropped. Never emits "#"-headings or lines starting with "|".
 */
export function htmlToText(html) {
  if (!html) return "";
  const pres = [];
  let s = html.replace(/<pre\b[^>]*>([\s\S]*?)<\/pre>/gi, (_, c) => {
    pres.push(decodeEntities(c.replace(/<[^>]+>/g, "")).replace(/\s+$/, ""));
    return `<p>\u0000${pres.length - 1}\u0000</p>`;
  });
  s = s.replace(/<(script|style)\b[\s\S]*?<\/\1>/gi, " ").replace(/<!--[\s\S]*?-->/g, " ");
  const lists = [];
  let out = "";
  for (const tok of s.split(/(<[^>]*>)/)) {
    if (!tok) continue;
    if (tok[0] !== "<") {
      out += decodeEntities(tok).replace(/\s+/g, " ");
      continue;
    }
    const m = tok.match(/^<\s*(\/?)\s*([a-zA-Z0-9]+)/);
    if (!m) continue;
    const close = m[1] === "/";
    const name = m[2].toLowerCase();
    if (name === "br") out += "\n";
    else if (name === "ul" || name === "ol") {
      if (close) lists.pop();
      else lists.push({ ordered: name === "ol", n: 0 });
      if (!lists.length || (!close && lists.length === 1)) out += "\n\n";
    } else if (name === "li" && !close) {
      const top = lists[lists.length - 1];
      const indent = "  ".repeat(Math.max(0, lists.length - 1));
      out += `\n${indent}${top?.ordered ? `${++top.n}. ` : "- "}`;
    } else if (/^(p|div|blockquote|h[1-6]|hr|table|section|article|dl)$/.test(name)) {
      out += lists.length ? "\n" : "\n\n";
    } else if (/^(tr|dt|dd)$/.test(name)) out += "\n";
    else if (/^(td|th)$/.test(name) && !close) out += " ";
    else if (name === "code") out += "`";
  }
  const text = out
    .split("\n")
    .map((l) => {
      const lead = l.match(/^ */)[0];
      const body = l.trim();
      // keep list indentation only
      return /^(- |\d+\. )/.test(body) ? lead + body : body;
    })
    .join("\n")
    .replace(/``/g, "")
    .replace(/^(#+)(\s)/gm, "$1​$2") // a literal "# x" line in a post must not become a builder heading
    .replace(/^\|/gm, "¦") // nor a table row the index skips
    .replace(/\n{3,}/g, "\n\n")
    .trim();
  return text.replace(/\u0000(\d+)\u0000/g, (_, i) => pres[Number(i)].replace(/^(#+\s)/gm, "​$1").replace(/^\|/gm, "¦"));
}

/** A stable non-negative integer from a string (FNV-1a 32-bit). */
export function hash32(s) {
  let h = 0x811c9dc5;
  for (const c of Buffer.from(s, "utf8")) h = Math.imul(h ^ c, 0x01000193) >>> 0;
  return h;
}

// page_id ranges (unique within one pack; builder dedups on page_id). Existing ones (see local-inventory §3):
// usgov pages 4e9 + hash31 (4.0e9…6.15e9), FM 21-76 4.5e9, EIPs 5e9, specs 6e9, ethereum.org 7e9, BIPs 8e9,
// MediaWiki sites code*1e9 + id. New ranges start above all of them.
export const ID_BASE = { medlineplus: 11e9, factbook: 12e9, pdf: 13e9, stackexchange: 1e14 };

/** Stack Exchange licence by contribution date (stackoverflow.com/help/licensing). */
export function seLicenseByDate(iso) {
  const d = (iso ?? "").slice(0, 10);
  if (d < "2011-04-08") return "CC BY-SA 2.5";
  if (d <= "2018-05-01") return "CC BY-SA 3.0";
  return "CC BY-SA 4.0";
}

export async function sha256File(path) {
  const h = createHash("sha256");
  for await (const b of createReadStream(path)) h.update(b);
  return h.digest("hex");
}

/**
 * Writes <out>/<name>.jsonl (builder input), <out>/manifest.json (the builder's --manifest: an array of
 * {source, title, url, license, chars}) and <out>/convert-info.json (counts, sources, licences, snapshot, input shas).
 */
export async function writeOutput(out, name, docs, info) {
  mkdirSync(out, { recursive: true });
  const jsonl = join(out, `${name}.jsonl`);
  writeFileSync(jsonl, docs.map((d) => JSON.stringify(d)).join("\n") + (docs.length ? "\n" : ""));
  const manifest = docs.map((d) => ({ source: d.source, title: d.title, url: d.url, license: d.license, chars: d.text.length }));
  writeFileSync(join(out, "manifest.json"), JSON.stringify(manifest, null, 1));
  const count = (key) => docs.reduce((m, d) => ((m[d[key]] = (m[d[key]] ?? 0) + 1), m), {});
  const inputs = [];
  for (const p of info.inputs ?? []) inputs.push({ file: basename(p), bytes: statSync(p).size, sha256: await sha256File(p) });
  const summary = {
    format: info.format,
    count: docs.length,
    sources: count("source"),
    licenses: count("license"),
    snapshot: info.snapshot ?? null,
    inputs,
    jsonl: { file: basename(jsonl), sha256: await sha256File(jsonl), bytes: statSync(jsonl).size },
    params: info.params ?? {},
    stats: info.stats ?? {},
    convertedAt: new Date().toISOString(),
  };
  writeFileSync(join(out, "convert-info.json"), `${JSON.stringify(summary, null, 2)}\n`);
  return summary;
}

/** Lines of a member of a 7z/zip archive, streamed by bsdtar (libarchive ships with macOS). */
export async function* archiveLines(archive, member) {
  const { spawn } = await import("node:child_process");
  const { createInterface } = await import("node:readline");
  const child = spawn("bsdtar", ["-xOf", archive, member], { stdio: ["ignore", "pipe", "pipe"] });
  let err = "";
  child.stderr.on("data", (b) => (err += b));
  const done = new Promise((ok) => child.on("close", ok));
  for await (const line of createInterface({ input: child.stdout, crlfDelay: Infinity })) yield line;
  const code = await done;
  if (code !== 0) throw new Error(`bsdtar ${member}: exit ${code} ${err.trim()}`);
}
