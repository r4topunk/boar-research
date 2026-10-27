// Renders the exact judge.v1 prompts judge-codex.mjs would send for the 4 rungs x 51 ids x 2 orders (no call).
import { readFileSync, writeFileSync } from "node:fs";
const LIB = "<workspace>/boar-eval/scorers/vendor/eval-lib/judge-core.mjs";
const { JUDGE_SYSTEM, VERDICT_SCHEMA, RUBRIC, blind, firstOrders, judgePrompt } = await import(LIB);
const W = process.argv[2] ?? (new URL(".", import.meta.url).pathname); const BE = "<workspace>/boar-eval/bench/v0.1/";
const jl = (p) => readFileSync(p, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
const want = new Set(readFileSync(W + "in/ids51.txt", "utf8").split("\n").filter(Boolean));
const questions = jl(BE + "questions.public.jsonl");
const ref = Object.fromEntries(jl(BE + "refs/refs.jsonl").filter((r) => r.ok).map((r) => [r.id, r]));
writeFileSync(W + "prompt/judge-system.txt", JUDGE_SYSTEM + "\n");
writeFileSync(W + "prompt/verdict-schema.json", JSON.stringify(VERDICT_SCHEMA, null, 1) + "\n");
writeFileSync(W + "prompt/rubric.json", JSON.stringify(RUBRIC, null, 1) + "\n");
let total = 0;
for (const rung of ["L0_15B_closedbook", "L1_17B_K0_s42", "L2_GemmaE2B_desk_s42", "L3_4B_phone_cut7"]) {
  const tr = Object.fromEntries(jl(W + `in/traces/${rung}.traces.jsonl`).map((t) => [t.itemId, t]));
  const ids = questions.map((q) => q.id).filter((id) => want.has(id) && questions.find((q) => q.id === id).grading?.type !== "venue-list" && tr[id] && ref[id]);
  const first = firstOrders(ids, 7); const rows = [];
  for (const id of ids) {
    const q = questions.find((x) => x.id === id); const notes = (q.rubric ?? []).join(" / ");
    for (const order of first[id] === "boarA" ? ["boarA", "boarB"] : ["boarB", "boarA"]) {
      const boarIsA = order === "boarA";
      const [answerA, answerB] = boarIsA ? [blind(tr[id].answer.text), blind(ref[id].answer)] : [blind(ref[id].answer), blind(tr[id].answer.text)];
      rows.push({ rung, queryId: id, order, boarIsA, prompt: judgePrompt({ question: q.question, notes, answerA, answerB }) });
    }
  }
  writeFileSync(W + `prompt/rendered-${rung}.jsonl`, rows.map((r) => JSON.stringify(r) + "\n").join(""));
  console.log(rung, ids.length, rows.length); total += rows.length;
}
console.log("total prompts", total);
