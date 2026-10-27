// Predicate-level floor variants for the B6E arm (Anvil, after Sonar's how-to risk). Dev only: Compass emergency-dev 300 + Anvil pool 599.
// env W (tree), SC (scratch with cdev-out rows). Gate scores: cdev from the frozen replay script rows; pool from arm/l0-b6e.jsonl.
import fs from "node:fs";
const W = process.env.W!, SC = process.env.SC!, A = "<workspace>/rnd/research/anvil/exp/emergency-gate";
const C = await import(`${W}/src/routing/context.ts`), K = await import(`${W}/src/routing/conditionCards.ts`);
const intent = (q: string) => C.ACTION_INTENT.test(q) || C.SHOULD_INTENT.test(q);
type It = { id: string; msg: string; ut: string[]; pE: number; grp: string; crit?: boolean };
const cd = new Map(fs.readFileSync(`${SC}/cdev-out/b6e-replay.rows.jsonl`, "utf8").trim().split("\n").map((l) => JSON.parse(l)).map((r: any) => [r.id, r.pE / r.mass]));
const cdev: It[] = fs.readFileSync("<workspace>/rnd/research/compass/exp/emergency-dev/dev.jsonl", "utf8").trim().split("\n").map((l) => JSON.parse(l)).map((r: any) => {
  const u = r.turns.filter((t: any) => t.role === "user").map((t: any) => t.text);
  return { id: r.id, msg: u[u.length - 1], ut: u.slice(0, -1), pE: cd.get(r.id) as number, grp: r.emergency ? "E" : r.howto ? "howto" : "neg", crit: r.sev === "critical" };
});
const g = new Map(fs.readFileSync(`${A}/arm/l0-b6e.jsonl`, "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((r: any) => r.set === "pool").map((r: any) => [r.id, r.em]));
const pool: It[] = JSON.parse(fs.readFileSync(`${A}/pool.json`, "utf8")).map((p: any) => ({ id: p.id, msg: p.msg, ut: p.history.filter((t: any) => t[0] === "user").map((t: any) => t[1]), pE: g.get(p.id) as number, grp: p.label === "EMERGENCY" ? "E" : p.label === "NOT" ? (p.hard_neg ? "hardneg" : "neg") : "info" }));
const base = (it: It) => it.pE >= 0.5 || C.isHealthFollowUp(it.msg, it.ut) || K.isCardEmergency(it.msg);
const cond = (q: string) => { const c = K.regexCondition(q); return !!c; };
const V: Record<string, (it: It) => boolean> = {
  V0_arm: base,
  V3_cardcond_intent: (it) => base(it) || (cond(it.msg) && intent(it.msg)),
  Vf01_regex_and_pE01: (it) => base(it) || (C.isHealthQuestion(it.msg) && it.pE >= 0.01),
  Vf001_regex_and_pE001: (it) => base(it) || (C.isHealthQuestion(it.msg) && it.pE >= 0.001),
  Vlex_regex_or: (it) => base(it) || C.isHealthQuestion(it.msg),
};
const n = (a: It[], f: (i: It) => boolean) => `${a.filter(f).length}/${a.length}`;
for (const [k, f] of Object.entries(V)) {
  const cE = cdev.filter((i) => i.grp === "E");
  console.log(`${k.padEnd(22)} cdev E ${n(cE, f)} crit-missed ${cE.filter((i) => i.crit && !f(i)).length} · strict FF ${n(cdev.filter((i) => i.grp === "neg"), f)} · howto ${n(cdev.filter((i) => i.grp === "howto"), f)}  ||  pool E ${n(pool.filter((i) => i.grp === "E"), f)} · NOT FF ${n(pool.filter((i) => i.grp === "neg" || i.grp === "hardneg"), f)} · hardneg ${n(pool.filter((i) => i.grp === "hardneg"), f)}`);
}
