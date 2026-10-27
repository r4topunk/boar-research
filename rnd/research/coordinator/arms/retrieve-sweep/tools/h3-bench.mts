// H3 compress micro-bench (0 LLM): switch off vs on, interleaved in one process (robust to machine load). usage: tsx h3-bench.mts <replay.jsonl> <budget>
import { readFileSync } from "node:fs";
const T = "<workspace>/kiln-local/rs-H3";
const { compressContext, isSubstantive } = await import(`${T}/src/routing/context.ts`);
const rows = readFileSync(process.argv[2], "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const budget = Number(process.argv[3]);
const inputs = rows.map((r) => [r.question ?? r.query, r.rawFull.filter((c: any) => isSubstantive(c))] as const);
const t = { off: 0, on: 0 };
for (let rep = 0; rep < 6; rep++) for (const on of [false, true, false, true]) {
  if (on) process.env.RS_COMPRESS_HEAD = "1"; else delete process.env.RS_COMPRESS_HEAD;
  const t0 = performance.now();
  for (const [q, raw] of inputs) compressContext(q, raw, { tokenBudget: budget });
  t[on ? "on" : "off"] += performance.now() - t0;
}
const n = rows.length * 12;
console.log(JSON.stringify({ items: rows.length, budget, off_ms_per_call: +(t.off / n).toFixed(4), on_ms_per_call: +(t.on / n).toFixed(4) }));
