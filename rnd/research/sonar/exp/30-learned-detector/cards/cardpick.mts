// Card-pick L0: which condition card each arm would show (conversationCondition + a card text in the item's language).
// usage: tsx cardpick.mts <treeA> <treeB>
import fs from "node:fs";
const [ta, tb] = process.argv.slice(2);
const A = await import(`${ta}/src/routing/conditionCards.ts`), B = await import(`${tb}/src/routing/conditionCards.ts`);
const X = new URL(".", import.meta.url).pathname;
const jl = (p: string) => fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const lang = (s: string) => (/[¿¡ñ]|\b(qué|está|mi|hijo|hace|tiene)\b/i.test(s) ? "es" : /[ãõç]|\b(não|você|meu|minha|está|tá)\b/i.test(s) ? "pt" : "en");
const card = (M: any, turns: string[]) => {
  const q = turns[turns.length - 1], prev = turns.slice(0, -1);
  const c = M.conversationCondition(q, prev).condition;
  if (!c || c === "MULTI") return "generic";
  const t = M.conditionCardText(c, q, lang(turns.join(" ")));
  return t ? c : "generic";
};
// Compass emergency-dev positives
const D = jl("<workspace>/rnd/research/compass/exp/emergency-dev/dev.jsonl").filter((d: any) => d.emergency === 1);
const KEYS = new Set(Object.keys((JSON.parse(fs.readFileSync(`${tb}/src/routing/conditionCards.v1.json`, "utf8")) as any).cards).concat(["snakebite"]));
for (const [name, M] of [["A", A], ["B", B]] as const) {
  let right = 0, wrong = 0, generic = 0; const wrongs: string[] = [];
  for (const d of D) {
    const turns = d.turns.filter((t: any) => t.role === "user").map((t: any) => t.text); const got = card(M, turns);
    const want = KEYS.has(d.cond) ? d.cond : "generic"; // a condition without a card: only the generic line is right
    if (got === "generic") generic++; else if (got === want || (want === "choking" && got === "chokinginfant" && /infant|beb|lactante/i.test(turns.join(" ")))) right++; else { wrong++; wrongs.push(`${d.id} ${d.cond}->${got}`); }
  }
  console.log(`${name} Compass positives ${D.length}: right card ${right}, WRONG card ${wrong}, generic ${generic} | ${wrongs.join("; ")}`);
}
for (const [name, M] of [["A", A], ["B", B]] as const) {
  const P = jl(X + "probes.cardpick.jsonl"); let ok = 0; const bad: string[] = [];
  for (const p of P) { const got = card(M, p.turns); if (got === p.expect) ok++; else bad.push(`${p.id} want ${p.expect} got ${got}`); }
  console.log(`${name} probes ${ok}/${P.length} | ${bad.join("; ")}`);
}
