// cvs-dev-replay: which DEV CV answers (rev1-routed, from arms the existing cv-dev-cv-s44 traces) would the CVS guard turn into abstains?
// The traces hold the rendered "Facts:" lines, so the figures are re-read from them (name: label figure) and fed to the guard.
// usage: tsx cvs-dev-replay.mts [tree]
import fs from "node:fs";
const tree = process.argv[2] ?? "<workspace>/wt/cvs";
const B = "<workspace>";
const { routeVerdict } = await import(`${tree}/src/routing/computedVerdict.ts`);
const { plausibleFact, comparableValues } = await import(`${tree}/src/routing/factSanity.ts`);
const { parseFigure, FIGURE_RE, parseUnit, toBase } = await import(`${tree}/src/routing/verdictUnits.ts`);
const T = fs.readFileSync(`${B}/boar-eval/runs/kiln/cv-dev-cv-s44/traces.jsonl`, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
let nF = 0, cv = 0, abst = 0; const rows: string[] = [];
for (const t of T) {
  if (!(t.route?.reasonCodes ?? []).includes("answer:computed-verdict")) continue;
  const plan = routeVerdict(t.question);
  if (!plan || !["compare", "threshold", "year"].includes(plan.kind)) continue; // rev1 scope (superlative/distance/literal out or model-free)
  cv++;
  const lines = String(t.answer.text).split("\n").filter((l: string) => /^- /.test(l) && !/Threshold in the question|Year in the question/.test(l));
  const facts: { name: string; dim: any; base: number }[] = [];
  for (const l of lines) {
    const m = l.match(/^- (.+?): (.+)$/); if (!m) continue;
    const rest = m[2].replace(/\s*\(=.*?\)/, "");
    if (plan.q === "year") { const y = rest.match(/(-?\d{1,4})(\s*BC)?$/); if (y) facts.push({ name: m[1], dim: "year", base: (y[2] ? -1 : 1) * Number(y[1]) }); continue; }
    const sci = rest.match(/(-?[\d.]+)\s*×\s*10\^(-?\d+)\s*(\S+)\s*$/);
    if (sci) { const u = parseUnit(sci[3]); if (u) facts.push({ name: m[1], dim: u.dim, base: toBase(Number(sci[1]) * 10 ** Number(sci[2]), u) }); continue; }
    const fm = rest.match(new RegExp(`(${FIGURE_RE})\\s*$`, "i")) ;
    // figure = last number+unit in the line (labels like "average density" precede it)
    const mm = rest.match(/(-?\d[\d,.]*(?:\s*(?:×\s*10\^-?\d+|million|billion|trillion))?)\s*(\S.*)?$/);
    if (!mm) continue;
    const fig = parseFigure(`${mm[1]} ${mm[2] ?? ""}`.trim()); void fm;
    if (fig) facts.push({ name: m[1], dim: fig.unit.dim, base: fig.base });
  }
  nF += facts.length;
  let bad = facts.filter((f) => !plausibleFact(f.name, f.dim, f.base));
  let pair = false;
  if (plan.kind === "compare" && facts.length === 2 && plan.q !== "year" && facts[0].dim === facts[1].dim && !comparableValues(facts[0].name, facts[1].name, facts[0].dim, facts[0].base, facts[1].base)) pair = true;
  if (bad.length || pair) { abst++; rows.push(`${t.itemId} ${t.question.slice(0, 60)} | ${lines.map((x: string) => x.slice(2)).join(" ; ")} | ${bad.length ? "range" : "100x"}`); }
}
console.log(`parsed facts total: ${nF}`);
console.log(`DEV CV answers in rev1 scope (compare/threshold/year): ${cv}; the guard would abstain on ${abst}`);
for (const r of rows) console.log("  " + r);
