// DEEPBO2 scorer (criterion sha256 c7e2232f...). Conventions = arms/deepvpara/tools/paired.mjs: judge-core combineOrders
// per item (disagreement = tie), ratio = Σboar/Σref rubric means (summarize), floor-adjusted = Σ(boar−1)/Σ(ref−1),
// paired Δ with items resampled jointly, bootstrapCI 2000 boots (ratio seed 5, floor seed 7; floorAdj CI seed 3).
// Picked set: per id, the Opus judgment pair (both orders) of the chosen seed (fallback = s42).
// node score.mjs <S1.picks.json | oracle | anti-oracle | s42 | s43 | longer | cites> ...   (no args = all baselines)
// Writes aggregates/score-<name>.json (+ baselines-summary.json when baselines run). Prints one JSON line per name.
import fs from "node:fs";
import path from "node:path";
const { combineOrders, summarize, meanScore, bootstrapCI } = await import("<workspace>/boar-eval/scorers/vendor/eval-lib/judge-core.mjs");
const HERE = path.dirname(new URL(import.meta.url).pathname);
const ROOT = path.resolve(HERE, "../../../../../..");
const B = path.join(ROOT, "blind/V-para"), AGG = path.join(HERE, "../aggregates");
const rd = (p) => fs.readFileSync(p, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
const want = new Set(fs.readFileSync(path.join(B, "runs-cut6/judged.ids"), "utf8").split("\n").filter(Boolean));
function pairs(p) {
  const by = {}; const rows = rd(p).filter((r) => r.ok && want.has(r.queryId));
  for (const r of rows) (by[r.queryId] ??= {})[r.order] = r.mapped;
  return Object.fromEntries(Object.entries(by).filter(([, o]) => o.boarA && o.boarB).map(([id, o]) => [id, { id, ...combineOrders(o.boarA, o.boarB) }]));
}
const J = { s42: pairs(path.join(B, "runs-dt512/dh-H-vpara-s42.judgments.jsonl")), s43: pairs(path.join(B, "runs-dt512/dh-H-vpara-s43.judgments.jsonl")) };
const ids = [...want].filter((id) => J.s42[id] && J.s43[id]).sort();
if (ids.length !== want.size) throw new Error(`missing judged pairs: ${want.size - ids.length}`);
// numeric fields only from pairs.jsonl (text never leaves this process)
const meta = Object.fromEntries(rd(path.join(B, "runs-deepbo2/pairs.jsonl")).map((r) => [r.id, { lenA: r.lenA, lenB: r.lenB, citesA: r.citesA, citesB: r.citesB }]));
const ratio = (ps) => ps.reduce((a, p) => a + meanScore(p.boar), 0) / ps.reduce((a, p) => a + meanScore(p.ref), 0);
const floorAdj = (ps) => ps.reduce((a, p) => a + meanScore(p.boar) - 1, 0) / ps.reduce((a, p) => a + meanScore(p.ref) - 1, 0);
const sc = (id, s) => meanScore(J[s][id].boar);
const oracleStrict = Object.fromEntries(ids.map((id) => [id, sc(id, "s42") > sc(id, "s43") ? "s42" : sc(id, "s43") > sc(id, "s42") ? "s43" : null]));
const BASE = {
  s42: () => "s42", s43: () => "s43",
  oracle: (id) => (sc(id, "s43") > sc(id, "s42") ? "s43" : "s42"),
  "anti-oracle": (id) => (sc(id, "s43") < sc(id, "s42") ? "s43" : "s42"),
  longer: (id) => (meta[id].lenB > meta[id].lenA ? "s43" : "s42"),
  cites: (id) => { const m = meta[id]; return m.citesB > m.citesA ? "s43" : m.citesB < m.citesA ? "s42" : BASE.longer(id); },
};
const eff = (p) => (p === "s43" ? "s43" : "s42"); // fallback / missing = s42
const set = (pk) => ids.map((id) => J[eff(pk[id])][id]);
const refSets = { s42: set(Object.fromEntries(ids.map((i) => [i, "s42"]))), s43: set(Object.fromEntries(ids.map((i) => [i, "s43"]))),
  oracle: set(Object.fromEntries(ids.map((i) => [i, BASE.oracle(i)]))) };
function paired(ps, qs) {
  const joint = ps.map((a, k) => ({ a, b: qs[k] }));
  const dR = (xs) => ratio(xs.map((x) => x.a)) - ratio(xs.map((x) => x.b));
  const dF = (xs) => floorAdj(xs.map((x) => x.a)) - floorAdj(xs.map((x) => x.b));
  return { dRatio: dR(joint), dRatioCI: bootstrapCI(joint, dR, { seed: 5 }), dFloor: dF(joint), dFloorCI: bootstrapCI(joint, dF, { seed: 7 }) };
}
function score(name, pk, extra = {}) {
  const ps = set(pk), s = summarize(ps);
  const vs = Object.fromEntries(Object.entries(refSets).map(([k, q]) => [k, paired(ps, q)]));
  // Δ vs the expected single (mean of the two singles), items resampled jointly
  const tri = ps.map((a, k) => ({ a, b: refSets.s42[k], c: refSets.s43[k] }));
  const dE = (xs) => ratio(xs.map((x) => x.a)) - (ratio(xs.map((x) => x.b)) + ratio(xs.map((x) => x.c))) / 2;
  const dEF = (xs) => floorAdj(xs.map((x) => x.a)) - (floorAdj(xs.map((x) => x.b)) + floorAdj(xs.map((x) => x.c))) / 2;
  const strict = ids.filter((id) => oracleStrict[id]);
  const avg = (vs.s42.dRatio + vs.s43.dRatio) / 2;
  const both = vs.s42.dRatioCI[0] > 0 && vs.s43.dRatioCI[0] > 0;
  const out = { name, n: s.n, ratio: s.qualityRatio, ci: s.qualityRatioCI, floorAdj: floorAdj(ps), floorAdjCI: bootstrapCI(ps, floorAdj, { seed: 3 }),
    win: ps.filter((p) => p.winner === "boar").length, tie: ps.filter((p) => p.winner === "tie").length, loss: ps.filter((p) => p.winner === "ref").length,
    judgePosCons: s.positionConsistency,
    vsS42: vs.s42, vsS43: vs.s43, vsOracle: vs.oracle,
    vsExpectedSingle: { dRatio: dE(tri), dRatioCI: bootstrapCI(tri, dE, { seed: 5 }), dFloor: dEF(tri), dFloorCI: bootstrapCI(tri, dEF, { seed: 7 }) },
    avgDRatioVsSingles: avg, avgDFloorVsSingles: (vs.s42.dFloor + vs.s43.dFloor) / 2,
    oracleAgree: { nStrict: strict.length, agree: strict.filter((id) => eff(pk[id]) === oracleStrict[id]).length,
      rate: strict.filter((id) => eff(pk[id]) === oracleStrict[id]).length / strict.length },
    verdictRatio: both ? (avg >= 0.015 ? "USEFUL" : "WEAK") : "NO",
    nPick: { s42: ids.filter((i) => pk[i] === "s42").length, s43: ids.filter((i) => pk[i] === "s43").length, fallback: ids.filter((i) => pk[i] !== "s42" && pk[i] !== "s43").length },
    ...extra, picks: Object.fromEntries(ids.map((i) => [i, pk[i] ?? "fallback"])) };
  return out;
}
const r4 = (k, v) => (typeof v === "number" ? +v.toFixed(4) : v);
const args = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(BASE);
fs.mkdirSync(AGG, { recursive: true });
const done = {};
for (const a of args) {
  let name, pk, extra = {};
  if (a.endsWith(".json")) {
    const j = JSON.parse(fs.readFileSync(a, "utf8"));
    name = j.selector ?? path.basename(a).replace(/\.picks\.json$/, ""); pk = j.picks;
    extra = { positionConsistency: j.agreeRate, parseFailRate: j.parseFailRate, nCalls: j.nCalls, wallS: j.wallS, msMedian: j.msMedian,
      failInfra: j.parseFailRate > 0.10 };
  } else if (BASE[a]) { name = a; pk = Object.fromEntries(ids.map((i) => [i, BASE[a](i)])); extra = { positionConsistency: null }; }
  else throw new Error(`unknown selector ${a}`);
  const o = score(name, pk, extra); done[name] = o;
  fs.writeFileSync(path.join(AGG, `score-${name}.json`), JSON.stringify(o, r4, 1));
  const { picks, ...line } = o;
  console.log(JSON.stringify({ name, ratio: o.ratio, ci: o.ci, floorAdj: o.floorAdj, floorAdjCI: o.floorAdjCI, wtl: [o.win, o.tie, o.loss],
    dVsS42: [o.vsS42.dRatio, ...o.vsS42.dRatioCI], dVsS43: [o.vsS43.dRatio, ...o.vsS43.dRatioCI], dVsOracle: [o.vsOracle.dRatio, ...o.vsOracle.dRatioCI],
    dFloorVsS42: [o.vsS42.dFloor, ...o.vsS42.dFloorCI], dFloorVsS43: [o.vsS43.dFloor, ...o.vsS43.dFloorCI], avgD: o.avgDRatioVsSingles,
    oracleAgree: o.oracleAgree.rate, posCons: o.positionConsistency ?? null, verdict: o.verdictRatio, nPick: o.nPick }, r4));
}
const baseNames = Object.keys(BASE).filter((k) => done[k]);
if (baseNames.length === Object.keys(BASE).length) {
  const summ = { criterionSha256: "c7e2232f34f9c34c8d5168aa0ac87a0a7bed515dbf95c84284ccb8145c34ed11", n: ids.length,
    expectedSingle: { ratio: (done.s42.ratio + done.s43.ratio) / 2, floorAdj: (done.s42.floorAdj + done.s43.floorAdj) / 2 },
    oracleStrictItems: ids.filter((i) => oracleStrict[i]).length,
    baselines: Object.fromEntries(baseNames.map((k) => { const { picks, ...o } = done[k]; return [k, o]; })) };
  fs.writeFileSync(path.join(AGG, "baselines-summary.json"), JSON.stringify(summ, r4, 1));
  console.log(JSON.stringify({ expectedSingle: summ.expectedSingle, oracleStrictItems: summ.oracleStrictItems }, r4));
}
