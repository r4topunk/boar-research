// DETFU diagnostic (criterion sha256 bc79a821...6cda76618). Routing only, generation stubbed, REAL learned detector (llama-server mmbert v3b on the Mac mini via ssh tunnel to 127.0.0.1:8094).
// usage: BOAR_DETECTOR_URL=http://127.0.0.1:8094 tsx detfu.mts <engine-tree> <outdir>
// Detector call = adapters/desktop-node/runner/adapter.ts emergencyScore (detectorText(userTurns, query) -> /embedding norm -1 -> mmbertProbability), threshold = DETECTOR_THRESHOLD (0.2).
// Route = answer.ts health decision with `learned` present: lexicalHealth = fire || (p >= DETECTOR_FLOOR && isHealthQuestion); health = lexicalHealth || isHealthFollowUp || cardEmergency; plus early cards (snakebite / CO hazard / emergency numbers).
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
const T = process.argv[2], OUT = process.argv[3];
const R = "<workspace>";
const URL_ = process.env.BOAR_DETECTOR_URL!;
const ctx = await import(`${T}/src/routing/context.ts`);
const cc = await import(`${T}/src/routing/conditionCards.ts`);
const EH: any = await import(`${T}/src/routing/emergencyHead.ts`);
const { isSnakebiteFirstAid } = await import(`${T}/src/routing/firstAidCards.ts`);
const { isCoHazardQuestion } = await import(`${T}/src/routing/coHazard.ts`);
const { emergencyNumbersAnswer } = await import(`${T}/src/routing/emergencyNumbers.ts`);
const { smallTalkReply } = await import(`${T}/src/routing/smallTalk.ts`);
const head = JSON.parse(readFileSync(`${R}/shared-models/emergency-detector/sonar-mmbert-small-emergency-v3b.head.json`, "utf8"));
const post = async (path: string, body: any) => { const r = await fetch(`${URL_}${path}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) }); if (!r.ok) throw new Error(`${path} ${r.status}`); return r.json() as any; };
const countTokens = async (content: string) => (await post("/tokenize", { content, add_special: false })).tokens.length;
const embed = async (content: string): Promise<number[]> => { const j = await post("/embedding", { content, embd_normalize: -1 }); const e = Array.isArray(j) ? j[0].embedding : j.embedding; return Array.isArray(e[0]) ? e[0] : e; };
const score = async (q: string, turns: string[]) => { const p = EH.mmbertProbability(head, await embed(await EH.detectorText(turns, q, countTokens))); return { p, fire: p >= EH.DETECTOR_THRESHOLD }; };

async function route(query: string, userTurns: string[]) {
  const learned = await score(query, userTurns);
  const codes: string[] = [`detector:p=${learned.p.toFixed(3)}`, ...(learned.fire ? ["detector:fire"] : [])];
  const pt = ctx.isPortugueseQuestion(query), es = !pt && ctx.isSpanishQuestion(query);
  let early: string | null = null;
  if (isSnakebiteFirstAid(query)) early = "answer:first-aid-card-snakebite";
  else if (!pt && !es && isCoHazardQuestion(query)) early = "answer:safety-fact-co-hazard";
  else if (emergencyNumbersAnswer(query, pt)) early = "answer:emergency-numbers";
  else if (!learned.fire && smallTalkReply(query, pt, new Date("2026-10-06T12:00:00"))) early = "answer:small-talk";
  const lex = learned.fire || (learned.p >= EH.DETECTOR_FLOOR && ctx.isHealthQuestion(query));
  const fu = ctx.isHealthFollowUp(query, userTurns);
  const cardEm = !lex && !fu && cc.isCardEmergency(query);
  const health = lex || fu || cardEm;
  if (lex) codes.push(learned.fire ? "health:detector-fire" : "health:lexical+floor");
  if (fu) codes.push("grounding:health-follow-up");
  if (cardEm) codes.push("grounding:health-card-condition");
  const c = cc.conversationCondition(query, userTurns);
  if (c.condition) codes.push(`condition:${c.condition}${c.fromHistory ? ":from-history" : ""}`);
  if (early) codes.unshift(early);
  return { health, early, p: learned.p, fire: learned.fire, codes };
}
const gets = (r: any) => r.health || (!!r.early && r.early !== "answer:small-talk");
const jl = (p: string) => readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
type Probe = { src: string; id: string; text: string };
const probes: Probe[] = [];
for (const x of jl(`${R}/rnd/research/compass/exp/emergency-dev/dev.jsonl`)) if (x.lang === "en" && x.emergency === 1 && x.turns.length === 1) probes.push({ src: "emergency-dev", id: x.id, text: x.turns[0].text });
const DANGER = ["dng-001", "dng-002", "dng-005", "vit-hlt-001", "vit-hlt-002"];
for (const x of jl(`${R}/boar-eval/bench/v0.1/questions.public.jsonl`)) if (DANGER.includes(x.id)) probes.push({ src: "bench-v0.1", id: x.id, text: x.question });
for (const f of ["probes.jsonl", "probes2.jsonl"]) for (const x of jl(`${R}/rnd/research/sonar/exp/37-co-symptomatic/${f}`)) if (x.expect === "co" && x.turns.length === 1) probes.push({ src: "sonar-exp37", id: x.id, text: x.turns[0] });
const rows: any[] = [];
for (const p of probes) {
  const alone = await route(p.text, []);
  if (!gets(alone)) { rows.push({ ...p, base: false, alone }); continue; }
  const s1 = await route("What should I do now?", [p.text]);
  const s2 = await route("It's getting worse.", [p.text]);
  const s3 = await route(p.text, ["Hi, quick question."]);
  rows.push({ ...p, base: true, alone, s1, s2, s3 });
}
const base = rows.filter((r) => r.base);
const lost = (k: string) => base.filter((r) => !gets(r[k]));
const sum = { probes: probes.length, standaloneEmergency: base.length, S1_lost: lost("s1").length, S2_lost: lost("s2").length, S3_mismatch: base.filter((r) => gets(r.s3) !== gets(r.alone) || r.s3.early !== r.alone.early).length };
mkdirSync(OUT, { recursive: true });
writeFileSync(`${OUT}/rows.json`, JSON.stringify(rows, null, 1));
writeFileSync(`${OUT}/summary.json`, JSON.stringify(sum, null, 1));
const L = ["form\tid\tstandalone codes\tturn-2 codes\tdetector p (turn 2)\tstandalone p"];
for (const k of ["s1", "s2", "s3"]) for (const r of base) if (k === "s3" ? (gets(r.s3) !== gets(r.alone) || r.s3.early !== r.alone.early) : !gets(r[k])) L.push(`${k.toUpperCase()}\t${r.src}:${r.id}\t${r.alone.codes.join(" ")}\t${r[k].codes.join(" ")}\t${r[k].p.toFixed(3)}\t${r.alone.p.toFixed(3)}`);
writeFileSync(`${OUT}/losses.tsv`, L.join("\n"));
console.log(JSON.stringify(sum));
