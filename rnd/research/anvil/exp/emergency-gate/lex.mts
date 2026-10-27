// Lexical health path of health9 (answer.ts:694-696): isHealthQuestion || isHealthFollowUp || isCardEmergency
import fs from "node:fs";
const D = process.env.S!;
const C = await import(`${D}/h9/src/routing/context.ts`);
const K = await import(`${D}/h9/src/routing/conditionCards.ts`);
const pool = JSON.parse(fs.readFileSync(`${D}/pool.json`, "utf8"));
const out = pool.map((p: any) => {
  const q = p.msg; const userTurns = p.history.filter((t: any) => t[0] === "user").map((t: any) => t[1]);
  const hq = C.isHealthQuestion(q), fu = C.isHealthFollowUp(q, userTurns), ce = !hq && !fu && K.isCardEmergency(q);
  return { id: p.id, lex: hq || fu || ce, hq, fu, ce };
});
fs.writeFileSync(`${D}/lex.json`, JSON.stringify(out));
console.log(out.filter((o: any) => o.lex).length, "/", out.length, "fire");
