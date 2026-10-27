// RETHURT analysis (criterion ce950ece…): existing judge.v1 judgments only. node rethurt.mjs [bucketRun=ctl-s44]
import fs from "node:fs";
const B = "<workspace>";
const { combineOrders, meanScore, bootstrapCI } = await import(`${B}/boar-eval/scorers/vendor/eval-lib/judge-core.mjs`);
const R = `${B}/rnd/research`, E = `${B}/boar-eval/runs`;
const F = {
  d35eng: [`${E}/night-2026-10-01/deep35/and-deep35-s42.judgments.jsonl`, `${E}/night-2026-10-01/deep35/and-deep35-s43.judgments.jsonl`],
  d35cb: [`${E}/kiln/moescreen/moescreen-deep35-v01-s42.judgments.jsonl`],
  d35r450: [`${R}/coordinator/arms/deepread/deep35-R450.judgments.jsonl`],
  b4eng: [`${E}/night-2026-10-01/and-qwen-s42.judgments.jsonl`, `${E}/night-2026-10-01/and-qwen-s43.judgments.jsonl`, `${E}/and-qwen-s44/and-qwen-s44.judgments.jsonl`],
  b4cb: [`${R}/anvil/exp/outofkit/runs/srv-qwen3-4b.judgments.jsonl`],
};
const rd = (p) => fs.readFileSync(p, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
const cat = {};
function load(files) { // per item: mean over seeds of order-combined rubric
  const acc = {};
  for (const f of files) {
    const by = {};
    for (const r of rd(f).filter((r) => r.ok)) { (by[r.queryId] ??= {})[r.order] = r.mapped; cat[r.queryId] ??= r.category; }
    for (const [id, o] of Object.entries(by)) {
      if (!(o.boarA && o.boarB)) continue;
      const c = combineOrders(o.boarA, o.boarB);
      (acc[id] ??= []).push({ b: meanScore(c.boar), r: meanScore(c.ref), c: c.boar.correctness });
    }
  }
  const m = (a, k) => a.reduce((s, x) => s + x[k], 0) / a.length;
  return Object.fromEntries(Object.entries(acc).map(([id, a]) => [id, { b: m(a, "b"), r: m(a, "r"), c: m(a, "c"), n: a.length }]));
}
const S = Object.fromEntries(Object.entries(F).map(([k, f]) => [k, load(f)]));
// buckets from scorecard
const bucketRun = process.argv[2] ?? "ctl-s44";
const csv = fs.readFileSync(`${R}/coordinator/RETRIEVAL-SCORECARD-2026-10-06.items.csv`, "utf8").trim().split("\n");
const hdr = csv[0].split(","); const bi = hdr.indexOf("bucket");
const bucket = {};
for (const line of csv.slice(1)) { const cells = line.match(/("([^"]|"")*"|[^,]*)(,|$)/g).map((c) => c.replace(/,$/, "")); if (cells[0] === bucketRun) bucket[cells[1]] = cells[bi]; }
const BN = { B1: "coverage", B2: "ranking", B3: "dropped", B4: "reader-fail", B5: "reader-ok", B6: "ambiguous", "no-gold": "no-gold" };
const ids = Object.keys(S.d35cb).filter((id) => Object.values(S).every((s) => s[id])).sort();
const ratio = (xs, k) => xs.reduce((a, x) => a + x[k].b, 0) / xs.reduce((a, x) => a + x[k].r, 0);
const ir = (s) => s.b / s.r;
const out = { n: ids.length, bucketRun, overall: {}, pairs: {} };
for (const k of Object.keys(S)) out.overall[k] = +ratio(ids.map((id) => ({ x: S[k][id] })), "x").toFixed(4);
const rows = ids.map((id) => ({ id, cat: cat[id], bucket: BN[bucket[id] ?? "no-gold"] ?? bucket[id], ...Object.fromEntries(Object.keys(S).flatMap((k) => [[`${k}_ir`, ir(S[k][id])], [`${k}_c`, S[k][id].c]])) }));
for (const [name, a, b] of [["deep35 engine-closed", "d35eng", "d35cb"], ["4B engine-closed", "b4eng", "b4cb"], ["deep35 R450-closed", "d35r450", "d35cb"]]) {
  const J = ids.map((id) => ({ a: S[a][id], b: S[b][id] }));
  const dR = (xs) => ratio(xs, "a") - ratio(xs, "b");
  const ci = bootstrapCI(J, dR, { seed: 5, n: 2000 });
  const d = ids.map((id) => ir(S[a][id]) - ir(S[b][id]));
  const eps = 1e-9;
  const conv = ids.filter((id) => S[a][id].c >= 4 && S[b][id].c <= 2), regr = ids.filter((id) => S[b][id].c >= 4 && S[a][id].c <= 2);
  const cw = (k) => ids.filter((id) => S[k][id].c <= 2).length, pass = (k) => ids.filter((id) => S[k][id].c >= 4).length;
  out.pairs[name] = { a, b, ratioA: +ratio(J, "a").toFixed(4), ratioB: +ratio(J, "b").toFixed(4), dRatio: +dR(J).toFixed(4), ci: ci.map((x) => +x.toFixed(4)),
    meanItemD: +(d.reduce((s, x) => s + x, 0) / d.length).toFixed(4),
    better: d.filter((x) => x > eps).length, worse: d.filter((x) => x < -eps).length, equal: d.filter((x) => Math.abs(x) <= eps).length,
    converted: conv, regressed: regr, cwA: cw(a), cwB: cw(b), passA: pass(a), passB: pass(b) };
  rows.forEach((r, i) => (r[`d_${a}_${b}`] = d[i]));
  const group = (key) => { const g = {}; rows.forEach((r, i) => ((g[r[key]] ??= []).push(d[i]))); const tot = d.reduce((s, x) => s + x, 0);
    return Object.fromEntries(Object.entries(g).sort().map(([k, v]) => { const s = v.reduce((x, y) => x + y, 0); return [k, { n: v.length, meanD: +(s / v.length).toFixed(4), sumD: +s.toFixed(4), shareOfNet: +(s / tot).toFixed(3) }]; })); };
  out.pairs[name].byBucket = group("bucket"); out.pairs[name].byCat = group("cat");
  const sumD = d.reduce((s, x) => s + x, 0), cov = rows.reduce((s, r, i) => s + (["coverage", "no-gold"].includes(r.bucket) ? d[i] : 0), 0);
  out.pairs[name].sumD = +sumD.toFixed(4); out.pairs[name].covNoGoldSumD = +cov.toFixed(4); out.pairs[name].covNoGoldShare = +(cov / sumD).toFixed(3);
}
const dk = "d_d35eng_d35cb";
const srt = [...rows].sort((x, y) => x[dk] - y[dk]);
out.topLoss = srt.slice(0, 10).map((r) => [r.id, r.bucket, +r[dk].toFixed(3), +r.d35cb_c.toFixed(2), +r.d35eng_c.toFixed(2)]);
out.topGain = srt.slice(-10).reverse().map((r) => [r.id, r.bucket, +r[dk].toFixed(3), +r.d35cb_c.toFixed(2), +r.d35eng_c.toFixed(2)]);
if (process.argv[3]) {
  const cols = Object.keys(rows[0]);
  fs.writeFileSync(process.argv[3], [cols.join(","), ...rows.map((r) => cols.map((c) => (typeof r[c] === "number" ? r[c].toFixed(4) : r[c])).join(","))].join("\n") + "\n");
}
console.log(JSON.stringify(out, null, 1));
