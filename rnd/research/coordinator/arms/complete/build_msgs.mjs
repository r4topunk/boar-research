// COMPLETE (Kiln): DEEPREAD's build_msgs.mjs with ONE prompt change (frozen COMPLETE-criterion.md): the answer instruction
// ("Answer in 2-3 short, direct sentences or a brief paragraph, no preamble." in the system prompt, plus the user-turn
// "(Response style: Keep it short: 2-3 sentences. ...)" suffix, which is the same length instruction) is replaced by the
// completeness instruction. Sources block, citation rules, bullets rule and safety lines unchanged.  node build_msgs.mjs > requests.jsonl
import fs from "node:fs";
const D = "<workspace>/rnd/research/anvil/exp/oracle";
const rd = (p) => fs.readFileSync(p, "utf8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
const dump = rd("<workspace>/boar-eval/runs/and-qwen-s44/and-qwen-s44.prompts.jsonl");
const withCtx = dump.find((r) => r.messages[0].content.includes("\n\nContext:\n"));
const SYS_PREFIX_OLD = withCtx.messages[0].content.split("\n\nContext:\n")[0];
const qs = new Map(rd("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl").map((q) => [q.id, q]));
const wq = qs.get(withCtx.itemId).question; const userMsg = withCtx.messages.at(-1).content;
if (!userMsg.startsWith(wq)) throw new Error("unexpected user message shape");
const STYLE_OLD = userMsg.slice(wq.length);
const OLD_INSTR = "Answer in 2-3 short, direct sentences or a brief paragraph, no preamble.";
const NEW_INSTR = "Answer completely, the way an expert would explain it to a curious traveler or student: lead with the direct answer, then the key supporting points (who/what/when/where/how much, causes, comparison verdict, caveats), 120–220 words. Use only facts you are sure of or that the sources state; never pad with guesses.";
if (SYS_PREFIX_OLD.split(OLD_INSTR).length !== 2) throw new Error("old answer instruction not found exactly once");
const SYS_PREFIX = SYS_PREFIX_OLD.replace(OLD_INSTR, NEW_INSTR);
const STYLE = ""; // user-turn length suffix dropped (it is the same answer instruction: "Keep it short: 2-3 sentences")
if (process.env.SHOW_PROMPT) { console.log(JSON.stringify({ SYS_PREFIX_OLD, SYS_PREFIX, STYLE_OLD, STYLE })); process.exit(0); }
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
