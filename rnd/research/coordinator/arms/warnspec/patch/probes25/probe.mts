import { readFileSync } from "node:fs";
const tree = process.argv[2];
const W = await import(`${tree}/src/routing/warn.ts`);
const C = await import(`${tree}/src/routing/context.ts`);
const P = JSON.parse(readFileSync("probes.json", "utf8"));
const T = JSON.parse(readFileSync("tiers.json", "utf8"));
const base = { modelId: "qwen3-4b-instruct-2507-q4km", codes: ["task:research", "detector:p=0.010"], outcome: "success", text: "A model answer of some length here.", kept: [], cited: [] };
for (const p of P) {
  const got = W.warnOf({ ...base, query: p.q });
  console.log(JSON.stringify({ id: p.id, exp: p.exp, got, ok: got === p.exp, reasons: W.healthReasons({ query: p.q, codes: base.codes, kept: [] }), lex: (p.q.match(W.WARN_LEX) || [null])[0], safety: C.isSafetyQuery(p.q), lang: W.warnLang(p.q) }));
}
for (const t of T) {
  const got = W.warnOf({ ...base, query: t.q, text: t.text, kept: Array.from({ length: t.kept }, () => ({ source: "x" })), cited: t.cited });
  console.log(JSON.stringify({ id: t.id, exp: t.exp, got, ok: got === t.exp, sents: W.contentSentences(t.text), unc: W.uncoveredSentences(t.text) }));
}
// rounding edge for the receipt's detector:p
for (const p of [0.0495, 0.04951, 0.0499]) console.log("p", p, p.toFixed(3), W.healthReasons({ query: "x", codes: [`detector:p=${p.toFixed(3)}`], kept: [] }));
