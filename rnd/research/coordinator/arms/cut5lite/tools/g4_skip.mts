// CUT5-SPEED G4: deterministic gate-skip safety check on dev data only (no blind/, no rnd/veil/).
// usage: tsx g4_skip.mts <engine-tree> > g4-output.txt
// Detector fire is not simulated (needs the model); the lexical emergency/safety guard is applied as in answer.ts (isCardEmergency || isSafetyQuery). history = earlier turns of the item.
import { readFileSync } from "node:fs";
const T = process.argv[2];
const R = "<workspace>";
const { classifyTask } = await import(`${T}/src/routing/classify.ts`);
const { routeGateSkip } = await import(`${T}/src/routing/routeGate.ts`);
const { smallTalkReply } = await import(`${T}/src/routing/smallTalk.ts`);
const { isCardEmergency } = await import(`${T}/src/routing/conditionCards.ts`);
const { isSafetyQuery, isPortugueseQuestion } = await import(`${T}/src/routing/context.ts`);
type Row = { set: string; id: string; text: string; turns: number; kind: string; mustNotSkip: boolean; why: string };
const rows: Row[] = [];
const jl = (p: string) => readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
for (const [name, p] of [
  ["chat-v0", `${R}/rnd/research/compass/chat-slice/slice.v0.jsonl`],
  ["chat-v1", `${R}/rnd/research/compass/chat-slice/v1-fresh/slice.v1.jsonl`],
  ["chat-v2", `${R}/rnd/research/compass/chat-slice/v2-fresh/slice.v2.jsonl`],
] as const)
  for (const r of jl(p)) {
    const last = r.turns[r.turns.length - 1].text;
    const exp = /emergen|safety|danger|first.?aid|hazard|urgent|call (911|112|192)/i.test(r.expected ?? "");
    const no = r.expected_search === "no";
    rows.push({ set: name, id: r.id, text: last, turns: r.turns.length - 1, kind: r.kind, mustNotSkip: no || r.kind === "meta" || r.kind === "greeting" || exp, why: [no ? "expected_search=no" : "", r.kind === "meta" ? "meta" : "", exp ? "emergency/safety" : ""].filter(Boolean).join("+") });
  }
for (const r of jl(`${R}/boar-eval/bench/v0.1/questions.public.jsonl`)) rows.push({ set: "bench-v0.1", id: r.id, text: r.question, turns: r.history?.turns?.length ?? 0, kind: r.category, mustNotSkip: !!r.danger, why: r.danger ? "danger" : "" });
for (const [name, p, key] of [
  ["probe-vg", `${R}/rnd/research/coordinator/arms/probes/vg-questions.probes.jsonl`, "text"],
  ["probe-water", `${R}/rnd/research/coordinator/arms/probes/water-safety.probes.jsonl`, "text"],
  ["probe-water-held", `${R}/rnd/research/coordinator/arms/probes/water-safety.heldout.jsonl`, "text"],
  ["probe-arith", `${R}/rnd/research/coordinator/arms/probes/arithmetic.probes.jsonl`, "text"],
  ["probe-travelfood", `${R}/rnd/research/sonar/exp/39-travel-food-probes/probes.jsonl`, "question"],
] as const)
  for (const r of jl(p)) rows.push({ set: name, id: r.id, text: r[key], turns: 0, kind: r.expect ?? "", mustNotSkip: name.startsWith("probe-water") && r.expect === "pos", why: name.startsWith("probe-water") && r.expect === "pos" ? "water-safety (expect pos)" : "" });
let skipped = 0, viol = 0;
const bySet: Record<string, [number, number]> = {};
const out: string[] = [];
for (const r of rows) {
  const pt = isPortugueseQuestion(r.text);
  const rule = classifyTask(r.text);
  const st = smallTalkReply(r.text, pt, new Date("2026-10-06T12:00:00"));
  const emergency = isCardEmergency(r.text) || isSafetyQuery(r.text); // as answer.ts
  const skip = routeGateSkip({ ruleTaskType: rule, query: r.text, historyTurns: r.turns, detectorFired: false, emergencyLexical: emergency });
  // Small talk caught by smallTalkReply never reaches the gate (answered earlier), but a skip there would still be a violation.
  const bad = skip && (r.mustNotSkip || !!st);
  (bySet[r.set] ??= [0, 0])[0]++;
  if (skip) { skipped++; bySet[r.set][1]++; out.push(`${bad ? "VIOLATION" : "skip"}\t${r.set}\t${r.id}\t${rule}\t${r.kind}\t${JSON.stringify(r.text)}`); }
  if (bad) viol++;
}
console.log(`messages ${rows.length}, skipped ${skipped}, violations ${viol}`);
for (const [k, [n, s]] of Object.entries(bySet)) console.log(`  ${k}: ${n} messages, ${s} skipped`);
console.log("\nverdict\tset\tid\trule\tkind\ttext");
console.log(out.join("\n"));
