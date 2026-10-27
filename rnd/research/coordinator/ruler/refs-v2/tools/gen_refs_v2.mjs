#!/usr/bin/env node
// References v2 for bench v0.4 (RULER-SPEC-v1 r3 §3.2, §6.3, §10.5): one uncapped frontier + live-web draw per item per family.
//   --family claude : Opus via `claude -p` (CLI login, cleanEnv: no API key), tools WebSearch + WebFetch.
//   --family codex  : gpt-5.6-sol via `codex exec` (ChatGPT CLI login only), web_search="live", shell off, read-only sandbox.
// Multi-turn items run as a conversation: one call per user turn, earlier turns (user + this family's own earlier answers) in the message.
// Location items: the message says where the user is. Every message carries "Current date: YYYY-MM-DD" (the call's local date).
// One draw: an item with an ok row is never regenerated. A failed turn is retried once (2 attempts); an item still failing gets no row
// and is listed at the end; a later run retries only items without an ok row (partial conversations are discarded and logged).
// Never prints question or answer text: ids, counts and timings only.
// Usage (from ruler/refs-v2): node tools/gen_refs_v2.mjs --family claude|codex [--conc 3] [--cap 110] [--ids a,b] [--dry-run]
import { appendFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { execFileSync, spawn } from "node:child_process";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const D = join(dirname(fileURLToPath(import.meta.url)), "..");
const BOAR = "<workspace>";
const ITEMS = `${BOAR}/boar-eval/bench/v0.4/items.jsonl`;
const ITEMS_SHA = "f9ad2f2f0fc367811ea03690bc9b05e52d85b1ee5fb662600efa818587d33594";
const PROMPT = join(D, "prompts", "reference.v2.md");
const PROMPT_SHA = "5e41177dfa1badcff297d14f477c94393c626da76db75797841f18ce920754f1";
const OUTDIR = `${BOAR}/boar-eval/bench/v0.4/refs/v2`;
const LIB = `${BOAR}/boar-eval/scorers/vendor/eval-lib/claude-cli.mjs`;
const CODEX_MODEL = "gpt-5.6-sol";

const a = process.argv.slice(2);
const get = (k, d) => (a.includes(k) ? a[a.indexOf(k) + 1] : d);
const family = get("--family");
if (!["claude", "codex"].includes(family)) { console.error("--family claude|codex"); process.exit(2); }
const conc = Number(get("--conc", "3")), CAP = Number(get("--cap", "110")), dryRun = a.includes("--dry-run");
const sha = (b) => createHash("sha256").update(b).digest("hex");
const sys = readFileSync(PROMPT, "utf8"); if (sha(sys) !== PROMPT_SHA) { console.error("ABORT prompt sha"); process.exit(2); }
const iBuf = readFileSync(ITEMS); if (sha(iBuf) !== ITEMS_SHA) { console.error("ABORT items sha"); process.exit(2); }
const GEN_SHA = sha(readFileSync(fileURLToPath(import.meta.url)));
const items = iBuf.toString().trim().split("\n").map((l) => JSON.parse(l));
const only = get("--ids") ? new Set(get("--ids").split(",").map((s) => s.trim())) : null;
const OUT = join(OUTDIR, `${family}.jsonl`), CALLS = join(OUTDIR, `${family}.calls.jsonl`), DISCARD = join(OUTDIR, `${family}.discarded.jsonl`);
mkdirSync(OUTDIR, { recursive: true });
const rd = (f) => (existsSync(f) ? readFileSync(f, "utf8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l)) : []);
const done = new Set(rd(OUT).filter((r) => r.ok).map((r) => r.id));
const todo = items.filter((it) => !done.has(it.id) && (!only || only.has(it.id)));
const turnsTodo = todo.reduce((s, it) => s + it.turns.length, 0);
let calls = rd(CALLS).length;
console.log(`family ${family}: ${items.length} items, ${done.size} done, ${todo.length} to do (${turnsTodo} turns), calls so far ${calls}/${CAP}, gen ${GEN_SHA.slice(0, 12)}`);
if (dryRun) process.exit(0);
if (calls + turnsTodo > CAP) console.warn(`WARN: ${turnsTodo} turns to do would pass the cap ${CAP} (calls so far ${calls}); the run stops at the cap`);

const today = () => { const d = new Date(Date.now() - 3 * 3600e3); return d.toISOString().slice(0, 10); }; // America/Sao_Paulo (GMT-3)
function message(it, k, prior) {
  const head = [`Current date: ${today()}`];
  if (it.context?.city) head.push(`The user is currently in ${it.context.city} (coordinates ${it.context.lat}, ${it.context.lon}).`);
  if (k === 0) return `${head.join("\n")}\n\n${it.turns[0]}`;
  const conv = prior.map((p, j) => `User: ${it.turns[j]}\n\nAssistant: ${p.answer}`).join("\n\n");
  return `${head.join("\n")}\n\nConversation so far:\n\n${conv}\n\nUser's latest message:\n${it.turns[k]}`;
}
function split(text) {
  const m = text.match(/\n\**Sources:?\**\s*\n([\s\S]*)$/i);
  const body = m ? text.slice(0, m.index).trim() : text.trim();
  const lines = m ? m[1].split("\n").map((l) => l.replace(/^[\s\-*\d.]+/, "").trim()).filter((l) => /https?:\/\//.test(l)) : [];
  const sources = lines.map((l) => { const p = l.split("|").map((x) => x.trim()); return { url: (p[0].match(/https?:\/\/[^\s)\]>"']+/) ?? [p[0]])[0].replace(/[.,;]+$/, ""), title: p[1] ?? null, date: p[2] ?? null }; });
  return { answer: body, sources };
}

let runClaude, cleanEnv, isRateLimited, usageSummary, cliVersion;
if (family === "claude") {
  ({ runClaude, cleanEnv, isRateLimited, usageSummary } = await import(LIB));
  cliVersion = execFileSync("claude", ["--version"], { env: cleanEnv(), encoding: "utf8" }).trim();
} else {
  const keep = new Set(["PATH", "HOME", "USER", "LOGNAME", "TMPDIR", "LANG", "LC_ALL", "CODEX_HOME"]);
  cleanEnv = () => Object.fromEntries(Object.entries(process.env).filter(([k]) => keep.has(k)));
  cliVersion = execFileSync("codex", ["--version"], { env: cleanEnv(), encoding: "utf8" }).trim();
}

function runCodex(prompt) {
  return new Promise((res) => {
    const cwd = mkdtempSync(join(tmpdir(), "boar-refs-v2-codex-")), sysPath = join(cwd, "system.txt");
    writeFileSync(sysPath, sys);
    const argv = ["exec", "--ignore-user-config", "--ignore-rules", "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only",
      "--model", CODEX_MODEL, "--json", "--color", "never", "-c", "forced_login_method=\"chatgpt\"", "-c", "model_provider=\"openai\"",
      "-c", `model_instructions_file=${JSON.stringify(sysPath)}`, "-c", "project_doc_max_bytes=0", "-c", "model_reasoning_effort=\"high\"",
      "-c", "web_search=\"live\"", "-c", "features.shell_tool=false", "-c", "features.apps=false", "-c", "features.multi_agent=false",
      "-c", "features.js_repl=false", "-c", "features.memory_tool=false", "-c", "personality=\"none\"", "-"];
    const t0 = performance.now(); let out = "", err = "", timedOut = false;
    const child = spawn("codex", argv, { cwd, env: cleanEnv(), stdio: ["pipe", "pipe", "pipe"] });
    child.stdout.on("data", (d) => { out += d; }); child.stderr.on("data", (d) => { err += d; }); child.stdin.on("error", () => {});
    const timer = setTimeout(() => { timedOut = true; child.kill("SIGTERM"); }, 900_000);
    child.on("close", (code) => {
      clearTimeout(timer); rmSync(cwd, { recursive: true, force: true });
      const ev = out.split("\n").flatMap((l) => { try { return [JSON.parse(l)]; } catch { return []; } });
      const text = ev.findLast((e) => e.type === "item.completed" && e.item?.type === "agent_message")?.item.text ?? "";
      const tools = ev.filter((e) => e.type === "item.completed" && e.item && !["agent_message", "reasoning", "plan", "error"].includes(e.item.type)).map((e) => e.item);
      const failed = ev.some((e) => ["error", "turn.failed"].includes(e.type));
      const diag = ev.filter((e) => ["error", "turn.failed"].includes(e.type)).map((e) => String(e.error?.message ?? e.message ?? "")).join(" ");
      const rateLimited = (code !== 0 || failed || !text) && /rate.?limit|usage limit|usage_limit|\b429\b|too many requests/i.test(err + diag);
      const error = rateLimited ? "CLI login rate limit" : timedOut ? "timeout" : code !== 0 || failed ? `CLI failed (exit ${code})` : !text ? "no final message" : undefined;
      res({ ok: !error, error, rateLimited, text, wallMs: Math.round(performance.now() - t0), usage: ev.findLast((e) => e.type === "turn.completed")?.usage,
        toolTypes: tools.map((t) => t.type), searches: tools.filter((t) => /search/i.test(t.type)).map((t) => t.query ?? t.action?.query ?? null) });
    });
    child.stdin.end(prompt);
  });
}

async function call(prompt) {
  if (family === "claude") {
    const r = await runClaude({ prompt, systemPrompt: sys, model: "opus", tools: ["WebSearch", "WebFetch"], timeoutMs: 900_000, maxBudgetUsd: 8 });
    const keys = Object.keys(r.json?.modelUsage ?? {});
    return { ok: r.ok && !!r.json?.result, error: r.error ?? null, rateLimited: isRateLimited(r), text: r.json?.result ?? "", wallMs: Math.round(r.wallMs),
      model: keys.find((k) => k.includes("opus")) ?? keys[0], usage: r.json ? usageSummary(r.json) : null,
      searches: r.toolCalls.filter((c) => c.name === "WebSearch").map((c) => c.input?.query), fetches: r.toolCalls.filter((c) => c.name === "WebFetch").map((c) => c.input?.url) };
  }
  const r = await runCodex(prompt);
  return { ...r, model: CODEX_MODEL, fetches: [] };
}

let stop = false; const failures = [];
async function doItem(it) {
  const prior = [];
  for (let k = 0; k < it.turns.length && !stop; k++) {
    let got = null;
    for (let att = 1; att <= 2 && !stop && !got; att++) {
      if (calls >= CAP) { console.error("CAP reached: stop"); stop = true; break; }
      calls++; const startedAt = new Date().toISOString(); const msg = message(it, k, prior);
      const r = await call(msg);
      const s = split(r.text);
      const ok = r.ok && s.answer.length > 0;
      appendFileSync(CALLS, JSON.stringify({ id: it.id, turn: k, attempt: att, ok, error: r.error ?? null, wallMs: r.wallMs, at: startedAt }) + "\n");
      if (ok) got = { turn: k, answer: s.answer, sources: s.sources, rawResult: r.text, words: s.answer.split(/\s+/).filter(Boolean).length,
        asOfDate: msg.slice(14, 24), messageSha256: sha(msg), model: r.model, usage: r.usage ?? null, webSearches: r.searches ?? [], webFetches: r.fetches ?? [],
        toolTypes: r.toolTypes ?? null, wallMs: r.wallMs, startedAt, finishedAt: new Date().toISOString() };
      else { console.error(`${it.id} t${k} FAIL att ${att}: ${String(r.error).slice(0, 120)}`); if (r.rateLimited) { console.error("RATE LIMITED: stop"); stop = true; } }
    }
    if (!got) { if (prior.length) appendFileSync(DISCARD, JSON.stringify({ id: it.id, turnsDone: prior.length, at: new Date().toISOString() }) + "\n"); failures.push(it.id); return; }
    prior.push(got);
  }
  if (prior.length !== it.turns.length) return;
  const multi = it.turns.length > 1;
  const answer = multi ? prior.map((p, j) => `[Turn ${j + 1}]\n${p.answer}`).join("\n\n") : prior[0].answer;
  const srcs = [...new Map(prior.flatMap((p) => p.sources).map((s) => [s.url, s])).values()];
  const row = { id: it.id, family, ok: true, multiTurn: multi, nTurns: it.turns.length, hasLocation: !!it.context?.city, answer, sources: srcs,
    words: prior.reduce((s, p) => s + p.words, 0), turns: prior, models: [...new Set(prior.map((p) => p.model))],
    promptVersion: "reference.v2", promptSha256: PROMPT_SHA, itemsSha256: ITEMS_SHA, generatorSha256: GEN_SHA, cliVersion,
    via: family === "claude" ? "claude -p (CLI login, cleanEnv)" : "codex exec (ChatGPT CLI login, clean env, web_search live)", generatedAt: new Date().toISOString() };
  appendFileSync(OUT, JSON.stringify(row) + "\n");
  console.log(`${it.id} ok turns=${it.turns.length} words=${row.words} src=${srcs.length} search=${prior.reduce((s, p) => s + (p.webSearches?.length ?? 0), 0)} ${(prior.reduce((s, p) => s + p.wallMs, 0) / 1000).toFixed(0)}s ${row.models.join(",")}`);
}
const q = [...todo];
await Promise.all(Array.from({ length: conc }, async () => { while (q.length && !stop) await doItem(q.shift()); }));
console.log(`done: calls ${calls}/${CAP}; failed items ${failures.length}${failures.length ? ": " + failures.join(",") : ""}`);
process.exit(stop ? 3 : failures.length ? 4 : 0);
