// PACKSHAPE copy of PACKPROOF outcome labels: byte-identical prompt/schema/recheck logic to uxmatrix/tools/label.mjs (criterion 0cc3ca20); PACKPROOF criterion 37f74d6f. Usage: node label.mjs <units.json> <labels.jsonl>
import { readFileSync, appendFileSync, existsSync } from "node:fs";
const { runClaude } = await import("<workspace>/boar-eval/scorers/vendor/eval-lib/claude-cli.mjs");
const [uf, out] = process.argv.slice(2);
const CAP = 60, CAPBC = 60; // PACKSHAPE cap (criterion); prompt/schema byte-identical to packproof label.mjs
const units = JSON.parse(readFileSync(uf, "utf8")).units;
const SYS = "You are a strict grader of an offline phone assistant. You compare its answer with a reference answer and check whether the passages it showed the user contain that answer.";
const prompt = (u, src) => `QUESTION:\n${u.question}\n\nREFERENCE ANSWER:\n${u.gold}\n\nRUBRIC (what a good answer must contain):\n${u.rubric.map((r) => "- " + r).join("\n")}\n\nASSISTANT ANSWER (exactly as the user saw it):\n${u.answer}\n\nSOURCE PASSAGES THE APP SHOWED WITH THE ANSWER:\n${src}\n\nDecide two things.\n(1) source_holds: true if at least one source passage states, or directly entails, the central answer-bearing claim of the reference answer; false otherwise.\n(2) label, exactly one of:\n- CORRECT_WITH_SOURCE: the answer gives the central claim of the reference answer correctly (minor omissions are fine; nothing central contradicts it) AND source_holds is true.\n- CORRECT_FROM_MEMORY: the answer gives the central claim correctly but source_holds is false.\n- HONEST_UNKNOWN: the answer says it does not have the information or declines, and does not assert an invented or wrong specific, and source_holds is false.\n- REFUSED_WRONGLY: the answer says it does not have the information or declines without giving the central claim, although source_holds is true.\n- WRONG_WARNED: the answer's central claim is wrong, missing or contains an invented or wrong specific, AND the answer carries a visible warning that it may be wrong or is not from the offline library (for example a line starting 'Not found in this phone's offline library').\n- WRONG_CONFIDENT: the central claim is wrong, missing or contains an invented or wrong specific, with no such warning.\nA warning line does not make a correct answer wrong: a correct answer with a warning is CORRECT_FROM_MEMORY or CORRECT_WITH_SOURCE. Judge correctness against the reference answer, not your own knowledge. Set confidence to "clear" or "borderline". Reply with the JSON {"label": ..., "source_holds": true|false, "confidence": "clear"|"borderline"}.`;
const LAB = ["CORRECT_WITH_SOURCE", "CORRECT_FROM_MEMORY", "HONEST_UNKNOWN", "REFUSED_WRONGLY", "WRONG_WARNED", "WRONG_CONFIDENT"];
const SCHEMA = { type: "object", properties: { label: { type: "string", enum: LAB }, source_holds: { type: "boolean" }, confidence: { type: "string", enum: ["clear", "borderline"] } }, required: ["label", "source_holds", "confidence"] };
const rows = () => (existsSync(out) ? readFileSync(out, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)) : []);
let invoc = rows().reduce((a, r) => a + (r.tries || 1), 0);
const have = new Set(rows().filter((r) => r.ok).map((r) => r.key + "|" + r.call));
async function call(u, c, cap) {
  if (have.has(u.key + "|" + c)) return;
  let r, tries = 0;
  for (let t = 0; t < 2; t++) {
    if (invoc >= cap) { console.log("CAP, skip", u.key, c); return; }
    invoc++; tries++;
    r = await runClaude({ prompt: prompt(u, c === "B" ? u.sources_rev : u.sources), systemPrompt: SYS, model: "haiku", effort: "low", tools: [], jsonSchema: SCHEMA, timeoutMs: 180000 });
    if (r.ok && r.json?.structured_output?.label) break;
  }
  const so = r?.json?.structured_output ?? {};
  appendFileSync(out, JSON.stringify({ key: u.key, id: u.id, call: c, label: so.label ?? null, source_holds: so.source_holds ?? null, conf: so.confidence ?? null, ok: !!so.label, tries }) + "\n");
}
const pool = async (list, n) => { let i = 0; await Promise.all(Array.from({ length: n }, async () => { while (i < list.length) await list[i++](); })); };
const by = () => { const b = {}; for (const r of rows()) if (r.ok) (b[r.key] ??= {})[r.call] = r; return b; };
await pool(units.map((u) => () => call(u, "A", CAP)), 4);
let b = by(); console.log("A done, invocations", invoc);
if (process.env.ONLY_A === "1") process.exit(0);
await pool(units.filter((u) => b[u.key]?.A?.conf === "borderline").map((u) => () => call(u, "B", CAPBC)), 4);
b = by();
await pool(units.filter((u) => b[u.key]?.B && b[u.key].A.label !== b[u.key].B.label).map((u) => () => call(u, "C", CAPBC)), 4);
console.log("total invocations", invoc, "unlabelled", units.filter((u) => !by()[u.key]?.A).length);
