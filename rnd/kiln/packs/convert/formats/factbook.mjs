// CIA World Factbook CC0 JSON archive (github.com/factbook/factbook.json, one <region>/<code>.json per country)
// → one builder document per country: a "Key facts:" paragraph (one fact per line, kept under one chunk so the
// builder's lead rule embeds the prose that follows it), then "## Background" and one section per category.
import { readFileSync, readdirSync, statSync } from "node:fs";
import { basename, join } from "node:path";
import { ID_BASE, htmlToText } from "../lib/common.mjs";

export const usage = `factbook <dir | file.json ...>  [--snapshot DATE] [--limit N] [--id-base N]`;

/** A field's text: its own "text", else its first child's (the latest year in yearly series), HTML stripped. */
export function fieldText(v) {
  if (v == null) return "";
  if (typeof v === "string") return htmlToText(v).replace(/\s*\n+\s*/g, " ");
  if (typeof v.text === "string") return htmlToText(v.text).replace(/\s*\n+\s*/g, " ");
  for (const [k, c] of Object.entries(v)) if (k !== "note") return fieldText(c);
  return "";
}

/** Every leaf of a field as "Label: text" lines (sub-fields as "Label (sub): text"; notes kept). */
function flatten(label, v, out) {
  if (v == null) return;
  if (typeof v === "string") {
    const t = htmlToText(v).replace(/\s*\n+\s*/g, " ");
    if (t) out.push(`${label}: ${t}`);
    return;
  }
  if (typeof v.text === "string") {
    const t = htmlToText(v.text).replace(/\s*\n+\s*/g, " ");
    if (t) out.push(`${label}: ${t}`);
  }
  for (const [k, c] of Object.entries(v)) if (k !== "text") flatten(`${label} (${k.trim()})`, c, out);
}

const KEY_FACTS = [
  ["Official name", ["Government", "Country name", "conventional long form"]],
  ["Capital", ["Government", "Capital", "name"]],
  ["Time zone", ["Government", "Capital", "time difference"]],
  ["Location", ["Geography", "Location"]],
  ["Area", ["Geography", "Area", "total "]],
  ["Area", ["Geography", "Area", "total"]],
  ["Population", ["People and Society", "Population", "total"]],
  ["Population", ["People and Society", "Population"]],
  ["Languages", ["People and Society", "Languages", "Languages"]],
  ["Religions", ["People and Society", "Religions"]],
  ["Ethnic groups", ["People and Society", "Ethnic groups"]],
  ["Government type", ["Government", "Government type"]],
  ["Independence", ["Government", "Independence"]],
  ["Currency", ["Economy", "Exchange rates", "Currency"]],
  ["GDP (official exchange rate)", ["Economy", "GDP (official exchange rate)"]],
  ["Real GDP per capita", ["Economy", "Real GDP per capita"]],
  ["Life expectancy at birth", ["People and Society", "Life expectancy at birth", "total population"]],
  ["Climate", ["Geography", "Climate"]],
  ["Internet country code", ["Communications", "Internet country code"]],
];
const REGIONS = new Set(["africa", "antarctica", "australia-oceania", "central-america-n-caribbean", "central-asia", "east-n-southeast-asia", "europe", "meta", "middle-east", "north-america", "oceans", "south-america", "south-asia", "world"]);
// T-K6: archive short forms that are not usable display titles (abbreviations, truncated or list-like names, ocean
// files without a country name). The archive's own short form is kept as an alias.
const TITLE_OVERRIDE = {
  cg: "Democratic Republic of the Congo", dr: "Dominican Republic", ee: "European Union", gz: "Gaza Strip",
  sv: "Svalbard", um: "United States Pacific Island Wildlife Refuges",
  oo: "Southern Ocean", xo: "Indian Ocean", xq: "Arctic Ocean", zh: "Atlantic Ocean", zn: "Pacific Ocean",
};
const at = (o, path) => path.reduce((x, k) => (x == null ? x : x[k]), o);
const nameOk = (s) => s && !/^none$/i.test(s);

