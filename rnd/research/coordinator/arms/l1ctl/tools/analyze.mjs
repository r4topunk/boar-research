// L1CTL analysis: Haiku-low vs Opus-med on signal20 (orders combined via judge-core combineOrders; disagreement = tie).
import fs from "node:fs";
const { combineOrders, summarize, meanScore } = await import("<workspace>/boar-eval/scorers/vendor/eval-lib/judge-core.mjs");
const rd = (p) => fs.readFileSync(p, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
const ids = fs.readFileSync("<workspace>/rnd/research/coordinator/arms/signal20.ids", "utf8").split("\n").filter(Boolean);
const K = "<workspace>/boar-eval/runs/kiln/speedpack-l1/spctl-v01-s44.judgments.";
function pairs(p) { const by = {}; for (const r of rd(p).filter((r) => r.ok && ids.includes(r.queryId))) (by[r.queryId] ??= {})[r.order] = r;
  return Object.fromEntries(Object.entries(by).map(([id, o]) => [id, { id, raw: o, ...combineOrders(o.boarA.mapped, o.boarB.mapped) }])); }
const H = pairs(K + "haiku55-low.jsonl"), O = pairs(K + "v1-med.jsonl");
const ratio = (P) => ids.reduce((a, id) => a + meanScore(P[id].boar), 0) / ids.reduce((a, id) => a + meanScore(P[id].ref), 0);
const same = ids.filter((id) => H[id].winner === O[id].winner).length;
const corr = (P, id) => (P[id].raw.boarA.mapped.boar.correctness + P[id].raw.boarB.mapped.boar.correctness) / 2;
const rowsH = rd(K + "haiku55-low.jsonl"); const dur = rowsH.map((r) => r.durationMs / 1000);
const sH = summarize(Object.values(H)), sO = summarize(ids.map((id) => O[id]));
console.log(JSON.stringify({ n: ids.length, sameWinner: same, ratioHaiku: ratio(H), ratioOpus: ratio(O),
  winH: [sH.boarWin, sH.tie, sH.refWin], winO: [sO.boarWin, sO.tie, sO.refWin], posConsH: sH.positionConsistency, posConsO: sO.positionConsistency,
  meanCorrH: ids.reduce((a, id) => a + corr(H, id), 0) / 20, meanCorrO: ids.reduce((a, id) => a + corr(O, id), 0) / 20,
  sPerCallMean: dur.reduce((a, b) => a + b) / dur.length, sPerCallMedian: dur.sort((a, b) => a - b)[19],
  usd: rowsH.reduce((a, r) => a + r.listPriceEquivalentUsd, 0), models: [...new Set(rowsH.map((r) => r.judgeModel + "/" + r.judgeVersion))] }));
for (const id of ids) console.log(id, "H", corr(H, id), H[id].winner, "| O", corr(O, id), O[id].winner);
