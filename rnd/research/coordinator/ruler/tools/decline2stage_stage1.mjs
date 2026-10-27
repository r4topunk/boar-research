#!/usr/bin/env node
// DECLINE2STAGE stage 1 (criterion ../DECLINE2STAGE-criterion.md): one Haiku 5.5-low call per (question, answer), no references.
// Not part of judge.mjs (judge.v1 bytes untouched); reuses boar-eval's claude -p wrapper (isolated, no tools, structured output).
// usage: node decline2stage_stage1.mjs --units <units.jsonl> --out <out.jsonl> [--keys <file>] [--rep 1] [--cap 260] [--conc 4] [--ledger <calls.log>]
// Resumes: (key, rep) rows already ok in --out are skipped. Every attempted call appends one line to --ledger; refuses to start when the ledger is at --cap.
// rc 0 ok | 3 rate limited | 4 call/parse error (rerun resumes) | 6 cap reached.
import { appendFileSync, existsSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
const LIB = "<workspace>/boar-eval/scorers/vendor/eval-lib";
const { isRateLimited, runClaude } = await import(`${LIB}/claude-cli.mjs`);
export const MODEL = "claude-haiku-5-5", EFFORT = "low", STAGE1_VERSION = "decline2stage.s1.v1";
export const SYSTEM = "You are a strict binary classifier. You read a question and an answer and return the requested JSON field only.";
export const QUESTION_LINE = "Does the answer attempt to answer the question (give any substantive claim about it)? yes/no";
export const prompt = (q, a) => `${QUESTION_LINE}\n\n<question>\n${q}\n</question>\n\n<answer>\n${a}\n</answer>\n\nReply "yes" if the answer attempts to answer the question, "no" if it does not.`;
export const SCHEMA = { type: "object", properties: { attempted: { type: "string", enum: ["yes", "no"] } }, required: ["attempted"], additionalProperties: false };
const a = process.argv.slice(2); const get = (k, d) => (a.includes(k) ? a[a.indexOf(k) + 1] : d);
const units = readFileSync(get("--units"), "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const out = get("--out"); const rep = Number(get("--rep", "1")); const cap = Number(get("--cap", "260")); const conc = Number(get("--conc", "4"));
const ledger = get("--ledger", out + ".calls.log");
const keys = get("--keys") ? new Set(readFileSync(get("--keys"), "utf8").split("\n").filter(Boolean)) : null;
const done = new Set(existsSync(out) ? readFileSync(out, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)).filter((r) => r.ok).map((r) => `${r.key}|${r.rep}`) : []);
const used = () => (existsSync(ledger) ? readFileSync(ledger, "utf8").split("\n").filter(Boolean).length : 0);
const todo = units.filter((u) => (!keys || keys.has(u.key)) && !done.has(`${u.key}|${rep}`));
if (keys) { const miss = [...keys].filter((k) => !units.some((u) => u.key === k)); if (miss.length) { console.error("unknown keys", miss); process.exit(2); } }
const promptSha = createHash("sha256").update(SYSTEM + "\n" + prompt("{q}", "{a}") + "\n" + JSON.stringify(SCHEMA)).digest("hex");
console.log(`todo ${todo.length} rep ${rep} calls used ${used()}/${cap} promptSha ${promptSha.slice(0, 12)}`);
let stop = 0; let i = 0;
async function worker() {
  while (!stop && i < todo.length) {
    const u = todo[i++];
    if (used() >= cap) { stop = stop || 6; break; }
    appendFileSync(ledger, `${new Date().toISOString()}\t${u.key}\t${rep}\n`);
    const r = await runClaude({ prompt: prompt(u.question, u.text), systemPrompt: SYSTEM, model: MODEL, effort: EFFORT, tools: [], jsonSchema: SCHEMA, timeoutMs: 120_000 });
    if (isRateLimited(r)) { console.error(`RATE LIMITED at ${u.key}`); stop = stop || 3; break; }
    const v = r.json?.structured_output?.attempted;
    if (!r.ok || (v !== "yes" && v !== "no")) { console.error(`ERROR at ${u.key}: ${r.error ?? "no structured_output"}`); stop = stop || 4; break; }
    const row = { key: u.key, set: u.set, id: u.id, rep, ok: true, attempted: v, notAttempted: v === "no", stage1Version: STAGE1_VERSION, promptSha256: promptSha,
                  requestedModel: MODEL, effort: EFFORT, model: r.json ? Object.keys(r.json.modelUsage ?? {})[0] : undefined, textSha256: u.text_sha256,
                  durationMs: r.json?.duration_ms, listPriceEquivalentUsd: r.json?.total_cost_usd, createdAt: new Date().toISOString() };
    appendFileSync(out, JSON.stringify(row) + "\n"); console.log(`${u.key} ${v} ${((row.durationMs ?? 0) / 1000).toFixed(1)}s`);
  }
}
await Promise.all(Array.from({ length: conc }, worker));
process.exit(stop);
