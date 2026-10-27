// DEEPVPARA paired analysis (arms/deepread/analyze.mjs conventions: judge-core combineOrders/summarize, orders combined per item,
// disagreement = tie; ratio = Σboar/Σref rubric means; floor-adjusted = Σ(boar−1)/Σ(ref−1) [analyze.mjs]; paired Δ with items
// resampled jointly, bootstrapCI 2000 boots). Prints aggregates + ids only.
// node paired.mjs <A.judgments> <B.judgments> <ids file> <nameA> <nameB> [A.traces] [--floor-missing] [--strict]
// Fail-closed (FAILCLOSED-2026-10-11): always prints "n judged = X of n planned = Y" (+ the ids) on stderr. Default stdout is unchanged (ids are
// intersected). --floor-missing keeps every planned id: an arm with no complete judgment pair for an id gets boar = 1/1/1 (rubric floor) and the
// reference scores of the other arm's pair for that id (else the arm's mean reference score), winner = ref; adds out.floorMissing. --strict: exit 1 if any id is unjudged (without --floor-missing).
// --common-mode <sigmaRaw>[,<sigmaFloor>] (optional; output is byte-identical without it): adds run-level noise to the item-bootstrap CI. SE_item = (CIhigh-CIlow)/(2*1.96);
// single arm: est +/- 1.96*sqrt(SE_item^2 + s^2) [ratioCIcm, floorAdjCIcm]; paired delta: +/- 1.96*sqrt(SE_item^2 + 2*s^2) (two independent runs) [dRatioCIcm, dFloorCIcm]; s = sigmaFloor (default sigmaRaw).
import fs from "node:fs";
const { combineOrders, summarize, meanScore, bootstrapCI } = await import("<workspace>/boar-eval/scorers/vendor/eval-lib/judge-core.mjs");
const rd = (p) => fs.readFileSync(p, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
const FLAGS = process.argv.slice(2).filter((x) => x.startsWith("--")), FLOOR_MISSING = FLAGS.includes("--floor-missing"), STRICT = FLAGS.includes("--strict");
const CMI = process.argv.indexOf("--common-mode"), CMARG = CMI >= 0 ? process.argv[CMI + 1] : null;
if (CMI >= 0 && !/^\d*\.?\d+(,\d*\.?\d+)?$/.test(CMARG ?? "")) { console.error("--common-mode needs <sigmaRaw>[,<sigmaFloor>] (non-negative numbers)"); process.exit(2); }
const CM = CMARG ? (([r, f]) => ({ sigmaRaw: +r, sigmaFloor: f === undefined ? +r : +f }))(CMARG.split(",")) : null;
const [ap, bp, idf, na, nb] = process.argv.slice(2).filter((x, i, a) => !x.startsWith("--") && a[i - 1] !== "--common-mode");
const want = new Set(fs.readFileSync(idf, "utf8").split("\n").filter(Boolean));
function pairs(p) {
  const by = {}; const rows = rd(p).filter((r) => r.ok && want.has(r.queryId));
  for (const r of rows) (by[r.queryId] ??= {})[r.order] = r.mapped;
  return Object.fromEntries(Object.entries(by).filter(([, o]) => o.boarA && o.boarB).map(([id, o]) => [id, { id, ...combineOrders(o.boarA, o.boarB) }]));
}
const A = pairs(ap), B = pairs(bp);
const missing0 = { [na]: [...want].filter((i) => !A[i]), [nb]: [...want].filter((i) => !B[i]) };
let ids = [...want].filter((id) => A[id] && B[id]).sort();
const planned = [...want].sort(), unjudged = planned.filter((id) => !ids.includes(id));
console.error(`n judged = ${ids.length} of n planned = ${planned.length}` + (unjudged.length ? ` | not judged in both arms (${FLOOR_MISSING ? "scored at the rubric floor" : "dropped"}): ${unjudged.join(",")}` : ""));
if (STRICT && !FLOOR_MISSING && unjudged.length) { console.log(JSON.stringify({ error: "unjudged ids", unjudged })); process.exit(1); }
const floorMissing = {};
if (FLOOR_MISSING && unjudged.length) {
  const K = ["correctness", "completeness", "usefulness"], meanRef = (P) => { const v = Object.values(P); return Object.fromEntries(K.map((k) => [k, v.length ? v.reduce((a, p) => a + p.ref[k], 0) / v.length : 5])); };
  for (const [name, P, Q] of [[na, A, B], [nb, B, A]]) {
    const mr = meanRef(P); floorMissing[name] = [];
    for (const id of unjudged) if (!P[id]) { P[id] = { id, winner: "ref", consistent: true, boar: Object.fromEntries(K.map((k) => [k, 1])), ref: Q[id]?.ref ?? mr, floorScored: true }; floorMissing[name].push(id); }
  }
  ids = planned;
}
const ratio = (ps) => ps.reduce((a, p) => a + meanScore(p.boar), 0) / ps.reduce((a, p) => a + meanScore(p.ref), 0);
const floorAdj = (ps) => ps.reduce((a, p) => a + meanScore(p.boar) - 1, 0) / ps.reduce((a, p) => a + meanScore(p.ref) - 1, 0);
const out = { ...(FLOOR_MISSING ? { floorMissing } : {}), missing: missing0 };
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
if (CM) {
  const se = (ci) => (ci[1] - ci[0]) / (2 * 1.96), cm = (est, ci, sg, k) => { const h = 1.96 * Math.sqrt(se(ci) ** 2 + k * sg ** 2); return [est - h, est + h]; };
  for (const [name, P] of [[na, A], [nb, B]]) { const ps = ids.map((i) => P[i]); out[name].ratioCIcm = cm(out[name].ratio, out[name].ci, CM.sigmaRaw, 1); out[name].floorAdjCIcm = cm(floorAdj(ps), out[name].floorAdjCI, CM.sigmaFloor, 1); }
  out.paired.dRatioCIcm = cm(out.paired.dRatio, out.paired.dRatioCI, CM.sigmaRaw, 2); out.paired.dFloorCIcm = cm(out.paired.dFloor, out.paired.dFloorCI, CM.sigmaFloor, 2);
  out.paired.commonMode = { ...CM, seItemRaw: se(out.paired.dRatioCI), seItemFloor: se(out.paired.dFloorCI) };
}
out.perItem = rows;
console.log(JSON.stringify(out, (k, v) => (typeof v === "number" ? +v.toFixed(4) : v), 1));
