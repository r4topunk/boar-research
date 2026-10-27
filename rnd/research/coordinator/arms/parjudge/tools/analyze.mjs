// PARJUDGE analysis. Per level: wall (times.txt first start -> last exit), calls/min, rate-limit/error lines in shard logs,
// spend rows in window, median/p90 s/call (row durationMs), list-eq cost, and agreement vs the sequential HAIKUJUDGE A1 run
// via arms/judge2/judge2-analysis.mjs reused as is (A1 in the "opus" reference slot; orders combined; 2000 boots seed 5).
// Usage: node analyze.mjs > ../analysis.json
import fs from "node:fs"; import { execFileSync } from "node:child_process";
const BE = "<workspace>/boar-eval", ARM = "<workspace>/rnd/research/coordinator/arms";
const A1 = `${BE}/runs/kiln/haikujudge/deep35-R450.judgments.haiku55-low.jsonl`, A1LOG = `${BE}/runs/kiln/haikujudge/deep35-R450.haiku55-low.log`;
const rd = (p) => fs.readFileSync(p, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
const q = (a, p) => { const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.ceil(p * s.length) - 1)]; };
function timing(rows) { const d = rows.map((r) => r.durationMs / 1000);
  return { calls: rows.length, ok: rows.filter((r) => r.ok).length, medS: q(d, 0.5), p90S: q(d, 0.9), maxS: Math.max(...d),
    usd: rows.reduce((a, r) => a + (r.listPriceEquivalentUsd ?? 0), 0), models: [...new Set(rows.map((r) => r.judgeModel))] }; }
const spend = rd(`${BE}/runs/judge-spend.jsonl`);
const out = { sequentialA1: { ...timing(rd(A1)), wallS: null } };
const a1t = rd(A1).map((r) => Date.parse(r.createdAt)).sort((a, b) => a - b);
const lastEl = [...fs.readFileSync(A1LOG, "utf8").matchAll(/elapsed=(\d+)s/g)].pop();
out.sequentialA1.wallS = +lastEl[1]; out.sequentialA1.createdAtSpanS = (a1t.at(-1) - a1t[0]) / 1000; out.sequentialA1.gapMs = 1000;
out.sequentialA1.callsPerMin = (114 / out.sequentialA1.wallS) * 60;
for (const N of [4, 8]) {
  const D = `${BE}/runs/kiln/parjudge/N${N}`; if (!fs.existsSync(`${BE}/runs/kiln/parjudge/N${N}.judgments.jsonl`)) continue;
  const rows = rd(`${BE}/runs/kiln/parjudge/N${N}.judgments.jsonl`);
  const t = fs.readFileSync(`${D}/times.txt`, "utf8"); const st = [...t.matchAll(/^start \d+ (\d+)/gm)].map((m) => +m[1]);
  const en = [...t.matchAll(/^end \d+ (\d+) rc=(\d+) dies=(\d+)/gm)]; const wallS = Math.max(...en.map((m) => +m[1])) - Math.min(...st);
  const logs = fs.readdirSync(D).filter((f) => f.endsWith(".log")).map((f) => fs.readFileSync(`${D}/${f}`, "utf8")).join("\n");
  const re = /rate.?limit|usage limit|\b429\b|overloaded|too many requests/gi;
  const sp = spend.filter((s) => s.purpose.startsWith(`boar-eval-judge:deep35-R450-par${N}-`));
  const keys = new Set(rows.map((r) => `${r.queryId}|${r.order}`));
  const cfg = { label: `PARJUDGE N=${N} vs sequential A1`, legs: { deep35: { x: `${BE}/runs/kiln/parjudge/N${N}.judgments.jsonl`, opus: A1 } } };
  fs.writeFileSync(`/tmp/parjudge-cfg-N${N}.json`, JSON.stringify(cfg));
  const ag = JSON.parse(execFileSync("node", [`${ARM}/judge2/judge2-analysis.mjs`, `/tmp/parjudge-cfg-N${N}.json`], { encoding: "utf8" })).legs.deep35;
  out[`N${N}`] = { ...timing(rows), uniqueKeys: keys.size, wallS, callsPerMin: (rows.length / wallS) * 60, speedupVsA1: out.sequentialA1.wallS / wallS,
    rateLimitOrOverloadLogHits: (logs.match(re) ?? []).length, errorLines: (logs.match(/API\/verdict ERROR/g) ?? []).length,
    timeoutsOver60s: rows.filter((r) => r.durationMs > 60000).length, dies: en.reduce((a, m) => a + +m[3], 0), nonzeroExits: en.filter((m) => m[2] !== "0").length,
    spendRows: sp.length, spendUsd: sp.reduce((a, s) => a + (s.listPriceEquivalentUsd ?? 0), 0),
    vsA1: ag.vsOpus, posCons: ag.x.posCons, posConsA1: ag.opus.posCons, ratio: ag.x.ratio, ratioA1: ag.opus.ratio };
}
console.log(JSON.stringify(out, (k, v) => (typeof v === "number" ? +v.toFixed(4) : v), 1));
