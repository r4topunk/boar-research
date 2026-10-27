// DEEPROUTE analysis (question ad3ecf9c…): deep35 engine vs 4B engine, v0.1 EN, existing judge.v1 judgments only.
// node deeproute.mjs [bucketRun=ctl-s44] [items.csv]   — 0 model/judge calls. Loaders/bootstrap as rethurt.mjs.
import fs from "node:fs";
import crypto from "node:crypto";
const B = "<workspace>";
const { combineOrders, meanScore, bootstrapCI } = await import(`${B}/boar-eval/scorers/vendor/eval-lib/judge-core.mjs`);
const R = `${B}/rnd/research`, E = `${B}/boar-eval/runs`, N1 = `${E}/night-2026-10-01`;
const F = {
  deep: { j: [42, 43].map((s) => `${N1}/deep35/and-deep35-s${s}.judgments.jsonl`), t: [42, 43].map((s) => `${N1}/deep35/and-deep35-s${s}.traces.jsonl`) },
  b4: { j: [`${N1}/and-qwen-s42.judgments.jsonl`, `${N1}/and-qwen-s43.judgments.jsonl`, `${E}/and-qwen-s44/and-qwen-s44.judgments.jsonl`],
        t: [`${N1}/and-qwen-s42.traces.jsonl`, `${N1}/and-qwen-s43.traces.jsonl`, `${E}/and-qwen-s44/and-qwen-s44.traces.jsonl`] },
};
const SCORE = `${R}/coordinator/RETRIEVAL-SCORECARD-2026-10-06.items.csv`, BENCH = `${B}/boar-eval/bench/v0.1/questions.public.jsonl`;
const sha = (p) => crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex").slice(0, 12);
const rd = (p) => fs.readFileSync(p, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
const bench = Object.fromEntries(rd(BENCH).map((q) => [q.id, q]));
const mean = (a) => a.reduce((s, x) => s + x, 0) / a.length;
function loadJ(files) { // per item: mean over seeds of order-combined rubric (RETHURT convention)
  const acc = {};
  for (const f of files) {
    const by = {};
    for (const r of rd(f).filter((r) => r.ok)) (by[r.queryId] ??= {})[r.order] = r.mapped;
    for (const [id, o] of Object.entries(by)) {
      if (!(o.boarA && o.boarB)) continue;
      const c = combineOrders(o.boarA, o.boarB);
      (acc[id] ??= []).push({ b: meanScore(c.boar), r: meanScore(c.ref), c: c.boar.correctness });
    }
  }
  return Object.fromEntries(Object.entries(acc).map(([id, a]) => [id, { b: mean(a.map((x) => x.b)), r: mean(a.map((x) => x.r)), c: mean(a.map((x) => x.c)), n: a.length }]));
}
function loadT(files) { // per item: list of traces over seeds
  const acc = {};
  for (const f of files) for (const t of rd(f)) (acc[t.itemId] ??= []).push(t);
  return acc;
}
const J = { deep: loadJ(F.deep.j), b4: loadJ(F.b4.j) }, T = { deep: loadT(F.deep.t), b4: loadT(F.b4.t) };
// scorecard buckets (as rethurt.mjs)
const bucketRun = process.argv[2] ?? "ctl-s44";
const csv = fs.readFileSync(SCORE, "utf8").trim().split("\n");
const hdr = csv[0].split(","); const bi = hdr.indexOf("bucket");
const bucket = {};
for (const line of csv.slice(1)) { const cells = line.match(/("([^"]|"")*"|[^,]*)(,|$)/g).map((c) => c.replace(/,$/, "")); if (cells[0] === bucketRun) bucket[cells[1]] = cells[bi]; }
const BN = { B1: "coverage", B2: "ranking", B3: "dropped", B4: "reader-fail", B5: "reader-ok", B6: "ambiguous", "no-gold": "no-gold" };
const ids = Object.keys(J.deep).filter((id) => J.b4[id] && bench[id]).sort();
const ir = (s) => s.b / s.r;
// routing-time signals from the 4B traces: majority over seeds (≥ 2 of 3)
const maj = (ts, f) => ts.filter(f).length * 2 > ts.length;
const has = (t, re) => t.route.reasonCodes.some((c) => re.test(c));
const qlen = (id) => bench[id].question.trim().split(/\s+/).length;
const medLen = [...ids.map(qlen)].sort((a, b) => a - b)[Math.floor(ids.length / 2)];
const rows = ids.map((id) => {
  const t4 = T.b4[id], td = T.deep[id];
  return {
    id, cat: bench[id].category, bucket: BN[bucket[id] ?? "no-gold"] ?? bucket[id], qlen: qlen(id),
    b4_ir: ir(J.b4[id]), deep_ir: ir(J.deep[id]), b4_c: J.b4[id].c, deep_c: J.deep[id].c,
    b4_ms: mean(t4.map((t) => t.timing.totalMs)), deep_ms: mean(td.map((t) => t.timing.totalMs)),
    b4_ttft: mean(t4.map((t) => t.timing.ttftMs)), deep_ttft: mean(td.map((t) => t.timing.ttftMs)),
    b4_tier: t4[0].route.tier, deep_tier: td[0].route.tier,
    task: t4[0].route.task, research: maj(t4, (t) => t.route.task === "research"),
    noSource: maj(t4, (t) => has(t, /^grounding:(no-good-source|no-source-memory)$/)),
    offTopicInstant: maj(t4, (t) => has(t, /^instant:off-topic$/)),
    weak: maj(t4, (t) => t.answer.weakSources), declined: maj(t4, (t) => t.answer.declined),
  };
});
rows.forEach((r) => (r.d = r.deep_ir - r.b4_ir));
const totD = rows.reduce((s, r) => s + r.d, 0);
const out = { n: ids.length, bucketRun, medLen, shas: {} };
for (const p of [...F.deep.j, ...F.b4.j, ...F.deep.t, ...F.b4.t, SCORE, BENCH]) out.shas[p.replace(B + "/", "")] = sha(p);
const ratio = (xs, pick) => xs.reduce((a, x) => a + J[pick(x)][x.id].b, 0) / xs.reduce((a, x) => a + J[pick(x)][x.id].r, 0);
const r4 = ratio(rows, () => "b4"), rD = ratio(rows, () => "deep");
const mean4 = mean(rows.map((r) => r.b4_ms));
const sim = (name, route, { post = false, note = "" } = {}) => { // route(row) -> true = deep
  const pick = (x) => (route(x) ? "deep" : "b4");
  const mx = ratio(rows, pick), dfn = (xs) => ratio(xs, pick) - ratio(xs, () => "b4");
  const ci = bootstrapCI(rows, dfn, { seed: 5, n: 2000 });
  const ms = mean(rows.map((x) => (route(x) ? (post ? x.b4_ms + x.deep_ms : x.deep_ms) : x.b4_ms)));
  const nd = rows.filter(route).length;
  return { name, note, deepN: nd, deepPct: +(100 * nd / rows.length).toFixed(1), ratio: +mx.toFixed(4), dRatio: +(mx - r4).toFixed(4), ci: ci.map((x) => +x.toFixed(4)),
    captured: +((mx - r4) / (rD - r4)).toFixed(3), wallX: +(ms / mean4).toFixed(2) };
};
const hard = new Set(["reasoning", "comparison", "synthesis", "explanation"]);
out.router = [
  sim("all-4B", () => false),
  sim("all-deep", () => true),
  sim("oracle (per-item best)", (x) => x.d > 0, { note: "uses judgments" }),
  sim("R1 task:research", (x) => x.research),
  sim("R2 no on-topic source (no-good-source | no-source-memory)", (x) => x.noSource),
  sim("R3 instant:off-topic", (x) => x.offTopicInstant),
  sim("R4 weakSources (post-gen escalate)", (x) => x.weak, { post: true }),
  sim("R5 category in reasoning/comparison/synthesis/explanation", (x) => hard.has(x.cat) && x.b4_tier !== "instant"),
  sim(`R6 question ≥ ${medLen} words`, (x) => x.qlen >= medLen),
  sim("R7 no-gold (scorecard; not on device)", (x) => x.bucket === "no-gold"),
  sim("R8 R2 or R3 (any pre-gen retrieval-miss signal)", (x) => x.noSource || x.offTopicInstant),
];
const grp = (key) => { const g = {}; rows.forEach((r) => (g[r[key]] ??= []).push(r)); return Object.fromEntries(Object.entries(g).sort().map(([k, v]) => {
  const ds = v.map((r) => r.d), s = ds.reduce((a, b) => a + b, 0);
  return [k, { n: v.length, meanD: +(s / v.length).toFixed(4), share: +(s / totD).toFixed(3), ci: bootstrapCI(ds, mean, { seed: 5, n: 2000 }).map((x) => +x.toFixed(3)), dRatio: +(ratio(v, () => "deep") - ratio(v, () => "b4")).toFixed(4) }]; })); };
out.overall = { r4: +r4.toFixed(4), rD: +rD.toFixed(4), meanItemD: +(totD / rows.length).toFixed(4), sumD: +totD.toFixed(4),
  better: rows.filter((r) => r.d > 1e-9).length, worse: rows.filter((r) => r.d < -1e-9).length,
  cw4: rows.filter((r) => r.b4_c <= 2).length, cwD: rows.filter((r) => r.deep_c <= 2).length, pass4: rows.filter((r) => r.b4_c >= 4).length, passD: rows.filter((r) => r.deep_c >= 4).length,
  wall: { b4MeanMs: Math.round(mean4), deepMeanMs: Math.round(mean(rows.map((r) => r.deep_ms))), b4TtftMs: Math.round(mean(rows.map((r) => r.b4_ttft))), deepTtftMs: Math.round(mean(rows.map((r) => r.deep_ttft))) },
  instantBoth: rows.filter((r) => r.b4_tier === "instant").map((r) => `${r.id}:${r.deep_tier}`), declinedAny: rows.filter((r) => r.declined).length };
out.byCat = grp("cat"); out.byBucket = grp("bucket");
const f3 = (x) => +x.toFixed(3);
out.wins = rows.filter((r) => r.d >= 0.15).sort((a, b) => b.d - a.d).map((r) => [r.id, r.cat, r.bucket, f3(r.d), f3(r.b4_c), f3(r.deep_c)]);
out.losses = rows.filter((r) => r.d <= -0.15).sort((a, b) => a.d - b.d).map((r) => [r.id, r.cat, r.bucket, f3(r.d), f3(r.b4_c), f3(r.deep_c)]);
// signal crosstab: how well each routing signal separates deep-wins
out.signals = Object.fromEntries(["research", "noSource", "offTopicInstant", "weak"].map((k) => [k, { on: rows.filter((r) => r[k]).length, sumDon: f3(rows.filter((r) => r[k]).reduce((s, r) => s + r.d, 0)), sumDoff: f3(rows.filter((r) => !r[k]).reduce((s, r) => s + r.d, 0)) }]));
if (process.argv[3]) {
  const cols = ["id", "cat", "bucket", "qlen", "task", "research", "noSource", "offTopicInstant", "weak", "b4_tier", "deep_tier", "b4_ir", "deep_ir", "d", "b4_c", "deep_c", "b4_ms", "deep_ms", "b4_ttft", "deep_ttft"];
  fs.writeFileSync(process.argv[3], [cols.join(","), ...rows.map((r) => cols.map((c) => (typeof r[c] === "number" ? r[c].toFixed(4) : typeof r[c] === "boolean" ? +r[c] : r[c])).join(","))].join("\n") + "\n");
}
console.log(JSON.stringify(out, null, 1));
