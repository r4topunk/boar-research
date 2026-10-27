// JUDGE2 analysis (Kiln). Per leg (orders combined per item with judge-core combineOrders, as JUDGE-TRIAGE): winner
// agreement vs Opus (and vs Sonnet-low when given), Cohen κ on BOAR correctness >= 4 vs Opus, ratio Σ/Σ and Δ (X − Opus)
// with 2000 joint boots (seed 5), Pearson r on the BOAR mean rubric, position consistency, rubric means per side,
// shim telemetry (failures, s/call, tokens). Cross legs: deep35 − 4B paired Δratio under each judge (2000 boots, seed 5).
// Usage: node judge2-analysis.mjs <config.json>   config: {legs:{name:{x, opus, sonnetLow?, calls?}}, cross:[a,b], label}
import fs from "node:fs";
const LIB = "<workspace>/boar-eval/scorers/vendor/eval-lib/judge-core.mjs";
const { combineOrders, summarize, meanScore, bootstrapCI } = await import(LIB);
const rd = (p) => fs.readFileSync(p, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
function pairs(p) {
  const by = {};
  for (const r of rd(p).filter((r) => r.ok)) (by[r.queryId] ??= {})[r.order] = r.mapped;
  return Object.fromEntries(Object.entries(by).filter(([, o]) => o.boarA && o.boarB).map(([id, o]) => [id, { id, ...combineOrders(o.boarA, o.boarB) }]));
}
const ratio = (ps) => ps.reduce((a, p) => a + meanScore(p.boar), 0) / ps.reduce((a, p) => a + meanScore(p.ref), 0);
const pearson = (x, y) => { const n = x.length, mx = x.reduce((a, b) => a + b) / n, my = y.reduce((a, b) => a + b) / n;
  let sxy = 0, sxx = 0, syy = 0; for (let i = 0; i < n; i++) { sxy += (x[i] - mx) * (y[i] - my); sxx += (x[i] - mx) ** 2; syy += (y[i] - my) ** 2; }
  return sxy / Math.sqrt(sxx * syy); };
function kappa(a, b) { const n = a.length; const po = a.filter((v, i) => v === b[i]).length / n;
  const pa = a.filter(Boolean).length / n, pb = b.filter(Boolean).length / n; const pe = pa * pb + (1 - pa) * (1 - pb);
  return pe === 1 ? 1 : (po - pe) / (1 - pe); }
const median = (a) => { const s = a.filter((x) => x != null).sort((x, y) => x - y); return s.length ? s[Math.floor((s.length - 1) / 2)] : null; };
function compare(X, R) { // X = candidate judge pairs, R = reference judge pairs
  const ids = Object.keys(X).filter((id) => R[id]).sort();
  const same = ids.filter((id) => X[id].winner === R[id].winner).length;
  const ka = kappa(ids.map((id) => X[id].boar.correctness >= 4), ids.map((id) => R[id].boar.correctness >= 4));
  const r = pearson(ids.map((id) => meanScore(X[id].boar)), ids.map((id) => meanScore(R[id].boar)));
  const joint = ids.map((id) => ({ x: X[id], r: R[id] }));
  const d = (xs) => ratio(xs.map((j) => j.x)) - ratio(xs.map((j) => j.r));
  return { n: ids.length, sameWinner: same, sameWinnerPct: (100 * same) / ids.length, kappaCorr4: ka, pearsonBoarMean: r,
    ratioX: ratio(ids.map((id) => X[id])), ratioRef: ratio(ids.map((id) => R[id])), dRatio: d(joint), dRatioCI: bootstrapCI(joint, d, { seed: 5, n: 2000 }) };
}
function describe(P) { const s = summarize(Object.values(P)); return { n: s.n, ratio: s.qualityRatio, ratioCI: s.qualityRatioCI, win: s.boarWin, tie: s.tie, loss: s.refWin,
  posCons: s.positionConsistency, rubricBoar: s.rubricBoar, rubricRef: s.rubricRef }; }
function telemetry(p) { if (!p || !fs.existsSync(p)) return null; const c = rd(p); const ok = c.filter((x) => x.ok);
  const kinds = c.reduce((a, x) => (x.kind && (a[x.kind] = (a[x.kind] ?? 0) + 1), a), {});
  return { calls: c.length, ok: ok.length, failures: kinds, thinkLeaks: c.filter((x) => x.thinkLeak).length, reasoningChars: c.reduce((a, x) => a + (x.reasoningChars ?? 0), 0),
    sPerCallMed: median(ok.map((x) => x.wallMs)) / 1000, sPerCallMean: ok.reduce((a, x) => a + x.wallMs, 0) / ok.length / 1000, sPerCallMax: Math.max(...ok.map((x) => x.wallMs)) / 1000,
    wallSumMin: c.reduce((a, x) => a + x.wallMs, 0) / 60000, promptTokMed: median(ok.map((x) => x.promptTokens)), outTokMed: median(ok.map((x) => x.completionTokens)),
    cachedTokMed: median(ok.map((x) => x.cachedTokens)), prefillTokSMed: median(ok.map((x) => x.prefillTokS)), decodeTokSMed: median(ok.map((x) => x.decodeTokS)),
    finish: c.reduce((a, x) => ((a[x.finish ?? "none"] = (a[x.finish ?? "none"] ?? 0) + 1), a), {}) }; }
const cfg = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const out = { label: cfg.label, legs: {} }; const P = {};
for (const [name, L] of Object.entries(cfg.legs)) {
  const X = pairs(L.x), O = pairs(L.opus); P[name] = { X, O };
  out.legs[name] = { x: describe(X), opus: describe(O), vsOpus: compare(X, O), telemetry: telemetry(L.calls) };
  if (L.sonnetLow) { const S = pairs(L.sonnetLow); out.legs[name].vsSonnetLow = compare(X, S); out.legs[name].sonnetLowVsOpus = compare(S, O); }
}
if (cfg.cross) { const [a, b] = cfg.cross; out.cross = {};
  for (const j of ["X", "O"]) { const A = P[a][j], B = P[b][j]; const ids = Object.keys(A).filter((id) => B[id]).sort();
    const joint = ids.map((id) => ({ a: A[id], b: B[id] })); const d = (xs) => ratio(xs.map((z) => z.a)) - ratio(xs.map((z) => z.b));
    out.cross[j === "X" ? "candidate" : "opus"] = { n: ids.length, dRatio: d(joint), dRatioCI: bootstrapCI(joint, d, { seed: 5, n: 2000 }),
      better: ids.filter((id) => meanScore(A[id].boar) > meanScore(B[id].boar)).length, worse: ids.filter((id) => meanScore(A[id].boar) < meanScore(B[id].boar)).length }; } }
console.log(JSON.stringify(out, (k, v) => (typeof v === "number" ? +v.toFixed(4) : v), 1));
