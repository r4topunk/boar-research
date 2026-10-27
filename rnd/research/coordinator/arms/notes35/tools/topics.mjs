#!/usr/bin/env node
// NOTES35 topic list: Wikipedia Vital Articles Level 3 (~1,000 titles) with their section path, then a deterministic
// breadth-first order whose every prefix is section-balanced. Topics come from Wikipedia's list only (never bench items).
//
//   node tools/topics.mjs [--out-dir topics]      # writes topics/vital3.jsonl (+ .sha256), topics/order-bf.txt (+ .sha256)
//   node tools/topics.mjs --from-cache            # re-derive from topics/vital3.raw.json (no network)
//
// Network: GET only, en.wikipedia.org API, the app pack builder's User-Agent, maxlag 5 and its retry/backoff
// (boar-app/scripts/build-knowledge-pack.mjs `wiki()`), one request at a time (3 requests in total). Nothing is uploaded.
//
// Why not only the builder's helper: build-knowledge-pack.mjs lists `Vital_articles/Level_<n>/` subpages and keeps them
// through lib `vitalListPages`; that matches Level 4/5 (one subpage per topic). Level 3 is ONE page,
// "Wikipedia:Vital articles/Level 3" (its old topic subpages are now redirects), so vitalListPages returns only its
// "Nav bar" subpage. We run the builder's discovery step anyway (logged), then read the root page itself: its wikitext
// for the section path (== Section ==, === Subsection ===, ==== Sub-subsection ====) and its prop=links (the builder's
// method) as a cross-check that every listed title is a real article link on the page.
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const BOAR = resolve(HERE, "../../../../../..");
const { vitalListPages } = await import(join(BOAR, "boar-app/scripts/lib/knowledge-pack-lib.mjs"));

const WIKI_API = "https://en.wikipedia.org/w/api.php";
const USER_AGENT = "BOAR-knowledge-pack-builder/1.0 (https://github.com/UPSTREAM_REPO/boar-app)"; // = build-knowledge-pack.mjs
const LEVEL = 3;
const ROOT = `Wikipedia:Vital articles/Level ${LEVEL}`;

const argv = process.argv.slice(2);
const outDir = resolve(argv.includes("--out-dir") ? argv[argv.indexOf("--out-dir") + 1] : join(HERE, "../topics"));
const fromCache = argv.includes("--from-cache");
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const sha256 = (s) => createHash("sha256").update(s).digest("hex");

// Same request policy as the builder's wiki(): formatversion 2, maxlag 5, retry 429/5xx/maxlag with 2 s * 2^n backoff.
async function wiki(params, attempt = 0) {
  const url = `${WIKI_API}?${new URLSearchParams({ format: "json", formatversion: "2", maxlag: "5", ...params })}`;
  try {
    const res = await fetch(url, { headers: { "User-Agent": USER_AGENT } });
    if (res.status === 429 || res.status >= 500) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.error?.code === "maxlag") throw new Error("maxlag");
    if (data.error) throw new Error(`${data.error.code}: ${data.error.info}`);
    return data;
  } catch (e) {
    if (attempt >= 6) throw e;
    await sleep(2000 * 2 ** attempt);
    return wiki(params, attempt + 1);
  }
}

async function download() {
  // 1. The builder's discovery step, verbatim parameters (logged only; see header).
  const prefix = `Vital_articles/Level_${LEVEL}/`;
  const pages = [];
  let cont = {};
  do {
    const d = await wiki({ action: "query", list: "allpages", apnamespace: "4", apprefix: prefix, apfilterredir: "nonredirects", aplimit: "500", ...cont });
    pages.push(...d.query.allpages.map((p) => p.title));
    cont = d.continue ?? null;
  } while (cont);
  const helperPages = vitalListPages(pages, LEVEL);
  // 2. The Level 3 list page itself: wikitext (sections) + links (the builder's prop=links method).
  const rev = await wiki({ action: "query", prop: "revisions", rvprop: "content|ids|timestamp", rvslots: "main", titles: ROOT });
  const page = rev.query.pages[0];
  const r = page.revisions[0];
  const links = [];
  let c = {};
  do {
    const d = await wiki({ action: "query", prop: "links", titles: ROOT, plnamespace: "0", pllimit: "max", ...c });
    for (const p of d.query.pages) for (const l of p.links ?? []) links.push(l.title);
    c = d.continue ?? null;
  } while (c);
  return { root: ROOT, pageid: page.pageid, revid: r.revid, timestamp: r.timestamp, fetchedAt: new Date().toISOString(),
           allpagesNonRedirects: pages, helperListPages: helperPages, links, wikitext: r.slots.main.content };
}

const norm = (t) => {
  const s = t.replace(/_/g, " ").replace(/\s+/g, " ").trim();
  return s.charAt(0).toUpperCase() + s.slice(1);
};
const cleanHeading = (h) => h.replace(/<[^>]+>/g, "").replace(/\{\{[^}]*\}\}/g, "").replace(/\[\[(?:[^|\]]*\|)?([^\]]*)\]\]/g, "$1").trim();

