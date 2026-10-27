// DEEPREAD (Kiln): build the chat messages for deep35 R450 with gen_oracle.mts's exact prompt logic (same SYS_PREFIX,
// STYLE suffix, Context formatting, ctx-R450.jsonl), so only the model/backend changes. Also checks that every item's
// passages match the 4B R450 trace's retrieval.kept (title + sim) and question.  node build_msgs.mjs > requests.jsonl
import fs from "node:fs";
const D = "<workspace>/rnd/research/anvil/exp/oracle";
const rd = (p) => fs.readFileSync(p, "utf8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
const dump = rd("<workspace>/boar-eval/runs/and-qwen-s44/and-qwen-s44.prompts.jsonl");
const withCtx = dump.find((r) => r.messages[0].content.includes("\n\nContext:\n"));
const SYS_PREFIX = withCtx.messages[0].content.split("\n\nContext:\n")[0];
const qs = new Map(rd("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl").map((q) => [q.id, q]));
const wq = qs.get(withCtx.itemId).question; const userMsg = withCtx.messages.at(-1).content;
if (!userMsg.startsWith(wq)) throw new Error("unexpected user message shape");
const STYLE = userMsg.slice(wq.length);
const ctxs = rd(`${D}/ctx-R450.jsonl`);
const t4 = new Map(rd(`${D}/runs/qwen3-4b-R450.traces.jsonl`).map((t) => [t.itemId, t]));
let mism = 0;
for (const c of ctxs) {
  const q = qs.get(c.id);
  const context = c.passages.map((p, i) => `[${i + 1}] ${p.kind === "wiki" ? "Wikipedia" : "Web"}: ${p.title}\n${p.text}`).join("\n\n");
  const system = c.passages.length ? `${SYS_PREFIX}\n\nContext:\n${context}` : SYS_PREFIX;
  const tr = t4.get(c.id);
  const same = tr && tr.question === q.question && JSON.stringify(tr.retrieval.kept) === JSON.stringify(c.passages.map((p) => ({ title: p.title, sim: p.sim })));
  if (!same) { mism++; console.error("MISMATCH vs 4B trace:", c.id); }
  console.log(JSON.stringify({ id: c.id, question: q.question, nPassages: c.passages.length, kept: c.passages.map((p) => ({ title: p.title, sim: p.sim })),
    messages: [{ role: "system", content: system }, { role: "user", content: q.question + STYLE }] }));
}
console.error(`items ${ctxs.length}, 4B traces ${t4.size}, mismatches ${mism}`);
