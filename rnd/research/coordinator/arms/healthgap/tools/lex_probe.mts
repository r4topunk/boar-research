// HEALTHGAP: the engine's own deterministic layers on the 15 model-answered Q2 items (0 LLM). Run from the cut 7 tree:
//   cp tools/lex_probe.mts <tree>/_p.mts && (cd <tree> && npx tsx ./_p.mts); rm <tree>/_p.mts
import * as fs from "node:fs";
const T = "<workspace>/kiln-local/be-0cfd4a77-cut7/src/routing/";
const CX: any = await import(T + "context.ts");
const CC: any = await import(T + "conditionCards.ts");
const CO: any = await import(T + "coHazard.ts");
const CA: any = await import(T + "calculators.ts");
const AR: any = await import(T + "arithmetic.ts");
const ids = "h01 h02 h08 h10 h15 h19 h21 h23 h24 h27 h28 n03 n06 n12 vit-hlt-003".split(" ");
const qs: Record<string, string> = {};
for (const f of ["health", "multiturn", "final-probes", "final-probes-mt"]) for (const l of fs.readFileSync(`<workspace>/rnd/research/coordinator/arms/numguard/review/${f}.jsonl`, "utf8").split("\n")) if (l.trim()) { const d = JSON.parse(l); qs[d.id] = d.question; }
for (const l of fs.readFileSync("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "utf8").split("\n")) if (l.trim()) { const d = JSON.parse(l); qs[d.id] = d.question; }
for (const id of ids) {
  const q = qs[id]; const pt = CX.isPortugueseQuestion(q);
  const w = (f: () => any) => { try { const v = f(); return v == null ? null : typeof v === "object" ? (v.kind ?? v.template ?? JSON.stringify(v).slice(0, 40)) : v; } catch (e: any) { return "ERR " + e.message; } };
  console.log(JSON.stringify({ id, lexicon: w(() => CX.isHealthQuestion(q)), card: w(() => CC.regexCondition(q)), cardEmergency: w(() => CC.isCardEmergency(q)), coHazard: w(() => CO.isCoHazardQuestion(q)), coExposure: w(() => CO.isCoExposure(q)), calc: w(() => CA.calculate(q, pt)), arith: w(() => AR.arithmeticAnswer(q)) }));
}
