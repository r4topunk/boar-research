// Stack Exchange site dump (archive.org item "stackexchange", <site>.7z with Posts.xml + Users.xml)
// → one builder document per question with its best answers and per-row attribution.
import { basename } from "node:path";
import { ID_BASE, archiveLines, hash32, htmlToText, seLicenseByDate, xmlAttrs } from "../lib/common.mjs";

// Sites renamed after their dump file name was fixed (old host → current host; old URLs redirect).
const RENAMED = { "health.stackexchange.com": "medicalsciences.stackexchange.com" };

export const usage = `stackexchange <site>.7z  [--site-host HOST] [--min-score N=1] [--max-answers N=5] [--keep-unanswered] [--limit N] [--id-base N]`;

export function siteHostOf(file, override) {
  if (override) return override;
  const host = basename(file).replace(/\.7z$/, "");
  return RENAMED[host] ?? host;
}

export function tagsOf(raw) {
  if (!raw) return [];
  return raw.includes("|") ? raw.split("|").filter(Boolean) : [...raw.matchAll(/<([^>]+)>/g)].map((m) => m[1]);
}

/** The post's licence: its ContentLicense attribute (2024 dumps) or else the date rule. */
export function postLicense(p) {
  return p.ContentLicense || seLicenseByDate(p.CreationDate);
}

/** Author name + profile URL for a post (deleted accounts → "user<Id>"; no account → OwnerDisplayName). */
export function author(p, users, host) {
  if (p.OwnerUserId) {
    const name = users.get(p.OwnerUserId) ?? `user${p.OwnerUserId}`;
    return `${name} (https://${host}/users/${p.OwnerUserId})`;
  }
  return p.OwnerDisplayName ? `${p.OwnerDisplayName} (no profile)` : "anonymous (no profile)";
}

/** One document from a question row, its answer rows and the users map (pure; unit-tested). */
export function questionDoc(q, answers, users, host, opts = {}) {
  const minScore = opts.minScore ?? 1;
  const maxAnswers = opts.maxAnswers ?? 5;
  const kept = answers
    .filter((a) => a.Id === q.AcceptedAnswerId || Number(a.Score) >= minScore)
    .sort((a, b) => (b.Id === q.AcceptedAnswerId) - (a.Id === q.AcceptedAnswerId) || Number(b.Score) - Number(a.Score) || Number(a.Id) - Number(b.Id))
    .slice(0, maxAnswers);
  if (!kept.length && !opts.keepUnanswered) return null;
  const url = `https://${host}/questions/${q.Id}`;
  const tags = tagsOf(q.Tags);
  const parts = [];
  if (tags.length) parts.push(`Tags: ${tags.join(", ")}`);
  parts.push(htmlToText(q.Body));
  if (kept.length) {
    parts.push("## Answers");
    for (const a of kept) {
      const flags = [`score ${Number(a.Score)}`, ...(a.Id === q.AcceptedAnswerId ? ["accepted"] : [])].join(", ");
      parts.push(`### Answer (${flags})\n\n${htmlToText(a.Body)}`);
    }
  }
  const license = postLicense(q);
  const answerLicenses = [...new Set(kept.map(postLicense))].filter((l) => l !== license);
  const attribution = [
    `Q by ${author(q, users, host)}`,
    ...kept.map((a) => `A by ${author(a, users, host)}`),
    url,
    ...(answerLicenses.length ? [`answers also under ${answerLicenses.join(", ")}`] : []),
  ].join("; ");
  return {
    page_id: (opts.idBase ?? ID_BASE.stackexchange + (hash32(host) % 1e6) * 1e8) + Number(q.Id),
    title: q.Title,
    text: parts.filter(Boolean).join("\n\n"),
    source: "stackexchange",
    url,
    license,
    attribution,
    aliases: [],
    views: Number(q.ViewCount) || 0,
    infoboxes: null,
  };
}

export async function convert(input, opts) {
  const host = siteHostOf(input, opts["site-host"]);
  const questions = [];
  const answersByParent = new Map();
  const needUsers = new Set();
  let rows = 0;
  for await (const line of archiveLines(input, "Posts.xml")) {
    if (!line.includes("<row ")) continue;
    rows++;
    const p = xmlAttrs(line);
    if (p.PostTypeId === "1") questions.push(p);
    else if (p.PostTypeId === "2") {
      if (!answersByParent.has(p.ParentId)) answersByParent.set(p.ParentId, []);
      answersByParent.get(p.ParentId).push(p);
    }
  }
  for (const q of questions) {
    if (q.OwnerUserId) needUsers.add(q.OwnerUserId);
    for (const a of answersByParent.get(q.Id) ?? []) if (a.OwnerUserId) needUsers.add(a.OwnerUserId);
  }
  const users = new Map();
  for await (const line of archiveLines(input, "Users.xml")) {
    if (!line.includes("<row ")) continue;
    const id = line.match(/ Id="(-?\d+)"/)?.[1];
    if (!needUsers.has(id)) continue;
    users.set(id, xmlAttrs(line).DisplayName);
  }
  const docs = [];
  const stats = { postRows: rows, questions: questions.length, noKeptAnswer: 0, short: 0, licenseFromAttribute: 0, licenseDateMismatch: 0, mixedLicenseRows: 0 };
  const idBase = opts["id-base"] ? Number(opts["id-base"]) : undefined;
  for (const q of questions) {
    if (opts.limit && docs.length >= opts.limit) break;
    const d = questionDoc(q, answersByParent.get(q.Id) ?? [], users, host, {
      minScore: Number(opts["min-score"] ?? 1),
      maxAnswers: Number(opts["max-answers"] ?? 5),
      keepUnanswered: !!opts["keep-unanswered"],
      idBase,
    });
    if (!d) {
      stats.noKeptAnswer++;
      continue;
    }
    if (d.text.length < 200) {
      stats.short++;
      continue;
    }
    if (q.ContentLicense) stats.licenseFromAttribute++;
    if (q.ContentLicense && q.ContentLicense !== seLicenseByDate(q.CreationDate)) stats.licenseDateMismatch++;
    if (d.attribution.includes("answers also under")) stats.mixedLicenseRows++;
    docs.push(d);
  }
  return {
    name: host.replace(/\./g, "-"),
    docs,
    info: { format: "stackexchange", snapshot: "archive.org stackexchange item, dump 2024-04-02", inputs: [input], params: { host, minScore: opts["min-score"] ?? 1, maxAnswers: opts["max-answers"] ?? 5, limit: opts.limit ?? 0 }, stats },
  };
}
