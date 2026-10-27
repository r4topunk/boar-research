// DEEPVPARA paired analysis (arms/deepread/analyze.mjs conventions: judge-core combineOrders/summarize, orders combined per item,
// disagreement = tie; ratio = Σboar/Σref rubric means; floor-adjusted = Σ(boar−1)/Σ(ref−1) [analyze.mjs]; paired Δ with items
// resampled jointly, bootstrapCI 2000 boots). Prints aggregates + ids only.
// node paired.mjs <A.judgments> <B.judgments> <ids file> <nameA> <nameB> [A.traces]
import fs from "node:fs";
const { combineOrders, summarize, meanScore, bootstrapCI } = await import("<workspace>/boar-eval/scorers/vendor/eval-lib/judge-core.mjs");
const rd = (p) => fs.readFileSync(p, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
const [ap, bp, idf, na, nb] = process.argv.slice(2);
const want = new Set(fs.readFileSync(idf, "utf8").split("\n").filter(Boolean));
function pairs(p) {
  const by = {}; const rows = rd(p).filter((r) => r.ok && want.has(r.queryId));
  for (const r of rows) (by[r.queryId] ??= {})[r.order] = r.mapped;
  return Object.fromEntries(Object.entries(by).filter(([, o]) => o.boarA && o.boarB).map(([id, o]) => [id, { id, ...combineOrders(o.boarA, o.boarB) }]));
}
const A = pairs(ap), B = pairs(bp);
const ids = [...want].filter((id) => A[id] && B[id]).sort();
const ratio = (ps) => ps.reduce((a, p) => a + meanScore(p.boar), 0) / ps.reduce((a, p) => a + meanScore(p.ref), 0);
const floorAdj = (ps) => ps.reduce((a, p) => a + meanScore(p.boar) - 1, 0) / ps.reduce((a, p) => a + meanScore(p.ref) - 1, 0);
const out = { missing: { [na]: [...want].filter((i) => !A[i]), [nb]: [...want].filter((i) => !B[i]) } };
for (const [name, P] of [[na, A], [nb, B]]) {
  const ps = ids.map((i) => P[i]), s = summarize(ps);
  out[name] = { n: s.n, ratio: s.qualityRatio, ci: s.qualityRatioCI, win: s.boarWin, tie: s.tie, loss: s.refWin, posCons: s.positionConsistency,
    floorAdj: floorAdj(ps), floorAdjCI: bootstrapCI(ps, floorAdj, { seed: 3 }),
    winRateCI: bootstrapCI(ps, (xs) => xs.filter((p) => p.winner === "boar").length / xs.length, { seed: 9 }) };
}
const joint = ids.map((id) => ({ a: A[id], b: B[id] }));
const dR = (xs) => ratio(xs.map((x) => x.a)) - ratio(xs.map((x) => x.b));
const dF = (xs) => floorAdj(xs.map((x) => x.a)) - floorAdj(xs.map((x) => x.b));
// L1 rule (L1-PROTOCOL): per item, the arm's winner vs the reference over both orders (combineOrders: disagreement = tie);
// "wins" = items whose combined winner is boar. Head-to-head by combined rubric mean (sa vs sb) is descriptive only.
const rows = ids.map((id) => ({ id, wa: A[id].winner, wb: B[id].winner, sa: meanScore(A[id].boar), sb: meanScore(B[id].boar) }));
out.paired = { n: ids.length, dRatio: dR(joint), dRatioCI: bootstrapCI(joint, dR, { seed: 5 }), dFloor: dF(joint), dFloorCI: bootstrapCI(joint, dF, { seed: 7 }),
  winsVsRef: { [na]: rows.filter((r) => r.wa === "boar").length, [nb]: rows.filter((r) => r.wb === "boar").length },
  tiesVsRef: { [na]: rows.filter((r) => r.wa === "tie").length, [nb]: rows.filter((r) => r.wb === "tie").length },
  lossesVsRef: { [na]: rows.filter((r) => r.wa === "ref").length, [nb]: rows.filter((r) => r.wb === "ref").length },
  headToHead: { aHigher: rows.filter((r) => r.sa > r.sb).length, same: rows.filter((r) => r.sa === r.sb).length, bHigher: rows.filter((r) => r.sa < r.sb).length } };
out.perItem = rows;
console.log(JSON.stringify(out, (k, v) => (typeof v === "number" ? +v.toFixed(4) : v), 1));
