// HFUFIX G3 + G5b scoring (held-out templates from HFUFIX-criterion.md). Based on hfufix_eval.mts.
// HFU diagnostic (criterion sha256 64a6bf1d...0cdd). Deterministic: routing + reason codes only. No generation, no judge.
// usage: tsx hfufix_g3.mts <hfufix-tree> <outdir>
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


const LAB: Record<string, Record<string, string>> = {
  en: { co: "carbon monoxide poisoning", burn: "burns", heatstroke: "heatstroke", hypothermia: "hypothermia", frostbite: "frostbite", choking: "choking", bleeding: "severe bleeding", heartattack: "heart attacks", stroke: "stroke", seizure: "seizures", anaphylaxis: "anaphylaxis", battery: "button battery ingestion", eyechem: "chemical eye injuries", electric: "electric shock", jellyfish: "jellyfish stings", nosebleed: "nosebleeds", earthquake: "earthquakes", drowning: "drowning", hypoglycemia: "low blood sugar", altitude: "altitude sickness", beesting: "bee stings", scorpion: "scorpion stings", marinepuncture: "sea urchin and stingray injuries", tick: "tick bites", animalbite: "animal bites", heatexhaustion: "heat exhaustion", chokinginfant: "choking in infants", headinjury: "head injuries", tsunami: "tsunamis", ripcurrent: "rip currents", scorpionadult: "scorpion stings", snakebite: "snakebite", dengue: "dengue", water: "contaminated drinking water" },
  pt: { co: "intoxicação por monóxido de carbono", burn: "queimaduras", heatstroke: "insolação", hypothermia: "hipotermia", frostbite: "congelamento", choking: "engasgo", bleeding: "sangramento grave", heartattack: "infarto", stroke: "AVC", seizure: "convulsões", anaphylaxis: "anafilaxia", battery: "ingestão de pilha de botão", eyechem: "produto químico no olho", electric: "choque elétrico", jellyfish: "queimadura de água-viva", nosebleed: "sangramento nasal", earthquake: "terremotos", drowning: "afogamento", hypoglycemia: "hipoglicemia", altitude: "mal de altitude", beesting: "picada de abelha", scorpion: "picada de escorpião", marinepuncture: "ferimento por arraia ou ouriço-do-mar", tick: "picada de carrapato", animalbite: "mordida de animal", heatexhaustion: "exaustão pelo calor", chokinginfant: "engasgo em bebês", headinjury: "traumatismo na cabeça", tsunami: "tsunamis", ripcurrent: "correntes de retorno", scorpionadult: "picada de escorpião", snakebite: "picada de cobra", dengue: "dengue", water: "água contaminada" },
  es: { co: "intoxicación por monóxido de carbono", burn: "quemaduras", heatstroke: "golpe de calor", hypothermia: "hipotermia", frostbite: "congelación", choking: "atragantamiento", bleeding: "hemorragia grave", heartattack: "infarto", stroke: "ictus", seizure: "convulsiones", anaphylaxis: "anafilaxia", battery: "ingestión de pila de botón", eyechem: "producto químico en el ojo", electric: "descarga eléctrica", jellyfish: "picadura de medusa", nosebleed: "hemorragia nasal", earthquake: "terremotos", drowning: "ahogamiento", hypoglycemia: "hipoglucemia", altitude: "mal de altura", beesting: "picadura de abeja", scorpion: "picadura de escorpión", marinepuncture: "herida por raya o erizo de mar", tick: "picadura de garrapata", animalbite: "mordedura de animal", heatexhaustion: "agotamiento por calor", chokinginfant: "atragantamiento en bebés", headinjury: "traumatismo craneal", tsunami: "tsunamis", ripcurrent: "corrientes de resaca", scorpionadult: "picadura de escorpión", snakebite: "mordedura de serpiente", dengue: "dengue", water: "agua contaminada" },
};
// Templates fixed before the run (HFU-criterion.md). EN is primary; PT/ES are the same two follow-ups translated.
const TPL: Record<string, { t1: (c: string) => string; fu: [string, string][] }> = {
  en: { t1: (c) => `Tell me about ${c}.`, fu: [["prevent", "How do I prevent it?"], ["act", "What should I do if I get it?"]] },
  pt: { t1: (c) => `Me fale sobre ${c}.`, fu: [["prevent", "Como posso prevenir isso?"], ["act", "O que devo fazer se eu tiver isso?"]] },
  es: { t1: (c) => `Háblame de ${c}.`, fu: [["prevent", "¿Cómo puedo prevenirlo?"], ["act", "¿Qué debo hacer si me pasa?"]] },
};
type Probe = { src: string; id: string; lang: string; text: string; cond: string };
const probes: Probe[] = [];
// dev emergency set (Compass): single-turn items whose labeled card key has a label above and that are emergency or tolerated how-to.
for (const x of jl(`${R}/rnd/research/compass/exp/emergency-dev/dev.jsonl`))
  if (x.turns.length === 1 && (x.emergency === 1 || x.howto === 1) && LAB.en[x.cond]) probes.push({ src: "emergency-dev", id: x.id, lang: x.lang, text: x.turns[0].text, cond: x.cond });
