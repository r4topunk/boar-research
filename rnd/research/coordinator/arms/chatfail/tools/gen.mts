/**
 * CHATFAIL S1 generation driver. One model x four arms, CHAT-FU-v1 replayed in chat order, history = the arm's OWN prior answers.
 *   tools/gen.sh --model m4 --arms C0,A1,A2,A3 [--chats c01,c02,c03] [--tag smoke]      (server on the mini via ssh -L 8191:127.0.0.1:8191)
 * Per arm the prompt is assembled by that arm's scratch tree (scratch/s1-<arm>): rag/pure.ts assembleChatMessages (GROUNDING with/without L1),
 * constants/personalities.ts (Succinct system prompt + styleReminder with/without L1), ui-android/chat/answerBridge.ts buildChatHistory (last 6
 * messages verbatim; A3 drops declined assistant turns = L4). Context + style come from tools/out/ctx-{base|patched}.jsonl (C0,A1 base; A2,A3 patched).
 * Turns where the engine answers without the model (first-aid cards / health decline, reason "no-generation-reached") take the engine's text; no call.
 * Request = the engine's server-backend body: /v1/chat/completions, max_tokens 512, temp 0.7, top_k 40, top_p 0.95, min_p 0.05, seed 42, cache_prompt false.
 */
import { appendFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..");
const argv = process.argv.slice(2);
const get = (k: string, d?: string) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : d);
const model = get("--model", "m4")!;
const arms = get("--arms", "C0,A1,A2,A3")!.split(",");
const only = get("--chats")?.split(",");
const tag = get("--tag", "")!;
const port = get("--port", "8191")!;
const MAXTOK = 512, SENT = "@@STYLE@@";
const CHATS = get("--chatsfile", "<workspace>/boar-eval/bench/slices/chat-fu-v1/chats.jsonl")!;
const CTXNAME = get("--ctx"); // one context file for every arm (v0.1 single-turn run); default: base for C0/A1, patched for A2/A3
const OUT = join(ROOT, "tools/out");
mkdirSync(OUT, { recursive: true });

const ctxOf = (name: string) => {
  const m = new Map<string, any>();
  for (const l of readFileSync(join(OUT, `ctx-${name}.jsonl`), "utf8").trim().split("\n")) { const r = JSON.parse(l); m.set(`${r.chat}|${r.turn}`, r); }
  return m;
};
const CTX = CTXNAME ? { base: ctxOf(CTXNAME), patched: ctxOf(CTXNAME) } : { base: ctxOf("base"), patched: ctxOf("patched") };
const ROUTING: Record<string, "base" | "patched"> = { C0: "base", A1: "base", A2: "patched", A3: "patched" };

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
async function gen(messages: any[]) {
  const body = { messages, stream: false, max_tokens: MAXTOK, temperature: 0.7, top_k: 40, top_p: 0.95, min_p: 0.05, seed: 42, cache_prompt: false };
  for (let attempt = 0; ; attempt++) {
    try {
      const t = Date.now();
      const r = await fetch(`http://127.0.0.1:${port}/v1/chat/completions`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), signal: AbortSignal.timeout(600000) });
      if (!r.ok) throw new Error(`HTTP ${r.status} ${(await r.text()).slice(0, 200)}`);
      const j: any = await r.json();
      return { text: String(j.choices[0].message.content ?? "").trim(), tokens: j.usage.completion_tokens, n_prompt_tokens: j.usage.prompt_tokens, ms: Date.now() - t, finish_reason: j.choices[0].finish_reason };
    } catch (e: any) {
      if (attempt >= 20) throw e;
      console.error(`gen retry ${attempt}: ${e?.message ?? e}`); await sleep(15000);
    }
  }
}

const chats = readFileSync(CHATS, "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((c) => !only || only.includes(c.chat));
let totalNew = 0;
for (const arm of arms) {
  const tree = join(ROOT, "scratch", `s1-${arm.toLowerCase()}`);
  const pure: any = await import(join(tree, "src/rag/pure.ts"));
  const PERS: any = await import(join(tree, "src/constants/personalities.ts"));
  const AB: any = await import(join(tree, "src/ui-android/chat/answerBridge.ts"));
  const p = PERS.getPersonality("succinct");
  const file = join(OUT, `gen-${model}-${arm}${tag ? "-" + tag : ""}.jsonl`);
  const done = new Map<string, any>();
  if (existsSync(file)) {
    for (const l of readFileSync(file, "utf8").trim().split("\n")) if (l) { const r = JSON.parse(l); done.set(`${r.chat}|${r.turn}`, r); }
  } else writeFileSync(file, "");
  const ctxMap = CTX[ROUTING[arm]];
  let empties = 0, wall = 0;
  for (const ch of chats) {
    const prior: { role: "user" | "assistant"; text: string }[] = [];
    for (const t of ch.turns) {
      const key = `${ch.chat}|${t.turn}`;
      let rec = done.get(key);
      if (!rec) {
        const c = ctxMap.get(key);
        if (!c) throw new Error(`no context for ${key}`);
        const { history } = AB.buildChatHistory(prior, null);
        const style = String(c.style).split(SENT).join(p.styleReminder);
        const chunks = c.sources.map((s: any) => ({ title: s.title, body: s.body }));
        const messages = pure.assembleChatMessages(t.text, chunks, p.systemPrompt, history, style);
        const base = { arm, model, chat: ch.chat, kind: ch.kind, topic: ch.topic, turn: t.turn, text: t.text, expected_intent: t.expected_intent, capability_request: t.capability_request, class: c.class, plan_kind: c.plan_kind, searched_for: c.searched_for, n_sources: c.sources.length, n_history: history.turns.length };
        if (c.reason === "no-generation-reached") rec = { ...base, engine_fixed: true, answer: c.result_text, tokens: 0, finish_reason: "engine", ms: 0, messages };
        else {
          const g = await gen(messages);
          rec = { ...base, engine_fixed: false, answer: g.text, tokens: g.tokens, finish_reason: g.finish_reason, ms: g.ms, n_prompt_tokens: g.n_prompt_tokens, messages };
          wall += g.ms; totalNew++;
        }
        appendFileSync(file, JSON.stringify(rec) + "\n"); done.set(key, rec);
        console.log(arm, ch.chat, t.turn, t.capability_request ? "CAP" : "-", rec.class, rec.tokens, rec.finish_reason, rec.answer.slice(0, 60).replace(/\n/g, " "));
      }
      if (!String(rec.answer).trim()) empties++;
      prior.push({ role: "user", text: t.text }, { role: "assistant", text: rec.answer });
    }
  }
  console.log(`ARM-DONE ${model} ${arm} rows ${done.size} empties ${empties} gen_wall_s ${(wall / 1000).toFixed(0)}`);
  if (empties > 3) { console.error(`KILL: > 3 empty answers on ${model} ${arm}`); process.exit(3); }
}
console.log(`ALL-DONE ${model} new ${totalNew}`);
