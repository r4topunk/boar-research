// DEEPTHINK-V02 per-category Δ (category = 2nd token of the v0.2 item id; no item text read). Same conventions as paired.mjs:
// combineOrders per item, ratio = Σboar/Σref, floor-adj = Σ(boar−1)/Σ(ref−1). Pools all given seeds (pairs A_i with B_i).
// node percat.mjs <ids> <nameA> <nameB> <A1.judgments> <B1.judgments> [<A2> <B2> ...]
import fs from "node:fs";
const { combineOrders, meanScore } = await import("<workspace>/boar-eval/scorers/vendor/eval-lib/judge-core.mjs");
const [idf, na, nb, ...fs_] = process.argv.slice(2);
const want = new Set(fs.readFileSync(idf, "utf8").split("\n").filter(Boolean));
const pairs = (p) => { const by = {}; for (const r of fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map(JSON.parse)) if (r.ok && want.has(r.queryId)) (by[r.queryId] ??= {})[r.order] = r.mapped;
  return Object.fromEntries(Object.entries(by).filter(([, o]) => o.boarA && o.boarB).map(([id, o]) => [id, combineOrders(o.boarA, o.boarB)])); };
const acc = {};
for (let i = 0; i < fs_.length; i += 2) { const A = pairs(fs_[i]), B = pairs(fs_[i + 1]);
  for (const id of want) { if (!A[id] || !B[id]) continue; const c = id.split("-")[1], a = (acc[c] ??= { n: 0, ab: 0, ar: 0, bb: 0, br: 0, aw: 0, bw: 0 });
    a.n++; a.ab += meanScore(A[id].boar); a.ar += meanScore(A[id].ref); a.bb += meanScore(B[id].boar); a.br += meanScore(B[id].ref);
    a.aw += A[id].winner === "boar"; a.bw += B[id].winner === "boar"; } }
const out = {};
for (const [c, a] of Object.entries(acc).sort()) { const ra = a.ab / a.ar, rb = a.bb / a.br, fa = (a.ab - a.n) / (a.ar - a.n), fb = (a.bb - a.n) / (a.br - a.n);
  out[c] = { n: a.n, [na]: +ra.toFixed(3), [nb]: +rb.toFixed(3), dRatio: +(ra - rb).toFixed(3), dFloor: +(fa - fb).toFixed(3), [`win${na}`]: a.aw, [`win${nb}`]: a.bw }; }
console.log(JSON.stringify(out));
