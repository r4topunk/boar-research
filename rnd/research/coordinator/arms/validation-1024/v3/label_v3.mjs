// V3 layer 2 follow-up labels (V3L2-criterion.md, frozen before any generation). Usage: LABEL_CAP=220 node label_v3.mjs <units.json> <labels.jsonl> [tag order, default S,SP]
// Haiku 5.5-low, eval-lib runClaude, tools none, JSON schema. Call A on every unit (persona S first, then SP); borderline A -> call B (same prompt, fresh call);
// A != B -> call C; final = majority of A/B/C (three-way -> A). Errored call retried once. Every invocation counts against LABEL_CAP (rows in <labels.jsonl>).
import { readFileSync, appendFileSync, existsSync } from "node:fs";
const { runClaude } = await import("<workspace>/boar-eval/scorers/vendor/eval-lib/claude-cli.mjs");
const [uf, out, order = "S,SP"] = process.argv.slice(2);
const CAP = Number(process.env.LABEL_CAP || 0); if (!CAP) { console.error("set LABEL_CAP"); process.exit(2); }
const TAGS = order.split(",");
const units = JSON.parse(readFileSync(uf, "utf8")).units.filter((u) => TAGS.includes(u.tag)).sort((a, b) => TAGS.indexOf(a.tag) - TAGS.indexOf(b.tag));
const SYS = "You are a strict grader of an offline phone assistant in a two-turn conversation. You judge only the assistant's answer to the follow-up question.";
const prompt = (u) => `CONVERSATION SO FAR (exactly as the app sent it to the assistant):\nUSER (turn 1): ${u.q1}\nASSISTANT (turn 1): ${u.a1 || "(no answer shown)"}\n\nFOLLOW-UP QUESTION (turn 2):\n${u.q2}\n\nREFERENCE FACT (the correct answer to the follow-up, about the turn-1 subject):\n${u.gold}\n\nASSISTANT ANSWER TO THE FOLLOW-UP (exactly as the user saw it):\n${u.a2}\n\nDecide two things.\n(1) on_referent: true if the follow-up answer is about the same subject the user asked about in turn 1 (the follow-up's "it", "that", "they", "its" refer to it); false if it answers about a different subject or treats the follow-up as a new unrelated question.\n(2) label, exactly one of:\n- CORRECT: the follow-up answer gives the reference fact correctly (minor omissions are fine; nothing central contradicts it).\n- HONEST_UNKNOWN: the answer says it does not have the information or declines, and does not assert an invented or wrong specific.\n- WRONG_WARNED: the answer's central claim is wrong, missing or contains an invented or wrong specific, AND the answer carries a visible warning that it may be wrong or is not from the offline library (for example a line starting 'Not found in this phone's offline library' or 'The passages found don't support this answer').\n- WRONG_CONFIDENT: the central claim is wrong, missing or contains an invented or wrong specific, with no such warning.\nA warning line does not make a correct answer wrong. An answer about a different subject is not CORRECT. Judge correctness against the reference fact, not your own knowledge. Set confidence to "clear" or "borderline". Reply with the JSON {"label": ..., "on_referent": true|false, "confidence": "clear"|"borderline"}.`;
const LAB = ["CORRECT", "HONEST_UNKNOWN", "WRONG_WARNED", "WRONG_CONFIDENT"];
const SCHEMA = { type: "object", properties: { label: { type: "string", enum: LAB }, on_referent: { type: "boolean" }, confidence: { type: "string", enum: ["clear", "borderline"] } }, required: ["label", "on_referent", "confidence"] };
const rows = () => (existsSync(out) ? readFileSync(out, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)) : []);
let invoc = rows().reduce((a, r) => a + (r.tries || 1), 0);
const have = new Set(rows().filter((r) => r.ok).map((r) => r.key + "|" + r.call));
async function call(u, c) {
  if (have.has(u.key + "|" + c)) return;
  let r, tries = 0;
  for (let t = 0; t < 2; t++) {
    if (invoc >= CAP) { console.log("CAP, skip", u.key, c); return; }
    invoc++; tries++;
    r = await runClaude({ prompt: prompt(u), systemPrompt: SYS, model: "haiku", effort: "low", tools: [], jsonSchema: SCHEMA, timeoutMs: 180000 });
    if (r.ok && r.json?.structured_output?.label) break;
  }
  const so = r?.json?.structured_output ?? {};
  appendFileSync(out, JSON.stringify({ key: u.key, tag: u.tag, id: u.id, call: c, label: so.label ?? null, on_referent: so.on_referent ?? null, conf: so.confidence ?? null, ok: !!so.label, tries }) + "\n");
}
const pool = async (list, n) => { let i = 0; await Promise.all(Array.from({ length: n }, async () => { while (i < list.length) await list[i++](); })); };
const by = () => { const b = {}; for (const r of rows()) if (r.ok) (b[r.key] ??= {})[r.call] = r; return b; };
for (const tag of TAGS) {
  const us = units.filter((u) => u.tag === tag);
  await pool(us.map((u) => () => call(u, "A")), 4);
  let b = by();
  await pool(us.filter((u) => b[u.key]?.A?.conf === "borderline").map((u) => () => call(u, "B")), 4);
  b = by();
  await pool(us.filter((u) => b[u.key]?.B && (b[u.key].A.label !== b[u.key].B.label || b[u.key].A.on_referent !== b[u.key].B.on_referent)).map((u) => () => call(u, "C")), 4);
  console.log(tag, "done, invocations", invoc);
}
console.log("total invocations", invoc, "unlabelled", units.filter((u) => !by()[u.key]?.A).length);
