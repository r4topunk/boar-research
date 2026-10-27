// PDF manuals (US Army ATP/FM/TC, other US government publications) → one builder document per section.
// pdftotext -layout; running headers/footers, page numbers, Word bookmark ids ("195B") and front matter dropped;
// a chapter opens on a page whose first line is "Chapter N" / "Appendix X" / "Glossary" (centred); sections are
// ALL-CAPS lines at the left margin. When the table of contents lists section names ("Tier 1 Skills for …"),
// only those open a new document and the other caps headings become "## " subsections; otherwise every caps
// heading opens one. "References" and "Index" end the text. Step lists keep one line per step.
import { execFileSync } from "node:child_process";
import { ID_BASE, hash32 } from "../lib/common.mjs";

export const usage = `pdf <manual.pdf> --manual "ATP 4-02.11" --doc-title "…" --date 2026-03-23 --url URL [--limit N] [--id-base N] [--min-chars 200]`;
export const LICENSE = "US government work (17 U.S.C. §105), public release";

const norm = (s) => s.toUpperCase().replace(/[^A-Z0-9]+/g, " ").trim();
const runKey = (s) => s.trim().replace(/\d+/g, "#").replace(/\s+/g, " ");
const CHAPTER = /^\s{8,}(Chapter \d+|Appendix [A-Z]|Glossary|References|Index)\s*$/;
const CAPS = /^[A-Z][A-Z0-9 ,'’()/&:–—-]{3,}$/;

/** Title-case section names from a table of contents with dot leaders (indented entries only). */
export function tocSections(lines) {
  const out = new Set();
  let pending = "";
  for (const l of lines) {
    const m = l.match(/^(\s{6,})(\S.*?)\s*\.{4,}/);
    if (m) {
      const name = `${pending} ${m[2]}`.trim();
      if (/[a-z]/.test(name)) out.add(norm(name));
      pending = "";
    } else pending = /^\s{6,}\S/.test(l) && !/\.{4,}/.test(l) && /[a-z]/.test(l) ? `${pending} ${l.trim()}` : "";
  }
  return out;
}

/** Body lines of a page with running headers/footers removed. */
function cleanPage(lines, running) {
  const nonEmpty = lines.map((l, i) => [l, i]).filter(([l]) => l.trim());
  const edge = new Set([...nonEmpty.slice(0, 3), ...nonEmpty.slice(-3)].map(([, i]) => i));
  return lines.filter((l, i) => CHAPTER.test(l) || !(edge.has(i) && (running.has(runKey(l)) || /^\s*([ivx]+|\d+|[A-Z]-\d+)\s*$/.test(l))));
}

/** Text of one section: lines kept, paragraphs at blank lines and at numbered paragraphs ("4-12."). */
export function sectionText(lines) {
  const out = [];
  for (const raw of lines) {
    if (raw[0] === "\u0001") {
      out.push(raw.slice(1));
      continue;
    }
    if (/^\s*\d{1,4}B\s*$/.test(raw)) continue; // Word bookmark ids left in the text layer
    if (/Distribution Restriction:|This publication supersedes|intentionally left blank/i.test(raw)) continue;
    let l = raw.trim().replace(/\s{3,}/g, " · ");
    if (!l) {
      if (out.length && out[out.length - 1] !== "") out.push("");
      continue;
    }
    l = l.replace(/^[•●]\s*/, "- ").replace(/^[▪◦○]\s*/, "  - ");
    if (/^([A-Z]-)?\d+-\d+\.\s/.test(l) && out.length && out[out.length - 1] !== "") out.push("");
    if (/^[#|]/.test(l)) l = `​${l}`;
    out.push(l);
  }
  return out.join("\n").replace(/\n{2,}/g, "\n\n").trim();
}

/** Documents from pdftotext -layout output (pure; unit-tested on a synthetic manual). */
export function manualDocs(layoutText, meta) {
  const pages = layoutText.split("\f").map((p) => p.split("\n"));
  const counts = new Map();
  for (const p of pages) {
    const ne = p.filter((l) => l.trim());
    for (const k of new Set([...ne.slice(0, 3), ...ne.slice(-3)].map(runKey))) counts.set(k, (counts.get(k) ?? 0) + 1);
  }
  const running = new Set([...counts].filter(([k, n]) => n >= Math.max(3, pages.length * 0.15) && k.length <= 90 && !CAPS.test(k)).map(([k]) => k));
  const toc = tocSections(pages.slice(0, Math.min(pages.length, 20)).flat());
  const docs = [];
  let chapter = null; // {label, title}
  let section = null; // {name, lines}
  let started = false;
  let stopped = false;
  const flush = () => {
    if (section && chapter) {
      const text = sectionText(section.lines);
      if (text.length >= (meta.minChars ?? 200)) {
        const where = [chapter.label, chapter.title].filter(Boolean).join(" ");
        docs.push({ title: `${meta.manual} — ${where}${section.name ? `: ${section.name}` : ""}`, text });
      }
    }
    section = null;
  };
  for (const page of pages) {
    if (stopped) break;
    const lines = cleanPage(page, running);
    for (let i = 0; i < lines.length; i++) {
      const l = lines[i];
      const m = l.match(CHAPTER);
      // A new chapter: a centred "Chapter N" whose label differs from the current one (running headers repeat it),
      // followed by its centred title.
      if (m && m[1] !== chapter?.label) {
        const label = m[1];
        if (/^(References|Index)$/.test(label)) {
          if (started) {
            flush();
            stopped = true;
            break;
          }
          continue;
        }
        let j = i + 1;
        const titleLines = [];
        while (j < lines.length && lines[j].trim() && /^\s{6,}\S/.test(lines[j])) titleLines.push(lines[j++].trim().replace(/\s+\d+B$/, ""));
        if (label !== "Glossary" && !titleLines.length) continue; // a cross-reference, not a chapter start
        flush();
        started = true;
        chapter = { label, title: titleLines.join(" ") };
        section = { name: "", lines: [] };
        i = j - 1;
        continue;
      }
      if (!started) continue;
      if (CAPS.test(l) && !/^\s/.test(l)) {
        // multi-line caps heading at the margin
        let name = l.trim();
        while (i + 1 < lines.length && CAPS.test(lines[i + 1]) && !/^\s/.test(lines[i + 1]) && lines[i + 1].trim().length < 40) name += ` ${lines[++i].trim()}`;
        if (toc.size && !toc.has(norm(name))) {
          // the heading's last word wrapped below a bookmark id and blank lines ("… MARINE CORPS" / "195B" / "UNITS")
          let j = i + 1;
          while (j < lines.length && j < i + 8 && (!lines[j].trim() || /^\s*\d{1,4}B\s*$/.test(lines[j]))) j++;
          if (j < lines.length && CAPS.test(lines[j]) && toc.has(norm(`${name} ${lines[j]}`))) {
            name += ` ${lines[j].trim()}`;
            i = j;
          }
        }
        const pretty = name.toLowerCase().replace(/(^|[\s(/-])([a-z])/g, (_, a, b) => a + b.toUpperCase());
        if (!toc.size || toc.has(norm(name)) || !section) {
          flush();
          section = { name: pretty, lines: [] };
        } else {
          section.lines.push("", `\u0001## ${pretty}`, "");
        }
        continue;
      }
      section?.lines.push(l);
    }
  }
  if (!stopped) flush();
  // Repeated section names in one chapter ("Application of Tourniquets" under tier 1 and tier 2) get a counter.
  const seen = new Map();
  for (const d of docs) {
    const n = (seen.get(d.title) ?? 0) + 1;
    seen.set(d.title, n);
    if (n > 1) d.title = `${d.title} (${n})`;
  }
  const base = meta.idBase ?? ID_BASE.pdf + (hash32(meta.manual) % 1000) * 1e6;
  return docs.map((d, i) => ({
    page_id: base + i,
    title: d.title,
    text: d.text,
    source: "usgov",
    url: meta.url,
    license: LICENSE,
    attribution: `${meta.docTitle ?? meta.manual}, ${meta.manual}, ${meta.date ?? "undated"}; ${meta.url}`,
    aliases: [],
    views: 0,
    infoboxes: null,
  }));
}

export async function convert(input, opts) {
  if (!opts.manual || !opts.url) throw new Error("pdf: --manual and --url are required");
  const layout = execFileSync("pdftotext", ["-layout", "-enc", "UTF-8", input, "-"], { maxBuffer: 1 << 30 }).toString("utf8");
  let docs = manualDocs(layout, {
    manual: opts.manual,
    docTitle: opts["doc-title"],
    date: opts.date,
    url: opts.url,
    idBase: opts["id-base"] ? Number(opts["id-base"]) : undefined,
    minChars: Number(opts["min-chars"] ?? 200),
  });
  if (opts.limit) docs = docs.slice(0, opts.limit);
  return {
    name: opts.manual.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
    docs,
    info: { format: "pdf", snapshot: opts.date ?? null, inputs: [input], params: { manual: opts.manual, url: opts.url, limit: opts.limit ?? 0 }, stats: { pages: layout.split("\f").length, sections: docs.length } },
  };
}
