// CHATFAIL S0 replay: 0 model calls. Feeds each chat turn by turn to the TS engine's classify() and follow-up planner
// (imported from a scratch tree via Vite ssrLoadModule) and records intent class + anchor turn per turn.
//   node tools/replay.mjs --tree scratch/base [--chats <jsonl>] [--limit N] [--v01 <questions.public.jsonl>] --out tools/out/before.json
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const arg = (k, d) => { const i = process.argv.indexOf("--" + k); return i < 0 ? d : process.argv[i + 1]; };

const tree = path.resolve(arg("tree", "scratch/base"));
const chatsFile = arg("chats", "<workspace>/boar-eval/bench/slices/chat-fu-v1/chats.jsonl");
const v01File = arg("v01", "<workspace>/boar-eval/bench/v0.1/questions.public.jsonl");
const limit = Number(arg("limit", "0"));
const out = arg("out", null);

const { createServer } = await import(createRequire(tree + "/package.json").resolve("vite"));
const server = await createServer({ root: tree, logLevel: "error", server: { middlewareMode: true, hmr: false, watch: null }, appType: "custom", optimizeDeps: { noDiscovery: true } });
const cls = await server.ssrLoadModule("/src/routing/classify.ts");
const fu = await server.ssrLoadModule("/src/routing/followUp.ts");
const X = await server.ssrLoadModule("/src/routing/context.ts");
const K = await server.ssrLoadModule("/src/routing/conditionCards.ts");
// Engine rule (answer.ts, chatroute): no in-context code rule and no follow-up planner in a health conversation (lexical part only:
// the learned detector is not replayed, and it can only add health turns, so this is the most the change can move).
const lexH = (t) => X.isHealthQuestion(t) || X.isSafetyQuery(t) || K.isCardEmergency(t);
const healthChat = (q, prior) => lexH(q) || X.isHealthFollowUp(q, prior) || prior.some(lexH);
const inContext = typeof cls.classifyTaskInContext === "function";
const classify = (q, prior) => (inContext && !healthChat(q, prior) ? cls.classifyTaskInContext(q, prior) : cls.classifyTask(q));

// expected_intent -> engine TaskTypes that count as correctly routed. The engine has no "format" type: a reformat request routes to
// chat/summarize/extract (generation over the previous answer), which is accepted; lookup also accepts research (both retrieve).
const ACCEPT = { lookup: ["lookup", "research"], chat: ["chat", "conversation"], code: ["code"], format: ["chat", "summarize", "extract"], translate: ["translate"], compare: ["compare"] };
// Classes that keep retrieval on and the Succinct 2-3 sentence cap (everything except the retrieval-irrelevant types).
const CAPPED = new Set(["lookup", "research", "chat", "conversation", "summarize", "extract", "compare", "unknown"]);

let chats = fs.readFileSync(chatsFile, "utf8").trim().split("\n").map((l) => JSON.parse(l));
if (limit) chats = chats.slice(0, limit);
const rows = [];
for (const ch of chats) {
  const hist = []; // what the engine holds: user turns + a placeholder assistant answer
  const users = [];
  for (const t of ch.turns) {
    const history = { turns: hist.map((x) => ({ ...x })) };
    const klass = classify(t.text, users.slice());
    const plan = healthChat(t.text, users) || (inContext && X.isHealthQuestion(t.text)) ? {} : fu.followUpSearch(t.text, history);
    const kind = plan.direct ? "direct" : plan.fallback ? "fallback" : "none";
    const joined = plan.direct ?? plan.fallback ?? null;
    let borrowed = null; // user-turn index (1-based) whose text the planner prepends
    if (joined) {
      const anchorText = joined.slice(0, joined.length - t.text.trim().length).trim();
      const idx = users.findIndex((u) => u.trim() === anchorText);
      borrowed = idx < 0 ? -1 : idx + 1;
    }
    // Worst case: a "fallback" plan borrows (the turn's own search found nothing, as in the live trace). Best case: it keeps its own turn.
    const anchorWorst = borrowed ?? t.turn, anchorBest = kind === "direct" ? borrowed : t.turn;
    rows.push({
      chat: ch.chat, kind: ch.kind, topic: ch.topic, turn: t.turn, text: t.text, exp_intent: t.expected_intent, exp_anchor: t.expected_anchor, cap: t.capability_request,
      class: klass, intent_ok: ACCEPT[t.expected_intent].includes(klass), capped: CAPPED.has(klass), plan: kind, planned: joined, anchor_worst: anchorWorst, anchor_best: anchorBest,
    });
    users.push(t.text); hist.push({ role: "user", text: t.text }, { role: "assistant", text: "…" });
  }
}
let v01 = null;
if (v01File && fs.existsSync(v01File) && !limit) {
  v01 = fs.readFileSync(v01File, "utf8").trim().split("\n").map((l) => { const j = JSON.parse(l); return { id: j.id, q: j.question, class: classify(j.question, []) }; });
}
await server.close();
const res = { tree, in_context_classifier: inContext, n_turns: rows.length, rows, v01 };
if (out) { fs.mkdirSync(path.dirname(out), { recursive: true }); fs.writeFileSync(out, JSON.stringify(res, null, 1)); }
const pct = (a, b) => (b ? ((100 * a) / b).toFixed(1) + "% (" + a + "/" + b + ")" : "n/a");
const ok = (f) => rows.filter(f), cap = ok((r) => r.cap), late = ok((r) => r.turn >= 3);
console.log(`tree=${path.basename(tree)} chats=${chats.length} turns=${rows.length} in-context-classifier=${inContext}`);
console.log("intent acc, all turns        ", pct(ok((r) => r.intent_ok).length, rows.length));
console.log("intent acc, capability turns ", pct(cap.filter((r) => r.intent_ok).length, cap.length));
console.log("capability turns on capped class", pct(cap.filter((r) => r.capped).length, cap.length));
console.log("anchor acc turn>=3 worst/best ", pct(late.filter((r) => r.anchor_worst === r.exp_anchor).length, late.length), "/", pct(late.filter((r) => r.anchor_best === r.exp_anchor).length, late.length));
