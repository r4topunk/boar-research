#!/usr/bin/env node
// Plumb: aggregates the vitalik-lantern judge + precheck + hand labels into the numbers the report needs.
// Usage: node rnd/plumb/analyze.mjs <eval dir> <system> [out.json] [hand-labels.json]
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const [evalDir, system, outJson, handPath] = process.argv.slice(2);
const { combineOrders, summarize, meanScore } = await import(join(evalDir, "scripts/lib/judge-core.mjs"));
const jl = (p) => readFileSync(p, "utf8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
const DS = "vitalik-lantern";
const qs = Object.fromEntries(jl(join(evalDir, "dataset", `questions.${DS}.jsonl`)).map((q) => [q.id, q]));
const runs = Object.fromEntries(jl(join(evalDir, "results/runs", DS, `${system}.jsonl`)).map((r) => [r.queryId, r]));
const subset = (s) => new Set(JSON.parse(readFileSync(join(evalDir, "dataset", `subset.${s}.${DS}.json`), "utf8")).ids);
const hand = JSON.parse(readFileSync(handPath ?? new URL("./data/hand-labels-run2.json", import.meta.url), "utf8"));

// One combined pair per question (both A/B orders), like report.mjs.
const byQ = {};
for (const j of jl(join(evalDir, "results/judgments", DS, `${system}__vs__claude-code__opus.jsonl`)).filter((j) => j.ok)) (byQ[j.queryId] ??= {})[j.order] = j;
const pairs = Object.entries(byQ)
  .filter(([, o]) => o.boarA && o.boarB)
  .map(([queryId, o]) => ({ queryId, category: qs[queryId].category, rationale: [o.boarA.verdict, o.boarB.verdict], ...combineOrders(o.boarA.mapped, o.boarB.mapped) }));

const fmt = (x) => (Number.isFinite(x) ? x.toFixed(2) : "–");
const pct = (x) => (Number.isFinite(x) ? `${Math.round(x * 100)}%` : "–");
function block(ps) {
  if (!ps.length) return null;
  const s = summarize(ps, { seed: 11 });
  return {
    n: ps.length,
    ratio: s.qualityRatio, ci: s.qualityRatioCI,
    correct: ps.filter((p) => p.boar.correctness >= 4).length / ps.length,
    refCorrect: ps.filter((p) => p.ref.correctness >= 4).length / ps.length,
    // Judge proxy for confident-wrong: answered (not declined) and correctness <= 2.
    judgeWrongAnswered: ps.filter((p) => !runs[p.queryId]?.declined && p.boar.correctness <= 2).length / ps.length,
    declined: ps.filter((p) => runs[p.queryId]?.declined).length / ps.length,
    win: s.boarWin, tie: s.tie, loss: s.refWin, posConsistency: s.positionConsistency,
  };
}
const out = { system, subsets: {}, categories: {}, worst: [], judgeVsHand: null };
for (const s of ["factual", "device", "competitor-app"]) {
  const ids = subset(s);
  out.subsets[s] = block(pairs.filter((p) => ids.has(p.queryId)));
  if (out.subsets[s]) out.subsets[s].missingJudged = [...ids].filter((i) => !pairs.find((p) => p.queryId === i));
}
const dev = subset("device");
for (const c of [...new Set(pairs.map((p) => p.category))].sort()) out.categories[c] = block(pairs.filter((p) => p.category === c && dev.has(p.queryId)));

// Worst: lowest BOAR mean rubric among ANSWERED (non-declined) rows; declines are a separate failure mode.
out.worst = pairs
  .filter((p) => dev.has(p.queryId) && !runs[p.queryId]?.declined)
  .map((p) => ({ id: p.queryId, category: p.category, query: qs[p.queryId].query, boarMean: meanScore(p.boar), correctness: p.boar.correctness, answer: runs[p.queryId].answer, hand: hand[p.queryId], rationale: p.rationale }))
  .sort((a, b) => a.correctness - b.correctness || a.boarMean - b.boarMean)
  .slice(0, 8);

// Judge (correctness >= 4) vs hand label (pass) on answered rows.
const answered = pairs.filter((p) => hand[p.queryId] && p.queryId !== "_about");
out.judgeVsHand = {
  n: answered.length,
  agree: answered.filter((p) => (p.boar.correctness >= 4) === (hand[p.queryId][0] === "pass")).length,
  handCwJudgeCorrectness: answered.filter((p) => hand[p.queryId][0] === "cw").map((p) => [p.queryId, p.boar.correctness]),
};

for (const [k, v] of Object.entries(out.subsets)) if (v) console.log(`${k}\tn=${v.n}\tratio=${fmt(v.ratio)} (${fmt(v.ci[0])}-${fmt(v.ci[1])})\tcorrect=${pct(v.correct)} ref=${pct(v.refCorrect)}\tdeclined=${pct(v.declined)}\tjudge-wrong-answered=${pct(v.judgeWrongAnswered)}\tW/T/L=${pct(v.win)}/${pct(v.tie)}/${pct(v.loss)}\tpos=${pct(v.posConsistency)}\tmissing=${v.missingJudged.join(",")}`);
for (const [k, v] of Object.entries(out.categories)) console.log(`cat ${k}\tn=${v.n}\tratio=${fmt(v.ratio)} (${fmt(v.ci[0])}-${fmt(v.ci[1])})\tcorrect=${pct(v.correct)}\tdeclined=${pct(v.declined)}`);
for (const w of out.worst) console.log(`worst ${w.id}\tcorr=${w.correctness}\tmean=${fmt(w.boarMean)}\thand=${w.hand?.[0]}\t${w.query}`);
console.log("judge vs hand", JSON.stringify(out.judgeVsHand));
if (outJson) writeFileSync(outJson, JSON.stringify(out, null, 1));
