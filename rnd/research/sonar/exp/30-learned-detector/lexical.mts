// Lexical baseline = health9's health-route predicate (answer.ts L693-696): isHealthQuestion || isHealthFollowUp || isCardEmergency.
// usage: tsx lexical.mts <tree> <in.json|jsonl with {turns}> <out.json>
import fs from "node:fs";
const [tree, inp, out] = process.argv.slice(2);
const C = await import(`${tree}/src/routing/context.ts`);
const K = await import(`${tree}/src/routing/conditionCards.ts`);
const txt = fs.readFileSync(inp, "utf8");
const items: any[] = inp.endsWith(".json") ? JSON.parse(txt) : txt.split("\n").filter(Boolean).map((l) => JSON.parse(l));
const res = items.map((x) => {
  const q = x.turns[x.turns.length - 1], prev = x.turns.slice(0, -1);
  const hq = C.isHealthQuestion(q), fu = C.isHealthFollowUp(q, prev), card = !hq && !fu && K.isCardEmergency(q);
  const cc = K.conversationCondition(q, prev);
  return { hq: +hq, fu: +fu, card: +K.isCardEmergency(q), cond: cc && cc.condition !== "MULTI" ? cc.condition : null, intent: +(C.ACTION_INTENT.test(q) || C.SHOULD_INTENT.test(q)), any: hq || fu || card ? 1 : 0 };
});
fs.writeFileSync(out, JSON.stringify(res));
console.log(inp, items.length, "fires", res.filter((r) => r.any).length);
