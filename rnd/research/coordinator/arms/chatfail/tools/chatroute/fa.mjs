// First-aid chats in CHAT-FU-v1: per turn, the lexical health flag answer.ts computes (without the learned detector) and
// whether the follow-up planner would run (non-health turn with history).
import fs from "node:fs";
import { createRequire } from "node:module";
const tree = process.argv[2];
const { createServer } = await import(createRequire(tree + "/package.json").resolve("vite"));
const server = await createServer({ root: tree, logLevel: "error", server: { middlewareMode: true, hmr: false, watch: null }, appType: "custom", optimizeDeps: { noDiscovery: true } });
const X = await server.ssrLoadModule("/src/routing/context.ts");
const K = await server.ssrLoadModule("/src/routing/conditionCards.ts");
const F = await server.ssrLoadModule("/src/routing/followUp.ts");
const chats = fs.readFileSync("<workspace>/boar-eval/bench/slices/chat-fu-v1/chats.jsonl", "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((c) => c.topic === "first aid");
for (const c of chats) {
  const users = [], turns = [];
  for (const t of c.turns) {
    const q = t.text;
    const hfu = X.isHealthFollowUp(q, users), lex = X.isHealthQuestion(q) || K.isCardEmergency(q);
    const health = lex || hfu;
    const p = users.length ? F.followUpSearch(q, { turns: turns.map((x) => ({ ...x })) }) : {};
    console.log(c.chat, t.turn, JSON.stringify(q), "health=" + health, health ? "planner:off" : users.length ? "planner:" + (p.direct ? "direct" : p.fallback ? "fallback" : "none") + " " + JSON.stringify(p.direct ?? p.fallback ?? "") : "first-turn");
    users.push(q); turns.push({ role: "user", text: q }, { role: "assistant", text: "…" });
  }
}
await server.close();
