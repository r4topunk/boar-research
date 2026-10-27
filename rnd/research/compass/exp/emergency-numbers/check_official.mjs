#!/usr/bin/env node
// Checks official-2026-10-03.json:
//  1. every quote that has a `snapshot` is an EXACT substring of that snapshot text (no normalisation);
//  2. every number in `numbers` appears in at least one of the country's quotes (digits only);
//  3. alias regexes compile and pass their should_match / should_not_match cases;
//  4. the proposed ES/EN/PT lines contain every digit-group the numbers object names.
// usage: node check_official.mjs   (exit 1 on any failure)
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const data = JSON.parse(readFileSync(join(here, "official-2026-10-03.json"), "utf8"));
let fail = 0;
const bad = (m) => { fail++; console.log("FAIL " + m); };

for (const c of data.countries) {
  const quotes = [{ quote: c.quote, snapshot: c.snapshot, status: c.status, what: "primary" }, ...(c.extra_quotes || [])];
  let ok = 0, dagger = 0;
  for (const q of quotes) {
    if (!q.snapshot) {
      if (q.status === "†") { dagger++; continue; }
      bad(`${c.iso} ${q.what}: no snapshot and status ${q.status}`); continue;
    }
    const text = readFileSync(join(here, q.snapshot), "utf8");
    if (text.includes(q.quote)) ok++;
    else bad(`${c.iso} ${q.what}: quote not an exact substring of ${q.snapshot}: ${JSON.stringify(q.quote.slice(0, 80))}`);
  }
  const allQuotes = quotes.map((q) => q.quote).join("\n");
  const nums = Object.values(c.numbers).filter(Boolean).join(" ").match(/\d{3}/g) || [];
  for (const n of new Set(nums)) if (!allQuotes.includes(n)) bad(`${c.iso}: number ${n} not in any quote`);
  for (const lang of ["en", "pt", "es"]) {
    for (const n of new Set(nums)) if (!c.proposed[lang].includes(n)) bad(`${c.iso} proposed.${lang} lacks ${n}`);
  }
  let re;
  try { re = new RegExp(c.aliases.regex, c.aliases.flags); } catch (e) { bad(`${c.iso}: regex error ${e.message}`); continue; }
  for (const s of c.aliases.should_match) if (!re.test(s)) bad(`${c.iso}: alias should match ${JSON.stringify(s)}`);
  for (const s of c.aliases.should_not_match) if (re.test(s)) bad(`${c.iso}: alias should NOT match ${JSON.stringify(s)}`);
  console.log(`${c.iso.padEnd(3)} ${c.status.padEnd(9)} quotes exact ${ok}/${quotes.length - dagger}${dagger ? `, † ${dagger}` : ""}, aliases ${c.aliases.should_match.length}+/${c.aliases.should_not_match.length}-`);
}
console.log(fail ? `\n${fail} FAILURE(S)` : "\nALL CHECKS PASS");
process.exit(fail ? 1 : 0);
