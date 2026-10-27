// DEEPREAD analysis (Kiln): judge-core summarize() on combined orders; floor-adjusted ratio; paired Δ vs 4B R450 (bootstrap,
// items resampled jointly); converted / regressed items; speed + RSS from traces.  node analyze.mjs <deep.judgments> <4b.judgments> [deep.traces]
import fs from "node:fs";
const LIB = "<workspace>/boar-eval/scorers/vendor/eval-lib/judge-core.mjs";
const { combineOrders, summarize, meanScore, bootstrapCI } = await import(LIB);
const rd = (p) => fs.readFileSync(p, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
function pairs(p) {
  const by = {};
  for (const r of rd(p).filter((r) => r.ok)) (by[r.queryId] ??= {})[r.order] = r.mapped;
  return Object.fromEntries(Object.entries(by).filter(([, o]) => o.boarA && o.boarB).map(([id, o]) => [id, { id, ...combineOrders(o.boarA, o.boarB) }]));
}
const [dp, fp, tp] = process.argv.slice(2);
const D = pairs(dp), F = pairs(fp);
const ids = Object.keys(D).filter((id) => F[id]).sort();
const fmt = (x) => x.toFixed(3);
const floorAdj = (ps) => ps.reduce((a, p) => a + meanScore(p.boar) - 1, 0) / ps.reduce((a, p) => a + meanScore(p.ref) - 1, 0);
const ratio = (ps) => ps.reduce((a, p) => a + meanScore(p.boar), 0) / ps.reduce((a, p) => a + meanScore(p.ref), 0);
const out = {};
for (const [name, P] of [["deep35", D], ["4b", F]]) {
  const ps = Object.values(P), s = summarize(ps);
  out[name] = { n: s.n, ratio: s.qualityRatio, ci: s.qualityRatioCI, win: s.boarWin, tie: s.tie, loss: s.refWin, winScore: s.winScore, posCons: s.positionConsistency,
    rubricBoar: s.rubricBoar, rubricRef: s.rubricRef, floorAdj: floorAdj(ps), floorAdjCI: bootstrapCI(ps, floorAdj, { seed: 3 }) };
}
const joint = ids.map((id) => ({ d: D[id], f: F[id] }));
const dRatio = (xs) => ratio(xs.map((x) => x.d)) - ratio(xs.map((x) => x.f));
const dFloor = (xs) => floorAdj(xs.map((x) => x.d)) - floorAdj(xs.map((x) => x.f));
out.paired = { n: ids.length, dRatio: dRatio(joint), dRatioCI: bootstrapCI(joint, dRatio, { seed: 5 }), dFloor: dFloor(joint), dFloorCI: bootstrapCI(joint, dFloor, { seed: 7 }) };
const rows = ids.map((id) => ({ id, sd: meanScore(D[id].boar), sf: meanScore(F[id].boar), wd: D[id].winner, wf: F[id].winner }));
out.converted = rows.filter((r) => r.sd >= 4 && r.sf <= 2);
out.regressed = rows.filter((r) => r.sf >= 4 && r.sd <= 2);
out.perItem = rows;
out.better = rows.filter((r) => r.sd > r.sf).length; out.worse = rows.filter((r) => r.sd < r.sf).length; out.same = rows.filter((r) => r.sd === r.sf).length;
if (tp) {
  const t = rd(tp); const med = (a) => { const s = [...a].filter((x) => x != null).sort((x, y) => x - y); return s.length ? s[Math.floor((s.length - 1) / 2)] : null; };
  const sum = (k) => t.reduce((a, x) => a + (x.timing[k] ?? 0), 0);
  out.speed = { n: t.length, errors: t.filter((x) => x.error).length, reasoningTokens: sum("reasoningTokens"),
    finish: t.reduce((a, x) => ((a[x.route.finishReason] = (a[x.route.finishReason] ?? 0) + 1), a), {}),
    decodeTokSAgg: sum("outputTokens") / (sum("decodeMs") / 1000), prefillTokSAgg: sum("promptTokens") / (sum("prefillMs") / 1000),
    decodeMed: med(t.map((x) => x.timing.decodeTokPerSec)), prefillMed: med(t.map((x) => x.timing.prefillTokPerSec)),
    promptTokMed: med(t.map((x) => x.timing.promptTokens)), outTokMed: med(t.map((x) => x.timing.outputTokens)),
    ttftMed: med(t.map((x) => x.timing.ttftMs)), totalMed: med(t.map((x) => x.timing.totalMs)), totalSumS: sum("totalMs") / 1000,
    peakRssMb: Math.max(...t.map((x) => x.resources?.peakRssMb ?? 0)), modelLoadMs: t[0]?.timing.modelLoadMs };
}
console.log(JSON.stringify(out, (k, v) => (typeof v === "number" ? +v.toFixed(4) : v), 1));
