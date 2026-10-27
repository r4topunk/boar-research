// GATE17S support labelling. Usage: node label.mjs <prep.json (outside repo, has question/context/response)> <out labels.jsonl>
import { readFileSync, appendFileSync, existsSync } from "node:fs";
const LIB = "<workspace>/boar-eval/scorers/vendor/eval-lib/claude-cli.mjs";
const { runClaude, cleanEnv } = await import(LIB);
const [prep, out] = process.argv.slice(2);
const items = JSON.parse(readFileSync(prep, "utf8"));
const SYS = "You are a strict support auditor. You only judge whether an answer is supported by the given source chunks. Whether the answer is true in the real world is irrelevant.";
const prompt = (q, chunks, a) => `QUESTION:\n${q}\n\nSOURCE CHUNKS:\n${chunks}\n\nANSWER:\n${a}\n\nLabel the answer SUPPORTED only if every factual claim in the answer that matters for answering the question is stated in, or directly entailed by, the source chunks. Label it UNSUPPORTED if any such claim is absent from the chunks, comes from outside knowledge, or contradicts them, or if the chunks do not address the question. An answer that only declines or says the sources lack the information is SUPPORTED. Ignore your own knowledge of whether the claims are true. Reply with the JSON {"label": "SUPPORTED" | "UNSUPPORTED"}.`;
const SCHEMA = { type: "object", properties: { label: { type: "string", enum: ["SUPPORTED", "UNSUPPORTED"] } }, required: ["label"] };
const have = new Set(existsSync(out) ? readFileSync(out, "utf8").split("\n").filter(Boolean).map((l) => { const r = JSON.parse(l); return r.key + "|" + r.call; }) : []);
let calls = 0;
async function call(it, c) {
  if (have.has(it.key + "|" + c)) return;
  const chunks = c === "B" ? it.chunks_rev : it.chunks;
  let r;
  for (let t = 0; t < 2; t++) {
    calls++;
    r = await runClaude({ prompt: prompt(it.question, chunks, it.response), systemPrompt: SYS, model: "haiku", effort: "low", tools: [], jsonSchema: SCHEMA, timeoutMs: 180000 });
    if (r.ok && r.json?.structured_output?.label) break;
  }
  const label = r.json?.structured_output?.label ?? null;
  appendFileSync(out, JSON.stringify({ key: it.key, call: c, label, ok: !!label }) + "\n");
}
const pool = async (list, n) => { let i = 0; await Promise.all(Array.from({ length: n }, async () => { while (i < list.length) await list[i++](); })); };
await pool(items.flatMap((it) => ["A", "B"].map((c) => () => call(it, c))), 4);
const rows = readFileSync(out, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const by = {}; for (const r of rows) (by[r.key] ??= {})[r.call] = r.label;
const need = items.filter((it) => by[it.key]?.A !== by[it.key]?.B);
console.log(`AB done, disagreements/missing: ${need.length}, claude invocations so far ${calls}`);
await pool(need.map((it) => () => call(it, "C")), 4);
console.log(`total invocations ${calls}`);