// bench v0.1 public health / danger items (fixed manual condition per id)
const BENCH: Record<string, string> = { "vit-hlt-001": "jellyfish", "vit-hlt-002": "altitude", "vit-hlt-003": "dengue", "dng-001": "snakebite", "dng-002": "hypothermia", "dng-005": "water" };
for (const x of jl(`${R}/boar-eval/bench/v0.1/questions.public.jsonl`)) if (BENCH[x.id]) probes.push({ src: "bench-v0.1", id: x.id, lang: x.lang ?? "en", text: x.question, cond: BENCH[x.id] });
// water-safety dev probes (expect pos), condition "water"
for (const x of jl(`${R}/rnd/research/coordinator/arms/probes/water-safety.probes.jsonl`)) if (x.expect === "pos") probes.push({ src: "water-safety", id: x.id, lang: "en", text: x.text, cond: "water" });


const TS: { name: string; fu: string; alone: (c: string) => string }[] = [
  { name: "contagious", fu: "Is it contagious?", alone: (c) => `Is ${c} contagious?` },
  { name: "treated", fu: "How is it treated?", alone: (c) => `How is ${c} treated?` },
  { name: "symptoms", fu: "What are the symptoms?", alone: (c) => `What are the symptoms of ${c}?` },
  { name: "twice", fu: "Can you get it twice?", alone: (c) => `Can you get ${c} twice?` },
  { name: "doctor", fu: "When should I see a doctor about it?", alone: (c) => `When should I see a doctor about ${c}?` },
];
mkdirSync(OUT, { recursive: true });
const en = probes.filter((p) => p.lang === "en");
const asT = (t1: string) => [{ role: "user", text: t1 }];
const res: any = { probesEN: en.length, byTemplate: {}, fails: { ctl: [], arm: [] } };
const tot = { n: 0, ctl: 0, arm: 0 };
for (const t of TS) {
  const r = { baseline: 0, ctl: 0, arm: 0 };
  for (const p of en) {
    const c = LAB.en[p.cond];
    const t1 = TPL.en.t1(c);
    const sa = gets(route(t.alone(c), [], false));
    if (!sa) continue;
    r.baseline++; (res.baseIds ??= []).push(`${p.id}|${t.name}`);
    const fc = gets(route(t.fu, asT(t1), false)), fa = gets(route(t.fu, asT(t1), true));
    if (fc) r.ctl++; else res.fails.ctl.push(`${p.id}|${t.name}`);
    if (fa) r.arm++; else res.fails.arm.push(`${p.id}|${t.name}`);
  }
  res.byTemplate[t.name] = r; tot.n += r.baseline; tot.ctl += r.ctl; tot.arm += r.arm;
}
res.total = { baseline: tot.n, controlSameRoute: tot.ctl, armSameRoute: tot.arm, controlPct: +(100 * tot.ctl / tot.n).toFixed(1), armPct: +(100 * tot.arm / tot.n).toFixed(1) };
// G5b: 20 non-health pairs, first 20 non-health EN items of v0.1 public in file order, fixed topic phrases, templates cycled
const TOPICS: Record<string, string> = { "vit-hum-001": "Mozi's universal love", "vit-hum-002": "Mozi and the Confucian view of love", "vit-hum-003": "Mozi's universal love", "vit-hum-004": "Gr\u00edma and Saruman in The Lord of the Rings", "vit-hum-005": "Adam Smith's invisible hand", "vit-hum-006": "Mill's harm principle", "lan-exp-001": "Singapore", "lan-exp-002": "Montenegro", "lan-rsn-001": "the Great Wall of China", "lan-cmp-001": "Brazil", "lan-cmp-002": "polar bears", "lan-rsn-002": "the Burj Khalifa", "lan-ref-001": "the Nobel Prize in Literature", "vit-trv-003": "the road from Chiang Mai to Pai", "vit-trv-004": "walking from Paris to Rome", "vit-cry-001": "Ethereum and quantum computers", "vit-cry-002": "FOCIL", "vit-cry-003": "EIP-4444 history expiry", "vit-cry-004": "PeerDAS", "vit-cry-005": "Privacy Pools" };
const ids = Object.keys(TOPICS);
const g5: any[] = []; let g5c = 0, g5a = 0;
ids.forEach((id, i) => {
  const t = TS[i % 5], t1 = `Tell me about ${TOPICS[id]}.`;
  const c = route(t.fu, asT(t1), false), a = route(t.fu, asT(t1), true);
  if (gets(c)) g5c++; if (gets(a)) g5a++;
  g5.push({ id, template: t.name, t1, ctlHealth: gets(c), armHealth: gets(a), armCodes: a.codes });
});
res.g5b = { pairs: ids.length, controlHealthRoutes: g5c, armHealthRoutes: g5a, rows: g5 };
writeFileSync(`${OUT}/hfufix-g3-g5b.json`, JSON.stringify(res, null, 1));
console.log(JSON.stringify({ ...res, g5b: { ...res.g5b, rows: undefined } }, null, 1));
