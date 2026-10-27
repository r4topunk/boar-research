#!/usr/bin/env node
// Bench v0 pairwise judge: system answers vs the frozen Opus+web references (rnd/bench/refs/v0), with Claude Code headless
// (`claude -p`, no tools) on the user's CLI login. Same prompt, schema, blinding, order draw and row fields as
// wt/eval/eval/scripts/judge.mjs (imported read-only by absolute path); writes ONLY under rnd/bench/judge/.
// Differences from judge.mjs: questions/refs/answers come from rnd/bench; ANY API error or rate limit stops the run
// (no retry; rerun resumes); venue-list items are not judged (scored objectively by OSM).
// Usage: node rnd/bench/judge/judge_bench.mjs --system <name> --answers <file.jsonl> [--limit N] [--seed 7] [--gap-ms 5000] [--out-dir DIR]
import { appendFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const LIB = process.env.BOAR_EVAL_LIB ?? "<workspace>/wt/eval/eval/scripts/lib";
const { cleanEnv, isRateLimited, logSpend, runClaude, sleep, totalSpend } = await import(join(LIB, "claude-cli.mjs"));
const { JUDGE_SYSTEM, VERDICT_SCHEMA, blind, firstOrders, judgePrompt, mapVerdict } = await import(join(LIB, "judge-core.mjs"));
const HERE = dirname(fileURLToPath(import.meta.url)); const BENCH = join(HERE, "..");
const JUDGE_VERSION = "judge.v1"; const Q_SHA = "dc859ebd91b0e02736ff45a5370fc64d42237ac65b93f02d57df619b20bb6b4f";
const a = process.argv.slice(2); const get = (k, d) => (a.includes(k) ? a[a.indexOf(k) + 1] : d);
const system = get("--system"); const answersPath = get("--answers");
const seed = Number(get("--seed", "7")); const gapMs = Number(get("--gap-ms", "5000")); const limit = Number(get("--limit", "0"));
const judgeModel = get("--judge-model", "opus");
if (!system || !answersPath) throw new Error("--system and --answers are required");
const sha = (p) => createHash("sha256").update(readFileSync(p)).digest("hex");
const qPath = join(BENCH, "questions/v0/questions.public.jsonl"); const refPath = join(BENCH, "refs/v0/claude-code__opus.jsonl");
if (sha(qPath) !== Q_SHA) throw new Error("questions sha mismatch: split not frozen?");
const refManifest = JSON.parse(readFileSync(join(BENCH, "refs/v0/MANIFEST.json"), "utf8"));
if (sha(refPath) !== refManifest.jsonl_sha256) throw new Error("references sha mismatch vs MANIFEST");
const readJsonl = (p) => readFileSync(p, "utf8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
const questions = Object.fromEntries(readJsonl(qPath).map((q) => [q.id, q]));
const ans = Object.fromEntries(readJsonl(answersPath).map((r) => [r.queryId, r]));
const ref = Object.fromEntries(readJsonl(refPath).filter((r) => r.ok).map((r) => [r.id, r]));
let ids = Object.keys(questions).filter((id) => questions[id].grading?.type !== "venue-list");
const skipped = ids.filter((id) => !ans[id] || !ref[id]); if (skipped.length) console.warn(`skipping ${skipped.length} ids without both answers: ${skipped.join(",")}`);
ids = ids.filter((id) => ans[id] && ref[id]);
const out = join(get("--out-dir", join(HERE, "v0")), `${system}__vs__refs-v0.jsonl`); const SPEND = join(HERE, "spend.jsonl");
mkdirSync(dirname(out), { recursive: true });
const done = new Set(existsSync(out) ? readJsonl(out).filter((r) => r.ok).map((r) => `${r.queryId}|${r.order}`) : []);
const cliVersion = execFileSync("claude", ["--version"], { env: cleanEnv(), encoding: "utf8" }).trim();
const first = firstOrders(ids, seed); const answersSha = sha(answersPath);
let calls = 0; const t0 = Date.now();
for (const id of ids) {
  const q = questions[id]; const notes = (q.rubric ?? []).join(" / ");
  const orders = first[id] === "boarA" ? ["boarA", "boarB"] : ["boarB", "boarA"];
  for (const order of orders) {
    if (done.has(`${id}|${order}`)) continue;
    if (limit && calls >= limit) { console.log(`limit ${limit} reached`); process.exit(0); }
    if (calls++) await sleep(gapMs);
    const boarIsA = order === "boarA";
    const [answerA, answerB] = boarIsA ? [blind(ans[id].answer), blind(ref[id].answer)] : [blind(ref[id].answer), blind(ans[id].answer)];
    const r = await runClaude({ prompt: judgePrompt({ question: q.question, notes, answerA, answerB }), systemPrompt: JUDGE_SYSTEM,
                                model: judgeModel, tools: [], jsonSchema: VERDICT_SCHEMA, timeoutMs: 180_000 });
    logSpend(SPEND, `bench-judge:${system}`, r);
    if (isRateLimited(r)) { console.error(`RATE LIMITED at ${id}/${order}: ${r.error ?? r.stderr}. Stopped; rerun resumes.`); process.exit(3); }
    const verdict = r.json?.structured_output; const ok = r.ok && verdict != null;
    if (!ok) { console.error(`API/verdict ERROR at ${id}/${order}: ${r.error ?? "no structured_output"}. Stopped (no retry); rerun resumes.`); process.exit(4); }
    const row = { queryId: id, category: q.category, order, ok, verdict, mapped: mapVerdict(verdict, boarIsA), system, reference: "refs-v0 claude-code__opus",
                  judgeModel: r.json ? Object.keys(r.json.modelUsage ?? {})[0] : undefined, judgeVersion: JUDGE_VERSION, seed, subset: "bench-v0-public",
                  durationMs: r.json?.duration_ms, listPriceEquivalentUsd: r.json?.total_cost_usd, cliVersion, answersSha256: answersSha,
                  refsSha256: refManifest.jsonl_sha256, questionsSha256: Q_SHA, createdAt: new Date().toISOString() };
    appendFileSync(out, JSON.stringify(row) + "\n");
    console.log(`${id} ${order} ${verdict.winner}->${row.mapped.winner} ${((row.durationMs ?? 0) / 1000).toFixed(1)}s elapsed=${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
}
console.log(`done ${out}; cumulative list-price equivalent ${totalSpend(SPEND).toFixed(2)} USD`);
