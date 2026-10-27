#!/usr/bin/env node
// CF data build: country facts from Wikidata (CC0) via the public SPARQL endpoint.
// Usage: node build-cf-data.mjs <out.json> [--cache <dir>]
// Generic User-Agent, no personal data. Fields the source lacks stay empty (never guessed).
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const OUT = process.argv[2] || "countryFacts.v1.json";
const cacheArg = process.argv.indexOf("--cache");
const CACHE = cacheArg > 0 ? process.argv[cacheArg + 1] : null;
if (CACHE) fs.mkdirSync(CACHE, { recursive: true });
const UA = "boar-cf-build/0.1";
const ENDPOINT = "https://query.wikidata.org/sparql";

// Country set. Step 1 asks Wikidata for the current UN members; then the observers (Vatican City, Palestine) and two widely
// recognised non-members (Taiwan, Kosovo) are added. Wikidata models three UN members as odd entities (the Kingdom of
// Denmark, the Kingdom of the Netherlands, "Third Hellenic Republic") and the UK twice: those are swapped for the
// entities people ask about (Denmark, the Netherlands, Greece, United Kingdom).
const SET_QUERY = `SELECT DISTINCT ?c WHERE {
  { ?c p:P463 ?un . ?un ps:P463 wd:Q1065 . FILTER NOT EXISTS { ?un pq:P582 ?unEnd } }
  UNION { VALUES ?c { wd:Q237 wd:Q219060 wd:Q865 wd:Q1246 wd:Q35 wd:Q55 wd:Q41 } }
  FILTER NOT EXISTS { ?c wdt:P576 ?dissolved }
}`;
const EXCLUDE = new Set(["Q756617", "Q29999", "Q17765809", "Q124653007"]);
let COUNTRY_SET = "";

