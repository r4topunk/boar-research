// SUPPORT labelling (criterion SUPPORT-criterion.md). Usage: node label.mjs <prep.json> <out labels.jsonl>
import { readFileSync, appendFileSync, existsSync } from "node:fs";
const LIB = "<workspace>/boar-eval/scorers/vendor/eval-lib/claude-cli.mjs";
const { runClaude } = await import(LIB);
const [prepf, out] = process.argv.slice(2);
const CAP = 245;
const units = JSON.parse(readFileSync(prepf, "utf8")).units;
const SYS = "You are a strict support auditor. You only judge whether the source chunks contain the information a reference answer needs. Whether anything is true in the real world is irrelevant.";
const prompt = (u, chunks) => `QUESTION:\n${u.question}\n\nREFERENCE ANSWER:\n${u.gold}\n\nRUBRIC (what a good answer must contain):\n${u.rubric.map((r) => "- " + r).join("\n")}\n\nSOURCE CHUNKS:\n${chunks}\n\nLabel SUPPORTS only if at least one single source chunk states, or directly entails, a central answer-bearing claim of the reference answer, that is, a claim that one of the non-'Penalize' rubric points asks for and without which the question cannot be answered well. Label NOT_SUPPORTS if the chunks only share the topic or keywords, give only background, contain only claims peripheral to the question, or if the needed claim is spread over several chunks so that no single chunk states it. Ignore your own knowledge of whether the reference answer or the chunks are true. Set confidence to "clear" when the label is unambiguous and "borderline" when a reasonable auditor could label it the other way. Reply with the JSON {"label": "SUPPORTS" | "NOT_SUPPORTS", "confidence": "clear" | "borderline"}.`;
const SCHEMA = { type: "object", properties: { label: { type: "string", enum: ["SUPPORTS", "NOT_SUPPORTS"] }, confidence: { type: "string", enum: ["clear", "borderline"] } }, required: ["label", "confidence"] };
const rows = () => (existsSync(out) ? readFileSync(out, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)) : []);
let invoc = rows().reduce((a, r) => a + (r.tries || 1), 0);   // resume-safe invocation counter
const have = new Set(rows().map((r) => r.key + "|" + r.call));
async function call(u, c) {
  if (have.has(u.key + "|" + c)) return;
  const chunks = c === "B" ? u.chunks_rev : u.chunks;
  let r, tries = 0;
  for (let t = 0; t < 2; t++) {
    if (invoc >= CAP) { console.log("CAP reached, skip", u.key, c); return; }
    invoc++; tries++;
    r = await runClaude({ prompt: prompt(u, chunks), systemPrompt: SYS, model: "haiku", effort: "low", tools: [], jsonSchema: SCHEMA, timeoutMs: 180000 });
    if (r.ok && r.json?.structured_output?.label) break;
  }
  const so = r?.json?.structured_output ?? {};
  appendFileSync(out, JSON.stringify({ key: u.key, call: c, label: so.label ?? null, conf: so.confidence ?? null, ok: !!so.label, tries }) + "\n");
}
const pool = async (list, n) => { let i = 0; await Promise.all(Array.from({ length: n }, async () => { while (i < list.length) await list[i++](); })); };
const by = () => { const b = {}; for (const r of rows()) (b[r.key] ??= {})[r.call] = r; return b; };
await pool(units.map((u) => () => call(u, "A")), 4);
console.log("A done, invocations", invoc);
let b = by();
const needB = units.filter((u) => b[u.key]?.A?.ok && b[u.key].A.conf === "borderline");
console.log("borderline", needB.length);
await pool(needB.map((u) => () => call(u, "B")), 4);
b = by();
const needC = units.filter((u) => b[u.key]?.B?.ok && b[u.key].A.label !== b[u.key].B.label);
console.log("A/B disagree", needC.length);
await pool(needC.map((u) => () => call(u, "C")), 4);
console.log("total invocations", invoc, "failed units", units.filter((u) => !by()[u.key]?.A?.ok).length);
