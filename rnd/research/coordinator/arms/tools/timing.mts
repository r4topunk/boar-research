import fs from "node:fs";
const t = process.argv[2];
const { verdictGuard } = await import(t + "/src/routing/verdictGuard.ts");
const { arithmeticAnswer } = await import(t + "/src/routing/arithmetic.ts");
const { isWaterSafetyQuestion } = await import(t + "/src/routing/waterSafety.ts");
const rows = fs.readFileSync("<workspace>/boar-eval/runs/kiln/overnight/traces/ov-cut2-v01-s44.traces.jsonl", "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const N = 50; let t0 = performance.now();
for (let i = 0; i < N; i++) for (const r of rows) verdictGuard(r.question, r.answer.text);
const vg = (performance.now() - t0) / (N * rows.length);
t0 = performance.now();
for (let i = 0; i < N; i++) for (const r of rows) { arithmeticAnswer(r.question); isWaterSafetyQuestion(r.question); }
console.log(`per item (M-series desktop): VG ${vg.toFixed(3)} ms, AR+SC triggers ${((performance.now() - t0) / (N * rows.length)).toFixed(3)} ms`);
