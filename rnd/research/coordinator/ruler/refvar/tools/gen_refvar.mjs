#!/usr/bin/env node
// REFVAR (RJ4) reference generator: R3-pilot prompt (reference.r3-pilot, uncapped, sources with dates), Opus + WebSearch + WebFetch via claude -p
// on the CLI login (shared helper, cleanEnv: no API key). Two independent draws (A, B) per id = separate fresh claude -p processes.
// Hard cap: 44 claude calls in total (40 + up to 4 retries), counted in refs/calls.jsonl; resumable; a rate limit stops the run (exit 3).
// Usage: node tools/gen_refvar.mjs [--conc 4]   (from ruler/refvar)
import { appendFileSync, existsSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { cleanEnv, isRateLimited, runClaude, usageSummary } from "<workspace>/wt/eval/eval/scripts/lib/claude-cli.mjs";
const D = join(dirname(fileURLToPath(import.meta.url)), "..");
const PROMPT = join(D, "prompts", "reference.r3-pilot.md");
const PROMPT_SHA = "4b2ef432aa24b09960b9d071bbbbc2b52f8e0cdacf6691514cd3e13aba1c3a2b";
const QFILE = "<workspace>/boar-eval/bench/v0.1/questions.public.jsonl";
const CAP = 44, TOOLS = ["WebSearch", "WebFetch"], MODEL = "opus";
const sha = (b) => createHash("sha256").update(b).digest("hex");
const sys = readFileSync(PROMPT, "utf8"); if (sha(sys) !== PROMPT_SHA) { console.error("ABORT prompt sha"); process.exit(2); }
const qBuf = readFileSync(QFILE); const Q = Object.fromEntries(qBuf.toString().trim().split("\n").map((l) => JSON.parse(l)).map((q) => [q.id, q]));
const ids = readFileSync(join(D, "refvar-20.ids"), "utf8").split("\n").map((s) => s.trim()).filter(Boolean);
const rd = (f) => (existsSync(f) ? readFileSync(f, "utf8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l)) : []);
const CALLS = join(D, "refs", "calls.jsonl");
const cliVersion = execFileSync("claude", ["--version"], { env: cleanEnv(), encoding: "utf8" }).trim();
function split(text) {
  const m = text.match(/\n\**Sources:?\**\s*\n([\s\S]*)$/i);
  const body = m ? text.slice(0, m.index).trim() : text.trim();
  const lines = m ? m[1].split("\n").map((l) => l.replace(/^[\s\-*\d.]+/, "").trim()).filter((l) => /https?:\/\//.test(l)) : [];
  const sources = lines.map((l) => { const p = l.split("|").map((x) => x.trim()); return { url: (p[0].match(/https?:\/\/[^\s)\]>"']+/) ?? [p[0]])[0].replace(/[.,;]+$/, ""), title: p[1] ?? null, date: p[2] ?? null }; });
  return { answer: body, sources };
}
const conc = Number(process.argv.includes("--conc") ? process.argv[process.argv.indexOf("--conc") + 1] : 4);
const jobs = []; for (const dr of ["A", "B"]) { const done = new Set(rd(join(D, "refs", `draw${dr}.jsonl`)).filter((r) => r.ok).map((r) => r.id)); for (const id of ids) if (!done.has(id)) jobs.push({ id, dr }); }
let calls = rd(CALLS).length, stop = false;
console.log(`todo ${jobs.length} jobs, calls so far ${calls}/${CAP}`);
async function work() {
  while (jobs.length && !stop) {
    const { id, dr } = jobs.shift(); const q = Q[id];
    for (let att = 1; att <= 2 && !stop; att++) {
      if (calls >= CAP) { console.error("CAP reached"); stop = true; break; }
      calls++; const startedAt = new Date().toISOString();
      const r = await runClaude({ prompt: q.question, systemPrompt: sys, model: MODEL, tools: TOOLS, timeoutMs: 900_000, maxBudgetUsd: 8 });
      const text = r.json?.result ?? ""; const s = split(text);
      appendFileSync(CALLS, JSON.stringify({ id, draw: dr, attempt: att, ok: r.ok && s.answer.length > 0, error: r.error ?? null, wallMs: Math.round(r.wallMs), listPriceEquivalentUsd: r.json?.total_cost_usd ?? null, at: startedAt }) + "\n");
      if (r.ok && s.answer.length > 0) {
        const keys = Object.keys(r.json?.modelUsage ?? {});
        const row = { id, draw: dr, category: q.category, lang: q.lang, question: q.question, ok: true, answer: s.answer, sources: s.sources, rawResult: text,
          words: s.answer.split(/\s+/).filter(Boolean).length, wallMs: Math.round(r.wallMs), ...(r.json ? usageSummary(r.json) : {}),
          actualModelId: keys.find((k) => k.includes(MODEL)) ?? keys[0], modelUsageIds: keys,
          webSearches: r.toolCalls.filter((c) => c.name === "WebSearch").map((c) => c.input?.query), webFetches: r.toolCalls.filter((c) => c.name === "WebFetch").map((c) => c.input?.url),
          requestedModel: MODEL, tools: TOOLS, via: "claude-code-CLI login (claude -p, cleanEnv: no API key)", promptVersion: "reference.r3-pilot", promptSha256: PROMPT_SHA,
          cliVersion, questionsSha256: sha(qBuf), startedAt, generatedAt: new Date().toISOString() };
        appendFileSync(join(D, "refs", `draw${dr}.jsonl`), JSON.stringify(row) + "\n");
        console.log(`${id} ${dr} ok words=${row.words} search=${row.webSearches.length} fetch=${row.webFetches.length} src=${row.sources.length} ${(row.wallMs / 1000).toFixed(0)}s ${row.actualModelId}`);
        break;
      }
      console.error(`${id} ${dr} FAIL att ${att}: ${String(r.error).slice(0, 200)}`);
      if (isRateLimited(r)) { console.error("RATE LIMITED: stop"); stop = true; }
    }
  }
}
await Promise.all(Array.from({ length: conc }, work));
console.log(`done; calls ${calls}/${CAP}`); process.exit(stop ? 3 : 0);
