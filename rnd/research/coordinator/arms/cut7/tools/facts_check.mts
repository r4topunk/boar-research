/**
 * FACTS G2/G3/G5 driver (deterministic, no model, no judge). Runs the wired condition of answer.ts
 * (not PT/ES, not isHealthQuestion/isCardEmergency; the learned detector is not simulated) + factsAnswer() on:
 * v0.1 public (60), V-exact (11), dev chat slices v0–v2 (192, last user turn), safety track v0.1–v0.3 (unique).
 * Usage: tsx facts_check.mts <tree> <out.jsonl>   (stdout: summary + latency)
 */
import { readFileSync, writeFileSync } from "node:fs";
import { performance } from "node:perf_hooks";
const [tree, out] = process.argv.slice(2);
const R = "<workspace>";
const t0 = performance.now();
const { factsAnswer } = await import(`${tree}/src/rag/facts.ts`);
const { isPortugueseQuestion, isSpanishQuestion, isHealthQuestion } = await import(`${tree}/src/routing/context.ts`);
const { isCardEmergency } = await import(`${tree}/src/routing/conditionCards.ts`);
const loadMs = performance.now() - t0;
const jl = (p: string) => readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const rows: { set: string; id: string; text: string }[] = [];
for (const r of jl(`${R}/boar-eval/bench/v0.1/questions.public.jsonl`)) rows.push({ set: "v0.1", id: r.id, text: r.question });
const v01 = new Set(rows.map((r) => r.id));
for (const r of jl(`${R}/rnd/research/compass/exp/bounty-eval/bench-vslice/questions.jsonl`)) rows.push({ set: v01.has(r.id) ? "vexact(dup v0.1)" : "vexact", id: r.id, text: r.question });
for (const [name, p] of [["chat-v0", "slice.v0.jsonl"], ["chat-v1", "v1-fresh/slice.v1.jsonl"], ["chat-v2", "v2-fresh/slice.v2.jsonl"]])
  for (const r of jl(`${R}/rnd/research/compass/chat-slice/${p}`)) rows.push({ set: name, id: r.id, text: r.turns[r.turns.length - 1].text });
const seen = new Set<string>();
for (const v of ["v0.1", "v0.2", "v0.3"])
  for (const r of jl(`${R}/rnd/bench/safety/track.${v}.jsonl`)) if (!seen.has(r.question)) { seen.add(r.question); rows.push({ set: `safety(${r.lang})`, id: r.id, text: r.question }); }
const wired = (q: string) => (isPortugueseQuestion(q) || isSpanishQuestion(q) || isHealthQuestion(q) || isCardEmergency(q) ? null : factsAnswer(q));
// first call (cold: builds the alias index)
const c0 = performance.now(); factsAnswer("How big is Iceland in square kilometres?"); const coldMs = performance.now() - c0;
const res = rows.map((r) => {
  const raw = factsAnswer(r.text);
  const a = wired(r.text);
  return { ...r, fired: !!a, rawFired: !!raw, template: a?.template ?? raw?.template ?? null, entities: a?.entities ?? raw?.entities ?? null, answer: a?.text ?? null };
});
writeFileSync(out, res.map((r) => JSON.stringify(r)).join("\n") + "\n");
const by: Record<string, { n: number; fired: number; raw: number }> = {};
for (const r of res) { const b = (by[r.set] ??= { n: 0, fired: 0, raw: 0 }); b.n++; if (r.fired) b.fired++; if (r.rawFired) b.raw++; }
console.log("module load ms", loadMs.toFixed(1), "cold first call ms", coldMs.toFixed(2));
console.table(by);
for (const r of res.filter((x) => x.fired || x.rawFired)) console.log(r.set, r.id, r.fired ? "FIRE" : "raw-only", r.template, r.entities?.join(","), "|", r.text.slice(0, 90));
// G5 latency: per-call wall time over every message, 20 passes (warm)
const times: number[] = [];
for (let p = 0; p < 20; p++) for (const r of rows) { const s = performance.now(); factsAnswer(r.text); times.push(performance.now() - s); }
times.sort((a, b) => a - b);
const pct = (q: number) => times[Math.min(times.length - 1, Math.floor(q * times.length))];
console.log(`latency warm n=${times.length} p50=${pct(0.5).toFixed(3)}ms p95=${pct(0.95).toFixed(3)}ms p99=${pct(0.99).toFixed(3)}ms max=${times[times.length - 1].toFixed(3)}ms`);
