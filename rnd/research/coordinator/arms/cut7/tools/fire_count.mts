/**
 * CUT7 fire count (deterministic, no model, no judge; scoped blind exception in CUT7-criterion.md 2d430a70).
 * Runs the cut 7 engine's FACTS instant path with the same wired condition as answer.ts / arms/facts/tools/facts_check.mts
 * (not PT/ES, not isHealthQuestion/isCardEmergency, then factsAnswer(query); the learned detector is not simulated, so
 * this is an upper bound that the cut 7 traces confirm) over the exact queries the cut 6 claim runs fed the runner
 * (requests files, item.question), restricted to the run's item set.
 * PRINTS ONLY: per set, total, fired count, fired ids, template, entity ids, FACTS answer text. Never a question text.
 * Usage: tsx fire_count.mts <tree> <outV02.json> <outVpara.json> <out.md>
 */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";
const [tree, outV02, outVp, outMd] = process.argv.slice(2);
const BL = "<workspace>/blind";
const { factsAnswer } = await import(`${tree}/src/rag/facts.ts`);
const { isPortugueseQuestion, isSpanishQuestion, isHealthQuestion } = await import(`${tree}/src/routing/context.ts`);
const { isCardEmergency } = await import(`${tree}/src/routing/conditionCards.ts`);
const wired = (q: string) => (isPortugueseQuestion(q) || isSpanishQuestion(q) || isHealthQuestion(q) || isCardEmergency(q) ? null : factsAnswer(q));
const jl = (p: string) => readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const shipIds = new Set(readFileSync(`${BL}/bench-v02/runs-ship/ship-all.en.ids`, "utf8").split("\n").map((s) => s.trim()).filter(Boolean));
const v02New = new Set(jl(`${BL}/bench-v02/live/v0.2/questions.v02-new.jsonl`).map((r) => r.id));
type Res = { set: string; source: string; total: number; fired: number; firedIds: string[]; rows: { id: string; template: string; entities: string[]; answer: string }[] };
const runSet = (set: string, reqFile: string, keep: (id: string) => boolean): Res => {
  const reqs = jl(reqFile).filter((r) => keep(r.item.id));
  const rows = [] as Res["rows"];
  for (const r of reqs) { const a = wired(r.item.question); if (a) rows.push({ id: r.item.id, template: a.template, entities: a.entities ?? [], answer: a.text }); }
  rows.sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
  return { set, source: reqFile.replace(BL + "/", "blind/"), total: reqs.length, fired: rows.length, firedIds: rows.map((x) => x.id), rows };
};
const sameQ = (a: string, b: string) => { // the two seeds must feed identical queries (compared in-process, nothing printed)
  const m = new Map(jl(a).map((r) => [r.item.id, r.item.question])); return jl(b).every((r) => m.get(r.item.id) === r.item.question);
};
const C6 = `${BL}/bench-v02/runs-cut6`, VP = `${BL}/V-para/runs-cut6`;
const checks = {
  v02SeedsSameQueries: sameQ(`${C6}/cut6-v02-s42.requests.jsonl`, `${C6}/cut6-v02-s43.requests.jsonl`),
  v01SeedsSameQueries: sameQ(`${C6}/cut6-v01-s42.requests.jsonl`, `${C6}/cut6-v01-s43.requests.jsonl`),
  vparaSeedsSameQueries: sameQ(`${VP}/cut6-vpara-s42.requests.jsonl`, `${VP}/cut6-vpara-s43.requests.jsonl`),
};
const v02 = runSet("v0.2-new held-out (Run A)", `${C6}/cut6-v02-s42.requests.jsonl`, (id) => v02New.has(id) && shipIds.has(id));
const v01 = runSet("v0.1 public + safety track (Run A, 72)", `${C6}/cut6-v01-s42.requests.jsonl`, () => true);
const vp = runSet("V-para (Run B, 58)", `${VP}/cut6-vpara-s42.requests.jsonl`, () => true);
for (const [p, o] of [[outV02, { checks, sets: [v02, v01] }], [outVp, { checks, sets: [vp] }]] as const) { mkdirSync(dirname(p), { recursive: true }); writeFileSync(p, JSON.stringify(o, null, 1) + "\n"); }
const md = [`# CUT7 fire count (tools/fire_count.mts, tree ${tree}; queries = cut 6 claim-run requests s42; seed queries identical: ${JSON.stringify(checks)})`, ""];
for (const s of [v02, v01, vp]) {
  md.push(`## ${s.set}: fired ${s.fired} / ${s.total}`, `source: ${s.source}`, "");
  if (s.rows.length) { md.push("| id | template | entities | FACTS answer text |", "|---|---|---|---|"); for (const r of s.rows) md.push(`| ${r.id} | ${r.template} | ${r.entities.join(",")} | ${r.answer.replace(/\|/g, "\\|").replace(/\n/g, " ")} |`); md.push(""); }
}
writeFileSync(outMd, md.join("\n") + "\n");
console.log(md.join("\n"));
