// HFUFIX build checks (G4/G5a + 192-message routing diff). Based on hfu.mts.
// HFU diagnostic (criterion sha256 64a6bf1d...0cdd). Deterministic: routing + reason codes only. No generation, no judge.
// usage: tsx hfufix_eval.mts <hfufix-tree> <outdir>
// The learned emergency detector is STUBBED (learned = null): answer.ts then uses the lexical path ("without the detector: unchanged").
// Health decision replicated from answer.ts (cut5lite): early cards (snakebite / CO hazard / emergency numbers), then
//   health = isHealthQuestion(q) || isHealthFollowUp(q, userTurns) || (!lex && !fu && isCardEmergency(q)).
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
const T = process.argv[2];
const OUT = process.argv[3];
const R = "<workspace>";
const ctx = await import(`${T}/src/routing/context.ts`);
const cc = await import(`${T}/src/routing/conditionCards.ts`);
const { isSnakebiteFirstAid } = await import(`${T}/src/routing/firstAidCards.ts`);
const { isCoHazardQuestion } = await import(`${T}/src/routing/coHazard.ts`);
const { emergencyNumbersAnswer } = await import(`${T}/src/routing/emergencyNumbers.ts`);
const { classifyTask } = await import(`${T}/src/routing/classify.ts`);
const { routeGateSkip } = await import(`${T}/src/routing/routeGate.ts`);
const { smallTalkReply } = await import(`${T}/src/routing/smallTalk.ts`);

const { recoverHealthFollowUp } = await import(`${T}/src/routing/healthFollowUp.ts`);
export type Route = { health: boolean; early: string | null; codes: string[]; task: string };
function route(query: string, turns: {role:string;text:string}[], fix: boolean): Route {
  const userTurns = turns.filter((t) => t.role === "user").map((t) => t.text);
  const rec = fix ? recoverHealthFollowUp(query, turns) : null;
  const codes: string[] = [];
  const pt = ctx.isPortugueseQuestion(query);
  const es = !pt && ctx.isSpanishQuestion(query);
  let early: string | null = null;
  if (isSnakebiteFirstAid(query)) early = "answer:first-aid-card-snakebite";
  else if (!pt && !es && isCoHazardQuestion(query)) early = "answer:safety-fact-co-hazard";
  else if (emergencyNumbersAnswer(query, pt)) early = "answer:emergency-numbers";
  else if (smallTalkReply(query, pt, new Date("2026-10-06T12:00:00"))) early = "answer:small-talk";
  const lex = ctx.isHealthQuestion(query);
  const fu = ctx.isHealthFollowUp(query, userTurns) || !!rec;
  const cardEm = !lex && !fu && cc.isCardEmergency(query);
  const health = lex || fu || cardEm;
  if (lex) codes.push("health:lexical");
  if (cardEm) codes.push("grounding:health-card-condition");
  if (fu) codes.push("grounding:health-follow-up");
  if (rec) codes.push(`grounding:health-follow-recovered-${rec}`);
  const cond = cc.conversationCondition(query, userTurns);
  if (cond.condition) codes.push(`condition:${cond.condition}${cond.fromHistory ? ":from-history" : ""}`);
  if (ctx.isSafetyQuery(query) || rec) codes.push("ui:safety-note");
  if (lex) codes.push("retrieve:canonical-health-terms"); // answer.ts L932 without detector: isHealthQuestion(req.query) only
  if (early) codes.unshift(early);
  const rule = classifyTask(query);
  const skip = routeGateSkip({ ruleTaskType: rule, query, historyTurns: userTurns.length * 2, detectorFired: false, emergencyLexical: cc.isCardEmergency(query) || ctx.isSafetyQuery(query) });
  codes.push(`task:${rule}`);
  if (skip) codes.push("route-gate:skip-rules");
  return { health, early, codes, task: rule };
}
// "health route" = answer.ts treats the turn as health (health flag) OR an early health card fires (snakebite / CO / numbers).
const gets = (r: Route) => r.health || (!!r.early && r.early !== "answer:small-talk");
const jl = (p: string) => readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));


