#!/usr/bin/env node
// FACT-AVAIL labeller: one call per (item, checklist point): do the candidate pack passages state the point? claude -p, no tools, structured output.
// usage: node factavail_judge.mjs --units in/units.jsonl --out out/<name>.jsonl --model haiku|opus [--effort low] [--keys file] [--cap N] [--conc 4]
// Resumes (ok keys skipped); every attempted call appends to <out>.calls.log; stops at --cap. Prints keys and labels only.
import { appendFileSync, existsSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
const { isRateLimited, runClaude } = await import("<workspace>/boar-eval/scorers/vendor/eval-lib/claude-cli.mjs");
export const SYSTEM = "You check whether reference passages from an offline library contain a specific piece of information. You return the requested JSON only.";
export const prompt = (u) =>
  `A good answer to the question below must contain this key point:\n<key_point>\n${u.point}\n</key_point>\n\n` +
  `<question>\n${u.question}\n</question>\n\nPassages from the offline library:\n` +
  u.passages.map((p, i) => `<passage n="${i + 1}" title="${p.title.replace(/"/g, "'")}">\n${p.text}\n</passage>`).join("\n") +
  `\n\nDoes at least one passage state the information in the key point (the same fact, possibly in other words)? ` +
  `Answer "yes" only if a reader could write the key point from that passage alone; related or partial information is "no". ` +
  `If yes, give the number of the best passage; if no, give 0.`;
export const SCHEMA = { type: "object", properties: { stated: { type: "string", enum: ["yes", "no"] }, passage: { type: "integer" } },
  required: ["stated", "passage"], additionalProperties: false };
const a = process.argv.slice(2); const get = (k, d) => (a.includes(k) ? a[a.indexOf(k) + 1] : d);
const units = readFileSync(get("--units"), "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const out = get("--out"), model = get("--model", "haiku"), effort = get("--effort"), cap = Number(get("--cap", "340")), conc = Number(get("--conc", "4"));
const ledger = out + ".calls.log";
const keys = get("--keys") ? new Set(readFileSync(get("--keys"), "utf8").split("\n").map((s) => s.trim()).filter(Boolean)) : null;
const done = new Set(existsSync(out) ? readFileSync(out, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)).filter((r) => r.ok).map((r) => r.key) : []);
const used = () => (existsSync(ledger) ? readFileSync(ledger, "utf8").split("\n").filter(Boolean).length : 0);
const promptSha = createHash("sha256").update(SYSTEM + "\n" + prompt({ point: "{p}", question: "{q}", passages: [] }) + JSON.stringify(SCHEMA)).digest("hex");
const todo = units.filter((u) => (!keys || keys.has(u.key)) && !done.has(u.key));
console.log(`${todo.length} to do, ${done.size} done, calls used ${used()}/${cap}, model ${model}${effort ? "-" + effort : ""}, prompt ${promptSha.slice(0, 12)}`);
let stop = false, rc = 0;
async function work() {
  while (todo.length && !stop) {
    const u = todo.shift();
    if (used() >= cap) { console.error("CAP reached"); stop = true; rc = 6; break; }
    appendFileSync(ledger, `${u.key}\t${new Date().toISOString()}\n`);
    const r = await runClaude({ prompt: prompt(u), systemPrompt: SYSTEM, model, effort, tools: [], jsonSchema: SCHEMA, timeoutMs: 180_000 });
    const v = r.json?.structured_output;
    if (isRateLimited(r)) { console.error("RATE LIMITED: stop"); stop = true; rc = 3; break; }
    if (!r.ok || !v) { console.error(`${u.key} ERROR ${String(r.error).slice(0, 100)}`); rc = 4; continue; }
    const n = v.stated === "yes" && v.passage >= 1 && v.passage <= u.passages.length ? v.passage : 0;
    const p = n ? u.passages[n - 1] : null;
    appendFileSync(out, JSON.stringify({ key: u.key, id: u.id, point_index: u.point_index, n_points: u.n_points, ok: true, stated: v.stated, passage: v.passage,
      pack: p?.pack ?? null, chunk: p?.chunk ?? null, title: p?.title ?? null, n_passages: u.passages.length,
      model: Object.keys(r.json?.modelUsage ?? {})[0], requestedModel: model, effort: effort ?? null, promptSha256: promptSha, createdAt: new Date().toISOString() }) + "\n");
    console.log(`${u.key} ${v.stated}`);
  }
}
await Promise.all(Array.from({ length: conc }, work));
process.exit(rc);
