// LESPORT-L1 analysis (adapted from arms/deepread/analyze.mjs): judge-core summarize() on combined orders; floor-adjusted;
// paired Δ les−A and les−B (bootstrap, items resampled jointly, 2000 boots); per-item winner les vs A; speed from les traces.
// node analyze_l1.mjs <les.judgments> <A.judgments> <B.judgments> <les.traces> <A.traces> <items.csv>
import fs from "node:fs";
const LIB = "<workspace>/boar-eval/scorers/vendor/eval-lib/judge-core.mjs";
const { combineOrders, summarize, meanScore, bootstrapCI } = await import(LIB);
const rd = (p) => fs.readFileSync(p, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
function pairs(p) {
  const by = {};
  for (const r of rd(p).filter((r) => r.ok)) (by[r.queryId] ??= {})[r.order] = r.mapped;
  return Object.fromEntries(Object.entries(by).filter(([, o]) => o.boarA && o.boarB).map(([id, o]) => [id, { id, ...combineOrders(o.boarA, o.boarB) }]));
}
const [bp, ap, fp, bt, at, csvp] = process.argv.slice(2);
const S = { les: pairs(bp), A: pairs(ap), B: pairs(fp) };
const floorAdj = (ps) => ps.reduce((a, p) => a + meanScore(p.boar) - 1, 0) / ps.reduce((a, p) => a + meanScore(p.ref) - 1, 0);
const ratio = (ps) => ps.reduce((a, p) => a + meanScore(p.boar), 0) / ps.reduce((a, p) => a + meanScore(p.ref), 0);
const out = { okRows: rd(bp).filter((r) => r.ok).length, totalRows: rd(bp).length };
for (const [name, P] of Object.entries(S)) {
  const ps = Object.values(P), s = summarize(ps);
  out[name] = { n: s.n, ratio: s.qualityRatio, ci: s.qualityRatioCI, win: s.boarWin, tie: s.tie, loss: s.refWin, posCons: s.positionConsistency,
    rubricBoar: s.rubricBoar, rubricRef: s.rubricRef, floorAdj: floorAdj(ps), floorAdjCI: bootstrapCI(ps, floorAdj, { seed: 3 }) };
}
for (const ctl of ["A", "B"]) {
  const ids = Object.keys(S.les).filter((id) => S[ctl][id]).sort();
  const joint = ids.map((id) => ({ d: S.les[id], f: S[ctl][id] }));
  const dR = (xs) => ratio(xs.map((x) => x.d)) - ratio(xs.map((x) => x.f));
  const dF = (xs) => floorAdj(xs.map((x) => x.d)) - floorAdj(xs.map((x) => x.f));
  out[`paired_${ctl}`] = { n: ids.length, dRatio: dR(joint), dRatioCI: bootstrapCI(joint, dR, { seed: 5 }), dFloor: dF(joint), dFloorCI: bootstrapCI(joint, dF, { seed: 7 }) };
}
// per-item winner les vs A: compare combined mean scores of the two answers (each judged against the same ref);
// equal means = tie (combined orders already map order disagreement to tie inside each pair).
const ids = Object.keys(S.les).filter((id) => S.A[id]).sort();
const T = Object.fromEntries(rd(bt).map((t) => [t.itemId, t])), TA = Object.fromEntries(rd(at).map((t) => [t.itemId, t]));
const rows = ids.map((id) => {
  const b = meanScore(S.les[id].boar), a = meanScore(S.A[id].boar), f = S.B[id] ? meanScore(S.B[id].boar) : null;
  return { id, les: b, A: a, B: f, ref: meanScore(S.les[id].ref), winner_vs_A: b > a ? "les" : b < a ? "A" : "tie",
    les_tok_s: T[id]?.timing?.decodeTokPerSec, les_total_s: T[id]?.timing?.totalS, nprompt_les: T[id]?.timing?.promptTokens, nprompt_A: TA[id]?.timing?.promptTokens };
});
out.vsA = { les: rows.filter((r) => r.winner_vs_A === "les").length, tie: rows.filter((r) => r.winner_vs_A === "tie").length, A: rows.filter((r) => r.winner_vs_A === "A").length };
out.npromptEqual = rows.filter((r) => r.nprompt_les === r.nprompt_A).length;
fs.writeFileSync(csvp, "id,les_mean,A_mean,B_mean,ref_mean,winner_vs_A,les_tok_s,les_total_s\n" +
  rows.map((r) => [r.id, r.les, r.A, r.B, r.ref, r.winner_vs_A, r.les_tok_s, r.les_total_s].map((x) => (typeof x === "number" ? +x.toFixed(3) : x ?? "")).join(",")).join("\n") + "\n");
const med = (a) => { const s = a.filter((x) => x != null).sort((x, y) => x - y); return s.length ? s[Math.floor((s.length - 1) / 2)] : null; };
const tr = Object.values(T);
out.speed = { n: tr.length, errors: tr.filter((t) => t.error).length, prefillS: med(tr.map((t) => t.timing?.prefillS)), tokS: med(tr.map((t) => t.timing?.decodeTokPerSec)),
  totalS: med(tr.map((t) => t.timing?.totalS)), outTok: med(tr.map((t) => t.timing?.outputTokens)), totalSumS: tr.reduce((a, t) => a + (t.timing?.totalS ?? 0), 0),
  rssGiB: med(tr.map((t) => t.resources?.peakRssGiB)), footGiB: med(tr.map((t) => t.resources?.peakFootprintGiB)), rssMax: Math.max(...tr.map((t) => t.resources?.peakRssGiB ?? 0)), A_prefillS: med(Object.values(TA).map((t) => t.timing.prefillMs / 1000)), A_tokS: med(Object.values(TA).map((t) => t.timing.decodeTokPerSec)), A_totalS: med(Object.values(TA).map((t) => t.timing.totalMs / 1000)) };
console.log(JSON.stringify(out, (k, v) => (typeof v === "number" ? +v.toFixed(4) : v), 1));