/** One document from a country JSON object and its file code ("br") (pure; unit-tested). */
export function countryDoc(d, code, opts = {}) {
  const cn = d.Government?.["Country name"] ?? {};
  const short = fieldText(cn["conventional short form"]);
  const archiveTitle = nameOk(short) ? short : fieldText(cn["conventional long form"]) || (code === "xx" ? "World" : code.toUpperCase());
  const title = TITLE_OVERRIDE[code] ?? archiveTitle;
  const facts = [];
  const seen = new Set();
  for (const [label, path] of KEY_FACTS) {
    if (seen.has(label)) continue;
    let t = fieldText(at(d, path));
    if (label === "Currency") t = t.replace(/\s+per US dollar\b.*$/, "");
    if (label === "Time zone") t = t.replace(/\s*\(.*$/, "");
    if (!t || /^none$/i.test(t)) continue;
    if (t.length > 160) t = `${t.slice(0, t.lastIndexOf(" ", 157))}…`;
    facts.push(`${label}: ${t}`);
    seen.add(label);
  }
  // One chunk: the builder's lead rule skips a first chunk that starts with "Key facts:" only if it's alone.
  let keyFacts = `Key facts:\n${facts.join("\n")}`;
  while (keyFacts.length > 1400) keyFacts = keyFacts.slice(0, keyFacts.lastIndexOf("\n"));
  const parts = facts.length ? [keyFacts] : [];
  const bg = fieldText(d.Introduction?.Background);
  if (bg) parts.push(`## Background\n\n${bg}`);
  for (const [cat, fields] of Object.entries(d)) {
    if (cat === "Introduction" || !fields || typeof fields !== "object") continue;
    const paras = [];
    for (const [f, v] of Object.entries(fields)) {
      const lines = [];
      flatten(f.trim(), v, lines);
      if (lines.length) paras.push(lines.join("\n"));
    }
    if (paras.length) parts.push(`## ${cat}\n\n${paras.join("\n\n")}`);
  }
  const aliases = [archiveTitle !== title && !/^[A-Z]{2}$/.test(archiveTitle) && archiveTitle.length > 1 && archiveTitle.length < 80 ? archiveTitle : null, cn["conventional long form"], cn["local short form"], cn["local long form"], cn["former"], cn["abbreviation"]]
    .flatMap((v) => fieldText(v).split(/\s*(?:[;,/]|\bor\b)\s*/))
    .map((x) => x.replace(/\s*\([^)]*\)\s*/g, " ").trim())
    .filter((x) => nameOk(x) && x !== title && x.length > 1 && x.length < 80 && !/[()]/.test(x));
  const snapshot = opts.snapshot ?? "unknown";
  return {
    page_id: (opts.idBase ?? ID_BASE.factbook) + parseInt(code, 36),
    title,
    text: parts.join("\n\n"),
    source: "factbook",
    url: opts.urlOf ? opts.urlOf(code) : `https://github.com/factbook/factbook.json/blob/master/${code}.json`,
    license: `CC0 (CIA World Factbook archive, data as of ${snapshot})`,
    attribution: `CIA World Factbook (US government work), via the factbook/factbook.json CC0 archive, snapshot ${snapshot}`,
    aliases: [...new Set(aliases)],
    views: 0,
    infoboxes: null,
  };
}

function files(inputs) {
  const out = [];
  for (const p of inputs) {
    if (statSync(p).isDirectory()) {
      for (const e of readdirSync(p, { recursive: true })) if (/(^|\/)[a-z]{2}\.json$/.test(e)) out.push(join(p, e));
    } else out.push(p);
  }
  return out.sort();
}

export async function convert(input, opts) {
  const inputs = files([input, ...(opts._extra ?? [])]);
  const docs = [];
  const stats = { files: inputs.length, short: 0 };
  for (const f of inputs) {
    if (opts.limit && docs.length >= opts.limit) break;
    const code = basename(f, ".json");
    const region = basename(join(f, ".."));
    const d = countryDoc(JSON.parse(readFileSync(f, "utf8")), code, {
      snapshot: opts.snapshot,
      idBase: opts["id-base"] ? Number(opts["id-base"]) : undefined,
      urlOf: (c) => `https://github.com/factbook/factbook.json/blob/master/${REGIONS.has(region) ? `${region}/` : ""}${c}.json`,
    });
    if (d.text.length < 200) {
      stats.short++;
      continue;
    }
    docs.push(d);
  }
  return { name: "factbook", docs, info: { format: "factbook", snapshot: opts.snapshot ?? null, inputs, params: { limit: opts.limit ?? 0 }, stats } };
}
