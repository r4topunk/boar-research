// HFU diagnostic (criterion sha256 64a6bf1d...0cdd). Deterministic: routing + reason codes only. No generation, no judge.
// usage: tsx hfu.mts <engine-tree> <outdir>
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

export type Route = { health: boolean; early: string | null; codes: string[]; task: string };
function route(query: string, userTurns: string[]): Route {
  const codes: string[] = [];
  const pt = ctx.isPortugueseQuestion(query);
  const es = !pt && ctx.isSpanishQuestion(query);
  let early: string | null = null;
  if (isSnakebiteFirstAid(query)) early = "answer:first-aid-card-snakebite";
  else if (!pt && !es && isCoHazardQuestion(query)) early = "answer:safety-fact-co-hazard";
  else if (emergencyNumbersAnswer(query, pt)) early = "answer:emergency-numbers";
  else if (smallTalkReply(query, pt, new Date("2026-10-06T12:00:00"))) early = "answer:small-talk";
  const lex = ctx.isHealthQuestion(query);
  const fu = ctx.isHealthFollowUp(query, userTurns);
  const cardEm = !lex && !fu && cc.isCardEmergency(query);
  const health = lex || fu || cardEm;
  if (lex) codes.push("health:lexical");
  if (cardEm) codes.push("grounding:health-card-condition");
  if (fu) codes.push("grounding:health-follow-up");
  const cond = cc.conversationCondition(query, userTurns);
  if (cond.condition) codes.push(`condition:${cond.condition}${cond.fromHistory ? ":from-history" : ""}`);
  if (ctx.isSafetyQuery(query)) codes.push("ui:safety-note");
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

// ---------- (a) chat slices v0-v2 ----------
export const KEYWORDS =
  "dengue|malaria|zika|fever|febre|fiebre|sick|ill(ness)?|disease|doen[çc]a|enfermedad|symptom|sintoma|s[íi]ntoma|doctor|m[ée]dico|hospital|medic(ine|ation)|rem[ée]dio|medicamento|vaccin|vacina|pain|dor\\b|dolor|injur|ferid|herida|bleed|sangr|burn|queimad|quemad|bite|bitten|picad|mordid|sting|poison|envenen|intoxic|allerg|alergi|asthma|asma|diabet|insulin|pregnan|gr[áa]vida|embarazada|heart|cora[çc][ãa]o|coraz[óo]n|stroke|avc|infarto|choking|engasg|drown|afog|hypotherm|hipotermia|heat ?stroke|insola|dehydrat|desidrat|first aid|primeiros socorros|primeros auxilios|emergenc|emerg[êe]ncia|ambulance|ambul[âa]ncia|snake|cobra|serpente|serpiente|scorpion|escorpi|jellyfish|tick\\b|carrapato|garrapata|health|sa[úu]de|salud|infection|infec[çc]|virus|v[íi]rus|bacteria|cancer|c[âa]ncer|toxic|overdose|suicid|crisis|crise|depress|anxiety|ansiedade|ansiedad|water (is )?(safe|contaminated)|[áa]gua (pot[áa]vel|contaminada)|boil";
const KW = new RegExp(`(^|[^\\p{L}])(${KEYWORDS})`, "iu");
const rowsA: any[] = [];
const slices: [string, string][] = [
  ["chat-v0", `${R}/rnd/research/compass/chat-slice/slice.v0.jsonl`],
  ["chat-v1", `${R}/rnd/research/compass/chat-slice/v1-fresh/slice.v1.jsonl`],
  ["chat-v2", `${R}/rnd/research/compass/chat-slice/v2-fresh/slice.v2.jsonl`],
];
let convTotal = 0, convHealth = 0;
for (const [set, p] of slices)
  for (const c of jl(p)) {
    convTotal++;
    const all = c.turns.map((t: any) => t.text).join(" \n ");
    if (!KW.test(all)) continue;
    convHealth++;
    const users: string[] = c.turns.filter((t: any) => t.role === "user").map((t: any) => t.text);
    if (users.length < 2) { rowsA.push({ set, id: c.id, kind: c.kind, single: true, turn: users[0], r: route(users[0], []) }); continue; }
    // standalone form = the first user turn alone; follow-up forms = each later user turn with the earlier user turns as history
    const first = route(users[0], []);
    for (let i = 1; i < users.length; i++) {
      const fu = route(users[i], users.slice(0, i));
      const alone = route(users[i], []);
      rowsA.push({ set, id: c.id, kind: c.kind, i, first: users[0], q: users[i], rFirst: first, rFu: fu, rAlone: alone });
    }
  }

// ---------- (b) synthetic pairs ----------
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

const rowsB: any[] = [];
for (const p of probes) {
  const L = TPL[p.lang] ? p.lang : "en";
  const t1 = TPL[L].t1(LAB[L][p.cond]);
  const rs = route(p.text, []);
  const rt1 = route(t1, []);
  for (const [form, q] of TPL[L].fu) rowsB.push({ ...p, form, t1, q, rStandalone: rs, rTurn1: rt1, rFu: route(q, [t1]) });
}

// ---------- outputs ----------
mkdirSync(OUT, { recursive: true });
writeFileSync(`${OUT}/rows-a.json`, JSON.stringify(rowsA, null, 1));
writeFileSync(`${OUT}/rows-b.json`, JSON.stringify(rowsB, null, 1));
const summary: any = { convTotal, convHealth, keywords: KEYWORDS, a: {}, b: {} };
// (a): counted follow-up forms = later user turns of health-keyword conversations whose FIRST user turn gets a health route; lost = the follow-up (with history) does not
const aFu = rowsA.filter((r) => !r.single);
const aBase = aFu.filter((r) => gets(r.rFirst));
const aLost = aBase.filter((r) => !gets(r.rFu));
summary.a = { followUpTurns: aFu.length, baseline: aBase.length, lost: aLost.length, singleTurnHealthConvs: rowsA.filter((r) => r.single).length };
// (b)
const bBase = rowsB.filter((r) => gets(r.rStandalone));
const bLost = bBase.filter((r) => !gets(r.rFu));
const by = (rows: any[], f: (r: any) => string) => { const m: Record<string, number> = {}; for (const r of rows) m[f(r)] = (m[f(r)] ?? 0) + 1; return m; };
summary.b = { probes: probes.length, followUpForms: rowsB.length, standaloneHealth: bBase.length, lost: bLost.length, turn1Health: rowsB.filter((r) => gets(r.rTurn1)).length, byLangBase: by(bBase, (r) => r.lang), byLangLost: by(bLost, (r) => r.lang), byFormBase: by(bBase, (r) => r.form), byFormLost: by(bLost, (r) => r.form), fuRoutedViaFollowUp: bBase.filter((r) => r.rFu.codes.includes("grounding:health-follow-up")).length };
writeFileSync(`${OUT}/summary.json`, JSON.stringify(summary, null, 1));
const fmt = (c: string[]) => c.join(" ");
const lines: string[] = ["### (a) chat-slice losses", "set\tid\tturn\tfirst-turn codes\tfollow-up codes\tfollow-up text"];
for (const r of aLost) lines.push(`${r.set}\t${r.id}\t${r.i}\t${fmt(r.rFirst.codes)}\t${fmt(r.rFu.codes)}\t${JSON.stringify(r.q)}`);
lines.push("", "### (b) synthetic losses", "src\tid\tlang\tform\tstandalone codes\tfollow-up codes\tfollow-up text\tturn1");
for (const r of bLost) lines.push(`${r.src}\t${r.id}\t${r.lang}\t${r.form}\t${fmt(r.rStandalone.codes)}\t${fmt(r.rFu.codes)}\t${JSON.stringify(r.q)}\t${JSON.stringify(r.t1)}`);
writeFileSync(`${OUT}/losses.tsv`, lines.join("\n"));
console.log(JSON.stringify(summary, null, 1));