mkdirSync(OUT, { recursive: true });
// ---- 192 dev chat messages: every user turn, history = the conversation's earlier turns (user + assistant)
const slices: [string, string][] = [
  ["chat-v0", `${R}/rnd/research/compass/chat-slice/slice.v0.jsonl`],
  ["chat-v1", `${R}/rnd/research/compass/chat-slice/v1-fresh/slice.v1.jsonl`],
  ["chat-v2", `${R}/rnd/research/compass/chat-slice/v2-fresh/slice.v2.jsonl`],
];
let msgs = 0, changed = 0, noCondConvs = 0, noCondChanges = 0, noCondNewHealth = 0, newHealth = 0, safetyChanged = 0;
const lines: string[] = ["set\tid\tturn\tcondConv\tbase(health|codes)\tfix(health|codes)\ttext"];
for (const [set, p] of slices)
  for (const c of jl(p)) {
    const users: string[] = c.turns.filter((t: any) => t.role === "user").map((t: any) => t.text);
    const condConv = users.some((_, i) => cc.conversationCondition(users[i], users.slice(0, i)).condition !== null);
    if (!condConv) noCondConvs++;
    for (let i = 0; i < c.turns.length; i++) {
      if (c.turns[i].role !== "user") continue;
      msgs++;
      const hist = c.turns.slice(0, i);
      const b = route(c.turns[i].text, hist, false), f = route(c.turns[i].text, hist, true);
      const diff = JSON.stringify([b.health, b.early, b.codes]) !== JSON.stringify([f.health, f.early, f.codes]);
      if (!diff) continue;
      changed++;
      if (!gets(b) && gets(f)) { newHealth++; if (!condConv) noCondNewHealth++; }
      if (!condConv) noCondChanges++;
      lines.push(`${set}\t${c.id}\t${i}\t${condConv}\t${b.health}|${b.codes.join(" ")}\t${f.health}|${f.codes.join(" ")}\t${JSON.stringify(c.turns[i].text)}`);
    }
  }
writeFileSync(`${OUT}/chat-diff.tsv`, lines.join("\n"));
// ---- G4: HFU synthetic set, same probes/templates as hfu.mts (read from its rows-b.json)
const B = JSON.parse(readFileSync(`${OUT}/rows-b.json`, "utf8"));
const asTurns = (t1: string) => [{ role: "user", text: t1 }];
let base = 0, lostBase = 0, lostFix = 0; const byForm: Record<string, number[]> = {}, byLang: Record<string, number[]> = {};
let nonBaseNew = 0;
const g4rows: any[] = [];
for (const r of B) {
  const sa = gets(route(r.text, [], false));
  const fb = gets(route(r.q, asTurns(r.t1), false)), ff = gets(route(r.q, asTurns(r.t1), true));
  if (!sa) { if (!fb && ff) nonBaseNew++; continue; }
  base++;
  if (!fb) lostBase++;
  if (!ff) lostFix++;
  const k = (m: Record<string, number[]>, key: string) => (m[key] ??= [0, 0, 0]);
  for (const [m, key] of [[byForm, r.form], [byLang, r.lang]] as const) { const a = k(m, key); a[0]++; if (!fb) a[1]++; if (!ff) a[2]++; }
  if (!ff) g4rows.push({ id: r.id, lang: r.lang, form: r.form, q: r.q, codes: route(r.q, asTurns(r.t1), true).codes });
}
const summary = { msgs, changed, newHealthRoutes: newHealth, convsNoHealthCondition: noCondConvs, changesInNoConditionConvs: noCondChanges, newHealthInNoConditionConvs: noCondNewHealth,
  g4: { baselineForms: base, lostBefore: lostBase, lostAfter: lostFix, recovered: lostBase - lostFix, byForm_base_lostBefore_lostAfter: byForm, byLang_base_lostBefore_lostAfter: byLang, nonBaselineFormsNewlyRouted: nonBaseNew } };
writeFileSync(`${OUT}/hfufix-summary.json`, JSON.stringify(summary, null, 1));
writeFileSync(`${OUT}/hfufix-g4-remaining.json`, JSON.stringify(g4rows, null, 1));
console.log(JSON.stringify(summary, null, 1));
