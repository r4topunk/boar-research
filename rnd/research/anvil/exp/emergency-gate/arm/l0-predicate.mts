// L0 predicate level (Anvil B6E arm): arm health = gate EM || isHealthFollowUp || isCardEmergency (answer.ts);
// control (same tree, BOAR_ROUTE_GATE=0) health = isHealthQuestion || isHealthFollowUp || isCardEmergency. Dev pool labels.
import fs from "node:fs";
const [tree] = process.argv.slice(2);
const C = await import(`${tree}/src/routing/context.ts`), K = await import(`${tree}/src/routing/conditionCards.ts`);
const D = "<workspace>/rnd/research/anvil/exp/emergency-gate";
const pool = JSON.parse(fs.readFileSync(`${D}/pool.json`, "utf8"));
const g = new Map(fs.readFileSync(`${D}/arm/l0-b6e.jsonl`, "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((r) => r.set === "pool").map((r) => [r.id, r]));
const tally: Record<string, Record<string, number>> = { arm: {}, ctl: {} };
for (const p of pool) {
  const ut = p.history.filter((t: any) => t[0] === "user").map((t: any) => t[1]);
  const fu = C.isHealthFollowUp(p.msg, ut);
  const armLex = (g.get(p.id) as any).emergency, ctlLex = C.isHealthQuestion(p.msg);
  const arm = armLex || fu || (!armLex && !fu && K.isCardEmergency(p.msg));
  const ctl = ctlLex || fu || (!ctlLex && !fu && K.isCardEmergency(p.msg));
  for (const [k, v] of [["arm", arm], ["ctl", ctl]] as const) tally[k][`${p.label}:${v}`] = (tally[k][`${p.label}:${v}`] ?? 0) + 1;
}
for (const k of ["arm", "ctl"]) console.log(k, `EMERGENCY ${tally[k]["EMERGENCY:true"] ?? 0}/185 · NOT fired ${tally[k]["NOT:true"] ?? 0}/391 · HEALTH_INFO fired ${tally[k]["HEALTH_INFO:true"] ?? 0}/23`);
