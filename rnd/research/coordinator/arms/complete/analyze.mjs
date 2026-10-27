// COMPLETE analysis (Kiln): DEEPREAD's analyze.mjs (same summarize() on combined orders, floor-adjusted ratio, paired bootstrap)
// with the comparator = DEEPREAD deep35-R450 instead of the 4B. Added: per-item paired Δ incl. correctness, confident-wrong
// (combined correctness ≤ 2 and not a decline, bench precheck.refused) before/after, median words, decode s per item.
// node analyze.mjs <complete.judgments> <deepread.judgments> <complete.traces> <deepread.traces>
import fs from "node:fs";
import { execFileSync } from "node:child_process";
const LIB = "<workspace>/boar-eval/scorers/vendor/eval-lib/judge-core.mjs";
const { combineOrders, summarize, meanScore, bootstrapCI } = await import(LIB);
const rd = (p) => fs.readFileSync(p, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
function pairs(p) {
  const by = {};
  for (const r of rd(p).filter((r) => r.ok)) (by[r.queryId] ??= {})[r.order] = r.mapped;
  return Object.fromEntries(Object.entries(by).filter(([, o]) => o.boarA && o.boarB).map(([id, o]) => [id, { id, ...combineOrders(o.boarA, o.boarB) }]));
}
const [dp, fp, tp, tfp] = process.argv.slice(2);
const D = pairs(dp), F = pairs(fp);
const ids = Object.keys(D).filter((id) => F[id]).sort();
const fmt = (x) => x.toFixed(3);
const floorAdj = (ps) => ps.reduce((a, p) => a + meanScore(p.boar) - 1, 0) / ps.reduce((a, p) => a + meanScore(p.ref) - 1, 0);
const ratio = (ps) => ps.reduce((a, p) => a + meanScore(p.boar), 0) / ps.reduce((a, p) => a + meanScore(p.ref), 0);
const out = {};
for (const [name, P] of [["complete", D], ["deepread", F]]) {
  const ps = Object.values(P), s = summarize(ps);
  out[name] = { n: s.n, ratio: s.qualityRatio, ci: s.qualityRatioCI, win: s.boarWin, tie: s.tie, loss: s.refWin, winScore: s.winScore, posCons: s.positionConsistency,
    rubricBoar: s.rubricBoar, rubricRef: s.rubricRef, floorAdj: floorAdj(ps), floorAdjCI: bootstrapCI(ps, floorAdj, { seed: 3 }) };
}
const joint = ids.map((id) => ({ d: D[id], f: F[id] }));
const dRatio = (xs) => ratio(xs.map((x) => x.d)) - ratio(xs.map((x) => x.f));
const dFloor = (xs) => floorAdj(xs.map((x) => x.d)) - floorAdj(xs.map((x) => x.f));
out.paired = { n: ids.length, dRatio: dRatio(joint), dRatioCI: bootstrapCI(joint, dRatio, { seed: 5 }), dFloor: dFloor(joint), dFloorCI: bootstrapCI(joint, dFloor, { seed: 7 }) };
const TC = new Map(rd(tp).map((t) => [t.itemId, t])), TF = new Map(rd(tfp).map((t) => [t.itemId, t]));
const decl = (p) => JSON.parse(execFileSync("python3", ["-I", new URL("./declines.py", import.meta.url).pathname, p], { encoding: "utf8" }));
const DC = decl(tp), DF = decl(tfp);
const words = (t) => (t?.answer.text ?? "").split(/\s+/).filter(Boolean).length;
const rows = ids.map((id) => ({ id, sd: meanScore(D[id].boar), sf: meanScore(F[id].boar), dS: meanScore(D[id].boar) - meanScore(F[id].boar), wd: D[id].winner, wf: F[id].winner,
  cd: D[id].boar.correctness, cf: F[id].boar.correctness, cmd: D[id].boar.completeness, cmf: F[id].boar.completeness,
  wordsD: words(TC.get(id)), wordsF: words(TF.get(id)), declD: DC[id], declF: DF[id],
  decodeSD: (TC.get(id)?.timing.decodeMs ?? 0) / 1000, decodeSF: (TF.get(id)?.timing.decodeMs ?? 0) / 1000, finishD: TC.get(id)?.route.finishReason }));
const cw = (k, dk) => rows.filter((r) => r[k] <= 2 && !r[dk]).map((r) => r.id);
out.confidentWrong = { complete: cw("cd", "declD"), deepread: cw("cf", "declF") };
out.confidentWrong.nComplete = out.confidentWrong.complete.length; out.confidentWrong.nDeepread = out.confidentWrong.deepread.length;
out.declines = { complete: rows.filter((r) => r.declD).map((r) => r.id), deepread: rows.filter((r) => r.declF).map((r) => r.id) };
const mean = (a) => a.reduce((x, y) => x + y, 0) / a.length;
const medA = (a) => { const s = [...a].sort((x, y) => x - y); return s.length % 2 ? s[(s.length - 1) / 2] : (s[s.length / 2 - 1] + s[s.length / 2]) / 2; };
out.correctness = { complete: mean(rows.map((r) => r.cd)), deepread: mean(rows.map((r) => r.cf)) }; out.correctness.delta = out.correctness.complete - out.correctness.deepread;
out.words = { medComplete: medA(rows.map((r) => r.wordsD)), medDeepread: medA(rows.map((r) => r.wordsF)), meanComplete: mean(rows.map((r) => r.wordsD)), meanDeepread: mean(rows.map((r) => r.wordsF)),
  in120to220: rows.filter((r) => r.wordsD >= 120 && r.wordsD <= 220).length };
out.decodeS = { medComplete: medA(rows.map((r) => r.decodeSD)), medDeepread: medA(rows.map((r) => r.decodeSF)), meanComplete: mean(rows.map((r) => r.decodeSD)), meanDeepread: mean(rows.map((r) => r.decodeSF)) };
out.finishLength = rows.filter((r) => r.finishD === "length").map((r) => r.id);
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
