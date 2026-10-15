// DETMAX G3/G4/G5 scoring (criterion sha256 a7c784af...2328). Routing only, generation stubbed, REAL learned detector (llama-server mmbert v3b on the Mac mini via ssh tunnel to 127.0.0.1:8094).
// usage: BOAR_DETECTOR_URL=http://127.0.0.1:8094 tsx detmax.mts <engine-tree> <outdir>
// Detector call = adapters/desktop-node/runner/adapter.ts emergencyScore (detectorText(userTurns, query) -> /embedding norm -1 -> mmbertProbability), threshold = DETECTOR_THRESHOLD (0.2).
// Route = answer.ts health decision with `learned` present: lexicalHealth = fire || (p >= DETECTOR_FLOOR && isHealthQuestion); health = lexicalHealth || isHealthFollowUp || cardEmergency; plus early cards (snakebite / CO hazard / emergency numbers).
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
const T = process.argv[2], OUT = process.argv[3];
const R = "$BOAR_WS";
const URL_ = process.env.BOAR_DETECTOR_URL!;
const ctx = await import(`${T}/src/routing/context.ts`);
const cc = await import(`${T}/src/routing/conditionCards.ts`);
const EH: any = await import(`${T}/src/routing/emergencyHead.ts`);
const { isSnakebiteFirstAid } = await import(`${T}/src/routing/firstAidCards.ts`);
const { isCoHazardQuestion } = await import(`${T}/src/routing/coHazard.ts`);
const { emergencyNumbersAnswer } = await import(`${T}/src/routing/emergencyNumbers.ts`);
const { smallTalkReply } = await import(`${T}/src/routing/smallTalk.ts`);
const head = JSON.parse(readFileSync(`${R}/shared-models/emergency-detector/mmbert-small-emergency-v3b.head.json`, "utf8"));
const post = async (path: string, body: any) => { const r = await fetch(`${URL_}${path}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) }); if (!r.ok) throw new Error(`${path} ${r.status}`); return r.json() as any; };
const countTokens = async (content: string) => (await post("/tokenize", { content, add_special: false })).tokens.length;
const embed = async (content: string): Promise<number[]> => { const j = await post("/embedding", { content, embd_normalize: -1 }); const e = Array.isArray(j) ? j[0].embedding : j.embedding; return Array.isArray(e[0]) ? e[0] : e; };
const score = async (q: string, turns: string[]) => { const p = EH.mmbertProbability(head, await embed(await EH.detectorText(turns, q, countTokens))); return { p, fire: p >= EH.DETECTOR_THRESHOLD }; };

let calls = 0, callMs = 0;
async function scoreT(q: string, turns: string[]) { const t = performance.now(); const r = await score(q, turns); callMs += performance.now() - t; calls++; return r; }
// arm = answer.ts DETMAX rule: with earlier user turns, also score the turn alone and take max p / either fire
async function route(query: string, userTurns: string[], arm: boolean) {
  let learned = await scoreT(query, userTurns);
  if (arm && userTurns.length) { const a = await scoreT(query, []); learned = { p: Math.max(learned.p, a.p), fire: learned.fire || a.fire }; }
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
for (const x of jl(`${R}/rnd/research/agent-notes/exp/emergency-dev/dev.jsonl`)) if (x.lang === "en" && x.emergency === 1 && x.turns.length === 1) probes.push({ src: "emergency-dev", id: x.id, text: x.turns[0].text });
const DANGER = ["dng-001", "dng-002", "dng-005", "vit-hlt-001", "vit-hlt-002"];
for (const x of jl(`${R}/boar-eval/bench/v0.1/questions.public.jsonl`)) if (DANGER.includes(x.id)) probes.push({ src: "bench-v0.1", id: x.id, text: x.question });
for (const f of ["probes.jsonl", "probes2.jsonl"]) for (const x of jl(`${R}/rnd/research/agent-notes/exp/37-co-symptomatic/${f}`)) if (x.expect === "co" && x.turns.length === 1) probes.push({ src: "agent-exp37", id: x.id, text: x.turns[0] });
mkdirSync(OUT, { recursive: true });
const PREFIXES = ["Hi, quick question.", "Thanks for the help earlier.", "Different topic now.", "Ok so I have another question."];
const res: any = { g3: {}, g4: {}, g5: {} };
const base: any[] = [];
for (const p of probes) { const a = await route(p.text, [], false); if (gets(a)) base.push({ ...p, alone: a }); }
res.g3.baseline = base.length;
const mism: any[] = [];
for (const [pi, pre] of PREFIXES.entries()) {
  let c = 0, a = 0;
  for (const b of base) {
    const rc = await route(b.text, [pre], false), ra = await route(b.text, [pre], true);
    const same = (r: any) => gets(r) === gets(b.alone) && r.early === b.alone.early;
    if (!same(rc)) c++;
    if (!same(ra)) { a++; mism.push({ prefix: pre, id: b.id, aloneP: b.alone.p, ctlP: rc.p, armP: ra.p, armCodes: ra.codes }); }
  }
  res.g3[pi === 0 ? "S3 (DETFU prefix)" : `held-out P${pi}`] = { prefix: pre, controlMismatches: c, armMismatches: a, of: base.length };
}
res.g3.armMismatchRows = mism;
// G4: 192 dev chat messages (all user turns of the 192 conversations, history = earlier turns) control vs arm, with the real detector
const slices = [["chat-v0", `${R}/rnd/research/agent-notes/chat-slice/slice.v0.jsonl`], ["chat-v1", `${R}/rnd/research/agent-notes/chat-slice/v1-fresh/slice.v1.jsonl`], ["chat-v2", `${R}/rnd/research/agent-notes/chat-slice/v2-fresh/slice.v2.jsonl`]];
const added: any[] = []; let msgs = 0, withHist = 0, changedAny = 0; let c0 = calls, ms0 = callMs;
let ctlCalls = 0, armCalls = 0, armMs = 0;
for (const [set, p] of slices) for (const c of jl(p)) {
  const users: string[] = c.turns.filter((t: any) => t.role === "user").map((t: any) => t.text);
  for (let i = 0; i < users.length; i++) {
    msgs++; const prev = users.slice(0, i); if (prev.length) withHist++;
    let k = calls; const rc = await route(users[i], prev, false); ctlCalls += calls - k;
    k = calls; const t0 = callMs; const ra = await route(users[i], prev, true); armCalls += calls - k; armMs += callMs - t0;
    if (JSON.stringify(rc.codes) !== JSON.stringify(ra.codes) || gets(rc) !== gets(ra)) {
      changedAny++;
      const alone = await route(users[i], [], false);
      added.push({ set, id: c.id, turn: i, text: users[i], routeAdded: !gets(rc) && gets(ra), ctl: rc.codes, arm: ra.codes, standaloneRoutes: gets(alone), standaloneFire: alone.fire });
    }
  }
}
res.g4 = { userTurns: msgs, withHistory: withHist, changed: changedAny, routesAdded: added.filter((x) => x.routeAdded).length, rows: added };
res.g5 = { armDetectorCallsOnChat: armCalls, controlDetectorCallsOnChat: ctlCalls, extraCalls: armCalls - ctlCalls, turnsWithHistory: withHist, desktopMsPerCallMean: +(callMs / calls).toFixed(1) };
writeFileSync(`${OUT}/detmax-result.json`, JSON.stringify(res, null, 1));
console.log(JSON.stringify({ g3: { ...res.g3, armMismatchRows: res.g3.armMismatchRows.length }, g4: { ...res.g4, rows: undefined }, g5: res.g5 }, null, 1));