async function sparql(name, query) {
  const file = CACHE ? path.join(CACHE, `${name}.json`) : null;
  if (file && fs.existsSync(file)) return JSON.parse(fs.readFileSync(file, "utf8"));
  for (let attempt = 0; attempt < 5; attempt++) {
    const res = await fetch(ENDPOINT, {
      method: "POST",
      headers: { "User-Agent": UA, Accept: "application/sparql-results+json", "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ query }).toString(),
    });
    if (res.ok) {
      const rows = (await res.json()).results.bindings;
      if (file) fs.writeFileSync(file, JSON.stringify(rows));
      return rows;
    }
    await new Promise((r) => setTimeout(r, 4000 * (attempt + 1)));
  }
  throw new Error(`SPARQL failed: ${name}`);
}
const qid = (u) => u.value.split("/").pop();
const val = (b, k) => (b[k] ? b[k].value : undefined);

const mkQ = () => ({
  base: `SELECT ?c ?cLabel ?iso2 WHERE {
    ${COUNTRY_SET}
    OPTIONAL { ?c wdt:P297 ?iso2 }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
  }`,
  capital: `SELECT ?c ?x ?xLabel WHERE { ${COUNTRY_SET} ?c p:P36 ?s . ?s ps:P36 ?x . FILTER NOT EXISTS { ?s pq:P582 ?e } OPTIONAL { ?s wikibase:rank ?rk }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }`,
  population: `SELECT ?c ?v ?t ?pref WHERE { ${COUNTRY_SET} ?c p:P1082 ?s . ?s ps:P1082 ?v . ?s wikibase:rank ?rk . FILTER(?rk != wikibase:DeprecatedRank) BIND(?rk = wikibase:PreferredRank AS ?pref) OPTIONAL { ?s pq:P585 ?t } FILTER NOT EXISTS { ?s pq:P518 ?part } }`,
  area: `SELECT ?c ?v ?u WHERE { ${COUNTRY_SET} ?c p:P2046 ?s . ?s psv:P2046 ?n . ?n wikibase:quantityAmount ?v ; wikibase:quantityUnit ?u . ?s wikibase:rank ?rk . FILTER(?rk != wikibase:DeprecatedRank) }`,
  // Currency: a current currency item (no end date), a statement with no end time, not deprecated;
  // a preferred-rank statement wins over the others (Netherlands: euro over the Caribbean US dollar).
  currency: `SELECT ?c ?x ?xLabel ?code ?pref ?scoped WHERE { ${COUNTRY_SET} ?c p:P38 ?s . ?s ps:P38 ?x . ?s wikibase:rank ?rk . FILTER(?rk != wikibase:DeprecatedRank) BIND(?rk = wikibase:PreferredRank AS ?pref)
    OPTIONAL { ?s pq:P518 ?part } BIND(BOUND(?part) AS ?scoped) FILTER NOT EXISTS { ?s pq:P582 ?e } FILTER NOT EXISTS { ?x wdt:P576 ?cEnd } ?x wdt:P31/wdt:P279* wd:Q8142 . OPTIONAL { ?x wdt:P498 ?code }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }`,
  languages: `SELECT ?c ?x ?xLabel ?pref WHERE { ${COUNTRY_SET} ?c p:P37 ?s . ?s ps:P37 ?x . ?s wikibase:rank ?rk . FILTER(?rk != wikibase:DeprecatedRank) BIND(?rk = wikibase:PreferredRank AS ?pref) FILTER NOT EXISTS { ?s pq:P582 ?e }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }`,
  calling: `SELECT ?c ?v WHERE { ${COUNTRY_SET} ?c wdt:P474 ?v }`,
  driving: `SELECT ?c ?x WHERE { ${COUNTRY_SET} ?c wdt:P1622 ?x }`,
  plug: `SELECT ?c ?x ?xLabel WHERE { ${COUNTRY_SET} ?c wdt:P2853 ?x SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }`,
  voltage: `SELECT ?c ?v WHERE { ${COUNTRY_SET} ?c wdt:P2884 ?v }`,
    tz: `SELECT ?c ?x ?xLabel WHERE { ${COUNTRY_SET} ?c wdt:P421 ?x SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }`,
  continent: `SELECT ?c ?x ?xLabel WHERE { ${COUNTRY_SET} ?c wdt:P30 ?x SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }`,
  neighbours: `SELECT ?c ?x ?xLabel WHERE { ${COUNTRY_SET} ?c wdt:P47 ?x . ?x wdt:P31 wd:Q6256 SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }`,
  gov: `SELECT ?c ?x ?xLabel WHERE { ${COUNTRY_SET} ?c p:P122 ?s . ?s ps:P122 ?x . ?s wikibase:rank ?rk . FILTER(?rk != wikibase:DeprecatedRank) FILTER NOT EXISTS { ?s pq:P582 ?e }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }`,
  hos: `SELECT ?c ?x ?xLabel WHERE { ${COUNTRY_SET} ?c wdt:P1906 ?x SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }`,
});

const setRows = await sparql("set", SET_QUERY);
const SET = setRows.map((b) => qid(b.c)).filter((x) => !EXCLUDE.has(x));
console.error(`country set: ${SET.length}`);
COUNTRY_SET = `VALUES ?c { ${SET.map((x) => "wd:" + x).join(" ")} }`;
const Q = mkQ();
const rows = {};
for (const [k, q] of Object.entries(Q)) {
  rows[k] = await sparql(k, q);
  console.error(`${k}: ${rows[k].length} rows`);
}

const by = {};
const rec = (id) => (by[id] ??= { qid: id });
for (const b of rows.base) {
  const r = rec(qid(b.c));
  r.name = val(b, "cLabel");
  if (val(b, "iso2")) r.iso2 = val(b, "iso2");
}
const ids = Object.keys(by);
const push = (id, key, v) => {
  if (!by[id]) return;
  (by[id][key] ??= []);
  if (!by[id][key].includes(v)) by[id][key].push(v);
};
for (const b of rows.capital) push(qid(b.c), "capital", val(b, "xLabel"));
{
  const prefLang = new Set(rows.languages.filter((b) => val(b, "pref") === "true").map((b) => qid(b.c)));
  for (const b of rows.languages) if (!prefLang.has(qid(b.c)) || val(b, "pref") === "true") push(qid(b.c), "languages", val(b, "xLabel"));
}
for (const b of rows.calling) push(qid(b.c), "calling", val(b, "v"));
// Plug items -> the IEC letter type (IEC TR 60083), a fixed table of standards, never per-country. The category item
// "AC power plugs and sockets: British and related types" is not a plug and is dropped; an unknown label stays as written.
const PLUG_TYPE = { "NEMA 1-15": "A", "NEMA 5-15": "B", Europlug: "C", "BS 546": "D", "Type E": "E", Schuko: "F", "BS 1363": "G", "Type H": "H", "AS/NZS 3112": "I", "SN 441011": "J", "Type K": "K", "Type L": "L", "IEC 60906-1": "N" };
for (const b of rows.plug) {
  const label = val(b, "xLabel");
  if (/^AC power plugs and sockets/.test(label)) continue;
  const t = PLUG_TYPE[label] ?? (/^Type ([A-O])$/.exec(label)?.[1]);
  push(qid(b.c), "plugs", t ? (/^Type /.test(label) ? `Type ${t}` : `Type ${t} (${label})`) : label);
}
for (const b of rows.voltage) push(qid(b.c), "voltage", Number(val(b, "v")));
for (const b of rows.tz) if (/^UTC[+−±-]/.test(val(b, "xLabel"))) push(qid(b.c), "timezones", val(b, "xLabel"));
for (const b of rows.continent) push(qid(b.c), "continents", val(b, "xLabel"));
for (const b of rows.neighbours) push(qid(b.c), "neighbours", val(b, "xLabel"));
for (const b of rows.hos) push(qid(b.c), "headOfState", val(b, "xLabel"));
{
  // Per country: preferred-rank statements if any; else the ones not scoped to part of the country (France's CFP franc,
  // the Caribbean Netherlands' dollar) if any; else all. Names of withdrawn ISO 4217 codes (Poland's old zloty) are dropped.
  const NAME_FALLBACK = { EUR: "euro" };
  const WITHDRAWN = new Set(["PLZ"]);
  const per = {};
  for (const b of rows.currency) (per[qid(b.c)] ??= []).push(b);
  for (const [id, bs] of Object.entries(per)) {
    if (!by[id]) continue;
    const pref = bs.filter((b) => val(b, "pref") === "true");
    const unscoped = bs.filter((b) => val(b, "scoped") !== "true");
    const use = pref.length ? pref : unscoped.length ? unscoped : bs;
    for (const b of use) {
      const code = /^[A-Z]{3}$/.test(val(b, "code") ?? "") ? val(b, "code") : undefined;
      let name = val(b, "xLabel");
      if (/^Q\d+$/.test(name)) name = NAME_FALLBACK[code] ?? undefined;
      if (!name || !code || WITHDRAWN.has(code)) continue;
      (by[id].currencies ??= []);
      if (!by[id].currencies.some((x) => x.code === code)) by[id].currencies.push({ name, code });
    }
  }
  // More than three current currencies (Zimbabwe's multi-currency list): not one answer, so left empty.
  for (const c of Object.values(by)) if (c.currencies && c.currencies.length > 3) delete c.currencies;
}
for (const b of rows.driving) {
  const id = qid(b.c);
  if (by[id]) by[id].driving = { Q14565199: "right", Q11920728: "left", Q13196750: "left" }[qid(b.x)] ?? undefined;
}
for (const b of rows.gov) push(qid(b.c), "government", val(b, "xLabel"));
// Population: a preferred-rank statement when there is one, else the newest point in time (undated statements rank last).
const popBest = {};
for (const b of rows.population) {
  const id = qid(b.c);
  const t = val(b, "t") ? val(b, "t").slice(0, 4) : "";
  const v = Number(val(b, "v"));
  const pref = val(b, "pref") === "true" ? 1 : 0;
  const cur = popBest[id];
  if (!cur || pref > cur.pref || (pref === cur.pref && (t > cur.t || (t === cur.t && t !== "" && v > cur.v)))) popBest[id] = { v, t, pref };
}
for (const [id, p] of Object.entries(popBest)) if (by[id]) { by[id].population = Math.round(p.v); if (p.t) by[id].populationYear = Number(p.t); }
// Area: km² only (Q712226); several values -> the largest (land+water totals dominate).
for (const b of rows.area) {
  const id = qid(b.c);
  if (!by[id] || qid(b.u) !== "Q712226") continue;
  const v = Number(val(b, "v"));
  if (!by[id].areaKm2 || v > by[id].areaKm2) by[id].areaKm2 = v;
}

const names = new Set(Object.values(by).map((c) => c.name));
for (const c of Object.values(by)) if (c.neighbours) c.neighbours = c.neighbours.filter((n) => names.has(n) && n !== c.name);
const countries = ids
  .map((id) => by[id])
  .filter((c) => c.name && !/^Q\d+$/.test(c.name))
  .sort((a, b) => a.name.localeCompare(b.name));

const out = {
  source: "Wikidata (CC0 1.0), https://query.wikidata.org/sparql",
  retrieved: new Date().toISOString().slice(0, 10),
  count: countries.length,
  queries: Q,
  countries,
};
const text = JSON.stringify(out);
fs.writeFileSync(OUT, text);
const sha = crypto.createHash("sha256").update(text).digest("hex");
console.error(`wrote ${OUT}: ${countries.length} countries, ${text.length} bytes, sha256 ${sha}`);
const cov = (f) => countries.filter((c) => (Array.isArray(c[f]) ? c[f].length : c[f] !== undefined)).length;
console.error(Object.fromEntries(["capital", "currencies", "population", "areaKm2", "languages", "calling", "driving", "plugs", "voltage", "timezones", "continents", "neighbours", "headOfState", "government"].map((f) => [f, cov(f)])));