/** List entries under "=Level 3 vital articles=": [{title, path}] in page order. */
function parseList(wikitext) {
  const lines = wikitext.split("\n");
  const out = [];
  const path = [];
  let inList = false;
  for (const line of lines) {
    const h = line.match(/^(=+)\s*(.*?)\s*\1\s*$/);
    if (h) {
      const level = h[1].length;
      if (level === 1) { inList = /vital articles/i.test(h[2]); path.length = 0; continue; }
      if (!inList) continue;
      path.length = level - 2;
      path[level - 2] = cleanHeading(h[2]);
      continue;
    }
    if (!inList || !/^\*/.test(line) || !path.length) continue;
    // First article link of the bullet ({{Icon|..}} badges precede it); skip File:/Category:/namespace links.
    const links = [...line.matchAll(/\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]/g)].map((m) => m[1]).filter((t) => !/^[A-Za-z ]+:/.test(t));
    const va = line.match(/\{\{VA link\|([^}|]+)/i);
    const t = links[0] ?? va?.[1];
    if (t) out.push({ title: norm(t), path: path.filter(Boolean).slice() });
  }
  return out;
}

const rawFile = join(outDir, "vital3.raw.json");
mkdirSync(outDir, { recursive: true });
let raw;
if (fromCache) raw = JSON.parse(readFileSync(rawFile, "utf8"));
else {
  raw = await download();
  writeFileSync(rawFile, JSON.stringify(raw));
}
console.error(`builder discovery (allpages ${raw.allpagesNonRedirects.length} non-redirect pages under Level_${LEVEL}/): vitalListPages -> ${JSON.stringify(raw.helperListPages)} (not a list; reading ${raw.root} itself, revid ${raw.revid})`);

const linkSet = new Set(raw.links.map(norm));
const entries = parseList(raw.wikitext);
const seen = new Set();
const rows = [];
let notLinked = 0;
for (const e of entries) {
  if (seen.has(e.title)) continue;
  seen.add(e.title);
  if (!linkSet.has(e.title)) { notLinked++; continue; }
  rows.push({ title: e.title, section: e.path[0], subsection: e.path.slice(1).join(" > "), path: e.path, rank: rows.length, revid: raw.revid });
}
const jsonl = rows.map((r) => JSON.stringify(r)).join("\n") + "\n";
writeFileSync(join(outDir, "vital3.jsonl"), jsonl);
writeFileSync(join(outDir, "vital3.jsonl.sha256"), `${sha256(jsonl)}  vital3.jsonl\n`);

// Breadth-first order: inside a section, round-robin over its subsections (alphabetical), titles sorted inside each;
// then round-robin over the sections (alphabetical). Any prefix of N titles is within one title per section of balanced.
const cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
const roundRobin = (lists) => {
  const out = [];
  for (let i = 0; lists.some((l) => i < l.length); i++) for (const l of lists) if (i < l.length) out.push(l[i]);
  return out;
};
const bySection = new Map();
for (const r of rows) {
  if (!bySection.has(r.section)) bySection.set(r.section, new Map());
  const subs = bySection.get(r.section);
  if (!subs.has(r.subsection)) subs.set(r.subsection, []);
  subs.get(r.subsection).push(r);
}
const sectionSeqs = [...bySection.keys()].sort(cmp).map((s) => {
  const subs = bySection.get(s);
  return roundRobin([...subs.keys()].sort(cmp).map((k) => subs.get(k).slice().sort((a, b) => cmp(a.title, b.title))));
});
const order = roundRobin(sectionSeqs);
const orderTxt = order.map((r, i) => `${i + 1}\t${r.title}\t${r.path.join(" > ")}`).join("\n") + "\n";
writeFileSync(join(outDir, "order-bf.txt"), orderTxt);
writeFileSync(join(outDir, "order-bf.txt.sha256"), `${sha256(orderTxt)}  order-bf.txt\n`);

const count = (list) => {
  const m = new Map();
  for (const r of list) m.set(r.section, (m.get(r.section) ?? 0) + 1);
  return [...m.entries()].sort((a, b) => cmp(a[0], b[0]));
};
console.log(`vital3: ${rows.length} titles (list bullets ${entries.length}, duplicates ${entries.length - seen.size}, not in page links ${notLinked}), revid ${raw.revid}`);
console.log(`vital3.jsonl sha256 ${sha256(jsonl)}`);
console.log(`order-bf.txt sha256 ${sha256(orderTxt)}`);
console.log("section counts (all | first 300 of order-bf):");
const first300 = new Map(count(order.slice(0, 300)));
for (const [s, n] of count(rows)) console.log(`  ${s}: ${n} | ${first300.get(s) ?? 0}`);
