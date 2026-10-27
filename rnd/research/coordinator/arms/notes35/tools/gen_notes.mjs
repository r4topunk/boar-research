#!/usr/bin/env node
// NOTES35 generator: one short encyclopedic note per topic, from a llama-server (OpenAI-compatible /v1/chat/completions).
// Node >= 22, built-ins only. One request at a time; resumable (titles already in --out are skipped).
//
//   node gen_notes.mjs --order ../topics/order-bf.txt --n 300 --out notes.jsonl \
//     --server-url http://127.0.0.1:8097 --model qwen3.6-35b-a3b-ud-q2kxl [--think-budget 512] [--seed 42]
//
// Request: system = note.system.md (sha256 pinned in note.system.md.sha256), user = USER_TEMPLATE; temperature 0.3,
// top_p 0.9, max_tokens 450 (+ the thinking budget when --think-budget N, as runner/server.ts maxTokensFor does).
// Thinking OFF by default: chat_template_kwargs {enable_thinking: false} (Qwen3.x templates default to ON).
// --think-budget N: thinking ON with thinking_budget_tokens N + reasoning_budget_message (runner/server.ts requestFor);
// needs llama-server --reasoning-format deepseek so the reasoning stays out of `content`.
// Output rows: {title, section, note, model, promptSha256, params, tokens, ms, createdAt, finish, words}.
// Progress every 10 notes on stderr (counts only). Exit 0 = all N titles present in --out; 2 = some failed.
import { createHash } from "node:crypto";
import { appendFileSync, existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { parseArgs } from "node:util";

const HERE = dirname(fileURLToPath(import.meta.url));
const THINKING_BUDGET_MESSAGE = "\nI have thought enough; answering now.\n"; // = runner/server.ts (the app's literal)
const USER_TEMPLATE = "Topic: {title}\n(Encyclopedia section: {section})";

const { values: o } = parseArgs({
  options: {
    order: { type: "string" },
    n: { type: "string" },
    out: { type: "string" },
    "server-url": { type: "string", default: "http://127.0.0.1:8097" },
    model: { type: "string" },
    "think-budget": { type: "string", default: "0" },
    seed: { type: "string", default: "42" },
    system: { type: "string", default: join(HERE, "note.system.md") },
    "timeout-ms": { type: "string", default: "900000" },
    retries: { type: "string", default: "2" },
  },
});
if (!o.order || !o.n || !o.out || !o.model) {
  console.error("usage: gen_notes.mjs --order order-bf.txt --n N --out notes.jsonl --model NAME [--server-url URL] [--think-budget N] [--seed 42]");
  process.exit(1);
}
const N = Number(o.n);
const budget = Number(o["think-budget"]);
const base = o["server-url"].replace(/\/+$/, "");
const system = readFileSync(o.system, "utf8");
const pinFile = `${o.system}.sha256`;
const promptSha256 = createHash("sha256").update(system).digest("hex");
if (existsSync(pinFile) && !readFileSync(pinFile, "utf8").startsWith(promptSha256)) {
  console.error(`system prompt sha256 ${promptSha256} != ${pinFile}`);
  process.exit(1);
}

// order-bf.txt: rank<TAB>title<TAB>section path
const topics = readFileSync(o.order, "utf8").split("\n").filter(Boolean).map((l) => {
  const [rank, title, section] = l.split("\t");
  return { rank: Number(rank), title, section };
}).slice(0, N);

const done = new Set();
if (existsSync(o.out)) {
  for (const line of readFileSync(o.out, "utf8").split("\n")) {
    if (!line.trim()) continue;
    try { done.add(JSON.parse(line).title); } catch { /* a line cut by a kill: its title is redone */ }
  }
}
const todo = topics.filter((t) => !done.has(t.title));
const params = {
  temperature: 0.3, top_p: 0.9, max_tokens: 450 + (budget > 0 ? budget : 0), seed: Number(o.seed),
  enable_thinking: budget > 0, ...(budget > 0 ? { thinking_budget_tokens: budget } : {}), user_template: USER_TEMPLATE,
};
console.error(`gen_notes: ${topics.length} titles, ${done.size} already in ${o.out}, ${todo.length} to generate (thinking ${budget > 0 ? budget : "off"})`);

function body(t) {
  return {
    model: o.model,
    messages: [
      { role: "system", content: system.trim() },
      { role: "user", content: USER_TEMPLATE.replace("{title}", t.title).replace("{section}", t.section) },
    ],
    stream: false,
    temperature: params.temperature,
    top_p: params.top_p,
    max_tokens: params.max_tokens,
    seed: params.seed,
    cache_prompt: false,
    ...(budget > 0
      ? { thinking_budget_tokens: budget, reasoning_budget_message: THINKING_BUDGET_MESSAGE }
      : { chat_template_kwargs: { enable_thinking: false } }),
  };
}

const clean = (s) => s.replace(/<think>[\s\S]*?<\/think>/g, "").replace(/^\s*<\/?think>\s*/g, "").trim();

let ok = 0, failed = 0, truncated = 0, tokSum = 0, msSum = 0;
for (const t of todo) {
  let row = null;
  for (let attempt = 0; attempt <= Number(o.retries) && !row; attempt++) {
    const t0 = performance.now();
    try {
      const res = await fetch(`${base}/v1/chat/completions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body(t)),
        signal: AbortSignal.timeout(Number(o["timeout-ms"])),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const d = await res.json();
      const ch = d.choices?.[0];
      const note = clean(ch?.message?.content ?? "");
      if (!note) throw new Error("empty note");
      const ms = Math.round(performance.now() - t0);
      row = {
        title: t.title, section: t.section, note, model: o.model, promptSha256, params,
        tokens: d.usage?.completion_tokens ?? null, ms, createdAt: new Date().toISOString(),
        finish: ch.finish_reason ?? null, words: note.split(/\s+/).filter(Boolean).length,
        reasoningChars: (ch?.message?.reasoning_content ?? "").length, rank: t.rank,
        ...(d.timings ? { tokPerS: Math.round(d.timings.predicted_per_second * 10) / 10 } : {}),
      };
    } catch (e) {
      if (attempt === Number(o.retries)) console.error(`fail rank ${t.rank}: ${String(e?.message ?? e).slice(0, 80)}`);
      else await new Promise((r) => setTimeout(r, 5000));
    }
  }
  if (row) {
    appendFileSync(o.out, `${JSON.stringify(row)}\n`);
    ok++;
    tokSum += row.tokens ?? 0;
    msSum += row.ms;
    if (row.finish === "length") truncated++;
  } else failed++;
  if ((ok + failed) % 10 === 0) {
    console.error(`[${new Date().toISOString().slice(11, 19)}] ${ok + failed}/${todo.length} (ok ${ok}, failed ${failed}, truncated ${truncated}, mean ${ok ? Math.round(msSum / ok) : 0} ms, ${ok ? Math.round(tokSum / ok) : 0} tok)`);
  }
}
console.error(`done: ok ${ok}, failed ${failed}, truncated ${truncated}, total in file ${done.size + ok}/${topics.length}`);
process.exit(failed ? 2 : 0);
