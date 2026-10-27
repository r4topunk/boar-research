// LENGTHSHARE part 1 (0 judge calls): per-dimension ratios from existing Opus judge.v1 rows.
// For each arm/seed: raw ratio and floor-adjusted ratio on (a) the 3-dim rubric mean, (b) correctness only,
// (c) completeness only, (d) usefulness only. Pooled = pairs of all seeds concatenated (each item once per seed).
// Prints aggregates only (no ids, no text). Conventions = deepvpara/tools/paired.mjs (combineOrders, bootstrapCI 2000).
// node dimshare.mjs <ids file> <label> <judgments...>   (several labels: separate invocations)
import fs from "node:fs";
const { combineOrders, bootstrapCI } = await import("<workspace>/boar-eval/scorers/vendor/eval-lib/judge-core.mjs");
const [idf, label, ...files] = process.argv.slice(2);
const want = new Set(fs.readFileSync(idf, "utf8").split("\n").filter(Boolean));
const rd = (p) => fs.readFileSync(p, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
const K = ["correctness", "completeness", "usefulness"];
function pairs(p) {
  const by = {};
  for (const r of rd(p).filter((r) => r.ok && want.has(r.queryId))) (by[r.queryId] ??= {})[r.order] = r.mapped;
  return Object.values(by).filter((o) => o.boarA && o.boarB).map((o) => combineOrders(o.boarA, o.boarB));
}
const dims = { all: (s) => K.reduce((a, k) => a + s[k], 0) / 3, correctness: (s) => s.correctness, completeness: (s) => s.completeness, usefulness: (s) => s.usefulness };
const stats = (ps) => {
  const out = { n: ps.length };
  for (const [d, f] of Object.entries(dims)) {
    const raw = (xs) => xs.reduce((a, p) => a + f(p.boar), 0) / xs.reduce((a, p) => a + f(p.ref), 0);
    const fa = (xs) => xs.reduce((a, p) => a + f(p.boar) - 1, 0) / xs.reduce((a, p) => a + f(p.ref) - 1, 0);
    out[d] = { raw: raw(ps), rawCI: bootstrapCI(ps, raw, { seed: 3 }), floorAdj: fa(ps), floorAdjCI: bootstrapCI(ps, fa, { seed: 7 }),
      meanBoar: ps.reduce((a, p) => a + f(p.boar), 0) / ps.length, meanRef: ps.reduce((a, p) => a + f(p.ref), 0) / ps.length };
  }
  return out;
};
const res = { label, files: files.map((f) => f.split("/").slice(-2).join("/")), perSeed: {}, pooled: null };
let pool = [];
for (const f of files) { const ps = pairs(f); res.perSeed[f.split("/").pop()] = stats(ps); pool = pool.concat(ps); }
res.pooled = stats(pool);
console.log(JSON.stringify(res, (k, v) => (typeof v === "number" ? +v.toFixed(4) : v), 1));
