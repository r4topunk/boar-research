// MedlinePlus Health Topics XML (medlineplus.gov/xml.html, mplus_topics_<date>.xml or its zip)
// → one builder document per English health topic. Only NLM's own text is used: <full-summary>,
// also-called names, related topics and groups. <site> links (A.D.A.M. encyclopedia "ency/", ASHP
// drug pages "druginfo/", external sites) are dropped entirely.
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { ID_BASE, decodeEntities, htmlToText, xmlAttrs } from "../lib/common.mjs";

export const usage = `medlineplus <mplus_topics_DATE.xml | .zip>  [--lang English] [--limit N] [--id-base N]`;
export const LICENSE = "Public domain (NLM); courtesy of MedlinePlus from the National Library of Medicine";
export const CREDIT = "Courtesy of MedlinePlus from the National Library of Medicine";

const inner = (s) => decodeEntities(s.replace(/<[^>]+>/g, "")).replace(/\s+/g, " ").trim();
const all = (block, tag) => [...block.matchAll(new RegExp(`<${tag}\\b[^>]*>([\\s\\S]*?)</${tag}>`, "g"))].map((m) => inner(m[1]));

/** One document from a <health-topic …>…</health-topic> block (pure; unit-tested). */
export function topicDoc(block, opts = {}) {
  const a = xmlAttrs(block.match(/<health-topic\b[^>]*>/)[0]);
  if (opts.lang && a.language !== opts.lang) return null;
  const summaryRaw = block.match(/<full-summary>([\s\S]*?)<\/full-summary>/)?.[1];
  if (!summaryRaw) return null;
  // The summary is HTML escaped inside XML: unescape once, then convert the HTML.
  const summary = htmlToText(decodeEntities(summaryRaw));
  const alsoCalled = all(block, "also-called");
  const seeRefs = all(block, "see-reference");
  const related = all(block, "related-topic");
  const groups = all(block, "group");
  const parts = [summary];
  if (alsoCalled.length) parts.push(`Also called: ${alsoCalled.join(", ")}`);
  if (related.length) parts.push(`See also: ${related.join(", ")}`);
  if (groups.length) parts.push(`Topic groups: ${groups.join(", ")}`);
  const seen = new Set([a.title.toLowerCase()]);
  const aliases = [...alsoCalled, ...seeRefs].filter((x) => x && !seen.has(x.toLowerCase()) && seen.add(x.toLowerCase()));
  return {
    page_id: (opts.idBase ?? ID_BASE.medlineplus) + Number(a.id),
    title: a.title,
    text: parts.join("\n\n"),
    source: "medlineplus",
    url: a.url,
    license: LICENSE,
    attribution: `${CREDIT}; ${a.url}`,
    aliases,
    views: 0,
    infoboxes: null,
  };
}

export async function convert(input, opts) {
  const xml = input.endsWith(".zip") ? execFileSync("unzip", ["-p", input], { maxBuffer: 1 << 30 }).toString("utf8") : readFileSync(input, "utf8");
  const generated = xml.match(/<health-topics\b[^>]*date-generated="([^"]+)"/)?.[1] ?? null;
  const docs = [];
  const stats = { topics: 0, otherLanguage: 0, noSummary: 0, short: 0 };
  const lang = opts.lang ?? "English";
  for (const m of xml.matchAll(/<health-topic\b[\s\S]*?<\/health-topic>/g)) {
    stats.topics++;
    if (opts.limit && docs.length >= opts.limit) break;
    const d = topicDoc(m[0], { lang, idBase: opts["id-base"] ? Number(opts["id-base"]) : undefined });
    if (!d) {
      if (xmlAttrs(m[0].match(/<health-topic\b[^>]*>/)[0]).language !== lang) stats.otherLanguage++;
      else stats.noSummary++;
      continue;
    }
    if (d.text.length < 200) {
      stats.short++;
      continue;
    }
    docs.push(d);
  }
  return { name: "medlineplus-topics", docs, info: { format: "medlineplus", snapshot: generated, inputs: [input], params: { lang, limit: opts.limit ?? 0 }, stats } };
}
