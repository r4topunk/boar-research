// SEEDVAR analysis (numbers only): per-seed ratio/floor/win, pairwise paired Δ between seeds, mean/SD across seeds, per-item Pearson r.
// node seedvar.mjs <ids file> <label> <judgments…>   (judge-core conventions as deepvpara/tools/paired.mjs)
import fs from "node:fs";
const { combineOrders, summarize, meanScore, bootstrapCI } = await import("<workspace>/boar-eval/scorers/vendor/eval-lib/judge-core.mjs");
const [idf, label, ...paths] = process.argv.slice(2);
const want = new Set(fs.readFileSync(idf, "utf8").split("\n").filter(Boolean));
const rd = (p) => fs.readFileSync(p, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
function pairs(p) { const by = {}; for (const r of rd(p).filter((r) => r.ok && want.has(r.queryId))) (by[r.queryId] ??= {})[r.order] = r.mapped;
  return Object.fromEntries(Object.entries(by).filter(([, o]) => o.boarA && o.boarB).map(([id, o]) => [id, { id, ...combineOrders(o.boarA, o.boarB) }])); }
const ratio = (ps) => ps.reduce((a, p) => a + meanScore(p.boar), 0) / ps.reduce((a, p) => a + meanScore(p.ref), 0);
const floorAdj = (ps) => ps.reduce((a, p) => a + meanScore(p.boar) - 1, 0) / ps.reduce((a, p) => a + meanScore(p.ref) - 1, 0);
const S = paths.map((p) => ({ name: p.replace(/.*\//, "").replace(/\.judgments.*/, ""), P: pairs(p) }));
const ids = [...want].filter((id) => S.every((s) => s.P[id])).sort();
const out = { label, n: ids.length, seeds: {}, pairwise: [], perItemR: [] };
for (const s of S) { const ps = ids.map((i) => s.P[i]); const sm = summarize(ps);
  out.seeds[s.name] = { ratio: sm.qualityRatio, ci: sm.qualityRatioCI, floorAdj: floorAdj(ps), floorAdjCI: bootstrapCI(ps, floorAdj, { seed: 3 }), win: sm.boarWin, corrMean: ps.reduce((a, p) => a + meanScore(p.boar), 0) / ps.length }; }
const r = Object.values(out.seeds).map((s) => s.ratio), f = Object.values(out.seeds).map((s) => s.floorAdj);
const sd = (xs) => { const m = xs.reduce((a, b) => a + b, 0) / xs.length; return Math.sqrt(xs.reduce((a, x) => a + (x - m) ** 2, 0) / (xs.length - 1)); };
out.acrossSeeds = { k: r.length, ratioMean: r.reduce((a, b) => a + b, 0) / r.length, ratioSD: sd(r), ratioRange: [Math.min(...r), Math.max(...r)], floorMean: f.reduce((a, b) => a + b, 0) / f.length, floorSD: sd(f) };
const pear = (a, b) => { const n = a.length, ma = a.reduce((x, y) => x + y, 0) / n, mb = b.reduce((x, y) => x + y, 0) / n;
  let sab = 0, sa = 0, sb = 0; for (let i = 0; i < n; i++) { sab += (a[i] - ma) * (b[i] - mb); sa += (a[i] - ma) ** 2; sb += (b[i] - mb) ** 2; } return sab / Math.sqrt(sa * sb); };
for (let i = 0; i < S.length; i++) for (let j = i + 1; j < S.length; j++) {
  const joint = ids.map((id) => ({ a: S[i].P[id], b: S[j].P[id] })); const dR = (xs) => ratio(xs.map((x) => x.a)) - ratio(xs.map((x) => x.b));
  out.pairwise.push({ a: S[i].name, b: S[j].name, dRatio: dR(joint), dRatioCI: bootstrapCI(joint, dR, { seed: 5 }),
    h2h: { aHigher: joint.filter((x) => meanScore(x.a.boar) > meanScore(x.b.boar)).length, same: joint.filter((x) => meanScore(x.a.boar) === meanScore(x.b.boar)).length, bHigher: joint.filter((x) => meanScore(x.a.boar) < meanScore(x.b.boar)).length } });
  out.perItemR.push({ a: S[i].name, b: S[j].name, r: pear(ids.map((id) => meanScore(S[i].P[id].boar)), ids.map((id) => meanScore(S[j].P[id].boar))) }); }
console.log(JSON.stringify(out, (k, v) => (typeof v === "number" ? +v.toFixed(4) : v)));
