// JUDGEVAR per-item agreement between two judge passes over the same traces. Aggregates only.
// node agree.mjs <A.judgments> <B.judgments> <ids file>
import fs from "node:fs";
const { combineOrders, meanScore } = await import("<workspace>/boar-eval/scorers/vendor/eval-lib/judge-core.mjs");
const [ap, bp, idf] = process.argv.slice(2);
const want = new Set(fs.readFileSync(idf, "utf8").split("\n").filter(Boolean));
const rd = (p) => fs.readFileSync(p, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
function pairs(p) { const by = {}; for (const r of rd(p).filter((r) => r.ok && want.has(r.queryId))) (by[r.queryId] ??= {})[r.order] = r.mapped;
  return Object.fromEntries(Object.entries(by).filter(([, o]) => o.boarA && o.boarB).map(([id, o]) => [id, { raw: o, c: combineOrders(o.boarA, o.boarB) }])); }
const A = pairs(ap), B = pairs(bp); const ids = [...want].filter((i) => A[i] && B[i]).sort();
const K = ["correctness", "completeness", "usefulness"];
const sa = ids.map((i) => meanScore(A[i].c.boar)), sb = ids.map((i) => meanScore(B[i].c.boar));
const mean = (x) => x.reduce((a, b) => a + b, 0) / x.length;
const r = (x, y) => { const mx = mean(x), my = mean(y); const c = x.reduce((a, v, k) => a + (v - mx) * (y[k] - my), 0); return c / Math.sqrt(x.reduce((a, v) => a + (v - mx) ** 2, 0) * y.reduce((a, v) => a + (v - my) ** 2, 0)); };
const perDim = Object.fromEntries(K.map((k) => { const d = ids.map((i) => A[i].c.boar[k] - B[i].c.boar[k]); return [k, { meanAbsDelta: +mean(d.map(Math.abs)).toFixed(3), exact: d.filter((x) => x === 0).length, r: +r(ids.map((i) => A[i].c.boar[k]), ids.map((i) => B[i].c.boar[k])).toFixed(3) }]; }));
const rawOrder = ids.flatMap((i) => ["boarA", "boarB"].map((o) => K.map((k) => A[i].raw[o].boar[k] - B[i].raw[o].boar[k])));
const out = { n: ids.length, meanRubric: { r: +r(sa, sb).toFixed(3), meanAbsDelta: +mean(sa.map((v, k) => Math.abs(v - sb[k]))).toFixed(3), exact: sa.filter((v, k) => v === sb[k]).length, aHigher: sa.filter((v, k) => v > sb[k]).length, bHigher: sa.filter((v, k) => v < sb[k]).length },
  perDim, winnerAgreement: ids.filter((i) => A[i].c.winner === B[i].c.winner).length, orderConsistency: { A: ids.filter((i) => A[i].c.consistent).length, B: ids.filter((i) => B[i].c.consistent).length },
  perCallExactAllDims: rawOrder.filter((d) => d.every((x) => x === 0)).length, perCallTotal: rawOrder.length, refMeanAbsDelta: +mean(ids.map((i) => Math.abs(meanScore(A[i].c.ref) - meanScore(B[i].c.ref)))).toFixed(3) };
console.log(JSON.stringify(out));
